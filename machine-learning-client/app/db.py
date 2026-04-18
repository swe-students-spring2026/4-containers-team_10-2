"""Database helpers for the machine-learning client."""

from pymongo import MongoClient
from pymongo.errors import PyMongoError

from app.config import Config

_CLIENT = None
_CLIENT_SOURCE = None


def get_client():
    """Create and cache a MongoDB client."""
    global _CLIENT, _CLIENT_SOURCE  # pylint: disable=global-statement

    if _CLIENT is None or _CLIENT_SOURCE is not MongoClient:
        _CLIENT = MongoClient(Config.MONGO_URI)
        _CLIENT_SOURCE = MongoClient

    return _CLIENT


def get_collection():
    """Return the MongoDB collection for face-shape predictions."""
    client = get_client()
    db = client[Config.MONGO_DB_NAME]
    return db[Config.MONGO_COLLECTION]


def ping_db():
    """Check that the database connection is alive."""
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
        raise RuntimeError("Failed to insert prediction") from exc
