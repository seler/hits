import argparse
import asyncio
import json
import logging
import os
import subprocess
from pathlib import Path

import youtube_dl

from file_queue import Queue

logger = logging.getLogger(__name__)
__version_info__ = (0, 1, "dev1")
__version__ = ".".join(map(str, __version_info__))


async def download_and_convert(source_url, destination_dir: Path):
    logger.info("Download and processing started.")
    with youtube_dl.YoutubeDL(params={"forcefilename": True}) as ytdl:
        info = ytdl.extract_info(source_url, download=True)
        filename = ytdl.prepare_filename(info)
    filename_wo_ext = os.path.splitext(filename)[0]

    for ext in ["mp4", "mkv", "webm"]:
        filepath = Path(f"{filename_wo_ext}.{ext}").resolve()
        if filepath.exists():
            break

    video_dest_dir = destination_dir / "Video"
    audio_dest_dir = destination_dir / "Audio"
    black_dest_dir = destination_dir / "Black"
    video_dest_dir.mkdir(parents=True, exist_ok=True)
    audio_dest_dir.mkdir(parents=True, exist_ok=True)
    black_dest_dir.mkdir(parents=True, exist_ok=True)

    if ext not in ["mp4", "mkv"]:
        ext = "mkv"

    normal_tmp_filename = video_dest_dir / f"{filename_wo_ext}.{ext}"
    audio_tmp_filename = audio_dest_dir / f"{filename_wo_ext}.mp3"
    black_tmp_filename = black_dest_dir / f"{filename_wo_ext}.mp4"
    # fmt: off
    cmd = [
        "ffmpeg", "-i", filepath, "-f", "lavfi", "-i", "color=c=black:s=1280x720:r=5",  # noqa
        "-map", "0", "-c:v", "libx264", "-c:a", "ac3", "-y", normal_tmp_filename,
        "-map", "0", "-vn", "-ab", "256k", "-y", audio_tmp_filename,
        "-map", "0:1", "-map", "1:0", "-crf", "0", "-c:v", "libx264", "-t", "9999", "-pix_fmt", "yuv420p", "-shortest", "-y", black_tmp_filename,  # noqa
    ]
    # fmt: on

    p = subprocess.Popen(cmd)
    p.communicate()
    filepath.unlink()
    if p.returncode:
        raise RuntimeError("ffmpeg failed")
    logger.info("Download and processing done.")


async def loop(queue_file, destination_dir):
    while True:
        queue = Queue(queue_file)
        queue_data = await queue.get()
        try:
            logger.info(f"Processing {json.dumps(queue_data)}")
            await download_and_convert(queue_data["url"], destination_dir)
        except Exception:
            await queue.put(queue_data)
            raise


def main():
    parser = argparse.ArgumentParser(
        description="description", epilog="optional text below args list"
    )

    group = parser.add_mutually_exclusive_group()
    group.add_argument("-v", "--verbose", action="store_true")
    group.add_argument("-q", "--quiet", action="store_true")

    parser.add_argument(
        "--version", action="version", version="%(prog)s {}".format(__version__)
    )
    parser.add_argument("--destination", type=Path, required=True)
    parser.add_argument("--queue-file", type=Path, required=True)

    args = parser.parse_args()

    if args.verbose:
        level = logging.DEBUG
    elif args.quiet:
        level = logging.ERROR
    else:
        level = logging.INFO
    logging.basicConfig(level=level)
    logger.info("Starting main loop.")
    try:
        asyncio.run(loop(args.queue_file.resolve(), args.destination.resolve()))
    except (KeyboardInterrupt, SystemExit):
        parser.exit(status=0, message="Gracefully exiting.\n")


if __name__ == "__main__":
    main()
