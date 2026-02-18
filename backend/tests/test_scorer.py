import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from backend.services.scorer import score_contact_info, score_keywords, score_content, score_length_density, score_industry_specific, score_role_specific, calculate_overall_score
from backend.services.parser import ResumeData
from backend.services.role_taxonomy import ExperienceLevel

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


# ROLE-SPECIFIC SCORING TESTS

def test_role_specific_software_engineer_mid():
    """Test role-specific scoring for mid-level software engineer"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={"name": "John Doe", "email": "john@example.com"},
        experience=[{"description": "Architected microservices platform using Python and AWS. Mentored 3 junior developers on CI/CD best practices."}],
        education=[{"degree": "BS Computer Science"}],
        skills=["Python", "AWS", "Docker", "CI/CD", "Microservices", "Mentoring"],
        metadata={"pageCount": 1, "wordCount": 500, "hasPhoto": False, "fileFormat": "pdf"}
    )

    result = score_role_specific(resume, "software_engineer", "mid")

    # Should score well: has required skills, mid-level keywords (architected, mentored), and some preferred sections
    assert result["score"] >= 12  # Out of 20 points
    assert "score" in result
    assert "issues" in result


def test_role_specific_product_manager_senior():
    """Test role-specific scoring for senior product manager"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={"name": "Jane Smith", "email": "jane@example.com"},
        experience=[{"description": "Drove product strategy for enterprise platform using data-driven decisions. Led cross-functional team of 12. Increased revenue by 45%. Established strategic partnerships with Fortune 500 clients. Product launches resulted in measurable impact on KPIs and go-to-market success."}],
        education=[{"degree": "MBA"}],
        skills=["Product Strategy", "Stakeholder Management", "Data Analysis", "KPIs", "Go-to-Market", "Revenue Growth", "Cross-functional Leadership"],
        metadata={"pageCount": 1, "wordCount": 600, "hasPhoto": False, "fileFormat": "pdf"}
    )

    result = score_role_specific(resume, "product_manager", "senior")

    # Should score well: has product strategy keywords, senior action verbs (drove, led, established), metrics
    assert result["score"] >= 10  # Out of 20 points (reasonable for mid-tier match)
    assert "score" in result
    assert "issues" in result


def test_role_specific_missing_required_skills():
    """Test role-specific scoring when missing required skills"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={"name": "Test User", "email": "test@example.com"},
        experience=[{"description": "Did some work on things"}],
        education=[],
        skills=[],
        metadata={"pageCount": 1, "wordCount": 400, "hasPhoto": False, "fileFormat": "pdf"}
    )

    result = score_role_specific(resume, "software_engineer", "entry")

    # Should have lower score and suggest missing required skills
    assert result["score"] < 10
    assert any("required skills" in issue[1].lower() for issue in result["issues"])


def test_role_specific_without_role_defaults():
    """Test role-specific scoring defaults when no role specified"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={"name": "Test User", "email": "test@example.com"},
        experience=[],
        education=[],
        skills=[],
        metadata={"pageCount": 1, "wordCount": 400, "hasPhoto": False, "fileFormat": "pdf"}
    )

    result = score_role_specific(resume, "", "")

    # Should give default score and suggest selecting role
    assert result["score"] == 10
    assert any("role" in issue[1].lower() and "experience level" in issue[1].lower() for issue in result["issues"])


def test_content_uses_role_specific_action_verbs():
    """Test that score_content uses role-specific action verbs when role provided"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={"name": "John Doe", "email": "john@example.com"},
        experience=[{"description": "- Spearheaded cloud migration initiative\n- Pioneered new architecture\n- Transformed development process"}],
        education=[],
        skills=[],
        metadata={"pageCount": 1, "wordCount": 500, "hasPhoto": False, "fileFormat": "pdf"}
    )

    # Senior-level action verbs for software engineer
    result = score_content(resume, "software_engineer", "senior")

    # Should recognize senior-level action verbs (spearheaded, pioneered, transformed)
    assert result["score"] >= 15  # Should score well with senior action verbs


def test_keywords_uses_role_typical_keywords():
    """Test that score_keywords uses typical_keywords from role when no JD provided"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={"name": "Jane Smith", "email": "jane@example.com"},
        experience=[{"description": "Product strategy roadmap kpis market research go-to-market prioritization analytics automation dashboards optimization"}],
        education=[],
        skills=["Product Strategy", "Analytics", "Roadmap", "KPIs", "Automation", "Optimization"],
        metadata={"pageCount": 1, "wordCount": 500, "hasPhoto": False, "fileFormat": "pdf"}
    )

    # Should use product manager mid-level keywords
    result = score_keywords(resume, "", "product_manager", "mid")

    # Should score based on role keywords, not just default (8 keywords out of 14 = 57% = 12 points)
    assert result["score"] >= 10  # Should be better than default
    assert "score" in result


def test_calculate_overall_score_with_role_and_level():
    """Test calculate_overall_score with role_id and level parameters"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={"name": "John Doe", "email": "john@example.com", "phone": "555-1234", "location": "SF"},
        experience=[{"description": "- Architected microservices using Python\n- Mentored 5 developers\n- Improved performance by 50%"}],
        education=[{"degree": "BS CS"}],
        skills=["Python", "AWS", "Docker", "Microservices"],
        metadata={"pageCount": 1, "wordCount": 500, "hasPhoto": False, "fileFormat": "pdf"}
    )

    result = calculate_overall_score(resume, "", "software_engineer", "mid")

    # Should calculate score using role-specific scoring
    assert "overallScore" in result
    assert "breakdown" in result
    assert "roleSpecific" in result["breakdown"]  # New breakdown category
    assert result["breakdown"]["roleSpecific"]["maxScore"] == 20
