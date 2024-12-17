import os
import sys
import time
from pytubefix import YouTube

# Ensure the script handles Unicode characters properly
sys.stdout.reconfigure(encoding="utf-8")


def on_progress(stream, chunk, bytes_remaining):
    total_size = stream.filesize
    bytes_downloaded = total_size - bytes_remaining
    percentage_of_completion = bytes_downloaded / total_size * 100
    download_speed = bytes_downloaded / (time.time() - start_time)
    eta = bytes_remaining / download_speed if download_speed > 0 else 0
    minutes = int(eta // 60)
    remaining_seconds = int(eta % 60)
    # Clear the line before printing
    print(
        f"\r\033[KPROGRESS: {percentage_of_completion:.2f}%  "
        f"SPEED: {download_speed / (1024 * 1024):.2f} MB/s  "
        f"ETA: {minutes}m{remaining_seconds}s",
        end="",
        flush=True,
    )


def sanitize_filename(filename):
    # Replace characters that are invalid in Windows filenames
    return "".join(c if c not in r'\/:*?"<>|' else "_" for c in filename)


def download_video(url):
    global start_time
    try:
        yt = YouTube(url, on_progress_callback=on_progress)
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
        video_filesize = (
            video_stream.filesize + audio_stream.filesize
        )  # Total filesize in bytes

        print(f"Title: {yt.title}")
        print(f"Resolution: {video_resolution}")
        print(f"Length: {video_length // 60} minutes {video_length % 60} seconds")
        print(f"File Size: {video_filesize / (1024 * 1024):.2f} MB")

        # Download video and audio streams
        output_path = "C:\\Users\\woobin\\Downloads"
        sanitized_title = sanitize_filename(yt.title)
        start_time = time.time()
        video_path = video_stream.download(
            output_path=output_path, filename="video.mp4"
        )
        audio_path = audio_stream.download(
            output_path=output_path, filename="audio.mp4"
        )

        # Merge video and audio using ffmpeg
        final_output = os.path.join(output_path, f"{sanitized_title}.mp4")
        os.system(
            f'ffmpeg -i "{video_path}" -i "{audio_path}" -c:v copy -c:a aac "{final_output}"'
        )

        # Remove temporary files
        os.remove(video_path)
        os.remove(audio_path)

        print(f"\nDownload and merge completed: {final_output}")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    video_url = input("Enter the YouTube video URL: ")
    download_video(video_url)
