from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.core.cookie_manager import CookieManager

router = APIRouter(prefix="/api/cookies", tags=["cookies"])


class ImportCookieRequest(BaseModel):
    path: str = Field(min_length=1)


@router.post("/import")
async def import_cookies(payload: ImportCookieRequest) -> dict[str, str]:
    """校验用户选择的 cookies.txt，避免任务启动后才报错。"""
    try:
        CookieManager.validate_cookie_file(payload.path)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"ok": "true", "path": payload.path}
