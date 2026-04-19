"""Tests for db helpers."""

from unittest.mock import MagicMock, patch

import pytest
from pymongo.errors import PyMongoError

from app import db as db_module
from app.db import get_client, get_collection, insert_prediction, ping_db


@patch("app.db.MongoClient")
def test_get_client_returns_client(mock_mongo_client):
    """get_client returns a Mongo client."""
    fake_client = MagicMock()
    mock_mongo_client.return_value = fake_client

    result = get_client()

    assert result is fake_client
    mock_mongo_client.assert_called_once()


@patch("app.db.MongoClient")
def test_get_client_is_cached(mock_mongo_client):
    """get_client caches the client."""
    fake_client = MagicMock()
    mock_mongo_client.return_value = fake_client

    db_module.CACHED_CLIENT = None
    db_module.CACHED_CLIENT_SOURCE = None

    first = get_client()
    second = get_client()

    assert first is second
    assert mock_mongo_client.call_count == 1


@patch("app.db.get_client")
def test_get_collection_returns_collection(mock_get_client):
    """get_collection returns configured collection."""
    fake_client = MagicMock()
    fake_db = MagicMock()
    fake_collection = MagicMock()

    fake_client.__getitem__.return_value = fake_db
    fake_db.__getitem__.return_value = fake_collection
    mock_get_client.return_value = fake_client

    result = get_collection()

    assert result is fake_collection


@patch("app.db.get_client")
def test_ping_db_success(mock_get_client):
    """ping_db succeeds."""
    fake_client = MagicMock()
    mock_get_client.return_value = fake_client

    assert ping_db() is True
    fake_client.admin.command.assert_called_once_with("ping")


@patch("app.db.get_client")
def test_ping_db_wraps_pymongo_error(mock_get_client):
    """ping_db wraps PyMongo errors."""
    fake_client = MagicMock()
    fake_client.admin.command.side_effect = PyMongoError("connection refused")
    mock_get_client.return_value = fake_client

    with pytest.raises(RuntimeError, match="Failed to ping MongoDB"):
        ping_db()


@patch("app.db.get_collection")
def test_insert_prediction_success(mock_get_collection):
    """insert_prediction inserts a document."""
    fake_collection = MagicMock()
    fake_collection.insert_one.return_value.inserted_id = "abc123"
    mock_get_collection.return_value = fake_collection

    result = insert_prediction({"face_shape": "Oval"})

    assert result == "abc123"
    fake_collection.insert_one.assert_called_once_with({"face_shape": "Oval"})


@patch("app.db.get_collection")
def test_insert_prediction_wraps_pymongo_error(mock_get_collection):
    """insert_prediction wraps PyMongo errors."""
    fake_collection = MagicMock()
    fake_collection.insert_one.side_effect = PyMongoError("insert failed")
    mock_get_collection.return_value = fake_collection

    with pytest.raises(RuntimeError, match="Failed to insert prediction"):
        insert_prediction({"face_shape": "Oval"})
