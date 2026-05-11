from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from app.core.binary_locator import BinaryLocator
from app.core.event_bus import EventBus
from app.core.ffmpeg_updater import FfmpegUpdater
from app.core.queue_manager import QueueManager
from app.core.yt_dlp_updater import YtDlpUpdater
from app.core.yt_dlp_runner import YtDlpRunner
from app.models.task import DownloadTask
from app.storage.history_repo import HistoryRepository
from app.storage.settings_repo import SettingsRepository


@dataclass
class AppState:
    # Runtime helpers and services shared by API handlers.
    # 所有 API 都通过这里拿到共享单例，避免每次请求重复初始化重对象。
    binary_locator: BinaryLocator
    history_repo: HistoryRepository
    event_bus: EventBus
    runner: YtDlpRunner
    yt_dlp_updater: YtDlpUpdater
    ffmpeg_updater: FfmpegUpdater
    queue_manager: QueueManager
    settings_repo: SettingsRepository


app_state: AppState | None = None


def init_state() -> AppState:
    # 开发态：root 通常是仓库根目录。
    # 打包态：root 通常会解析到 <resources>/backend。
    root = Path(__file__).resolve().parents[2]
    backend_root = root if (root / "app").exists() else root / "backend"
    binary_locator = BinaryLocator(base_dir=root)
    history_repo = HistoryRepository(db_path=backend_root / "data" / "history.db")
    settings_repo = SettingsRepository(settings_path=backend_root / "data" / "settings.json")
    event_bus = EventBus()
    yt_dlp_updater = YtDlpUpdater(
        yt_dlp_path=binary_locator.get_yt_dlp_path(),
        platform_folder=binary_locator.detect_platform_folder(),
    )
    ffmpeg_updater = FfmpegUpdater(
        ffmpeg_path=binary_locator.get_ffmpeg_path(),
        platform_folder=binary_locator.detect_platform_folder(),
    )
    runner = YtDlpRunner(
        yt_dlp_path=binary_locator.get_yt_dlp_path(),
        ffmpeg_path=binary_locator.get_ffmpeg_path(),
        terminal_callback=lambda payload: event_bus.publish(
            {"type": "terminal_output", "data": payload}
        ),
    )

    async def on_update(task: DownloadTask) -> None:
        # 每次状态变化都立即落库 + 广播，保证重启后历史可恢复、前端可实时刷新。
        history_repo.upsert_task(task)
        await event_bus.publish({"type": "task_update", "data": task.model_dump(mode="json")})

    # 并发下载数从用户设置读取，默认 2，上限由设置仓库统一约束。
    queue_manager = QueueManager(
        runner=runner.run,
        on_update=on_update,
        concurrency=settings_repo.get_download_concurrency(),
    )
    return AppState(
        binary_locator=binary_locator,
        history_repo=history_repo,
        event_bus=event_bus,
        runner=runner,
        yt_dlp_updater=yt_dlp_updater,
        ffmpeg_updater=ffmpeg_updater,
        queue_manager=queue_manager,
        settings_repo=settings_repo,
    )
