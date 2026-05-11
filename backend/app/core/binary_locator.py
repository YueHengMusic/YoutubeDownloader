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
        兼容以下常见布局：
        1) 开发态：<repo>/resources/bin
        2) 打包态A：<resources>/bin（base_dir 可能是 <resources>）
        3) 打包态B：<resources>/bin（base_dir 可能是 <resources>/backend）
        """
        candidates = [
            # 开发态：仓库根目录下 resources/bin
            self.base_dir / "resources" / "bin",
            # 打包态：base_dir 本身就是 resources
            self.base_dir / "bin",
            # 打包态：base_dir 是 resources/backend
            self.base_dir.parent / "bin",
        ]
        for candidate in candidates:
            if candidate.exists():
                return candidate
        # 若都不存在，优先回退到开发态结构，便于后续安装流程自动创建目录。
        return candidates[0]

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

    def get_ffprobe_path(self) -> Path:
        """
        ffprobe 与 ffmpeg 通常位于同一目录。
        yt-dlp 的部分后处理能力会依赖 ffprobe，因此需要单独定位与校验。
        """
        folder = self.detect_platform_folder()
        exe = "ffprobe.exe" if folder == "windows" else "ffprobe"
        return self.get_bin_root() / folder / exe
