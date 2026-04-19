"""Tests for label mapper."""

from app.label_mapper import (
    FACE_SHAPE_RECOMMENDATIONS,
    get_hairstyle_recommendations,
    normalize_face_shape,
)


def test_normalize_face_shape_supported():
    """Supported shape is returned unchanged."""
    assert normalize_face_shape("Oval") == "Oval"


def test_normalize_face_shape_unknown():
    """Unknown shape falls back to Unknown."""
    assert normalize_face_shape("Hexagon") == "Unknown"


def test_get_hairstyle_recommendations_supported_shape():
    """Recommendations returned for supported shape."""
    result = get_hairstyle_recommendations("Round")

    assert "male" in result
    assert "female" in result
    assert len(result["male"]) >= 1
    assert len(result["female"]) >= 1


def test_get_hairstyle_recommendations_unknown_shape():
    """Unknown shape uses Unknown recommendations."""
    result = get_hairstyle_recommendations("Hexagon")

    assert result == FACE_SHAPE_RECOMMENDATIONS["Unknown"]


def test_recommendation_entries_have_expected_keys():
    """Recommendation entries have expected fields."""
    result = get_hairstyle_recommendations("Oval")
    style = result["male"][0]

    assert "name" in style
    assert "lengths" in style
    assert "textures" in style
    assert "maintenance" in style
    assert "barber_notes" in style
