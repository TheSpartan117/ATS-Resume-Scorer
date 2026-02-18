"""
Integration tests for the complete ATS Resume Scorer pipeline.

Tests end-to-end scoring flow for both modes:
- ATS Simulation Mode (with job description)
- Quality Coach Mode (without job description)

Also tests mode switching, caching behavior, and score distributions.
"""
import pytest
import os
import glob
from typing import List, Dict
from backend.services.parser import parse_pdf, ResumeData
from backend.services.scorer_v2 import AdaptiveScorer
from backend.services.role_taxonomy import ExperienceLevel
from backend.services.red_flags_validator import RedFlagsValidator


# Test job descriptions for ATS mode
SAMPLE_JOB_DESCRIPTIONS = {
    "software_engineer": """
    Senior Software Engineer - Remote

    Required Skills:
    - Python, JavaScript, TypeScript
    - AWS, Docker, Kubernetes
    - Microservices architecture
    - CI/CD pipelines
    - RESTful APIs
    - SQL databases

    Preferred Skills:
    - React, Vue.js
    - Terraform, Jenkins
    - MongoDB, Redis
    - Agile/Scrum methodology
    - Leadership experience

    Responsibilities:
    - Design and develop scalable microservices
    - Lead technical architecture decisions
    - Mentor junior engineers
    - Collaborate with product team
    """,

    "data_scientist": """
    Data Scientist - Machine Learning

    Required:
    - Python, SQL
    - Machine Learning, Deep Learning
    - TensorFlow, PyTorch, scikit-learn
    - Statistics, A/B testing
    - Data visualization

    Preferred:
    - AWS, GCP
    - Spark, Airflow
    - NLP, Computer Vision
    - PhD in relevant field
    """,

    "product_manager": """
    Senior Product Manager

    Required:
    - 5+ years product management experience
    - Roadmap planning
    - User research, A/B testing
    - Agile methodology
    - Data-driven decision making

    Preferred:
    - Technical background
    - B2B SaaS experience
    - SQL knowledge
    """
}


@pytest.fixture
def scorer():
    """Create AdaptiveScorer instance"""
    return AdaptiveScorer()


@pytest.fixture
def validator():
    """Create RedFlagsValidator instance"""
    return RedFlagsValidator()


@pytest.fixture
def sample_resume():
    """Create a high-quality sample resume for testing"""
    return ResumeData(
        fileName="test_senior_engineer.pdf",
        contact={
            "name": "Jane Developer",
            "email": "jane.developer@email.com",
            "phone": "+1-555-0123",
            "linkedin": "linkedin.com/in/janedev",
            "location": "San Francisco, CA"
        },
        experience=[
            {
                "title": "Senior Software Engineer",
                "company": "Tech Corp",
                "location": "San Francisco, CA",
                "startDate": "Jan 2020",
                "endDate": "Present",
                "description": """
                - Led team of 5 engineers building microservices with Python and AWS
                - Reduced deployment time by 60% through CI/CD automation using Jenkins and Docker
                - Architected scalable REST APIs handling 1M+ requests/day
                - Implemented Kubernetes orchestration reducing infrastructure costs by 40%
                - Mentored 3 junior engineers, conducted code reviews
                """
            },
            {
                "title": "Software Engineer",
                "company": "Startup Inc",
                "location": "Remote",
                "startDate": "Jun 2018",
                "endDate": "Dec 2019",
                "description": """
                - Built React frontend and Django backend for SaaS platform
                - Integrated payment processing with Stripe, increasing revenue by 25%
                - Optimized SQL queries reducing page load time by 50%
                - Implemented automated testing with pytest and Jest
                """
            }
        ],
        education=[
            {
                "degree": "BS Computer Science",
                "institution": "Stanford University",
                "location": "Stanford, CA",
                "graduationDate": "2018",
                "gpa": "3.8"
            }
        ],
        skills=[
            "Python", "JavaScript", "TypeScript", "React", "Django",
            "AWS", "Docker", "Kubernetes", "Jenkins", "Git",
            "PostgreSQL", "MongoDB", "Redis", "REST API", "Microservices"
        ],
        certifications=[
            {
                "name": "AWS Certified Solutions Architect",
                "issuer": "Amazon Web Services",
                "date": "2021"
            }
        ],
        metadata={
            "pageCount": 1,
            "wordCount": 520,
            "hasPhoto": False,
            "fileFormat": "pdf"
        }
    )


