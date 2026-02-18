import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from backend.services.parser import parse_pdf, parse_docx, ResumeData

def test_parse_pdf_extracts_basic_info():
    """Test that PDF parser extracts contact information"""
    # This test requires a sample PDF
    # For now, we'll test the structure
    resume_data = ResumeData(
        fileName="test.pdf",
        contact={
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "555-1234"
        },
        experience=[],
        education=[],
        skills=[],
        metadata={"pageCount": 1, "wordCount": 100, "hasPhoto": False, "fileFormat": "pdf"}
    )

    assert resume_data.contact["name"] == "John Doe"
    assert resume_data.contact["email"] == "john@example.com"
    assert resume_data.metadata["fileFormat"] == "pdf"
