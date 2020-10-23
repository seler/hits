from pathlib import Path

from fastapi import FastAPI
from pydantic import BaseModel, BaseSettings

from file_queue import Queue


class Settings(BaseSettings):
    queue_file: Path


class Request(BaseModel):
    url: str


settings = Settings()
queue = Queue(settings.queue_file)
app = FastAPI()


@app.post("/")
async def index(request: Request):
    await queue.put({"url": request.url})
    return {"Hello": "World"}