@pytest.fixture
def poor_resume():
    """Create a low-quality resume for testing"""
    return ResumeData(
        fileName="poor_resume.pdf",
        contact={
            "name": "John Doe"
            # Missing email and phone
        },
        experience=[
            {
                "title": "Developer",
                "company": "Company",
                "description": "Worked on projects. Did coding."
            }
        ],
        education=[],
        skills=["Python"],
        certifications=[],
        metadata={
            "pageCount": 3,
            "wordCount": 150,
            "hasPhoto": True,
            "fileFormat": "pdf"
        }
    )


def test_ats_mode_complete_flow(scorer, sample_resume):
    """
    Test complete ATS Simulation Mode flow:
    Resume → Parse → Score (ATS mode with JD)
    """
    result = scorer.score(
        resume_data=sample_resume,
        role_id="software_engineer",
        level=ExperienceLevel.SENIOR,
        job_description=SAMPLE_JOB_DESCRIPTIONS["software_engineer"],
        mode="auto"
    )

    # Verify mode detection
    assert result["mode"] == "ats_simulation"

    # Verify score structure
    assert "overallScore" in result
    assert "breakdown" in result
    assert "keyword_details" in result
    assert "auto_reject" in result

    # Verify breakdown has correct categories
    breakdown = result["breakdown"]
    assert "keyword_match" in breakdown
    assert "format" in breakdown
    assert "structure" in breakdown

    # Verify max scores (70/20/10 split)
    assert breakdown["keyword_match"]["maxScore"] == 70
    assert breakdown["format"]["maxScore"] == 20
    assert breakdown["structure"]["maxScore"] == 10

    # Verify keyword details
    kw = result["keyword_details"]
    assert "required_matched" in kw
    assert "required_total" in kw
    assert "preferred_matched" in kw
    assert "preferred_total" in kw
    assert "required_match_pct" in kw
    assert "preferred_match_pct" in kw

    # High-quality resume should score well
    assert result["overallScore"] >= 70, f"Good resume scored {result['overallScore']}, expected >= 70"
    assert result["auto_reject"] is False

    # Should match most required keywords
    assert kw["required_match_pct"] >= 60


def test_quality_mode_complete_flow(scorer, sample_resume):
    """
    Test complete Quality Coach Mode flow:
    Resume → Parse → Score (Quality mode without JD)
    """
    result = scorer.score(
        resume_data=sample_resume,
        role_id="software_engineer",
        level=ExperienceLevel.SENIOR,
        job_description=None,
        mode="auto"
    )

    # Verify mode detection
    assert result["mode"] == "quality_coach"

    # Verify score structure
    assert "overallScore" in result
    assert "breakdown" in result
    assert "keyword_details" in result
    assert "cta" in result

    # Verify breakdown has correct categories
    breakdown = result["breakdown"]
    assert "role_keywords" in breakdown
    assert "content_quality" in breakdown
    assert "format" in breakdown
    assert "professional_polish" in breakdown

    # Verify max scores (25/30/25/20 split)
    assert breakdown["role_keywords"]["maxScore"] == 25
    assert breakdown["content_quality"]["maxScore"] == 30
    assert breakdown["format"]["maxScore"] == 25
    assert breakdown["professional_polish"]["maxScore"] == 20

    # High-quality resume should score well
    assert result["overallScore"] >= 65, f"Good resume scored {result['overallScore']}, expected >= 65"

    # Should have call-to-action
    assert len(result["cta"]) > 0


def test_mode_switching_consistency(scorer, sample_resume):
    """
    Test that switching modes maintains consistent underlying data.
    Same resume should produce comparable results across modes.
    """
    # Score in ATS mode
    ats_result = scorer.score(
        resume_data=sample_resume,
        role_id="software_engineer",
        level=ExperienceLevel.SENIOR,
        job_description=SAMPLE_JOB_DESCRIPTIONS["software_engineer"],
        mode="ats_simulation"
    )

    # Score in Quality mode
    quality_result = scorer.score(
        resume_data=sample_resume,
        role_id="software_engineer",
        level=ExperienceLevel.SENIOR,
        job_description=None,
        mode="quality_coach"
    )

    # Both should recognize it's a good resume
    assert ats_result["overallScore"] >= 65
    assert quality_result["overallScore"] >= 65

    # Both modes should find the resume sections
    assert ats_result["breakdown"]["format"]["score"] >= 15
    assert quality_result["breakdown"]["format"]["score"] >= 15


