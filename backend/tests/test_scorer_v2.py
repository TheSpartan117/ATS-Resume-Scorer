"""
Tests for adaptive scorer with dual-mode scoring and main orchestrator.
"""
import pytest
from services.scorer_v2 import AdaptiveScorer, ResumeScorer
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
    assert "overallScore" in result


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
    assert "overallScore" in result
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


# ===== ResumeScorer Tests =====

@pytest.fixture
def resume_scorer():
    """Fixture for ResumeScorer instance"""
    return ResumeScorer()


def test_resume_scorer_ats_mode(resume_scorer, sample_resume):
    """Test ResumeScorer in ATS mode"""
    job_description = """
    Required: Python, AWS, Docker, Kubernetes
    Preferred: React, TypeScript
    """

    result = resume_scorer.score(
        resume=sample_resume,
        role="software_engineer",
        level=ExperienceLevel.SENIOR,
        mode='ats',
        job_description=job_description
    )

    # Check return structure
    assert 'score' in result
    assert 'mode' in result
    assert 'interpretation' in result
    assert 'breakdown' in result
    assert 'recommendations' in result
    assert 'issues' in result
    assert 'strengths' in result
    assert 'keyword_details' in result

    # Check values
    assert result['mode'] == 'ats'
    assert isinstance(result['score'], (int, float))
    assert 0 <= result['score'] <= 100
    assert result['interpretation'] in [
        "Needs significant improvement",
        "Needs improvement",
        "Good",
        "Very good",
        "Excellent"
    ]


def test_resume_scorer_quality_mode(resume_scorer, sample_resume):
    """Test ResumeScorer in Quality mode"""
    result = resume_scorer.score(
        resume=sample_resume,
        role="software_engineer",
        level=ExperienceLevel.SENIOR,
        mode='quality'
    )

    # Check return structure
    assert 'score' in result
    assert 'mode' in result
    assert 'interpretation' in result
    assert 'breakdown' in result
    assert 'recommendations' in result
    assert 'issues' in result
    assert 'strengths' in result
    assert 'keyword_details' in result

    # Check values
    assert result['mode'] == 'quality'
    assert isinstance(result['score'], (int, float))
    assert 0 <= result['score'] <= 100
    assert result['interpretation'] in [
        "Needs significant improvement",
        "Needs improvement",
        "Good",
        "Very good",
        "Excellent"
    ]


def test_score_interpretation_ranges(resume_scorer):
    """Test score interpretation for different ranges"""
    assert resume_scorer._interpret_score(95) == "Excellent"
    assert resume_scorer._interpret_score(86) == "Excellent"
    assert resume_scorer._interpret_score(85) == "Very good"
    assert resume_scorer._interpret_score(76) == "Very good"
    assert resume_scorer._interpret_score(75) == "Good"
    assert resume_scorer._interpret_score(61) == "Good"
    assert resume_scorer._interpret_score(60) == "Needs improvement"
    assert resume_scorer._interpret_score(41) == "Needs improvement"
    assert resume_scorer._interpret_score(40) == "Needs significant improvement"
    assert resume_scorer._interpret_score(0) == "Needs significant improvement"


def test_recommendations_generated(resume_scorer, sample_resume):
    """Test that recommendations are generated"""
    job_description = """
    Required: Python, AWS, Docker, Kubernetes, Machine Learning
    Preferred: React, TypeScript, GraphQL
    """

    result = resume_scorer.score(
        resume=sample_resume,
        role="software_engineer",
        level=ExperienceLevel.SENIOR,
        mode='ats',
        job_description=job_description
    )

    # Should have recommendations
    assert 'recommendations' in result
    assert isinstance(result['recommendations'], list)
    assert len(result['recommendations']) > 0
    assert len(result['recommendations']) <= 7  # Capped at 7


def test_ats_mode_requires_job_description(resume_scorer, sample_resume):
    """Test that ATS mode requires job description"""
    with pytest.raises(ValueError, match="job_description is required"):
        resume_scorer.score(
            resume=sample_resume,
            role="software_engineer",
            level=ExperienceLevel.SENIOR,
            mode='ats'
        )


def test_invalid_mode_raises_error(resume_scorer, sample_resume):
    """Test that invalid mode raises ValueError"""
    with pytest.raises(ValueError, match="Invalid mode"):
        resume_scorer.score(
            resume=sample_resume,
            role="software_engineer",
            level=ExperienceLevel.SENIOR,
            mode='invalid_mode'
        )


