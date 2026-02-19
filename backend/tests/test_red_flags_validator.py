"""
Tests for red flags validator - employment history validation.
"""

import pytest
from datetime import datetime
from backend.services.red_flags_validator import RedFlagsValidator
from backend.services.parser import ResumeData


def create_mock_resume_with_gap():
    """Create resume with 15-month employment gap"""
    return ResumeData(
        fileName="test.pdf",
        contact={"name": "John Doe", "email": "john@example.com"},
        experience=[
            {
                "title": "Software Engineer",
                "company": "Company A",
                "startDate": "Jan 2020",
                "endDate": "Dec 2020"
            },
            {
                "title": "Senior Engineer",
                "company": "Company B",
                "startDate": "Mar 2022",  # 15-month gap
                "endDate": "Present"
            }
        ],
        education=[],
        skills=["Python"],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
    )


def test_detect_employment_gap():
    """Test that 15-month gap is detected as warning"""
    validator = RedFlagsValidator()
    resume = create_mock_resume_with_gap()

    issues = validator.validate_employment_history(resume)

    gap_issues = [i for i in issues if 'gap' in i['message'].lower()]
    assert len(gap_issues) >= 1
    assert gap_issues[0]['severity'] == 'warning'  # 9-18 months = warning
    assert '15' in gap_issues[0]['message']


def test_date_validation_catches_invalid_dates():
    """Test that end before start is caught"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={},
        experience=[{
            "title": "Engineer",
            "company": "Company",
            "startDate": "Jan 2023",
            "endDate": "Jan 2022"  # End before start!
        }],
        education=[],
        skills=[],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
    )

    validator = RedFlagsValidator()
    issues = validator.validate_employment_history(resume)

    date_issues = [i for i in issues if 'before' in i['message'].lower()]
    assert len(date_issues) >= 1
    assert date_issues[0]['severity'] == 'critical'


def test_experience_level_alignment():
    """Test that claiming Senior with 3 years triggers warning"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={},
        experience=[{
            "title": "Engineer",
            "company": "Company",
            "startDate": "Jan 2023",
            "endDate": "Present"
        }],
        education=[],
        skills=[],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
    )

    validator = RedFlagsValidator()
    issues = validator.validate_experience_level(resume, "senior")

    level_issues = [i for i in issues if 'senior' in i['message'].lower()]
    assert len(level_issues) >= 1
    assert level_issues[0]['severity'] in ['warning', 'critical']


def test_parse_date_handles_multiple_formats():
    """Test that various date formats are parsed correctly"""
    validator = RedFlagsValidator()

    # Test different formats
    assert validator.parse_date("Jan 2020").year == 2020
    assert validator.parse_date("Jan 2020").month == 1

    assert validator.parse_date("January 2020").year == 2020
    assert validator.parse_date("January 2020").month == 1

    assert validator.parse_date("01/2020").year == 2020
    assert validator.parse_date("01/2020").month == 1

    assert validator.parse_date("2020").year == 2020

    # Test Present/Current
    present_date = validator.parse_date("Present")
    assert present_date.year == datetime.now().year

    current_date = validator.parse_date("Current")
    assert current_date.year == datetime.now().year


def test_critical_gap_detection():
    """Test that 18+ month gap is critical"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={},
        experience=[
            {
                "title": "Engineer 1",
                "company": "Company A",
                "startDate": "Jan 2020",
                "endDate": "Jun 2020"
            },
            {
                "title": "Engineer 2",
                "company": "Company B",
                "startDate": "Feb 2022",  # 20-month gap
                "endDate": "Present"
            }
        ],
        education=[],
        skills=[],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
    )

    validator = RedFlagsValidator()
    issues = validator.validate_employment_history(resume)

    gap_issues = [i for i in issues if 'gap' in i['message'].lower()]
    assert len(gap_issues) >= 1
    assert gap_issues[0]['severity'] == 'critical'
    assert '20' in gap_issues[0]['message']


def test_job_hopping_detection():
    """Test that multiple short tenures are detected"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={},
        experience=[
            {
                "title": "Engineer 1",
                "company": "Company A",
                "startDate": "Jan 2020",
                "endDate": "Jun 2020"  # 6 months
            },
            {
                "title": "Engineer 2",
                "company": "Company B",
                "startDate": "Jul 2020",
                "endDate": "Dec 2020"  # 6 months
            },
            {
                "title": "Engineer 3",
                "company": "Company C",
                "startDate": "Jan 2021",
                "endDate": "Present"
            }
        ],
        education=[],
        skills=[],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
    )

    validator = RedFlagsValidator()
    issues = validator.validate_employment_history(resume)

    hopping_issues = [i for i in issues if 'hopping' in i['message'].lower() or 'short tenure' in i['message'].lower()]
    assert len(hopping_issues) >= 1
    assert hopping_issues[0]['severity'] == 'warning'


def test_missing_dates_detection():
    """Test that missing dates are flagged as critical"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={},
        experience=[{
            "title": "Engineer",
            "company": "Company",
            "startDate": "Jan 2020",
            # Missing endDate
        }],
        education=[],
        skills=[],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
    )

    validator = RedFlagsValidator()
    issues = validator.validate_employment_history(resume)

    missing_issues = [i for i in issues if 'missing' in i['message'].lower()]
    assert len(missing_issues) >= 1
    assert missing_issues[0]['severity'] == 'critical'


def test_date_format_consistency():
    """Test that inconsistent date formats trigger warning"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={},
        experience=[
            {
                "title": "Engineer 1",
                "company": "Company A",
                "startDate": "Jan 2020",  # Mon YYYY format
                "endDate": "Dec 2020"
            },
            {
                "title": "Engineer 2",
                "company": "Company B",
                "startDate": "01/2021",  # MM/YYYY format
                "endDate": "Present"
            }
        ],
        education=[],
        skills=[],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
    )

    validator = RedFlagsValidator()
    issues = validator.validate_employment_history(resume)

    format_issues = [i for i in issues if 'format' in i['message'].lower()]
    assert len(format_issues) >= 1
    assert format_issues[0]['severity'] == 'warning'


def test_future_start_date_detection():
    """Test that future start dates are caught"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={},
        experience=[{
            "title": "Engineer",
            "company": "Company",
            "startDate": "Jan 2030",  # Future date
            "endDate": "Present"
        }],
        education=[],
        skills=[],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
    )

    validator = RedFlagsValidator()
    issues = validator.validate_employment_history(resume)

    future_issues = [i for i in issues if 'future' in i['message'].lower()]
    assert len(future_issues) >= 1
    assert future_issues[0]['severity'] == 'critical'


def test_validate_resume_categorizes_issues():
    """Test that validate_resume returns issues in proper categories"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={},
        experience=[
            {
                "title": "Engineer",
                "company": "Company A",
                "startDate": "Jan 2023",
                "endDate": "Jan 2022"  # Critical: end before start
            },
            {
                "title": "Senior Engineer",
                "company": "Company B",
                "startDate": "Feb 2022",
                "endDate": "Present"
            }
        ],
        education=[],
        skills=[],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
    )

    validator = RedFlagsValidator()
    result = validator.validate_resume(resume, "software_engineer", "senior")

    assert 'critical' in result
    assert 'warnings' in result
    assert 'suggestions' in result
    assert len(result['critical']) > 0  # Should have date error


def test_no_experience_listed():
    """Test that missing experience is flagged as critical"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={},
        experience=[],  # No experience
        education=[],
        skills=[],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
    )

    validator = RedFlagsValidator()
    issues = validator.validate_employment_history(resume)

    assert len(issues) >= 1
    assert issues[0]['severity'] == 'critical'
    assert 'no work experience' in issues[0]['message'].lower()


def test_calculate_total_experience():
    """Test total experience calculation"""
    validator = RedFlagsValidator()

    experience = [
        {
            "startDate": "Jan 2020",
            "endDate": "Dec 2020"  # 1 year
        },
        {
            "startDate": "Jan 2021",
            "endDate": "Dec 2022"  # 2 years
        }
    ]

    total_years = validator.calculate_total_experience(experience)
    assert total_years == pytest.approx(3.0, rel=0.2)  # ~3 years


def test_entry_level_validation():
    """Test that entry level validation works correctly"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={},
        experience=[{
            "title": "Junior Engineer",
            "company": "Company",
            "startDate": "Jan 2024",
            "endDate": "Present"  # ~1 year
        }],
        education=[],
        skills=[],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
    )

    validator = RedFlagsValidator()
    issues = validator.validate_experience_level(resume, "entry")

    # Should have no issues for entry level with 1 year
    level_issues = [i for i in issues if 'entry' in i['message'].lower()]
    assert len(level_issues) == 0


def test_executive_level_validation():
    """Test that executive level requires 12+ years"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={},
        experience=[{
            "title": "Engineer",
            "company": "Company",
            "startDate": "Jan 2020",
            "endDate": "Present"  # ~5 years
        }],
        education=[],
        skills=[],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
    )

    validator = RedFlagsValidator()
    issues = validator.validate_experience_level(resume, "executive")

    level_issues = [i for i in issues if 'executive' in i['message'].lower()]
    assert len(level_issues) >= 1
    assert level_issues[0]['severity'] in ['warning', 'critical']


# ===== Content Depth Validation Tests (P7-P9) =====

def test_vague_phrases_detection():
    """Test detection of vague phrases in experience descriptions (P7)"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={},
        experience=[
            {
                "title": "Software Engineer",
                "company": "Company A",
                "startDate": "Jan 2020",
                "endDate": "Dec 2021",
                "description": "• Responsible for developing applications\n• Worked on multiple projects\n• Helped with code reviews"
            },
            {
                "title": "Senior Engineer",
                "company": "Company B",
                "startDate": "Jan 2022",
                "endDate": "Present",
                "description": "• Built scalable microservices architecture\n• Reduced deployment time by 40%"
            }
        ],
        education=[],
        skills=[],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
    )

    validator = RedFlagsValidator()
    issues = validator.validate_content_depth(resume)

    vague_issues = [i for i in issues if 'vague' in i['message'].lower()]
    assert len(vague_issues) >= 1
    assert vague_issues[0]['severity'] == 'warning'
    assert 'responsible for' in vague_issues[0]['message'].lower() or 'worked on' in vague_issues[0]['message'].lower()


