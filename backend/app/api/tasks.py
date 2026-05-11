from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.models.task import CreateTaskRequest, DownloadTask, TaskActionResponse, TaskStatus
import app.state as state_module

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.get("")
async def list_tasks() -> list[DownloadTask]:
    """返回内存中的任务列表（按创建时间倒序）。"""
    if state_module.app_state is None:
        raise HTTPException(status_code=503, detail="App state not initialized")
    return state_module.app_state.queue_manager.list_tasks()


def _ensure_dependencies_ready() -> None:
    """创建/重试任务前统一校验依赖状态。"""
    if state_module.app_state is None:
        raise HTTPException(status_code=503, detail="App state not initialized")
    if (
        state_module.app_state.is_installing_yt_dlp
        or state_module.app_state.is_installing_ffmpeg
        or state_module.app_state.yt_dlp_install_lock.locked()
        or state_module.app_state.ffmpeg_install_lock.locked()
    ):
        raise HTTPException(status_code=400, detail="Dependencies are still installing")
    yt_path = state_module.app_state.binary_locator.get_yt_dlp_path()
    ff_path = state_module.app_state.binary_locator.get_ffmpeg_path()
    ffprobe_path = state_module.app_state.binary_locator.get_ffprobe_path()
    if (not yt_path.exists()) or (not ff_path.exists()) or (not ffprobe_path.exists()):
        raise HTTPException(status_code=400, detail="Dependencies are not installed")


@router.post("")
async def create_task(payload: CreateTaskRequest) -> DownloadTask:
    """创建下载任务并加入队列。"""
    _ensure_dependencies_ready()
    task = DownloadTask(**payload.model_dump())
    await state_module.app_state.queue_manager.add_task(task)
    return task


@router.post("/{task_id}/retry")
async def retry_task(task_id: str) -> DownloadTask:
    """
    重试失败任务：
    - 仅允许 `failed` 状态；
    - 使用原任务参数创建一个新的任务 ID 重新入队。
    """
    _ensure_dependencies_ready()
    if state_module.app_state is None:
        raise HTTPException(status_code=503, detail="App state not initialized")
    source_task = state_module.app_state.queue_manager.tasks.get(task_id)
    if source_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    if source_task.status != TaskStatus.failed:
        raise HTTPException(status_code=400, detail="Only failed tasks can be retried")

    request_fields = source_task.model_dump(
        exclude={"id", "status", "progress", "speed", "eta", "log", "error", "result_path", "created_at", "updated_at"}
    )
    new_task = DownloadTask(**request_fields)
    await state_module.app_state.queue_manager.add_task(new_task)
    return new_task


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
