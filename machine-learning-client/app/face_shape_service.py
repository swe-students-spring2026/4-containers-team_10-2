"""Face-shape analysis service."""

# pylint: disable=no-member,too-many-locals,too-many-return-statements

from collections import Counter, defaultdict, deque
from math import atan2, degrees, hypot

import cv2
import mediapipe as mp

from app.label_mapper import get_hairstyle_recommendations, normalize_face_shape


mp_face_mesh = mp.solutions.face_mesh
_face_mesh = mp_face_mesh.FaceMesh(
    static_image_mode=False,
    max_num_faces=1,
    refine_landmarks=False,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5,
)

_session_history = defaultdict(lambda: deque(maxlen=10))

_MAX_ROLL_DEGREES = 12.0

_TOP = 10
_CHIN = 152
_FOREHEAD_L = 103
_FOREHEAD_R = 332
_CHEEK_L = 234
_CHEEK_R = 454
_EYE_L = 33
_EYE_R = 263

_JAW_LEFT_CLUSTER = [172, 136, 150, 149]
_JAW_RIGHT_CLUSTER = [397, 365, 379, 378]
_CHIN_LEFT_CLUSTER = [136, 135, 169]
_CHIN_RIGHT_CLUSTER = [365, 364, 394]


def _pt(landmarks, idx, width, height):
    """Return one landmark point."""
    landmark = landmarks[idx]
    return landmark.x * width, landmark.y * height


def _dist(point_a, point_b):
    """Return Euclidean distance."""
    return hypot(point_a[0] - point_b[0], point_a[1] - point_b[1])


def _avg_pt(landmarks, indices, width, height):
    """Return a centroid."""
    xs = [landmarks[idx].x * width for idx in indices]
    ys = [landmarks[idx].y * height for idx in indices]
    return sum(xs) / len(xs), sum(ys) / len(ys)


def _roll_degrees(landmarks, width, height):
    """Return face roll in degrees."""
    eye_left = _pt(landmarks, _EYE_L, width, height)
    eye_right = _pt(landmarks, _EYE_R, width, height)
    return degrees(atan2(eye_right[1] - eye_left[1], eye_right[0] - eye_left[0]))


def _bounding_box(landmarks, width, height):
    """Return landmark bounding box."""
    xs = [landmark.x * width for landmark in landmarks]
    ys = [landmark.y * height for landmark in landmarks]

    min_x = int(max(min(xs), 0))
    min_y = int(max(min(ys), 0))
    max_x = int(min(max(xs), width))
    max_y = int(min(max(ys), height))

    return {
        "x": min_x,
        "y": min_y,
        "width": max_x - min_x,
        "height": max_y - min_y,
    }


def _extract_features(landmarks, width, height):
    """Extract face-shape features."""
    top = _pt(landmarks, _TOP, width, height)
    chin = _pt(landmarks, _CHIN, width, height)

    forehead_left = _pt(landmarks, _FOREHEAD_L, width, height)
    forehead_right = _pt(landmarks, _FOREHEAD_R, width, height)

    cheek_left = _pt(landmarks, _CHEEK_L, width, height)
    cheek_right = _pt(landmarks, _CHEEK_R, width, height)

    jaw_left = _avg_pt(landmarks, _JAW_LEFT_CLUSTER, width, height)
    jaw_right = _avg_pt(landmarks, _JAW_RIGHT_CLUSTER, width, height)

    chin_left = _avg_pt(landmarks, _CHIN_LEFT_CLUSTER, width, height)
    chin_right = _avg_pt(landmarks, _CHIN_RIGHT_CLUSTER, width, height)

    face_length = _dist(top, chin)
    forehead_width = _dist(forehead_left, forehead_right)
    cheekbone_width = _dist(cheek_left, cheek_right)
    jaw_width = _dist(jaw_left, jaw_right)
    chin_width = _dist(chin_left, chin_right)

    if cheekbone_width <= 0 or jaw_width <= 0 or forehead_width <= 0:
        return None

    return {
        "face_length": face_length,
        "forehead_width": forehead_width,
        "cheekbone_width": cheekbone_width,
        "jaw_width": jaw_width,
        "chin_width": chin_width,
        "length_to_cheek": face_length / cheekbone_width,
        "forehead_to_jaw": forehead_width / jaw_width,
        "jaw_to_forehead": jaw_width / forehead_width,
        "cheek_to_forehead": cheekbone_width / forehead_width,
        "cheek_to_jaw": cheekbone_width / jaw_width,
        "chin_to_jaw": chin_width / jaw_width,
        "chin_to_cheek": chin_width / cheekbone_width,
    }


