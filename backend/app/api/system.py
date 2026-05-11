from __future__ import annotations

import asyncio
from typing import Callable

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

import app.state as state_module
from app.storage.settings_repo import SettingsRepository

router = APIRouter(prefix="/api/system", tags=["system"])


class AppSettingsResponse(BaseModel):
    """系统设置响应模型。"""

    download_concurrency: int
    min_download_concurrency: int
    max_download_concurrency: int
    default_download_concurrency: int


class UpdateAppSettingsRequest(BaseModel):
    """系统设置更新请求模型。"""

    download_concurrency: int = Field(
        ge=SettingsRepository.MIN_DOWNLOAD_CONCURRENCY,
        le=SettingsRepository.MAX_DOWNLOAD_CONCURRENCY,
    )


def _build_terminal_callback(source_id: str) -> Callable[[dict], None]:
    """
    创建线程安全的终端事件回调：
    - system 接口中的更新检查/下载逻辑运行在 `asyncio.to_thread` 线程池；
    - 这里把线程中的日志安全投递回主事件循环，再统一广播到前端 WebSocket。
    """
    if state_module.app_state is None:
        raise RuntimeError("App state not initialized")
    loop = asyncio.get_running_loop()
    event_bus = state_module.app_state.event_bus

    def emit(payload: dict) -> None:
        stream = str(payload.get("stream", "stdout"))
        text = str(payload.get("text", "")).strip()
        if not text:
            return
        asyncio.run_coroutine_threadsafe(
            event_bus.publish(
                {
                    "type": "terminal_output",
                    "data": {
                        "task_id": source_id,
                        "stream": stream,
                        "text": text,
                    },
                }
            ),
            loop,
        )

    return emit


def _build_settings_response(download_concurrency: int) -> AppSettingsResponse:
    return AppSettingsResponse(
        download_concurrency=download_concurrency,
        min_download_concurrency=SettingsRepository.MIN_DOWNLOAD_CONCURRENCY,
        max_download_concurrency=SettingsRepository.MAX_DOWNLOAD_CONCURRENCY,
        default_download_concurrency=SettingsRepository.DEFAULT_DOWNLOAD_CONCURRENCY,
    )


@router.get("/settings")
async def get_settings() -> AppSettingsResponse:
    """
    读取应用设置（当前仅包含并发下载数）。
    """
    if state_module.app_state is None:
        raise HTTPException(status_code=503, detail="App state not initialized")
    download_concurrency = state_module.app_state.settings_repo.get_download_concurrency()
    return _build_settings_response(download_concurrency)


@router.put("/settings")
async def update_settings(payload: UpdateAppSettingsRequest) -> AppSettingsResponse:
    """
    更新应用设置并立即应用到运行中的队列。
    """
    if state_module.app_state is None:
        raise HTTPException(status_code=503, detail="App state not initialized")
    saved_value = state_module.app_state.settings_repo.set_download_concurrency(payload.download_concurrency)
    applied_value = await state_module.app_state.queue_manager.set_concurrency(saved_value)
    return _build_settings_response(applied_value)


@router.get("/dependencies")
async def dependencies() -> dict:
    """
    返回依赖文件存在性信息。
    目的：让设置页可以直观看到本地是否已有 yt-dlp / ffmpeg。
    """
    if state_module.app_state is None:
        raise HTTPException(status_code=503, detail="App state not initialized")
    yt_path = state_module.app_state.binary_locator.get_yt_dlp_path()
    ff_path = state_module.app_state.binary_locator.get_ffmpeg_path()
    return {
        "yt_dlp": {
            "path": str(yt_path),
            "exists": yt_path.exists(),
            "installing": state_module.app_state.is_installing_yt_dlp,
        },
        "ffmpeg": {
            "path": str(ff_path),
            "exists": ff_path.exists(),
            "installing": state_module.app_state.is_installing_ffmpeg,
        },
    }


@router.get("/yt-dlp/update-status")
async def yt_dlp_update_status() -> dict:
    """
    查询 yt-dlp 更新状态：本地版本、最新版本、是否需要更新。
    """
    if state_module.app_state is None:
        raise HTTPException(status_code=503, detail="App state not initialized")
    terminal_callback = _build_terminal_callback("system-yt-dlp")
    return await asyncio.to_thread(state_module.app_state.yt_dlp_updater.check_update_status, terminal_callback)


@router.post("/yt-dlp/update")
async def yt_dlp_update() -> dict:
    """
    一键下载/更新 yt-dlp。
    """
    if state_module.app_state is None:
        raise HTTPException(status_code=503, detail="App state not initialized")
    try:
        state_module.app_state.is_installing_yt_dlp = True
        terminal_callback = _build_terminal_callback("system-yt-dlp")
        return await asyncio.to_thread(state_module.app_state.yt_dlp_updater.ensure_latest, terminal_callback)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"yt-dlp update failed: {exc}") from exc
    finally:
        state_module.app_state.is_installing_yt_dlp = False


@router.get("/ffmpeg/update-status")
async def ffmpeg_update_status() -> dict:
    """
    查询 ffmpeg 更新状态：本地版本、本地发布ID、最新发布信息、是否需要更新。
    """
    if state_module.app_state is None:
        raise HTTPException(status_code=503, detail="App state not initialized")
    terminal_callback = _build_terminal_callback("system-ffmpeg")
    return await asyncio.to_thread(state_module.app_state.ffmpeg_updater.check_update_status, terminal_callback)


@router.post("/ffmpeg/update")
async def ffmpeg_update() -> dict:
    """
    一键下载/更新 ffmpeg。
    """
    if state_module.app_state is None:
        raise HTTPException(status_code=503, detail="App state not initialized")
    try:
        state_module.app_state.is_installing_ffmpeg = True
        terminal_callback = _build_terminal_callback("system-ffmpeg")
        return await asyncio.to_thread(state_module.app_state.ffmpeg_updater.ensure_latest, terminal_callback)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"ffmpeg update failed: {exc}") from exc
    finally:
        state_module.app_state.is_installing_ffmpeg = False
