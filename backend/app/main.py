from __future__ import annotations

import asyncio
import json

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from app.api.cookies import router as cookies_router
from app.api.history import router as history_router
from app.api.system import router as system_router
from app.api.tasks import router as tasks_router
import app.state as state_module


app = FastAPI(title="yt-dlp desktop backend")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup() -> None:
    # 先初始化应用共享状态（队列、更新器、存储、事件总线等）。
    state_module.app_state = state_module.init_state()
    # 后台异步执行 yt-dlp 检查/更新，避免阻塞服务启动。
    async def ensure_yt_dlp_latest() -> None:
        if state_module.app_state is None:
            return
        try:
            await asyncio.to_thread(state_module.app_state.yt_dlp_updater.ensure_latest)
        except Exception:
            # 网络问题或 GitHub 限流都不应导致应用整体启动失败。
            return

    asyncio.create_task(ensure_yt_dlp_latest())
    await state_module.app_state.queue_manager.start()


@app.on_event("shutdown")
async def shutdown() -> None:
    await state_module.app_state.queue_manager.shutdown()


app.include_router(tasks_router)
app.include_router(history_router)
app.include_router(cookies_router)
app.include_router(system_router)


@app.get("/")
async def root() -> dict[str, str]:
    """
    根路径说明（避免用户直接访问 8000 时看到 404 误以为服务异常）。
    """
    return {
        "message": "yt-dlp desktop backend is running",
        "hint": "Use /api/* endpoints from desktop frontend",
    }


@app.websocket("/ws/tasks")
async def ws_tasks(ws: WebSocket) -> None:
    if state_module.app_state is None:
        await ws.close(code=1011)
        return
    await ws.accept()
    try:
        async for event in state_module.app_state.event_bus.subscribe():
            await ws.send_text(json.dumps(event))
    except WebSocketDisconnect:
        return
