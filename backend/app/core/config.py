"""
Central place for every tunable value in the pipeline.
Nothing here should be hardcoded elsewhere in the app.
"""

import os
from pathlib import Path


class Settings:
    # ---- CORS ----
    CORS_ORIGINS: list[str] = [
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "*",  # Allow local file:// and Live Server origin during research
    ]

    # ---- Storage ----
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent  # backend/
    STORAGE_DIR: Path = BASE_DIR / "storage"
    UPLOAD_DIR: Path = STORAGE_DIR / "uploads"
    AUDIO_DIR: Path = STORAGE_DIR / "audio"

    # ---- Video input validation ----
    MAX_VIDEO_DURATION_SECONDS: int = 60
    ALLOWED_VIDEO_EXTENSIONS: set[str] = {".mp4", ".mov", ".mkv", ".webm", ".avi"}

    # ---- Whisper ASR ----
    # "tiny", "base", "small" - keep configurable via env var
    WHISPER_MODEL_SIZE: str = os.getenv("WHISPER_MODEL_SIZE", "small")
    WHISPER_DEVICE: str = os.getenv("WHISPER_DEVICE", "cpu")
    WHISPER_COMPUTE_TYPE: str = os.getenv("WHISPER_COMPUTE_TYPE", "int8")
    WHISPER_TASK: str = "transcribe"
    WHISPER_LANGUAGE: str | None = None  # None = auto-detect; set "hi" to force Hindi

    # ---- Risk classification & Postprocessing thresholds ----
    RISK_CONFIDENCE_THRESHOLD: float = float(os.getenv("RISK_CONFIDENCE_THRESHOLD", "0.50"))
    MERGE_ADJACENT_SEGMENTS_GAP_SECONDS: float = float(os.getenv("MERGE_GAP_SECONDS", "1.0"))

    # ---- Default Policy Versions ----
    DEFAULT_YOUTUBE_POLICY_VERSION: str = "v1"
    DEFAULT_META_POLICY_VERSION: str = "v1"


settings = Settings()
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
settings.AUDIO_DIR.mkdir(parents=True, exist_ok=True)
