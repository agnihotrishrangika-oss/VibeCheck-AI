"""
Step 4: Postprocessor.
Applies confidence thresholds, merges adjacent risk events within a temporal tolerance window,
preserves timestamps, and provides temporal IoU computation.
"""

from typing import List, Dict, Any, Tuple


def compute_temporal_iou(interval_a: Tuple[float, float], interval_b: Tuple[float, float]) -> float:
    """
    Computes Intersection over Union (IoU) between two temporal windows: (start, end).
    Used for temporal localization benchmarking against ground truth.
    """
    start_a, end_a = interval_a
    start_b, end_b = interval_b

    intersection_start = max(start_a, start_b)
    intersection_end = min(end_a, end_b)
    intersection_len = max(0.0, intersection_end - intersection_start)

    union_start = min(start_a, start_b)
    union_end = max(end_a, end_b)
    union_len = max(1e-6, union_end - union_start)

    return round(intersection_len / union_len, 4)


def postprocess_segments(
    segments: List[Dict[str, Any]],
    confidence_threshold: float = 0.50,
    gap_seconds: float = 1.0,
) -> List[Dict[str, Any]]:
    """
    Postprocessing pipeline:
    1. Re-labels segments below confidence_threshold as 'normal'.
    2. Merges adjacent flagged segments with identical labels if separated by <= gap_seconds.
    3. Preserves exact start and end timestamps.
    """
    if not segments:
        return []

    # Step 1: Threshold validation
    processed: List[Dict[str, Any]] = []
    for seg in segments:
        seg_copy = dict(seg)
        conf = seg_copy.get("confidence", 0.0)
        label = seg_copy.get("label", "normal")

        if label != "normal" and conf < confidence_threshold:
            # Downgrade sub-threshold risk to normal
            seg_copy["label"] = "normal"

        processed.append(seg_copy)

    # Step 2: Merge adjacent segments with identical risk labels
    merged: List[Dict[str, Any]] = []
    current = processed[0]

    for next_seg in processed[1:]:
        can_merge = (
            current["label"] != "normal"
            and current["label"] == next_seg["label"]
            and (next_seg["start"] - current["end"]) <= gap_seconds
        )

        if can_merge:
            # Merge adjacent segments
            current["end"] = round(next_seg["end"], 2)
            current["text"] = f"{current['text']} {next_seg['text']}".strip()
            # Confidence is max of the combined windows
            current["confidence"] = round(max(current["confidence"], next_seg["confidence"]), 4)
            if "probabilities" in current and "probabilities" in next_seg:
                # Merge probabilities
                label = current["label"]
                current["probabilities"][label] = current["confidence"]
        else:
            merged.append(current)
            current = next_seg

    merged.append(current)
    return merged
