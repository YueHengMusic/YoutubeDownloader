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

    def __init__(self, runner: TaskRunFunc, on_update: TaskUpdateCallback, concurrency: int = 2) -> None:
        self.runner = runner
        self.on_update = on_update
        self.concurrency = concurrency
        self.tasks: dict[str, DownloadTask] = {}
        self.waiting: asyncio.Queue[str] = asyncio.Queue()
        self._workers: list[asyncio.Task[None]] = []
        self._started = False

    async def start(self) -> None:
        """应用启动时创建 worker 协程。"""
        if self._started:
            return
        self._started = True
        for _ in range(self.concurrency):
            self._workers.append(asyncio.create_task(self._worker()))

    async def shutdown(self) -> None:
        """应用退出时取消 worker 协程。"""
        for worker in self._workers:
            worker.cancel()
        self._workers.clear()
        self._started = False

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
        task.status = TaskStatus.canceled
        task.updated_at = datetime.utcnow()
        await self.on_update(task)
        return True

    def list_tasks(self) -> list[DownloadTask]:
        """返回稳定排序结果，避免前端列表闪烁。"""
        return sorted(self.tasks.values(), key=lambda item: item.created_at, reverse=True)

    async def _worker(self) -> None:
        """worker 主循环：不断取任务并执行。"""
        while True:
            task_id = await self.waiting.get()
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
