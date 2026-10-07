"""
Tests for Audio Extractor service (FFmpeg & FFprobe).
"""

from pathlib import Path
import pytest
from app.services.audio_extractor import get_duration_seconds, extract_audio

MEDIA_DIR = Path(__file__).parent / "test_media"


def test_get_duration_seconds():
    video_path = MEDIA_DIR / "test_normal_5s.mp4"
    assert video_path.exists(), "test_normal_5s.mp4 fixture missing"
    duration = get_duration_seconds(video_path)
    assert 4.5 <= duration <= 5.5


def test_get_duration_invalid_file():
    with pytest.raises(RuntimeError):
        get_duration_seconds(MEDIA_DIR / "non_existent_file.mp4")


def test_extract_audio_pcm_wav(tmp_path):
    video_path = MEDIA_DIR / "test_normal_5s.mp4"
    out_wav = tmp_path / "extracted.wav"
    extract_audio(video_path, out_wav)

    assert out_wav.exists()
    assert out_wav.stat().st_size > 0
    # Check duration of extracted wav
    wav_dur = get_duration_seconds(out_wav)
    assert 4.5 <= wav_dur <= 5.5
