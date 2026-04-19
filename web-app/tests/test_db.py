"""Tests for db helpers."""

from unittest.mock import MagicMock, patch

from app.db import (
    _serialize_record,
    add_favorite_style,
    create_user,
    find_user_by_email,
    find_user_by_id,
    find_user_by_username,
    get_face_shape_counts,
    get_favorite_styles,
    get_latest_prediction,
    get_recent_predictions,
    get_total_scans,
    get_user_preferences,
    ping_db,
    remove_favorite_style,
    update_user_preferences,
)


def test_serialize_record_none():
    """Serialize returns None for empty record."""
    assert _serialize_record(None) is None


def test_serialize_record_converts_ids():
    """Serialize converts ids to strings."""
    record = {"_id": 123, "user_id": 456}
    result = _serialize_record(record)

    assert result["_id"] == "123"
    assert result["user_id"] == "456"


@patch("app.db.get_users_collection")
def test_create_user(mock_get_users_collection):
    """Create user inserts document."""
    mock_collection = MagicMock()
    mock_collection.insert_one.return_value.inserted_id = "abc123"
    mock_get_users_collection.return_value = mock_collection

    result = create_user({"username": "testuser"})

    assert result == "abc123"
    mock_collection.insert_one.assert_called_once()


@patch("app.db.get_users_collection")
def test_find_user_by_email(mock_get_users_collection):
    """Find user by email queries correctly."""
    mock_collection = MagicMock()
    mock_collection.find_one.return_value = {"email": "test@example.com"}
    mock_get_users_collection.return_value = mock_collection

    result = find_user_by_email("test@example.com")

    assert result["email"] == "test@example.com"
    mock_collection.find_one.assert_called_once_with({"email": "test@example.com"})


@patch("app.db.get_users_collection")
def test_find_user_by_username(mock_get_users_collection):
    """Find user by username queries correctly."""
    mock_collection = MagicMock()
    mock_collection.find_one.return_value = {"username": "testuser"}
    mock_get_users_collection.return_value = mock_collection

    result = find_user_by_username("testuser")

    assert result["username"] == "testuser"
    mock_collection.find_one.assert_called_once_with({"username": "testuser"})


@patch("app.db.get_users_collection")
def test_find_user_by_id_invalid(mock_get_users_collection):
    """Invalid id returns None."""
    result = find_user_by_id("not-a-valid-objectid")

    assert result is None
    mock_get_users_collection.assert_called_once()


@patch("app.db.get_collection")
def test_get_recent_predictions(mock_get_collection):
    """Recent predictions are serialized."""
    mock_collection = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.sort.return_value.limit.return_value = [
        {"_id": 1, "user_id": 2, "face_shape": "Oval"}
    ]
    mock_collection.find.return_value = mock_cursor
    mock_get_collection.return_value = mock_collection

    result = get_recent_predictions("10", limit=5)

    assert result[0]["_id"] == "1"
    assert result[0]["user_id"] == "2"


@patch("app.db.get_collection")
def test_get_latest_prediction(mock_get_collection):
    """Latest prediction is serialized."""
    mock_collection = MagicMock()
    mock_collection.find_one.return_value = {
        "_id": 1,
        "user_id": 2,
        "face_shape": "Round",
    }
    mock_get_collection.return_value = mock_collection

    result = get_latest_prediction("10")

    assert result["_id"] == "1"
    assert result["face_shape"] == "Round"


@patch("app.db.get_collection")
def test_get_face_shape_counts(mock_get_collection):
    """Face shape counts are aggregated."""
    mock_collection = MagicMock()
    mock_collection.aggregate.return_value = [
        {"_id": "Oval", "count": 3},
        {"_id": "Round", "count": 2},
    ]
    mock_get_collection.return_value = mock_collection

    result = get_face_shape_counts("10")

    assert result == {"Oval": 3, "Round": 2}


@patch("app.db.get_collection")
def test_get_total_scans(mock_get_collection):
    """Total scan count is returned."""
    mock_collection = MagicMock()
    mock_collection.count_documents.return_value = 5
    mock_get_collection.return_value = mock_collection

    result = get_total_scans("10")

    assert result == 5
    mock_collection.count_documents.assert_called_once_with({"user_id": "10"})


@patch("app.db.find_user_by_id")
def test_get_user_preferences_default(mock_find_user_by_id):
    """Default preferences are returned when user missing."""
    mock_find_user_by_id.return_value = None

    result = get_user_preferences("10")

    assert result == {
        "hair_length": "any",
        "hair_texture": "any",
        "maintenance_level": "any",
    }


@patch("app.db.find_user_by_id")
def test_get_user_preferences_existing(mock_find_user_by_id):
    """Existing preferences are returned."""
    mock_find_user_by_id.return_value = {
        "preferences": {
            "hair_length": "short",
            "hair_texture": "wavy",
            "maintenance_level": "low",
        }
    }

    result = get_user_preferences("10")

    assert result["hair_length"] == "short"
    assert result["hair_texture"] == "wavy"
    assert result["maintenance_level"] == "low"


@patch("app.db.get_users_collection")
def test_update_user_preferences(mock_get_users_collection):
    """Preferences update calls Mongo."""
    mock_collection = MagicMock()
    mock_get_users_collection.return_value = mock_collection

    update_user_preferences(
        "507f1f77bcf86cd799439011",
        {"hair_length": "medium"},
    )

    mock_collection.update_one.assert_called_once()


@patch("app.db.find_user_by_id")
def test_get_favorite_styles_default(mock_find_user_by_id):
    """Missing user returns empty favorites."""
    mock_find_user_by_id.return_value = None

    assert get_favorite_styles("10") == []


@patch("app.db.find_user_by_id")
def test_get_favorite_styles_existing(mock_find_user_by_id):
    """Favorites are returned."""
    mock_find_user_by_id.return_value = {
        "favorite_styles": [{"name": "Pompadour", "category": "male"}]
    }

    result = get_favorite_styles("10")

    assert result == [{"name": "Pompadour", "category": "male"}]


@patch("app.db.get_users_collection")
def test_add_favorite_style(mock_get_users_collection):
    """Favorite add uses addToSet."""
    mock_collection = MagicMock()
    mock_get_users_collection.return_value = mock_collection

    add_favorite_style("507f1f77bcf86cd799439011", {"name": "Pompadour"})

    mock_collection.update_one.assert_called_once()


@patch("app.db.get_users_collection")
def test_remove_favorite_style(mock_get_users_collection):
    """Favorite remove uses pull."""
    mock_collection = MagicMock()
    mock_get_users_collection.return_value = mock_collection

    remove_favorite_style("507f1f77bcf86cd799439011", "Pompadour", "male")

    mock_collection.update_one.assert_called_once()


@patch("app.db.get_client")
def test_ping_db(mock_get_client):
    """Ping db returns true."""
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client

    assert ping_db() is True
    mock_client.admin.command.assert_called_once_with("ping")
