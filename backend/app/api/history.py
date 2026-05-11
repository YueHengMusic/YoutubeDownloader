from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

import app.state as state_module
from app.models.task import TaskActionResponse

router = APIRouter(prefix="/api/history", tags=["history"])


@router.get("")
async def list_history(limit: int = Query(default=200, ge=1, le=1000)) -> list[dict]:
    """读取 SQLite 中的历史记录。"""
    if state_module.app_state is None:
        raise HTTPException(status_code=503, detail="App state not initialized")
    return state_module.app_state.history_repo.list_history(limit=limit)


@router.delete("/{task_id}")
async def delete_history(task_id: str) -> TaskActionResponse:
    """删除单条历史记录。"""
    if state_module.app_state is None:
        raise HTTPException(status_code=503, detail="App state not initialized")
    ok = state_module.app_state.history_repo.delete_history_item(task_id)
    if not ok:
        raise HTTPException(status_code=404, detail="History item not found")
    return TaskActionResponse(ok=True, message="History item deleted")


@router.delete("")
async def clear_history() -> TaskActionResponse:
    """清空全部历史记录。"""
    if state_module.app_state is None:
        raise HTTPException(status_code=503, detail="App state not initialized")
    deleted = state_module.app_state.history_repo.clear_history()
    return TaskActionResponse(ok=True, message=f"History cleared: {deleted}")
