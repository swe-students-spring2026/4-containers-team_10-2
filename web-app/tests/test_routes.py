"""Tests for main routes."""

# pylint: disable=too-many-arguments,too-many-positional-arguments,unused-argument

from unittest.mock import patch


def test_index_requires_login(client):
    """Index redirects when logged out."""
    response = client.get("/")

    assert response.status_code in {301, 302}


@patch("app.routes.get_favorite_styles", return_value=[])
@patch(
    "app.routes.get_user_preferences",
    return_value={
        "hair_length": "any",
        "hair_texture": "any",
        "maintenance_level": "any",
    },
)
def test_index_logged_in(mock_preferences, mock_favorites, logged_in_client):
    """Index renders when logged in."""
    response = logged_in_client.get("/")

    assert response.status_code == 200


@patch("app.routes.fetch_dashboard_summary")
def test_dashboard(mock_fetch_dashboard_summary, logged_in_client):
    """Dashboard renders summary."""
    mock_fetch_dashboard_summary.return_value = {
        "latest": {
            "face_shape": "Oval",
            "confidence": 0.91,
            "recommended_hairstyles": {"male": [], "female": []},
        },
        "counts": {"Oval": 4},
        "recent": [
            {
                "face_shape": "Oval",
                "confidence": 0.91,
                "recommended_hairstyles": {"male": [], "female": []},
            }
        ],
        "total_scans": 4,
        "preferences": {
            "hair_length": "any",
            "hair_texture": "any",
            "maintenance_level": "any",
        },
        "favorites": [],
    }

    response = logged_in_client.get("/dashboard")

    assert response.status_code == 200
    assert b"Oval" in response.data


@patch("app.routes.get_favorite_styles", return_value=[])
@patch(
    "app.routes.get_user_preferences",
    return_value={
        "hair_length": "any",
        "hair_texture": "any",
        "maintenance_level": "any",
    },
)
@patch(
    "app.routes.get_recent_predictions",
    return_value=[
        {
            "face_shape": "Round",
            "confidence": 0.82,
            "recommended_hairstyles": {"male": [], "female": []},
        }
    ],
)
def test_history(mock_recent, mock_preferences, mock_favorites, logged_in_client):
    """History renders."""
    response = logged_in_client.get("/history")

    assert response.status_code == 200
    assert b"Round" in response.data


def test_health(client):
    """Health endpoint works."""
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json == {"status": "ok"}


@patch("app.routes.ping_db", return_value=True)
def test_db_health_ok(mock_ping_db, client):
    """Db health succeeds."""
    response = client.get("/db-health")

    assert response.status_code == 200
    assert response.json["status"] == "ok"
    mock_ping_db.assert_called_once()


@patch("app.routes.ping_db", side_effect=RuntimeError("db down"))
def test_db_health_error(mock_ping_db, client):
    """Db health handles failure."""
    response = client.get("/db-health")

    assert response.status_code == 500
    assert response.json["status"] == "error"
    mock_ping_db.assert_called_once()


def test_analyze_missing_image(logged_in_client):
    """Analyze rejects missing frame."""
    response = logged_in_client.post("/api/analyze", json={})

    assert response.status_code == 400
    assert response.json["status"] == "error"


