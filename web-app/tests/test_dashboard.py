"""Dashboard and history page tests for the web application."""

# pylint: disable=duplicate-code

from unittest.mock import patch


def test_dashboard_route_renders_summary(logged_in_client):
    """Test that the dashboard renders summary information."""
    summary = {
        "latest": {
            "_id": "1",
            "face_detected": True,
            "face_shape": "Oval",
            "confidence": 0.91,
            "recommended_hairstyles": [
                "Textured quiff",
                "Classic side part",
                "Layered medium cut",
            ],
            "timestamp": "2026-04-13T20:00:00Z",
        },
        "counts": {
            "Oval": 4,
            "Round": 1,
        },
        "recent": [
            {
                "_id": "1",
                "timestamp": "2026-04-13T20:00:00Z",
                "face_shape": "Oval",
                "confidence": 0.91,
                "face_detected": True,
            }
        ],
        "total_scans": 5,
    }

    with patch("app.routes.fetch_dashboard_summary", return_value=summary):
        response = logged_in_client.get("/dashboard")

    assert response.status_code == 200
    assert b"Hairstyle Recommendation Dashboard" in response.data
    assert b"Total Scans" in response.data
    assert b"Oval" in response.data


def test_dashboard_route_with_no_latest(logged_in_client):
    """Test that the dashboard handles empty summary data."""
    summary = {
        "latest": None,
        "counts": {},
        "recent": [],
        "total_scans": 0,
    }

    with patch("app.routes.fetch_dashboard_summary", return_value=summary):
        response = logged_in_client.get("/dashboard")

    assert response.status_code == 200
    assert b"No scans available yet." in response.data


def test_history_route_renders_records(logged_in_client):
    """Test that the history page renders stored records."""
    records = [
        {
            "_id": "1",
            "timestamp": "2026-04-13T20:00:00Z",
            "session_id": "abc",
            "user_id": "507f1f77bcf86cd799439011",
            "face_detected": True,
            "face_shape": "Oval",
            "confidence": 0.95,
            "recommended_hairstyles": [
                "Textured quiff",
                "Classic side part",
                "Layered medium cut",
            ],
        },
        {
            "_id": "2",
            "timestamp": "2026-04-13T20:01:00Z",
            "session_id": "abc",
            "user_id": "507f1f77bcf86cd799439011",
            "face_detected": True,
            "face_shape": "Round",
            "confidence": 0.52,
            "recommended_hairstyles": [
                "Pompadour",
                "Angular fringe",
                "High fade with volume",
            ],
        },
    ]

    with patch("app.routes.get_recent_predictions", return_value=records):
        response = logged_in_client.get("/history")

    assert response.status_code == 200
    assert b"Scan History" in response.data
    assert b"Textured quiff" in response.data
    assert b"Pompadour" in response.data


def test_history_route_with_no_records(logged_in_client):
    """Test that the history page handles an empty record list."""
    with patch("app.routes.get_recent_predictions", return_value=[]):
        response = logged_in_client.get("/history")

    assert response.status_code == 200
    assert b"No scans found yet." in response.data
