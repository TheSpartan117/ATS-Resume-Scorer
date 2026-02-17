"""Tests for upload endpoint"""
import pytest
from fastapi.testclient import TestClient
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from main import app
import io
import fitz  # PyMuPDF


client = TestClient(app)


def create_test_pdf():
    """Create a minimal valid PDF with resume content"""
    doc = fitz.open()  # Create new PDF
    page = doc.new_page()  # Add a page

    # Add resume text
    text = """
    John Doe
    john.doe@example.com
    (555) 123-4567
    San Francisco, CA
    linkedin.com/in/johndoe

    EXPERIENCE
    Senior Software Engineer
    Tech Company - San Francisco, CA
    January 2020 - Present
    - Led team of 5 engineers to develop React applications
    - Increased system performance by 40%
    - Managed $1M cloud infrastructure budget
    - Built and deployed 10+ microservices using Python and Docker

    EDUCATION
    Bachelor of Science in Computer Science
    University of California - Berkeley, CA
    Graduated: 2015

    SKILLS
    Python, JavaScript, React, AWS, Docker, Kubernetes, SQL
    """

    page.insert_text((72, 72), text)

    # Save to bytes
    pdf_bytes = doc.tobytes()
    doc.close()

    return pdf_bytes


def test_upload_pdf_returns_score():
    """Test uploading a PDF resume returns a score"""
    pdf_content = create_test_pdf()
    files = {"file": ("test_resume.pdf", io.BytesIO(pdf_content), "application/pdf")}

    response = client.post("/api/upload", files=files)

    assert response.status_code == 200
    data = response.json()

    # Verify response structure
    assert "fileName" in data
    assert "contact" in data
    assert "metadata" in data
    assert "score" in data
    assert "uploadedAt" in data

    # Verify score structure
    assert "overallScore" in data["score"]
    assert "breakdown" in data["score"]
    assert "issues" in data["score"]


def test_upload_invalid_file_type_returns_400():
    """Test uploading non-PDF/DOCX file returns 400"""
    txt_content = b"This is a text file"
    files = {"file": ("test.txt", io.BytesIO(txt_content), "text/plain")}

    response = client.post("/api/upload", files=files)

    assert response.status_code == 400
    assert "PDF or DOCX only" in response.json()["detail"]


def test_upload_file_too_large_returns_400():
    """Test uploading file >10MB returns 400"""
    # Create 11MB file
    large_content = b"x" * (11 * 1024 * 1024)
    files = {"file": ("large.pdf", io.BytesIO(large_content), "application/pdf")}

    response = client.post("/api/upload", files=files)

    assert response.status_code == 400
    assert "too large" in response.json()["detail"].lower()


def test_upload_with_job_description():
    """Test upload with optional job description for keyword matching"""
    pdf_content = create_test_pdf()
    files = {"file": ("test.pdf", io.BytesIO(pdf_content), "application/pdf")}
    data = {"jobDescription": "Looking for Python developer"}

    response = client.post("/api/upload", files=files, data=data)

    assert response.status_code == 200
    # Score should use job description for keyword matching
    assert response.json()["score"]["overallScore"] >= 0
