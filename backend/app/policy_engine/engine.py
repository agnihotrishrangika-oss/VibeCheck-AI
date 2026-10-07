"""
Core Modular Policy Engine.
Maintains clear architectural boundary: DETECTION != POLICY != ACTION

The ML model determines WHAT happened (label, confidence, text, timestamps).
The PolicyEngine determines HOW the platform policy treats it.
The final platform action is never guaranteed or predicted.
"""

from typing import Dict, List, Optional
from app.policy_engine.schemas import PolicyAssessment, PolicyRule
from app.policy_engine.rules_youtube import YOUTUBE_RULES_V1, YOUTUBE_RULES_V2
from app.policy_engine.rules_meta import META_RULES_V1, META_RULES_V2


class PolicyEngine:
    def __init__(self):
        self.rules_registry = {
            "YouTube": {
                "v1": YOUTUBE_RULES_V1,
                "v1.2-standard": YOUTUBE_RULES_V1,
                "v2": YOUTUBE_RULES_V2,
                "v2.0-strict": YOUTUBE_RULES_V2,
            },
            "Instagram / Meta": {
                "v1": META_RULES_V1,
                "v2026.1-standard": META_RULES_V1,
                "v2": META_RULES_V2,
                "v2026.2-strict": META_RULES_V2,
            },
        }

    def get_rule(self, platform: str, category: str, version: str = "v1") -> Optional[PolicyRule]:
        platform_rules = self.rules_registry.get(platform, {})
        version_rules = platform_rules.get(version, platform_rules.get("v1", {}))
        return version_rules.get(category)

    def evaluate_event(
        self,
        label: str,
        confidence: float,
        text: Optional[str] = None,
        platform: str = "YouTube",
        version: str = "v1",
    ) -> PolicyAssessment:
        """
        Evaluate a single detected risk event against a specific platform policy.
        Terminology adheres to: 'potential policy violation', 'requires review', 'potential policy issue'.
        """
        if label == "normal" or confidence < 0.35:
            return PolicyAssessment(
                platform=platform,
                policy_version=version,
                status="low_concern",
                status_label="Compliant / Low Concern",
                policy_category="General Content",
                severity="Low",
                confidence_score=round(confidence, 3),
                recommended_action="No policy intervention recommended.",
                context_exceptions="Content appears normative under platform guidelines.",
            )

        rule = self.get_rule(platform, label, version)
        if not rule:
            # Fallback if label is unmapped
            return PolicyAssessment(
                platform=platform,
                policy_version=version,
                status="requires_review",
                status_label="Requires Review",
                policy_category=label.replace("_", " ").title(),
                severity="Medium",
                confidence_score=round(confidence, 3),
                recommended_action="Route to human moderation queue for manual policy assessment.",
                context_exceptions="Uncategorized risk category.",
            )

        # Apply platform thresholds from structured rule record
        if confidence >= rule.violation_threshold:
            status = "potential_policy_violation"
            status_label = "Potential Policy Violation"
            action = rule.recommended_action
            severity = rule.severity
        elif confidence >= rule.review_threshold:
            status = "requires_review"
            status_label = "Requires Review"
            action = (
                f"Borderline confidence ({confidence:.2f}). "
                f"Recommend human moderator review under {rule.source_title} exceptions."
            )
            severity = "Medium" if rule.severity != "Low" else "Low"
        else:
            status = "potential_policy_issue"
            status_label = "Potential Policy Issue (Low Concern)"
            action = "Monitor content; below active enforcement threshold."
            severity = "Low"

        exceptions_str = "; ".join(rule.context_exceptions) if rule.context_exceptions else None

        return PolicyAssessment(
            platform=platform,
            policy_version=rule.policy_version,
            status=status,
            status_label=status_label,
            policy_category=rule.policy_category,
            triggered_rule_id=rule.rule_id,
            rule_description=rule.rule_description,
            severity=severity,
            confidence_score=round(confidence, 3),
            recommended_action=action,
            context_exceptions=exceptions_str,
            source_url=rule.source_url,
            source_title=rule.source_title,
        )

    def evaluate_multiplatform(
        self,
        label: str,
        confidence: float,
        text: Optional[str] = None,
        youtube_version: str = "v1",
        meta_version: str = "v1",
    ) -> Dict[str, PolicyAssessment]:
        """
        Evaluate one detected event against BOTH YouTube and Instagram/Meta policies.
        Timestamps and detected risk remain identical across platforms.
        """
        yt_assessment = self.evaluate_event(
            label=label,
            confidence=confidence,
            text=text,
            platform="YouTube",
            version=youtube_version,
        )
        meta_assessment = self.evaluate_event(
            label=label,
            confidence=confidence,
            text=text,
            platform="Instagram / Meta",
            version=meta_version,
        )
        return {
            "youtube": yt_assessment,
            "instagram_meta": meta_assessment,
        }

    def run_adaptation_experiment(
        self,
        events: List[dict],
        v1_name: str = "v1",
        v2_name: str = "v2",
    ) -> Dict[str, dict]:
        """
        Research Experiment 2:
        Given identical detected events and identical ML model outputs:
        Demonstrate that changing the policy profile (v1 -> v2) changes policy assessment
        WITHOUT retraining the ML model!
        """
        results_v1 = []
        results_v2 = []

        for ev in events:
            label = ev.get("label", "normal")
            conf = ev.get("confidence", 0.0)
            txt = ev.get("text", "")

            v1_eval = self.evaluate_multiplatform(
                label=label, confidence=conf, text=txt, youtube_version=v1_name, meta_version=v1_name
            )
            v2_eval = self.evaluate_multiplatform(
                label=label, confidence=conf, text=txt, youtube_version=v2_name, meta_version=v2_name
            )

            results_v1.append({
                "start": ev.get("start"),
                "end": ev.get("end"),
                "text": txt,
                "label": label,
                "confidence": conf,
                "youtube": v1_eval["youtube"],
                "instagram_meta": v1_eval["instagram_meta"],
            })
            results_v2.append({
                "start": ev.get("start"),
                "end": ev.get("end"),
                "text": txt,
                "label": label,
                "confidence": conf,
                "youtube": v2_eval["youtube"],
                "instagram_meta": v2_eval["instagram_meta"],
            })

        return {
            "policy_v1_results": results_v1,
            "policy_v2_results": results_v2,
            "principle": "DETECTION != POLICY != ACTION",
            "experiment_note": (
                "ML detections are identical across both runs. "
                "Policy decisions shift dynamically due to independent policy engine rule parameters."
            ),
        }


policy_engine = PolicyEngine()
