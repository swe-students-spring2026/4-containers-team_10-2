"""Configuration for the web application."""

# pylint: disable=too-few-public-methods

import os


class Config:
    """Application configuration values."""

    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    ML_CLIENT_URL = os.getenv("ML_CLIENT_URL", "http://localhost:5001")
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
    MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "hairstyle_app")
    MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", "face_shape_predictions")
    USERS_COLLECTION = os.getenv("USERS_COLLECTION", "users")
