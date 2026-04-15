"""Pytest fixtures for the web application tests."""

# pylint: disable=redefined-outer-name

import pytest

from app.app import create_app


@pytest.fixture
def app():
    """Create and configure a Flask app for testing."""
    flask_app = create_app()
    flask_app.config.update(
        TESTING=True,
        ML_CLIENT_URL="http://localhost:5001",
    )
    return flask_app


@pytest.fixture
def client(app):
    """Create a Flask test client."""
    return app.test_client()