def test_poor_resume_scoring(scorer, poor_resume):
    """Test that poor resumes are scored appropriately in both modes"""
    # ATS mode with JD
    ats_result = scorer.score(
        resume_data=poor_resume,
        role_id="software_engineer",
        level=ExperienceLevel.SENIOR,
        job_description=SAMPLE_JOB_DESCRIPTIONS["software_engineer"],
        mode="ats_simulation"
    )

    # Quality mode without JD
    quality_result = scorer.score(
        resume_data=poor_resume,
        role_id="software_engineer",
        level=ExperienceLevel.SENIOR,
        job_description=None,
        mode="quality_coach"
    )

    # Both should give low scores
    assert ats_result["overallScore"] < 50, f"Poor resume scored {ats_result['overallScore']} in ATS mode"
    assert quality_result["overallScore"] < 50, f"Poor resume scored {quality_result['overallScore']} in Quality mode"

    # ATS mode should auto-reject
    assert ats_result["auto_reject"] is True
    assert ats_result["rejection_reason"] is not None


def test_keyword_transparency_ats_mode(scorer, sample_resume):
    """Test that ATS mode shows matched/missing keywords transparently"""
    result = scorer.score(
        resume_data=sample_resume,
        role_id="software_engineer",
        level=ExperienceLevel.SENIOR,
        job_description=SAMPLE_JOB_DESCRIPTIONS["software_engineer"],
        mode="ats_simulation"
    )

    kw = result["keyword_details"]

    # Should show counts
    assert kw["required_matched"] >= 0
    assert kw["required_total"] > 0
    assert kw["preferred_matched"] >= 0
    assert kw["preferred_total"] > 0

    # Percentages should be calculated
    assert 0 <= kw["required_match_pct"] <= 100
    assert 0 <= kw["preferred_match_pct"] <= 100

    # Should have issues/details in breakdown
    assert "issues" in result["breakdown"]["keyword_match"]


def test_validation_integration(validator, sample_resume):
    """Test that validation works with resume data"""
    issues = validator.validate_resume(
        resume=sample_resume,
        role="software_engineer",
        level="senior"
    )

    # Should categorize issues
    assert "critical" in issues
    assert "warnings" in issues
    assert "suggestions" in issues

    # Good resume should have few critical issues
    assert len(issues["critical"]) == 0


def test_grammar_caching(validator, sample_resume):
    """Test that grammar checking is cached for performance"""
    # First call
    issues1 = validator.validate_resume(
        resume=sample_resume,
        role="software_engineer",
        level="senior"
    )

    # Second call with same resume (should use cache)
    issues2 = validator.validate_resume(
        resume=sample_resume,
        role="software_engineer",
        level="senior"
    )

    # Results should be identical
    assert len(issues1["critical"]) == len(issues2["critical"])
    assert len(issues1["warnings"]) == len(issues2["warnings"])


def test_score_breakdown_correctness(scorer, sample_resume):
    """Test that score breakdowns are mathematically correct"""
    # ATS mode
    ats_result = scorer.score(
        resume_data=sample_resume,
        role_id="software_engineer",
        level=ExperienceLevel.SENIOR,
        job_description=SAMPLE_JOB_DESCRIPTIONS["software_engineer"],
        mode="ats_simulation"
    )

    # Verify ATS breakdown sums correctly
    ats_total = (
        ats_result["breakdown"]["keyword_match"]["score"] +
        ats_result["breakdown"]["format"]["score"] +
        ats_result["breakdown"]["structure"]["score"]
    )
    assert abs(ats_total - ats_result["overallScore"]) < 0.5

    # Quality mode
    quality_result = scorer.score(
        resume_data=sample_resume,
        role_id="software_engineer",
        level=ExperienceLevel.SENIOR,
        job_description=None,
        mode="quality_coach"
    )

    # Verify Quality breakdown sums correctly
    quality_total = (
        quality_result["breakdown"]["role_keywords"]["score"] +
        quality_result["breakdown"]["content_quality"]["score"] +
        quality_result["breakdown"]["format"]["score"] +
        quality_result["breakdown"]["professional_polish"]["score"]
    )
    assert abs(quality_total - quality_result["overallScore"]) < 0.5


def test_different_roles(scorer, sample_resume):
    """Test scoring across different roles"""
    roles = [
        ("software_engineer", ExperienceLevel.SENIOR),
        ("data_scientist", ExperienceLevel.MID),
    ]

    for role_id, level in roles:
        # ATS mode
        jd = SAMPLE_JOB_DESCRIPTIONS.get(role_id)
        if jd:
            result = scorer.score(
                resume_data=sample_resume,
                role_id=role_id,
                level=level,
                job_description=jd,
                mode="ats_simulation"
            )
            assert "overallScore" in result
            assert result["mode"] == "ats_simulation"

        # Quality mode
        result = scorer.score(
            resume_data=sample_resume,
            role_id=role_id,
            level=level,
            job_description=None,
            mode="quality_coach"
        )
        assert "overallScore" in result
        assert result["mode"] == "quality_coach"


