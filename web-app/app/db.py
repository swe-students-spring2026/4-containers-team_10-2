"""Database helpers for the web app."""

from bson import ObjectId
from pymongo import MongoClient

from app.config import Config


def get_client():
    """Return a Mongo client."""
    return MongoClient(Config.MONGO_URI)


def get_collection():
    """Return the predictions collection."""
    client = get_client()
    db = client[Config.MONGO_DB_NAME]
    return db[Config.MONGO_COLLECTION]


def get_users_collection():
    """Return the users collection."""
    client = get_client()
    db = client[Config.MONGO_DB_NAME]
    return db[Config.USERS_COLLECTION]


def ping_db():
    """Ping Mongo."""
    client = get_client()
    client.admin.command("ping")
    return True


def _serialize_record(record):
    """Serialize Mongo fields."""
    if not record:
        return None

    record["_id"] = str(record["_id"])
    if "user_id" in record:
        record["user_id"] = str(record["user_id"])
    return record


def create_user(user_document):
    """Create a user."""
    collection = get_users_collection()
    result = collection.insert_one(user_document)
    return result.inserted_id


def find_user_by_email(email):
    """Find user by email."""
    collection = get_users_collection()
    return collection.find_one({"email": email})


def find_user_by_username(username):
    """Find user by username."""
    collection = get_users_collection()
    return collection.find_one({"username": username})


def find_user_by_id(user_id):
    """Find user by id."""
    collection = get_users_collection()
    try:
        return collection.find_one({"_id": ObjectId(user_id)})
    except Exception:  # pylint: disable=broad-except
        return None


def get_recent_predictions(user_id, limit=20):
    """Get recent predictions for a user."""
    collection = get_collection()
    records = list(
        collection.find({"user_id": user_id}).sort("timestamp", -1).limit(limit)
    )
    return [_serialize_record(record) for record in records]


def get_latest_prediction(user_id):
    """Get latest prediction for a user."""
    collection = get_collection()
    record = collection.find_one({"user_id": user_id}, sort=[("timestamp", -1)])
    return _serialize_record(record)


def get_face_shape_counts(user_id):
    """Get counts by face shape."""
    collection = get_collection()
    pipeline = [
        {"$match": {"user_id": user_id}},
        {"$group": {"_id": "$face_shape", "count": {"$sum": 1}}},
    ]
    results = list(collection.aggregate(pipeline))

    counts = {}
    for item in results:
        shape = item["_id"] or "Unknown"
        counts[shape] = item["count"]

    return counts


def get_total_scans(user_id):
    """Get total scan count."""
    collection = get_collection()
    return collection.count_documents({"user_id": user_id})


def get_user_preferences(user_id):
    """Get saved preferences."""
    user = find_user_by_id(user_id)
    if not user:
        return {
            "hair_length": "any",
            "hair_texture": "any",
            "maintenance_level": "any",
        }

    return user.get(
        "preferences",
        {
            "hair_length": "any",
            "hair_texture": "any",
            "maintenance_level": "any",
        },
    )


def update_user_preferences(user_id, preferences):
    """Update saved preferences."""
    collection = get_users_collection()
    collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"preferences": preferences}},
    )


def get_favorite_styles(user_id):
    """Get favorite styles."""
    user = find_user_by_id(user_id)
    if not user:
        return []
    return user.get("favorite_styles", [])


def add_favorite_style(user_id, style):
    """Add a favorite style."""
    collection = get_users_collection()
    collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$addToSet": {"favorite_styles": style}},
    )


def remove_favorite_style(user_id, style_name, category):
    """Remove a favorite style."""
    collection = get_users_collection()
    collection.update_one(
        {"_id": ObjectId(user_id)},
        {
            "$pull": {
                "favorite_styles": {
                    "name": style_name,
                    "category": category,
                }
            }
        },
    )
