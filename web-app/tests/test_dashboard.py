"""Dashboard and history page tests for the web application."""

from unittest.mock import patch


def test_dashboard_route_renders_summary(client):
    """Test that the dashboard renders summary information."""
    summary = {
        "latest": {
            "_id": "1",
            "emotion": "happy",
            "confidence": 0.91,
            "timestamp": "2026-04-13T20:00:00Z",
            "face_detected": True,
        },
        "counts": {
            "happy": 4,
            "sad": 1,
            "neutral": 2,
        },
        "recent": [
            {
                "_id": "1",
                "timestamp": "2026-04-13T20:00:00Z",
                "emotion": "happy",
                "confidence": 0.91,
                "face_detected": True,
            }
        ],
        "total_predictions": 7,
    }

    with patch("app.routes.fetch_dashboard_summary", return_value=summary):
        response = client.get("/dashboard")

    assert response.status_code == 200
    assert b"Emotion Dashboard" in response.data
    assert b"Total Predictions" in response.data
    assert b"Happy" in response.data


def test_dashboard_route_with_no_latest(client):
    """Test that the dashboard handles empty summary data."""
    summary = {
        "latest": None,
        "counts": {
            "happy": 0,
            "sad": 0,
            "neutral": 0,
        },
        "recent": [],
        "total_predictions": 0,
    }

    with patch("app.routes.fetch_dashboard_summary", return_value=summary):
        response = client.get("/dashboard")

    assert response.status_code == 200
    assert b"No predictions available yet." in response.data


def test_history_route_renders_records(client):
    """Test that the history page renders stored records."""
    records = [
        {
            "_id": "1",
            "timestamp": "2026-04-13T20:00:00Z",
            "session_id": "abc",
            "emotion": "happy",
            "confidence": 0.95,
            "face_detected": True,
            "border_color": "yellow",
        },
        {
            "_id": "2",
            "timestamp": "2026-04-13T20:01:00Z",
            "session_id": "abc",
            "emotion": "sad",
            "confidence": 0.52,
            "face_detected": True,
            "border_color": "blue",
        },
    ]

    with patch("app.routes.get_recent_predictions", return_value=records):
        response = client.get("/history")

    assert response.status_code == 200
    assert b"Prediction History" in response.data
    assert b"yellow" in response.data
    assert b"blue" in response.data


def test_history_route_with_no_records(client):
    """Test that the history page handles an empty record list."""
    with patch("app.routes.get_recent_predictions", return_value=[]):
        response = client.get("/history")

    assert response.status_code == 200
    assert b"No records found yet." in response.data
