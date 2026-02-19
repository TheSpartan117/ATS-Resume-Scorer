import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_create_editor_session():
    """Test creating a new editor session"""
    response = client.post("/api/editor/session", json={
        "resume_id": "test_123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
    assert "working_docx_url" in data
    assert "sections" in data
    assert "current_score" in data
    assert "suggestions" in data

def test_create_editor_session_with_suggestions():
    """Test that session includes generated suggestions"""
    response = client.post("/api/editor/session", json={
        "resume_id": "test_123",
        "role": "software_engineer",
        "level": "mid"
    })

    assert response.status_code == 200
    data = response.json()
    assert "suggestions" in data
    assert isinstance(data["suggestions"], list)
    # Should have at least some suggestions from the sample resume
    assert len(data["suggestions"]) > 0
    # Each suggestion should have required fields
    if len(data["suggestions"]) > 0:
        sug = data["suggestions"][0]
        assert "id" in sug
        assert "type" in sug
        assert "severity" in sug
        assert "title" in sug
        assert "description" in sug

def test_get_editor_session():
    """Test retrieving existing session"""
    # First create session
    create_response = client.post("/api/editor/session", json={
        "resume_id": "test_456",
        "role": "software_engineer",
        "level": "mid"
    })
    assert create_response.status_code == 200
    session_id = create_response.json()["session_id"]

    # Now get it
    response = client.get(f"/api/editor/session/{session_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["session_id"] == session_id
    assert "suggestions" in data
    assert "current_score" in data
    assert "sections" in data
    assert "working_docx_url" in data

def test_get_nonexistent_session():
    """Test retrieving a session that doesn't exist"""
    response = client.get("/api/editor/session/nonexistent-id")
    assert response.status_code == 404
    assert "detail" in response.json()
