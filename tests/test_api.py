"""
FastAPI Integration Tests.
Tests all endpoints:
- POST /api/analyze (Video upload, duration checks, format validation)
- POST /api/analyze/text (Text mode)
- POST /api/policy/adapt (Policy adaptation experiment)
- GET  /api/history
- GET  /api/history/{id}
- GET  /api/policies
"""

from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)
MEDIA_DIR = Path(__file__).parent / "test_media"


def test_analyze_unsupported_file_extension():
    # Attempting to upload a .txt file to /api/analyze
    fake_file = {"file": ("test.txt", b"plain text content", "text/plain")}
    response = client.post("/api/analyze", files=fake_file)
    assert response.status_code == 400
    assert "Unsupported file type" in response.json()["detail"]


def test_analyze_video_exceeds_max_duration():
    # 65s video fixture exceeds the 60s limit
    long_video = MEDIA_DIR / "test_long_65s.mp4"
    assert long_video.exists()
    with open(long_video, "rb") as f:
        response = client.post("/api/analyze", files={"file": ("test_long_65s.mp4", f, "video/mp4")})
    assert response.status_code == 400
    assert "max is 60" in response.json()["detail"].lower() or "maximum allowed" in response.json()["detail"].lower()


def test_analyze_valid_speech_video():
    video_path = MEDIA_DIR / "test_speech_video.mp4"
    assert video_path.exists()
    with open(video_path, "rb") as f:
        response = client.post("/api/analyze", files={"file": ("test_speech_video.mp4", f, "video/mp4")})

    assert response.status_code == 200
    data = response.json()
    assert "video_id" in data
    assert "duration_seconds" in data
    assert data["duration_seconds"] <= 60
    assert "segments" in data
    assert "policy_overview" in data
    assert "youtube" in data["policy_overview"]
    assert "instagram_meta" in data["policy_overview"]

    # Check each segment contains multiplatform assessments with identical timestamps
    for seg in data["segments"]:
        assert "start" in seg
        assert "end" in seg
        assert "text" in seg
        assert "label" in seg
        assert "confidence" in seg
        assert "youtube_policy" in seg
        assert "instagram_policy" in seg
        assert seg["youtube_policy"]["platform"] == "YouTube"
        assert seg["instagram_policy"]["platform"] == "Instagram / Meta"


def test_analyze_silent_video():
    silent_video = MEDIA_DIR / "test_silent_3s.mp4"
    assert silent_video.exists()
    with open(silent_video, "rb") as f:
        response = client.post("/api/analyze", files={"file": ("test_silent_3s.mp4", f, "video/mp4")})
    assert response.status_code == 200
    data = response.json()
    assert data["duration_seconds"] <= 60


def test_analyze_text_endpoint_normal():
    response = client.post(
        "/api/analyze/text",
        json={"text": "Yeh kitna sundar video hai, wonderful travel memories!"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["segments"]) == 1
    seg = data["segments"][0]
    assert seg["label"] == "normal"
    assert seg["youtube_policy"]["status"] == "low_concern"
    assert seg["instagram_policy"]["status"] == "low_concern"


def test_analyze_text_endpoint_hindi_english_risk():
    response = client.post(
        "/api/analyze/text",
        json={"text": "Abe idiot chup kar bilkul bakwas kar raha hai saale"}
    )
    assert response.status_code == 200
    data = response.json()
    seg = data["segments"][0]
    assert seg["label"] in ["harassment", "hate_speech"]
    assert seg["confidence"] > 0.40
    assert seg["youtube_policy"] is not None
    assert seg["instagram_policy"] is not None


def test_policy_adapt_endpoint():
    request_data = {
        "events": [
            {
                "start": 10.0,
                "end": 14.0,
                "text": "Borderline toxic insult in Hinglish",
                "label": "harassment",
                "confidence": 0.54,
            }
        ],
        "v1_version": "v1",
        "v2_version": "v2",
    }
    response = client.post("/api/policy/adapt", json=request_data)
    assert response.status_code == 200
    data = response.json()
    assert "policy_v1_results" in data
    assert "policy_v2_results" in data
    # Shows policy shift without ML retraining
    assert data["policy_v1_results"][0]["youtube"]["status"] == "requires_review"
    assert data["policy_v2_results"][0]["youtube"]["status"] == "potential_policy_violation"


def test_history_endpoints():
    # 1. Fetch history list
    res_list = client.get("/api/history")
    assert res_list.status_code == 200
    items = res_list.json()
    assert isinstance(items, list)

    if len(items) > 0:
        first_id = items[0]["id"]
        res_detail = client.get(f"/api/history/{first_id}")
        assert res_detail.status_code == 200
        detail = res_detail.json()
        assert "video_id" in detail
        assert "segments" in detail


def test_policy_definitions_endpoint():
    response = client.get("/api/policies")
    assert response.status_code == 200
    data = response.json()
    assert "YouTube" in data
    assert "Instagram / Meta" in data
