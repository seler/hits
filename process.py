import json
import logging
import subprocess
import sys

import youtube_dl

from processing_queue import Queue

logger = logging.getLogger(__name__)


def convert(url):
    info = youtube_dl.YoutubeDL().extract_info(url, download=False)
    video_file_url = info["requested_formats"][0]["url"]
    audio_file_url = info["requested_formats"][1]["url"]

    # fmt: off
    cmd = [
        "ffmpeg", "-i", video_file_url, "-i", audio_file_url, "-f", "lavfi", "-i", "color=c=black:s=1280x720:r=5",  # noqa
        "-map", "0:0", "-map", "1:0", "-c:v", "libx264", "-c:a", "ac3", "-y", "output.mp4",
        "-map", "1:0", "-vn", "-ab", "256k", "-y", "output.mp3",
        "-map", "0:0", "-map", "2:0", "-crf", "0", "-c:v", "libx264", "-t", "30", "-pix_fmt", "yuv420p", "-shortest", "-y", "black.mp4",  # noqa
    ]
    # fmt: on

    p = subprocess.Popen(cmd)
    p.communicate()


def main():
    logging.basicConfig(level=logging.INFO)
    logger.info("Starting main loop.")

    queue = Queue()

    while True:
        try:
            data = queue.get()
            logger.info(f"Processing {json.dumps(data)}")
            convert(**data)
        except (KeyboardInterrupt, SystemExit):
            if data is not None:
                queue.put(data)
            logger.info("Exiting.")
            sys.exit(0)
        except Exception as e:
            if data is not None:
                queue.put(data)
            logger.error(f"Failed to process {data}. Exception: {e}")
            sys.exit(1)
        else:
            # clean data after successful conversion
            data = None


if __name__ == "__main__":
    main()