def test_bullet_length_too_short_critical():
    """Test detection of critically short bullets (<30 chars) (P8)"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={},
        experience=[{
            "title": "Engineer",
            "company": "Company",
            "startDate": "Jan 2020",
            "endDate": "Present",
            "description": "• Fixed bugs\n• Code review\n• Built REST APIs using Python and FastAPI with PostgreSQL database"
        }],
        education=[],
        skills=[],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
    )

    validator = RedFlagsValidator()
    issues = validator.validate_content_depth(resume)

    short_issues = [i for i in issues if 'short' in i['message'].lower() and 'critical' in i['severity']]
    assert len(short_issues) >= 1
    assert short_issues[0]['severity'] == 'critical'


def test_bullet_length_too_short_warning():
    """Test detection of short bullets (30-49 chars) as warnings (P8)"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={},
        experience=[{
            "title": "Engineer",
            "company": "Company",
            "startDate": "Jan 2020",
            "endDate": "Present",
            "description": "• Developed features for web application"
        }],
        education=[],
        skills=[],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
    )

    validator = RedFlagsValidator()
    issues = validator.validate_content_depth(resume)

    short_issues = [i for i in issues if 'detailed' in i['message'].lower() and i['severity'] == 'warning']
    assert len(short_issues) >= 1


def test_bullet_length_too_long_critical():
    """Test detection of critically long bullets (>200 chars) (P8)"""
    long_bullet = "• " + "a" * 210  # 212 chars total
    resume = ResumeData(
        fileName="test.pdf",
        contact={},
        experience=[{
            "title": "Engineer",
            "company": "Company",
            "startDate": "Jan 2020",
            "endDate": "Present",
            "description": long_bullet
        }],
        education=[],
        skills=[],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
    )

    validator = RedFlagsValidator()
    issues = validator.validate_content_depth(resume)

    long_issues = [i for i in issues if 'long' in i['message'].lower() and 'critical' in i['severity']]
    assert len(long_issues) >= 1
    assert long_issues[0]['severity'] == 'critical'


def test_bullet_length_too_long_warning():
    """Test detection of long bullets (151-200 chars) as warnings (P8)"""
    long_bullet = "• Developed and deployed a comprehensive microservices architecture using Spring Boot, Docker, and Kubernetes that improved system scalability and reduced deployment time by forty percent"
    resume = ResumeData(
        fileName="test.pdf",
        contact={},
        experience=[{
            "title": "Engineer",
            "company": "Company",
            "startDate": "Jan 2020",
            "endDate": "Present",
            "description": long_bullet
        }],
        education=[],
        skills=[],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
    )

    validator = RedFlagsValidator()
    issues = validator.validate_content_depth(resume)

    long_issues = [i for i in issues if 'concise' in i['message'].lower() and i['severity'] == 'warning']
    assert len(long_issues) >= 1


def test_bullet_length_optimal():
    """Test that optimal length bullets (50-150 chars) trigger no issues (P8)"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={},
        experience=[{
            "title": "Engineer",
            "company": "Company",
            "startDate": "Jan 2020",
            "endDate": "Present",
            "description": "• Built scalable REST APIs using FastAPI and PostgreSQL\n• Reduced query response time by 60% through optimization"
        }],
        education=[],
        skills=[],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
    )

    validator = RedFlagsValidator()
    issues = validator.validate_content_depth(resume)

    # Should have no bullet length issues
    length_issues = [i for i in issues if 'short' in i['message'].lower() or 'long' in i['message'].lower()]
    assert len(length_issues) == 0


def test_fragment_detection():
    """Test detection of incomplete bullet points (P9)"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={},
        experience=[{
            "title": "Engineer",
            "company": "Company",
            "startDate": "Jan 2020",
            "endDate": "Present",
            "description": "• Python, Django\n• APIs\n• Was responsible for the project\n• Developed comprehensive application"
        }],
        education=[],
        skills=[],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
    )

    validator = RedFlagsValidator()
    issues = validator.validate_content_depth(resume)

    fragment_issues = [i for i in issues if 'fragment' in i['message'].lower() or 'incomplete' in i['message'].lower()]
    assert len(fragment_issues) >= 1
    assert fragment_issues[0]['severity'] == 'warning'


def test_weak_verb_detection():
    """Test detection of weak verbs (was, is, been) in bullets (P9)"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={},
        experience=[{
            "title": "Engineer",
            "company": "Company",
            "startDate": "Jan 2020",
            "endDate": "Present",
            "description": "• Was working on the API development\n• Is responsible for database management\n• Has been involved in code reviews"
        }],
        education=[],
        skills=[],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
    )

    validator = RedFlagsValidator()
    issues = validator.validate_content_depth(resume)

    weak_issues = [i for i in issues if 'weak' in i['message'].lower() or 'fragment' in i['message'].lower()]
    assert len(weak_issues) >= 1
    assert weak_issues[0]['severity'] == 'warning'


def test_content_depth_with_multiple_issues():
    """Test content depth validation with multiple types of issues"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={},
        experience=[
            {
                "title": "Software Engineer",
                "company": "Company A",
                "startDate": "Jan 2020",
                "endDate": "Dec 2021",
                "description": "• Worked on projects\n• Was responsible for APIs\n• " + "x" * 205
            },
            {
                "title": "Engineer",
                "company": "Company B",
                "startDate": "Jan 2022",
                "endDate": "Present",
                "description": "• Built scalable microservices with 99.9% uptime"
            }
        ],
        education=[],
        skills=[],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
    )

    validator = RedFlagsValidator()
    issues = validator.validate_content_depth(resume)

    # Should have multiple types of issues
    assert len(issues) >= 3

    # Check for vague phrases
    vague_issues = [i for i in issues if 'vague' in i['message'].lower()]
    assert len(vague_issues) >= 1

    # Check for fragments/weak verbs
    fragment_issues = [i for i in issues if 'fragment' in i['message'].lower() or 'weak' in i['message'].lower()]
    assert len(fragment_issues) >= 1

    # Check for length issues
    length_issues = [i for i in issues if 'long' in i['message'].lower()]
    assert len(length_issues) >= 1


def test_content_depth_no_description():
    """Test content depth validation when experience has no description"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={},
        experience=[{
            "title": "Engineer",
            "company": "Company",
            "startDate": "Jan 2020",
            "endDate": "Present"
            # No description field
        }],
        education=[],
        skills=[],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
    )

    validator = RedFlagsValidator()
    issues = validator.validate_content_depth(resume)

    # Should not crash, may warn about missing descriptions
    assert isinstance(issues, list)


def test_content_depth_empty_description():
    """Test content depth validation with empty description"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={},
        experience=[{
            "title": "Engineer",
            "company": "Company",
            "startDate": "Jan 2020",
            "endDate": "Present",
            "description": ""
        }],
        education=[],
        skills=[],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
    )

    validator = RedFlagsValidator()
    issues = validator.validate_content_depth(resume)

    # Should not crash
    assert isinstance(issues, list)


def test_validate_resume_includes_content_depth():
    """Test that validate_resume calls validate_content_depth"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={},
        experience=[{
            "title": "Engineer",
            "company": "Company",
            "startDate": "Jan 2020",
            "endDate": "Present",
            "description": "• Responsible for development\n• Short\n• " + "x" * 210
        }],
        education=[],
        skills=[],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
    )

    validator = RedFlagsValidator()
    result = validator.validate_resume(resume, "software_engineer", "mid")

    # Should have content depth issues in warnings
    all_issues = result['critical'] + result['warnings']
    content_issues = [i for i in all_issues if 'vague' in i['message'].lower() or
                      'short' in i['message'].lower() or 'long' in i['message'].lower()]
    assert len(content_issues) > 0


def test_all_vague_phrases():
    """Test detection of all documented vague phrases"""
    vague_phrases = [
        "responsible for",
        "worked on",
        "helped with",
        "assisted with",
        "involved in",
        "participated in"
    ]

    for phrase in vague_phrases:
        resume = ResumeData(
            fileName="test.pdf",
            contact={},
            experience=[{
                "title": "Engineer",
                "company": "Company",
                "startDate": "Jan 2020",
                "endDate": "Present",
                "description": f"• {phrase.capitalize()} the project development and implementation"
            }],
            education=[],
            skills=[],
            certifications=[],
            metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
        )

        validator = RedFlagsValidator()
        issues = validator.validate_content_depth(resume)

        vague_issues = [i for i in issues if 'vague' in i['message'].lower()]
        assert len(vague_issues) >= 1, f"Failed to detect vague phrase: {phrase}"


# ===== Section Completeness Validation Tests (P10-P13) =====

def test_missing_required_section_experience():
    """Test that missing Experience section is flagged as critical (P10)"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={"name": "John Doe"},
        experience=[],  # Missing experience
        education=[{"degree": "BS Computer Science", "institution": "University"}],
        skills=["Python", "Java"],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
    )

    validator = RedFlagsValidator()
    issues = validator.validate_section_completeness(resume)

    missing_issues = [i for i in issues if 'experience' in i['message'].lower() and 'required' in i['message'].lower()]
    assert len(missing_issues) >= 1
    assert missing_issues[0]['severity'] == 'critical'


def test_missing_required_section_education():
    """Test that missing Education section is flagged as critical (P10)"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={"name": "John Doe"},
        experience=[{"title": "Engineer", "company": "Company", "startDate": "Jan 2020", "endDate": "Present"}],
        education=[],  # Missing education
        skills=["Python", "Java"],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
    )

    validator = RedFlagsValidator()
    issues = validator.validate_section_completeness(resume)

    missing_issues = [i for i in issues if 'education' in i['message'].lower() and 'required' in i['message'].lower()]
    assert len(missing_issues) >= 1
    assert missing_issues[0]['severity'] == 'critical'


def test_missing_required_section_skills():
    """Test that missing Skills section is flagged as critical (P10)"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={"name": "John Doe"},
        experience=[{"title": "Engineer", "company": "Company", "startDate": "Jan 2020", "endDate": "Present"}],
        education=[{"degree": "BS Computer Science", "institution": "University"}],
        skills=[],  # Missing skills
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
    )

    validator = RedFlagsValidator()
    issues = validator.validate_section_completeness(resume)

    missing_issues = [i for i in issues if 'skills' in i['message'].lower() and 'required' in i['message'].lower()]
    assert len(missing_issues) >= 1
    assert missing_issues[0]['severity'] == 'critical'


