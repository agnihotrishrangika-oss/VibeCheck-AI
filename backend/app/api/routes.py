"""
/analyze wires Step 1 (audio_extractor) into Step 2 (asr_whisper).
Classifier + postprocessor stages plug in right where marked below —
leave that TODO for your teammate rather than guessing their interface.
"""

import uuid
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, HTTPException

from app.core.config import settings
from app.services.audio_extractor import get_duration_seconds, extract_audio
from app.services.asr_whisper import transcribe_audio
from app.models.schemas import AnalyzeResponse, TranscriptSegment

router = APIRouter()


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_video(file: UploadFile = File(...)):
    ext = Path(file.filename).suffix.lower()
    if ext not in settings.ALLOWED_VIDEO_EXTENSIONS:
        raise HTTPException(400, f"Unsupported file type: {ext}")

    video_id = str(uuid.uuid4())
    video_path = settings.UPLOAD_DIR / f"{video_id}{ext}"
    video_path.write_bytes(await file.read())

    try:
        duration = get_duration_seconds(video_path)
        if duration > settings.MAX_VIDEO_DURATION_SECONDS:
            raise HTTPException(
                400,
                f"Video is {duration:.1f}s, max is {settings.MAX_VIDEO_DURATION_SECONDS}s",
            )

        audio_path = settings.AUDIO_DIR / f"{video_id}.wav"
        extract_audio(video_path, audio_path)

        raw_segments, language = transcribe_audio(audio_path)

        # TODO (teammate): pass raw_segments through
        #   classifier_hatebert.py  -> fills in each segment's `label`
        #   postprocessor.py        -> applies HATE_CONFIDENCE_THRESHOLD,
        #                              merges adjacent flagged segments
        segments = [TranscriptSegment(**seg) for seg in raw_segments]

        return AnalyzeResponse(
            video_id=video_id,
            duration_seconds=duration,
            language=language,
            segments=segments,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Processing failed: {e}")

    finally:
        video_path.unlink(missing_ok=True)
        audio_path_cleanup = settings.AUDIO_DIR / f"{video_id}.wav"
        audio_path_cleanup.unlink(missing_ok=True)


@router.get("/history")
async def get_history():
    # TODO (teammate): read past AnalyzeResponse results from a DB.
    # Not part of the extraction/transcription work — stubbed for now.
    raise HTTPException(501, "Not implemented yet")