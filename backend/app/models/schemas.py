
"""
Shared request/response shapes. Keep transcription-only fields here now;
your teammate's classifier_hatebert.py / postprocessor.py will extend
TranscriptSegment with label/confidence once that stage is wired in.
"""

from pydantic import BaseModel
from typing import Optional


class TranscriptSegment(BaseModel):
    start: float                 # seconds
    end: float                   # seconds
    text: str
    label: Optional[str] = None       # filled in later by classifier_hatebert.py
    confidence: Optional[float] = None  # filled in later by postprocessor.py


class AnalyzeResponse(BaseModel):
    video_id: str
    duration_seconds: float
    language: Optional[str] = None
    segments: list[TranscriptSegment]


class ErrorResponse(BaseModel):
    detail: str
