import pytest
from services.scorer import score_contact_info
from services.parser import ResumeData

def test_complete_contact_info_gets_full_score():
    """Test that complete contact info receives 10/10 points"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "555-1234",
            "location": "San Francisco, CA",
            "linkedin": "linkedin.com/in/johndoe",
            "website": None
        },
        experience=[],
        education=[],
        skills=[],
        metadata={"pageCount": 1, "wordCount": 500, "hasPhoto": False, "fileFormat": "pdf"}
    )

    result = score_contact_info(resume)

    assert result["score"] == 10
    assert len(result["issues"]) == 0

def test_missing_email_reduces_score():
    """Test that missing email is flagged as critical issue"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={
            "name": "John Doe",
            "email": None,
            "phone": "555-1234",
            "location": "San Francisco, CA",
            "linkedin": None,
            "website": None
        },
        experience=[],
        education=[],
        skills=[],
        metadata={"pageCount": 1, "wordCount": 500, "hasPhoto": False, "fileFormat": "pdf"}
    )

    result = score_contact_info(resume)

    assert result["score"] < 10
    assert any("email" in issue[1].lower() for issue in result["issues"])
    assert any(issue[0] == "critical" for issue in result["issues"])
