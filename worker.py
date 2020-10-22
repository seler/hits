import asyncio
import json
import logging
import subprocess
import sys

import youtube_dl

from file_queue import Queue

logger = logging.getLogger(__name__)


async def youtubedl_download_urls(url):
    info = youtube_dl.YoutubeDL().extract_info(url, download=False)
    return {
        "video_file_url": info["requested_formats"][0]["url"],
        "audio_file_url": info["requested_formats"][1]["url"],
    }


async def ffmpeg_download_convert(video_file_url, audio_file_url):
    return
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


async def process(queue, download, convert):
    queue_data = await queue.get()
    try:
        logger.info(f"Processing {json.dumps(queue_data)}")
        download_results = await download(**queue_data)
        await convert(**download_results)
    except Exception as e:
        await queue.put(queue_data)
        raise Exception(f"Could not convert {queue_data}.") from e


async def main():
    logger.info("Starting main loop.")
    queue = Queue("./queuefile")

    try:
        while True:
            await process(
                queue, download=youtubedl_download_urls, convert=ffmpeg_download_convert
            )
    except (KeyboardInterrupt, SystemExit):
        logger.info("Exiting.")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Failed to process. Exception: {e}")
        sys.exit(1)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
