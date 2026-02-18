"""Tests for export API endpoints"""
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_export_resume_pdf():
    """Test PDF export"""
    request_data = {
        "content": "<h1>John Doe</h1><p>Software Engineer</p>",
        "name": "John Doe",
        "format": "pdf"
    }

    response = client.post("/api/export/resume", json=request_data)

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert "John_Doe" in response.headers["content-disposition"]


def test_export_resume_docx():
    """Test DOCX export"""
    request_data = {
        "content": "<h1>John Doe</h1><p>Software Engineer</p>",
        "name": "John Doe",
        "format": "docx"
    }

    response = client.post("/api/export/resume", json=request_data)

    assert response.status_code == 200
    assert "officedocument" in response.headers["content-type"]
    assert "John_Doe" in response.headers["content-disposition"]


def test_export_report():
    """Test score report export"""
    request_data = {
        "resumeData": {"contact": {"name": "John Doe"}},
        "scoreData": {"overall_score": 80, "mode": "ats_simulation"},
        "mode": "ats_simulation",
        "role": "software_engineer",
        "level": "senior"
    }

    response = client.post("/api/export/report", json=request_data)

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
