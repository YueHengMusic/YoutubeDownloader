import asyncio
import json
import urllib.request

import websockets

async def main():
    async with websockets.connect('ws://127.0.0.1:8000/ws/tasks') as ws:
        urllib.request.urlopen('http://127.0.0.1:8000/api/system/ffmpeg/update-status').read()
        events = []
        for _ in range(10):
            try:
                msg = await asyncio.wait_for(ws.recv(), timeout=1.2)
            except Exception:
                break
            events.append(json.loads(msg))
        print('events=', len(events))
        print(json.dumps(events, ensure_ascii=False, indent=2))

asyncio.run(main())
