"""Database module for MongoDB operations."""

from pymongo import MongoClient
from pymongo.errors import PyMongoError

from app.config import Config


def get_client():
    """Get MongoDB client instance."""
    return MongoClient(Config.MONGO_URI)


def get_collection():
    """Get MongoDB collection for predictions."""
    client = get_client()
    db = client[Config.MONGO_DB_NAME]
    return db[Config.MONGO_COLLECTION]


def ping_db():
    """Ping the database to verify connection."""
    client = get_client()
    client.admin.command("ping")
    return True


def insert_prediction(document):
    """Insert a prediction document into MongoDB."""
    try:
        collection = get_collection()
        result = collection.insert_one(document)
        return str(result.inserted_id)
    except PyMongoError as exc:
        raise RuntimeError("Failed to insert prediction into MongoDB") from exc
