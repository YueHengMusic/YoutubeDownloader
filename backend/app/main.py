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
    await state_module.app_state.queue_manager.start()

    async def ensure_missing_dependencies() -> None:
        """
        应用启动时自动处理“缺失依赖”：
        - 若 yt-dlp / ffmpeg 缺失则自动下载安装；
        - 若已安装则不主动更新，避免每次启动都触发远端请求。
        """
        if state_module.app_state is None:
            return

        app_state = state_module.app_state
        loop = asyncio.get_running_loop()

        def build_terminal_callback(source_id: str):
            def emit(payload: dict) -> None:
                stream = str(payload.get("stream", "stdout"))
                text = str(payload.get("text", "")).strip()
                if not text:
                    return
                asyncio.run_coroutine_threadsafe(
                    app_state.event_bus.publish(
                        {
                            "type": "terminal_output",
                            "data": {"task_id": source_id, "stream": stream, "text": text},
                        }
                    ),
                    loop,
                )

            return emit

        async def ensure_missing_yt_dlp() -> None:
            yt_path = app_state.binary_locator.get_yt_dlp_path()
            if yt_path.exists():
                return
            app_state.is_installing_yt_dlp = True
            try:
                await asyncio.to_thread(
                    app_state.yt_dlp_updater.ensure_latest,
                    build_terminal_callback("system-yt-dlp"),
                )
            except Exception:
                return
            finally:
                app_state.is_installing_yt_dlp = False

        async def ensure_missing_ffmpeg() -> None:
            ff_path = app_state.binary_locator.get_ffmpeg_path()
            if ff_path.exists():
                return
            app_state.is_installing_ffmpeg = True
            try:
                await asyncio.to_thread(
                    app_state.ffmpeg_updater.ensure_latest,
                    build_terminal_callback("system-ffmpeg"),
                )
            except Exception:
                return
            finally:
                app_state.is_installing_ffmpeg = False

        await asyncio.gather(ensure_missing_yt_dlp(), ensure_missing_ffmpeg())

    # 后台异步执行，避免阻塞后端服务启动。
    asyncio.create_task(ensure_missing_dependencies())


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