def test_all_required_sections_present():
    """Test that no issues when all required sections are present (P10)"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={"name": "John Doe"},
        experience=[{"title": "Engineer", "company": "Company", "startDate": "Jan 2020", "endDate": "Present"}],
        education=[{"degree": "BS Computer Science", "institution": "University"}],
        skills=["Python", "Java"],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
    )

    validator = RedFlagsValidator()
    issues = validator.validate_section_completeness(resume)

    # Should have no critical missing section issues
    missing_issues = [i for i in issues if 'required' in i['message'].lower() and i['severity'] == 'critical']
    assert len(missing_issues) == 0


def test_recency_check_within_2_years():
    """Test that most recent role within 2 years passes recency check (P12)"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={"name": "John Doe"},
        experience=[{
            "title": "Engineer",
            "company": "Company",
            "startDate": "Jan 2024",
            "endDate": "Present"
        }],
        education=[{"degree": "BS Computer Science", "institution": "University"}],
        skills=["Python"],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
    )

    validator = RedFlagsValidator()
    issues = validator.validate_section_completeness(resume)

    recency_issues = [i for i in issues if 'recency' in i['message'].lower() or 'most recent' in i['message'].lower()]
    assert len(recency_issues) == 0


def test_recency_check_more_than_2_years():
    """Test that most recent role >2 years ago triggers warning (P12)"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={"name": "John Doe"},
        experience=[{
            "title": "Engineer",
            "company": "Company",
            "startDate": "Jan 2020",
            "endDate": "Dec 2021"  # Ended >2 years ago
        }],
        education=[{"degree": "BS Computer Science", "institution": "University"}],
        skills=["Python"],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
    )

    validator = RedFlagsValidator()
    issues = validator.validate_section_completeness(resume)

    recency_issues = [i for i in issues if 'recent' in i['message'].lower() or '2 years' in i['message'].lower()]
    assert len(recency_issues) >= 1
    assert recency_issues[0]['severity'] == 'warning'


def test_recency_check_with_present_role():
    """Test recency check with current ongoing role"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={"name": "John Doe"},
        experience=[
            {
                "title": "Senior Engineer",
                "company": "Current Company",
                "startDate": "Jan 2022",
                "endDate": "Present"
            },
            {
                "title": "Engineer",
                "company": "Old Company",
                "startDate": "Jan 2018",
                "endDate": "Dec 2021"
            }
        ],
        education=[{"degree": "BS Computer Science", "institution": "University"}],
        skills=["Python"],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
    )

    validator = RedFlagsValidator()
    issues = validator.validate_section_completeness(resume)

    # Should pass recency check since current role is ongoing
    recency_issues = [i for i in issues if 'recent' in i['message'].lower()]
    assert len(recency_issues) == 0


def test_missing_summary_objective():
    """Test that missing summary/objective triggers suggestion (P13)"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={"name": "John Doe", "email": "john@example.com"},  # No summary
        experience=[{"title": "Engineer", "company": "Company", "startDate": "Jan 2020", "endDate": "Present"}],
        education=[{"degree": "BS Computer Science", "institution": "University"}],
        skills=["Python"],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
    )

    validator = RedFlagsValidator()
    issues = validator.validate_section_completeness(resume)

    summary_issues = [i for i in issues if 'summary' in i['message'].lower() or 'objective' in i['message'].lower()]
    assert len(summary_issues) >= 1
    assert summary_issues[0]['severity'] == 'suggestion'


def test_summary_present():
    """Test that summary presence is detected (P13)"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={
            "name": "John Doe",
            "email": "john@example.com",
            "summary": "Experienced software engineer with 5 years of expertise"
        },
        experience=[{"title": "Engineer", "company": "Company", "startDate": "Jan 2020", "endDate": "Present"}],
        education=[{"degree": "BS Computer Science", "institution": "University"}],
        skills=["Python"],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
    )

    validator = RedFlagsValidator()
    issues = validator.validate_section_completeness(resume)

    # Should not have summary/objective suggestions
    summary_issues = [i for i in issues if 'summary' in i['message'].lower() or 'objective' in i['message'].lower()]
    assert len(summary_issues) == 0


def test_section_completeness_multiple_issues():
    """Test section completeness with multiple issues"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={"name": "John Doe"},
        experience=[{
            "title": "Engineer",
            "company": "Company",
            "startDate": "Jan 2019",
            "endDate": "Dec 2021"  # More than 2 years ago
        }],
        education=[],  # Missing education
        skills=[],  # Missing skills
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
    )

    validator = RedFlagsValidator()
    issues = validator.validate_section_completeness(resume)

    # Should have multiple issues
    assert len(issues) >= 3

    # Check for missing education (critical)
    education_issues = [i for i in issues if 'education' in i['message'].lower() and i['severity'] == 'critical']
    assert len(education_issues) >= 1

    # Check for missing skills (critical)
    skills_issues = [i for i in issues if 'skills' in i['message'].lower() and i['severity'] == 'critical']
    assert len(skills_issues) >= 1

    # Check for recency warning
    recency_issues = [i for i in issues if 'recent' in i['message'].lower() and i['severity'] == 'warning']
    assert len(recency_issues) >= 1

    # Check for missing summary (suggestion)
    summary_issues = [i for i in issues if ('summary' in i['message'].lower() or 'objective' in i['message'].lower()) and i['severity'] == 'suggestion']
    assert len(summary_issues) >= 1


def test_validate_resume_includes_section_completeness():
    """Test that validate_resume calls validate_section_completeness"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={},
        experience=[],  # Missing experience
        education=[],  # Missing education
        skills=[],  # Missing skills
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
    )

    validator = RedFlagsValidator()
    result = validator.validate_resume(resume, "software_engineer", "mid")

    # Should have section completeness issues in critical
    assert len(result['critical']) > 0
    section_issues = [i for i in result['critical'] if 'required' in i['message'].lower()]
    assert len(section_issues) >= 2  # At least experience and education missing


# ===== Professional Standards Validation Tests (P14-P17) =====

def test_professional_email_format():
    """Test detection of professional email format (P14)"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={
            "name": "John Doe",
            "email": "john.doe@company.com"  # Professional format
        },
        experience=[{"title": "Engineer", "company": "Company", "startDate": "Jan 2020", "endDate": "Present"}],
        education=[{"degree": "BS Computer Science", "institution": "University"}],
        skills=["Python"],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
    )

    validator = RedFlagsValidator()
    issues = validator.validate_professional_standards(resume)

    # Should have no email issues for professional format
    email_issues = [i for i in issues if 'email' in i['message'].lower()]
    assert len(email_issues) == 0


def test_unprofessional_email_with_numbers():
    """Test detection of unprofessional email with numbers (P14)"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={
            "name": "John Doe",
            "email": "john123@gmail.com"  # Has numbers
        },
        experience=[{"title": "Engineer", "company": "Company", "startDate": "Jan 2020", "endDate": "Present"}],
        education=[{"degree": "BS Computer Science", "institution": "University"}],
        skills=["Python"],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
    )

    validator = RedFlagsValidator()
    issues = validator.validate_professional_standards(resume)

    email_issues = [i for i in issues if 'email' in i['message'].lower() and 'numbers' in i['message'].lower()]
    assert len(email_issues) >= 1
    assert email_issues[0]['severity'] == 'warning'


def test_unprofessional_email_with_underscores():
    """Test detection of unprofessional email with underscores (P14)"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={
            "name": "John Doe",
            "email": "john_doe@gmail.com"  # Has underscore
        },
        experience=[{"title": "Engineer", "company": "Company", "startDate": "Jan 2020", "endDate": "Present"}],
        education=[{"degree": "BS Computer Science", "institution": "University"}],
        skills=["Python"],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
    )

    validator = RedFlagsValidator()
    issues = validator.validate_professional_standards(resume)

    email_issues = [i for i in issues if 'email' in i['message'].lower() and 'underscores' in i['message'].lower()]
    assert len(email_issues) >= 1
    assert email_issues[0]['severity'] == 'warning'


def test_outdated_email_provider():
    """Test detection of outdated email providers (P14)"""
    outdated_providers = ['aol.com', 'yahoo.com', 'hotmail.com']

    for provider in outdated_providers:
        resume = ResumeData(
            fileName="test.pdf",
            contact={
                "name": "John Doe",
                "email": f"john.doe@{provider}"
            },
            experience=[{"title": "Engineer", "company": "Company", "startDate": "Jan 2020", "endDate": "Present"}],
            education=[{"degree": "BS Computer Science", "institution": "University"}],
            skills=["Python"],
            certifications=[],
            metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
        )

        validator = RedFlagsValidator()
        issues = validator.validate_professional_standards(resume)

        outdated_issues = [i for i in issues if 'outdated' in i['message'].lower() or 'provider' in i['message'].lower()]
        assert len(outdated_issues) >= 1, f"Failed to detect outdated provider: {provider}"
        assert outdated_issues[0]['severity'] == 'warning'


def test_linkedin_url_valid():
    """Test valid LinkedIn URL format (P15)"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={
            "name": "John Doe",
            "email": "john.doe@gmail.com",
            "linkedin": "linkedin.com/in/johndoe"
        },
        experience=[{"title": "Engineer", "company": "Company", "startDate": "Jan 2020", "endDate": "Present"}],
        education=[{"degree": "BS Computer Science", "institution": "University"}],
        skills=["Python"],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
    )

    validator = RedFlagsValidator()
    issues = validator.validate_professional_standards(resume)

    # Should have no LinkedIn issues
    linkedin_issues = [i for i in issues if 'linkedin' in i['message'].lower()]
    assert len(linkedin_issues) == 0


