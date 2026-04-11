# placeholder for now

def normalize_emotion(raw_label):
    if raw_label == "happy":
        return "happy"
    if raw_label == "sad":
        return "sad"
    return "neutral"

def emotion_to_border_color(emotion):
    mapping = {
        "happy": "yellow",
        "sad": "blue",
        "neutral": "gray",
    }
    return mapping.get(emotion, "gray")