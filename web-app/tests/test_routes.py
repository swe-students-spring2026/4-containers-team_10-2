def test_health(client):
    res = client.get("/health")
    assert res.status_code == 200


def test_db_health(client):
    res = client.get("/db-health")
    assert res.status_code == 200


def test_analyze_missing_image(client):
    res = client.post("/api/analyze", json={})
    assert res.status_code == 400


def test_analyze_success(client):
    res = client.post("/api/analyze", json={"image_b64": "test"})
    assert res.status_code == 200


def test_api_history(client):
    res = client.get("/api/history")
    assert res.status_code == 200


def test_api_latest(client):
    res = client.get("/api/latest")
    assert res.status_code == 200


def test_save_preferences(client):
    res = client.post("/api/preferences", json={"hair_length": "short"})
    assert res.status_code == 200


def test_favorites_missing(client):
    res = client.post("/api/favorites", json={})
    assert res.status_code == 400


def test_favorites_add(client):
    res = client.post("/api/favorites", json={
        "action": "add",
        "name": "fade",
        "category": "modern"
    })
    assert res.status_code == 200


def test_favorites_remove(client):
    res = client.post("/api/favorites", json={
        "action": "remove",
        "name": "fade",
        "category": "modern"
    })
    assert res.status_code == 200