from __future__ import annotations

import platform
from pathlib import Path


class BinaryLocator:
    """
    负责定位 yt-dlp / ffmpeg 可执行文件路径。
    同时兼容两种目录结构：
    - 开发态：repo_root/resources/bin/...
    - 打包态：<resources>/bin/...
    """

    def __init__(self, base_dir: Path) -> None:
        self.base_dir = base_dir

    def get_bin_root(self) -> Path:
        """
        动态推导二进制根目录。
        """
        dev_style = self.base_dir / "resources" / "bin"
        if dev_style.exists() or (self.base_dir / "resources").exists():
            return dev_style
        # 打包后 backend 通常位于 <resources>/backend，因此 bin 在其同级目录。
        return self.base_dir.parent / "bin"

    def detect_platform_folder(self) -> str:
        """
        把系统名称映射成资源目录约定名称。
        """
        sys = platform.system().lower()
        if "windows" in sys:
            return "windows"
        if "darwin" in sys:
            return "macos"
        return "linux"

    def get_yt_dlp_path(self) -> Path:
        folder = self.detect_platform_folder()
        exe = "yt-dlp.exe" if folder == "windows" else "yt-dlp"
        return self.get_bin_root() / folder / exe

    def get_ffmpeg_path(self) -> Path:
        folder = self.detect_platform_folder()
        exe = "ffmpeg.exe" if folder == "windows" else "ffmpeg"
        return self.get_bin_root() / folder / exe
