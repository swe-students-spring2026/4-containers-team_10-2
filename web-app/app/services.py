"""Service layer for communicating with the ML client and shaping dashboard data."""

import requests

from app.db import get_emotion_counts, get_latest_prediction, get_recent_predictions


def submit_frame_for_analysis(ml_client_url, image_b64, session_id, user_id):
    """Send a frame to the ML client for emotion analysis."""
    response = requests.post(
        f"{ml_client_url}/analyze",
        json={
            "session_id": session_id,
            "user_id": user_id,
            "image_b64": image_b64,
        },
        timeout=15,
    )
    response.raise_for_status()
    return response.json()


def fetch_dashboard_summary(user_id):
    """Return summary data for the dashboard."""
    latest = get_latest_prediction(user_id=user_id)
    counts = get_emotion_counts(user_id=user_id)
    recent = get_recent_predictions(user_id=user_id, limit=10)

    total_predictions = sum(counts.values())

    return {
        "latest": latest,
        "counts": counts,
        "recent": recent,
        "total_predictions": total_predictions,
    }
