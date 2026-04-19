import pytest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.app import create_app


class FakeUser:
    id = "507f1f77bcf86cd799439011"
    is_authenticated = False   # 🔥 ADD THIS


@pytest.fixture
def app():
    app = create_app()
    app.config["TESTING"] = True
    app.config["LOGIN_DISABLED"] = True
    return app


@pytest.fixture
def client(app, monkeypatch):
    # fake logged-in user
    monkeypatch.setattr("flask_login.utils._get_user", lambda: FakeUser())

    # MOCK ALL DB FUNCTIONS HERE
    monkeypatch.setattr("app.routes.get_recent_predictions", lambda *args, **kwargs: [])
    monkeypatch.setattr("app.routes.get_latest_prediction", lambda *args, **kwargs: {})
    monkeypatch.setattr("app.routes.get_user_preferences", lambda *args, **kwargs: {})
    monkeypatch.setattr("app.routes.get_favorite_styles", lambda *args, **kwargs: [])
    monkeypatch.setattr("app.routes.update_user_preferences", lambda *args, **kwargs: None)
    monkeypatch.setattr("app.routes.add_favorite_style", lambda *args, **kwargs: None)
    monkeypatch.setattr("app.routes.remove_favorite_style", lambda *args, **kwargs: None)
    monkeypatch.setattr("app.routes.ping_db", lambda: True)

    monkeypatch.setattr(
        "app.routes.submit_frame_for_analysis",
        lambda *args, **kwargs: {"recommended_hairstyles": []},
    )
    monkeypatch.setattr(
        "app.routes.apply_preferences_to_recommendations",
        lambda *args, **kwargs: [],
    )
    monkeypatch.setattr(
        "app.routes.annotate_favorites",
        lambda *args, **kwargs: [],
    )

    return app.test_client()