"""Flask application entry point."""

from flask import Flask
from flask_login import LoginManager

from app.auth import auth
from app.config import Config
from app.db import find_user_by_id
from app.models import User
from app.routes import main


def create_app():
    """Create and configure the Flask application."""
    flask_app = Flask(__name__)
    flask_app.config.from_object(Config)

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(flask_app)

    @login_manager.user_loader
    def load_user(user_id):
        """Load a user for Flask-Login."""
        document = find_user_by_id(user_id)
        return User.from_document(document)

    flask_app.register_blueprint(main)
    flask_app.register_blueprint(auth)

    return flask_app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
