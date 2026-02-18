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
