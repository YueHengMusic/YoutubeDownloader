from __future__ import annotations

import asyncio
import json
import locale
import os
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Awaitable, Callable

from app.core.cookie_manager import CookieManager
from app.models.task import DownloadTarget, DownloadTask, ResolutionMode, SubtitleMode, TaskStatus

ProgressCallback = Callable[[DownloadTask], Awaitable[None]]
TerminalCallback = Callable[[dict], Awaitable[None]]
# 速度提取：匹配 `at 1.23MiB/s`、`at 850KB/s`、`at 2.4MB/s` 等常见格式。
SPEED_PATTERN = re.compile(r"\bat\s+([0-9.]+\s*[KMGTP]?i?B/s)\b", re.IGNORECASE)
# ETA 提取：匹配 `ETA 00:12`、`ETA 01:23:45`、`ETA Unknown`。
ETA_PATTERN = re.compile(r"\bETA\s+([0-9:]+|Unknown)\b", re.IGNORECASE)
# 输出路径提取：覆盖常见下载/合并/转码等结果行。
RESULT_PATH_PATTERNS = [
    re.compile(r"^\[download\]\s+Destination:\s+(.+)$"),
    re.compile(r"^\[download\]\s+(.+?)\s+has already been downloaded$"),
    re.compile(r'^(?:\[[A-Za-z0-9_]+\]\s+)?Merging formats into\s+"(.+)"$'),
    re.compile(r"^\[[A-Za-z0-9_]+\]\s+Destination:\s+(.+)$"),
    # 封面下载常见输出：
    # - Writing video thumbnail to: xxx.webp
    # - [info] Writing video thumbnail 41 to: xxx.webp
    re.compile(r"^(?:\[[A-Za-z0-9_]+\]\s+)?Writing video thumbnail(?:\s+\d+)?\s+to:\s+(.+)$"),
]
# yt-dlp 常见中间文件命名：xxx.f251.webm / xxx.f401.mp4 / xxx.f140.m4a
INTERMEDIATE_FRAGMENT_PATTERN = re.compile(r"\.f\d+\.[^\\/]+$", re.IGNORECASE)


class YtDlpRunner:
    def __init__(
        self,
        yt_dlp_path: Path,
        ffmpeg_path: Path,
        terminal_callback: TerminalCallback | None = None,
    ) -> None:
        self.yt_dlp_path = yt_dlp_path
        self.ffmpeg_path = ffmpeg_path
        self._active_processes: dict[str, asyncio.subprocess.Process] = {}
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
            str(self.ffmpeg_path.parent),
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
        self._active_processes[task.id] = process

        assert process.stdout is not None
        try:
            async for line in process.stdout:
                # Windows 下部分下载器输出可能不是 UTF-8（例如 cp936），直接 utf-8 ignore 会截断路径中的全角/中文字符。
                # 这里优先用系统首选编码解码，失败再回退 utf-8，尽量保留原始路径字符。
                preferred_encoding = locale.getpreferredencoding(False) or "utf-8"
                try:
                    text = line.decode(preferred_encoding, errors="replace").strip()
                except LookupError:
                    text = line.decode("utf-8", errors="replace").strip()
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
        finally:
            self._active_processes.pop(task.id, None)

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

    async def cancel(self, task_id: str) -> None:
        """尽力终止指定任务对应的 yt-dlp 进程（含 Windows 子进程树）。"""
        process = self._active_processes.get(task_id)
        if process is None or process.returncode is not None:
            return
        pid = process.pid
        if os.name == "nt":
            # Windows 下使用 taskkill /T /F 终止整个进程树，避免 ffmpeg 子进程残留。
            await asyncio.to_thread(
                subprocess.run,
                ["taskkill", "/PID", str(pid), "/T", "/F"],
                check=False,
                capture_output=True,
                text=True,
            )
            return

        process.terminate()
        try:
            await asyncio.wait_for(process.wait(), timeout=1.5)
        except asyncio.TimeoutError:
            process.kill()

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
            # 速度/ETA 主要出现在 download 进度行中，和百分比一起解析。
            speed_match = SPEED_PATTERN.search(text)
            if speed_match:
                task.speed = speed_match.group(1).replace(" ", "")
            eta_match = ETA_PATTERN.search(text)
            if eta_match:
                eta_value = eta_match.group(1).strip()
                task.eta = eta_value if eta_value.lower() != "unknown" else None

        # 如果未来启用 --print-json，这里会尝试解析文件路径。
        if text.startswith("{") and text.endswith("}"):
            try:
                data = json.loads(text)
                filepath = data.get("_filename")
                if filepath:
                    task.result_path = filepath
            except json.JSONDecodeError:
                pass
        # 兼容常规文本输出：很多情况下不会有 JSON 行，需要从日志里直接提取最终文件路径。
        for pattern in RESULT_PATH_PATTERNS:
            match = pattern.search(text)
            if not match:
                continue
            candidate_path = match.group(1).strip().strip('"')
            # 对于中间分片文件，不覆盖已存在的最终结果路径，避免“打开文件”指向临时文件。
            if INTERMEDIATE_FRAGMENT_PATTERN.search(candidate_path):
                if not task.result_path:
                    task.result_path = candidate_path
                break
            task.result_path = candidate_path
            break
