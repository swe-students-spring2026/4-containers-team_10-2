"""Database helper tests for the web application."""

from unittest.mock import MagicMock, patch

from app.db import (
    _serialize_record,
    create_user,
    find_user_by_email,
    find_user_by_id,
    find_user_by_username,
    get_client,
    get_collection,
    get_emotion_counts,
    get_latest_prediction,
    get_recent_predictions,
    get_users_collection,
    ping_db,
)


def test_get_client():
    """Test that a MongoClient is created."""
    with patch("app.db.MongoClient") as mock_client:
        get_client()
        mock_client.assert_called_once()


def test_get_collection():
    """Test that the configured predictions collection is returned."""
    mock_collection = MagicMock()
    mock_db = MagicMock()
    mock_db.__getitem__.return_value = mock_collection
    mock_client = MagicMock()
    mock_client.__getitem__.return_value = mock_db

    with patch("app.db.get_client", return_value=mock_client):
        collection = get_collection()

    assert collection == mock_collection


def test_get_users_collection():
    """Test that the configured users collection is returned."""
    mock_collection = MagicMock()
    mock_db = MagicMock()
    mock_db.__getitem__.return_value = mock_collection
    mock_client = MagicMock()
    mock_client.__getitem__.return_value = mock_db

    with patch("app.db.get_client", return_value=mock_client):
        collection = get_users_collection()

    assert collection == mock_collection


def test_ping_db():
    """Test that the database ping command is executed."""
    mock_client = MagicMock()

    with patch("app.db.get_client", return_value=mock_client):
        result = ping_db()

    mock_client.admin.command.assert_called_once_with("ping")
    assert result is True


def test_serialize_record_none():
    """Test that serializing None returns None."""
    assert _serialize_record(None) is None


def test_serialize_record_converts_id_and_user_id_to_string():
    """Test that record identifiers are converted to strings."""
    record = {"_id": 123, "user_id": 456, "emotion": "happy"}
    result = _serialize_record(record)

    assert result["_id"] == "123"
    assert result["user_id"] == "456"
    assert result["emotion"] == "happy"


def test_create_user():
    """Test inserting a new user document."""
    mock_collection = MagicMock()
    mock_collection.insert_one.return_value.inserted_id = "abc123"

    with patch("app.db.get_users_collection", return_value=mock_collection):
        inserted_id = create_user({"email": "test@example.com"})

    assert inserted_id == "abc123"
    mock_collection.insert_one.assert_called_once()


def test_find_user_by_email():
    """Test finding a user by email."""
    mock_collection = MagicMock()
    mock_collection.find_one.return_value = {"email": "test@example.com"}

    with patch("app.db.get_users_collection", return_value=mock_collection):
        result = find_user_by_email("test@example.com")

    assert result["email"] == "test@example.com"
    mock_collection.find_one.assert_called_once_with({"email": "test@example.com"})


def test_find_user_by_username():
    """Test finding a user by username."""
    mock_collection = MagicMock()
    mock_collection.find_one.return_value = {"username": "testuser"}

    with patch("app.db.get_users_collection", return_value=mock_collection):
        result = find_user_by_username("testuser")

    assert result["username"] == "testuser"
    mock_collection.find_one.assert_called_once_with({"username": "testuser"})


def test_find_user_by_id_success():
    """Test finding a user by id."""
    mock_collection = MagicMock()
    mock_collection.find_one.return_value = {"username": "testuser"}

    with patch("app.db.get_users_collection", return_value=mock_collection):
        result = find_user_by_id("507f1f77bcf86cd799439011")

    assert result["username"] == "testuser"
    mock_collection.find_one.assert_called_once()


def test_find_user_by_id_invalid_object_id():
    """Test that invalid ids return None."""
    with patch("app.db.get_users_collection"):
        result = find_user_by_id("not-a-real-object-id")

    assert result is None


def test_get_recent_predictions():
    """Test fetching recent prediction records for a user."""
    mock_cursor = MagicMock()
    mock_cursor.limit.return_value = [
        {"_id": 1, "user_id": 10, "emotion": "happy"},
        {"_id": 2, "user_id": 10, "emotion": "sad"},
    ]

    mock_collection = MagicMock()
    mock_collection.find.return_value.sort.return_value = mock_cursor

    with patch("app.db.get_collection", return_value=mock_collection):
        result = get_recent_predictions(user_id="10", limit=2)

    assert len(result) == 2
    assert result[0]["_id"] == "1"
    assert result[1]["_id"] == "2"
    mock_collection.find.assert_called_once_with({"user_id": "10"})
    mock_collection.find.return_value.sort.assert_called_once_with("timestamp", -1)
    mock_cursor.limit.assert_called_once_with(2)


def test_get_latest_prediction_with_record():
    """Test fetching the latest prediction for a user when one exists."""
    mock_collection = MagicMock()
    mock_collection.find_one.return_value = {
        "_id": 7,
        "user_id": 10,
        "emotion": "neutral",
    }

    with patch("app.db.get_collection", return_value=mock_collection):
        result = get_latest_prediction(user_id="10")

    assert result["_id"] == "7"
    assert result["emotion"] == "neutral"
    mock_collection.find_one.assert_called_once_with(
        {"user_id": "10"},
        sort=[("timestamp", -1)],
    )


def test_get_latest_prediction_without_record():
    """Test fetching the latest prediction when none exists."""
    mock_collection = MagicMock()
    mock_collection.find_one.return_value = None

    with patch("app.db.get_collection", return_value=mock_collection):
        result = get_latest_prediction(user_id="10")

    assert result is None


def test_get_emotion_counts_with_results():
    """Test aggregation of known emotion counts for a user."""
    mock_collection = MagicMock()
    mock_collection.aggregate.return_value = [
        {"_id": "happy", "count": 4},
        {"_id": "sad", "count": 2},
        {"_id": "neutral", "count": 3},
    ]

    with patch("app.db.get_collection", return_value=mock_collection):
        result = get_emotion_counts(user_id="10")

    assert result == {
        "happy": 4,
        "sad": 2,
        "neutral": 3,
    }


def test_get_emotion_counts_ignores_unknown_emotions():
    """Test that unknown emotions are ignored in aggregation."""
    mock_collection = MagicMock()
    mock_collection.aggregate.return_value = [
        {"_id": "happy", "count": 1},
        {"_id": "angry", "count": 9},
    ]

    with patch("app.db.get_collection", return_value=mock_collection):
        result = get_emotion_counts(user_id="10")

    assert result == {
        "happy": 1,
        "sad": 0,
        "neutral": 0,
    }
