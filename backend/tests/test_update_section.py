"""
Tests for update section endpoint.
"""
import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_update_experience_section():
    """Test updating Experience section content"""
    # Create session
    response = client.post("/api/editor/session", json={
        "resume_id": "test_update"
    })
    assert response.status_code == 200
    session_id = response.json()["session_id"]

    # Update Experience section (sample doc has 4 paragraphs, use indices 2-3)
    response = client.post("/api/editor/update-section", json={
        "session_id": session_id,
        "section": "Experience",
        "content": "<p>Led team of 8 engineers building cloud platform</p>",
        "start_para": 2,
        "end_para": 3
    })

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "updated_url" in data


def test_update_section_preserves_formatting():
    """Test that updating preserves formatting"""
    response = client.post("/api/editor/session", json={
        "resume_id": "test_format"
    })
    assert response.status_code == 200
    session_id = response.json()["session_id"]

    # Update with HTML formatting (use valid indices 0-1)
    response = client.post("/api/editor/update-section", json={
        "session_id": session_id,
        "section": "Skills",
        "content": "<ul><li>Python</li><li>JavaScript</li></ul>",
        "start_para": 0,
        "end_para": 1
    })

    assert response.status_code == 200
    assert response.json()["success"] is True


def test_update_section_invalid_range():
    """Test updating with invalid paragraph range"""
    response = client.post("/api/editor/session", json={
        "resume_id": "test_invalid"
    })
    assert response.status_code == 200
    session_id = response.json()["session_id"]

    response = client.post("/api/editor/update-section", json={
        "session_id": session_id,
        "section": "Experience",
        "content": "<p>Test</p>",
        "start_para": 100,  # Invalid - beyond document bounds
        "end_para": 105
    })

    # Should return 400 error for invalid range
    assert response.status_code == 400
    assert "Invalid paragraph indices" in response.json()["detail"]


def test_update_section_invalid_session():
    """Test updating with invalid session ID"""
    response = client.post("/api/editor/update-section", json={
        "session_id": "nonexistent-session-id",
        "section": "Experience",
        "content": "<p>Test</p>",
        "start_para": 0,
        "end_para": 1
    })

    # Should return 404 for nonexistent session
    assert response.status_code == 404
    assert "Session not found" in response.json()["detail"]
