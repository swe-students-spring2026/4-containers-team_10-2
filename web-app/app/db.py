"""Database access helpers for the web application."""

from bson import ObjectId
from pymongo import MongoClient

from app.config import Config


def get_client():
    """Create and return a MongoDB client."""
    return MongoClient(Config.MONGO_URI)


def get_collection():
    """Return the MongoDB collection for face-shape predictions."""
    client = get_client()
    db = client[Config.MONGO_DB_NAME]
    return db[Config.MONGO_COLLECTION]


def get_users_collection():
    """Return the MongoDB collection for users."""
    client = get_client()
    db = client[Config.MONGO_DB_NAME]
    return db[Config.USERS_COLLECTION]


def ping_db():
    """Check whether the database connection is alive."""
    client = get_client()
    client.admin.command("ping")
    return True


def _serialize_record(record):
    """Convert MongoDB fields into template/API-friendly values."""
    if not record:
        return None

    record["_id"] = str(record["_id"])
    if "user_id" in record:
        record["user_id"] = str(record["user_id"])
    return record


def create_user(user_document):
    """Insert a new user document."""
    collection = get_users_collection()
    result = collection.insert_one(user_document)
    return result.inserted_id


def find_user_by_email(email):
    """Find a user by email."""
    collection = get_users_collection()
    return collection.find_one({"email": email})


def find_user_by_username(username):
    """Find a user by username."""
    collection = get_users_collection()
    return collection.find_one({"username": username})


def find_user_by_id(user_id):
    """Find a user by MongoDB id."""
    collection = get_users_collection()

    try:
        return collection.find_one({"_id": ObjectId(user_id)})
    except Exception:  # pylint: disable=broad-except
        return None


def get_recent_predictions(user_id, limit=20):
    """Fetch recent face-shape prediction records for a user."""
    collection = get_collection()
    records = list(
        collection.find({"user_id": user_id}).sort("timestamp", -1).limit(limit)
    )
    return [_serialize_record(record) for record in records]


def get_latest_prediction(user_id):
    """Fetch the latest prediction record for a user."""
    collection = get_collection()
    record = collection.find_one({"user_id": user_id}, sort=[("timestamp", -1)])
    return _serialize_record(record)


def get_face_shape_counts(user_id):
    """Aggregate counts by detected face shape for a user."""
    collection = get_collection()
    pipeline = [
        {"$match": {"user_id": user_id}},
        {
            "$group": {
                "_id": "$face_shape",
                "count": {"$sum": 1},
            }
        },
    ]
    results = list(collection.aggregate(pipeline))

    counts = {}

    for item in results:
        shape = item["_id"] or "Unknown"
        counts[shape] = item["count"]

    return counts


def get_total_scans(user_id):
    """Return total number of scans for a user."""
    collection = get_collection()
    return collection.count_documents({"user_id": user_id})
