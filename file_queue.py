import asyncio
import fcntl
import json
import shutil
from pathlib import Path


class Queue:
    def __init__(self, filepath: Path):
        filepath.parent.mkdir(parents=True, exist_ok=True)
        self.filepath = filepath

    async def put(self, value):
        with open(self.filepath, "a") as f:
            fcntl.lockf(f, fcntl.LOCK_EX)
            f.write(json.dumps(value) + "\n")
            fcntl.lockf(f, fcntl.LOCK_UN)

    async def get(self):
        while True:
            tmpfilepath = self.filepath.with_name(self.filepath.name + "tmp")
            with open(self.filepath, "a+") as f:
                fcntl.lockf(f, fcntl.LOCK_EX)
                f.seek(0)
                data = f.readline()
                with open(tmpfilepath, "a+") as tmpf:
                    tmpf.seek(0)
                    shutil.copyfileobj(f, tmpf)
                fcntl.lockf(f, fcntl.LOCK_UN)
            shutil.move(tmpfilepath, self.filepath)
            if data != "":
                return json.loads(data)
            await asyncio.sleep(0.1)
