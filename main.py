import argparse
import logging
import os
import shutil

from moviepy.editor import VideoFileClip
from yt_dlp import YoutubeDL


def set_ffmpeg_path():
    if not os.getenv("IMAGEIO_FFMPEG_EXE"):
        ffmpeg_path = shutil.which("ffmpeg")
        if ffmpeg_path:
            os.environ["IMAGEIO_FFMPEG_EXE"] = ffmpeg_path
        else:
            raise RuntimeError(
                "No ffmpeg exe could be found. Install ffmpeg on your system, or set the IMAGEIO_FFMPEG_EXE environment variable"
            )


def download_video(
    url, output_path, convert_to_mp3=False, keep_video=False, progress_callback=None
):
    ydl_opts = {
        "format": "best",
        "outtmpl": os.path.join(output_path, "%(title)s.%(ext)s"),
        "progress_hooks": [progress_callback] if progress_callback else [],
    }
    with YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)
        video_path = ydl.prepare_filename(info_dict)
        print(f"Downloaded: {url}")

    if convert_to_mp3:
        convert_video_to_mp3(video_path)
        if not keep_video:
            try:
                os.remove(video_path)  # Delete the MP4 file if keep_video is False
            except FileNotFoundError as e:
                logging.error(
                    f"File not found error: {video_path} could not be deleted! {e}"
                )
                print(f"File not found error: {video_path} could not be deleted! {e}")


def convert_video_to_mp3(video_path):
    try:
        video_clip = VideoFileClip(video_path)
        audio_path = os.path.splitext(video_path)[0] + ".mp3"
        video_clip.audio.write_audiofile(audio_path)
        video_clip.close()
        print(f"Converted to MP3: {audio_path}")
    except OSError as e:
        logging.error(f"MoviePy error: the file {video_path} could not be found! {e}")
        print(f"MoviePy error: the file {video_path} could not be found! {e}")


def download_from_file(
    file_path,
    output_path,
    convert_to_mp3=False,
    keep_video=False,
    progress_callback=None,
):
    with open(file_path, "r") as file:
        urls = file.readlines()
        for url in urls:
            download_video(
                url.strip(), output_path, convert_to_mp3, keep_video, progress_callback
            )


def download_videos(
    url_or_file, output_path, convert_to_mp3, keep_video, progress_callback=None
):
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    set_ffmpeg_path()

    if os.path.isfile(url_or_file):
        download_from_file(
            url_or_file, output_path, convert_to_mp3, keep_video, progress_callback
        )
    else:
        download_video(
            url_or_file, output_path, convert_to_mp3, keep_video, progress_callback
        )


def main():
    parser = argparse.ArgumentParser(description="Download YouTube videos.")
    parser.add_argument(
        "--urls", "-u", required=True, help="URL or file path containing URLs"
    )
    parser.add_argument(
        "--path", "-p", required=True, help="Output path for downloaded files"
    )
    parser.add_argument("--mp3", action="store_true", help="Convert video to MP3")
    parser.add_argument(
        "--keep-video", action="store_true", help="Keep the video file after conversion"
    )

    args = parser.parse_args()

    download_videos(args.urls, args.path, args.mp3, args.keep_video)


if __name__ == "__main__":
    main()
