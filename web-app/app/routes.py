import uuid

from flask import Blueprint, current_app, jsonify, render_template, request

from app.services import submit_frame_for_analysis

main = Blueprint("main", __name__)

@main.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@main.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200

@main.route("/api/analyze", methods=["POST"])
def analyze():
    data = request.get_json(silent=True) or {}
    image_b64 = data.get("image_b64")

    if not image_b64:
        return jsonify({"status": "error", "message": "Missing image_b64"}), 400

    session_id = data.get("session_id") or str(uuid.uuid4())

    result = submit_frame_for_analysis(
        current_app.config["ML_CLIENT_URL"],
        image_b64,
        session_id,
    )

    return jsonify(result), 200