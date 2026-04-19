"""Service helpers for the web app."""

import requests

from app.db import (
    get_face_shape_counts,
    get_favorite_styles,
    get_latest_prediction,
    get_recent_predictions,
    get_total_scans,
    get_user_preferences,
)


def submit_frame_for_analysis(ml_client_url, image_b64, session_id, user_id):
    """Send a frame to the ML client."""
    response = requests.post(
        f"{ml_client_url}/analyze",
        json={
            "session_id": session_id,
            "user_id": user_id,
            "image_b64": image_b64,
        },
        timeout=15,
    )
    response.raise_for_status()
    return response.json()


def _matches_preferences(style, preferences):
    hair_length = preferences.get("hair_length", "any")
    hair_texture = preferences.get("hair_texture", "any")
    maintenance_level = preferences.get("maintenance_level", "any")

    if hair_length != "any" and hair_length not in style.get("lengths", []):
        return False

    if hair_texture != "any" and hair_texture not in style.get("textures", []):
        return False

    if maintenance_level != "any" and maintenance_level != style.get("maintenance"):
        return False

    return True


def apply_preferences_to_recommendations(recommendations, preferences):
    """Filter recommendations by user preferences."""
    filtered = {"male": [], "female": []}

    for category in ("male", "female"):
        options = recommendations.get(category, [])
        matches = [
            style for style in options if _matches_preferences(style, preferences)
        ]

        if len(matches) >= 2:
            filtered[category] = matches[:3]
        elif len(matches) == 1:
            remainder = [
                style for style in options if style["name"] != matches[0]["name"]
            ]
            filtered[category] = (matches + remainder)[:3]
        else:
            filtered[category] = options[:3]

    return filtered


def _favorite_keys(favorites):
    return {f"{item.get('category', '')}:{item.get('name', '')}" for item in favorites}


def annotate_favorites(recommendations, favorites):
    """Mark recommendations that are already favorited."""
    keys = _favorite_keys(favorites)
    annotated = {"male": [], "female": []}

    for category in ("male", "female"):
        for style in recommendations.get(category, []):
            item = dict(style)
            item["favorited"] = f"{category}:{style['name']}" in keys
            item["category"] = category
            annotated[category].append(item)

    return annotated


def fetch_dashboard_summary(user_id):
    """Build dashboard summary."""
    latest = get_latest_prediction(user_id=user_id)
    counts = get_face_shape_counts(user_id=user_id)
    recent = get_recent_predictions(user_id=user_id, limit=10)
    total_scans = get_total_scans(user_id=user_id)
    preferences = get_user_preferences(user_id)
    favorites = get_favorite_styles(user_id)

    return {
        "latest": latest,
        "counts": counts,
        "recent": recent,
        "total_scans": total_scans,
        "preferences": preferences,
        "favorites": favorites,
    }
