"""Tests for services."""

# pylint: disable=too-many-arguments,too-many-positional-arguments

from unittest.mock import MagicMock, patch

import requests

from app.services import (
    annotate_favorites,
    apply_preferences_to_recommendations,
    fetch_dashboard_summary,
    submit_frame_for_analysis,
)


def test_submit_frame_for_analysis():
    """Submit frame posts to ML client."""
    mock_response = MagicMock()
    mock_response.json.return_value = {"status": "ok"}
    mock_response.raise_for_status.return_value = None

    with patch("app.services.requests.post", return_value=mock_response) as mock_post:
        result = submit_frame_for_analysis(
            "http://localhost:5001",
            "fake-image",
            "session-123",
            "user-123",
        )

    assert result == {"status": "ok"}
    mock_post.assert_called_once_with(
        "http://localhost:5001/analyze",
        json={
            "session_id": "session-123",
            "user_id": "user-123",
            "image_b64": "fake-image",
        },
        timeout=15,
    )


def test_submit_frame_for_analysis_raises_for_http_error():
    """Submit frame propagates request errors."""
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = requests.HTTPError("bad request")

    with patch("app.services.requests.post", return_value=mock_response):
        try:
            submit_frame_for_analysis(
                "http://localhost:5001",
                "fake-image",
                "session-123",
                "user-123",
            )
            assert False
        except requests.HTTPError:
            assert True


def test_apply_preferences_to_recommendations_filters():
    """Recommendations are filtered by preferences."""
    recommendations = {
        "male": [
            {
                "name": "Classic side part",
                "lengths": ["short"],
                "textures": ["straight"],
                "maintenance": "low",
                "barber_notes": "notes",
            },
            {
                "name": "Pompadour",
                "lengths": ["medium"],
                "textures": ["wavy"],
                "maintenance": "high",
                "barber_notes": "notes",
            },
        ],
        "female": [
            {
                "name": "Shoulder-length lob",
                "lengths": ["medium"],
                "textures": ["straight"],
                "maintenance": "low",
                "barber_notes": "notes",
            }
        ],
    }

    preferences = {
        "hair_length": "short",
        "hair_texture": "straight",
        "maintenance_level": "low",
    }

    result = apply_preferences_to_recommendations(recommendations, preferences)

    assert result["male"][0]["name"] == "Classic side part"
    assert len(result["female"]) == 1


def test_apply_preferences_to_recommendations_one_match_branch():
    """One match branch keeps one match plus remainder."""
    recommendations = {
        "male": [
            {
                "name": "Classic side part",
                "lengths": ["short"],
                "textures": ["straight"],
                "maintenance": "low",
                "barber_notes": "notes",
            },
            {
                "name": "Pompadour",
                "lengths": ["medium"],
                "textures": ["wavy"],
                "maintenance": "high",
                "barber_notes": "notes",
            },
            {
                "name": "Textured crop",
                "lengths": ["short"],
                "textures": ["curly"],
                "maintenance": "medium",
                "barber_notes": "notes",
            },
        ],
        "female": [],
    }

    preferences = {
        "hair_length": "short",
        "hair_texture": "straight",
        "maintenance_level": "low",
    }

    result = apply_preferences_to_recommendations(recommendations, preferences)

    assert len(result["male"]) == 3
    assert result["male"][0]["name"] == "Classic side part"


def test_apply_preferences_to_recommendations_no_match_branch():
    """No match branch falls back to first options."""
    recommendations = {
        "male": [
            {
                "name": "Classic side part",
                "lengths": ["short"],
                "textures": ["straight"],
                "maintenance": "low",
                "barber_notes": "notes",
            },
            {
                "name": "Pompadour",
                "lengths": ["medium"],
                "textures": ["wavy"],
                "maintenance": "high",
                "barber_notes": "notes",
            },
        ],
        "female": [],
    }

    preferences = {
        "hair_length": "long",
        "hair_texture": "coily",
        "maintenance_level": "high",
    }

    result = apply_preferences_to_recommendations(recommendations, preferences)

    assert result["male"][0]["name"] == "Classic side part"
    assert result["male"][1]["name"] == "Pompadour"


def test_annotate_favorites_marks_saved():
    """Favorites are annotated on styles."""
    recommendations = {
        "male": [
            {
                "name": "Classic side part",
                "lengths": [],
                "textures": [],
                "maintenance": "low",
                "barber_notes": "notes",
            }
        ],
        "female": [],
    }
    favorites = [{"name": "Classic side part", "category": "male"}]

    result = annotate_favorites(recommendations, favorites)

    assert result["male"][0]["favorited"] is True
    assert result["male"][0]["category"] == "male"


@patch("app.services.get_face_shape_counts")
@patch("app.services.get_favorite_styles")
@patch("app.services.get_latest_prediction")
@patch("app.services.get_recent_predictions")
@patch("app.services.get_total_scans")
@patch("app.services.get_user_preferences")
def test_fetch_dashboard_summary(
    mock_get_user_preferences,
    mock_get_total_scans,
    mock_get_recent_predictions,
    mock_get_latest_prediction,
    mock_get_favorite_styles,
    mock_get_face_shape_counts,
):
    """Dashboard summary aggregates expected values."""
    mock_get_latest_prediction.return_value = {"face_shape": "Oval"}
    mock_get_face_shape_counts.return_value = {"Oval": 4}
    mock_get_recent_predictions.return_value = [{"face_shape": "Oval"}]
    mock_get_total_scans.return_value = 4
    mock_get_user_preferences.return_value = {"hair_length": "short"}
    mock_get_favorite_styles.return_value = [{"name": "Pompadour"}]

    result = fetch_dashboard_summary("10")

    assert result["latest"]["face_shape"] == "Oval"
    assert result["counts"] == {"Oval": 4}
    assert result["recent"] == [{"face_shape": "Oval"}]
    assert result["total_scans"] == 4
    assert result["preferences"] == {"hair_length": "short"}
    assert result["favorites"] == [{"name": "Pompadour"}]
