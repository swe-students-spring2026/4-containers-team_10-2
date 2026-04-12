"""Schema definitions for prediction documents."""

from datetime import datetime, timezone


def build_prediction_document(session_id, result):
    """Build a prediction document for MongoDB storage."""
    return {
        "session_id": session_id,
        "source": "webcam",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "face_detected": result["face_detected"],
        "raw_emotion": result["raw_emotion"],
        "emotion": result["emotion"],
        "confidence": result["confidence"],
        "scores": result["scores"],
        "border_color": result["border_color"],
    }
