"""Tests for auth routes."""

from unittest.mock import patch

from werkzeug.security import generate_password_hash


def test_signup_get(client):
    """Signup page renders."""
    response = client.get("/signup")

    assert response.status_code == 200


def test_signup_missing_fields(client):
    """Signup rejects missing fields."""
    response = client.post(
        "/signup",
        data={"username": "", "email": "", "password": ""},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"All fields are required." in response.data


def test_signup_duplicate_username(client):
    """Signup rejects duplicate username."""
    with patch(
        "app.auth.find_user_by_username",
        return_value={"username": "testuser"},
    ), patch("app.auth.find_user_by_email", return_value=None):
        response = client.post(
            "/signup",
            data={
                "username": "testuser",
                "email": "test@example.com",
                "password": "password123",
            },
            follow_redirects=True,
        )

    assert response.status_code == 200
    assert b"Username already exists." in response.data


def test_signup_duplicate_email(client):
    """Signup rejects duplicate email."""
    with patch("app.auth.find_user_by_username", return_value=None), patch(
        "app.auth.find_user_by_email",
        return_value={"email": "test@example.com"},
    ):
        response = client.post(
            "/signup",
            data={
                "username": "testuser",
                "email": "test@example.com",
                "password": "password123",
            },
            follow_redirects=True,
        )

    assert response.status_code == 200
    assert b"Email already exists." in response.data


def test_signup_success(client):
    """Signup creates a user and logs them in."""
    with patch("app.auth.find_user_by_username", return_value=None), patch(
        "app.auth.find_user_by_email",
        return_value=None,
    ), patch(
        "app.auth.create_user",
        return_value="507f1f77bcf86cd799439011",
    ):
        response = client.post(
            "/signup",
            data={
                "username": "testuser",
                "email": "test@example.com",
                "password": "password123",
            },
            follow_redirects=True,
        )

    assert response.status_code == 200
    assert b"Account created successfully." in response.data


def test_login_get(client):
    """Login page renders."""
    response = client.get("/login")

    assert response.status_code == 200


def test_login_invalid_credentials(client):
    """Login rejects bad credentials."""
    with patch("app.auth.find_user_by_email", return_value=None):
        response = client.post(
            "/login",
            data={"email": "bad@example.com", "password": "wrong"},
            follow_redirects=True,
        )

    assert response.status_code == 200
    assert b"Invalid email or password." in response.data


def test_login_success(client):
    """Login succeeds with valid credentials."""
    user_document = {
        "_id": "507f1f77bcf86cd799439011",
        "username": "testuser",
        "email": "test@example.com",
        "password_hash": generate_password_hash("password123"),
    }

    with patch("app.auth.find_user_by_email", return_value=user_document):
        response = client.post(
            "/login",
            data={"email": "test@example.com", "password": "password123"},
            follow_redirects=True,
        )

    assert response.status_code == 200
    assert b"Logged in successfully." in response.data


def test_logout_success(logged_in_client):
    """Logout clears the session."""
    response = logged_in_client.get("/logout", follow_redirects=True)

    assert response.status_code == 200
    assert b"Logged out successfully." in response.data
