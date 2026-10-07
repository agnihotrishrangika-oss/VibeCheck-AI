"""
Tests for Independent Modular Policy Engine.
Validates:
- Separation Principle: Detection != Policy != Action
- Official YouTube profile evaluation
- Official Instagram/Meta profile evaluation
- Dual platform evaluation with identical timestamps
- Experiment 2: Policy adaptation without ML retraining
"""

from app.policy_engine import policy_engine


def test_evaluate_normal_event_low_concern():
    assessment = policy_engine.evaluate_event(
        label="normal",
        confidence=0.90,
        text="Namaste, welcome to the vlog",
        platform="YouTube",
    )
    assert assessment.status == "low_concern"
    assert assessment.severity == "Low"
    assert "no policy intervention" in assessment.recommended_action.lower()


def test_youtube_policy_profiles():
    # Hate speech evaluation on YouTube
    yt_hate = policy_engine.evaluate_event(
        label="hate_speech",
        confidence=0.88,
        text="Communal slur attack",
        platform="YouTube",
        version="v1",
    )
    assert yt_hate.status == "potential_policy_violation"
    assert yt_hate.triggered_rule_id == "YT-HATE-01"
    assert "https://support.google.com/youtube/answer/2801939" in yt_hate.source_url
    assert "strike" in yt_hate.recommended_action.lower()

    # Harassment evaluation on YouTube
    yt_harass = policy_engine.evaluate_event(
        label="harassment",
        confidence=0.72,
        text="Stop talking idiot",
        platform="YouTube",
        version="v1",
    )
    assert yt_harass.status == "potential_policy_violation"
    assert yt_harass.triggered_rule_id == "YT-HARASS-01"


def test_meta_instagram_policy_profiles():
    # Hate speech evaluation on Instagram / Meta
    meta_hate = policy_engine.evaluate_event(
        label="hate_speech",
        confidence=0.85,
        text="Targeted identity attack",
        platform="Instagram / Meta",
        version="v1",
    )
    assert meta_hate.status == "potential_policy_violation"
    assert meta_hate.triggered_rule_id == "META-HATE-01"
    assert "https://transparency.meta.com/policies/community-standards/hate-speech/" in meta_hate.source_url

    # Bullying on Meta
    meta_bully = policy_engine.evaluate_event(
        label="harassment",
        confidence=0.75,
        text="Targeting user maliciously",
        platform="Instagram / Meta",
        version="v1",
    )
    assert meta_bully.status == "potential_policy_violation"
    assert meta_bully.triggered_rule_id == "META-BULLY-01"


def test_same_event_evaluated_under_both_platforms():
    event_label = "harassment"
    event_confidence = 0.70
    event_text = "Abe saale chup kar bakwas kar raha hai"

    eval_results = policy_engine.evaluate_multiplatform(
        label=event_label,
        confidence=event_confidence,
        text=event_text,
    )
    assert "youtube" in eval_results
    assert "instagram_meta" in eval_results

    yt = eval_results["youtube"]
    ig = eval_results["instagram_meta"]

    # Both assess the exact same detected risk
    assert yt.confidence_score == 0.70
    assert ig.confidence_score == 0.70
    # But each applies its own platform-specific rules and sources
    assert yt.platform == "YouTube"
    assert ig.platform == "Instagram / Meta"
    assert yt.triggered_rule_id == "YT-HARASS-01"
    assert ig.triggered_rule_id == "META-BULLY-01"
    assert "youtube" in yt.source_url.lower()
    assert "meta.com" in ig.source_url.lower()


def test_experiment_policy_adaptation_without_ml_retraining():
    """
    Research Experiment 2:
    Takes identical detected events.
    Switches policy profile from v1 Standard to v2 Strict.
    Demonstrates that policy assessments shift WITHOUT retraining the ML model!
    """
    detected_events = [
        {
            "start": 14.2,
            "end": 18.7,
            "text": "Borderline offensive remark in Hinglish",
            "label": "harassment",
            "confidence": 0.55,  # Borderline confidence
        }
    ]

    exp = policy_engine.run_adaptation_experiment(
        events=detected_events,
        v1_name="v1",
        v2_name="v2",
    )

    v1_event = exp["policy_v1_results"][0]
    v2_event = exp["policy_v2_results"][0]

    # Detections are 100% identical
    assert v1_event["label"] == v2_event["label"] == "harassment"
    assert v1_event["confidence"] == v2_event["confidence"] == 0.55
    assert v1_event["start"] == v2_event["start"] == 14.2
    assert v1_event["end"] == v2_event["end"] == 18.7

    # Under v1 (Standard): YouTube threshold is 0.65 -> confidence 0.55 is "requires_review"
    assert v1_event["youtube"].status == "requires_review"

    # Under v2 (Strict Civic Policy): YouTube threshold tightened to 0.50 -> shifts to "potential_policy_violation"!
    assert v2_event["youtube"].status == "potential_policy_violation"
