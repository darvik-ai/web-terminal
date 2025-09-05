
from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import asyncio
import os
import pty
import threading

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def get(request: Request):
    with open("/app/static/index.html") as f:
        return HTMLResponse(f.read())

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    loop = asyncio.get_event_loop()
    # Create a PTY for the bash shell
    master_fd, slave_fd = pty.openpty()

    pid = os.fork()
    if pid == 0:
        # Child process: replace with bash
        os.setsid()
        os.dup2(slave_fd, 0)
        os.dup2(slave_fd, 1)
        os.dup2(slave_fd, 2)
        os.execv("/bin/bash", ["bash"])
    else:
        # Parent process: stream PTY I/O
        def read_pty():
            while True:
                try:
                    data = os.read(master_fd, 1024)
                    if not data:
                        break
                    coro = websocket.send_text(data.decode(errors="ignore"))
                    asyncio.run_coroutine_threadsafe(coro, loop)
                except Exception:
                    break

        thread = threading.Thread(target=read_pty, daemon=True)
        thread.start()

        try:
            while True:
                msg = await websocket.receive_text()
                os.write(master_fd, msg.encode() + b"\n")
        except Exception:
            pass
        finally:
            thread.join(timeout=1)
            os.close(master_fd)
            os.close(slave_fd)