def test_cache_functionality(resume_scorer):
    """Test cache storage and retrieval"""
    test_hash = "abc123"
    test_data = {"validation": "results"}

    # Cache data
    resume_scorer.cache_validation_results(test_hash, test_data)

    # Retrieve cached data
    cached = resume_scorer.get_cached_validation(test_hash)
    assert cached == test_data

    # Non-existent cache returns None
    assert resume_scorer.get_cached_validation("nonexistent") is None

    # Clear cache
    resume_scorer.clear_cache()
    assert resume_scorer.get_cached_validation(test_hash) is None


def test_mode_switching_seamless(resume_scorer, sample_resume):
    """Test that mode switching works seamlessly"""
    job_description = """
    Required: Python, AWS, Docker
    Preferred: React
    """

    # Score in ATS mode
    ats_result = resume_scorer.score(
        resume=sample_resume,
        role="software_engineer",
        level=ExperienceLevel.SENIOR,
        mode='ats',
        job_description=job_description
    )

    # Score in Quality mode (without JD)
    quality_result = resume_scorer.score(
        resume=sample_resume,
        role="software_engineer",
        level=ExperienceLevel.SENIOR,
        mode='quality'
    )

    # Both should complete successfully
    assert ats_result['mode'] == 'ats'
    assert quality_result['mode'] == 'quality'

    # Both should have valid scores
    assert 0 <= ats_result['score'] <= 100
    assert 0 <= quality_result['score'] <= 100


def test_breakdown_structure_ats(resume_scorer, sample_resume):
    """Test breakdown structure in ATS mode"""
    job_description = "Required: Python, AWS"

    result = resume_scorer.score(
        resume=sample_resume,
        role="software_engineer",
        level=ExperienceLevel.SENIOR,
        mode='ats',
        job_description=job_description
    )

    breakdown = result['breakdown']
    assert 'keyword_match' in breakdown
    assert 'format' in breakdown
    assert 'structure' in breakdown

    # Each category should have score and maxScore
    for category in breakdown.values():
        assert 'score' in category
        assert 'maxScore' in category
        assert 'issues' in category


def test_breakdown_structure_quality(resume_scorer, sample_resume):
    """Test breakdown structure in Quality mode"""
    result = resume_scorer.score(
        resume=sample_resume,
        role="software_engineer",
        level=ExperienceLevel.SENIOR,
        mode='quality'
    )

    breakdown = result['breakdown']
    assert 'role_keywords' in breakdown
    assert 'content_quality' in breakdown
    assert 'format' in breakdown
    assert 'professional_polish' in breakdown

    # Each category should have score and maxScore
    for category in breakdown.values():
        assert 'score' in category
        assert 'maxScore' in category
        assert 'issues' in category


def test_issues_categorized(resume_scorer, sample_resume):
    """Test that issues are properly categorized"""
    job_description = "Required: Python"

    result = resume_scorer.score(
        resume=sample_resume,
        role="software_engineer",
        level=ExperienceLevel.SENIOR,
        mode='ats',
        job_description=job_description
    )

    issues = result['issues']
    assert 'critical' in issues
    assert 'warnings' in issues
    assert 'suggestions' in issues
    assert 'info' in issues

    # Each should be a list
    assert isinstance(issues['critical'], list)
    assert isinstance(issues['warnings'], list)
    assert isinstance(issues['suggestions'], list)
    assert isinstance(issues['info'], list)


def test_strengths_identified(resume_scorer, sample_resume):
    """Test that strengths are identified"""
    job_description = """
    Required: Python, AWS, Docker, Kubernetes
    Preferred: React
    """

    result = resume_scorer.score(
        resume=sample_resume,
        role="software_engineer",
        level=ExperienceLevel.SENIOR,
        mode='ats',
        job_description=job_description
    )

    # Should have strengths list
    assert 'strengths' in result
    assert isinstance(result['strengths'], list)


def test_recommendations_actionable(resume_scorer, sample_resume):
    """Test that recommendations are actionable strings"""
    job_description = """
    Required: Python, AWS, Docker, Kubernetes, Machine Learning, Data Science
    Preferred: React, TypeScript, GraphQL, Node.js
    """

    result = resume_scorer.score(
        resume=sample_resume,
        role="software_engineer",
        level=ExperienceLevel.SENIOR,
        mode='ats',
        job_description=job_description
    )

    recommendations = result['recommendations']

    # Should be non-empty strings
    for rec in recommendations:
        assert isinstance(rec, str)
        assert len(rec) > 0

    # Should have keywords like "Add", "Include", "Improve", "CRITICAL", "WARNING", "TIP"
    rec_text = ' '.join(recommendations)
    assert any(keyword in rec_text for keyword in [
        'Add', 'Include', 'Improve', 'CRITICAL', 'WARNING', 'TIP', 'missing', 'more'
    ])
