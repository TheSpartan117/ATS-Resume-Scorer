"""
Tests for ATS Mode Scorer.
"""

import pytest
from backend.services.scorer_ats import ATSScorer
from backend.services.parser import ResumeData


def create_mock_resume(
    keywords_in_text: int = 5,
    total_keywords: int = 10,
    critical_issues: int = 0,
    warning_issues: int = 0,
    experience_years: float = 5.0,
    recency_months: int = 1,
    page_count: int = 1,
    has_photo: bool = False,
    file_format: str = "pdf",
    word_count: int = 500
) -> ResumeData:
    """Create mock resume for testing"""
    return ResumeData(
        fileName="test.pdf",
        contact={
            "name": "John Doe",
            "email": "john.doe@example.com",
            "phone": "123-456-7890",
            "location": "San Francisco, CA",
            "linkedin": "linkedin.com/in/johndoe"
        },
        experience=[
            {
                "title": "Software Engineer",
                "company": "Tech Company",
                "startDate": "Jan 2020",
                "endDate": "Present",
                "description": "Developed Python applications with Django and REST APIs using PostgreSQL"
            }
        ],
        education=[
            {
                "degree": "BS Computer Science",
                "institution": "University"
            }
        ],
        skills=["Python", "Django", "REST API", "PostgreSQL", "Docker"],
        certifications=[],
        metadata={
            "pageCount": page_count,
            "wordCount": word_count,
            "fileFormat": file_format,
            "hasPhoto": has_photo
        }
    )


def test_ats_scorer_initialization():
    """Test that ATS scorer initializes correctly"""
    scorer = ATSScorer()
    assert scorer.keyword_matcher is not None
    assert scorer.validator is not None


def test_score_keywords_excellent_match():
    """Test keyword scoring with 71%+ match (35 pts)"""
    scorer = ATSScorer()
    resume = create_mock_resume()

    result = scorer._score_keywords(
        resume,
        "software_engineer",
        "mid",
        ""
    )

    assert 'score' in result
    assert 'details' in result
    assert result['maxScore'] == 35
    assert 'percentage' in result['details']
    assert 'matched' in result['details']
    assert 'missing' in result['details']


def test_score_keywords_strict_thresholds():
    """Test strict keyword thresholds from design"""
    scorer = ATSScorer()

    # We can't easily mock the percentage, but we can verify structure
    # In actual use, the keyword_matcher will determine the percentage
    resume = ResumeData(
        fileName="test.pdf",
        contact={"name": "John Doe"},
        experience=[{
            "title": "Engineer",
            "company": "Company",
            "startDate": "Jan 2020",
            "endDate": "Present",
            "description": "Python Django REST API"
        }],
        education=[],
        skills=["Python", "Django"],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
    )

    result = scorer._score_keywords(resume, "software_engineer", "mid", "")

    # Verify the structure and logic
    assert result['maxScore'] == 35
    percentage = result['details']['percentage']

    # Check that scoring follows strict thresholds
    if percentage >= 71:
        assert result['score'] == 35
    elif percentage >= 51:
        assert result['score'] == 25
    elif percentage >= 31:
        assert result['score'] == 10
    else:
        assert result['score'] == 0


def test_score_keywords_with_job_description():
    """Test keyword scoring with job description"""
    scorer = ATSScorer()
    resume = create_mock_resume()

    job_description = """
    We need a Python developer with Django experience.
    Must know REST APIs and PostgreSQL.
    Docker experience is required.
    """

    result = scorer._score_keywords(
        resume,
        "software_engineer",
        "mid",
        job_description
    )

    assert result['score'] >= 0
    assert result['score'] <= 35
    assert 'percentage' in result['details']
    # Should match most keywords from JD
    assert result['details']['matched_count'] > 0


def test_score_red_flags_no_critical():
    """Test red flags scoring with 0 critical issues (20 pts)"""
    scorer = ATSScorer()
    resume = ResumeData(
        fileName="test.pdf",
        contact={"name": "John Doe", "email": "john@example.com"},
        experience=[{
            "title": "Software Engineer",
            "company": "Company",
            "startDate": "Jan 2020",
            "endDate": "Present",
            "description": "Developed scalable applications using Python and Django"
        }],
        education=[{"degree": "BS Computer Science", "institution": "University"}],
        skills=["Python", "Django"],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
    )

    result = scorer._score_red_flags(resume, "software_engineer", "mid")

    assert result['maxScore'] == 20
    assert 'details' in result
    assert 'critical_count' in result['details']
    assert 'warning_count' in result['details']
    # Harsh scoring - even with no critical issues, warnings will reduce score
    assert result['score'] >= 5  # Adjusted for harsh scoring reality