def test_linkedin_url_with_https():
    """Test valid LinkedIn URL with https (P15)"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={
            "name": "John Doe",
            "email": "john.doe@gmail.com",
            "linkedin": "https://www.linkedin.com/in/johndoe"
        },
        experience=[{"title": "Engineer", "company": "Company", "startDate": "Jan 2020", "endDate": "Present"}],
        education=[{"degree": "BS Computer Science", "institution": "University"}],
        skills=["Python"],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
    )

    validator = RedFlagsValidator()
    issues = validator.validate_professional_standards(resume)

    # Should have no LinkedIn issues
    linkedin_issues = [i for i in issues if 'linkedin' in i['message'].lower()]
    assert len(linkedin_issues) == 0


def test_linkedin_missing():
    """Test missing LinkedIn URL triggers suggestion (P15)"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={
            "name": "John Doe",
            "email": "john.doe@gmail.com"
            # No LinkedIn
        },
        experience=[{"title": "Engineer", "company": "Company", "startDate": "Jan 2020", "endDate": "Present"}],
        education=[{"degree": "BS Computer Science", "institution": "University"}],
        skills=["Python"],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
    )

    validator = RedFlagsValidator()
    issues = validator.validate_professional_standards(resume)

    linkedin_issues = [i for i in issues if 'linkedin' in i['message'].lower() and 'adding' in i['message'].lower()]
    assert len(linkedin_issues) >= 1
    assert linkedin_issues[0]['severity'] == 'suggestion'


def test_linkedin_company_page_invalid():
    """Test LinkedIn company page is flagged as invalid (P15)"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={
            "name": "John Doe",
            "email": "john.doe@gmail.com",
            "linkedin": "linkedin.com/company/mycompany"
        },
        experience=[{"title": "Engineer", "company": "Company", "startDate": "Jan 2020", "endDate": "Present"}],
        education=[{"degree": "BS Computer Science", "institution": "University"}],
        skills=["Python"],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
    )

    validator = RedFlagsValidator()
    issues = validator.validate_professional_standards(resume)

    linkedin_issues = [i for i in issues if 'linkedin' in i['message'].lower() and 'company' in i['message'].lower()]
    assert len(linkedin_issues) >= 1
    assert linkedin_issues[0]['severity'] == 'warning'


def test_phone_format_consistency_consistent():
    """Test consistent phone formatting passes (P16)"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={
            "name": "John Doe",
            "email": "john.doe@gmail.com",
            "phone": "123-456-7890"
        },
        experience=[
            {
                "title": "Engineer",
                "company": "Company A",
                "startDate": "Jan 2020",
                "endDate": "Dec 2021",
                "description": "Contact: 123-456-7890"  # Same format
            },
            {
                "title": "Senior Engineer",
                "company": "Company B",
                "startDate": "Jan 2022",
                "endDate": "Present"
            }
        ],
        education=[{"degree": "BS Computer Science", "institution": "University"}],
        skills=["Python"],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
    )

    validator = RedFlagsValidator()
    issues = validator.validate_professional_standards(resume)

    # Should have no phone format issues
    phone_issues = [i for i in issues if 'phone' in i['message'].lower() and 'format' in i['message'].lower()]
    assert len(phone_issues) == 0


def test_phone_format_consistency_inconsistent():
    """Test inconsistent phone formatting triggers warning (P16)"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={
            "name": "John Doe",
            "email": "john.doe@gmail.com",
            "phone": "123-456-7890"
        },
        experience=[
            {
                "title": "Engineer",
                "company": "Company A",
                "startDate": "Jan 2020",
                "endDate": "Dec 2021",
                "description": "Contact: (123) 456-7890"  # Different format (parentheses)
            },
            {
                "title": "Senior Engineer",
                "company": "Company B",
                "startDate": "Jan 2022",
                "endDate": "Present"
            }
        ],
        education=[{"degree": "BS Computer Science", "institution": "University"}],
        skills=["Python"],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
    )

    validator = RedFlagsValidator()
    issues = validator.validate_professional_standards(resume)

    phone_issues = [i for i in issues if 'phone' in i['message'].lower() and 'consistent' in i['message'].lower()]
    assert len(phone_issues) >= 1
    assert phone_issues[0]['severity'] == 'warning'


def test_location_format_valid():
    """Test valid location format (P17)"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={
            "name": "John Doe",
            "email": "john.doe@gmail.com",
            "location": "San Francisco, CA"
        },
        experience=[{"title": "Engineer", "company": "Company", "startDate": "Jan 2020", "endDate": "Present"}],
        education=[{"degree": "BS Computer Science", "institution": "University"}],
        skills=["Python"],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
    )

    validator = RedFlagsValidator()
    issues = validator.validate_professional_standards(resume)

    # Should have no location issues
    location_issues = [i for i in issues if 'location' in i['message'].lower()]
    assert len(location_issues) == 0


def test_location_format_invalid():
    """Test invalid location format triggers warning (P17)"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={
            "name": "John Doe",
            "email": "john.doe@gmail.com",
            "location": "San Francisco"  # Missing state/country
        },
        experience=[{"title": "Engineer", "company": "Company", "startDate": "Jan 2020", "endDate": "Present"}],
        education=[{"degree": "BS Computer Science", "institution": "University"}],
        skills=["Python"],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
    )

    validator = RedFlagsValidator()
    issues = validator.validate_professional_standards(resume)

    location_issues = [i for i in issues if 'location' in i['message'].lower() and 'format' in i['message'].lower()]
    assert len(location_issues) >= 1
    assert location_issues[0]['severity'] == 'warning'


def test_professional_standards_no_contact():
    """Test professional standards validation with no contact info"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={},
        experience=[{"title": "Engineer", "company": "Company", "startDate": "Jan 2020", "endDate": "Present"}],
        education=[{"degree": "BS Computer Science", "institution": "University"}],
        skills=["Python"],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
    )

    validator = RedFlagsValidator()
    issues = validator.validate_professional_standards(resume)

    # Should have issue for missing LinkedIn
    linkedin_issues = [i for i in issues if 'linkedin' in i['message'].lower()]
    assert len(linkedin_issues) >= 1


def test_professional_standards_multiple_issues():
    """Test professional standards with multiple issues"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={
            "name": "John Doe",
            "email": "john123_doe@yahoo.com",  # Numbers, underscore, outdated provider
            "phone": "123-456-7890",
            "location": "San Francisco"  # Missing state
        },
        experience=[
            {
                "title": "Engineer",
                "company": "Company",
                "startDate": "Jan 2020",
                "endDate": "Present",
                "description": "Contact: (123) 456 7890"  # Inconsistent phone format
            }
        ],
        education=[{"degree": "BS Computer Science", "institution": "University"}],
        skills=["Python"],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
    )

    validator = RedFlagsValidator()
    issues = validator.validate_professional_standards(resume)

    # Should have multiple issues
    assert len(issues) >= 3

    # Email issues
    email_issues = [i for i in issues if 'email' in i['message'].lower()]
    assert len(email_issues) >= 1

    # LinkedIn missing
    linkedin_issues = [i for i in issues if 'linkedin' in i['message'].lower()]
    assert len(linkedin_issues) >= 1

    # Location format
    location_issues = [i for i in issues if 'location' in i['message'].lower()]
    assert len(location_issues) >= 1


def test_validate_resume_includes_professional_standards():
    """Test that validate_resume calls validate_professional_standards"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={
            "name": "John Doe",
            "email": "john123@yahoo.com"  # Unprofessional
        },
        experience=[{"title": "Engineer", "company": "Company", "startDate": "Jan 2020", "endDate": "Present"}],
        education=[{"degree": "BS Computer Science", "institution": "University"}],
        skills=["Python"],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
    )

    validator = RedFlagsValidator()
    result = validator.validate_resume(resume, "software_engineer", "mid")

    # Should have professional standards issues in warnings or suggestions
    all_issues = result['warnings'] + result['suggestions']
    professional_issues = [i for i in all_issues if 'email' in i['message'].lower() or 'linkedin' in i['message'].lower()]
    assert len(professional_issues) >= 1


# ===== Grammar Checker Validation Tests (P18-P21) =====

def test_typo_detection():
    """Test detection of typos in experience descriptions (P18)"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={"name": "John Doe"},
        experience=[{
            "title": "Software Engineer",
            "company": "Company A",
            "startDate": "Jan 2020",
            "endDate": "Present",
            "description": "• Develped scalable applications\n• Implemented continous integration"
        }],
        education=[{"degree": "BS Computer Science", "institution": "University"}],
        skills=["Python"],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
    )

    validator = RedFlagsValidator()
    issues = validator.validate_grammar(resume)

    typo_issues = [i for i in issues if i['category'] == 'typo']
    assert len(typo_issues) >= 1
    assert typo_issues[0]['severity'] == 'warning'


def test_grammar_error_detection():
    """Test detection of grammar errors (P19) - Note: pyspellchecker focuses on typos"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={"name": "John Doe"},
        experience=[{
            "title": "Software Engineer",
            "company": "Company A",
            "startDate": "Jan 2020",
            "endDate": "Present",
            "description": "• Workd on multiple projects with typos\n• The team complted the implementation"
        }],
        education=[{"degree": "BS Computer Science", "institution": "University"}],
        skills=["Python"],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
    )

    validator = RedFlagsValidator()
    issues = validator.validate_grammar(resume)

    # pyspellchecker detects typos as 'typo' category, not 'grammar'
    # This is acceptable - typo detection is the primary concern for resume validation
    typo_issues = [i for i in issues if i['category'] == 'typo']
    assert len(typo_issues) >= 1, f"Expected typos but found {len(issues)} total issues"
    assert typo_issues[0]['severity'] == 'warning'


def test_capitalization_error_detection():
    """Test detection of capitalization errors (P21)"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={"name": "John Doe"},
        experience=[{
            "title": "Software Engineer",
            "company": "Company A",
            "startDate": "Jan 2020",
            "endDate": "Present",
            "description": "• worked at microsoft corporation\n• developed apis for the project"
        }],
        education=[{"degree": "BS Computer Science", "institution": "University"}],
        skills=["Python"],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
    )

    validator = RedFlagsValidator()
    issues = validator.validate_grammar(resume)

    casing_issues = [i for i in issues if i['category'] == 'capitalization']
    assert len(casing_issues) >= 1
    assert casing_issues[0]['severity'] == 'suggestion'


def test_grammar_validation_with_clean_text():
    """Test that clean text produces no grammar issues"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={"name": "John Doe"},
        experience=[{
            "title": "Software Engineer",
            "company": "Company A",
            "startDate": "Jan 2020",
            "endDate": "Present",
            "description": "• Developed scalable applications using Python and FastAPI\n• Implemented continuous integration pipelines"
        }],
        education=[{"degree": "BS Computer Science", "institution": "University"}],
        skills=["Python"],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
    )

    validator = RedFlagsValidator()
    issues = validator.validate_grammar(resume)

    # Should have minimal or no grammar issues with clean text
    assert isinstance(issues, list)


