
from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import asyncio
import os

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def get(request: Request):
    with open("/app/static/index.html") as f:
        return HTMLResponse(f.read())

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    # Start a persistent bash process
    process = await asyncio.create_subprocess_exec(
        "bash",
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
        env=os.environ.copy()
    )

    async def read_from_bash():
        while True:
            data = await process.stdout.read(1024)
            if not data:
                break
            await websocket.send_text(data.decode(errors="ignore"))

    reader_task = asyncio.create_task(read_from_bash())
    try:
        while True:
            msg = await websocket.receive_text()
            if process.stdin:
                process.stdin.write(msg.encode() + b"\n")
                await process.stdin.drain()
    except Exception:
        pass
    finally:
        reader_task.cancel()
        if process.stdin:
            process.stdin.close()
        await process.wait()
