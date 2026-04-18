"""Service-layer tests for the web application."""

# pylint: disable=duplicate-code

from unittest.mock import Mock, patch

import pytest
import requests

from app.services import fetch_dashboard_summary, submit_frame_for_analysis


def test_submit_frame_for_analysis_success():
    """Test successful submission of a frame to the ML client."""
    mock_response = Mock()
    mock_response.json.return_value = {
        "status": "ok",
        "face_detected": True,
        "face_shape": "Oval",
        "confidence": 0.95,
        "recommended_hairstyles": [
            "Textured quiff",
            "Classic side part",
            "Layered medium cut",
        ],
    }
    mock_response.raise_for_status.return_value = None

    with patch("app.services.requests.post", return_value=mock_response) as mock_post:
        result = submit_frame_for_analysis(
            "http://localhost:5001",
            "fake-image-data",
            "session-123",
            "user-123",
        )

    mock_post.assert_called_once_with(
        "http://localhost:5001/analyze",
        json={
            "session_id": "session-123",
            "user_id": "user-123",
            "image_b64": "fake-image-data",
        },
        timeout=15,
    )
    assert result["status"] == "ok"
    assert result["face_shape"] == "Oval"


def test_submit_frame_for_analysis_http_error():
    """Test that HTTP errors from the ML client are raised."""
    mock_response = Mock()
    mock_response.raise_for_status.side_effect = requests.HTTPError("boom")

    with patch("app.services.requests.post", return_value=mock_response):
        with pytest.raises(requests.HTTPError):
            submit_frame_for_analysis(
                "http://localhost:5001",
                "fake-image-data",
                "session-123",
                "user-123",
            )


def test_fetch_dashboard_summary():
    """Test dashboard summary aggregation for a specific user."""
    latest = {
        "_id": "1",
        "face_detected": True,
        "face_shape": "Oval",
        "confidence": 0.92,
        "recommended_hairstyles": [
            "Textured quiff",
            "Classic side part",
            "Layered medium cut",
        ],
        "timestamp": "2026-04-13T20:00:00Z",
    }
    counts = {
        "Oval": 3,
        "Round": 1,
    }
    recent = [
        {"_id": "1", "face_shape": "Oval"},
        {"_id": "2", "face_shape": "Round"},
    ]

    with patch(
        "app.services.get_latest_prediction", return_value=latest
    ) as mock_latest, patch(
        "app.services.get_face_shape_counts", return_value=counts
    ) as mock_counts, patch(
        "app.services.get_recent_predictions", return_value=recent
    ) as mock_recent, patch(
        "app.services.get_total_scans", return_value=4
    ) as mock_total:
        summary = fetch_dashboard_summary("user-123")

    mock_latest.assert_called_once_with(user_id="user-123")
    mock_counts.assert_called_once_with(user_id="user-123")
    mock_recent.assert_called_once_with(user_id="user-123", limit=10)
    mock_total.assert_called_once_with(user_id="user-123")

    assert summary["latest"] == latest
    assert summary["counts"] == counts
    assert summary["recent"] == recent
    assert summary["total_scans"] == 4
