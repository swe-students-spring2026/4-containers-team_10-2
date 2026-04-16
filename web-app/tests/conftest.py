"""Pytest fixtures for the web application tests."""

# pylint: disable=redefined-outer-name

import pytest

import app.app as app_module
from app.app import create_app
from app.models import User


@pytest.fixture
def app():
    """Create and configure a Flask app for testing."""
    flask_app = create_app()
    flask_app.config.update(
        TESTING=True,
        SECRET_KEY="test-secret-key",
        ML_CLIENT_URL="http://localhost:5001",
        LOGIN_DISABLED=False,
    )
    return flask_app


@pytest.fixture
def client(app):
    """Create a Flask test client."""
    return app.test_client()


@pytest.fixture
def test_user():
    """Create a reusable authenticated user object."""
    return User("507f1f77bcf86cd799439011", "testuser", "test@example.com")


@pytest.fixture(autouse=True)
def mock_find_user_by_id(monkeypatch, test_user):
    """Mock Flask-Login user loading to always return the test user."""
    user_document = {
        "_id": test_user.id,
        "username": test_user.username,
        "email": test_user.email,
    }

    def fake_find_user_by_id(_user_id):
        return user_document

    monkeypatch.setattr(app_module, "find_user_by_id", fake_find_user_by_id)


@pytest.fixture
def logged_in_client(client, test_user):
    """Return a client with an authenticated session."""
    with client.session_transaction() as session:
        session["_user_id"] = test_user.id
        session["_fresh"] = True
    return client
