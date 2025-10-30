import os
from pathlib import Path

import whisper
import yt_dlp
from moviepy import VideoFileClip
from youtube_transcript_api import YouTubeTranscriptApi

s2t_model = whisper.load_model("base")


def download_video(url, out_dir="video_data"):
    Path(out_dir).mkdir(exist_ok=True)
    ydl_opts = {
        "format": "best[height<=720]",
        "outtmpl": f"{out_dir}/%(id)s.%(ext)s",
        "quiet": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        video_path = ydl.prepare_filename(info)
    return video_path, info["id"]


def extract_frames(video_path, out_dir="frames", fps=0.2):
    os.makedirs(out_dir, exist_ok=True)
    clip = VideoFileClip(video_path)
    duration = clip.duration
    clip.write_images_sequence(
        os.path.join(out_dir, "frame%04d.png"), fps=fps, logger=None
    )
    clip.close()
    return duration, out_dir


def get_transcript(
    video_id,
    local_video_path: str = None,
    fallback_to_whisper: bool = True,
):
    try:
        ytt_api = YouTubeTranscriptApi()
        transcript = ytt_api.fetch(video_id, languages=["en"])
        transcript = transcript.to_raw_data()
        return [
            {
                "start": s["start"],
                "end": s["start"] + s.get("duration", 0),
                "text": s["text"].strip(),
            }
            for s in transcript
        ]
    except Exception as e:
        print(f"[WARN] YouTube transcript failed ({e}).", end=" ")
        if not fallback_to_whisper:
            print("Whisper fallback disabled → returning empty.")
            return []

    if not local_video_path or not Path(local_video_path).exists():
        print("No local video → cannot run Whisper.")
        return []

    # Transcribe – returns timestamps automatically
    result = s2t_model.transcribe(
        local_video_path,
        fp16=False,
        verbose=True,
    )

    segments = [
        {"start": s["start"], "end": s["end"], "text": s["text"].strip()}
        for s in result.get("segments", [])
    ]
    return segments


def ts(sec):
    m, s = int(sec // 60), int(sec % 60)
    return f"{m:02d}:{s:02d}"
