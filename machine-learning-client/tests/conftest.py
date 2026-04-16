"""Shared pytest fixtures for the machine-learning-client tests."""

import pytest

from app.server import app as flask_app


@pytest.fixture
def app():
    """Provide the Flask app configured for testing."""
    flask_app.config.update({"TESTING": True})
    return flask_app


@pytest.fixture
def client(app):  # pylint: disable=redefined-outer-name
    """Provide a Flask test client."""
    return app.test_client()
