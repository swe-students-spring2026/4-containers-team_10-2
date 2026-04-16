"""Tests for image_utils module."""

from app.image_utils import decode_base64_image


def test_decode_base64_image_returns_input():
    """Stub implementation returns the input unchanged."""
    payload = "abc123=="
    assert decode_base64_image(payload) == payload


def test_decode_base64_image_with_empty_string():
    """Empty string is returned unchanged."""
    assert decode_base64_image("") == ""


def test_decode_base64_image_with_none():
    """None is returned unchanged (stub has no validation)."""
    assert decode_base64_image(None) is None
