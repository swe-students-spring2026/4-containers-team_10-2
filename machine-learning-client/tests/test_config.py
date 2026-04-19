"""Tests for config."""

from app.config import Config


def test_config_has_expected_attributes():
    """Config exposes required settings."""
    assert hasattr(Config, "MONGO_URI")
    assert hasattr(Config, "MONGO_DB_NAME")
    assert hasattr(Config, "MONGO_COLLECTION")
    assert hasattr(Config, "ML_CLIENT_HOST")
    assert hasattr(Config, "ML_CLIENT_PORT")


def test_ml_client_port_is_int():
    """Port is an integer."""
    assert isinstance(Config.ML_CLIENT_PORT, int)