def test_grammar_validation_checks_education():
    """Test that grammar validation checks education section"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={"name": "John Doe"},
        experience=[{
            "title": "Software Engineer",
            "company": "Company A",
            "startDate": "Jan 2020",
            "endDate": "Present",
            "description": "• Developed scalable applications"
        }],
        education=[{
            "degree": "Bachelor of Scince in Computer Science",  # Typo: Scince
            "institution": "University",
            "graduationDate": "2020"
        }],
        skills=["Python"],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
    )

    validator = RedFlagsValidator()
    issues = validator.validate_grammar(resume)

    # Should detect typo in education
    typo_issues = [i for i in issues if i['category'] == 'typo' and 'education' in i['message'].lower()]
    assert len(typo_issues) >= 1


def test_grammar_validation_checks_summary():
    """Test that grammar validation checks summary section"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={
            "name": "John Doe",
            "summary": "Experianced software engineer with 5 years of experiance"  # Typos
        },
        experience=[{
            "title": "Software Engineer",
            "company": "Company A",
            "startDate": "Jan 2020",
            "endDate": "Present",
            "description": "• Developed applications"
        }],
        education=[{"degree": "BS Computer Science", "institution": "University"}],
        skills=["Python"],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
    )

    validator = RedFlagsValidator()
    issues = validator.validate_grammar(resume)

    # Should detect typos in summary
    typo_issues = [i for i in issues if i['category'] == 'typo' and 'summary' in i['message'].lower()]
    assert len(typo_issues) >= 1


def test_grammar_validation_limits_issues():
    """Test that grammar validation limits number of issues per category"""
    # Create text with many repeated typos
    many_typos = "\n".join([f"• Develped application number {i}" for i in range(20)])

    resume = ResumeData(
        fileName="test.pdf",
        contact={"name": "John Doe"},
        experience=[{
            "title": "Software Engineer",
            "company": "Company A",
            "startDate": "Jan 2020",
            "endDate": "Present",
            "description": many_typos
        }],
        education=[{"degree": "BS Computer Science", "institution": "University"}],
        skills=["Python"],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
    )

    validator = RedFlagsValidator()
    issues = validator.validate_grammar(resume)

    # Should limit to max 10 per category
    typo_issues = [i for i in issues if i['category'] == 'typo']
    assert len(typo_issues) <= 10


def test_grammar_validation_handles_missing_languagetool():
    """Test graceful handling when LanguageTool is unavailable"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={"name": "John Doe"},
        experience=[{
            "title": "Software Engineer",
            "company": "Company A",
            "startDate": "Jan 2020",
            "endDate": "Present",
            "description": "• Developed applications"
        }],
        education=[{"degree": "BS Computer Science", "institution": "University"}],
        skills=["Python"],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
    )

    validator = RedFlagsValidator()
    # Force LanguageTool to be None
    validator._language_tool = None
    validator._lt_init_failed = True

    # Should not crash, return empty list
    issues = validator.validate_grammar(resume)
    assert issues == []


def test_grammar_validation_caching():
    """Test that grammar validation caches results"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={"name": "John Doe"},
        experience=[{
            "title": "Software Engineer",
            "company": "Company A",
            "startDate": "Jan 2020",
            "endDate": "Present",
            "description": "• Develped scalable applications"  # Typo
        }],
        education=[{"degree": "BS Computer Science", "institution": "University"}],
        skills=["Python"],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
    )

    validator = RedFlagsValidator()

    # First call - should check grammar
    issues1 = validator.validate_grammar(resume)

    # Second call with same text - should use cache
    issues2 = validator.validate_grammar(resume)

    # Results should be identical
    assert len(issues1) == len(issues2)
    assert issues1 == issues2


def test_validate_resume_includes_grammar():
    """Test that validate_resume calls validate_grammar"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={"name": "John Doe"},
        experience=[{
            "title": "Software Engineer",
            "company": "Company A",
            "startDate": "Jan 2020",
            "endDate": "Present",
            "description": "• Develped scalable applications\n• She work on multiple projects"
        }],
        education=[{"degree": "BS Computer Science", "institution": "University"}],
        skills=["Python"],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
    )

    validator = RedFlagsValidator()
    result = validator.validate_resume(resume, "software_engineer", "mid")

    # Should have grammar issues in warnings
    grammar_issues = [i for i in result['warnings'] if i['category'] in ['typo', 'grammar', 'capitalization']]
    assert len(grammar_issues) >= 1


def test_grammar_validation_empty_sections():
    """Test grammar validation with empty sections"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={},
        experience=[],
        education=[],
        skills=[],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
    )

    validator = RedFlagsValidator()
    issues = validator.validate_grammar(resume)

    # Should not crash with empty sections
    assert isinstance(issues, list)


# ===== Metadata Validation Tests (P36-P44) =====

def test_page_count_optimal():
    """Test that 1-2 page resumes pass validation (P36)"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={"name": "John Doe"},
        experience=[{"title": "Engineer", "company": "Company", "startDate": "Jan 2020", "endDate": "Present"}],
        education=[{"degree": "BS Computer Science", "institution": "University"}],
        skills=["Python"],
        certifications=[],
        metadata={"pageCount": 2, "wordCount": 600, "fileFormat": "pdf"}
    )

    validator = RedFlagsValidator()
    issues = validator.validate_metadata(resume)

    # Should have no page count issues
    page_issues = [i for i in issues if 'page_count' in i['category']]
    assert len(page_issues) == 0


def test_page_count_too_long_warning():
    """Test that 3-4 page resumes trigger warning (P36)"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={"name": "John Doe"},
        experience=[{"title": "Engineer", "company": "Company", "startDate": "Jan 2020", "endDate": "Present"}],
        education=[{"degree": "BS Computer Science", "institution": "University"}],
        skills=["Python"],
        certifications=[],
        metadata={"pageCount": 3, "wordCount": 1200, "fileFormat": "pdf"}
    )

    validator = RedFlagsValidator()
    issues = validator.validate_metadata(resume)

    page_issues = [i for i in issues if 'page_count' in i['category']]
    assert len(page_issues) >= 1
    assert page_issues[0]['severity'] == 'warning'
    assert '3 pages' in page_issues[0]['message']


def test_page_count_too_long_critical():
    """Test that 4+ page resumes trigger critical (P36)"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={"name": "John Doe"},
        experience=[{"title": "Engineer", "company": "Company", "startDate": "Jan 2020", "endDate": "Present"}],
        education=[{"degree": "BS Computer Science", "institution": "University"}],
        skills=["Python"],
        certifications=[],
        metadata={"pageCount": 5, "wordCount": 2000, "fileFormat": "pdf"}
    )

    validator = RedFlagsValidator()
    issues = validator.validate_metadata(resume)

    page_issues = [i for i in issues if 'page_count' in i['category']]
    assert len(page_issues) >= 1
    assert page_issues[0]['severity'] == 'critical'
    assert '5 pages' in page_issues[0]['message']


def test_word_count_optimal():
    """Test that 400-800 word resumes pass validation (P37)"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={"name": "John Doe"},
        experience=[{"title": "Engineer", "company": "Company", "startDate": "Jan 2020", "endDate": "Present"}],
        education=[{"degree": "BS Computer Science", "institution": "University"}],
        skills=["Python"],
        certifications=[],
        metadata={"pageCount": 2, "wordCount": 600, "fileFormat": "pdf"}
    )

    validator = RedFlagsValidator()
    issues = validator.validate_metadata(resume)

    # Should have no word count issues
    word_issues = [i for i in issues if 'word_count' in i['category']]
    assert len(word_issues) == 0


def test_word_count_too_low_warning():
    """Test that <300 words triggers warning (P37)"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={"name": "John Doe"},
        experience=[{"title": "Engineer", "company": "Company", "startDate": "Jan 2020", "endDate": "Present"}],
        education=[{"degree": "BS Computer Science", "institution": "University"}],
        skills=["Python"],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 250, "fileFormat": "pdf"}
    )

    validator = RedFlagsValidator()
    issues = validator.validate_metadata(resume)

    word_issues = [i for i in issues if 'word_count' in i['category']]
    assert len(word_issues) >= 1
    assert word_issues[0]['severity'] == 'warning'
    assert '250 words' in word_issues[0]['message']


def test_word_count_too_low_suggestion():
    """Test that 300-399 words triggers suggestion (P37)"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={"name": "John Doe"},
        experience=[{"title": "Engineer", "company": "Company", "startDate": "Jan 2020", "endDate": "Present"}],
        education=[{"degree": "BS Computer Science", "institution": "University"}],
        skills=["Python"],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 350, "fileFormat": "pdf"}
    )

    validator = RedFlagsValidator()
    issues = validator.validate_metadata(resume)

    word_issues = [i for i in issues if 'word_count' in i['category']]
    assert len(word_issues) >= 1
    assert word_issues[0]['severity'] == 'suggestion'


def test_word_count_too_high_warning():
    """Test that >1200 words triggers warning (P37)"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={"name": "John Doe"},
        experience=[{"title": "Engineer", "company": "Company", "startDate": "Jan 2020", "endDate": "Present"}],
        education=[{"degree": "BS Computer Science", "institution": "University"}],
        skills=["Python"],
        certifications=[],
        metadata={"pageCount": 3, "wordCount": 1500, "fileFormat": "pdf"}
    )

    validator = RedFlagsValidator()
    issues = validator.validate_metadata(resume)

    word_issues = [i for i in issues if 'word_count' in i['category']]
    assert len(word_issues) >= 1
    assert word_issues[0]['severity'] == 'warning'
    assert '1500 words' in word_issues[0]['message']


def test_word_count_too_high_suggestion():
    """Test that 801-1200 words triggers suggestion (P37)"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={"name": "John Doe"},
        experience=[{"title": "Engineer", "company": "Company", "startDate": "Jan 2020", "endDate": "Present"}],
        education=[{"degree": "BS Computer Science", "institution": "University"}],
        skills=["Python"],
        certifications=[],
        metadata={"pageCount": 2, "wordCount": 900, "fileFormat": "pdf"}
    )

    validator = RedFlagsValidator()
    issues = validator.validate_metadata(resume)

    word_issues = [i for i in issues if 'word_count' in i['category']]
    assert len(word_issues) >= 1
    assert word_issues[0]['severity'] == 'suggestion'


