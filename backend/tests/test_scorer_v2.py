"""
Tests for adaptive scorer with dual-mode scoring.
"""
import pytest
from services.scorer_v2 import AdaptiveScorer
from services.parser import ResumeData
from services.role_taxonomy import ExperienceLevel


@pytest.fixture
def sample_resume():
    return ResumeData(
        fileName="test.pdf",
        contact={"name": "John Doe", "email": "john@example.com", "phone": "+1-555-0100"},
        experience=[{
            "title": "Senior Software Engineer",
            "company": "Tech Corp",
            "description": """
            - Led team of 5 engineers building microservices with Python and AWS
            - Reduced deployment time by 60% through CI/CD automation
            - Implemented Kubernetes orchestration
            """
        }],
        education=[{"degree": "BS Computer Science", "institution": "Stanford"}],
        skills=["Python", "AWS", "Docker", "Kubernetes", "React"],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 450, "hasPhoto": False, "fileFormat": "pdf"}
    )


@pytest.fixture
def scorer():
    return AdaptiveScorer()


def test_ats_mode_triggered_with_jd(scorer, sample_resume):
    """Test that ATS Simulation mode is triggered when JD is provided"""
    job_description = """
    Required: Python, AWS, Docker, Kubernetes
    Preferred: React, TypeScript
    """

    result = scorer.score(
        sample_resume,
        role_id="software_engineer",
        level=ExperienceLevel.SENIOR,
        job_description=job_description,
        mode="auto"
    )

    assert result["mode"] == "ats_simulation"
    assert "breakdown" in result
    assert "keyword_details" in result
    assert "overall_score" in result


def test_quality_mode_triggered_without_jd(scorer, sample_resume):
    """Test that Quality Coach mode is triggered when no JD provided"""
    result = scorer.score(
        sample_resume,
        role_id="software_engineer",
        level=ExperienceLevel.SENIOR,
        job_description=None,
        mode="auto"
    )

    assert result["mode"] == "quality_coach"
    assert "breakdown" in result
    assert "keyword_details" in result
    assert "overall_score" in result
    assert "cta" in result


def test_ats_keyword_matching(scorer, sample_resume):
    """Test that ATS mode correctly matches keywords with synonyms"""
    job_description = """
    Required: Python, AWS, Docker, Kubernetes, microservices
    Preferred: React, TypeScript, CI/CD
    """

    result = scorer.score(
        sample_resume,
        role_id="software_engineer",
        level=ExperienceLevel.SENIOR,
        job_description=job_description,
        mode="auto"
    )

    assert result["mode"] == "ats_simulation"

    # Check keyword matching details
    keyword_details = result["keyword_details"]
    assert "required_matched" in keyword_details
    assert "required_total" in keyword_details
    assert "preferred_matched" in keyword_details
    assert "preferred_total" in keyword_details

    # Python, AWS, Docker, Kubernetes should be matched (in resume)
    assert keyword_details["required_matched"] >= 4

    # Score breakdown should have keyword_match, format, and structure
    breakdown = result["breakdown"]
    assert "keyword_match" in breakdown
    assert "format" in breakdown
    assert "structure" in breakdown
