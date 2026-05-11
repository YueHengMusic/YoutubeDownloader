from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.models.task import CreateTaskRequest, DownloadTask, TaskActionResponse
import app.state as state_module

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.get("")
async def list_tasks() -> list[DownloadTask]:
    """返回内存中的任务列表（按创建时间倒序）。"""
    if state_module.app_state is None:
        raise HTTPException(status_code=503, detail="App state not initialized")
    return state_module.app_state.queue_manager.list_tasks()


@router.post("")
async def create_task(payload: CreateTaskRequest) -> DownloadTask:
    """创建下载任务并加入队列。"""
    if state_module.app_state is None:
        raise HTTPException(status_code=503, detail="App state not initialized")
    if state_module.app_state.is_installing_yt_dlp or state_module.app_state.is_installing_ffmpeg:
        raise HTTPException(status_code=400, detail="Dependencies are still installing")
    yt_path = state_module.app_state.binary_locator.get_yt_dlp_path()
    ff_path = state_module.app_state.binary_locator.get_ffmpeg_path()
    if (not yt_path.exists()) or (not ff_path.exists()):
        raise HTTPException(status_code=400, detail="Dependencies are not installed")
    task = DownloadTask(**payload.model_dump())
    await state_module.app_state.queue_manager.add_task(task)
    return task


@router.post("/{task_id}/cancel")
async def cancel_task(task_id: str) -> TaskActionResponse:
    """尽力取消任务：只要任务还没结束，就会标记为 canceled。"""
    if state_module.app_state is None:
        raise HTTPException(status_code=503, detail="App state not initialized")
    ok = await state_module.app_state.queue_manager.cancel_task(task_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Task not found or not cancelable")
    return TaskActionResponse(ok=True, message="Task canceled")


@router.delete("/{task_id}")
async def delete_task(task_id: str) -> TaskActionResponse:
    """删除队列任务（运行中任务不可删除，请先取消）。"""
    if state_module.app_state is None:
        raise HTTPException(status_code=503, detail="App state not initialized")
    ok = state_module.app_state.queue_manager.remove_task(task_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Task not found or running")
    return TaskActionResponse(ok=True, message="Task deleted")
