import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from backend.services.scorer import score_contact_info, score_keywords, score_content, score_length_density, score_industry_specific
from backend.services.parser import ResumeData

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

def test_keywords_with_job_description():
    resume = ResumeData(
        fileName="test.pdf",
        contact={"name": "John", "email": "j@ex.com"},
        skills=["Python", "React", "AWS"],
        experience=[{"title": "Python developer", "company": "Tech Corp", "description": "React and AWS experience"}],
        education=[],
        metadata={"pageCount": 1, "wordCount": 500, "hasPhoto": False, "fileFormat": "pdf"}
    )

    jd = "Looking for Python developer with React and AWS experience"
    result = score_keywords(resume, jd)

    assert result["score"] > 10  # Should have good match

def test_keywords_without_job_description():
    resume = ResumeData(
        fileName="test.pdf",
        contact={"name": "John"},
        experience=[],
        education=[],
        skills=[],
        metadata={"pageCount": 1, "wordCount": 500, "hasPhoto": False, "fileFormat": "pdf"}
    )

    result = score_keywords(resume)
    assert result["score"] == 10  # Default score
    assert any("job description" in issue[1].lower() for issue in result["issues"])

def test_content_with_action_verbs_and_numbers():
    resume = ResumeData(
        fileName="test.pdf",
        contact={"name": "John"},
        experience=[{"description": "- Led team of 10 engineers\n- Increased productivity by 40%\n- Managed $2M budget\n- Developed 5 products"}],
        education=[],
        skills=[],
        metadata={"pageCount": 1, "wordCount": 500, "hasPhoto": False, "fileFormat": "pdf"}
    )

    result = score_content(resume)
    # Should score well: all bullets start with verbs (6pts), all quantified (6pts), structure (5pts), no passive (3pts), professional (3pts), no buzzwords (2pts) = 25pts
    assert result["score"] >= 20  # Should score very well with strong verbs and metrics

def test_length_density_optimal():
    resume = ResumeData(
        fileName="test.pdf",
        contact={"name": "John"},
        experience=[],
        education=[],
        skills=[],
        metadata={"pageCount": 1, "wordCount": 500, "hasPhoto": False, "fileFormat": "pdf"}
    )

    result = score_length_density(resume)
    assert result["score"] == 10  # Perfect score for 1 page, 500 words

def test_industry_tech_role():
    resume = ResumeData(
        fileName="test.pdf",
        contact={"name": "John", "website": "github.com/john"},
        experience=[{"text": "Developed React apps with Python backend using AWS and Docker"}],
        education=[],
        skills=["Python", "React", "AWS", "Docker", "Kubernetes", "SQL"],
        metadata={"pageCount": 1, "wordCount": 500, "hasPhoto": False, "fileFormat": "pdf"}
    )

    result = score_industry_specific(resume, "tech")
    assert result["score"] >= 15  # Should score well with skills and tech keywords
