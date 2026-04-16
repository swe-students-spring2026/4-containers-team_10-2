"""Database module for MongoDB operations."""

from pymongo import MongoClient
from pymongo.errors import PyMongoError

from app.config import Config

_client = None


def get_client():
    """Get MongoDB client instance (cached singleton)."""
    global _client  # pylint: disable=global-statement
    if _client is None:
        _client = MongoClient(Config.MONGO_URI)
    return _client


def get_collection():
    """Get MongoDB collection for predictions."""
    client = get_client()
    database = client[Config.MONGO_DB_NAME]
    return database[Config.MONGO_COLLECTION]


def ping_db():
    """Ping the database to verify connection."""
    try:
        client = get_client()
        client.admin.command("ping")
        return True
    except PyMongoError as exc:
        raise RuntimeError("Failed to ping MongoDB") from exc


def insert_prediction(document):
    """Insert a prediction document into MongoDB."""
    try:
        collection = get_collection()
        result = collection.insert_one(document)
        return str(result.inserted_id)
    except PyMongoError as exc:
        raise RuntimeError("Failed to insert prediction into MongoDB") from exc