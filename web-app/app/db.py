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
    """Check whether the database connection is alive."""
    client = get_client()
    client.admin.command("ping")
    return True


def _serialize_record(record):
    """Convert MongoDB record fields to template/API-friendly values."""
    if not record:
        return None

    record["_id"] = str(record["_id"])
    return record


def get_recent_predictions(limit=20):
    """Fetch the most recent prediction records."""
    collection = get_collection()
    records = list(collection.find().sort("timestamp", -1).limit(limit))
    return [_serialize_record(record) for record in records]


def get_latest_prediction():
    """Fetch the latest prediction record."""
    collection = get_collection()
    record = collection.find_one(sort=[("timestamp", -1)])
    return _serialize_record(record)


def get_emotion_counts():
    """Aggregate counts by emotion."""
    collection = get_collection()
    pipeline = [
        {
            "$group": {
                "_id": "$emotion",
                "count": {"$sum": 1},
            }
        }
    ]
    results = list(collection.aggregate(pipeline))

    counts = {
        "happy": 0,
        "sad": 0,
        "neutral": 0,
    }

    for item in results:
        emotion = item["_id"]
        if emotion in counts:
            counts[emotion] = item["count"]

    return counts
