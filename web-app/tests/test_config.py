"""Tests for config."""

from app.config import Config


def test_config_defaults():
    """Config exposes expected attributes."""
    assert hasattr(Config, "SECRET_KEY")
    assert hasattr(Config, "ML_CLIENT_URL")
    assert hasattr(Config, "MONGO_URI")
    assert hasattr(Config, "MONGO_DB_NAME")
    assert hasattr(Config, "MONGO_COLLECTION")
    assert hasattr(Config, "USERS_COLLECTION")
