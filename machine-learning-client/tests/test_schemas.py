"""Tests for schemas."""

from app.schemas import build_prediction_document


def test_build_prediction_document():
    """Prediction document is built correctly."""
    result = {
        "face_detected": True,
        "face_shape": "Oval",
        "confidence": 0.91,
        "recommended_hairstyles": {
            "male": [{"name": "Classic side part"}],
            "female": [{"name": "Shoulder-length lob"}],
        },
        "face_box": {"x": 1, "y": 2, "width": 3, "height": 4},
    }

    doc = build_prediction_document("user-1", "session-1", result)

    assert doc["user_id"] == "user-1"
    assert doc["session_id"] == "session-1"
    assert doc["face_detected"] is True
    assert doc["face_shape"] == "Oval"
    assert doc["confidence"] == 0.91
    assert doc["recommended_hairstyles"] == result["recommended_hairstyles"]
    assert doc["face_box"] == result["face_box"]
    assert "timestamp" in doc
