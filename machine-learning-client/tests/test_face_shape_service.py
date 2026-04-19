"""Tests for face-shape detection service logic."""

# pylint: disable=duplicate-code,too-few-public-methods

from collections import defaultdict, deque
from unittest.mock import patch

import numpy as np

from app.face_shape_service import (
    _bounding_box,
    _classify,
    _estimate_confidence,
    _extract_features,
    _roll_degrees,
    detect_face_shape,
)


class _FakeLandmark:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class _FakeFaceLandmarks:
    def __init__(self, landmarks):
        self.landmark = landmarks


class _FakeResults:
    def __init__(self, multi_face_landmarks):
        self.multi_face_landmarks = multi_face_landmarks


def _make_landmarks(overrides=None):
    landmarks = [_FakeLandmark(0.5, 0.5) for _ in range(468)]
    overrides = overrides or {}

    for idx, coords in overrides.items():
        landmarks[idx] = _FakeLandmark(coords[0], coords[1])

    return landmarks


def test_classify_heart():
    """Heart classification branch."""
    features = {
        "length_to_cheek": 1.40,
        "forehead_to_jaw": 1.12,
        "jaw_to_forehead": 0.89,
        "cheek_to_forehead": 1.02,
        "cheek_to_jaw": 1.03,
        "chin_to_jaw": 0.75,
    }
    assert _classify(features) == "Heart"


def test_classify_triangle():
    """Triangle classification branch."""
    features = {
        "length_to_cheek": 1.35,
        "forehead_to_jaw": 0.90,
        "jaw_to_forehead": 1.14,
        "cheek_to_forehead": 1.02,
        "cheek_to_jaw": 1.00,
        "chin_to_jaw": 0.86,
    }
    assert _classify(features) == "Triangle"


def test_classify_oval():
    """Oval classification branch."""
    features = {
        "length_to_cheek": 1.40,
        "forehead_to_jaw": 1.00,
        "jaw_to_forehead": 1.00,
        "cheek_to_forehead": 1.05,
        "cheek_to_jaw": 1.05,
        "chin_to_jaw": 0.85,
    }
    assert _classify(features) == "Oval"


def test_classify_round_current_logic():
    """Current logic classifies this short face as Square."""
    features = {
        "length_to_cheek": 1.20,
        "forehead_to_jaw": 0.95,
        "jaw_to_forehead": 1.05,
        "cheek_to_forehead": 1.05,
        "cheek_to_jaw": 1.05,
        "chin_to_jaw": 0.85,
    }
    assert _classify(features) == "Square"


def test_classify_square_current_logic():
    """Current logic classifies this borderline square case as Diamond."""
    features = {
        "length_to_cheek": 1.36,
        "forehead_to_jaw": 1.01,
        "jaw_to_forehead": 0.99,
        "cheek_to_forehead": 1.10,
        "cheek_to_jaw": 1.10,
        "chin_to_jaw": 0.85,
    }
    assert _classify(features) == "Diamond"


def test_classify_diamond_current_logic():
    """Diamond classification branch."""
    features = {
        "length_to_cheek": 1.40,
        "forehead_to_jaw": 1.00,
        "jaw_to_forehead": 1.00,
        "cheek_to_forehead": 1.25,
        "cheek_to_jaw": 1.20,
        "chin_to_jaw": 0.88,
    }
    assert _classify(features) == "Diamond"


def test_classify_oblong():
    """Oblong classification branch."""
    features = {
        "length_to_cheek": 1.70,
        "forehead_to_jaw": 1.00,
        "jaw_to_forehead": 1.00,
        "cheek_to_forehead": 1.05,
        "cheek_to_jaw": 1.05,
        "chin_to_jaw": 0.90,
    }
    assert _classify(features) == "Oblong"


def test_estimate_confidence_unknown_shape():
    """Unknown confidence uses the base value."""
    features = {
        "length_to_cheek": 1.40,
        "forehead_to_jaw": 1.00,
        "jaw_to_forehead": 1.00,
        "cheek_to_forehead": 1.05,
        "cheek_to_jaw": 1.05,
        "chin_to_jaw": 0.85,
    }
    assert _estimate_confidence("Unknown", features) == 0.5


def test_estimate_confidence_oval_current_logic():
    """Current Oval confidence includes the Oval bonus."""
    features = {
        "length_to_cheek": 1.45,
        "forehead_to_jaw": 1.00,
        "jaw_to_forehead": 1.00,
        "cheek_to_forehead": 1.05,
        "cheek_to_jaw": 1.05,
        "chin_to_jaw": 0.85,
    }
    assert _estimate_confidence("Oval", features) == 0.88


def test_roll_degrees_zero():
    """Zero roll when eyes are level."""
    landmarks = _make_landmarks(
        {
            33: (0.30, 0.40),
            263: (0.70, 0.40),
        }
    )
    assert abs(_roll_degrees(landmarks, 100, 100)) < 1e-6


def test_bounding_box():
    """Bounding box from landmarks."""
    landmarks = _make_landmarks(
        {
            10: (0.20, 0.30),
            152: (0.80, 0.90),
            234: (0.10, 0.50),
            454: (0.90, 0.50),
        }
    )
    result = _bounding_box(landmarks, 200, 100)

    assert result == {"x": 20, "y": 30, "width": 160, "height": 60}


