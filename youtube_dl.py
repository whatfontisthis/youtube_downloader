import os
import sys
import time
import traceback
import subprocess
from pytubefix import YouTube
from pathvalidate import sanitize_filename
from tqdm import tqdm
from datetime import datetime

# Ensure the script handles Unicode characters properly
sys.stdout.reconfigure(encoding="utf-8")

# Initialize global variables for the progress bar
pbar = None
stream_type = None  # Track whether we're downloading video or audio


def on_progress(stream, chunk, bytes_remaining):
    global pbar, stream_type
    total_size = stream.filesize  # Total size of the stream
    bytes_downloaded = total_size - bytes_remaining  # Bytes downloaded so far

    if pbar is None:
        # Initialize the progress bar with desired settings
        label = "Video" if stream_type == "video" else "Audio"
        pbar = tqdm(
            total=100,  # Progress bar will be in percentage
            unit="%",  # Display as percentage
            desc=label,
            ncols=50,  # Shorter progress bar
            bar_format="{l_bar}{bar}| {n_fmt}% [{rate_fmt}]",  # Custom format
            ascii=True,  # Use simpler ASCII characters
        )

    # Update the progress bar based on percentage
    percent_complete = (bytes_downloaded / total_size) * 100
    pbar.n = round(percent_complete)  # Update progress bar position
    pbar.refresh()  # Refresh the bar display

    if bytes_remaining == 0:
        pbar.close()  # Close the progress bar
        pbar = None


def download_video(url):
    global start_time, pbar, stream_type
    try:
        yt = YouTube(url, on_progress_callback=on_progress)

        # Fetch video and audio streams
        # Filter for video streams with resolution 1440p or the best below it
        video_stream = (
            yt.streams.filter(adaptive=True, file_extension="mp4", only_video=True)
            .filter(res="1440p")  # Attempt to fetch 1440p first
            .first()
        )

        # If 1440p is not available, fall back to the best available resolution
        if not video_stream:
            video_stream = (
                yt.streams.filter(adaptive=True, file_extension="mp4", only_video=True)
                .order_by("resolution")
                .desc()
                .first()
            )

        audio_stream = (
            yt.streams.filter(adaptive=True, file_extension="mp4", only_audio=True)
            .order_by("abr")
            .desc()
            .first()
        )

        # Display video details
        video_resolution = video_stream.resolution
        video_length = yt.length  # Length in seconds
        video_filesize = video_stream.filesize + audio_stream.filesize

        print(f"\nTitle: {yt.title}")
        print(f"Resolution: {video_resolution}")
        print(f"Length: {video_length // 60} minutes {video_length % 60} seconds")
        print(f"File Size: {video_filesize / (1024 * 1024):.2f} MB")

        # Define paths
        output_path = "C:\\Users\\woobin\\Downloads"
        sanitized_title = sanitize_filename(yt.title)
        start_time = time.time()

        # Download video
        stream_type = "video"
        video_path = video_stream.download(
            output_path=output_path, filename="video.mp4"
        )

        # Download audio
        stream_type = "audio"
        audio_path = audio_stream.download(
            output_path=output_path, filename="audio.mp4"
        )

        # Generate timestamp and final output filename
        timestamp = datetime.now().strftime("%y%m%d%H%M")
        final_output = os.path.join(output_path, f"{sanitized_title}_{timestamp}.mp4")

        # Notify user that merging is starting
        print("Merging video and audio...")
        sys.stdout.flush()  # Ensure the message is displayed immediately

        # Merge video and audio using ffmpeg
        ffmpeg_path = "c:\\ffmpeg\\bin\\ffmpeg.exe"
        command = [
            ffmpeg_path,
            "-loglevel",
            "quiet",
            "-i",
            video_path,
            "-i",
            audio_path,
            "-c:v",
            "copy",
            "-c:a",
            "aac",
            final_output,
        ]

        try:
            subprocess.run(
                command,
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            print(f"\nDownload Completed: {final_output}")
        except subprocess.CalledProcessError as e:
            print(f"An error occurred during merging: {e}")

        # Clean up temporary files
        os.remove(video_path)
        os.remove(audio_path)

    except Exception as e:
        print(f"An error occurred: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    video_url = input("Enter the YouTube video URL: ")
    download_video(video_url)
