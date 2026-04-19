"""HTTP server for the machine-learning client."""

from flask import Flask, jsonify, request

from app.config import Config
from app.db import insert_prediction, ping_db
from app.face_shape_service import detect_face_shape
from app.image_utils import decode_base64_image
from app.schemas import build_prediction_document

app = Flask(__name__)


@app.route("/health", methods=["GET"])
def health():
    """Basic health endpoint."""
    return jsonify({"status": "ok"}), 200


@app.route("/db-health", methods=["GET"])
def db_health():
    """Database health endpoint."""
    try:
        ping_db()
        return jsonify({"status": "ok", "database": "connected"}), 200
    except Exception as exc:  # pylint: disable=broad-except
        return jsonify({"status": "error", "message": str(exc)}), 500


@app.route("/analyze", methods=["POST"])
def analyze():
    """Analyze an incoming webcam frame for face shape."""
    data = request.get_json(silent=True) or {}

    user_id = data.get("user_id")
    session_id = data.get("session_id", "default-session")
    image_b64 = data.get("image_b64")

    if not image_b64:
        return jsonify({"status": "error", "message": "Missing image_b64"}), 400

    if not user_id:
        return jsonify({"status": "error", "message": "Missing user_id"}), 400

    try:
        image = decode_base64_image(image_b64)
        result = detect_face_shape(image, session_id=session_id)

        document = build_prediction_document(user_id, session_id, result)
        inserted_id = insert_prediction(document)

        return (
            jsonify(
                {
                    "status": "ok",
                    "inserted_id": inserted_id,
                    "face_detected": result["face_detected"],
                    "face_shape": result["face_shape"],
                    "confidence": result["confidence"],
                    "recommended_hairstyles": result["recommended_hairstyles"],
                    "face_box": result.get("face_box"),
                }
            ),
            200,
        )
    except Exception as exc:  # pylint: disable=broad-except
        return jsonify({"status": "error", "message": str(exc)}), 500


if __name__ == "__main__":
    app.run(host=Config.ML_CLIENT_HOST, port=Config.ML_CLIENT_PORT, debug=True)
