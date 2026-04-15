"""Route tests for the web application."""

# pylint: disable=duplicate-code

from unittest.mock import patch

import requests


def test_index_route_requires_login(client):
    """Test that the index route redirects anonymous users to login."""
    response = client.get("/")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_index_route_logged_in(logged_in_client):
    """Test that the index route renders for authenticated users."""
    response = logged_in_client.get("/")
    assert response.status_code == 200
    assert b"MoodMirror" in response.data
    assert b"Live Emotion Camera" in response.data


def test_dashboard_route_requires_login(client):
    """Test that the dashboard route redirects anonymous users."""
    response = client.get("/dashboard")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_dashboard_route_logged_in(logged_in_client, test_user):
    """Test that the dashboard renders for authenticated users."""
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

    with patch(
        "app.routes.fetch_dashboard_summary", return_value=summary
    ) as mock_summary:
        response = logged_in_client.get("/dashboard")

    assert response.status_code == 200
    assert b"Emotion Dashboard" in response.data
    mock_summary.assert_called_once_with(test_user.id)


def test_history_route_logged_in(logged_in_client, test_user):
    """Test that the history page renders only the current user's records."""
    records = [
        {
            "_id": "1",
            "timestamp": "2026-04-13T20:00:00Z",
            "session_id": "abc",
            "user_id": test_user.id,
            "emotion": "happy",
            "confidence": 0.95,
            "face_detected": True,
            "border_color": "yellow",
        }
    ]

    with patch(
        "app.routes.get_recent_predictions", return_value=records
    ) as mock_recent:
        response = logged_in_client.get("/history")

    assert response.status_code == 200
    assert b"Prediction History" in response.data
    mock_recent.assert_called_once_with(user_id=test_user.id, limit=50)


def test_health_route(client):
    """Test that the health route returns ok."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json == {"status": "ok"}


def test_db_health_route_success(client):
    """Test that the database health route reports success."""
    with patch("app.routes.ping_db", return_value=True):
        response = client.get("/db-health")

    assert response.status_code == 200
    assert response.json["status"] == "ok"
    assert response.json["database"] == "connected"


def test_db_health_route_failure(client):
    """Test that the database health route reports failure."""
    with patch("app.routes.ping_db", side_effect=RuntimeError("db down")):
        response = client.get("/db-health")

    assert response.status_code == 500
    assert response.json["status"] == "error"
    assert "db down" in response.json["message"]


def test_analyze_route_requires_login(client):
    """Test that analyze redirects anonymous users to login."""
    response = client.post("/api/analyze", json={"image_b64": "x"})
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_analyze_route_missing_image(logged_in_client):
    """Test that analyze returns an error when image data is missing."""
    response = logged_in_client.post("/api/analyze", json={"session_id": "abc"})
    assert response.status_code == 400
    assert response.json["status"] == "error"


def test_analyze_route_success(logged_in_client, test_user):
    """Test that analyze returns a successful ML response and forwards user_id."""
    with patch(
        "app.routes.submit_frame_for_analysis",
        return_value={
            "status": "ok",
            "emotion": "happy",
            "confidence": 0.95,
            "border_color": "yellow",
            "face_detected": True,
            "inserted_id": "123",
        },
    ) as mock_submit:
        response = logged_in_client.post(
            "/api/analyze",
            json={
                "session_id": "abc",
                "image_b64": "fake-image-data",
            },
        )

    assert response.status_code == 200
    assert response.json["status"] == "ok"
    assert response.json["emotion"] == "happy"
    mock_submit.assert_called_once_with(
        "http://localhost:5001",
        "fake-image-data",
        "abc",
        test_user.id,
    )


def test_analyze_route_ml_client_request_exception(logged_in_client):
    """Test that analyze returns a 502 when the ML client request fails."""
    with patch(
        "app.routes.submit_frame_for_analysis",
        side_effect=requests.RequestException("ml offline"),
    ):
        response = logged_in_client.post(
            "/api/analyze",
            json={
                "session_id": "abc",
                "image_b64": "fake-image-data",
            },
        )

    assert response.status_code == 502
    assert response.json["status"] == "error"
    assert "ml offline" in response.json["message"]


def test_analyze_route_unexpected_exception(logged_in_client):
    """Test that analyze returns a 500 on unexpected exceptions."""
    with patch(
        "app.routes.submit_frame_for_analysis",
        side_effect=RuntimeError("unexpected"),
    ):
        response = logged_in_client.post(
            "/api/analyze",
            json={
                "session_id": "abc",
                "image_b64": "fake-image-data",
            },
        )

    assert response.status_code == 500
    assert response.json["status"] == "error"
    assert "unexpected" in response.json["message"]


def test_api_history_route_requires_login(client):
    """Test that the history API requires authentication."""
    response = client.get("/api/history")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_api_history_route(logged_in_client, test_user):
    """Test that the history API returns only the current user's records."""
    fake_records = [
        {"_id": "1", "emotion": "happy"},
        {"_id": "2", "emotion": "sad"},
    ]

    with patch(
        "app.routes.get_recent_predictions", return_value=fake_records
    ) as mock_recent:
        response = logged_in_client.get("/api/history?limit=2")

    assert response.status_code == 200
    assert response.json["status"] == "ok"
    assert len(response.json["records"]) == 2
    mock_recent.assert_called_once_with(user_id=test_user.id, limit=2)


def test_api_latest_route_requires_login(client):
    """Test that the latest API requires authentication."""
    response = client.get("/api/latest")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_api_latest_route(logged_in_client, test_user):
    """Test that the latest API returns the current user's latest record."""
    latest = {"_id": "1", "emotion": "neutral"}

    with patch("app.routes.get_latest_prediction", return_value=latest) as mock_latest:
        response = logged_in_client.get("/api/latest")

    assert response.status_code == 200
    assert response.json["status"] == "ok"
    assert response.json["latest"] == latest
    mock_latest.assert_called_once_with(user_id=test_user.id)
