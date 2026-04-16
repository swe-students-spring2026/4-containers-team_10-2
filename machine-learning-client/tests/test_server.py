"""Tests for the Flask server module."""

from unittest.mock import patch


def test_health_endpoint(client):
    """GET /health returns 200 and status ok."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


@patch("app.server.ping_db")
def test_db_health_success(mock_ping, client):
    """GET /db-health returns 200 when DB is reachable."""
    mock_ping.return_value = True
    response = client.get("/db-health")
    assert response.status_code == 200
    body = response.get_json()
    assert body["status"] == "ok"
    assert body["database"] == "connected"
    mock_ping.assert_called_once()


@patch("app.server.ping_db")
def test_db_health_failure(mock_ping, client):
    """GET /db-health returns 500 when ping_db raises RuntimeError."""
    mock_ping.side_effect = RuntimeError("connection refused")
    response = client.get("/db-health")
    assert response.status_code == 500
    body = response.get_json()
    assert body["status"] == "error"
    assert "connection refused" in body["message"]


@patch("app.server.insert_prediction")
@patch("app.server.detect_emotion")
def test_analyze_with_payload(mock_detect, mock_insert, client):
    """POST /analyze returns prediction fields and stores the document."""
    mock_detect.return_value = {
        "face_detected": True,
        "raw_emotion": "happy",
        "emotion": "happy",
        "confidence": 0.95,
        "scores": {"happy": 0.95, "neutral": 0.04, "sad": 0.01},
        "border_color": "yellow",
    }
    mock_insert.return_value = "fake_mongo_id_123"

    response = client.post(
        "/analyze",
        json={"session_id": "sess-1", "image_b64": "abc=="},
    )

    assert response.status_code == 200
    body = response.get_json()
    assert body["status"] == "ok"
    assert body["inserted_id"] == "fake_mongo_id_123"
    assert body["emotion"] == "happy"
    assert body["confidence"] == 0.95
    assert body["border_color"] == "yellow"
    assert body["face_detected"] is True
    mock_detect.assert_called_once_with("abc==")
    mock_insert.assert_called_once()


def test_analyze_missing_image_returns_400(client):
    """POST /analyze without image_b64 returns 400."""
    response = client.post("/analyze", json={"session_id": "sess-1"})
    assert response.status_code == 400
    body = response.get_json()
    assert body["status"] == "error"
    assert "image_b64" in body["message"]


def test_analyze_empty_body_returns_400(client):
    """POST /analyze with no JSON body returns 400."""
    response = client.post("/analyze")
    assert response.status_code == 400
    assert response.get_json()["status"] == "error"


def test_analyze_invalid_json_returns_400(client):
    """POST /analyze with malformed JSON body returns 400 (silent=True)."""
    response = client.post(
        "/analyze",
        data="not-valid-json",
        content_type="application/json",
    )
    assert response.status_code == 400


@patch("app.server.insert_prediction")
@patch("app.server.detect_emotion")
def test_analyze_default_session_id(mock_detect, mock_insert, client):
    """POST /analyze uses 'default-session' when session_id not provided."""
    mock_detect.return_value = {
        "face_detected": True,
        "raw_emotion": "happy",
        "emotion": "happy",
        "confidence": 0.95,
        "scores": {"happy": 0.95, "neutral": 0.04, "sad": 0.01},
        "border_color": "yellow",
    }
    mock_insert.return_value = "id_xyz"

    response = client.post("/analyze", json={"image_b64": "xyz=="})

    assert response.status_code == 200
    inserted_doc = mock_insert.call_args[0][0]
    assert inserted_doc["session_id"] == "default-session"


@patch("app.server.insert_prediction")
@patch("app.server.detect_emotion")
def test_analyze_handles_db_error(mock_detect, mock_insert, client):
    """POST /analyze returns 500 when insert_prediction raises RuntimeError."""
    mock_detect.return_value = {
        "face_detected": True,
        "raw_emotion": "happy",
        "emotion": "happy",
        "confidence": 0.95,
        "scores": {"happy": 0.95, "neutral": 0.04, "sad": 0.01},
        "border_color": "yellow",
    }
    mock_insert.side_effect = RuntimeError("mongo down")

    response = client.post("/analyze", json={"image_b64": "abc=="})

    assert response.status_code == 500
    body = response.get_json()
    assert body["status"] == "error"
    assert "mongo down" in body["message"]
