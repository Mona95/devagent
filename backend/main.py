import asyncio
import json
import os
import queue
import threading

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from agent.agent import DevAgent

load_dotenv()

app = FastAPI(title="DevAgent API", version="1.0.0")

ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:5173"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TaskRequest(BaseModel):
    task: str = Field(min_length=1, max_length=2000)


def to_sse(event: dict) -> str:
    """Format one event in Server-Sent Events wire format."""
    return f"data: {json.dumps(event)}\n\n"


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "DevAgent API"}


@app.post("/api/run")
@app.post("/api/run")
async def run_task(body: TaskRequest, request: Request):
    events: queue.Queue = queue.Queue()
    cancel = threading.Event()
    DONE = object()

    def worker():
        try:
            agent = DevAgent()
            agent.run(
                body.task,
                stream_callback=events.put,
                should_cancel=cancel.is_set,
            )
        except Exception as e:
            events.put({"type": "error", "content": str(e)})
        finally:
            events.put(DONE)

    threading.Thread(target=worker, daemon=True).start()

    async def event_stream():
        try:
            while True:
                try:
                    # Wait up to 1s in a helper thread so the event loop stays free
                    event = await asyncio.to_thread(events.get, True, 1.0)
                except queue.Empty:
                    # Nothing arrived: good moment to check the client is still there
                    if await request.is_disconnected():
                        break
                    continue

                if event is DONE:
                    break
                yield to_sse(event)
        finally:
            cancel.set()  # runs on normal finish, disconnect or error

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )