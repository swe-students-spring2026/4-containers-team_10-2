"""Route definitions for the web application."""

import uuid
from flask import Blueprint, current_app, jsonify, render_template, request

from app.services import submit_frame_for_analysis

main = Blueprint("main", __name__)


@main.route("/")
def index():
    """Render the main webcam page."""
    return render_template("index.html")


@main.route("/health")
def health():
    """Health check endpoint."""
    return jsonify({"status": "ok"})


@main.route("/api/analyze", methods=["POST"])
def analyze():
    """Handle frame analysis requests."""
    data = request.get_json(silent=True) or {}
    image_b64 = data.get("image_b64")

    if not image_b64:
        return jsonify({"status": "error"}), 400

    session_id = data.get("session_id") or str(uuid.uuid4())

    result = submit_frame_for_analysis(
        current_app.config["ML_CLIENT_URL"],
        image_b64,
        session_id,
    )

    return jsonify(result)
