from __future__ import annotations

import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Awaitable, Callable

from app.core.cookie_manager import CookieManager
from app.models.task import DownloadTarget, DownloadTask, ResolutionMode, SubtitleMode, TaskStatus

ProgressCallback = Callable[[DownloadTask], Awaitable[None]]
TerminalCallback = Callable[[dict], Awaitable[None]]


class YtDlpRunner:
    def __init__(
        self,
        yt_dlp_path: Path,
        ffmpeg_path: Path,
        terminal_callback: TerminalCallback | None = None,
    ) -> None:
        self.yt_dlp_path = yt_dlp_path
        self.ffmpeg_path = ffmpeg_path
        # 终端日志回调由上层注入（通常是事件总线广播），这样运行器不直接依赖具体传输实现。
        self.terminal_callback = terminal_callback

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

        if task.download_target == DownloadTarget.audio:
            cmd.extend(["-x", "--audio-format", task.audio_format or "mp3"])

        if task.download_target == DownloadTarget.thumbnail:
            # 仅封面模式：不下载媒体本体，仅写封面文件。
            cmd.append("--skip-download")
            cmd.append("--write-thumbnail")
        elif task.write_thumbnail:
            cmd.append("--write-thumbnail")

        if task.embed_thumbnail:
            cmd.append("--embed-thumbnail")

        if task.subtitle_mode == SubtitleMode.manual:
            cmd.append("--write-subs")
        elif task.subtitle_mode == SubtitleMode.auto:
            cmd.append("--write-auto-subs")
        elif task.subtitle_mode == SubtitleMode.all:
            cmd.extend(["--write-subs", "--write-auto-subs"])

        if task.subtitle_mode != SubtitleMode.none and task.subtitle_langs:
            cmd.extend(["--sub-langs", task.subtitle_langs])

        if task.write_info_json:
            cmd.append("--write-info-json")

        if task.write_description:
            cmd.append("--write-description")

        if task.download_target == DownloadTarget.video and task.format_id:
            cmd.extend(["-f", task.format_id])

        if task.download_target == DownloadTarget.video and task.resolution:
            if task.resolution_mode == ResolutionMode.limit:
                # 严格“上限分辨率”：尽量选不高于目标值的格式，找不到再按合并格式回退。
                cmd.extend(["-f", f"bv*[height<={task.resolution}]+ba/b[height<={task.resolution}]"])
            else:
                # 偏好分辨率：作为排序优先级，不是硬性过滤。
                cmd.extend(["-S", f"res:{task.resolution}"])
        cmd.extend(CookieManager.cookie_args(task.cookie_mode, task.cookie_value))
        cmd.append(task.url)
        return cmd

    async def run(self, task: DownloadTask, callback: ProgressCallback) -> None:
        """
        执行一次 yt-dlp 子进程，并持续把进度回调给上层。
        """
        command = self.build_command(task)
        # 任务开始时先广播“完整命令行”，方便前端终端面板看到本次实际执行了什么。
        await self._emit_terminal_event(
            {
                "stream": "command",
                "task_id": task.id,
                "text": " ".join(command),
            }
        )
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
            # 持续广播 stdout 行，让前端可以实时渲染“正在执行中的终端输出”。
            await self._emit_terminal_event(
                {
                    "stream": "stdout",
                    "task_id": task.id,
                    "text": text,
                }
            )
            self._parse_line(task, text)
            task.updated_at = datetime.utcnow()
            await callback(task)

        return_code = await process.wait()
        await self._emit_terminal_event(
            {
                "stream": "status",
                "task_id": task.id,
                "text": f"yt-dlp exited with code {return_code}",
            }
        )
        if return_code == 0:
            task.status = TaskStatus.completed
            task.progress = 100.0
        else:
            if task.status != TaskStatus.canceled:
                task.status = TaskStatus.failed
                task.error = f"yt-dlp exited with code {return_code}"
        task.updated_at = datetime.utcnow()
        await callback(task)

    async def _emit_terminal_event(self, payload: dict) -> None:
        """
        统一终端事件出口：
        - 若上层未注入回调，则直接跳过，不影响核心下载流程。
        - 捕获并吞掉回调异常，避免“仅日志通道故障”导致下载任务失败。
        """
        if self.terminal_callback is None:
            return
        try:
            await self.terminal_callback(payload)
        except Exception:
            return

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
