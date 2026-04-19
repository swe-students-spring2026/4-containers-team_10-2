"""Schema helpers for MongoDB documents."""

# pylint: disable=duplicate-code

from datetime import datetime, timezone


def build_prediction_document(user_id, session_id, result):
    """Build a MongoDB document for a face-shape scan."""
    return {
        "user_id": user_id,
        "session_id": session_id,
        "source": "webcam",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "face_detected": result["face_detected"],
        "face_shape": result["face_shape"],
        "confidence": result["confidence"],
        "recommended_hairstyles": result["recommended_hairstyles"],
        "face_box": result.get("face_box"),
    }
