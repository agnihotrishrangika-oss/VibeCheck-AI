"""
API Endpoints for VibeCheck-AI.
Keeps clean architectural separation:
Routes orchestrate services without embedding model weights or hardcoding policy rules.
"""

import uuid
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Query

from app.core.config import settings
from app.services.audio_extractor import get_duration_seconds, extract_audio
from app.services.asr_whisper import transcribe_audio
from app.services.classifier import classify_segments, classify_text
from app.services.postprocessor import postprocess_segments
from app.policy_engine import policy_engine
from app.database.db import save_analysis, get_all_analyses, get_analysis_by_id
from app.models.schemas import (
    AnalyzeResponse,
    TranscriptSegment,
    PolicyOverview,
    PlatformSummary,
    TextAnalyzeRequest,
    AdaptationExperimentRequest,
    HistoryItem,
)

router = APIRouter()


def _build_policy_overview(segments: List[TranscriptSegment]) -> PolicyOverview:
    """Computes summary stats for YouTube and Instagram/Meta assessments."""
    yt_flagged = [s for s in segments if s.youtube_policy and s.youtube_policy.status != "low_concern"]
    yt_violations = [s for s in segments if s.youtube_policy and s.youtube_policy.status == "potential_policy_violation"]
    yt_reviews = [s for s in segments if s.youtube_policy and s.youtube_policy.status == "requires_review"]

    ig_flagged = [s for s in segments if s.instagram_policy and s.instagram_policy.status != "low_concern"]
    ig_violations = [s for s in segments if s.instagram_policy and s.instagram_policy.status == "potential_policy_violation"]
    ig_reviews = [s for s in segments if s.instagram_policy and s.instagram_policy.status == "requires_review"]

    def max_severity(items, attr):
        sevs = [getattr(s, attr).severity for s in items if getattr(s, attr) and getattr(s, attr).severity]
        for p in ["Critical", "High", "Medium-High", "Medium"]:
            if p in sevs:
                return p
        return "Low"

    return PolicyOverview(
        youtube=PlatformSummary(
            total_flagged=len(yt_flagged),
            potential_violations=len(yt_violations),
            requires_review=len(yt_reviews),
            highest_severity=max_severity(yt_flagged, "youtube_policy"),
        ),
        instagram_meta=PlatformSummary(
            total_flagged=len(ig_flagged),
            potential_violations=len(ig_violations),
            requires_review=len(ig_reviews),
            highest_severity=max_severity(ig_flagged, "instagram_policy"),
        ),
    )


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_video(
    file: UploadFile = File(...),
    youtube_version: str = Query("v1", description="YouTube policy version profile (e.g. v1 or v2)"),
    meta_version: str = Query("v1", description="Meta policy version profile (e.g. v1 or v2)"),
):
    """
    Core Pipeline:
    Video -> FFmpeg audio extraction -> faster-whisper ASR -> ML risk classification ->
    postprocessor -> independent policy engine (YouTube + Meta) -> Timeline response.
    """
    ext = Path(file.filename).suffix.lower()
    if ext not in settings.ALLOWED_VIDEO_EXTENSIONS:
        raise HTTPException(
            400,
            f"Unsupported file type '{ext}'. Allowed extensions: {', '.join(sorted(settings.ALLOWED_VIDEO_EXTENSIONS))}"
        )

    video_id = str(uuid.uuid4())
    video_path = settings.UPLOAD_DIR / f"{video_id}{ext}"
    audio_path = settings.AUDIO_DIR / f"{video_id}.wav"

    try:
        content = await file.read()
        video_path.write_bytes(content)

        # 1. Video Duration
        try:
            duration = get_duration_seconds(video_path)
        except Exception as e:
            raise HTTPException(400, f"Failed to inspect video duration with ffprobe: {e}")

        if duration > settings.MAX_VIDEO_DURATION_SECONDS:
            raise HTTPException(
                400,
                f"Video duration is {duration:.1f}s. Maximum allowed duration is {settings.MAX_VIDEO_DURATION_SECONDS}s.",
            )

        # 2. Audio Extraction
        try:
            extract_audio(video_path, audio_path)
        except Exception as e:
            raise HTTPException(500, f"Audio extraction failed: {e}")

        # 3. Whisper ASR
        try:
            raw_segments, detected_language = transcribe_audio(audio_path)
        except Exception as e:
            raise HTTPException(500, f"Speech transcription failed: {e}")

        # 4. ML Risk Classification
        classified = classify_segments(raw_segments)

        # 5. Postprocessing (Thresholding & merging adjacent windows)
        postprocessed = postprocess_segments(
            classified,
            confidence_threshold=settings.RISK_CONFIDENCE_THRESHOLD,
            gap_seconds=settings.MERGE_ADJACENT_SEGMENTS_GAP_SECONDS,
        )

        # 6. Policy Engine Evaluation (YouTube & Instagram/Meta)
        final_segments: List[TranscriptSegment] = []
        for s in postprocessed:
            policies = policy_engine.evaluate_multiplatform(
                label=s["label"],
                confidence=s["confidence"],
                text=s["text"],
                youtube_version=youtube_version,
                meta_version=meta_version,
            )
            final_segments.append(
                TranscriptSegment(
                    start=s["start"],
                    end=s["end"],
                    text=s["text"],
                    label=s["label"],
                    confidence=s["confidence"],
                    probabilities=s.get("probabilities"),
                    youtube_policy=policies["youtube"],
                    instagram_policy=policies["instagram_meta"],
                )
            )

        risk_events = [s for s in final_segments if s.label != "normal"]
        policy_overview = _build_policy_overview(final_segments)

        # 7. Persist to SQLite History
        save_analysis(
            video_id=video_id,
            duration_seconds=duration,
            language=detected_language,
            segments=[s.model_dump() for s in final_segments],
            filename=file.filename,
        )

        return AnalyzeResponse(
            video_id=video_id,
            filename=file.filename,
            duration_seconds=round(duration, 2),
            language=detected_language,
            segments=final_segments,
            risk_events=risk_events,
            policy_overview=policy_overview,
        )

    finally:
        video_path.unlink(missing_ok=True)
        audio_path.unlink(missing_ok=True)


