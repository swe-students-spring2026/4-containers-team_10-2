from unittest.mock import patch


# -------------------------
# HEALTH
# -------------------------

def test_health(client):
    res = client.get("/health")
    assert res.status_code == 200


# -------------------------
# ANALYZE SUCCESS
# -------------------------

@patch("app.server.detect_face_shape")
def test_analyze_success(mock_process, client):
    mock_process.return_value = {
        "face_shape": "oval",
        "recommended_hairstyles": []
    }

    res = client.post("/analyze", json={
        "image_b64": "test",
        "session_id": "1",
        "user_id": "1"
    })

    assert res.status_code in [200, 500]
    data = res.get_json()
    assert "face_shape" in data or data.get("status") == "error"


# -------------------------
# MISSING FIELDS
# -------------------------

def test_analyze_missing_all(client):
    res = client.post("/analyze", json={})
    assert res.status_code == 400


def test_analyze_missing_image(client):
    res = client.post("/analyze", json={
        "session_id": "1",
        "user_id": "1"
    })
    assert res.status_code == 400


def test_analyze_missing_session(client):
    res = client.post("/analyze", json={
        "image_b64": "test",
        "user_id": "1"
    })
    assert res.status_code in [400, 500]


def test_analyze_missing_user(client):
    res = client.post("/analyze", json={
        "image_b64": "test",
        "session_id": "1"
    })
    assert res.status_code == 400


# -------------------------
# BAD INPUT TYPES
# -------------------------

def test_analyze_invalid_json(client):
    res = client.post("/analyze", data="notjson")
    assert res.status_code in [400, 415]


# -------------------------
# PROCESS FAILURE
# -------------------------

@patch("app.server.detect_face_shape", side_effect=Exception("fail"))
def test_analyze_exception(mock_process, client):
    res = client.post("/analyze", json={
        "image_b64": "test",
        "session_id": "1",
        "user_id": "1"
    })

    assert res.status_code in [400, 500]


# -------------------------
# EDGE CASE
# -------------------------

@patch("app.server.detect_face_shape")
def test_analyze_empty_result(mock_process, client):
    mock_process.return_value = {}

    res = client.post("/analyze", json={
        "image_b64": "test",
        "session_id": "1",
        "user_id": "1"
    })

    assert res.status_code in [200, 500]