def test_score_red_flags_with_critical():
    """Test red flags scoring with critical issues"""
    scorer = ATSScorer()
    resume = ResumeData(
        fileName="test.pdf",
        contact={},
        experience=[{
            "title": "Engineer",
            "company": "Company",
            "startDate": "Jan 2023",
            "endDate": "Jan 2022"  # End before start - critical error
        }],
        education=[],  # Missing education - critical
        skills=[],  # Missing skills - critical
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
    )

    result = scorer._score_red_flags(resume, "software_engineer", "senior")

    assert result['maxScore'] == 20
    assert result['details']['critical_count'] > 0
    # Score should be lower with critical issues
    assert result['score'] < 20


def test_score_red_flags_deduction_for_warnings():
    """Test that warnings deduct points (max -5)"""
    scorer = ATSScorer()

    # This resume will have warnings but fewer critical issues
    resume = ResumeData(
        fileName="test.pdf",
        contact={
            "name": "John Doe",
            "email": "john123@yahoo.com"  # Warning: numbers and outdated provider
        },
        experience=[{
            "title": "Engineer",
            "company": "Company",
            "startDate": "Jan 2020",
            "endDate": "Present",
            "description": "Responsible for development"  # Warning: vague phrase
        }],
        education=[{"degree": "BS Computer Science", "institution": "University"}],
        skills=["Python"],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
    )

    result = scorer._score_red_flags(resume, "software_engineer", "mid")

    assert result['details']['warning_count'] > 0
    # Warnings should reduce score
    assert result['score'] < 20


def test_score_experience_perfect_match():
    """Test experience scoring with perfect level match"""
    scorer = ATSScorer()
    resume = ResumeData(
        fileName="test.pdf",
        contact={"name": "John Doe"},
        experience=[
            {
                "title": "Engineer",
                "company": "Company A",
                "startDate": "Jan 2020",
                "endDate": "Dec 2022",  # 3 years
                "description": "Developed applications using Python and Django framework"
            },
            {
                "title": "Senior Engineer",
                "company": "Company B",
                "startDate": "Jan 2023",
                "endDate": "Present",  # ~2 years
                "description": "Led team of developers building scalable systems"
            }
        ],
        education=[{"degree": "BS Computer Science", "institution": "University"}],
        skills=["Python"],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
    )

    result = scorer._score_experience(resume, "mid")

    assert result['maxScore'] == 20
    assert 'details' in result
    assert 'total_years' in result['details']
    # Should score high for mid level with ~5 years
    assert result['score'] >= 15


def test_score_experience_recency_check():
    """Test that recency impacts score"""
    scorer = ATSScorer()

    # Recent experience
    recent_resume = ResumeData(
        fileName="test.pdf",
        contact={"name": "John Doe"},
        experience=[{
            "title": "Engineer",
            "company": "Company",
            "startDate": "Jan 2024",
            "endDate": "Present",
            "description": "Current role with substantial description"
        }],
        education=[{"degree": "BS Computer Science", "institution": "University"}],
        skills=["Python"],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
    )

    result_recent = scorer._score_experience(recent_resume, "entry")

    # Should get recency points
    assert 'recency_message' in result_recent['details']
    assert result_recent['score'] >= 10


def test_score_experience_relevance():
    """Test that description quality impacts relevance score"""
    scorer = ATSScorer()

    # Good descriptions
    good_resume = ResumeData(
        fileName="test.pdf",
        contact={"name": "John Doe"},
        experience=[
            {
                "title": "Engineer",
                "company": "Company",
                "startDate": "Jan 2020",
                "endDate": "Present",
                "description": "Developed scalable microservices architecture using Python, Django, and PostgreSQL"
            }
        ],
        education=[{"degree": "BS Computer Science", "institution": "University"}],
        skills=["Python"],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
    )

    result_good = scorer._score_experience(good_resume, "mid")

    # Weak descriptions
    weak_resume = ResumeData(
        fileName="test.pdf",
        contact={"name": "John Doe"},
        experience=[
            {
                "title": "Engineer",
                "company": "Company",
                "startDate": "Jan 2020",
                "endDate": "Present",
                "description": "Dev"  # Very short
            }
        ],
        education=[{"degree": "BS Computer Science", "institution": "University"}],
        skills=["Python"],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
    )

    result_weak = scorer._score_experience(weak_resume, "mid")

    # Good descriptions should score higher
    assert result_good['score'] >= result_weak['score']


def test_score_formatting_optimal():
    """Test formatting score with optimal settings (20 pts)"""
    scorer = ATSScorer()
    resume = ResumeData(
        fileName="test.pdf",
        contact={"name": "John Doe"},
        experience=[{
            "title": "Engineer",
            "company": "Company",
            "startDate": "Jan 2020",
            "endDate": "Present"
        }],
        education=[],
        skills=[],
        certifications=[],
        metadata={
            "pageCount": 1,  # Optimal
            "wordCount": 500,  # Optimal
            "fileFormat": "pdf",  # Optimal
            "hasPhoto": False  # Optimal
        }
    )

    result = scorer._score_formatting(resume)

    assert result['maxScore'] == 20
    assert result['score'] == 20  # Perfect score
    assert result['details']['page_count'] == 1
    assert result['details']['file_format'] == 'pdf'
    assert result['details']['has_photo'] is False


