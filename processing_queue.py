import json
import shutil
import time

path = "testfifo"


class Queue:
    def put(self, value):
        with open(path, "a") as fifo:
            fifo.write(json.dumps(value) + "\n")

    def get(self):
        while True:
            with open(path, "r") as fifo:
                data = fifo.readline()
                with open(path + "2", "w") as fifo2:
                    shutil.copyfileobj(fifo, fifo2)
            shutil.move(path + "2", path)
            if data != "":
                return json.loads(data)
            time.sleep(0.1)
