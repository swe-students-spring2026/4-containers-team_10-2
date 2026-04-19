"""Tests for server routes."""

from unittest.mock import patch


def test_health(client):
    """Health endpoint returns ok."""
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json == {"status": "ok"}


@patch("app.server.ping_db", return_value=True)
def test_db_health_ok(mock_ping_db, client):
    """DB health returns ok."""
    response = client.get("/db-health")

    assert response.status_code == 200
    assert response.json["status"] == "ok"
    assert response.json["database"] == "connected"
    mock_ping_db.assert_called_once()


@patch("app.server.ping_db", side_effect=RuntimeError("db down"))
def test_db_health_error(mock_ping_db, client):
    """DB health returns error on failure."""
    response = client.get("/db-health")

    assert response.status_code == 500
    assert response.json["status"] == "error"
    mock_ping_db.assert_called_once()


def test_analyze_missing_image(client):
    """Analyze rejects missing image."""
    response = client.post("/analyze", json={"user_id": "user-1"})

    assert response.status_code == 400
    assert response.json["status"] == "error"
    assert "Missing image_b64" in response.json["message"]


def test_analyze_missing_user_id(client):
    """Analyze rejects missing user id."""
    response = client.post("/analyze", json={"image_b64": "fake-image"})

    assert response.status_code == 400
    assert response.json["status"] == "error"
    assert "Missing user_id" in response.json["message"]


@patch("app.server.insert_prediction", return_value="abc123")
@patch("app.server.build_prediction_document")
@patch("app.server.detect_face_shape")
@patch("app.server.decode_base64_image")
def test_analyze_success(
    mock_decode,
    mock_detect,
    mock_build,
    mock_insert,
    client,
):
    """Analyze returns successful payload."""
    mock_decode.return_value = "decoded-image"
    mock_detect.return_value = {
        "face_detected": True,
        "face_shape": "Oval",
        "confidence": 0.91,
        "recommended_hairstyles": {"male": [], "female": []},
        "face_box": {"x": 1, "y": 2, "width": 3, "height": 4},
    }
    mock_build.return_value = {"document": "value"}

    response = client.post(
        "/analyze",
        json={
            "user_id": "user-1",
            "session_id": "session-1",
            "image_b64": "fake-image",
        },
    )

    assert response.status_code == 200
    assert response.json["status"] == "ok"
    assert response.json["inserted_id"] == "abc123"
    assert response.json["face_shape"] == "Oval"

    mock_decode.assert_called_once_with("fake-image")
    mock_detect.assert_called_once_with("decoded-image", session_id="session-1")
    mock_build.assert_called_once()
    mock_insert.assert_called_once_with({"document": "value"})


@patch("app.server.decode_base64_image", side_effect=RuntimeError("decode failed"))
def test_analyze_error(mock_decode, client):
    """Analyze wraps unexpected errors."""
    response = client.post(
        "/analyze",
        json={
            "user_id": "user-1",
            "session_id": "session-1",
            "image_b64": "fake-image",
        },
    )

    assert response.status_code == 500
    assert response.json["status"] == "error"
    assert "decode failed" in response.json["message"]
    mock_decode.assert_called_once()
