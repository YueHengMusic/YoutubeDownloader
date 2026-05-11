from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Awaitable, Callable

from app.models.task import DownloadTask, TaskStatus

TaskUpdateCallback = Callable[[DownloadTask], Awaitable[None]]
TaskRunFunc = Callable[[DownloadTask, TaskUpdateCallback], Awaitable[None]]


class QueueManager:
    """
    轻量级内存任务队列 + 固定数量 worker。
    适合桌面端单机场景，逻辑直观，易于排查问题。
    """

    def __init__(
        self,
        runner: TaskRunFunc,
        on_update: TaskUpdateCallback,
        cancel_runner: Callable[[str], Awaitable[None]] | None = None,
        concurrency: int = 2,
    ) -> None:
        self.runner = runner
        self.on_update = on_update
        self.cancel_runner = cancel_runner
        self.concurrency = max(1, int(concurrency))
        self.tasks: dict[str, DownloadTask] = {}
        # waiting 队列支持 str/None：
        # - str: 正常任务 ID；
        # - None: worker 退出哨兵（用于动态缩容）。
        self.waiting: asyncio.Queue[str | None] = asyncio.Queue()
        self._workers: list[asyncio.Task[None]] = []
        self._started = False

    async def start(self) -> None:
        """应用启动时创建 worker 协程。"""
        if self._started:
            return
        self._started = True
        self._spawn_workers(self.concurrency)

    async def shutdown(self) -> None:
        """应用退出时取消 worker 协程。"""
        workers = list(self._workers)
        for worker in workers:
            worker.cancel()
        await asyncio.gather(*workers, return_exceptions=True)
        self._workers = []
        self._started = False

    async def set_concurrency(self, concurrency: int) -> int:
        """
        动态调整并发 worker 数量。

        调整策略：
        - 扩容：立即补充新 worker；
        - 缩容：向队列写入退出哨兵，worker 在完成当前任务后自然退出。
        """
        normalized = max(1, int(concurrency))
        self.concurrency = normalized
        if not self._started:
            return self.concurrency

        current_worker_count = len(self._workers)
        if normalized > current_worker_count:
            self._spawn_workers(normalized - current_worker_count)
            return self.concurrency
        if normalized < current_worker_count:
            for _ in range(current_worker_count - normalized):
                await self.waiting.put(None)
        return self.concurrency

    async def add_task(self, task: DownloadTask) -> None:
        """新任务入队，并立即推送一次状态给前端。"""
        self.tasks[task.id] = task
        await self.waiting.put(task.id)
        await self.on_update(task)

    async def cancel_task(self, task_id: str) -> bool:
        """把任务标记为取消。"""
        task = self.tasks.get(task_id)
        if not task:
            return False
        if task.status in (TaskStatus.completed, TaskStatus.failed, TaskStatus.canceled):
            return False
        if self.cancel_runner is not None:
            await self.cancel_runner(task_id)
        task.status = TaskStatus.canceled
        task.updated_at = datetime.utcnow()
        await self.on_update(task)
        return True

    def remove_task(self, task_id: str) -> bool:
        """
        从内存队列中删除任务。
        规则：
        - running 任务不允许直接删除，避免和正在执行的 worker 冲突；
        - pending/completed/failed/canceled 允许删除。
        """
        task = self.tasks.get(task_id)
        if task is None:
            return False
        if task.status == TaskStatus.running:
            return False
        del self.tasks[task_id]
        return True

    def list_tasks(self) -> list[DownloadTask]:
        """返回稳定排序结果，避免前端列表闪烁。"""
        return sorted(self.tasks.values(), key=lambda item: item.created_at, reverse=True)

    def _spawn_workers(self, count: int) -> None:
        """批量创建 worker 协程。"""
        for _ in range(max(0, count)):
            self._workers.append(asyncio.create_task(self._worker()))

    async def _worker(self) -> None:
        """worker 主循环：不断取任务并执行。"""
        current_worker = asyncio.current_task()
        try:
            while True:
                task_id = await self.waiting.get()
                if task_id is None:
                    # 收到退出哨兵：当前 worker 安全退出（用于缩容）。
                    self.waiting.task_done()
                    break

                task = self.tasks.get(task_id)
                if task is None or task.status == TaskStatus.canceled:
                    self.waiting.task_done()
                    continue
                try:
                    await self.runner(task, self.on_update)
                except Exception as exc:  # noqa: BLE001
                    task.status = TaskStatus.failed
                    task.error = str(exc)
                    task.updated_at = datetime.utcnow()
                    await self.on_update(task)
                finally:
                    self.waiting.task_done()
        finally:
            # 退出时从 worker 列表移除，确保后续缩扩容计算准确。
            if current_worker in self._workers:
                self._workers.remove(current_worker)
