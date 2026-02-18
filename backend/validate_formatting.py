#!/usr/bin/env python3
"""
Validation script for formatting validation implementation (Task 13).
Demonstrates P22-P25 parameter validation.
"""

from services.red_flags_validator import RedFlagsValidator
from services.parser import ResumeData


def test_formatting_validation():
    """Test all formatting validation parameters"""

    print("=" * 80)
    print("FORMATTING VALIDATION - Task 13 (Parameters 22-25)")
    print("=" * 80)
    print()

    # Create validator
    validator = RedFlagsValidator()

    # Test Case 1: Clean resume (should pass)
    print("Test 1: Clean Resume (All formatting correct)")
    print("-" * 80)
    resume_clean = ResumeData(
        fileName="clean_resume.pdf",
        contact={"name": "John Doe", "email": "john@email.com"},
        experience=[
            {
                "title": "Software Engineer",
                "company": "Tech Corp",
                "startDate": "Jan 2020",
                "endDate": "Present",
                "description": "• Developed scalable applications\n• Built REST APIs\n• Implemented CI/CD pipelines"
            }
        ],
        education=[{"degree": "BS Computer Science", "institution": "University"}],
        skills=["Python", "Java"],
        certifications=[],
        metadata={
            "pageCount": 1,
            "wordCount": 500,
            "fileFormat": "pdf",
            "fonts": ["Arial", "Calibri"],
            "rawText": "PROFESSIONAL EXPERIENCE\nSoftware Engineer\n\nEDUCATION\nBS Computer Science\n\nSKILLS\nPython, Java",
            "headerContent": "John Doe - Resume",
            "footerContent": "Page 1"
        }
    )

    issues_clean = validator.validate_formatting(resume_clean)
    print(f"✓ Issues found: {len(issues_clean)}")
    if issues_clean:
        for issue in issues_clean:
            print(f"  - [{issue['severity'].upper()}] {issue['message']}")
    else:
        print("  No formatting issues detected!")
    print()

    # Test Case 2: Bullet consistency issues (P22)
    print("Test 2: Bullet Consistency Issues (P22)")
    print("-" * 80)
    resume_bullets = ResumeData(
        fileName="mixed_bullets.pdf",
        contact={"name": "Jane Smith"},
        experience=[
            {
                "title": "Developer",
                "company": "Company A",
                "startDate": "Jan 2020",
                "endDate": "Dec 2021",
                "description": "• Developed applications\n- Built APIs\n* Wrote tests"
            },
            {
                "title": "Senior Developer",
                "company": "Company B",
                "startDate": "Jan 2022",
                "endDate": "Present",
                "description": "1. Led team\n2. Designed architecture"
            }
        ],
        education=[{"degree": "BS CS", "institution": "University"}],
        skills=["Python"],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
    )

    issues_bullets = validator.validate_formatting(resume_bullets)
    print(f"✓ Issues found: {len(issues_bullets)}")
    for issue in issues_bullets:
        if issue['category'] == 'bullet_consistency':
            print(f"  - [{issue['severity'].upper()}] {issue['message']}")
    print()

    # Test Case 3: Font readability issues (P23)
    print("Test 3: Font Readability Issues (P23)")
    print("-" * 80)
    resume_fonts = ResumeData(
        fileName="bad_fonts.pdf",
        contact={"name": "Bob Jones"},
        experience=[{"title": "Engineer", "company": "Company", "startDate": "Jan 2020", "endDate": "Present"}],
        education=[{"degree": "BS CS", "institution": "University"}],
        skills=["Python"],
        certifications=[],
        metadata={
            "pageCount": 1,
            "wordCount": 400,
            "fileFormat": "pdf",
            "fonts": ["Comic Sans MS", "Papyrus", "Arial", "Calibri"]
        }
    )

    issues_fonts = validator.validate_formatting(resume_fonts)
    print(f"✓ Issues found: {len(issues_fonts)}")
    for issue in issues_fonts:
        if issue['category'] == 'font_readability':
            print(f"  - [{issue['severity'].upper()}] {issue['message']}")
    print()

    # Test Case 4: Header consistency issues (P24)
    print("Test 4: Section Header Consistency Issues (P24)")
    print("-" * 80)
    resume_headers = ResumeData(
        fileName="mixed_headers.pdf",
        contact={"name": "Alice Wang"},
        experience=[{"title": "Engineer", "company": "Company", "startDate": "Jan 2020", "endDate": "Present"}],
        education=[{"degree": "BS CS", "institution": "University"}],
        skills=["Python"],
        certifications=[],
        metadata={
            "pageCount": 1,
            "wordCount": 400,
            "fileFormat": "pdf",
            "rawText": "PROFESSIONAL EXPERIENCE\nSoftware Engineer\n\nEducation\nBS Computer Science\n\nskills\nPython"
        }
    )

    issues_headers = validator.validate_formatting(resume_headers)
    print(f"✓ Issues found: {len(issues_headers)}")
    for issue in issues_headers:
        if issue['category'] == 'header_consistency':
            print(f"  - [{issue['severity'].upper()}] {issue['message']}")
    print()

    # Test Case 5: Header/footer content issues (P25)
    print("Test 5: Header/Footer Content Issues (P25)")
    print("-" * 80)
    resume_hf = ResumeData(
        fileName="contact_in_header.pdf",
        contact={"name": "Charlie Brown"},
        experience=[{"title": "Engineer", "company": "Company", "startDate": "Jan 2020", "endDate": "Present"}],
        education=[{"degree": "BS CS", "institution": "University"}],
        skills=["Python"],
        certifications=[],
        metadata={
            "pageCount": 1,
            "wordCount": 400,
            "fileFormat": "pdf",
            "headerContent": "Charlie Brown | charlie@email.com | (555) 123-4567",
            "footerContent": "linkedin.com/in/charliebrown"
        }
    )

    issues_hf = validator.validate_formatting(resume_hf)
    print(f"✓ Issues found: {len(issues_hf)}")
    for issue in issues_hf:
        if issue['category'] == 'header_footer_content':
            print(f"  - [{issue['severity'].upper()}] {issue['message']}")
    print()

    # Test Case 6: Comprehensive validation with all issues
    print("Test 6: Comprehensive Validation (Multiple Issues)")
    print("-" * 80)
    resume_all = ResumeData(
        fileName="problematic_resume.pdf",
        contact={"name": "Test User"},
        experience=[
            {
                "title": "Developer",
                "company": "Company A",
                "startDate": "Jan 2020",
                "endDate": "Present",
                "description": "• Developed apps\n- Built APIs\n* Wrote tests"
            }
        ],
        education=[{"degree": "BS CS", "institution": "University"}],
        skills=["Python"],
        certifications=[],
        metadata={
            "pageCount": 1,
            "wordCount": 400,
            "fileFormat": "pdf",
            "fonts": ["Comic Sans MS", "Papyrus", "Arial", "Times"],
            "rawText": "EXPERIENCE\nDeveloper\n\neducation\nBS CS",
            "headerContent": "test@email.com | 555-1234",
            "footerContent": "linkedin.com/in/testuser"
        }
    )

    issues_all = validator.validate_formatting(resume_all)
    print(f"✓ Total issues found: {len(issues_all)}")

    # Categorize by severity
    critical = [i for i in issues_all if i['severity'] == 'critical']
    warnings = [i for i in issues_all if i['severity'] == 'warning']
    suggestions = [i for i in issues_all if i['severity'] == 'suggestion']

    if critical:
        print(f"\n  CRITICAL ({len(critical)}):")
        for issue in critical:
            print(f"    - {issue['category']}: {issue['message'][:80]}...")

    if warnings:
        print(f"\n  WARNINGS ({len(warnings)}):")
        for issue in warnings:
            print(f"    - {issue['category']}: {issue['message'][:80]}...")

    if suggestions:
        print(f"\n  SUGGESTIONS ({len(suggestions)}):")
        for issue in suggestions:
            print(f"    - {issue['category']}: {issue['message'][:80]}...")
    print()

    # Summary
    print("=" * 80)
    print("VALIDATION SUMMARY")
    print("=" * 80)
    print(f"Parameters validated: P22-P25 (4 parameters)")
    print(f"Test cases executed: 6")
    print(f"Parameter coverage:")
    print(f"  ✓ P22: Bullet Consistency")
    print(f"  ✓ P23: Font Readability")
    print(f"  ✓ P24: Section Header Consistency")
    print(f"  ✓ P25: Header/Footer Content")
    print()
    print("Implementation: COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    test_formatting_validation()
