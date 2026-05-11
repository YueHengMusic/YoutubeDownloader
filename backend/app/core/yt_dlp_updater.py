from __future__ import annotations

import json
import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
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

    def get_installed_version(self) -> str | None:
        """
        调用 `yt-dlp --version` 获取本地版本。
        当文件不存在或执行失败时返回 None。
        """
        if not self.yt_dlp_path.exists():
            return None
        try:
            result = subprocess.run(
                [str(self.yt_dlp_path), "--version"],
                check=True,
                capture_output=True,
                text=True,
            )
            return result.stdout.strip() or None
        except Exception:  # noqa: BLE001
            return None

    def fetch_latest_release(self) -> ReleaseInfo:
        """
        从 GitHub API 获取最新稳定版发布信息。
        """
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

    def download_latest(self, release: ReleaseInfo | None = None) -> dict[str, str]:
        """
        下载最新 yt-dlp 到目标平台目录。
        """
        latest = release or self.fetch_latest_release()
        asset = self.pick_asset(latest)

        self.yt_dlp_path.parent.mkdir(parents=True, exist_ok=True)
        request = Request(asset.download_url, headers={"User-Agent": "yt-dlp-gui-desktop"})
        with urlopen(request, timeout=60) as response:  # noqa: S310 - trusted GitHub URL
            data = response.read()

        if asset.name.endswith(".zip"):
            raise RuntimeError("Zip assets are not supported yet; please use standalone binary asset.")

        with open(self.yt_dlp_path, "wb") as output_file:
            output_file.write(data)

        # 非 Windows 平台补执行权限，避免“权限不足无法运行”。
        if os.name != "nt":
            current_mode = os.stat(self.yt_dlp_path).st_mode
            os.chmod(self.yt_dlp_path, current_mode | 0o111)

        return {
            "updated_to": latest.tag_name,
            "asset": asset.name,
            "path": str(self.yt_dlp_path),
        }

    def check_update_status(self) -> dict[str, str | bool | None]:
        """
        比较本地版本与最新版本标签，返回是否需要更新。
        """
        latest = self.fetch_latest_release()
        installed = self.get_installed_version()
        has_update = installed != latest.tag_name
        return {
            "installed_version": installed,
            "latest_version": latest.tag_name,
            "has_update": has_update,
            "binary_path": str(self.yt_dlp_path),
        }

    def ensure_latest(self) -> dict[str, str | bool | None]:
        """
        一键保证本地有可用最新版：
        - 没有安装：下载
        - 版本不一致：下载更新
        - 已是最新：直接返回状态
        """
        status = self.check_update_status()
        if status["has_update"] is True:
            result = self.download_latest()
            return {**status, **result, "updated": True}
        return {**status, "updated": False}
