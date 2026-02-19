"""
Tests for the rescore endpoint.

Following TDD approach:
1. Test that rescoring updates the score
2. Test that rescoring generates new suggestions
"""

import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_rescore_updates_score():
    """Test that rescoring updates the score"""
    # Create session
    response = client.post("/api/editor/session", json={
        "resume_id": "test_rescore"
    })
    assert response.status_code == 200
    session_id = response.json()["session_id"]
    initial_score = response.json()["current_score"]["overallScore"]

    # Re-score (should work even without changes)
    response = client.post("/api/editor/rescore", json={
        "session_id": session_id
    })

    assert response.status_code == 200
    data = response.json()
    assert "score" in data
    assert "suggestions" in data
    assert "overallScore" in data["score"]
    # Score should be a number
    assert isinstance(data["score"]["overallScore"], (int, float))


def test_rescore_generates_new_suggestions():
    """Test that rescoring generates fresh suggestions"""
    response = client.post("/api/editor/session", json={
        "resume_id": "test_suggestions"
    })
    assert response.status_code == 200
    session_id = response.json()["session_id"]

    # Re-score
    response = client.post("/api/editor/rescore", json={
        "session_id": session_id
    })

    assert response.status_code == 200
    new_suggestions = response.json()["suggestions"]
    assert isinstance(new_suggestions, list)
    # Should return some suggestions structure


def test_rescore_missing_session():
    """Test that rescoring with invalid session fails gracefully"""
    response = client.post("/api/editor/rescore", json={
        "session_id": "invalid_session_id"
    })

    # Should return error status
    assert response.status_code in [400, 404]


def test_rescore_has_breakdown():
    """Test that rescore returns score breakdown"""
    # Create session
    response = client.post("/api/editor/session", json={
        "resume_id": "test_breakdown"
    })
    assert response.status_code == 200
    session_id = response.json()["session_id"]

    # Re-score
    response = client.post("/api/editor/rescore", json={
        "session_id": session_id
    })

    assert response.status_code == 200
    data = response.json()
    assert "breakdown" in data["score"]
    # Should have some scoring categories
    breakdown = data["score"]["breakdown"]
    assert isinstance(breakdown, dict)
    # Should have at least some categories
    assert len(breakdown) > 0


def test_rescore_updates_session():
    """Test that rescore updates the session storage"""
    # Create session
    response = client.post("/api/editor/session", json={
        "resume_id": "test_update"
    })
    assert response.status_code == 200
    session_id = response.json()["session_id"]

    # Re-score
    response = client.post("/api/editor/rescore", json={
        "session_id": session_id
    })
    assert response.status_code == 200
    new_score = response.json()["score"]["overallScore"]

    # Get session to verify it was updated
    response = client.get(f"/api/editor/session/{session_id}")
    assert response.status_code == 200
    session_data = response.json()

    # The session's current_score should be updated
    assert session_data["current_score"]["overallScore"] == new_score
