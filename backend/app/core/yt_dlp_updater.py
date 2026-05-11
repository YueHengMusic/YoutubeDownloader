from __future__ import annotations

import json
import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Callable
from urllib.request import Request, urlopen


GITHUB_RELEASE_API = "https://api.github.com/repos/yt-dlp/yt-dlp/releases/latest"


@dataclass
class ReleaseAsset:
    name: str
    download_url: str


@dataclass
class ReleaseInfo:
    tag_name: str
    assets: list[ReleaseAsset]


class YtDlpUpdater:
    """
    管理 yt-dlp 可执行文件的生命周期。

    职责：
    1) 检测本地是否已安装以及安装版本；
    2) 查询 GitHub Release 最新稳定版；
    3) 下载并更新到 resources/bin/<平台>/ 路径。
    """

    def __init__(self, yt_dlp_path: Path, platform_folder: str) -> None:
        self.yt_dlp_path = yt_dlp_path
        self.platform_folder = platform_folder

    def _emit_terminal_event(self, terminal_callback: Callable[[dict], None] | None, stream: str, text: str) -> None:
        """
        统一终端输出入口：
        - 更新器内部所有“执行命令/关键输出”都走这里，确保前端看到一条完整流水；
        - 回调异常不影响更新主流程，避免“日志失败导致功能失败”。
        """
        if terminal_callback is None:
            return
        try:
            terminal_callback({"stream": stream, "text": text})
        except Exception:  # noqa: BLE001
            return

    def get_installed_version(self, terminal_callback: Callable[[dict], None] | None = None) -> str | None:
        """
        调用 `yt-dlp --version` 获取本地版本。
        当文件不存在或执行失败时返回 None。
        """
        if not self.yt_dlp_path.exists():
            self._emit_terminal_event(terminal_callback, "status", "yt-dlp binary not found, installed version = None")
            return None
        try:
            self._emit_terminal_event(terminal_callback, "command", f"{self.yt_dlp_path} --version")
            result = subprocess.run(
                [str(self.yt_dlp_path), "--version"],
                check=True,
                capture_output=True,
                text=True,
            )
            version = result.stdout.strip() or None
            self._emit_terminal_event(terminal_callback, "stdout", f"yt-dlp version: {version or 'unknown'}")
            return version
        except Exception as exc:  # noqa: BLE001
            self._emit_terminal_event(terminal_callback, "status", f"failed to get yt-dlp version: {exc}")
            return None

    def fetch_latest_release(self, terminal_callback: Callable[[dict], None] | None = None) -> ReleaseInfo:
        """
        从 GitHub API 获取最新稳定版发布信息。
        """
        self._emit_terminal_event(terminal_callback, "command", f"GET {GITHUB_RELEASE_API}")
        request = Request(
            GITHUB_RELEASE_API,
            headers={
                "Accept": "application/vnd.github+json",
                "User-Agent": "yt-dlp-gui-desktop",
            },
        )
        with urlopen(request, timeout=20) as response:  # noqa: S310 - trusted fixed URL
            payload = json.loads(response.read().decode("utf-8"))
        assets = [
            ReleaseAsset(name=item["name"], download_url=item["browser_download_url"])
            for item in payload.get("assets", [])
            if "name" in item and "browser_download_url" in item
        ]
        self._emit_terminal_event(
            terminal_callback,
            "stdout",
            f"latest yt-dlp release: {payload['tag_name']}, assets={len(assets)}",
        )
        return ReleaseInfo(tag_name=payload["tag_name"], assets=assets)

    def pick_asset(self, release: ReleaseInfo) -> ReleaseAsset:
        """
        根据当前平台选择最合适的资源文件。
        """
        candidates: list[str]
        if self.platform_folder == "windows":
            candidates = ["yt-dlp.exe", "yt-dlp_win.zip"]
        elif self.platform_folder == "macos":
            candidates = ["yt-dlp_macos", "yt-dlp_macos.zip"]
        else:
            candidates = ["yt-dlp_linux", "yt-dlp"]

        for candidate in candidates:
            for asset in release.assets:
                if asset.name == candidate:
                    return asset
        raise RuntimeError(f"No suitable yt-dlp asset found for platform {self.platform_folder}")

    def download_latest(
        self,
        release: ReleaseInfo | None = None,
        terminal_callback: Callable[[dict], None] | None = None,
    ) -> dict[str, str]:
        """
        下载最新 yt-dlp 到目标平台目录。
        """
        latest = release or self.fetch_latest_release(terminal_callback)
        asset = self.pick_asset(latest)
        self._emit_terminal_event(
            terminal_callback,
            "status",
            f"selected yt-dlp asset: {asset.name}",
        )

        self.yt_dlp_path.parent.mkdir(parents=True, exist_ok=True)
        self._emit_terminal_event(
            terminal_callback,
            "command",
            f"GET {asset.download_url}",
        )
        request = Request(asset.download_url, headers={"User-Agent": "yt-dlp-gui-desktop"})
        with urlopen(request, timeout=60) as response:  # noqa: S310 - trusted GitHub URL
            data = response.read()
        self._emit_terminal_event(
            terminal_callback,
            "stdout",
            f"downloaded yt-dlp bytes: {len(data)}",
        )

        if asset.name.endswith(".zip"):
            raise RuntimeError("Zip assets are not supported yet; please use standalone binary asset.")

        with open(self.yt_dlp_path, "wb") as output_file:
            output_file.write(data)
        self._emit_terminal_event(
            terminal_callback,
            "stdout",
            f"yt-dlp binary saved to: {self.yt_dlp_path}",
        )

        # 非 Windows 平台补执行权限，避免“权限不足无法运行”。
        if os.name != "nt":
            current_mode = os.stat(self.yt_dlp_path).st_mode
            os.chmod(self.yt_dlp_path, current_mode | 0o111)
            self._emit_terminal_event(
                terminal_callback,
                "stdout",
                "applied executable permission for yt-dlp binary",
            )

        return {
            "updated_to": latest.tag_name,
            "asset": asset.name,
            "path": str(self.yt_dlp_path),
        }

    def check_update_status(
        self,
        terminal_callback: Callable[[dict], None] | None = None,
    ) -> dict[str, str | bool | None]:
        """
        比较本地版本与最新版本标签，返回是否需要更新。
        """
        self._emit_terminal_event(terminal_callback, "status", "checking yt-dlp update status...")
        latest = self.fetch_latest_release(terminal_callback)
        installed = self.get_installed_version(terminal_callback)
        has_update = installed != latest.tag_name
        self._emit_terminal_event(
            terminal_callback,
            "status",
            f"yt-dlp has_update={has_update} (installed={installed}, latest={latest.tag_name})",
        )
        return {
            "installed_version": installed,
            "latest_version": latest.tag_name,
            "has_update": has_update,
            "binary_path": str(self.yt_dlp_path),
        }

    def ensure_latest(
        self,
        terminal_callback: Callable[[dict], None] | None = None,
    ) -> dict[str, str | bool | None]:
        """
        一键保证本地有可用最新版：
        - 没有安装：下载
        - 版本不一致：下载更新
        - 已是最新：直接返回状态
        """
        self._emit_terminal_event(terminal_callback, "status", "start ensure latest yt-dlp")
        status = self.check_update_status(terminal_callback)
        if status["has_update"] is True:
            result = self.download_latest(terminal_callback=terminal_callback)
            self._emit_terminal_event(terminal_callback, "status", "yt-dlp update completed")
            return {**status, **result, "updated": True}
        self._emit_terminal_event(terminal_callback, "status", "yt-dlp already latest, skip download")
        return {**status, "updated": False}
