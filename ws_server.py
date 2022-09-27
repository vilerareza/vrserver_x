import asyncio
import time
from threading import Condition, Lock

import websockets

class Frame(object):
    def __init__(self) -> None:
        self.condition = Condition(lock = Lock())
        self.content = bytes()

# New
frames = {}

async def on_connect(websocket):
    global frames
    
    async def receive(websocket):
        while True:
            try:
                with frames[websocket.path].condition:
                    frames[websocket.path].content = await websocket.recv()
                    frames[websocket.path].condition.notify_all()
                    #print ('receive')
            except websockets.ConnectionClosedOK:
                break
    
    async def send(websocket):
        while True:
            try:
                with frames[websocket.path].condition:
                    frames[websocket.path].condition.wait()
                    await websocket.send(frames[websocket.path].content)
                    print ('send')
            except websockets.ConnectionClosedOK:
                break

    source, device = websocket.path.split('/')[0], websocket.path.split('/')[0]
    print (f'Connection request, {websocket.path}')
    frames [device] = Frame()
    if source == 'device':
        await receive(websocket)
    else:
        await send(websocket)

async def main():
    async with websockets.serve(on_connect, "0.0.0.0", 8000):
        await asyncio.Future()

asyncio.run (main())
