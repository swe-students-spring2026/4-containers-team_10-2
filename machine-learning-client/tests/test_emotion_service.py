"""Tests for emotion_service module."""

from app.emotion_service import detect_emotion


def test_detect_emotion_returns_expected_shape():
    """Result dict contains all required keys."""
    result = detect_emotion("any_image_payload")
    expected_keys = {
        "face_detected",
        "raw_emotion",
        "emotion",
        "confidence",
        "scores",
        "border_color",
    }
    assert expected_keys.issubset(result.keys())


def test_detect_emotion_stub_values():
    """Stub returns the hardcoded happy result."""
    result = detect_emotion("payload")
    assert result["face_detected"] is True
    assert result["raw_emotion"] == "happy"
    assert result["emotion"] == "happy"
    assert result["confidence"] == 0.95
    assert result["border_color"] == "yellow"


def test_detect_emotion_scores_structure():
    """Scores dict contains all emotion categories with valid values."""
    result = detect_emotion("payload")
    scores = result["scores"]
    assert set(scores.keys()) == {"happy", "neutral", "sad"}
    for value in scores.values():
        assert 0.0 <= value <= 1.0


def test_detect_emotion_ignores_input():
    """Stub produces the same result regardless of input."""
    assert detect_emotion("a") == detect_emotion("b")
    assert detect_emotion(None) == detect_emotion("")
