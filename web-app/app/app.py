"""Flask application entry point."""

from flask import Flask

from app.config import Config
from app.routes import main


def create_app():
    """Create and configure the Flask application."""
    flask_app = Flask(__name__)
    flask_app.config.from_object(Config)
    flask_app.register_blueprint(main)
    return flask_app


app = create_app()
