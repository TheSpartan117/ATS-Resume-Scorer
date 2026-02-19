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
