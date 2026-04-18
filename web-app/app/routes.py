"""Route definitions for the web application."""

import uuid

import requests
from flask import Blueprint, current_app, jsonify, render_template, request
from flask_login import current_user, login_required

from app.db import (
    get_latest_prediction,
    get_recent_predictions,
    ping_db,
)
from app.services import fetch_dashboard_summary, submit_frame_for_analysis

main = Blueprint("main", __name__)


@main.route("/", methods=["GET"])
@login_required
def index():
    """Render the live hairstyle recommendation interface."""
    return render_template("index.html")


@main.route("/dashboard", methods=["GET"])
@login_required
def dashboard():
    """Render the dashboard page."""
    summary = fetch_dashboard_summary(current_user.id)
    return render_template(
        "dashboard.html",
        latest=summary["latest"],
        counts=summary["counts"],
        recent=summary["recent"],
        total_scans=summary["total_scans"],
    )


@main.route("/history", methods=["GET"])
@login_required
def history():
    """Render the history page."""
    recent = get_recent_predictions(user_id=current_user.id, limit=50)
    return render_template("history.html", recent=recent)


@main.route("/health", methods=["GET"])
def health():
    """Basic application health endpoint."""
    return jsonify({"status": "ok"}), 200


@main.route("/db-health", methods=["GET"])
def db_health():
    """Database health endpoint."""
    try:
        ping_db()
        return jsonify({"status": "ok", "database": "connected"}), 200
    except Exception as exc:  # pylint: disable=broad-except
        return jsonify({"status": "error", "message": str(exc)}), 500


@main.route("/api/analyze", methods=["POST"])
@login_required
def analyze():
    """Receive a browser frame and forward it to the ML client."""
    data = request.get_json(silent=True) or {}
    image_b64 = data.get("image_b64")

    if not image_b64:
        return jsonify({"status": "error", "message": "Missing image_b64"}), 400

    session_id = data.get("session_id") or str(uuid.uuid4())

    try:
        result = submit_frame_for_analysis(
            current_app.config["ML_CLIENT_URL"],
            image_b64,
            session_id,
            current_user.id,
        )
        return jsonify(result), 200
    except requests.RequestException as exc:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": f"ML client request failed: {exc}",
                }
            ),
            502,
        )
    except Exception as exc:  # pylint: disable=broad-except
        return jsonify({"status": "error", "message": str(exc)}), 500


@main.route("/api/history", methods=["GET"])
@login_required
def api_history():
    """Return recent prediction history as JSON."""
    limit = request.args.get("limit", default=20, type=int)
    recent = get_recent_predictions(user_id=current_user.id, limit=limit)
    return jsonify({"status": "ok", "records": recent}), 200


@main.route("/api/latest", methods=["GET"])
@login_required
def api_latest():
    """Return the latest prediction as JSON."""
    latest = get_latest_prediction(user_id=current_user.id)
    return jsonify({"status": "ok", "latest": latest}), 200
