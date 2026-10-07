"""
Step 3: ML Risk Classifier.
Uses the trained Word+Char Subword Calibrated Model for Hindi-English / Hinglish risk detection.
Outputs WHAT happened (risk label and calibrated confidence).
Does NOT decide platform policy.
"""

from pathlib import Path
from typing import Dict, List, Any
import joblib

from app.core.config import settings

_MODEL_BUNDLE = None


def get_model_bundle():
    global _MODEL_BUNDLE
    if _MODEL_BUNDLE is None:
        model_path = settings.BASE_DIR / "app" / "models" / "saved_models" / "word_char_svm_calibrated.joblib"
        if not model_path.exists():
            # Fallback to tfidf_logreg_baseline if calibrated svm is not present
            model_path = settings.BASE_DIR / "app" / "models" / "saved_models" / "tfidf_logreg_baseline.joblib"
        if not model_path.exists():
            raise FileNotFoundError(f"Trained model not found at {model_path}. Run training first.")
        
        _MODEL_BUNDLE = joblib.load(model_path)
    return _MODEL_BUNDLE


def classify_text(text: str) -> Dict[str, Any]:
    """
    Classifies a single text string.
    Returns:
      {
        "label": "normal" | "harassment" | "hate_speech",
        "confidence": float (0.0 to 1.0),
        "probabilities": {"harassment": float, "hate_speech": float, "normal": float}
      }
    """
    cleaned = text.strip()
    if not cleaned:
        return {
            "label": "normal",
            "confidence": 1.0,
            "probabilities": {"normal": 1.0, "harassment": 0.0, "hate_speech": 0.0},
        }

    bundle = get_model_bundle()
    vec = bundle["vectorizer"]
    clf = bundle["classifier"]
    classes = bundle["classes"]

    X = vec.transform([cleaned])
    
    # Check if classifier supports predict_proba (calibrated classifier)
    if hasattr(clf, "predict_proba"):
        probs = clf.predict_proba(X)[0]
        prob_dict = {c: round(float(p), 4) for c, p in zip(classes, probs)}
        predicted_idx = probs.argmax()
        label = classes[predicted_idx]
        confidence = round(float(probs[predicted_idx]), 4)
    else:
        label = clf.predict(X)[0]
        confidence = 0.85
        prob_dict = {c: (0.85 if c == label else 0.075) for c in classes}

    return {
        "label": label,
        "confidence": confidence,
        "probabilities": prob_dict,
    }


def classify_segments(segments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Takes raw whisper segments: [{"start": float, "end": float, "text": str}]
    Returns segments with label, confidence, and probabilities populated.
    """
    classified = []
    for seg in segments:
        pred = classify_text(seg["text"])
        classified.append({
            "start": seg["start"],
            "end": seg["end"],
            "text": seg["text"],
            "label": pred["label"],
            "confidence": pred["confidence"],
            "probabilities": pred["probabilities"],
        })
    return classified
