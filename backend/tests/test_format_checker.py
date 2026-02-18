"""Tests for ATS format checker"""
from services.format_checker import ATSFormatChecker
from services.parser import ResumeData


def test_format_checker_passes_good_resume():
    """Test format checker passes well-formatted resume"""
    resume = ResumeData(
        fileName="good.pdf",
        contact={"name": "John Doe", "email": "john@example.com"},
        experience=[{"description": "- Led team of 10 engineers developing cloud infrastructure\n- Built scalable microservices architecture handling 1M requests per day\n- Implemented CI/CD pipeline reducing deployment time by 60%\n- Mentored junior developers and conducted code reviews\n- Drove adoption of best practices across engineering team"}],
        education=[{"degree": "BS Computer Science", "institution": "University of Technology"}],
        skills=["Python", "AWS", "Docker", "Kubernetes", "React"],
        metadata={"pageCount": 1, "wordCount": 500, "hasPhoto": False, "fileFormat": "pdf"}
    )

    # More realistic raw text with 200+ words
    raw_text = """John Doe
john@example.com | (555) 123-4567 | linkedin.com/in/johndoe

PROFESSIONAL SUMMARY
Senior Software Engineer with 8 years of experience building scalable cloud infrastructure and leading high-performing engineering teams.

EXPERIENCE

Senior Software Engineer | Tech Corp | San Francisco, CA | 2020-Present
- Led team of 10 engineers developing cloud infrastructure using AWS and Kubernetes
- Built scalable microservices architecture handling 1 million requests per day with 99.9% uptime
- Implemented CI/CD pipeline reducing deployment time by 60% and improving developer productivity
- Mentored junior developers and conducted code reviews to maintain code quality
- Drove adoption of best practices and engineering standards across the organization

Software Engineer | StartupXYZ | Remote | 2018-2020
- Developed RESTful APIs serving mobile and web applications
- Optimized database queries improving performance by 40%
- Collaborated with product team to deliver features on schedule

EDUCATION

BS Computer Science | University of Technology | 2018
GPA: 3.8/4.0 | Dean's List

SKILLS

Python, JavaScript, AWS, Docker, Kubernetes, React, Node.js, PostgreSQL, MongoDB, Redis"""

    checker = ATSFormatChecker()
    result = checker.check_format(resume, raw_text)

    assert result["passed"] == True
    assert result["score"] >= 0.8
    assert "text_extraction" in result["checks"]
    assert "sections_detected" in result["checks"]


def test_format_checker_fails_poor_resume():
    """Test format checker fails poorly formatted resume"""
    resume = ResumeData(
        fileName="poor.pdf",
        contact={},
        experience=[],
        education=[],
        skills=[],
        metadata={"pageCount": 1, "wordCount": 50, "hasPhoto": True, "fileFormat": "pdf"}
    )

    raw_text = "��� garbled text ���"

    checker = ATSFormatChecker()
    result = checker.check_format(resume, raw_text)

    assert result["passed"] == False
    assert result["score"] < 0.8
    assert len(result["issues"]) > 0
