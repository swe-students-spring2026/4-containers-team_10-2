"""Configuration module for environment variables."""

# pylint: disable=too-few-public-methods

import os


class Config:
    """Configuration class for application settings."""

    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
    MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "emotion_app")
    MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", "emotion_predictions")
    ML_CLIENT_HOST = os.getenv("ML_CLIENT_HOST", "0.0.0.0")
    ML_CLIENT_PORT = int(os.getenv("ML_CLIENT_PORT", "5001"))
