from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

import app.state as state_module

router = APIRouter(prefix="/api/history", tags=["history"])


@router.get("")
async def list_history(limit: int = Query(default=200, ge=1, le=1000)) -> list[dict]:
    """读取 SQLite 中的历史记录。"""
    if state_module.app_state is None:
        raise HTTPException(status_code=503, detail="App state not initialized")
    return state_module.app_state.history_repo.list_history(limit=limit)
