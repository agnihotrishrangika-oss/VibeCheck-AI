"""
Step 1: Input Handling.
Pulls a clean mono 16kHz WAV out of an uploaded video via ffmpeg/ffprobe.
"""

import subprocess
from pathlib import Path


def get_duration_seconds(video_path: Path) -> float:
    """Read duration without decoding the whole file."""
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(video_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffprobe failed: {result.stderr.strip()}")
    return float(result.stdout.strip())


def extract_audio(video_path: Path, audio_path: Path) -> None:
    """
    Extract audio in the exact format Whisper expects: mono, 16kHz, PCM.
    Doing this conversion here means asr_whisper.py never has to think
    about resampling.
    """
    cmd = [
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-vn",                   # drop video stream
        "-acodec", "pcm_s16le",  # uncompressed PCM
        "-ar", "16000",          # 16kHz sample rate
        "-ac", "1",              # mono
        str(audio_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg failed: {result.stderr.strip()}")

