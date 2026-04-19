"""Pytest fixtures for machine-learning-client."""

# pylint: disable=redefined-outer-name

import pytest

from app.server import app as flask_app


@pytest.fixture
def app():
    """Return Flask app."""
    flask_app.config.update(TESTING=True)
    return flask_app


@pytest.fixture
def client(app):
    """Return test client."""
    return app.test_client()