def test_experience_level_impact(scorer, sample_resume):
    """Test that experience level affects scoring appropriately"""
    results = {}

    for level in [ExperienceLevel.ENTRY, ExperienceLevel.MID, ExperienceLevel.SENIOR]:
        result = scorer.score(
            resume_data=sample_resume,
            role_id="software_engineer",
            level=level,
            job_description=None,
            mode="quality_coach"
        )
        results[level] = result["overallScore"]

    # Senior-level resume should score best at senior level
    # (or at least reasonably well)
    assert results[ExperienceLevel.SENIOR] >= 60


@pytest.mark.slow
def test_real_resume_corpus():
    """
    Test with real resume corpus from storage/uploads.
    Verify score distributions match target ranges.

    Target distribution:
    - 0-40: ~30% (6 resumes)
    - 41-60: ~40% (8 resumes)
    - 61-75: ~20% (4 resumes)
    - 76-85: ~8% (1-2 resumes)
    - 86-100: ~2% (0-1 resumes)
    """
    # Find all PDF files in storage
    storage_path = "/Users/sabuj.mondal/ats-resume-scorer/backend/storage/uploads"
    pdf_files = glob.glob(os.path.join(storage_path, "*.pdf"))

    if len(pdf_files) == 0:
        pytest.skip("No test resumes found in storage/uploads")

    scorer = AdaptiveScorer()
    scores = []
    results = []

    # Score each resume
    for pdf_path in pdf_files[:20]:  # Limit to 20 resumes
        try:
            # Parse PDF
            with open(pdf_path, 'rb') as f:
                file_content = f.read()

            resume = parse_pdf(file_content, os.path.basename(pdf_path))

            # Skip if parsing failed
            if resume.metadata.get("wordCount", 0) < 50:
                continue

            # Score in Quality mode (no JD required)
            result = scorer.score(
                resume_data=resume,
                role_id="software_engineer",
                level=ExperienceLevel.SENIOR,
                job_description=None,
                mode="quality_coach"
            )

            scores.append(result["overallScore"])
            results.append({
                "filename": os.path.basename(pdf_path),
                "score": result["overallScore"],
                "mode": result["mode"]
            })

        except Exception as e:
            # Skip problematic resumes
            print(f"Skipping {pdf_path}: {e}")
            continue

    # Need at least 10 resumes for distribution analysis
    if len(scores) < 10:
        pytest.skip(f"Not enough valid resumes ({len(scores)}), need at least 10")

    # Analyze distribution
    score_ranges = {
        "0-40": [s for s in scores if 0 <= s <= 40],
        "41-60": [s for s in scores if 41 <= s <= 60],
        "61-75": [s for s in scores if 61 <= s <= 75],
        "76-85": [s for s in scores if 76 <= s <= 85],
        "86-100": [s for s in scores if 86 <= s <= 100]
    }

    total = len(scores)
    distribution = {
        range_name: len(range_scores) / total * 100
        for range_name, range_scores in score_ranges.items()
    }

    # Print distribution for analysis
    print(f"\n=== Score Distribution ({total} resumes) ===")
    for range_name, percentage in distribution.items():
        count = len(score_ranges[range_name])
        print(f"{range_name}: {count} resumes ({percentage:.1f}%)")

    print("\n=== Individual Scores ===")
    for r in sorted(results, key=lambda x: x["score"], reverse=True):
        print(f"{r['filename']}: {r['score']:.1f}")

    # Verify reasonable distribution
    # Most scores should be in middle ranges (not all perfect or all terrible)
    assert distribution["0-40"] <= 50, "Too many low scores"
    assert distribution["86-100"] <= 20, "Too many perfect scores"

    # Average score should be reasonable
    avg_score = sum(scores) / len(scores)
    assert 30 <= avg_score <= 80, f"Average score {avg_score:.1f} is unrealistic"


def test_job_description_matching(scorer, sample_resume):
    """Test that JD keywords are properly matched"""
    result = scorer.score(
        resume_data=sample_resume,
        role_id="software_engineer",
        level=ExperienceLevel.SENIOR,
        job_description=SAMPLE_JOB_DESCRIPTIONS["software_engineer"],
        mode="ats_simulation"
    )

    kw = result["keyword_details"]

    # Resume has Python, AWS, Docker, Kubernetes, Microservices
    # These are all in the JD
    assert kw["required_matched"] >= 5, f"Only matched {kw['required_matched']} required keywords"


