from werkzeug.security import generate_password_hash, check_password_hash
from unittest.mock import patch
from werkzeug.security import generate_password_hash



def test_password_hashing():
    password = "test123"
    hashed = generate_password_hash(password)

    assert check_password_hash(hashed, password) is True


# -----------------------------
# SIGNUP
# -----------------------------

def test_signup_missing_fields(client):
    res = client.post("/signup", data={
        "username": "",
        "email": "",
        "password": ""
    })
    assert res.status_code == 200


@patch("app.auth.find_user_by_username", return_value=True)
def test_signup_duplicate_username(mock_user, client):
    res = client.post("/signup", data={
        "username": "test",
        "email": "test@test.com",
        "password": "pass"
    })
    assert res.status_code == 200


@patch("app.auth.find_user_by_username", return_value=None)
@patch("app.auth.find_user_by_email", return_value=True)
def test_signup_duplicate_email(mock_email, mock_user, client):
    res = client.post("/signup", data={
        "username": "test",
        "email": "test@test.com",
        "password": "pass"
    })
    assert res.status_code == 200


@patch("app.auth.find_user_by_username", return_value=None)
@patch("app.auth.find_user_by_email", return_value=None)
@patch("app.auth.create_user", return_value="507f1f77bcf86cd799439011")
def test_signup_success(mock_create, mock_email, mock_user, client):
    res = client.post("/signup", data={
        "username": "test",
        "email": "test@test.com",
        "password": "pass"
    })
    assert res.status_code in [200, 302]


# -----------------------------
# LOGIN
# -----------------------------

def test_login_get(client):
    res = client.get("/login")
    assert res.status_code == 200


@patch("app.auth.find_user_by_email", return_value=None)
def test_login_invalid_user(mock_email, client):
    res = client.post("/login", data={
        "email": "bad@test.com",
        "password": "wrong"
    })
    assert res.status_code == 200


@patch("app.auth.find_user_by_email")
def test_login_wrong_password(mock_email, client):
    mock_email.return_value = {
        "_id": "507f1f77bcf86cd799439011",
        "username": "test",
        "email": "test@test.com",
        "password_hash": generate_password_hash("correct")
    }

    with patch("werkzeug.security.check_password_hash", return_value=False):
        res = client.post("/login", data={
            "email": "test@test.com",
            "password": "wrong"
        })
        assert res.status_code == 200


@patch("app.auth.find_user_by_email")
def test_login_success(mock_email, client):
    mock_email.return_value = {
        "_id": "507f1f77bcf86cd799439011",
        "username": "test",
        "email": "test@test.com",
        "password_hash": generate_password_hash("pass")
    }

    with patch("werkzeug.security.check_password_hash", return_value=True):
        res = client.post("/login", data={
            "email": "test@test.com",
            "password": "pass"
        })
        assert res.status_code in [200, 302]


# -----------------------------
# LOGOUT
# -----------------------------

def test_logout(client):
    res = client.get("/logout")
    assert res.status_code in [200, 302]


