#!/usr/bin/env python3
"""
Simple test runner to verify grammar improvements.
Runs tests and shows results.
"""

import sys
from services.red_flags_validator import RedFlagsValidator
from services.parser import ResumeData


def test_resume_vocabulary():
    """Test that technical terms are not flagged"""
    print("Testing resume vocabulary...")

    validator = RedFlagsValidator()

    # Test case: Technical resume with many tech terms
    resume = ResumeData(
        fileName="test.pdf",
        contact={"name": "Test User"},
        experience=[{
            "title": "Software Engineer",
            "company": "Tech Company",
            "startDate": "Jan 2020",
            "endDate": "Present",
            "description": (
                "Developed microservices using Python, Django, and PostgreSQL. "
                "Deployed applications on AWS using Docker and Kubernetes. "
                "Implemented CI/CD pipelines with Jenkins and GitLab. "
                "Built REST APIs with React and Node.js frontend."
            )
        }],
        education=[],
        skills=["Python"],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
    )

    result = validator.validate_grammar(resume)
    typo_issues = [i for i in result if i['category'] == 'typo']

    if len(typo_issues) <= 1:
        print(f"✓ PASS: Resume vocabulary test (found {len(typo_issues)} false positives)")
        return True
    else:
        print(f"✗ FAIL: Resume vocabulary test (found {len(typo_issues)} false positives)")
        for issue in typo_issues:
            print(f"  - {issue['message']}")
        return False


def test_verb_tense_detection():
    """Test detection of mixed verb tenses"""
    print("Testing verb tense detection...")

    validator = RedFlagsValidator()

    resume = ResumeData(
        fileName="test.pdf",
        contact={"name": "Test User"},
        experience=[{
            "title": "Software Engineer",
            "company": "Tech Company",
            "startDate": "Jan 2020",
            "endDate": "Present",
            "description": "Managed a team of engineers and developing new features"
        }],
        education=[],
        skills=["Python"],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
    )

    result = validator.validate_grammar(resume)
    grammar_issues = [i for i in result if i['category'] == 'grammar']

    if any('tense' in i['message'].lower() for i in grammar_issues):
        print("✓ PASS: Verb tense detection")
        return True
    else:
        print("✗ FAIL: Verb tense detection (should detect mixed tenses)")
        return False


def test_plural_with_numbers():
    """Test detection of singular nouns with numbers"""
    print("Testing plural/singular with numbers...")

    validator = RedFlagsValidator()

    resume = ResumeData(
        fileName="test.pdf",
        contact={"name": "Test User"},
        experience=[{
            "title": "Software Engineer",
            "company": "Tech Company",
            "startDate": "Jan 2020",
            "endDate": "Present",
            "description": "Software engineer with 5 year of experience"
        }],
        education=[],
        skills=["Python"],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
    )

    result = validator.validate_grammar(resume)
    grammar_issues = [i for i in result if i['category'] == 'grammar']

    if any('years' in i['message'].lower() or 'plural' in i['message'].lower()
           for i in grammar_issues):
        print("✓ PASS: Plural detection")
        return True
    else:
        print("✗ FAIL: Plural detection (should detect 'year' vs 'years')")
        return False


def test_passive_voice_detection():
    """Test detection of passive voice"""
    print("Testing passive voice detection...")

    validator = RedFlagsValidator()

    resume = ResumeData(
        fileName="test.pdf",
        contact={"name": "Test User"},
        experience=[{
            "title": "Software Engineer",
            "company": "Tech Company",
            "startDate": "Jan 2020",
            "endDate": "Present",
            "description": (
                "The project was completed by the team. "
                "The features were implemented by me."
            )
        }],
        education=[],
        skills=["Python"],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
    )

    result = validator.validate_grammar(resume)
    grammar_issues = [i for i in result if i['category'] == 'grammar']

    if any('passive' in i['message'].lower() or 'active' in i['message'].lower()
           for i in grammar_issues):
        print("✓ PASS: Passive voice detection")
        return True
    else:
        print("✗ FAIL: Passive voice detection")
        return False


