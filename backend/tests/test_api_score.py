"""Tests for score endpoint"""
import pytest
from fastapi.testclient import TestClient
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from main import app


client = TestClient(app)


def test_score_with_updated_resume_data():
    """Test re-scoring with updated resume data"""
    resume_data = {
        "fileName": "updated_resume.pdf",
        "contact": {
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "555-1234",
            "location": "San Francisco, CA"
        },
        "experience": [
            {"text": "Led team of 10 engineers, developed 5 applications"}
        ],
        "education": [
            {"degree": "BS Computer Science"}
        ],
        "skills": ["Python", "React", "AWS"],
        "metadata": {
            "pageCount": 1,
            "wordCount": 500,
            "hasPhoto": False,
            "fileFormat": "pdf"
        },
        "jobDescription": "Python developer",
        "industry": "tech"
    }

    response = client.post("/api/score", json=resume_data)

    assert response.status_code == 200
    data = response.json()

    assert "overallScore" in data
    assert "breakdown" in data
    assert data["overallScore"] >= 0
    assert data["overallScore"] <= 100


def test_score_requires_resume_data():
    """Test score endpoint requires resume data"""
    response = client.post("/api/score", json={})

    assert response.status_code == 422  # Validation error