def _classify(features):
    """Classify a face shape."""
    length_to_cheek = features["length_to_cheek"]
    forehead_to_jaw = features["forehead_to_jaw"]
    jaw_to_forehead = features["jaw_to_forehead"]
    cheek_to_forehead = features["cheek_to_forehead"]
    cheek_to_jaw = features["cheek_to_jaw"]
    chin_to_jaw = features["chin_to_jaw"]

    # Heart: wide forehead, narrow pointed chin
    if forehead_to_jaw > 1.08 and chin_to_jaw < 0.82 and length_to_cheek < 1.55:
        return "Heart"

    # Triangle: wide jaw, narrow forehead
    if jaw_to_forehead > 1.08 and cheek_to_jaw <= 1.06:
        return "Triangle"

    # Diamond: prominent cheekbones wider than both forehead and jaw
    if cheek_to_forehead > 1.09 and cheek_to_jaw > 1.09 and 1.18 <= length_to_cheek <= 1.50:
        return "Diamond"

    # Oblong: long face with balanced widths
    if length_to_cheek > 1.50 and abs(forehead_to_jaw - 1.0) < 0.20:
        return "Oblong"

    # Oval: moderately long face with gently tapered proportions
    if 1.28 < length_to_cheek <= 1.55 and forehead_to_jaw >= 0.88:
        return "Oval"

    # Square: compact face with even forehead/jaw widths
    if (
        length_to_cheek <= 1.38
        and abs(forehead_to_jaw - 1.0) < 0.13
        and cheek_to_jaw < 1.10
        and chin_to_jaw >= 0.80
    ):
        return "Square"

    # Round: short face with rounded chin
    if length_to_cheek <= 1.30 and chin_to_jaw < 0.90 and cheek_to_forehead < 1.12:
        return "Round"

    # Soft fallback based on length ratio — avoids "Unknown" for borderline faces
    if length_to_cheek <= 1.30:
        return "Round"
    if length_to_cheek <= 1.50:
        return "Oval"
    return "Oblong"


def _smooth_shape(session_id, shape):
    """Return rolling majority vote."""
    history = _session_history[session_id]
    history.append(shape)
    return Counter(history).most_common(1)[0][0]


def _estimate_confidence(shape, features):
    """Estimate confidence."""
    base = {
        "Oval": 0.84,
        "Round": 0.82,
        "Square": 0.80,
        "Oblong": 0.80,
        "Diamond": 0.78,
        "Heart": 0.78,
        "Triangle": 0.76,
        "Unknown": 0.50,
    }.get(shape, 0.50)

    length_to_cheek = features["length_to_cheek"]
    forehead_to_jaw = features["forehead_to_jaw"]
    jaw_to_forehead = features["jaw_to_forehead"]
    cheek_to_forehead = features["cheek_to_forehead"]
    cheek_to_jaw = features["cheek_to_jaw"]
    chin_to_jaw = features["chin_to_jaw"]

    if shape == "Heart" and forehead_to_jaw > 1.12 and chin_to_jaw < 0.76:
        base += 0.05
    elif shape == "Triangle" and jaw_to_forehead > 1.12:
        base += 0.05
    elif shape == "Diamond" and cheek_to_forehead > 1.10 and cheek_to_jaw > 1.10:
        base += 0.05
    elif shape == "Oblong" and length_to_cheek > 1.65:
        base += 0.05
    elif shape == "Oval" and 1.40 <= length_to_cheek <= 1.55:
        base += 0.04
    elif shape == "Square" and abs(forehead_to_jaw - 1.0) < 0.05:
        base += 0.04
    elif shape == "Round" and 1.02 <= length_to_cheek <= 1.18:
        base += 0.04

    return min(round(base, 2), 0.95)


def detect_face_shape(image, session_id="default-session"):
    """Detect and classify face shape."""
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = _face_mesh.process(rgb)

    if not results.multi_face_landmarks:
        _session_history[session_id].clear()
        face_shape = "Unknown"
        return {
            "face_detected": False,
            "face_shape": face_shape,
            "confidence": 0.0,
            "recommended_hairstyles": get_hairstyle_recommendations(face_shape),
            "face_box": None,
        }

    height, width = image.shape[:2]
    landmarks = results.multi_face_landmarks[0].landmark

    roll = _roll_degrees(landmarks, width, height)
    if abs(roll) > _MAX_ROLL_DEGREES:
        current_best = (
            Counter(_session_history[session_id]).most_common(1)[0][0]
            if _session_history[session_id]
            else "Unknown"
        )
        face_shape = normalize_face_shape(current_best)
        features = _extract_features(landmarks, width, height)
        confidence = _estimate_confidence(face_shape, features) if features else 0.0

        return {
            "face_detected": True,
            "face_shape": face_shape,
            "confidence": round(confidence * 0.85, 2),
            "recommended_hairstyles": get_hairstyle_recommendations(face_shape),
            "face_box": _bounding_box(landmarks, width, height),
        }

    features = _extract_features(landmarks, width, height)
    raw_shape = _classify(features) if features else "Unknown"
    face_shape = normalize_face_shape(raw_shape)
    face_shape = _smooth_shape(session_id, face_shape)
    confidence = _estimate_confidence(face_shape, features) if features else 0.0
    face_box = _bounding_box(landmarks, width, height)

    return {
        "face_detected": True,
        "face_shape": face_shape,
        "confidence": confidence,
        "recommended_hairstyles": get_hairstyle_recommendations(face_shape),
        "face_box": face_box,
    }
