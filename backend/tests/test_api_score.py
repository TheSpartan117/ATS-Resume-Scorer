"""Tests for score endpoint"""
import pytest


def test_score_with_updated_resume_data(client):
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


def test_score_requires_resume_data(client):
    """Test score endpoint requires resume data"""
    response = client.post("/api/score", json={})

    assert response.status_code == 422  # Validation error


def test_score_auto_mode_with_jd_uses_ats(client):
    """Test auto mode with job description uses ATS mode"""
    resume_data = {
        "fileName": "resume.pdf",
        "contact": {"name": "John Doe", "email": "john@example.com"},
        "experience": [{"text": "Python developer with 5 years experience"}],
        "education": [{"degree": "BS Computer Science"}],
        "skills": ["Python", "AWS"],
        "metadata": {"pageCount": 1, "wordCount": 400, "hasPhoto": False, "fileFormat": "pdf"},
        "jobDescription": "Looking for Python developer with AWS experience",
        "role": "software_engineer",
        "level": "mid",
        "mode": "auto"
    }

    response = client.post("/api/score", json=resume_data)

    assert response.status_code == 200
    data = response.json()
    assert data["mode"] == "ats_simulation"
    assert "keywordDetails" in data


def test_score_auto_mode_without_jd_uses_quality(client):
    """Test auto mode without job description uses Quality mode"""
    resume_data = {
        "fileName": "resume.pdf",
        "contact": {"name": "Jane Smith", "email": "jane@example.com"},
        "experience": [{"text": "Developed 10+ applications"}],
        "education": [{"degree": "BS Computer Science"}],
        "skills": ["JavaScript", "React"],
        "metadata": {"pageCount": 1, "wordCount": 500, "hasPhoto": False, "fileFormat": "pdf"},
        "role": "software_engineer",
        "level": "mid",
        "mode": "auto"
    }

    response = client.post("/api/score", json=resume_data)

    assert response.status_code == 200
    data = response.json()
    assert data["mode"] == "quality_coach"


def test_score_explicit_ats_mode(client):
    """Test explicit ATS mode parameter"""
    resume_data = {
        "fileName": "resume.pdf",
        "contact": {"name": "John Doe", "email": "john@example.com"},
        "experience": [{"text": "Python developer"}],
        "education": [{"degree": "BS CS"}],
        "skills": ["Python"],
        "metadata": {"pageCount": 1, "wordCount": 400, "hasPhoto": False, "fileFormat": "pdf"},
        "jobDescription": "Python developer needed",
        "role": "software_engineer",
        "level": "mid",
        "mode": "ats"
    }

    response = client.post("/api/score", json=resume_data)

    assert response.status_code == 200
    data = response.json()
    assert data["mode"] == "ats_simulation"
    assert "breakdown" in data
    # ATS mode should have keyword_match category
    assert "keyword_match" in data["breakdown"]


def test_score_explicit_quality_mode(client):
    """Test explicit Quality mode parameter"""
    resume_data = {
        "fileName": "resume.pdf",
        "contact": {"name": "Jane Smith", "email": "jane@example.com"},
        "experience": [{"text": "Led development team"}],
        "education": [{"degree": "BS CS"}],
        "skills": ["Leadership"],
        "metadata": {"pageCount": 1, "wordCount": 500, "hasPhoto": False, "fileFormat": "pdf"},
        "role": "software_engineer",
        "level": "senior",
        "mode": "quality"
    }

    response = client.post("/api/score", json=resume_data)

    assert response.status_code == 200
    data = response.json()
    assert data["mode"] == "quality_coach"
    assert "breakdown" in data
    # Quality mode should have role_keywords, content_quality, professional_polish
    assert "role_keywords" in data["breakdown"]
    assert "content_quality" in data["breakdown"]
    assert "professional_polish" in data["breakdown"]


def test_score_response_includes_issue_counts(client):
    """Test response includes issue counts"""
    resume_data = {
        "fileName": "resume.pdf",
        "contact": {"name": "Test User", "email": "test@example.com"},
        "experience": [{"text": "Software engineer"}],
        "education": [{"degree": "BS"}],
        "skills": ["Python"],
        "metadata": {"pageCount": 1, "wordCount": 300, "hasPhoto": False, "fileFormat": "pdf"},
        "role": "software_engineer",
        "level": "mid"
    }

    response = client.post("/api/score", json=resume_data)

    assert response.status_code == 200
    data = response.json()
    assert "issueCounts" in data
    assert "critical" in data["issueCounts"]
    assert "warnings" in data["issueCounts"]
    assert "suggestions" in data["issueCounts"]
    assert isinstance(data["issueCounts"]["critical"], int)
    assert isinstance(data["issueCounts"]["warnings"], int)
    assert isinstance(data["issueCounts"]["suggestions"], int)


def test_score_mode_backward_compatibility(client):
    """Test backward compatibility - mode is optional"""
    resume_data = {
        "fileName": "resume.pdf",
        "contact": {"name": "John Doe", "email": "john@example.com"},
        "experience": [{"text": "Developer"}],
        "education": [{"degree": "BS"}],
        "skills": ["Python"],
        "metadata": {"pageCount": 1, "wordCount": 400, "hasPhoto": False, "fileFormat": "pdf"},
        "role": "software_engineer",
        "level": "mid"
        # No mode parameter - should auto-detect
    }

    response = client.post("/api/score", json=resume_data)

    assert response.status_code == 200
    data = response.json()
    # Should default to quality_coach without JD
    assert data["mode"] == "quality_coach"
