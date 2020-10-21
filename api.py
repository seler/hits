from flask import Flask, request
from processing_queue import Queue

app = Flask(__name__)
queue = Queue()


@app.route("/", methods=["POST"])
def schedule():
    queue.put(request.get_json())
    return ""
