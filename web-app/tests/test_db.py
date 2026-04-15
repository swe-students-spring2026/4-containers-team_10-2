"""Database helper tests for the web application."""

from unittest.mock import MagicMock, patch

from app.db import (
    _serialize_record,
    get_client,
    get_collection,
    get_emotion_counts,
    get_latest_prediction,
    get_recent_predictions,
    ping_db,
)


def test_get_client():
    """Test that a MongoClient is created."""
    with patch("app.db.MongoClient") as mock_client:
        get_client()
        mock_client.assert_called_once()


def test_get_collection():
    """Test that the configured Mongo collection is returned."""
    mock_collection = MagicMock()
    mock_db = MagicMock()
    mock_db.__getitem__.return_value = mock_collection
    mock_client = MagicMock()
    mock_client.__getitem__.return_value = mock_db

    with patch("app.db.get_client", return_value=mock_client):
        collection = get_collection()

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


def test_serialize_record_converts_id_to_string():
    """Test that a record _id is converted to a string."""
    record = {"_id": 123, "emotion": "happy"}
    result = _serialize_record(record)

    assert result["_id"] == "123"
    assert result["emotion"] == "happy"


def test_get_recent_predictions():
    """Test fetching recent prediction records."""
    mock_cursor = MagicMock()
    mock_cursor.limit.return_value = [
        {"_id": 1, "emotion": "happy"},
        {"_id": 2, "emotion": "sad"},
    ]

    mock_collection = MagicMock()
    mock_collection.find.return_value.sort.return_value = mock_cursor

    with patch("app.db.get_collection", return_value=mock_collection):
        result = get_recent_predictions(limit=2)

    assert len(result) == 2
    assert result[0]["_id"] == "1"
    assert result[1]["_id"] == "2"
    mock_collection.find.return_value.sort.assert_called_once_with("timestamp", -1)
    mock_cursor.limit.assert_called_once_with(2)


def test_get_latest_prediction_with_record():
    """Test fetching the latest prediction when one exists."""
    mock_collection = MagicMock()
    mock_collection.find_one.return_value = {"_id": 7, "emotion": "neutral"}

    with patch("app.db.get_collection", return_value=mock_collection):
        result = get_latest_prediction()

    assert result["_id"] == "7"
    assert result["emotion"] == "neutral"
    mock_collection.find_one.assert_called_once_with(sort=[("timestamp", -1)])


def test_get_latest_prediction_without_record():
    """Test fetching the latest prediction when none exists."""
    mock_collection = MagicMock()
    mock_collection.find_one.return_value = None

    with patch("app.db.get_collection", return_value=mock_collection):
        result = get_latest_prediction()

    assert result is None


def test_get_emotion_counts_with_results():
    """Test aggregation of known emotion counts."""
    mock_collection = MagicMock()
    mock_collection.aggregate.return_value = [
        {"_id": "happy", "count": 4},
        {"_id": "sad", "count": 2},
        {"_id": "neutral", "count": 3},
    ]

    with patch("app.db.get_collection", return_value=mock_collection):
        result = get_emotion_counts()

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
        result = get_emotion_counts()

    assert result == {
        "happy": 1,
        "sad": 0,
        "neutral": 0,
    }