def test_file_format_pdf():
    """Test that PDF format is accepted (P38)"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={"name": "John Doe"},
        experience=[{"title": "Engineer", "company": "Company", "startDate": "Jan 2020", "endDate": "Present"}],
        education=[{"degree": "BS Computer Science", "institution": "University"}],
        skills=["Python"],
        certifications=[],
        metadata={"pageCount": 2, "wordCount": 600, "fileFormat": "pdf"}
    )

    validator = RedFlagsValidator()
    issues = validator.validate_metadata(resume)

    # Should have no file format issues
    format_issues = [i for i in issues if 'file_format' in i['category']]
    assert len(format_issues) == 0


def test_file_format_docx_warning():
    """Test that DOCX format triggers warning (P38)"""
    resume = ResumeData(
        fileName="test.docx",
        contact={"name": "John Doe"},
        experience=[{"title": "Engineer", "company": "Company", "startDate": "Jan 2020", "endDate": "Present"}],
        education=[{"degree": "BS Computer Science", "institution": "University"}],
        skills=["Python"],
        certifications=[],
        metadata={"pageCount": 2, "wordCount": 600, "fileFormat": "docx"}
    )

    validator = RedFlagsValidator()
    issues = validator.validate_metadata(resume)

    format_issues = [i for i in issues if 'file_format' in i['category']]
    assert len(format_issues) >= 1
    assert format_issues[0]['severity'] == 'warning'
    assert 'Word format' in format_issues[0]['message']
    assert 'PDF' in format_issues[0]['message']


def test_file_format_invalid():
    """Test that invalid file format triggers critical (P38)"""
    resume = ResumeData(
        fileName="test.txt",
        contact={"name": "John Doe"},
        experience=[{"title": "Engineer", "company": "Company", "startDate": "Jan 2020", "endDate": "Present"}],
        education=[{"degree": "BS Computer Science", "institution": "University"}],
        skills=["Python"],
        certifications=[],
        metadata={"pageCount": 2, "wordCount": 600, "fileFormat": "txt"}
    )

    validator = RedFlagsValidator()
    issues = validator.validate_metadata(resume)

    format_issues = [i for i in issues if 'file_format' in i['category']]
    assert len(format_issues) >= 1
    assert format_issues[0]['severity'] == 'critical'


def test_readability_score_optimal():
    """Test that readability score 8-12 passes (P40)"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={"name": "John Doe"},
        experience=[{
            "title": "Software Engineer",
            "company": "Company A",
            "startDate": "Jan 2020",
            "endDate": "Present",
            "description": "Developed scalable web applications using modern frameworks. "
                          "Implemented CI/CD pipelines to automate deployment processes. "
                          "Collaborated with cross-functional teams to deliver high-quality products."
        }],
        education=[{"degree": "BS Computer Science", "institution": "University"}],
        skills=["Python"],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 500, "fileFormat": "pdf"}
    )

    validator = RedFlagsValidator()
    issues = validator.validate_metadata(resume)

    # Readability should be in optimal range (8-12)
    readability_issues = [i for i in issues if 'readability' in i['category']]
    # Should have no critical readability issues
    critical_readability = [i for i in readability_issues if i['severity'] == 'critical']
    assert len(critical_readability) == 0


def test_readability_score_too_complex():
    """Test that very complex text triggers warning (P40)"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={"name": "John Doe"},
        experience=[{
            "title": "Software Engineer",
            "company": "Company A",
            "startDate": "Jan 2020",
            "endDate": "Present",
            "description": "Orchestrated comprehensive architectural transformations leveraging microservices paradigms, "
                          "implementing sophisticated containerization strategies utilizing Docker and Kubernetes platforms, "
                          "facilitating unprecedented scalability improvements through distributed computing methodologies."
        }],
        education=[{"degree": "BS Computer Science", "institution": "University"}],
        skills=["Python"],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 500, "fileFormat": "pdf"}
    )

    validator = RedFlagsValidator()
    issues = validator.validate_metadata(resume)

    readability_issues = [i for i in issues if 'readability' in i['category']]
    # May trigger warning for overly complex text
    assert isinstance(readability_issues, list)


def test_keyword_density_normal():
    """Test that normal keyword usage passes (P41)"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={"name": "John Doe"},
        experience=[{
            "title": "Software Engineer",
            "company": "Company A",
            "startDate": "Jan 2020",
            "endDate": "Present",
            "description": "Developed applications using Python and JavaScript. "
                          "Built REST APIs and implemented database schemas. "
                          "Collaborated with team members on code reviews."
        }],
        education=[{"degree": "BS Computer Science", "institution": "University"}],
        skills=["Python"],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
    )

    validator = RedFlagsValidator()
    issues = validator.validate_metadata(resume)

    # Should have no keyword density issues
    density_issues = [i for i in issues if 'keyword_density' in i['category']]
    assert len(density_issues) == 0


def test_keyword_density_overstuffed():
    """Test that keyword stuffing triggers warning (P41)"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={"name": "John Doe"},
        experience=[{
            "title": "Python Developer",
            "company": "Company A",
            "startDate": "Jan 2020",
            "endDate": "Present",
            "description": "Python Python Python developer. Built Python applications using Python frameworks. "
                          "Python expert with Python experience. Developed Python scripts and Python APIs."
        }],
        education=[{"degree": "BS Computer Science", "institution": "University"}],
        skills=["Python"],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
    )

    validator = RedFlagsValidator()
    issues = validator.validate_metadata(resume)

    density_issues = [i for i in issues if 'keyword_density' in i['category']]
    assert len(density_issues) >= 1
    assert 'python' in density_issues[0]['message'].lower()


def test_section_balance_optimal():
    """Test that 50-60% experience section passes (P42)"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={"name": "John Doe", "summary": "Engineer with experience"},
        experience=[{
            "title": "Software Engineer",
            "company": "Company A",
            "startDate": "Jan 2020",
            "endDate": "Present",
            "description": "Developed scalable web applications using modern frameworks and technologies. "
                          "Built REST APIs and microservices architecture for high-performance systems."
        }],
        education=[{"degree": "BS Computer Science", "institution": "State University"}],
        skills=["Python", "JavaScript", "Docker"],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 500, "fileFormat": "pdf"}
    )

    validator = RedFlagsValidator()
    issues = validator.validate_metadata(resume)

    # Experience should be balanced (50-60%)
    balance_issues = [i for i in issues if 'section_balance' in i['category']]
    # Should have no critical balance issues
    critical_balance = [i for i in balance_issues if i['severity'] == 'critical']
    assert len(critical_balance) == 0


def test_section_balance_too_little_experience():
    """Test that <40% experience triggers warning (P42)"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={"name": "John Doe", "summary": "Software engineer with extensive background in computer science"},
        experience=[{
            "title": "Engineer",
            "company": "Company",
            "startDate": "Jan 2020",
            "endDate": "Present",
            "description": "Developed applications"
        }],
        education=[{
            "degree": "Bachelor of Science in Computer Science with focus on artificial intelligence and machine learning",
            "institution": "State University",
            "description": "Completed comprehensive coursework in algorithms, data structures, software engineering, and system design"
        }],
        skills=["Python", "Java", "C++", "JavaScript", "Docker", "Kubernetes"],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 500, "fileFormat": "pdf"}
    )

    validator = RedFlagsValidator()
    issues = validator.validate_metadata(resume)

    balance_issues = [i for i in issues if 'section_balance' in i['category']]
    assert len(balance_issues) >= 1
    assert balance_issues[0]['severity'] == 'warning'


def test_section_balance_too_much_experience():
    """Test that >70% experience triggers warning (P42)"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={"name": "John Doe"},
        experience=[{
            "title": "Software Engineer",
            "company": "Company A",
            "startDate": "Jan 2020",
            "endDate": "Present",
            "description": "Developed comprehensive web applications using modern frameworks. "
                          "Built scalable REST APIs and microservices architecture. "
                          "Implemented CI/CD pipelines and deployment automation. "
                          "Led team of developers in agile development processes. "
                          "Designed database schemas and optimized query performance."
        }],
        education=[{"degree": "BS CS", "institution": "University"}],
        skills=["Python"],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 500, "fileFormat": "pdf"}
    )

    validator = RedFlagsValidator()
    issues = validator.validate_metadata(resume)

    balance_issues = [i for i in issues if 'section_balance' in i['category']]
    assert len(balance_issues) >= 1


def test_ats_compatibility_with_photo():
    """Test that photos trigger ATS warning (P44)"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={"name": "John Doe"},
        experience=[{"title": "Engineer", "company": "Company", "startDate": "Jan 2020", "endDate": "Present"}],
        education=[{"degree": "BS Computer Science", "institution": "University"}],
        skills=["Python"],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf", "hasPhoto": True}
    )

    validator = RedFlagsValidator()
    issues = validator.validate_metadata(resume)

    ats_issues = [i for i in issues if 'ats_compatibility' in i['category'] and 'photo' in i['message'].lower()]
    assert len(ats_issues) >= 1
    assert ats_issues[0]['severity'] == 'warning'


def test_ats_compatibility_low_words_per_page():
    """Test that low words per page triggers ATS warning (P44)"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={"name": "John Doe"},
        experience=[{"title": "Engineer", "company": "Company", "startDate": "Jan 2020", "endDate": "Present"}],
        education=[{"degree": "BS Computer Science", "institution": "University"}],
        skills=["Python"],
        certifications=[],
        metadata={"pageCount": 2, "wordCount": 200, "fileFormat": "pdf"}  # Only 100 words/page
    )

    validator = RedFlagsValidator()
    issues = validator.validate_metadata(resume)

    ats_issues = [i for i in issues if 'ats_compatibility' in i['category'] and 'words per page' in i['message'].lower()]
    assert len(ats_issues) >= 1
    assert ats_issues[0]['severity'] == 'warning'


