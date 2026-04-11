# mostly placeholders for now 

from pymongo import MongoClient

from app.config import Config

def get_client():
    return MongoClient(Config.MONGO_URI)

def get_collection():
    client = get_client()
    db = client[Config.MONGO_DB_NAME]
    return db[Config.MONGO_COLLECTION]

def ping_db():
    client = get_client()
    client.admin.command("ping")
    return True

def get_recent_predictions(limit=20):
    collection = get_collection()
    records = list(collection.find().sort("timestamp", -1).limit(limit))

    for record in records:
        record["_id"] = str(record["_id"])

    return records

def get_latest_prediction():
    collection = get_collection()
    record = collection.find_one(sort=[("timestamp", -1)])

    if record:
        record["_id"] = str(record["_id"])

    return record

def get_emotion_counts():
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