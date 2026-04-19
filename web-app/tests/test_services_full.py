from unittest.mock import patch
import pytest

from app.services import (
    apply_preferences_to_recommendations,
    annotate_favorites,
    fetch_dashboard_summary,
)


# -----------------------------
# APPLY PREFERENCES (FULL)
# -----------------------------

def test_apply_preferences_multiple_matches():
    recs = {
        "male": [
            {"name": "a", "lengths": ["short"], "textures": ["straight"], "maintenance": "low"},
            {"name": "b", "lengths": ["short"], "textures": ["straight"], "maintenance": "low"},
            {"name": "c", "lengths": ["short"], "textures": ["straight"], "maintenance": "low"},
        ],
        "female": []
    }

    prefs = {
        "hair_length": "short",
        "hair_texture": "straight",
        "maintenance_level": "low"
    }

    result = apply_preferences_to_recommendations(recs, prefs)

    assert len(result["male"]) == 3


def test_apply_preferences_one_match():
    recs = {
        "male": [
            {"name": "a", "lengths": ["short"], "textures": ["straight"], "maintenance": "low"},
            {"name": "b", "lengths": ["long"], "textures": ["wavy"], "maintenance": "high"},
        ],
        "female": []
    }

    prefs = {
        "hair_length": "short",
        "hair_texture": "straight",
        "maintenance_level": "low"
    }

    result = apply_preferences_to_recommendations(recs, prefs)

    assert result["male"][0]["name"] == "a"
    assert len(result["male"]) >= 1


def test_apply_preferences_no_matches():
    recs = {
        "male": [
            {"name": "x", "lengths": ["long"], "textures": ["wavy"], "maintenance": "high"},
            {"name": "y", "lengths": ["long"], "textures": ["wavy"], "maintenance": "high"},
        ],
        "female": []
    }

    prefs = {
        "hair_length": "short",
        "hair_texture": "straight",
        "maintenance_level": "low"
    }

    result = apply_preferences_to_recommendations(recs, prefs)

    # fallback behavior
    assert result["male"] == recs["male"][:3]


# -----------------------------
# ANNOTATE FAVORITES (FULL)
# -----------------------------

def test_annotate_favorites_true():
    recs = {
        "male": [{"name": "fade"}],
        "female": []
    }

    favs = [{"name": "fade", "category": "male"}]

    result = annotate_favorites(recs, favs)

    assert result["male"][0]["favorited"] is True


def test_annotate_favorites_false():
    recs = {
        "male": [{"name": "buzz"}],
        "female": []
    }

    favs = [{"name": "fade", "category": "male"}]

    result = annotate_favorites(recs, favs)

    assert result["male"][0]["favorited"] is False


def test_annotate_multiple_items():
    recs = {
        "male": [{"name": "fade"}, {"name": "buzz"}],
        "female": [{"name": "bob"}]
    }

    favs = [
        {"name": "fade", "category": "male"},
        {"name": "bob", "category": "female"}
    ]

    result = annotate_favorites(recs, favs)

    assert result["male"][0]["favorited"] is True
    assert result["male"][1]["favorited"] is False
    assert result["female"][0]["favorited"] is True


# -----------------------------
# DASHBOARD SUMMARY (BIG COVERAGE)
# -----------------------------

@patch("app.services.get_latest_prediction")
@patch("app.services.get_face_shape_counts")
@patch("app.services.get_recent_predictions")
@patch("app.services.get_total_scans")
@patch("app.services.get_user_preferences")
@patch("app.services.get_favorite_styles")
def test_fetch_dashboard_summary(
    mock_favs,
    mock_prefs,
    mock_total,
    mock_recent,
    mock_counts,
    mock_latest,
):
    mock_latest.return_value = {"latest": True}
    mock_counts.return_value = {"oval": 5}
    mock_recent.return_value = [{"r": 1}]
    mock_total.return_value = 10
    mock_prefs.return_value = {"hair_length": "short"}
    mock_favs.return_value = [{"name": "fade"}]

    result = fetch_dashboard_summary("user123")

    assert result["latest"] == {"latest": True}
    assert result["counts"] == {"oval": 5}
    assert result["recent"] == [{"r": 1}]
    assert result["total_scans"] == 10
    assert result["preferences"] == {"hair_length": "short"}
    assert result["favorites"] == [{"name": "fade"}]