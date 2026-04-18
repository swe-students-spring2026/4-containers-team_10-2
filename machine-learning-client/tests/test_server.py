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
@patch("app.server.detect_face_shape")
@patch("app.server.decode_base64_image")
def test_analyze_with_payload(mock_decode, mock_detect, mock_insert, client):
    """POST /analyze returns face-shape fields and stores the document."""
    mock_decode.return_value = "decoded-image"
    mock_detect.return_value = {
        "face_detected": True,
        "face_shape": "Oval",
        "confidence": 0.95,
        "recommended_hairstyles": [
            "Textured quiff",
            "Classic side part",
            "Layered medium cut",
        ],
    }
    mock_insert.return_value = "fake_mongo_id_123"

    response = client.post(
        "/analyze",
        json={
            "session_id": "sess-1",
            "user_id": "user-123",
            "image_b64": "abc==",
        },
    )

    assert response.status_code == 200
    body = response.get_json()
    assert body["status"] == "ok"
    assert body["inserted_id"] == "fake_mongo_id_123"
    assert body["face_shape"] == "Oval"
    assert body["confidence"] == 0.95
    assert body["face_detected"] is True
    assert body["recommended_hairstyles"] == [
        "Textured quiff",
        "Classic side part",
        "Layered medium cut",
    ]
    mock_decode.assert_called_once_with("abc==")
    mock_detect.assert_called_once_with("decoded-image")
    mock_insert.assert_called_once()


def test_analyze_missing_image_returns_400(client):
    """POST /analyze without image_b64 returns 400."""
    response = client.post(
        "/analyze",
        json={"session_id": "sess-1", "user_id": "user-123"},
    )
    assert response.status_code == 400
    body = response.get_json()
    assert body["status"] == "error"
    assert "image_b64" in body["message"]


def test_analyze_missing_user_id_returns_400(client):
    """POST /analyze without user_id returns 400."""
    response = client.post(
        "/analyze",
        json={"session_id": "sess-1", "image_b64": "abc=="},
    )
    assert response.status_code == 400
    body = response.get_json()
    assert body["status"] == "error"
    assert "user_id" in body["message"]


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
@patch("app.server.detect_face_shape")
@patch("app.server.decode_base64_image")
def test_analyze_default_session_id(mock_decode, mock_detect, mock_insert, client):
    """POST /analyze uses 'default-session' when session_id not provided."""
    mock_decode.return_value = "decoded-image"
    mock_detect.return_value = {
        "face_detected": True,
        "face_shape": "Oval",
        "confidence": 0.95,
        "recommended_hairstyles": [
            "Textured quiff",
            "Classic side part",
            "Layered medium cut",
        ],
    }
    mock_insert.return_value = "id_xyz"

    response = client.post(
        "/analyze",
        json={
            "user_id": "user-123",
            "image_b64": "xyz==",
        },
    )

    assert response.status_code == 200
    inserted_doc = mock_insert.call_args[0][0]
    assert inserted_doc["session_id"] == "default-session"
    assert inserted_doc["user_id"] == "user-123"


@patch("app.server.insert_prediction")
@patch("app.server.detect_face_shape")
@patch("app.server.decode_base64_image")
def test_analyze_handles_db_error(mock_decode, mock_detect, mock_insert, client):
    """POST /analyze returns 500 when insert_prediction raises RuntimeError."""
    mock_decode.return_value = "decoded-image"
    mock_detect.return_value = {
        "face_detected": True,
        "face_shape": "Oval",
        "confidence": 0.95,
        "recommended_hairstyles": [
            "Textured quiff",
            "Classic side part",
            "Layered medium cut",
        ],
    }
    mock_insert.side_effect = RuntimeError("mongo down")

    response = client.post(
        "/analyze",
        json={
            "user_id": "user-123",
            "image_b64": "abc==",
        },
    )

    assert response.status_code == 500
    body = response.get_json()
    assert body["status"] == "error"
    assert "mongo down" in body["message"]