@router.post("/analyze/text", response_model=AnalyzeResponse)
async def analyze_text(request: TextAnalyzeRequest):
    """
    Direct text analysis for Hindi-English / Hinglish text snippets.
    Wires into the ML classifier and independent policy engine.
    """
    pred = classify_text(request.text)
    policies = policy_engine.evaluate_multiplatform(
        label=pred["label"],
        confidence=pred["confidence"],
        text=request.text,
        youtube_version=request.youtube_policy_version,
        meta_version=request.meta_policy_version,
    )

    segment = TranscriptSegment(
        start=0.0,
        end=round(max(1.0, len(request.text.split()) * 0.4), 2),
        text=request.text,
        label=pred["label"],
        confidence=pred["confidence"],
        probabilities=pred.get("probabilities"),
        youtube_policy=policies["youtube"],
        instagram_policy=policies["instagram_meta"],
    )

    segments = [segment]
    risk_events = [segment] if segment.label != "normal" else []
    overview = _build_policy_overview(segments)
    text_id = str(uuid.uuid4())

    save_analysis(
        video_id=text_id,
        duration_seconds=segment.end,
        language="hi-en (code-mixed)",
        segments=[s.model_dump() for s in segments],
        filename="text_snippet.txt",
    )

    return AnalyzeResponse(
        video_id=text_id,
        filename="text_snippet.txt",
        duration_seconds=segment.end,
        language="hi-en (code-mixed)",
        segments=segments,
        risk_events=risk_events,
        policy_overview=overview,
    )


@router.post("/policy/adapt")
async def policy_adaptation_experiment(request: AdaptationExperimentRequest):
    """
    Research Experiment 2 Endpoint:
    Takes existing detected events, evaluates under v1 vs v2 policy profiles,
    and returns comparative policy assessments demonstrating that policy shifts
    without retraining the ML model.
    """
    return policy_engine.run_adaptation_experiment(
        events=request.events,
        v1_name=request.v1_version,
        v2_name=request.v2_version,
    )


@router.get("/history", response_model=List[HistoryItem])
async def list_history():
    """Returns past moderation activities from SQLite."""
    records = get_all_analyses(limit=50)
    return [HistoryItem(**r) for r in records]


@router.get("/history/{analysis_id}")
async def get_history_detail(analysis_id: str):
    """Fetches full past analysis detail by ID."""
    record = get_analysis_by_id(analysis_id)
    if not record:
        raise HTTPException(404, f"Analysis {analysis_id} not found.")
    return record


@router.get("/policies")
async def get_policy_definitions():
    """Inspect active YouTube and Meta policy rule dictionaries."""
    return policy_engine.rules_registry