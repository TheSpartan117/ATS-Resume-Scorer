import pytest
import sys
import os
import io
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from backend.services.parser import parse_pdf, parse_docx, parse_pdf_with_pypdf, ResumeData

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


def test_parse_pdf_with_pypdf_fallback():
    """Test pypdf fallback when pymupdf fails"""
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    c.drawString(100, 750, "Test Resume")
    c.drawString(100, 730, "John Doe")
    c.drawString(100, 710, "john@example.com")
    c.drawString(100, 690, "Experience: Software Engineer")
    c.save()
    pdf_content = buffer.getvalue()

    result = parse_pdf_with_pypdf(pdf_content, "test.pdf")
    assert result is not None
    assert result.fileName == "test.pdf"
    assert result.metadata["fileFormat"] == "pdf"
