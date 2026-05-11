from __future__ import annotations

import asyncio
from collections.abc import AsyncGenerator


class EventBus:
    def __init__(self) -> None:
        self._listeners: set[asyncio.Queue[dict]] = set()

    async def publish(self, event: dict) -> None:
        """把一个事件广播给所有订阅者。"""
        for queue in list(self._listeners):
            await queue.put(event)

    async def subscribe(self) -> AsyncGenerator[dict, None]:
        """为每个客户端创建独立队列，并持续产出事件直到断开。"""
        queue: asyncio.Queue[dict] = asyncio.Queue()
        self._listeners.add(queue)
        try:
            while True:
                event = await queue.get()
                yield event
        finally:
            self._listeners.discard(queue)
