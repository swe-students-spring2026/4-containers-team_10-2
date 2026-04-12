"""Flask server for emotion detection API."""

from flask import Flask, jsonify, request

from app.config import Config
from app.db import insert_prediction, ping_db
from app.emotion_service import detect_emotion
from app.schemas import build_prediction_document

app = Flask(__name__)


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({"status": "ok"}), 200


@app.route("/db-health", methods=["GET"])
def db_health():
    """Database health check endpoint."""
    try:
        ping_db()
        return jsonify({"status": "ok", "database": "connected"}), 200
    except RuntimeError as exc:
        return jsonify({"status": "error", "message": str(exc)}), 500


@app.route("/analyze", methods=["POST"])
def analyze():
    """Analyze emotion from image data."""
    data = request.get_json(silent=True) or {}
    session_id = data.get("session_id", "default-session")
    image_b64 = data.get("image_b64")

    result = detect_emotion(image_b64)
    document = build_prediction_document(session_id, result)
    inserted_id = insert_prediction(document)

    return (
        jsonify(
            {
                "status": "ok",
                "inserted_id": inserted_id,
                "emotion": result["emotion"],
                "confidence": result["confidence"],
                "border_color": result["border_color"],
                "face_detected": result["face_detected"],
            }
        ),
        200,
    )


if __name__ == "__main__":
    app.run(host=Config.ML_CLIENT_HOST, port=Config.ML_CLIENT_PORT, debug=True)
