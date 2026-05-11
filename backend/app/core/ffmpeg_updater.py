from __future__ import annotations

import json
import os
import shutil
import subprocess
import tarfile
import tempfile
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Callable
from urllib.request import Request, urlopen


FFMPEG_RELEASE_API = "https://api.github.com/repos/yt-dlp/FFmpeg-Builds/releases/latest"


@dataclass
class FfmpegReleaseAsset:
    """
    FFmpeg 发布资产对象（只保留我们需要的字段，避免前后端耦合 GitHub 全量结构）。
    """

    name: str
    download_url: str


@dataclass
class FfmpegReleaseInfo:
    """
    FFmpeg 最新发布信息。
    id / published_at 用于判断是否需要更新（版本号不一定和 ffmpeg -version 一一对应）。
    """

    release_id: int
    tag_name: str
    published_at: str
    assets: list[FfmpegReleaseAsset]


class FfmpegUpdater:
    """
    负责 FFmpeg 的自动下载、更新检测与本地版本识别。

    设计目标（面向小白用户）：
    1) 没有 ffmpeg 时，一键下载可用版本；
    2) 已有 ffmpeg 时，给出“是否有更新”；
    3) 下载后自动解压并放到约定路径，前端无需关心复杂细节。
    """

    def __init__(self, ffmpeg_path: Path, platform_folder: str) -> None:
        self.ffmpeg_path = ffmpeg_path
        self.platform_folder = platform_folder
        self.meta_path = ffmpeg_path.with_suffix(ffmpeg_path.suffix + ".release.json")

    def _emit_terminal_event(self, terminal_callback: Callable[[dict], None] | None, stream: str, text: str) -> None:
        """
        统一终端输出入口：
        - 把检查/更新中的执行步骤持续写入同一条终端流；
        - 回调异常不影响更新器主逻辑，保证业务稳定性。
        """
        if terminal_callback is None:
            return
        try:
            terminal_callback({"stream": stream, "text": text})
        except Exception:  # noqa: BLE001
            return

    def get_installed_version(self, terminal_callback: Callable[[dict], None] | None = None) -> str | None:
        """
        通过执行 `ffmpeg -version` 读取本地版本。
        成功返回第一行（例如 `ffmpeg version ...`），失败返回 None。
        """
        if not self.ffmpeg_path.exists():
            self._emit_terminal_event(terminal_callback, "status", "ffmpeg binary not found, installed version = None")
            return None
        try:
            self._emit_terminal_event(terminal_callback, "command", f"{self.ffmpeg_path} -version")
            result = subprocess.run(
                [str(self.ffmpeg_path), "-version"],
                check=True,
                capture_output=True,
                text=True,
            )
            first_line = result.stdout.splitlines()[0] if result.stdout else ""
            version = first_line.strip() or None
            self._emit_terminal_event(terminal_callback, "stdout", f"ffmpeg version: {version or 'unknown'}")
            return version
        except Exception as exc:  # noqa: BLE001
            self._emit_terminal_event(terminal_callback, "status", f"failed to get ffmpeg version: {exc}")
            return None

    def _read_local_meta(self) -> dict | None:
        """
        读取本地记录的 release 元信息（由本工具下载成功后写入）。
        """
        if not self.meta_path.exists():
            return None
        try:
            return json.loads(self.meta_path.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            return None

    def _write_local_meta(self, payload: dict) -> None:
        """
        持久化本次下载对应的 release 元信息，供下次快速比较更新状态。
        """
        self.meta_path.parent.mkdir(parents=True, exist_ok=True)
        self.meta_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def fetch_latest_release(self, terminal_callback: Callable[[dict], None] | None = None) -> FfmpegReleaseInfo:
        """
        从 GitHub API 拉取 FFmpeg-Builds 最新发布信息。
        """
        self._emit_terminal_event(terminal_callback, "command", f"GET {FFMPEG_RELEASE_API}")
        request = Request(
            FFMPEG_RELEASE_API,
            headers={
                "Accept": "application/vnd.github+json",
                "User-Agent": "yt-dlp-gui-desktop",
            },
        )
        with urlopen(request, timeout=20) as response:  # noqa: S310 - 固定可信来源
            payload = json.loads(response.read().decode("utf-8"))

        assets = [
            FfmpegReleaseAsset(name=item["name"], download_url=item["browser_download_url"])
            for item in payload.get("assets", [])
            if "name" in item and "browser_download_url" in item
        ]
        return FfmpegReleaseInfo(
            release_id=int(payload["id"]),
            tag_name=str(payload["tag_name"]),
            published_at=str(payload["published_at"]),
            assets=assets,
        )

    def pick_asset(self, release: FfmpegReleaseInfo) -> FfmpegReleaseAsset:
        """
        按平台选择最合适的压缩包。

        当前策略：
        - Windows: 优先 win64-gpl.zip（非 shared，体积更大但常见兼容性更好）
        - macOS: 选择包含 macos + gpl 的包
        - Linux: 选择 linux64-gpl.tar.xz
        """
        asset_names = [item.name for item in release.assets]

        def find_first(predicate) -> FfmpegReleaseAsset | None:
            for asset in release.assets:
                if predicate(asset.name):
                    return asset
            return None

        if self.platform_folder == "windows":
            picked = find_first(lambda n: "win64-gpl.zip" in n and "shared" not in n)
            if picked:
                return picked
        elif self.platform_folder == "macos":
            picked = find_first(lambda n: "macos" in n and "gpl" in n and (n.endswith(".zip") or n.endswith(".tar.xz")))
            if picked:
                return picked
        else:
            picked = find_first(lambda n: "linux64-gpl.tar.xz" in n or ("linux64" in n and "gpl" in n))
            if picked:
                return picked

        raise RuntimeError(f"未找到适用于当前平台({self.platform_folder})的 FFmpeg 资产。可选项: {asset_names}")

    def _extract_archive(
        self,
        archive_path: Path,
        target_temp_dir: Path,
        terminal_callback: Callable[[dict], None] | None = None,
    ) -> None:
        """
        解压下载的压缩包到临时目录。
        """
        if archive_path.suffix == ".zip":
            self._emit_terminal_event(terminal_callback, "status", f"extract zip archive: {archive_path.name}")
            with zipfile.ZipFile(archive_path, "r") as zf:
                zf.extractall(target_temp_dir)
            return

        if archive_path.name.endswith(".tar.xz"):
            self._emit_terminal_event(terminal_callback, "status", f"extract tar.xz archive: {archive_path.name}")
            with tarfile.open(archive_path, mode="r:xz") as tf:
                tf.extractall(target_temp_dir)
            return

        raise RuntimeError(f"不支持的压缩格式: {archive_path.name}")

    def _locate_binary(self, root_dir: Path, binary_name: str) -> Path:
        """
        在解压目录中递归查找指定二进制文件。
        """
        for candidate in root_dir.rglob(binary_name):
            if candidate.is_file():
                return candidate
        raise RuntimeError(f"解压后未找到 {binary_name} 可执行文件")

    def download_latest(
        self,
        release: FfmpegReleaseInfo | None = None,
        terminal_callback: Callable[[dict], None] | None = None,
    ) -> dict[str, str]:
        """
        下载并安装最新 FFmpeg：
        1) 下载压缩包到临时目录；
        2) 解压并定位 ffmpeg 二进制；
        3) 覆盖到目标路径；
        4) 写入本地 release 元信息。
        """
        latest = release or self.fetch_latest_release(terminal_callback)
        asset = self.pick_asset(latest)
        self._emit_terminal_event(terminal_callback, "status", f"selected ffmpeg asset: {asset.name}")

        self.ffmpeg_path.parent.mkdir(parents=True, exist_ok=True)

        with tempfile.TemporaryDirectory(prefix="ffmpeg_update_") as temp_dir_str:
            temp_dir = Path(temp_dir_str)
            archive_path = temp_dir / asset.name

            self._emit_terminal_event(terminal_callback, "command", f"GET {asset.download_url}")
            request = Request(asset.download_url, headers={"User-Agent": "yt-dlp-gui-desktop"})
            with urlopen(request, timeout=120) as response:  # noqa: S310 - 固定可信来源
                payload = response.read()
                archive_path.write_bytes(payload)
            self._emit_terminal_event(terminal_callback, "stdout", f"downloaded ffmpeg bytes: {len(payload)}")

            extract_dir = temp_dir / "extract"
            extract_dir.mkdir(parents=True, exist_ok=True)
            self._extract_archive(archive_path, extract_dir, terminal_callback)

            ffmpeg_name = "ffmpeg.exe" if self.platform_folder == "windows" else "ffmpeg"
            ffprobe_name = "ffprobe.exe" if self.platform_folder == "windows" else "ffprobe"
            source_ffmpeg = self._locate_binary(extract_dir, ffmpeg_name)
            source_ffprobe = self._locate_binary(extract_dir, ffprobe_name)
            target_ffprobe = self.ffmpeg_path.with_name(ffprobe_name)

            shutil.copy2(source_ffmpeg, self.ffmpeg_path)
            shutil.copy2(source_ffprobe, target_ffprobe)
            self._emit_terminal_event(terminal_callback, "stdout", f"ffmpeg binary copied to: {self.ffmpeg_path}")
            self._emit_terminal_event(terminal_callback, "stdout", f"ffprobe binary copied to: {target_ffprobe}")

        # 非 Windows 平台要给执行权限，否则会出现“权限不足无法执行”。
        if os.name != "nt":
            ffprobe_path = self.ffmpeg_path.with_name("ffprobe")
            ffmpeg_mode = os.stat(self.ffmpeg_path).st_mode
            os.chmod(self.ffmpeg_path, ffmpeg_mode | 0o111)
            if ffprobe_path.exists():
                ffprobe_mode = os.stat(ffprobe_path).st_mode
                os.chmod(ffprobe_path, ffprobe_mode | 0o111)
            self._emit_terminal_event(
                terminal_callback,
                "stdout",
                "applied executable permission for ffmpeg/ffprobe binaries",
            )

        self._write_local_meta(
            {
                "release_id": latest.release_id,
                "tag_name": latest.tag_name,
                "published_at": latest.published_at,
                "asset": asset.name,
            }
        )

        return {
            "updated_to_release": latest.tag_name,
            "asset": asset.name,
            "path": str(self.ffmpeg_path),
        }

    def check_update_status(
        self,
        terminal_callback: Callable[[dict], None] | None = None,
    ) -> dict[str, str | bool | int | None]:
        """
        检查本地 FFmpeg 是否落后于最新发布。
        判定逻辑：
        - 若没有本地 release 元信息，且本地存在 ffmpeg，则给出“可能需要更新”；
        - 若有元信息，则比较 release_id。
        """
        self._emit_terminal_event(terminal_callback, "status", "checking ffmpeg update status...")
        latest = self.fetch_latest_release(terminal_callback)
        installed_version = self.get_installed_version(terminal_callback)
        local_meta = self._read_local_meta()
        local_release_id = int(local_meta["release_id"]) if local_meta and "release_id" in local_meta else None
        ffprobe_name = "ffprobe.exe" if self.platform_folder == "windows" else "ffprobe"
        ffprobe_path = self.ffmpeg_path.with_name(ffprobe_name)
        ffprobe_exists = ffprobe_path.exists()

        if local_release_id is None:
            has_update = installed_version is None or True
        else:
            has_update = local_release_id != latest.release_id
        # 关键兜底：即使 release 已最新，只要缺少 ffprobe 也必须重新安装同版本资产。
        if not ffprobe_exists:
            has_update = True

        self._emit_terminal_event(
            terminal_callback,
            "status",
            (
                f"ffmpeg has_update={has_update} "
                f"(local_release_id={local_release_id}, latest_release_id={latest.release_id}, ffprobe_exists={ffprobe_exists})"
            ),
        )
        if not ffprobe_exists:
            self._emit_terminal_event(
                terminal_callback,
                "status",
                f"ffprobe missing at {ffprobe_path}, will force reinstall ffmpeg package",
            )

        return {
            "installed_version": installed_version,
            "latest_release_id": latest.release_id,
            "latest_tag_name": latest.tag_name,
            "latest_published_at": latest.published_at,
            "local_release_id": local_release_id,
            "has_update": has_update,
            "binary_path": str(self.ffmpeg_path),
            "ffprobe_path": str(ffprobe_path),
            "ffprobe_exists": ffprobe_exists,
        }

    def ensure_latest(
        self,
        terminal_callback: Callable[[dict], None] | None = None,
    ) -> dict[str, str | bool | int | None]:
        """
        一键更新入口：若需要更新则下载，否则返回当前状态。
        """
        self._emit_terminal_event(terminal_callback, "status", "start ensure latest ffmpeg")
        status = self.check_update_status(terminal_callback)
        if status["has_update"] is True:
            result = self.download_latest(terminal_callback=terminal_callback)
            self._emit_terminal_event(terminal_callback, "status", "ffmpeg update completed")
            return {**status, **result, "updated": True}
        self._emit_terminal_event(terminal_callback, "status", "ffmpeg already latest, skip download")
        return {**status, "updated": False}
