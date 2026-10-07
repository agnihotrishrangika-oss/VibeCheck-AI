"""
Tests for faster-whisper ASR transcription.
"""

from pathlib import Path
from app.services.asr_whisper import transcribe_audio

MEDIA_DIR = Path(__file__).parent / "test_media"


def test_transcribe_audio_speech():
    speech_wav = MEDIA_DIR / "test_speech.wav"
    assert speech_wav.exists()
    segments, lang = transcribe_audio(speech_wav)
    assert isinstance(segments, list)
    assert len(segments) > 0
    # Every segment must preserve start, end, text
    for seg in segments:
        assert "start" in seg
        assert "end" in seg
        assert "text" in seg
        assert seg["end"] >= seg["start"]
        assert len(seg["text"]) > 0


def test_transcribe_silence():
    # Silent audio extraction check
    silent_wav = MEDIA_DIR / "test_mono_16k.wav"
    assert silent_wav.exists()
    segments, lang = transcribe_audio(silent_wav)
    assert isinstance(segments, list)
