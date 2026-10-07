"""
Shared request and response schemas for VibeCheck-AI.
Enforces the core principle:
DETECTION != POLICY != ACTION
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from app.policy_engine.schemas import PolicyAssessment


class TranscriptSegment(BaseModel):
    start: float
    end: float
    text: str
    label: str = "normal"  # "normal", "harassment", "hate_speech"
    confidence: float = 0.0
    probabilities: Optional[Dict[str, float]] = None
    youtube_policy: Optional[PolicyAssessment] = None
    instagram_policy: Optional[PolicyAssessment] = None


class PlatformSummary(BaseModel):
    total_flagged: int
    potential_violations: int
    requires_review: int
    highest_severity: str


class PolicyOverview(BaseModel):
    youtube: PlatformSummary
    instagram_meta: PlatformSummary
    disclaimer: str = (
        "Policy assessments represent simulated rule evaluations based on public Community Guidelines. "
        "They do not predict or guarantee actual enforcement actions by YouTube or Meta."
    )


class AnalyzeResponse(BaseModel):
    video_id: str
    filename: Optional[str] = None
    duration_seconds: float
    language: Optional[str] = None
    segments: List[TranscriptSegment]
    risk_events: List[TranscriptSegment]
    policy_overview: PolicyOverview
    created_at: Optional[str] = None


class TextAnalyzeRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000)
    youtube_policy_version: str = "v1"
    meta_policy_version: str = "v1"


class AdaptationExperimentRequest(BaseModel):
    events: List[Dict[str, Any]]
    v1_version: str = "v1"
    v2_version: str = "v2"


class HistoryItem(BaseModel):
    id: str
    created_at: str
    filename: Optional[str]
    duration_seconds: float
    language: Optional[str]
    total_segments: int
    risk_count: int
    highest_severity: str
    summary: str


class ErrorResponse(BaseModel):
    detail: str
