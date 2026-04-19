"""Tests for app factory."""

from app.app import create_app


def test_create_app():
    """App factory builds the app."""
    flask_app = create_app()

    assert flask_app is not None
    assert "main" in flask_app.blueprints
    assert "auth" in flask_app.blueprints
    assert flask_app.config["SECRET_KEY"] is not None


def test_login_manager_config():
    """Login manager is configured."""
    flask_app = create_app()

    assert getattr(flask_app, "login_manager").login_view == "auth.login"
