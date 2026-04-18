"""User model helpers for Flask-Login."""

# pylint: disable=too-few-public-methods

from flask_login import UserMixin


class User(UserMixin):
    """Simple user wrapper for MongoDB-backed authentication."""

    def __init__(self, user_id, username, email):
        self.id = str(user_id)
        self.username = username
        self.email = email

    @staticmethod
    def from_document(document):
        """Build a User object from a MongoDB document."""
        if not document:
            return None

        return User(
            user_id=document["_id"],
            username=document["username"],
            email=document["email"],
        )
