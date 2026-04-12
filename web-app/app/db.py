"""Database access helpers for the web application."""

from pymongo import MongoClient
from app.config import Config


def get_client():
    """Create and return a MongoDB client."""
    return MongoClient(Config.MONGO_URI)


def get_collection():
    """Return the MongoDB collection for emotion predictions."""
    client = get_client()
    return client[Config.MONGO_DB_NAME][Config.MONGO_COLLECTION]


def ping_db():
    """Check if the database connection is alive."""
    client = get_client()
    client.admin.command("ping")
    return True


def get_recent_predictions(limit=20):
    """Fetch recent prediction records."""
    collection = get_collection()
    return list(collection.find().sort("timestamp", -1).limit(limit))


def get_latest_prediction():
    """Fetch the most recent prediction."""
    collection = get_collection()
    return collection.find_one(sort=[("timestamp", -1)])


def get_emotion_counts():
    """Aggregate counts of each emotion."""
    collection = get_collection()
    pipeline = [{"$group": {"_id": "$emotion", "count": {"$sum": 1}}}]
    return list(collection.aggregate(pipeline))