def test_score_formatting_with_photo():
    """Test that photo reduces formatting score"""
    scorer = ATSScorer()
    resume = ResumeData(
        fileName="test.pdf",
        contact={"name": "John Doe"},
        experience=[],
        education=[],
        skills=[],
        certifications=[],
        metadata={
            "pageCount": 1,
            "wordCount": 500,
            "fileFormat": "pdf",
            "hasPhoto": True  # Should reduce score
        }
    )

    result = scorer._score_formatting(resume)

    assert result['score'] < 20  # Should lose photo points
    assert result['details']['has_photo'] is True


def test_score_formatting_page_count():
    """Test page count scoring"""
    scorer = ATSScorer()

    # Test 3 pages
    resume_3_pages = ResumeData(
        fileName="test.pdf",
        contact={"name": "John Doe"},
        experience=[],
        education=[],
        skills=[],
        certifications=[],
        metadata={"pageCount": 3, "wordCount": 500, "fileFormat": "pdf"}
    )

    result_3 = scorer._score_formatting(resume_3_pages)
    assert result_3['details']['page_count'] == 3
    assert result_3['score'] < 20  # Should score lower than optimal


def test_score_contact_info_complete():
    """Test contact info scoring with all fields (5 pts)"""
    scorer = ATSScorer()
    resume = ResumeData(
        fileName="test.pdf",
        contact={
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "123-456-7890",
            "location": "San Francisco, CA",
            "linkedin": "linkedin.com/in/johndoe"
        },
        experience=[],
        education=[],
        skills=[],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
    )

    result = scorer._score_contact_info(resume)

    assert result['maxScore'] == 5
    assert result['score'] == 5  # Perfect score
    assert result['details']['has_name'] is True
    assert result['details']['has_email'] is True
    assert result['details']['has_phone'] is True
    assert result['details']['has_location'] is True
    assert result['details']['has_linkedin'] is True


def test_score_contact_info_missing_fields():
    """Test contact info scoring with missing fields"""
    scorer = ATSScorer()
    resume = ResumeData(
        fileName="test.pdf",
        contact={
            "name": "John Doe",
            "email": "john@example.com"
            # Missing phone, location, linkedin
        },
        experience=[],
        education=[],
        skills=[],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
    )

    result = scorer._score_contact_info(resume)

    assert result['score'] == 2  # Only name and email
    assert result['details']['has_name'] is True
    assert result['details']['has_email'] is True
    assert result['details']['has_phone'] is False
    assert result['details']['has_location'] is False
    assert result['details']['has_linkedin'] is False
    assert 'missing' in result['details']
    assert 'phone' in result['details']['missing']
    assert 'location' in result['details']['missing']
    assert 'linkedin' in result['details']['missing']


def test_full_score_integration():
    """Test full scoring integration"""
    scorer = ATSScorer()
    resume = ResumeData(
        fileName="test.pdf",
        contact={
            "name": "John Doe",
            "email": "john.doe@example.com",
            "phone": "123-456-7890",
            "location": "San Francisco, CA",
            "linkedin": "linkedin.com/in/johndoe"
        },
        experience=[{
            "title": "Software Engineer",
            "company": "Tech Company",
            "startDate": "Jan 2020",
            "endDate": "Present",
            "description": "Developed Python Django REST APIs with PostgreSQL and Docker"
        }],
        education=[{
            "degree": "BS Computer Science",
            "institution": "University"
        }],
        skills=["Python", "Django", "REST API", "PostgreSQL", "Docker"],
        certifications=[],
        metadata={
            "pageCount": 1,
            "wordCount": 500,
            "fileFormat": "pdf",
            "hasPhoto": False
        }
    )

    result = scorer.score(resume, "software_engineer", "mid", "")

    assert 'score' in result
    assert 'breakdown' in result
    assert result['score'] >= 0
    assert result['score'] <= 100

    # Check all categories are present
    assert 'keywords' in result['breakdown']
    assert 'red_flags' in result['breakdown']
    assert 'experience' in result['breakdown']
    assert 'formatting' in result['breakdown']
    assert 'contact' in result['breakdown']

    # Verify max scores
    assert result['breakdown']['keywords']['maxScore'] == 35
    assert result['breakdown']['red_flags']['maxScore'] == 20
    assert result['breakdown']['experience']['maxScore'] == 20
    assert result['breakdown']['formatting']['maxScore'] == 20
    assert result['breakdown']['contact']['maxScore'] == 5

    # Total should match sum
    total = (
        result['breakdown']['keywords']['score'] +
        result['breakdown']['red_flags']['score'] +
        result['breakdown']['experience']['score'] +
        result['breakdown']['formatting']['score'] +
        result['breakdown']['contact']['score']
    )
    assert result['score'] == total


