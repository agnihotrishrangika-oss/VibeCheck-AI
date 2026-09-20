"""
Step 2: Speech-to-Text.
Loads Whisper once (module-level singleton) and reuses it across requests —
reloading the model per-request is slow and burns memory.
"""

from pathlib import Path
from faster_whisper import WhisperModel

from app.core.config import settings

_MODEL: WhisperModel | None = None


def get_model() -> WhisperModel:
    global _MODEL
    if _MODEL is None:
        _MODEL = WhisperModel(
            settings.WHISPER_MODEL_SIZE,
            device=settings.WHISPER_DEVICE,
            compute_type=settings.WHISPER_COMPUTE_TYPE,
        )
    return _MODEL


def transcribe_audio(audio_path: Path) -> tuple[list[dict], str]:
    """
    Returns (segments, detected_language).
    Each segment: {"start": float, "end": float, "text": str}
    These are exactly the timestamps you need to point at *where* in the
    video the hate speech occurs, not just whether it's present.
    """
    model = get_model()
    segments_iter, info = model.transcribe(
        str(audio_path),
        beam_size=5,
        task=settings.WHISPER_TASK,
        language=settings.WHISPER_LANGUAGE,
        word_timestamps=True,
        vad_filter=True,  # skips silence, keeps timestamps tighter
    )

    segments = [
        {
            "start": round(seg.start, 2),
            "end": round(seg.end, 2),
            "text": seg.text.strip(),
        }
        for seg in segments_iter
    ]
    return segments, info.language
