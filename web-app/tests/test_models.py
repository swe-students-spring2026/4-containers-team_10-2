"""Tests for models."""

from app.models import User


def test_user_init():
    """User stores core fields."""
    user = User("1", "testuser", "test@example.com")

    assert user.id == "1"
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.is_authenticated is True


def test_user_from_document():
    """User can be created from db document."""
    doc = {
        "_id": "507f1f77bcf86cd799439011",
        "username": "testuser",
        "email": "test@example.com",
    }

    user = User.from_document(doc)

    assert user.id == "507f1f77bcf86cd799439011"
    assert user.username == "testuser"
    assert user.email == "test@example.com"
