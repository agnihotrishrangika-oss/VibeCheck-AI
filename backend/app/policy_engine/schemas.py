"""
Data schemas for the Independent Policy Engine.
Maintains clear boundary: DETECTION != POLICY != ACTION
"""

from pydantic import BaseModel, Field
from typing import Optional, List


class PolicyRule(BaseModel):
    rule_id: str
    platform: str  # "YouTube" or "Instagram / Meta"
    policy_category: str  # e.g., "Hate Speech", "Harassment & Cyberbullying"
    rule_description: str
    protected_characteristics: List[str] = Field(default_factory=list)
    context_exceptions: List[str] = Field(default_factory=list)
    severity: str  # "Critical", "High", "Medium", "Low"
    recommended_action: str
    source_url: str
    source_title: str
    retrieved_date: str
    policy_version: str
    violation_threshold: float = 0.70
    review_threshold: float = 0.50


class PolicyAssessment(BaseModel):
    platform: str
    policy_version: str
    status: str  # "potential_policy_violation", "requires_review", "potential_policy_issue", "low_concern"
    status_label: str  # Human readable badge text
    policy_category: Optional[str] = None
    triggered_rule_id: Optional[str] = None
    rule_description: Optional[str] = None
    severity: str = "Low"
    confidence_score: float
    recommended_action: str
    context_exceptions: Optional[str] = None
    source_url: Optional[str] = None
    source_title: Optional[str] = None
    disclaimer: str = (
        "Research policy assessment only. Does not determine or guarantee actual platform enforcement."
    )
