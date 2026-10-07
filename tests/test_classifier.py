"""
Tests for ML Risk Classifier and HateBERT comparative service.
"""

from app.services.classifier import classify_text, classify_segments
from app.services.classifier_hatebert import analyze_hatebert_tokenization


def test_classify_normal_speech():
    result = classify_text("Yeh bahut sundar video hai, thanks for sharing this great vlog!")
    assert result["label"] == "normal"
    assert "confidence" in result
    assert 0.0 <= result["confidence"] <= 1.0
    assert "probabilities" in result


def test_classify_hindi_english_harassment():
    result = classify_text("Abe idiot chup kar bilkul bakwas kar raha hai tu")
    assert result["label"] in ["harassment", "hate_speech"]
    assert result["confidence"] > 0.40


def test_classify_threat():
    result = classify_text("Teri aukaat nahi hai, goli maar dunga saale jaan se maar dunga")
    assert result["label"] in ["hate_speech", "harassment"]
    assert result["confidence"] > 0.50


def test_classify_empty_string():
    result = classify_text("   ")
    assert result["label"] == "normal"
    assert result["confidence"] == 1.0


def test_classify_segments_preserves_structure():
    raw_segments = [
        {"start": 0.0, "end": 2.5, "text": "Namaste dosto swagat hai aapka."},
        {"start": 2.5, "end": 5.0, "text": "Abe idiot chup kar bakwas band kar."},
    ]
    classified = classify_segments(raw_segments)
    assert len(classified) == 2
    for seg in classified:
        assert "start" in seg
        assert "end" in seg
        assert "text" in seg
        assert "label" in seg
        assert "confidence" in seg
        assert "probabilities" in seg


def test_hatebert_subword_fragmentation():
    # Demonstrates empirical finding: HateBERT fragments Hindi transliterations
    analysis = analyze_hatebert_tokenization("Abe saale bhakt tera dimag kharab hai kya")
    assert analysis["token_count"] > 10
    assert len(analysis["subword_fragments"]) > 0
