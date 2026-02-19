"""
Tests for apply-suggestion endpoint.

Tests all 4 action types:
1. add_phone - Add phone number to contact section
2. replace_text - Replace weak action verbs
3. add_section - Add missing sections (Skills, Projects, etc.)
4. show_location - Just navigate to location (no-op for API)
"""

import pytest
from fastapi.testclient import TestClient
from backend.main import app
from docx import Document
import json
import io

client = TestClient(app)


def test_apply_add_phone_suggestion():
    """Test adding phone number to contact section"""
    # Create test session with DOCX
    response = client.post("/api/editor/session", json={
        "resume_id": "test_phone"
    })
    session_id = response.json()["session_id"]

    # Apply add_phone suggestion
    response = client.post("/api/editor/apply-suggestion", json={
        "session_id": session_id,
        "suggestion_id": "sug_001",
        "action": "add_phone",
        "value": "(555) 867-5309"
    })

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "updated_section" in data
    assert "content" in data
    assert "(555) 867-5309" in data["content"]


def test_apply_replace_text_suggestion():
    """Test replacing weak action verb"""
    # Create test session
    response = client.post("/api/editor/session", json={
        "resume_id": "test_replace"
    })
    session_id = response.json()["session_id"]

    # Apply replace_text suggestion
    response = client.post("/api/editor/apply-suggestion", json={
        "session_id": session_id,
        "suggestion_id": "sug_002",
        "action": "replace_text",
        "value": json.dumps({
            "current_text": "Responsible for managing team",
            "suggested_text": "Led cross-functional team",
            "para_idx": 3
        })
    })

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "Led cross-functional team" in data["content"]


def test_apply_add_section_suggestion():
    """Test adding missing Skills section"""
    # Create test session
    response = client.post("/api/editor/session", json={
        "resume_id": "test_section"
    })
    session_id = response.json()["session_id"]

    # Apply add_section suggestion
    response = client.post("/api/editor/apply-suggestion", json={
        "session_id": session_id,
        "suggestion_id": "sug_003",
        "action": "add_section",
        "value": "Skills\n- Python, FastAPI, React\n- Team Leadership"
    })

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "Skills" in data["updated_section"]
    assert "Python" in data["content"]


def test_apply_show_location_suggestion():
    """Test show_location action (navigation only)"""
    # Create test session
    response = client.post("/api/editor/session", json={
        "resume_id": "test_location"
    })
    session_id = response.json()["session_id"]

    # Apply show_location suggestion
    response = client.post("/api/editor/apply-suggestion", json={
        "session_id": session_id,
        "suggestion_id": "sug_004",
        "action": "show_location",
        "value": None
    })

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    # show_location is a no-op, so content should be empty
    assert data["content"] == ""


def test_apply_suggestion_invalid_session():
    """Test error handling for invalid session"""
    response = client.post("/api/editor/apply-suggestion", json={
        "session_id": "invalid_session_id",
        "suggestion_id": "sug_001",
        "action": "add_phone",
        "value": "(555) 123-4567"
    })

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_apply_suggestion_invalid_action():
    """Test error handling for invalid action type"""
    # Create test session
    response = client.post("/api/editor/session", json={
        "resume_id": "test_invalid"
    })
    session_id = response.json()["session_id"]

    # Apply invalid action
    response = client.post("/api/editor/apply-suggestion", json={
        "session_id": session_id,
        "suggestion_id": "sug_999",
        "action": "invalid_action",
        "value": "test"
    })

    assert response.status_code == 400
    assert "unknown action" in response.json()["detail"].lower()


def test_apply_replace_text_invalid_json():
    """Test error handling for invalid JSON in replace_text"""
    # Create test session
    response = client.post("/api/editor/session", json={
        "resume_id": "test_json"
    })
    session_id = response.json()["session_id"]

    # Apply replace_text with invalid JSON
    response = client.post("/api/editor/apply-suggestion", json={
        "session_id": session_id,
        "suggestion_id": "sug_005",
        "action": "replace_text",
        "value": "not valid json"
    })

    assert response.status_code == 400
    assert "invalid" in response.json()["detail"].lower()


def test_apply_add_section_no_content():
    """Test error handling for add_section with no content"""
    # Create test session
    response = client.post("/api/editor/session", json={
        "resume_id": "test_empty"
    })
    session_id = response.json()["session_id"]

    # Apply add_section with no content
    response = client.post("/api/editor/apply-suggestion", json={
        "session_id": session_id,
        "suggestion_id": "sug_006",
        "action": "add_section",
        "value": ""
    })

    assert response.status_code == 400
    assert "no section content" in response.json()["detail"].lower()
