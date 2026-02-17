"""
Integration tests for the complete ATS Resume Scorer pipeline.
Tests the full scoring workflow from ResumeData through all scoring categories.
"""
import pytest
from services.parser import ResumeData
from services.scorer import calculate_overall_score


def test_complete_scoring_integration():
    """Test full scoring pipeline with realistic resume"""
    resume = ResumeData(
        fileName="senior_engineer.pdf",
        contact={
            "name": "Jane Developer",
            "email": "jane@example.com",
            "phone": "555-1234",
            "location": "San Francisco, CA",
            "linkedin": "linkedin.com/in/jane",
            "website": "github.com/jane"
        },
        experience=[{
            "text": "Led team of 10 engineers, developed 5 React applications, " +
                   "increased performance by 40%, managed $2M cloud infrastructure budget"
        }],
        education=[{"degree": "BS Computer Science"}],
        skills=["Python", "React", "AWS", "Docker", "Kubernetes"],
        metadata={
            "pageCount": 1,
            "wordCount": 550,
            "hasPhoto": False,
            "fileFormat": "pdf"
        }
    )

    jd = "Senior Software Engineer with Python, React, and AWS experience"
    result = calculate_overall_score(resume, jd, "tech")

    # Should score well across all categories
    assert result["overallScore"] >= 70, f"Overall score {result['overallScore']} should be >= 70"
    assert result["breakdown"]["contactInfo"]["score"] == 10  # Perfect contact
    assert result["breakdown"]["formatting"]["score"] >= 15  # Good formatting
    assert result["breakdown"]["keywords"]["score"] >= 5  # Decent keyword match
    assert result["breakdown"]["content"]["score"] >= 15  # Action verbs and numbers
    assert result["breakdown"]["lengthDensity"]["score"] >= 8  # Good length
    assert result["breakdown"]["industrySpecific"]["score"] >= 15  # Tech role match


def test_poor_resume_scoring():
    """Test scoring on resume with issues"""
    resume = ResumeData(
        fileName="poor.pdf",
        contact={"name": "John"},  # Missing email, phone
        experience=[],
        education=[],
        skills=[],
        metadata={"pageCount": 3, "wordCount": 200, "hasPhoto": True, "fileFormat": "pdf"}
    )

    result = calculate_overall_score(resume)

    # Should have low score and many issues
    assert result["overallScore"] < 50, f"Overall score {result['overallScore']} should be < 50"
    assert len(result["issues"]["critical"]) > 0
    assert len(result["issues"]["warnings"]) > 0

    # Verify specific low scores
    assert result["breakdown"]["contactInfo"]["score"] < 5  # Missing critical info
    assert result["breakdown"]["formatting"]["score"] < 15  # Poor formatting (3 pages, photo)
    assert result["breakdown"]["content"]["score"] < 15  # No meaningful content
