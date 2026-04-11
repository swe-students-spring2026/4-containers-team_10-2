from pymongo import MongoClient
from pymongo.errors import PyMongoError

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

def insert_prediction(document):
    try:
        collection = get_collection()
        result = collection.insert_one(document)
        return str(result.inserted_id)
    except PyMongoError as exc:
        raise RuntimeError("Failed to insert prediction into MongoDB") from exc