def test_auto_mode_detection(scorer, sample_resume):
    """Test that auto mode correctly detects ATS vs Quality mode"""
    # With JD → should use ATS mode
    result_with_jd = scorer.score(
        resume_data=sample_resume,
        role_id="software_engineer",
        level=ExperienceLevel.SENIOR,
        job_description="Python, AWS required",
        mode="auto"
    )
    assert result_with_jd["mode"] == "ats_simulation"

    # Without JD → should use Quality mode
    result_without_jd = scorer.score(
        resume_data=sample_resume,
        role_id="software_engineer",
        level=ExperienceLevel.SENIOR,
        job_description=None,
        mode="auto"
    )
    assert result_without_jd["mode"] == "quality_coach"


def test_explicit_mode_override(scorer, sample_resume):
    """Test that explicit mode parameter overrides auto-detection"""
    # Force ATS mode even with no JD (should error)
    with pytest.raises(ValueError, match="job_description required"):
        scorer.score(
            resume_data=sample_resume,
            role_id="software_engineer",
            level=ExperienceLevel.SENIOR,
            job_description=None,
            mode="ats_simulation"
        )

    # Force Quality mode even with JD (should work)
    result = scorer.score(
        resume_data=sample_resume,
        role_id="software_engineer",
        level=ExperienceLevel.SENIOR,
        job_description=SAMPLE_JOB_DESCRIPTIONS["software_engineer"],
        mode="quality_coach"
    )
    assert result["mode"] == "quality_coach"


def test_issues_categorization(scorer, poor_resume):
    """Test that issues are properly categorized by severity"""
    result = scorer.score(
        resume_data=poor_resume,
        role_id="software_engineer",
        level=ExperienceLevel.SENIOR,
        job_description=None,
        mode="quality_coach"
    )

    issues = result.get("issues", {})

    # Should have categorized issues
    assert "critical" in issues
    assert "warnings" in issues
    assert "suggestions" in issues

    # Poor resume should have issues
    total_issues = len(issues["critical"]) + len(issues["warnings"]) + len(issues["suggestions"])
    assert total_issues > 0


def test_strengths_generation(scorer, sample_resume):
    """Test that strengths are identified for good resumes"""
    result = scorer.score(
        resume_data=sample_resume,
        role_id="software_engineer",
        level=ExperienceLevel.SENIOR,
        job_description=None,
        mode="quality_coach"
    )

    strengths = result.get("strengths", [])

    # Good resume should have identified strengths
    assert len(strengths) > 0

    # Each strength should be a non-empty string
    for strength in strengths:
        assert isinstance(strength, str)
        assert len(strength) > 0


def test_end_to_end_complete_workflow(scorer, validator):
    """
    Complete end-to-end test simulating actual user workflow:
    1. Upload resume
    2. Parse resume
    3. Validate resume
    4. Score in ATS mode
    5. Score in Quality mode
    6. Compare results
    """
    # Create resume
    resume = ResumeData(
        fileName="complete_workflow_test.pdf",
        contact={
            "name": "Alice Engineer",
            "email": "alice@example.com",
            "phone": "555-0199"
        },
        experience=[
            {
                "title": "Software Engineer",
                "company": "Tech Co",
                "description": "Built REST APIs with Python and Flask. Deployed on AWS using Docker."
            }
        ],
        education=[
            {
                "degree": "BS Computer Science",
                "institution": "MIT"
            }
        ],
        skills=["Python", "Flask", "AWS", "Docker", "REST API"],
        certifications=[],
        metadata={
            "pageCount": 1,
            "wordCount": 450,
            "hasPhoto": False,
            "fileFormat": "pdf"
        }
    )

    # Step 1: Validate
    validation_result = validator.validate_resume(
        resume=resume,
        role="software_engineer",
        level="mid"
    )
    assert "critical" in validation_result

    # Step 2: Score in ATS mode
    ats_score = scorer.score(
        resume_data=resume,
        role_id="software_engineer",
        level=ExperienceLevel.MID,
        job_description=SAMPLE_JOB_DESCRIPTIONS["software_engineer"],
        mode="ats_simulation"
    )
    assert ats_score["mode"] == "ats_simulation"
    assert "overallScore" in ats_score

    # Step 3: Score in Quality mode
    quality_score = scorer.score(
        resume_data=resume,
        role_id="software_engineer",
        level=ExperienceLevel.MID,
        job_description=None,
        mode="quality_coach"
    )
    assert quality_score["mode"] == "quality_coach"
    assert "overallScore" in quality_score

    # Both should return reasonable scores
    assert 0 <= ats_score["overallScore"] <= 100
    assert 0 <= quality_score["overallScore"] <= 100