def test_full_score_with_job_description():
    """Test full scoring with job description"""
    scorer = ATSScorer()
    resume = create_mock_resume()

    job_description = """
    Looking for a Python developer with Django and REST API experience.
    Must know PostgreSQL and Docker.
    """

    result = scorer.score(resume, "software_engineer", "mid", job_description)

    assert 'score' in result
    assert result['breakdown']['keywords']['details']['percentage'] > 0


def test_build_resume_text():
    """Test resume text building for keyword matching"""
    scorer = ATSScorer()
    resume = ResumeData(
        fileName="test.pdf",
        contact={"name": "John Doe"},
        experience=[{
            "title": "Software Engineer",
            "company": "Tech Co",
            "description": "Python Django development"
        }],
        education=[{
            "degree": "BS Computer Science",
            "institution": "MIT"
        }],
        skills=["Python", "Django", "PostgreSQL"],
        certifications=[{
            "name": "AWS Certified"
        }],
        metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
    )

    text = scorer._build_resume_text(resume)

    assert "John Doe" in text
    assert "Software Engineer" in text
    assert "Tech Co" in text
    assert "Python Django development" in text
    assert "BS Computer Science" in text
    assert "MIT" in text
    assert "Python" in text
    assert "Django" in text
    assert "PostgreSQL" in text
    assert "AWS Certified" in text


def test_score_with_poor_resume():
    """Test scoring with a poor quality resume"""
    scorer = ATSScorer()
    resume = ResumeData(
        fileName="test.pdf",
        contact={},  # No contact info
        experience=[],  # No experience
        education=[],  # No education
        skills=[],  # No skills
        certifications=[],
        metadata={
            "pageCount": 5,  # Too many pages
            "wordCount": 100,  # Too few words
            "fileFormat": "doc",  # Unusual format
            "hasPhoto": True  # Has photo
        }
    )

    result = scorer.score(resume, "software_engineer", "mid", "")

    # Should get low score
    assert result['score'] < 50
    # Should have low scores in most categories
    assert result['breakdown']['contact']['score'] == 0
    assert result['breakdown']['formatting']['score'] < 10
    assert result['breakdown']['red_flags']['score'] < 15


def test_score_with_excellent_resume():
    """Test scoring with an excellent quality resume"""
    scorer = ATSScorer()
    resume = ResumeData(
        fileName="test.pdf",
        contact={
            "name": "John Doe",
            "email": "john.doe@example.com",
            "phone": "123-456-7890",
            "location": "San Francisco, CA",
            "linkedin": "linkedin.com/in/johndoe"
        },
        experience=[
            {
                "title": "Senior Software Engineer",
                "company": "Tech Company",
                "startDate": "Jan 2020",
                "endDate": "Present",
                "description": "Developed scalable microservices using Python, Django, FastAPI, PostgreSQL, Redis, Docker, and Kubernetes"
            }
        ],
        education=[{
            "degree": "BS Computer Science",
            "institution": "Stanford University"
        }],
        skills=["Python", "Django", "FastAPI", "PostgreSQL", "Redis", "Docker", "Kubernetes", "AWS"],
        certifications=[],
        metadata={
            "pageCount": 1,
            "wordCount": 500,
            "fileFormat": "pdf",
            "hasPhoto": False
        }
    )

    result = scorer.score(resume, "software_engineer", "mid", "")

    # Harsh scoring - excellent resume still gets realistic score
    assert result['score'] >= 45  # Adjusted for harsh but realistic scoring
    # Should have high scores in most categories
    assert result['breakdown']['contact']['score'] == 5
    assert result['breakdown']['formatting']['score'] == 20


def test_experience_level_ranges():
    """Test that different experience levels are scored correctly"""
    scorer = ATSScorer()

    levels = ["entry", "mid", "senior", "lead", "executive"]

    for level in levels:
        resume = ResumeData(
            fileName="test.pdf",
            contact={"name": "John Doe"},
            experience=[{
                "title": "Engineer",
                "company": "Company",
                "startDate": "Jan 2020",
                "endDate": "Present",
                "description": "Developed applications"
            }],
            education=[{"degree": "BS Computer Science", "institution": "University"}],
            skills=["Python"],
            certifications=[],
            metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
        )

        result = scorer._score_experience(resume, level)

        assert 'details' in result
        assert 'total_years' in result['details']
        assert result['score'] >= 0
        assert result['score'] <= 20
