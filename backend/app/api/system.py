from __future__ import annotations

import asyncio

from fastapi import APIRouter, HTTPException

import app.state as state_module

router = APIRouter(prefix="/api/system", tags=["system"])


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
        "yt_dlp": {"path": str(yt_path), "exists": yt_path.exists()},
        "ffmpeg": {"path": str(ff_path), "exists": ff_path.exists()},
    }


@router.get("/yt-dlp/update-status")
async def yt_dlp_update_status() -> dict:
    """
    查询 yt-dlp 更新状态：本地版本、最新版本、是否需要更新。
    """
    if state_module.app_state is None:
        raise HTTPException(status_code=503, detail="App state not initialized")
    return await asyncio.to_thread(state_module.app_state.yt_dlp_updater.check_update_status)


@router.post("/yt-dlp/update")
async def yt_dlp_update() -> dict:
    """
    一键下载/更新 yt-dlp。
    """
    if state_module.app_state is None:
        raise HTTPException(status_code=503, detail="App state not initialized")
    try:
        return await asyncio.to_thread(state_module.app_state.yt_dlp_updater.ensure_latest)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"yt-dlp update failed: {exc}") from exc


@router.get("/ffmpeg/update-status")
async def ffmpeg_update_status() -> dict:
    """
    查询 ffmpeg 更新状态：本地版本、本地发布ID、最新发布信息、是否需要更新。
    """
    if state_module.app_state is None:
        raise HTTPException(status_code=503, detail="App state not initialized")
    return await asyncio.to_thread(state_module.app_state.ffmpeg_updater.check_update_status)


@router.post("/ffmpeg/update")
async def ffmpeg_update() -> dict:
    """
    一键下载/更新 ffmpeg。
    """
    if state_module.app_state is None:
        raise HTTPException(status_code=503, detail="App state not initialized")
    try:
        return await asyncio.to_thread(state_module.app_state.ffmpeg_updater.ensure_latest)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"ffmpeg update failed: {exc}") from exc
