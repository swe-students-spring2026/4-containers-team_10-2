"""Helpers for mapping model emotions to app labels and UI colors."""


def normalize_emotion(raw_label):
    """Map a raw emotion label to one of the app's supported emotions."""
    if raw_label == "happy":
        return "happy"
    if raw_label == "sad":
        return "sad"
    return "neutral"


def emotion_to_border_color(emotion):
    """Map an emotion label to a border color."""
    mapping = {
        "happy": "yellow",
        "sad": "blue",
        "neutral": "gray",
    }
    return mapping.get(emotion, "gray")