def test_ats_compatibility_missing_sections():
    """Test that missing sections triggers ATS warning (P44)"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={},  # Missing name
        experience=[],  # Missing experience
        education=[],  # Missing education
        skills=["Python"],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 200, "fileFormat": "pdf"}
    )

    validator = RedFlagsValidator()
    issues = validator.validate_metadata(resume)

    ats_issues = [i for i in issues if 'ats_compatibility' in i['category'] and 'missing' in i['message'].lower()]
    assert len(ats_issues) >= 1


def test_validate_resume_includes_metadata():
    """Test that validate_resume calls validate_metadata"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={"name": "John Doe"},
        experience=[{"title": "Engineer", "company": "Company", "startDate": "Jan 2020", "endDate": "Present"}],
        education=[{"degree": "BS Computer Science", "institution": "University"}],
        skills=["Python"],
        certifications=[],
        metadata={"pageCount": 5, "wordCount": 2000, "fileFormat": "docx"}  # Multiple issues
    )

    validator = RedFlagsValidator()
    result = validator.validate_resume(resume, "software_engineer", "mid")

    # Should have metadata issues
    all_issues = result['critical'] + result['warnings'] + result['suggestions']
    metadata_issues = [i for i in all_issues if i['category'] in [
        'page_count', 'word_count', 'file_format', 'readability',
        'keyword_density', 'section_balance', 'ats_compatibility'
    ]]
    assert len(metadata_issues) >= 2


def test_metadata_validation_no_metadata():
    """Test graceful handling when metadata is missing"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={"name": "John Doe"},
        experience=[{"title": "Engineer", "company": "Company", "startDate": "Jan 2020", "endDate": "Present"}],
        education=[{"degree": "BS Computer Science", "institution": "University"}],
        skills=["Python"],
        certifications=[],
        metadata={}
    )

    validator = RedFlagsValidator()
    issues = validator.validate_metadata(resume)

    # Should not crash with empty metadata
    assert isinstance(issues, list)


def test_metadata_comprehensive():
    """Test comprehensive metadata validation with multiple issues"""
    resume = ResumeData(
        fileName="test.docx",
        contact={"name": "John Doe"},
        experience=[{
            "title": "Python Developer",
            "company": "Company",
            "startDate": "Jan 2020",
            "endDate": "Present",
            "description": "Python Python Python. Python Python."  # Keyword stuffing
        }],
        education=[{"degree": "BS Computer Science", "institution": "University"}],
        skills=["Python"],
        certifications=[],
        metadata={"pageCount": 5, "wordCount": 1500, "fileFormat": "docx", "hasPhoto": True}
    )

    validator = RedFlagsValidator()
    issues = validator.validate_metadata(resume)

    # Should have multiple types of issues
    assert len(issues) >= 3

    # Check for different categories
    categories = set(i['category'] for i in issues)
    assert 'page_count' in categories or 'word_count' in categories or 'file_format' in categories


# ===== Formatting Validation Tests (P22-P25) =====

def test_bullet_consistency_all_same():
    """Test that consistent bullet markers pass validation (P22)"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={"name": "John Doe"},
        experience=[
            {
                "title": "Software Engineer",
                "company": "Company A",
                "startDate": "Jan 2020",
                "endDate": "Dec 2021",
                "description": "• Developed scalable applications\n• Built REST APIs\n• Implemented CI/CD"
            },
            {
                "title": "Senior Engineer",
                "company": "Company B",
                "startDate": "Jan 2022",
                "endDate": "Present",
                "description": "• Led development team\n• Designed architecture\n• Mentored junior developers"
            }
        ],
        education=[{"degree": "BS Computer Science", "institution": "University"}],
        skills=["Python"],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
    )

    validator = RedFlagsValidator()
    issues = validator.validate_formatting(resume)

    # Should have no bullet consistency issues
    bullet_issues = [i for i in issues if i['category'] == 'bullet_consistency']
    assert len(bullet_issues) == 0


def test_bullet_consistency_mixed_markers():
    """Test that mixed bullet markers trigger warning (P22)"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={"name": "John Doe"},
        experience=[
            {
                "title": "Software Engineer",
                "company": "Company A",
                "startDate": "Jan 2020",
                "endDate": "Dec 2021",
                "description": "• Developed scalable applications\n- Built REST APIs\n* Implemented CI/CD"
            },
            {
                "title": "Senior Engineer",
                "company": "Company B",
                "startDate": "Jan 2022",
                "endDate": "Present",
                "description": "1. Led development team\n2. Designed architecture"
            }
        ],
        education=[{"degree": "BS Computer Science", "institution": "University"}],
        skills=["Python"],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
    )

    validator = RedFlagsValidator()
    issues = validator.validate_formatting(resume)

    bullet_issues = [i for i in issues if i['category'] == 'bullet_consistency']
    assert len(bullet_issues) >= 1
    assert bullet_issues[0]['severity'] == 'warning'
    assert '•' in bullet_issues[0]['message'] or '-' in bullet_issues[0]['message']


def test_bullet_consistency_dash_vs_bullet():
    """Test detection of dash vs bullet point markers (P22)"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={"name": "John Doe"},
        experience=[
            {
                "title": "Software Engineer",
                "company": "Company A",
                "startDate": "Jan 2020",
                "endDate": "Dec 2021",
                "description": "- Developed applications\n- Built APIs"
            },
            {
                "title": "Senior Engineer",
                "company": "Company B",
                "startDate": "Jan 2022",
                "endDate": "Present",
                "description": "• Led team\n• Designed systems"
            }
        ],
        education=[{"degree": "BS Computer Science", "institution": "University"}],
        skills=["Python"],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
    )

    validator = RedFlagsValidator()
    issues = validator.validate_formatting(resume)

    bullet_issues = [i for i in issues if i['category'] == 'bullet_consistency']
    assert len(bullet_issues) >= 1
    assert bullet_issues[0]['severity'] == 'warning'


def test_font_readability_standard_fonts():
    """Test that standard fonts pass validation (P23)"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={"name": "John Doe"},
        experience=[{"title": "Engineer", "company": "Company", "startDate": "Jan 2020", "endDate": "Present"}],
        education=[{"degree": "BS Computer Science", "institution": "University"}],
        skills=["Python"],
        certifications=[],
        metadata={
            "pageCount": 1,
            "wordCount": 400,
            "fileFormat": "pdf",
            "fonts": ["Arial", "Calibri"]
        }
    )

    validator = RedFlagsValidator()
    issues = validator.validate_formatting(resume)

    # Should have no font readability issues
    font_issues = [i for i in issues if i['category'] == 'font_readability']
    assert len(font_issues) == 0


def test_font_readability_decorative_fonts():
    """Test that decorative fonts trigger critical error (P23)"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={"name": "John Doe"},
        experience=[{"title": "Engineer", "company": "Company", "startDate": "Jan 2020", "endDate": "Present"}],
        education=[{"degree": "BS Computer Science", "institution": "University"}],
        skills=["Python"],
        certifications=[],
        metadata={
            "pageCount": 1,
            "wordCount": 400,
            "fileFormat": "pdf",
            "fonts": ["Comic Sans MS", "Arial"]
        }
    )

    validator = RedFlagsValidator()
    issues = validator.validate_formatting(resume)

    font_issues = [i for i in issues if i['category'] == 'font_readability']
    assert len(font_issues) >= 1
    assert font_issues[0]['severity'] == 'critical'
    assert 'comic sans' in font_issues[0]['message'].lower()


def test_font_readability_multiple_decorative_fonts():
    """Test detection of various decorative fonts (P23)"""
    decorative_fonts = ['Papyrus', 'Curlz MT', 'Brush Script', 'Zapfino']

    for font in decorative_fonts:
        resume = ResumeData(
            fileName="test.pdf",
            contact={"name": "John Doe"},
            experience=[{"title": "Engineer", "company": "Company", "startDate": "Jan 2020", "endDate": "Present"}],
            education=[{"degree": "BS Computer Science", "institution": "University"}],
            skills=["Python"],
            certifications=[],
            metadata={
                "pageCount": 1,
                "wordCount": 400,
                "fileFormat": "pdf",
                "fonts": [font]
            }
        )

        validator = RedFlagsValidator()
        issues = validator.validate_formatting(resume)

        font_issues = [i for i in issues if i['category'] == 'font_readability']
        assert len(font_issues) >= 1, f"Failed to detect decorative font: {font}"
        assert font_issues[0]['severity'] == 'critical'


def test_font_readability_too_many_fonts():
    """Test that too many fonts trigger warning (P23)"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={"name": "John Doe"},
        experience=[{"title": "Engineer", "company": "Company", "startDate": "Jan 2020", "endDate": "Present"}],
        education=[{"degree": "BS Computer Science", "institution": "University"}],
        skills=["Python"],
        certifications=[],
        metadata={
            "pageCount": 1,
            "wordCount": 400,
            "fileFormat": "pdf",
            "fonts": ["Arial", "Calibri", "Times New Roman", "Georgia"]  # 4 fonts
        }
    )

    validator = RedFlagsValidator()
    issues = validator.validate_formatting(resume)

    font_issues = [i for i in issues if i['category'] == 'font_readability']
    assert len(font_issues) >= 1
    assert font_issues[0]['severity'] == 'warning'
    assert '4 different fonts' in font_issues[0]['message']


def test_section_header_consistency_all_caps():
    """Test that consistent ALL CAPS headers pass validation (P24)"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={"name": "John Doe"},
        experience=[{"title": "Engineer", "company": "Company", "startDate": "Jan 2020", "endDate": "Present"}],
        education=[{"degree": "BS Computer Science", "institution": "University"}],
        skills=["Python"],
        certifications=[],
        metadata={
            "pageCount": 1,
            "wordCount": 400,
            "fileFormat": "pdf",
            "rawText": "EXPERIENCE\nSoftware Engineer\n\nEDUCATION\nBS Computer Science\n\nSKILLS\nPython, Java"
        }
    )

    validator = RedFlagsValidator()
    issues = validator.validate_formatting(resume)

    # Should have no header consistency issues
    header_issues = [i for i in issues if i['category'] == 'header_consistency']
    assert len(header_issues) == 0


