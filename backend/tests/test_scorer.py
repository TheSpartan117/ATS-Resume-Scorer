import pytest
from services.scorer import score_contact_info, score_keywords, score_content, score_length_density
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
        experience=[{"text": "Led team of 10 engineers, increased productivity by 40%, managed $2M budget, developed 5 products"}],
        education=[],
        skills=[],
        metadata={"pageCount": 1, "wordCount": 500, "hasPhoto": False, "fileFormat": "pdf"}
    )

    result = score_content(resume)
    assert result["score"] > 15  # Should score well with verbs and numbers

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