def test_article_errors():
    """Test detection of missing articles"""
    print("Testing article error detection...")

    validator = RedFlagsValidator()

    resume = ResumeData(
        fileName="test.pdf",
        contact={"name": "Test User"},
        experience=[{
            "title": "Software Engineer",
            "company": "Tech Company",
            "startDate": "Jan 2020",
            "endDate": "Present",
            "description": "I am engineer with 5 years of experience"
        }],
        education=[],
        skills=["Python"],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
    )

    result = validator.validate_grammar(resume)
    grammar_issues = [i for i in result if i['category'] == 'grammar']

    if any('article' in i['message'].lower() for i in grammar_issues):
        print("✓ PASS: Article error detection")
        return True
    else:
        print("✗ FAIL: Article error detection")
        return False


def test_preposition_errors():
    """Test detection of incorrect prepositions"""
    print("Testing preposition error detection...")

    validator = RedFlagsValidator()

    resume = ResumeData(
        fileName="test.pdf",
        contact={"name": "Test User"},
        experience=[{
            "title": "Software Engineer",
            "company": "Tech Company",
            "startDate": "Jan 2020",
            "endDate": "Present",
            "description": "Worked in Google as a software engineer"
        }],
        education=[],
        skills=["Python"],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
    )

    result = validator.validate_grammar(resume)
    grammar_issues = [i for i in result if i['category'] == 'grammar']

    if any('at' in i['message'].lower() or 'preposition' in i['message'].lower()
           for i in grammar_issues):
        print("✓ PASS: Preposition error detection")
        return True
    else:
        print("✗ FAIL: Preposition error detection")
        return False


def test_long_sentence_detection():
    """Test detection of run-on sentences"""
    print("Testing long sentence detection...")

    validator = RedFlagsValidator()

    long_sentence = (
        "I managed a team of ten software engineers and we worked on multiple "
        "projects simultaneously and delivered them all on time and within budget "
        "while maintaining high quality standards and meeting all stakeholder "
        "requirements and expectations throughout the entire development cycle "
        "from planning to deployment."
    )

    resume = ResumeData(
        fileName="test.pdf",
        contact={"name": "Test User"},
        experience=[{
            "title": "Software Engineer",
            "company": "Tech Company",
            "startDate": "Jan 2020",
            "endDate": "Present",
            "description": long_sentence
        }],
        education=[],
        skills=["Python"],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
    )

    result = validator.validate_grammar(resume)
    grammar_issues = [i for i in result if i['category'] == 'grammar']

    if any('long' in i['message'].lower() or 'sentence' in i['message'].lower()
           for i in grammar_issues):
        print("✓ PASS: Long sentence detection")
        return True
    else:
        print("✗ FAIL: Long sentence detection")
        return False


def test_good_grammar_no_false_positives():
    """Test that good grammar doesn't trigger false positives"""
    print("Testing no false positives on good grammar...")

    validator = RedFlagsValidator()

    resume = ResumeData(
        fileName="test.pdf",
        contact={"name": "Test User"},
        experience=[{
            "title": "Senior Software Engineer",
            "company": "Tech Company",
            "startDate": "Jan 2020",
            "endDate": "Present",
            "description": (
                "Led a team of 5 engineers in developing scalable microservices. "
                "Implemented CI/CD pipelines using Jenkins and Docker. "
                "Improved system performance by 40% through optimization."
            )
        }],
        education=[],
        skills=["Python"],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
    )

    result = validator.validate_grammar(resume)
    grammar_issues = [i for i in result if i['category'] == 'grammar']

    if len(grammar_issues) <= 1:
        print(f"✓ PASS: No false positives (found {len(grammar_issues)} issues)")
        return True
    else:
        print(f"✗ FAIL: Too many false positives (found {len(grammar_issues)} issues)")
        for issue in grammar_issues:
            print(f"  - {issue['message']}")
        return False


def main():
    """Run all tests and report results"""
    print("\n" + "=" * 60)
    print("Grammar Improvements Test Suite - Solution 1")
    print("=" * 60 + "\n")

    tests = [
        test_resume_vocabulary,
        test_verb_tense_detection,
        test_plural_with_numbers,
        test_passive_voice_detection,
        test_article_errors,
        test_preposition_errors,
        test_long_sentence_detection,
        test_good_grammar_no_false_positives,
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"✗ ERROR: {test.__name__} - {str(e)}")
            results.append(False)
        print()

    # Summary
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    percentage = (passed / total * 100) if total > 0 else 0

    print(f"Results: {passed}/{total} tests passed ({percentage:.0f}%)")
    print("=" * 60 + "\n")

    if passed == total:
        print("✓ All tests passed! Grammar improvements are working correctly.")
        return 0
    else:
        print(f"✗ {total - passed} test(s) failed. Review the output above.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
