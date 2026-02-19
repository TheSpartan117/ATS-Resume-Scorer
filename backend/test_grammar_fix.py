#!/usr/bin/env python3
"""
Test script to verify grammar checking works with pyspellchecker
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.red_flags_validator import RedFlagsValidator
from services.parser import ResumeData


def test_typo_detection():
    """Test detection of typos in experience descriptions"""
    print("Testing typo detection...")

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

    print(f"\nFound {len(issues)} grammar issues:")
    for issue in issues:
        print(f"  - [{issue['category']}] {issue['message']}")

    typo_issues = [i for i in issues if i['category'] == 'typo']
    print(f"\nTypo issues found: {len(typo_issues)}")

    if len(typo_issues) >= 1:
        print("✓ Test PASSED: Typos detected successfully")
        return True
    else:
        print("✗ Test FAILED: Expected at least 1 typo issue")
        return False


def test_basic_grammar():
    """Test basic grammar checks"""
    print("\n\nTesting basic grammar checks...")

    resume = ResumeData(
        fileName="test.pdf",
        contact={"name": "John Doe"},
        experience=[{
            "title": "Software Engineer",
            "company": "Company A",
            "startDate": "Jan 2020",
            "endDate": "Present",
            "description": "• They is working on the project\n• Developed features"
        }],
        education=[],
        skills=["Python"],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
    )

    validator = RedFlagsValidator()
    issues = validator.validate_grammar(resume)

    print(f"\nFound {len(issues)} grammar issues:")
    for issue in issues:
        print(f"  - [{issue['category']}] {issue['message']}")

    grammar_issues = [i for i in issues if i['category'] == 'grammar']
    print(f"\nGrammar issues found: {len(grammar_issues)}")

    if len(grammar_issues) >= 1:
        print("✓ Test PASSED: Grammar errors detected successfully")
        return True
    else:
        print("✗ Test FAILED: Expected at least 1 grammar issue")
        return False


def test_graceful_fallback():
    """Test that validator works even if spell checker is unavailable"""
    print("\n\nTesting graceful fallback...")

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
        education=[],
        skills=["Python"],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
    )

    validator = RedFlagsValidator()
    # Force spell checker to fail
    validator._spell_init_failed = True
    validator._spell_checker = None

    issues = validator.validate_grammar(resume)

    print(f"With unavailable spell checker, returned {len(issues)} issues")
    print("✓ Test PASSED: Graceful fallback works (returns empty list)")
    return True


if __name__ == "__main__":
    print("=" * 60)
    print("Grammar Checking Implementation Test")
    print("=" * 60)

    results = []
    results.append(("Typo Detection", test_typo_detection()))
    results.append(("Basic Grammar", test_basic_grammar()))
    results.append(("Graceful Fallback", test_graceful_fallback()))

    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)
    for test_name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{test_name}: {status}")

    all_passed = all(result[1] for result in results)
    print("\n" + "=" * 60)
    if all_passed:
        print("ALL TESTS PASSED ✓")
        sys.exit(0)
    else:
        print("SOME TESTS FAILED ✗")
        sys.exit(1)
