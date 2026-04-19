"""Tests for face-shape detection service logic."""

# pylint: disable=duplicate-code

from unittest.mock import patch

import numpy as np

from app.face_shape_service import (
    _classify,
    _estimate_confidence,
    detect_face_shape,
)


def test_classify_from_aspect_ratio_oval():
    """Test oval face classification."""
    assert _classify(1.35) == "Oval"


def test_classify_from_aspect_ratio_round():
    """Test round face classification."""
    assert _classify(0.8) == "Round"


def test_classify_from_aspect_ratio_square():
    """Test square face classification."""
    assert _classify(1.2) == "Square"


def test_classify_from_aspect_ratio_diamond():
    """Test diamond face classification."""
    assert _classify(1.0) == "Diamond"


def test_classify_from_aspect_ratio_unknown():
    """Test unknown face classification fallback."""
    assert _classify(0.9) == "Unknown"


def test_estimate_confidence_unknown_shape():
    """Test confidence for unknown shape."""
    assert _estimate_confidence("Unknown", 10000) == 0.45


def test_estimate_confidence_large_face_area():
    """Test confidence increases for larger face area."""
    assert _estimate_confidence("Oval", 90000) == 0.9


def test_detect_face_shape_no_faces():
    """Test response when no faces are detected."""
    image = np.zeros((200, 200, 3), dtype=np.uint8)

    with patch("app.face_shape_service.face_cascade") as mock_cascade:
        mock_cascade.detectMultiScale.return_value = []

        result = detect_face_shape(image)

    assert result["face_detected"] is False
    assert result["face_shape"] == "Unknown"
    assert result["confidence"] == 0.0
    assert len(result["recommended_hairstyles"]) == 3
    assert result["face_box"] is None


def test_detect_face_shape_with_one_face():
    """Test response when one face is detected."""
    image = np.zeros((300, 300, 3), dtype=np.uint8)

    with patch("app.face_shape_service.face_cascade") as mock_cascade:
        mock_cascade.detectMultiScale.return_value = [(50, 60, 180, 130)]

        result = detect_face_shape(image)

    assert result["face_detected"] is True
    assert result["face_shape"] in {
        "Oval",
        "Round",
        "Square",
        "Diamond",
        "Unknown",
    }
    assert isinstance(result["confidence"], float)
    assert len(result["recommended_hairstyles"]) == 3
    assert result["face_box"] == {
        "x": 50,
        "y": 60,
        "width": 180,
        "height": 130,
    }


def test_detect_face_shape_uses_largest_face():
    """Test that the largest detected face is selected."""
    image = np.zeros((400, 400, 3), dtype=np.uint8)

    with patch("app.face_shape_service.face_cascade") as mock_cascade:
        mock_cascade.detectMultiScale.return_value = [
            (10, 10, 50, 50),
            (100, 120, 200, 140),
            (30, 30, 80, 70),
        ]

        result = detect_face_shape(image)

    assert result["face_detected"] is True
    assert result["face_box"] == {
        "x": 100,
        "y": 120,
        "width": 200,
        "height": 140,
    }


def test_detect_face_shape_returns_recommendations():
    """Test that recommendations are returned for detected face shapes."""
    image = np.zeros((300, 300, 3), dtype=np.uint8)

    with patch("app.face_shape_service.face_cascade") as mock_cascade:
        mock_cascade.detectMultiScale.return_value = [(40, 50, 170, 120)]

        result = detect_face_shape(image)

    assert "recommended_hairstyles" in result
    assert isinstance(result["recommended_hairstyles"], list)
    assert len(result["recommended_hairstyles"]) == 3
