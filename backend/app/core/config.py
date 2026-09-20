
"""
Central place for every tunable value in the pipeline.
Nothing here should be hardcoded elsewhere in the app.
"""

from pathlib import Path


class Settings:
    # ---- CORS ----
    CORS_ORIGINS: list[str] = [
        "http://localhost:5500",   # Live Server / plain frontend dev
        "http://127.0.0.1:5500",
    ]

    # ---- Storage ----
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent  # backend/
    UPLOAD_DIR: Path = BASE_DIR / "storage" / "uploads"
    AUDIO_DIR: Path = BASE_DIR / "storage" / "audio"

    # ---- Video input validation ----
    MAX_VIDEO_DURATION_SECONDS: int = 60
    ALLOWED_VIDEO_EXTENSIONS: set[str] = {".mp4", ".mov", ".mkv", ".webm", ".avi"}

    # ---- Whisper ASR ----
    # "small" or "medium" — medium is more accurate on Hinglish/accented
    # speech but slower. Keep configurable, tune once you see real data.
    WHISPER_MODEL_SIZE: str = "small"
    WHISPER_DEVICE: str = "cpu"          # "cuda" if you have a GPU
    WHISPER_COMPUTE_TYPE: str = "int8"   # "float16" if WHISPER_DEVICE == "cuda"
    # Force transcription in the spoken language rather than auto-translating
    # to English — the hate-speech classifier expects original Hinglish text.
    WHISPER_TASK: str = "transcribe"
    WHISPER_LANGUAGE: str | None = None  # None = auto-detect; set "hi" to force Hindi

    # ---- Hate-speech classification (thresholds used by postprocessor.py) ----
    HATE_CONFIDENCE_THRESHOLD: float = 0.6
    MERGE_ADJACENT_SEGMENTS_GAP_SECONDS: float = 1.0


settings = Settings()
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
settings.AUDIO_DIR.mkdir(parents=True, exist_ok=True)
