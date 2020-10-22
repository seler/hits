import asyncio
import json
import shutil


class Queue:
    def __init__(self, filepath):
        self.filepath = filepath

    async def put(self, value):
        with open(self.filepath, "a") as fifo:
            fifo.write(json.dumps(value) + "\n")

    async def get(self):
        while True:
            with open(self.filepath, "a+") as fifo:
                fifo.seek(0)
                data = fifo.readline()
                with open(self.filepath + "2", "a+") as fifo2:
                    fifo2.seek(0)
                    shutil.copyfileobj(fifo, fifo2)
            shutil.move(self.filepath + "2", self.filepath)
            if data != "":
                return json.loads(data)
            await asyncio.sleep(0.1)
