"""Tests for label_mapper module."""

from app.label_mapper import emotion_to_border_color, normalize_emotion


def test_normalize_emotion_happy():
    """Happy label maps to 'happy'."""
    assert normalize_emotion("happy") == "happy"


def test_normalize_emotion_sad():
    """Sad label maps to 'sad'."""
    assert normalize_emotion("sad") == "sad"


def test_normalize_emotion_unknown_defaults_to_neutral():
    """Unknown labels fall back to 'neutral'."""
    assert normalize_emotion("angry") == "neutral"
    assert normalize_emotion("") == "neutral"
    assert normalize_emotion("HAPPY") == "neutral"


def test_emotion_to_border_color_known_labels():
    """Known emotions map to their designated colors."""
    assert emotion_to_border_color("happy") == "yellow"
    assert emotion_to_border_color("sad") == "blue"
    assert emotion_to_border_color("neutral") == "gray"


def test_emotion_to_border_color_unknown_defaults_to_gray():
    """Unknown emotions default to gray."""
    assert emotion_to_border_color("angry") == "gray"
    assert emotion_to_border_color("") == "gray"
    assert emotion_to_border_color(None) == "gray"
