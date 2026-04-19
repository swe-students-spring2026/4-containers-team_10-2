"""Face-shape analysis service."""

# pylint: disable=no-member
# pylint: disable=too-many-locals

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
    return landmarks[idx].x * width, landmarks[idx].y * height


def _dist(a, b):
    return hypot(a[0] - b[0], a[1] - b[1])


def _avg_pt(landmarks, indices, width, height):
    xs = [landmarks[i].x * width for i in indices]
    ys = [landmarks[i].y * height for i in indices]
    return sum(xs) / len(xs), sum(ys) / len(ys)


def _roll_degrees(landmarks, width, height):
    left = _pt(landmarks, _EYE_L, width, height)
    right = _pt(landmarks, _EYE_R, width, height)
    return degrees(atan2(right[1] - left[1], right[0] - left[0]))


def _bounding_box(landmarks, width, height):
    xs = [lm.x * width for lm in landmarks]
    ys = [lm.y * height for lm in landmarks]

    min_x, max_x = int(max(min(xs), 0)), int(min(max(xs), width))
    min_y, max_y = int(max(min(ys), 0)), int(min(max(ys), height))

    return {"x": min_x, "y": min_y, "width": max_x - min_x, "height": max_y - min_y}


def _extract_features(landmarks, width, height):
    top = _pt(landmarks, _TOP, width, height)
    chin = _pt(landmarks, _CHIN, width, height)

    fl = _pt(landmarks, _FOREHEAD_L, width, height)
    fr = _pt(landmarks, _FOREHEAD_R, width, height)
    cl = _pt(landmarks, _CHEEK_L, width, height)
    cr = _pt(landmarks, _CHEEK_R, width, height)

    jl = _avg_pt(landmarks, _JAW_LEFT_CLUSTER, width, height)
    jr = _avg_pt(landmarks, _JAW_RIGHT_CLUSTER, width, height)
    chl = _avg_pt(landmarks, _CHIN_LEFT_CLUSTER, width, height)
    chr_ = _avg_pt(landmarks, _CHIN_RIGHT_CLUSTER, width, height)

    face_len = _dist(top, chin)
    fw = _dist(fl, fr)
    cw = _dist(cl, cr)
    jw = _dist(jl, jr)
    chin_w = _dist(chl, chr_)

    if cw <= 0 or jw <= 0 or fw <= 0:
        return None

    return {
        "length_to_cheek": face_len / cw,
        "forehead_to_jaw": fw / jw,
        "jaw_to_forehead": jw / fw,
        "cheek_to_forehead": cw / fw,
        "cheek_to_jaw": cw / jw,
        "chin_to_jaw": chin_w / jw,
    }


def _classify(f):
    shape = "Unknown"

    if f["length_to_cheek"] > 1.55 and abs(f["forehead_to_jaw"] - 1.0) < 0.20:
        shape = "Oblong"
    elif f["forehead_to_jaw"] > 1.10 and f["chin_to_jaw"] < 0.85:
        shape = "Heart"
    elif f["jaw_to_forehead"] > 1.10 and f["cheek_to_jaw"] < 1.15:
        shape = "Triangle"
    elif 1.30 <= f["length_to_cheek"] <= 1.55:
        shape = "Oval"
    elif f["length_to_cheek"] < 1.35:
        shape = "Round"
    elif abs(f["forehead_to_jaw"] - 1.0) < 0.12:
        shape = "Square"
    elif f["cheek_to_forehead"] > 1.20 and f["cheek_to_jaw"] > 1.18:
        shape = "Diamond"

    return shape


def _smooth(session_id, shape):
    hist = _session_history[session_id]
    hist.append(shape)
    return Counter(hist).most_common(1)[0][0]


def _estimate_confidence(shape, f):
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

    if not f:
        return base

    if shape == "Heart" and f["forehead_to_jaw"] > 1.12:
        base += 0.05
    elif shape == "Triangle" and f["jaw_to_forehead"] > 1.12:
        base += 0.05
    elif shape == "Diamond" and f["cheek_to_forehead"] > 1.20:
        base += 0.05
    elif shape == "Oblong" and f["length_to_cheek"] > 1.65:
        base += 0.05

    return min(round(base, 2), 0.95)


def _no_face(session_id):
    _session_history[session_id].clear()
    return {
        "face_detected": False,
        "face_shape": "Unknown",
        "confidence": 0.0,
        "recommended_hairstyles": get_hairstyle_recommendations("Unknown"),
        "face_box": None,
    }


def detect_face_shape(image, session_id="default-session"):
    """Detect face shape."""
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = _face_mesh.process(rgb)

    if not results.multi_face_landmarks:
        return _no_face(session_id)

    h, w = image.shape[:2]
    landmarks = results.multi_face_landmarks[0].landmark

    roll = _roll_degrees(landmarks, w, h)
    features = _extract_features(landmarks, w, h)

    if abs(roll) > _MAX_ROLL_DEGREES:
        best = (
            Counter(_session_history[session_id]).most_common(1)[0][0]
            if _session_history[session_id]
            else "Unknown"
        )
        shape = normalize_face_shape(best)
        conf = _estimate_confidence(shape, features) * 0.85
    else:
        raw = _classify(features) if features else "Unknown"
        shape = _smooth(session_id, normalize_face_shape(raw))
        conf = _estimate_confidence(shape, features)

    return {
        "face_detected": True,
        "face_shape": shape,
        "confidence": round(conf, 2),
        "recommended_hairstyles": get_hairstyle_recommendations(shape),
        "face_box": _bounding_box(landmarks, w, h),
    }
