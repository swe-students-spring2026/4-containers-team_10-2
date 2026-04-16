"""Authentication tests for the web application."""

from unittest.mock import patch

from werkzeug.security import generate_password_hash


def test_login_page_renders(client):
    """Test that the login page renders."""
    response = client.get("/login")
    assert response.status_code == 200
    assert b"Login" in response.data


def test_signup_page_renders(client):
    """Test that the signup page renders."""
    response = client.get("/signup")
    assert response.status_code == 200
    assert b"Create Account" in response.data


def test_signup_missing_fields(client):
    """Test signup with missing fields."""
    response = client.post(
        "/signup",
        data={"username": "", "email": "", "password": ""},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"All fields are required." in response.data


def test_signup_duplicate_username(client):
    """Test signup failure when username already exists."""
    with patch(
        "app.auth.find_user_by_username", return_value={"username": "testuser"}
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
    """Test signup failure when email already exists."""
    with patch("app.auth.find_user_by_username", return_value=None), patch(
        "app.auth.find_user_by_email", return_value={"email": "test@example.com"}
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
    """Test successful signup and login."""
    with patch("app.auth.find_user_by_username", return_value=None), patch(
        "app.auth.find_user_by_email", return_value=None
    ), patch("app.auth.create_user", return_value="507f1f77bcf86cd799439011"):
        response = client.post(
            "/signup",
            data={
                "username": "testuser",
                "email": "test@example.com",
                "password": "password123",
            },
            follow_redirects=False,
        )

    assert response.status_code == 302
    assert "/dashboard" in response.headers["Location"]


def test_login_invalid_credentials(client):
    """Test login failure with invalid credentials."""
    with patch("app.auth.find_user_by_email", return_value=None):
        response = client.post(
            "/login",
            data={"email": "bad@example.com", "password": "wrong"},
            follow_redirects=True,
        )

    assert response.status_code == 200
    assert b"Invalid email or password." in response.data


def test_login_success(client):
    """Test successful login."""
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
            follow_redirects=False,
        )

    assert response.status_code == 302
    assert "/dashboard" in response.headers["Location"]


def test_logout_requires_login(client):
    """Test that logout requires authentication."""
    response = client.get("/logout")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_logout_success(logged_in_client):
    """Test successful logout."""
    response = logged_in_client.get("/logout", follow_redirects=True)
    assert response.status_code == 200
    assert b"Logged out successfully." in response.data
