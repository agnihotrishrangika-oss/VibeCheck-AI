"""
Tests for Postprocessor: confidence thresholding, adjacent segment merging, and temporal IoU.
"""

from app.services.postprocessor import postprocess_segments, compute_temporal_iou


def test_confidence_threshold_downgrades_to_normal():
    segments = [
        {"start": 0.0, "end": 2.0, "text": "borderline word", "label": "harassment", "confidence": 0.35},
    ]
    processed = postprocess_segments(segments, confidence_threshold=0.50)
    assert len(processed) == 1
    assert processed[0]["label"] == "normal"


def test_merge_adjacent_risk_segments():
    # Two adjacent harassment segments within 0.5s gap should merge into one
    segments = [
        {"start": 10.0, "end": 12.0, "text": "Abe idiot", "label": "harassment", "confidence": 0.80},
        {"start": 12.3, "end": 14.5, "text": "bakwas band kar", "label": "harassment", "confidence": 0.85},
    ]
    merged = postprocess_segments(segments, confidence_threshold=0.50, gap_seconds=1.0)
    assert len(merged) == 1
    assert merged[0]["start"] == 10.0
    assert merged[0]["end"] == 14.5
    assert merged[0]["text"] == "Abe idiot bakwas band kar"
    assert merged[0]["confidence"] == 0.85
    assert merged[0]["label"] == "harassment"


def test_non_adjacent_segments_do_not_merge():
    # Gap is 3.0s > 1.0s gap threshold
    segments = [
        {"start": 5.0, "end": 7.0, "text": "Abe idiot", "label": "harassment", "confidence": 0.80},
        {"start": 10.0, "end": 12.0, "text": "chup kar", "label": "harassment", "confidence": 0.82},
    ]
    merged = postprocess_segments(segments, confidence_threshold=0.50, gap_seconds=1.0)
    assert len(merged) == 2
    assert merged[0]["start"] == 5.0
    assert merged[1]["start"] == 10.0


def test_different_risk_labels_do_not_merge():
    segments = [
        {"start": 5.0, "end": 7.0, "text": "saale idiot", "label": "harassment", "confidence": 0.80},
        {"start": 7.1, "end": 9.0, "text": "goli maar dunga", "label": "hate_speech", "confidence": 0.90},
    ]
    merged = postprocess_segments(segments, confidence_threshold=0.50, gap_seconds=1.0)
    assert len(merged) == 2


def test_temporal_iou():
    # Identical interval
    assert compute_temporal_iou((10.0, 20.0), (10.0, 20.0)) == 1.0
    # No overlap
    assert compute_temporal_iou((10.0, 15.0), (20.0, 25.0)) == 0.0
    # 50% overlap: [10, 20] and [15, 25] -> intersection = [15, 20] (5), union = [10, 25] (15) -> 5/15 = 0.3333
    iou = compute_temporal_iou((10.0, 20.0), (15.0, 25.0))
    assert abs(iou - (5.0 / 15.0)) < 1e-3
