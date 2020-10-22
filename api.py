from fastapi import FastAPI
from pydantic import BaseModel

from file_queue import Queue

queue = Queue("./queuefile")
app = FastAPI()


class Request(BaseModel):
    url: str


@app.post("/")
async def index(request: Request):
    await queue.put({"url": request.url})
    return {"Hello": "World"}
