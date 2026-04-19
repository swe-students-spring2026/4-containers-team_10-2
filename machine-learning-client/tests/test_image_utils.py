"""Tests for image utils."""

# pylint: disable=no-member

import base64

import cv2
import numpy as np

from app.image_utils import decode_base64_image


def test_decode_base64_image_none():
    """None input returns None."""
    assert decode_base64_image(None) is None


def test_decode_base64_image_empty_string():
    """Empty string is returned unchanged."""
    assert decode_base64_image("") == ""


def test_decode_base64_image_invalid_string_returns_original():
    """Invalid image payload falls back to original input."""
    payload = "not-valid-base64"
    assert decode_base64_image(payload) == payload


def test_decode_base64_image_valid_image():
    """Valid base64 image decodes to ndarray."""
    image = np.zeros((10, 10, 3), dtype=np.uint8)
    success, encoded = cv2.imencode(".jpg", image)
    assert success is True

    payload = base64.b64encode(encoded.tobytes()).decode("utf-8")
    decoded = decode_base64_image(payload)

    assert isinstance(decoded, np.ndarray)
    assert decoded.shape[0] > 0
    assert decoded.shape[1] > 0


def test_decode_base64_image_with_data_url_prefix():
    """Data URL prefix is handled."""
    image = np.zeros((8, 8, 3), dtype=np.uint8)
    success, encoded = cv2.imencode(".jpg", image)
    assert success is True

    raw = base64.b64encode(encoded.tobytes()).decode("utf-8")
    payload = f"data:image/jpeg;base64,{raw}"
    decoded = decode_base64_image(payload)

    assert isinstance(decoded, np.ndarray)
