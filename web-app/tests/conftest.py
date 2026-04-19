"""Pytest fixtures for the web app."""

# pylint: disable=redefined-outer-name

from unittest.mock import patch

import pytest

from app.app import create_app
from app.models import User


@pytest.fixture
def app():
    """Create a test app."""
    flask_app = create_app()
    flask_app.config.update(
        TESTING=True,
        SECRET_KEY="test-secret-key",
        ML_CLIENT_URL="http://localhost:5001",
        LOGIN_DISABLED=False,
        WTF_CSRF_ENABLED=False,
    )
    return flask_app


@pytest.fixture
def client(app):
    """Create a test client."""
    return app.test_client()


@pytest.fixture
def test_user():
    """Create a reusable user."""
    return User("507f1f77bcf86cd799439011", "testuser", "test@example.com")


@pytest.fixture
def logged_in_client(app, client, test_user):  # pylint: disable=unused-argument
    """Create an authenticated test client."""
    with patch(
        "app.app.find_user_by_id",
        return_value={
            "_id": test_user.id,
            "username": test_user.username,
            "email": test_user.email,
        },
    ):
        with client.session_transaction() as session:
            session["_user_id"] = test_user.id
            session["_fresh"] = True
        yield client
