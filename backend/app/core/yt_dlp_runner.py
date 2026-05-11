from __future__ import annotations

import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Awaitable, Callable

from app.core.cookie_manager import CookieManager
from app.models.task import DownloadTask, TaskStatus

ProgressCallback = Callable[[DownloadTask], Awaitable[None]]


class YtDlpRunner:
    def __init__(self, yt_dlp_path: Path, ffmpeg_path: Path) -> None:
        self.yt_dlp_path = yt_dlp_path
        self.ffmpeg_path = ffmpeg_path

    def build_command(self, task: DownloadTask) -> list[str]:
        """把任务字段翻译成一条可执行的 yt-dlp 命令。"""
        output_tpl = str(Path(task.output_dir) / "%(title)s.%(ext)s")
        cmd = [
            str(self.yt_dlp_path),
            "--newline",
            "--no-color",
            "--progress",
            "--ffmpeg-location",
            str(self.ffmpeg_path),
            "-o",
            output_tpl,
        ]
        if task.format_id:
            cmd.extend(["-f", task.format_id])
        if task.resolution:
            cmd.extend(["-S", f"res:{task.resolution}"])
        cmd.extend(CookieManager.cookie_args(task.cookie_mode, task.cookie_value))
        cmd.append(task.url)
        return cmd

    async def run(self, task: DownloadTask, callback: ProgressCallback) -> None:
        """
        执行一次 yt-dlp 子进程，并持续把进度回调给上层。
        """
        command = self.build_command(task)
        task.status = TaskStatus.running
        task.updated_at = datetime.utcnow()
        await callback(task)

        # 把 stderr 合并到 stdout，前端只读一个流就能看到完整日志。
        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )

        assert process.stdout is not None
        async for line in process.stdout:
            text = line.decode("utf-8", errors="ignore").strip()
            if not text:
                continue
            self._parse_line(task, text)
            task.updated_at = datetime.utcnow()
            await callback(task)

        return_code = await process.wait()
        if return_code == 0:
            task.status = TaskStatus.completed
            task.progress = 100.0
        else:
            if task.status != TaskStatus.canceled:
                task.status = TaskStatus.failed
                task.error = f"yt-dlp exited with code {return_code}"
        task.updated_at = datetime.utcnow()
        await callback(task)

    def _parse_line(self, task: DownloadTask, text: str) -> None:
        """从 yt-dlp 输出文本中解析进度、结果路径等关键字段。"""
        task.log = f"{task.log}\n{text}".strip()

        # 常见进度行格式： [download]  12.3% of ...
        if "[download]" in text and "%" in text:
            try:
                pct_part = text.split("%", 1)[0]
                pct = pct_part.split()[-1]
                task.progress = float(pct)
            except (ValueError, IndexError):
                pass

        # 如果未来启用 --print-json，这里会尝试解析文件路径。
        if text.startswith("{") and text.endswith("}"):
            try:
                data = json.loads(text)
                filepath = data.get("_filename")
                if filepath:
                    task.result_path = filepath
            except json.JSONDecodeError:
                pass
