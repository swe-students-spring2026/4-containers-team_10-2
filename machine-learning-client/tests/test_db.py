"""Tests for db module."""

from unittest.mock import MagicMock, patch

import pytest
from pymongo.errors import PyMongoError


@pytest.fixture(autouse=True)
def _reset_client():
    """Reset the cached MongoClient singleton between tests."""
    import app.db as db_module  # pylint: disable=import-outside-toplevel

    db_module._client = None  # pylint: disable=protected-access
    yield
    db_module._client = None  # pylint: disable=protected-access


@patch("app.db.MongoClient")
def test_get_client_returns_mongo_client(mock_mongo_client):
    """get_client wraps MongoClient using the configured URI."""
    from app.db import get_client  # pylint: disable=import-outside-toplevel

    fake_client = MagicMock()
    mock_mongo_client.return_value = fake_client

    result = get_client()

    assert result is fake_client
    mock_mongo_client.assert_called_once()


@patch("app.db.MongoClient")
def test_get_client_is_cached(mock_mongo_client):
    """get_client only instantiates MongoClient once (singleton behaviour)."""
    from app.db import get_client  # pylint: disable=import-outside-toplevel

    mock_mongo_client.return_value = MagicMock()

    first = get_client()
    second = get_client()

    assert first is second
    assert mock_mongo_client.call_count == 1


@patch("app.db.MongoClient")
def test_get_collection_uses_configured_names(mock_mongo_client):
    """get_collection selects the configured DB and collection."""
    from app.db import get_collection  # pylint: disable=import-outside-toplevel

    fake_client = MagicMock()
    mock_mongo_client.return_value = fake_client

    result = get_collection()

    # Accessing via MagicMock's __getitem__ chain should produce the collection
    assert result is fake_client.__getitem__.return_value.__getitem__.return_value


@patch("app.db.MongoClient")
def test_ping_db_success(mock_mongo_client):
    """ping_db returns True when the admin ping command succeeds."""
    from app.db import ping_db  # pylint: disable=import-outside-toplevel

    fake_client = MagicMock()
    fake_client.admin.command.return_value = {"ok": 1.0}
    mock_mongo_client.return_value = fake_client

    assert ping_db() is True
    fake_client.admin.command.assert_called_once_with("ping")


@patch("app.db.MongoClient")
def test_ping_db_wraps_pymongo_error(mock_mongo_client):
    """ping_db raises RuntimeError when MongoDB ping fails."""
    from app.db import ping_db  # pylint: disable=import-outside-toplevel

    fake_client = MagicMock()
    fake_client.admin.command.side_effect = PyMongoError("connection refused")
    mock_mongo_client.return_value = fake_client

    with pytest.raises(RuntimeError, match="Failed to ping MongoDB"):
        ping_db()


@patch("app.db.MongoClient")
def test_insert_prediction_returns_string_id(mock_mongo_client):
    """insert_prediction returns the inserted document's id as a string."""
    from app.db import insert_prediction  # pylint: disable=import-outside-toplevel

    fake_client = MagicMock()
    fake_collection = fake_client.__getitem__.return_value.__getitem__.return_value
    fake_collection.insert_one.return_value.inserted_id = "abc123"
    mock_mongo_client.return_value = fake_client

    result = insert_prediction({"foo": "bar"})

    assert result == "abc123"
    fake_collection.insert_one.assert_called_once_with({"foo": "bar"})


@patch("app.db.MongoClient")
def test_insert_prediction_wraps_pymongo_error(mock_mongo_client):
    """insert_prediction raises RuntimeError when insert_one fails."""
    from app.db import insert_prediction  # pylint: disable=import-outside-toplevel

    fake_client = MagicMock()
    fake_collection = fake_client.__getitem__.return_value.__getitem__.return_value
    fake_collection.insert_one.side_effect = PyMongoError("write error")
    mock_mongo_client.return_value = fake_client

    with pytest.raises(RuntimeError, match="Failed to insert prediction"):
        insert_prediction({"foo": "bar"})
