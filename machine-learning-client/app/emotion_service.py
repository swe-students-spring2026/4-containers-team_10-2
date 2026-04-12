"""Emotion detection service layer."""

from app.label_mapper import emotion_to_border_color, normalize_emotion


def detect_emotion(_image):
    """Return a stubbed emotion analysis result for the provided image."""
    raw_emotion = "happy"
    emotion = normalize_emotion(raw_emotion)

    return {
        "face_detected": True,
        "raw_emotion": raw_emotion,
        "emotion": emotion,
        "confidence": 0.95,
        "scores": {
            "happy": 0.95,
            "neutral": 0.04,
            "sad": 0.01,
        },
        "border_color": emotion_to_border_color(emotion),
    }
