"""Routes for the web app."""

import uuid

import requests
from flask import Blueprint, current_app, jsonify, render_template, request
from flask_login import current_user, login_required

from app.db import (
    add_favorite_style,
    get_favorite_styles,
    get_latest_prediction,
    get_recent_predictions,
    get_user_preferences,
    ping_db,
    remove_favorite_style,
    update_user_preferences,
)
from app.services import (
    annotate_favorites,
    apply_preferences_to_recommendations,
    fetch_dashboard_summary,
    submit_frame_for_analysis,
)

main = Blueprint("main", __name__)


@main.route("/", methods=["GET"])
@login_required
def index():
    """Render live scan page."""
    preferences = get_user_preferences(current_user.id)
    favorites = get_favorite_styles(current_user.id)
    return render_template(
        "index.html",
        preferences=preferences,
        favorites=favorites,
    )


@main.route("/dashboard", methods=["GET"])
@login_required
def dashboard():
    """Render dashboard."""
    summary = fetch_dashboard_summary(current_user.id)
    latest = summary["latest"]

    if latest and latest.get("recommended_hairstyles"):
        latest["recommended_hairstyles"] = apply_preferences_to_recommendations(
            latest["recommended_hairstyles"],
            summary["preferences"],
        )
        latest["recommended_hairstyles"] = annotate_favorites(
            latest["recommended_hairstyles"],
            summary["favorites"],
        )

    return render_template(
        "dashboard.html",
        latest=latest,
        counts=summary["counts"],
        recent=summary["recent"],
        total_scans=summary["total_scans"],
        preferences=summary["preferences"],
        favorites=summary["favorites"],
    )


@main.route("/history", methods=["GET"])
@login_required
def history():
    """Render history page."""
    recent = get_recent_predictions(user_id=current_user.id, limit=50)
    preferences = get_user_preferences(current_user.id)
    favorites = get_favorite_styles(current_user.id)

    for item in recent:
        if item.get("recommended_hairstyles"):
            item["recommended_hairstyles"] = apply_preferences_to_recommendations(
                item["recommended_hairstyles"],
                preferences,
            )
            item["recommended_hairstyles"] = annotate_favorites(
                item["recommended_hairstyles"],
                favorites,
            )

    return render_template("history.html", recent=recent, favorites=favorites)


@main.route("/health", methods=["GET"])
def health():
    """Basic health check."""
    return jsonify({"status": "ok"}), 200


@main.route("/db-health", methods=["GET"])
def db_health():
    """Database health check."""
    try:
        ping_db()
        return jsonify({"status": "ok", "database": "connected"}), 200
    except Exception as exc:  # pylint: disable=broad-except
        return jsonify({"status": "error", "message": str(exc)}), 500


@main.route("/api/analyze", methods=["POST"])
@login_required
def analyze():
    """Analyze a browser frame."""
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

        preferences = get_user_preferences(current_user.id)
        favorites = get_favorite_styles(current_user.id)

        result["recommended_hairstyles"] = apply_preferences_to_recommendations(
            result["recommended_hairstyles"],
            preferences,
        )
        result["recommended_hairstyles"] = annotate_favorites(
            result["recommended_hairstyles"],
            favorites,
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
    """Return history records."""
    limit = request.args.get("limit", default=20, type=int)
    recent = get_recent_predictions(user_id=current_user.id, limit=limit)
    return jsonify({"status": "ok", "records": recent}), 200


@main.route("/api/latest", methods=["GET"])
@login_required
def api_latest():
    """Return latest record."""
    latest = get_latest_prediction(user_id=current_user.id)
    return jsonify({"status": "ok", "latest": latest}), 200


@main.route("/api/preferences", methods=["POST"])
@login_required
def save_preferences():
    """Save preferences."""
    data = request.get_json(silent=True) or {}
    preferences = {
        "hair_length": data.get("hair_length", "any"),
        "hair_texture": data.get("hair_texture", "any"),
        "maintenance_level": data.get("maintenance_level", "any"),
    }
    update_user_preferences(current_user.id, preferences)
    return jsonify({"status": "ok", "preferences": preferences}), 200


@main.route("/api/favorites", methods=["POST"])
@login_required
def update_favorites():
    """Add or remove a favorite style."""
    data = request.get_json(silent=True) or {}
    action = data.get("action")
    name = data.get("name")
    category = data.get("category")
    face_shape = data.get("face_shape")
    barber_notes = data.get("barber_notes", "")

    if not action or not name or not category:
        return jsonify({"status": "error", "message": "Missing favorite fields"}), 400

    if action == "add":
        add_favorite_style(
            current_user.id,
            {
                "name": name,
                "category": category,
                "face_shape": face_shape,
                "barber_notes": barber_notes,
            },
        )
    elif action == "remove":
        remove_favorite_style(current_user.id, name, category)
    else:
        return jsonify({"status": "error", "message": "Invalid action"}), 400

    return jsonify({"status": "ok"}), 200