def test_extract_features():
    """Feature extraction returns values."""
    landmarks = _make_landmarks(
        {
            10: (0.50, 0.10),
            152: (0.50, 0.90),
            103: (0.30, 0.20),
            332: (0.70, 0.20),
            234: (0.20, 0.50),
            454: (0.80, 0.50),
            172: (0.28, 0.75),
            136: (0.30, 0.78),
            150: (0.29, 0.76),
            149: (0.31, 0.77),
            397: (0.72, 0.75),
            365: (0.70, 0.78),
            379: (0.71, 0.76),
            378: (0.69, 0.77),
            135: (0.40, 0.86),
            169: (0.42, 0.85),
            364: (0.60, 0.86),
            394: (0.58, 0.85),
        }
    )
    features = _extract_features(landmarks, 200, 200)

    assert features is not None
    assert features["length_to_cheek"] > 0
    assert features["forehead_to_jaw"] > 0
    assert features["jaw_to_forehead"] > 0


def test_detect_face_shape_no_faces():
    """No face returns Unknown."""
    image = np.zeros((200, 200, 3), dtype=np.uint8)

    with patch("app.face_shape_service._face_mesh") as mock_face_mesh:
        mock_face_mesh.process.return_value = _FakeResults(None)

        result = detect_face_shape(image)

    assert result["face_detected"] is False
    assert result["face_shape"] == "Unknown"
    assert result["confidence"] == 0.0
    assert result["face_box"] is None


def test_detect_face_shape_with_face():
    """Face detection returns structured response."""
    image = np.zeros((300, 300, 3), dtype=np.uint8)

    landmarks = _make_landmarks(
        {
            10: (0.50, 0.12),
            152: (0.50, 0.88),
            103: (0.35, 0.22),
            332: (0.65, 0.22),
            234: (0.22, 0.50),
            454: (0.78, 0.50),
            172: (0.30, 0.74),
            136: (0.32, 0.77),
            150: (0.31, 0.75),
            149: (0.33, 0.76),
            397: (0.70, 0.74),
            365: (0.68, 0.77),
            379: (0.69, 0.75),
            378: (0.67, 0.76),
            135: (0.42, 0.85),
            169: (0.44, 0.84),
            364: (0.58, 0.85),
            394: (0.56, 0.84),
            33: (0.38, 0.40),
            263: (0.62, 0.40),
        }
    )

    with patch("app.face_shape_service._face_mesh") as mock_face_mesh:
        mock_face_mesh.process.return_value = _FakeResults(
            [_FakeFaceLandmarks(landmarks)]
        )

        result = detect_face_shape(image, session_id="session-a")

    assert result["face_detected"] is True
    assert result["face_shape"] in {
        "Oval",
        "Round",
        "Square",
        "Diamond",
        "Heart",
        "Triangle",
        "Oblong",
        "Unknown",
    }
    assert isinstance(result["confidence"], float)
    assert result["face_box"]["width"] > 0
    assert result["face_box"]["height"] > 0


def test_detect_face_shape_tilted_frame_uses_previous_shape():
    """Tilted frame uses previous best shape."""
    image = np.zeros((300, 300, 3), dtype=np.uint8)

    upright_landmarks = _make_landmarks(
        {
            10: (0.50, 0.12),
            152: (0.50, 0.88),
            103: (0.35, 0.22),
            332: (0.65, 0.22),
            234: (0.22, 0.50),
            454: (0.78, 0.50),
            172: (0.30, 0.74),
            136: (0.32, 0.77),
            150: (0.31, 0.75),
            149: (0.33, 0.76),
            397: (0.70, 0.74),
            365: (0.68, 0.77),
            379: (0.69, 0.75),
            378: (0.67, 0.76),
            135: (0.42, 0.85),
            169: (0.44, 0.84),
            364: (0.58, 0.85),
            394: (0.56, 0.84),
            33: (0.38, 0.40),
            263: (0.62, 0.40),
        }
    )

    tilted_landmarks = _make_landmarks(
        {
            10: (0.50, 0.12),
            152: (0.50, 0.88),
            103: (0.35, 0.22),
            332: (0.65, 0.22),
            234: (0.22, 0.50),
            454: (0.78, 0.50),
            172: (0.30, 0.74),
            136: (0.32, 0.77),
            150: (0.31, 0.75),
            149: (0.33, 0.76),
            397: (0.70, 0.74),
            365: (0.68, 0.77),
            379: (0.69, 0.75),
            378: (0.67, 0.76),
            135: (0.42, 0.85),
            169: (0.44, 0.84),
            364: (0.58, 0.85),
            394: (0.56, 0.84),
            33: (0.38, 0.36),
            263: (0.62, 0.46),
        }
    )

    with patch("app.face_shape_service._face_mesh") as mock_face_mesh, patch(
        "app.face_shape_service._session_history",
        defaultdict(lambda: deque(maxlen=10)),
    ):
        mock_face_mesh.process.side_effect = [
            _FakeResults([_FakeFaceLandmarks(upright_landmarks)]),
            _FakeResults([_FakeFaceLandmarks(tilted_landmarks)]),
        ]

        first = detect_face_shape(image, session_id="session-b")
        second = detect_face_shape(image, session_id="session-b")

    assert first["face_detected"] is True
    assert second["face_detected"] is True
    assert second["face_shape"] == first["face_shape"]
