from flask import Flask

from app.config import Config
from app.routes import main

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.register_blueprint(main)
    return app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)