@patch("app.routes.annotate_favorites")
@patch("app.routes.apply_preferences_to_recommendations")
@patch("app.routes.get_favorite_styles")
@patch("app.routes.get_user_preferences")
@patch("app.routes.submit_frame_for_analysis")
def test_analyze_success(
    mock_submit_frame_for_analysis,
    mock_get_user_preferences,
    mock_get_favorite_styles,
    mock_apply_preferences,
    mock_annotate_favorites,
    logged_in_client,
    test_user,
):
    """Analyze returns filtered and annotated recommendations."""
    raw_result = {
        "status": "ok",
        "face_detected": True,
        "face_shape": "Oval",
        "confidence": 0.95,
        "recommended_hairstyles": {"male": [], "female": []},
    }
    filtered = {"male": [{"name": "Pompadour"}], "female": []}
    annotated = {"male": [{"name": "Pompadour", "favorited": True}], "female": []}

    mock_submit_frame_for_analysis.return_value = raw_result
    mock_get_user_preferences.return_value = {
        "hair_length": "short",
        "hair_texture": "straight",
        "maintenance_level": "low",
    }
    mock_get_favorite_styles.return_value = [{"name": "Pompadour", "category": "male"}]
    mock_apply_preferences.return_value = filtered
    mock_annotate_favorites.return_value = annotated

    response = logged_in_client.post(
        "/api/analyze",
        json={"session_id": "abc", "image_b64": "fake-image"},
    )

    assert response.status_code == 200
    assert response.json["face_shape"] == "Oval"
    mock_submit_frame_for_analysis.assert_called_once_with(
        "http://localhost:5001",
        "fake-image",
        "abc",
        test_user.id,
    )
    mock_apply_preferences.assert_called_once()
    mock_annotate_favorites.assert_called_once()


@patch("app.routes.get_recent_predictions", return_value=[{"face_shape": "Oval"}])
def test_api_history(mock_recent, logged_in_client, test_user):
    """Api history returns recent records."""
    response = logged_in_client.get("/api/history?limit=5")

    assert response.status_code == 200
    assert response.json["status"] == "ok"
    mock_recent.assert_called_once_with(user_id=test_user.id, limit=5)


@patch("app.routes.get_latest_prediction", return_value={"face_shape": "Oval"})
def test_api_latest(mock_latest, logged_in_client, test_user):
    """Api latest returns latest record."""
    response = logged_in_client.get("/api/latest")

    assert response.status_code == 200
    assert response.json["status"] == "ok"
    assert response.json["latest"]["face_shape"] == "Oval"
    mock_latest.assert_called_once_with(user_id=test_user.id)


@patch("app.routes.update_user_preferences")
def test_save_preferences(mock_update_user_preferences, logged_in_client, test_user):
    """Preferences save route updates db."""
    response = logged_in_client.post(
        "/api/preferences",
        json={
            "hair_length": "medium",
            "hair_texture": "curly",
            "maintenance_level": "high",
        },
    )

    assert response.status_code == 200
    assert response.json["status"] == "ok"
    mock_update_user_preferences.assert_called_once_with(
        test_user.id,
        {
            "hair_length": "medium",
            "hair_texture": "curly",
            "maintenance_level": "high",
        },
    )


def test_update_favorites_missing_fields(logged_in_client):
    """Favorites route validates input."""
    response = logged_in_client.post("/api/favorites", json={"action": "add"})

    assert response.status_code == 400
    assert response.json["status"] == "error"


@patch("app.routes.add_favorite_style")
def test_update_favorites_add(mock_add_favorite_style, logged_in_client, test_user):
    """Favorites add route saves favorite."""
    response = logged_in_client.post(
        "/api/favorites",
        json={
            "action": "add",
            "name": "Pompadour",
            "category": "male",
            "face_shape": "Oval",
            "barber_notes": "notes",
        },
    )

    assert response.status_code == 200
    assert response.json["status"] == "ok"
    mock_add_favorite_style.assert_called_once_with(
        test_user.id,
        {
            "name": "Pompadour",
            "category": "male",
            "face_shape": "Oval",
            "barber_notes": "notes",
        },
    )


@patch("app.routes.remove_favorite_style")
def test_update_favorites_remove(
    mock_remove_favorite_style,
    logged_in_client,
    test_user,
):
    """Favorites remove route removes favorite."""
    response = logged_in_client.post(
        "/api/favorites",
        json={
            "action": "remove",
            "name": "Pompadour",
            "category": "male",
        },
    )

    assert response.status_code == 200
    assert response.json["status"] == "ok"
    mock_remove_favorite_style.assert_called_once_with(
        test_user.id,
        "Pompadour",
        "male",
    )