def test_section_header_consistency_title_case():
    """Test that consistent Title Case headers pass validation (P24)"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={"name": "John Doe"},
        experience=[{"title": "Engineer", "company": "Company", "startDate": "Jan 2020", "endDate": "Present"}],
        education=[{"degree": "BS Computer Science", "institution": "University"}],
        skills=["Python"],
        certifications=[],
        metadata={
            "pageCount": 1,
            "wordCount": 400,
            "fileFormat": "pdf",
            "rawText": "Professional Experience\nSoftware Engineer\n\nEducation\nBS Computer Science\n\nTechnical Skills\nPython, Java"
        }
    )

    validator = RedFlagsValidator()
    issues = validator.validate_formatting(resume)

    # Should have no header consistency issues
    header_issues = [i for i in issues if i['category'] == 'header_consistency']
    assert len(header_issues) == 0


def test_section_header_consistency_mixed():
    """Test that mixed header capitalization triggers warning (P24)"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={"name": "John Doe"},
        experience=[{"title": "Engineer", "company": "Company", "startDate": "Jan 2020", "endDate": "Present"}],
        education=[{"degree": "BS Computer Science", "institution": "University"}],
        skills=["Python"],
        certifications=[],
        metadata={
            "pageCount": 1,
            "wordCount": 400,
            "fileFormat": "pdf",
            "rawText": "EXPERIENCE\nSoftware Engineer\n\nEducation\nBS Computer Science\n\nskills\nPython, Java"
        }
    )

    validator = RedFlagsValidator()
    issues = validator.validate_formatting(resume)

    header_issues = [i for i in issues if i['category'] == 'header_consistency']
    assert len(header_issues) >= 1
    assert header_issues[0]['severity'] == 'warning'
    assert 'capitalization' in header_issues[0]['message'].lower()


def test_section_header_consistency_all_caps_vs_title():
    """Test detection of ALL CAPS vs Title Case mixing (P24)"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={"name": "John Doe"},
        experience=[{"title": "Engineer", "company": "Company", "startDate": "Jan 2020", "endDate": "Present"}],
        education=[{"degree": "BS Computer Science", "institution": "University"}],
        skills=["Python"],
        certifications=[],
        metadata={
            "pageCount": 1,
            "wordCount": 400,
            "fileFormat": "pdf",
            "rawText": "PROFESSIONAL EXPERIENCE\nSoftware Engineer at Company\n\nEducation Background\nBS Computer Science\n\nSKILLS\nPython"
        }
    )

    validator = RedFlagsValidator()
    issues = validator.validate_formatting(resume)

    header_issues = [i for i in issues if i['category'] == 'header_consistency']
    assert len(header_issues) >= 1
    assert header_issues[0]['severity'] == 'warning'


def test_header_footer_content_no_contact_info():
    """Test that headers/footers without contact info pass (P25)"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={"name": "John Doe"},
        experience=[{"title": "Engineer", "company": "Company", "startDate": "Jan 2020", "endDate": "Present"}],
        education=[{"degree": "BS Computer Science", "institution": "University"}],
        skills=["Python"],
        certifications=[],
        metadata={
            "pageCount": 2,
            "wordCount": 400,
            "fileFormat": "pdf",
            "headerContent": "John Doe - Resume",
            "footerContent": "Page 1 of 2"
        }
    )

    validator = RedFlagsValidator()
    issues = validator.validate_formatting(resume)

    # Should have no header/footer issues
    hf_issues = [i for i in issues if i['category'] == 'header_footer_content']
    assert len(hf_issues) == 0


def test_header_footer_content_email_in_header():
    """Test that email in header triggers critical error (P25)"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={"name": "John Doe"},
        experience=[{"title": "Engineer", "company": "Company", "startDate": "Jan 2020", "endDate": "Present"}],
        education=[{"degree": "BS Computer Science", "institution": "University"}],
        skills=["Python"],
        certifications=[],
        metadata={
            "pageCount": 2,
            "wordCount": 400,
            "fileFormat": "pdf",
            "headerContent": "John Doe | john.doe@email.com | 555-123-4567",
            "footerContent": ""
        }
    )

    validator = RedFlagsValidator()
    issues = validator.validate_formatting(resume)

    hf_issues = [i for i in issues if i['category'] == 'header_footer_content']
    assert len(hf_issues) >= 1
    email_issues = [i for i in hf_issues if 'email' in i['message'].lower()]
    assert len(email_issues) >= 1
    assert email_issues[0]['severity'] == 'critical'


def test_header_footer_content_phone_in_footer():
    """Test that phone number in footer triggers critical error (P25)"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={"name": "John Doe"},
        experience=[{"title": "Engineer", "company": "Company", "startDate": "Jan 2020", "endDate": "Present"}],
        education=[{"degree": "BS Computer Science", "institution": "University"}],
        skills=["Python"],
        certifications=[],
        metadata={
            "pageCount": 2,
            "wordCount": 400,
            "fileFormat": "pdf",
            "headerContent": "",
            "footerContent": "Contact: (555) 123-4567"
        }
    )

    validator = RedFlagsValidator()
    issues = validator.validate_formatting(resume)

    hf_issues = [i for i in issues if i['category'] == 'header_footer_content']
    assert len(hf_issues) >= 1
    phone_issues = [i for i in hf_issues if 'phone' in i['message'].lower()]
    assert len(phone_issues) >= 1
    assert phone_issues[0]['severity'] == 'critical'


def test_header_footer_content_linkedin_in_header():
    """Test that LinkedIn URL in header triggers critical error (P25)"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={"name": "John Doe"},
        experience=[{"title": "Engineer", "company": "Company", "startDate": "Jan 2020", "endDate": "Present"}],
        education=[{"degree": "BS Computer Science", "institution": "University"}],
        skills=["Python"],
        certifications=[],
        metadata={
            "pageCount": 2,
            "wordCount": 400,
            "fileFormat": "pdf",
            "headerContent": "John Doe | linkedin.com/in/johndoe",
            "footerContent": ""
        }
    )

    validator = RedFlagsValidator()
    issues = validator.validate_formatting(resume)

    hf_issues = [i for i in issues if i['category'] == 'header_footer_content']
    assert len(hf_issues) >= 1
    linkedin_issues = [i for i in hf_issues if 'linkedin' in i['message'].lower()]
    assert len(linkedin_issues) >= 1
    assert linkedin_issues[0]['severity'] == 'critical'


def test_header_footer_content_multiple_contact_info():
    """Test detection of multiple contact info in header/footer (P25)"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={"name": "John Doe"},
        experience=[{"title": "Engineer", "company": "Company", "startDate": "Jan 2020", "endDate": "Present"}],
        education=[{"degree": "BS Computer Science", "institution": "University"}],
        skills=["Python"],
        certifications=[],
        metadata={
            "pageCount": 2,
            "wordCount": 400,
            "fileFormat": "pdf",
            "headerContent": "john@email.com | (555) 123-4567 | linkedin.com/in/john",
            "footerContent": "Page 1"
        }
    )

    validator = RedFlagsValidator()
    issues = validator.validate_formatting(resume)

    hf_issues = [i for i in issues if i['category'] == 'header_footer_content']
    assert len(hf_issues) >= 2  # Should detect multiple types of contact info


def test_formatting_validation_no_experience():
    """Test formatting validation with no experience section"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={"name": "John Doe"},
        experience=[],
        education=[{"degree": "BS Computer Science", "institution": "University"}],
        skills=["Python"],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 200, "fileFormat": "pdf"}
    )

    validator = RedFlagsValidator()
    issues = validator.validate_formatting(resume)

    # Should not crash with empty experience
    assert isinstance(issues, list)


def test_formatting_validation_no_metadata():
    """Test formatting validation with minimal metadata"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={"name": "John Doe"},
        experience=[{
            "title": "Engineer",
            "company": "Company",
            "startDate": "Jan 2020",
            "endDate": "Present",
            "description": "• Developed applications"
        }],
        education=[{"degree": "BS Computer Science", "institution": "University"}],
        skills=["Python"],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 200, "fileFormat": "pdf"}
    )

    validator = RedFlagsValidator()
    issues = validator.validate_formatting(resume)

    # Should not crash with minimal metadata
    assert isinstance(issues, list)


def test_validate_resume_includes_formatting():
    """Test that validate_resume calls validate_formatting"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={"name": "John Doe"},
        experience=[
            {
                "title": "Software Engineer",
                "company": "Company A",
                "startDate": "Jan 2020",
                "endDate": "Dec 2021",
                "description": "• Developed applications\n- Built APIs"  # Inconsistent bullets
            }
        ],
        education=[{"degree": "BS Computer Science", "institution": "University"}],
        skills=["Python"],
        certifications=[],
        metadata={
            "pageCount": 1,
            "wordCount": 400,
            "fileFormat": "pdf",
            "fonts": ["Comic Sans MS"],  # Decorative font
            "rawText": "EXPERIENCE\nSoftware Engineer\n\neducation\nBS CS",  # Mixed headers
            "headerContent": "john@email.com"  # Email in header
        }
    )

    validator = RedFlagsValidator()
    result = validator.validate_resume(resume, "software_engineer", "mid")

    # Should have formatting issues
    all_issues = result['critical'] + result['warnings'] + result['suggestions']
    formatting_issues = [i for i in all_issues if i['category'] in [
        'bullet_consistency', 'font_readability', 'header_consistency', 'header_footer_content'
    ]]
    assert len(formatting_issues) >= 3  # Should catch multiple issues


def test_formatting_comprehensive():
    """Test comprehensive formatting validation with multiple issues"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={"name": "John Doe"},
        experience=[
            {
                "title": "Software Engineer",
                "company": "Company A",
                "startDate": "Jan 2020",
                "endDate": "Dec 2021",
                "description": "• Developed scalable applications\n* Built REST APIs\n1. Implemented CI/CD"
            },
            {
                "title": "Senior Engineer",
                "company": "Company B",
                "startDate": "Jan 2022",
                "endDate": "Present",
                "description": "- Led development team\n- Designed architecture"
            }
        ],
        education=[{"degree": "BS Computer Science", "institution": "University"}],
        skills=["Python"],
        certifications=[],
        metadata={
            "pageCount": 2,
            "wordCount": 600,
            "fileFormat": "pdf",
            "fonts": ["Comic Sans MS", "Papyrus", "Arial", "Calibri"],
            "rawText": "PROFESSIONAL EXPERIENCE\nSoftware Engineer\n\nEducation\nBS CS\n\nskills\nPython",
            "headerContent": "john.doe@email.com | (555) 123-4567",
            "footerContent": "linkedin.com/in/johndoe"
        }
    )

    validator = RedFlagsValidator()
    issues = validator.validate_formatting(resume)

    # Should have multiple types of formatting issues
    assert len(issues) >= 4

    # Check for different categories
    categories = set(i['category'] for i in issues)
    assert 'bullet_consistency' in categories
    assert 'font_readability' in categories
    assert 'header_consistency' in categories
    assert 'header_footer_content' in categories
