#!/usr/bin/env python3
"""
Debug script for ATS scorer issues.
Tests various scenarios to identify problems.
"""

import sys
import json
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from services.scorer_ats import ATSScorer
from services.parser import ResumeData
from services.keyword_matcher import KeywordMatcher
from services.red_flags_validator import RedFlagsValidator


def create_test_resume(scenario="good"):
    """Create test resume for different scenarios"""

    if scenario == "good":
        return ResumeData(
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
                "description": "Developed scalable web applications using Python, Django, REST APIs, PostgreSQL, Docker, and Kubernetes. Led team of 3 developers."
            }],
            education=[{
                "degree": "BS Computer Science",
                "institution": "Stanford University"
            }],
            skills=["Python", "Django", "REST API", "PostgreSQL", "Docker", "Kubernetes", "AWS", "React"],
            certifications=[],
            metadata={
                "pageCount": 1,
                "wordCount": 500,
                "fileFormat": "pdf",
                "hasPhoto": False
            }
        )

    elif scenario == "with_jd_keywords":
        return ResumeData(
            fileName="test.pdf",
            contact={
                "name": "Jane Smith",
                "email": "jane@example.com",
                "phone": "555-1234",
                "location": "NYC",
                "linkedin": "linkedin.com/in/janesmith"
            },
            experience=[{
                "title": "Senior Python Developer",
                "company": "Tech Corp",
                "startDate": "Jan 2019",
                "endDate": "Present",
                "description": "Expert in Python programming with Django framework. Built REST APIs using FastAPI. Database design with PostgreSQL. Cloud deployment on AWS. Containerization with Docker."
            }],
            education=[{
                "degree": "MS Computer Science",
                "institution": "MIT"
            }],
            skills=["Python", "Django", "FastAPI", "PostgreSQL", "REST API", "AWS", "Docker", "Git"],
            certifications=[{"name": "AWS Certified Developer"}],
            metadata={
                "pageCount": 2,
                "wordCount": 650,
                "fileFormat": "pdf",
                "hasPhoto": False
            }
        )

    elif scenario == "poor":
        return ResumeData(
            fileName="test.pdf",
            contact={},  # No contact info
            experience=[],  # No experience
            education=[],  # No education
            skills=[],  # No skills
            certifications=[],
            metadata={
                "pageCount": 5,
                "wordCount": 100,
                "fileFormat": "doc",
                "hasPhoto": True
            }
        )

    elif scenario == "no_jd":
        return ResumeData(
            fileName="test.pdf",
            contact={
                "name": "Bob Johnson",
                "email": "bob@example.com"
            },
            experience=[{
                "title": "Developer",
                "company": "Some Company",
                "startDate": "Jan 2022",
                "endDate": "Present",
                "description": "Did stuff"
            }],
            education=[{
                "degree": "BS",
                "institution": "College"
            }],
            skills=["JavaScript", "HTML"],
            certifications=[],
            metadata={
                "pageCount": 1,
                "wordCount": 300,
                "fileFormat": "pdf"
            }
        )


def test_keyword_matcher():
    """Test keyword matcher component"""
    print("\n" + "="*80)
    print("TEST 1: KEYWORD MATCHER")
    print("="*80)

    matcher = KeywordMatcher()

    # Test with role keywords
    resume_text = "Python Django REST API PostgreSQL Docker Kubernetes AWS React"

    print("\n1.1 Testing role-based keyword matching (software_engineer, mid)...")
    result = matcher.match_role_keywords(resume_text, "software_engineer", "mid")
    print(f"   Result: {result}")
    print(f"   Percentage: {result['percentage']:.1f}%")
    print(f"   Matched: {len(result['matched'])} keywords")
    print(f"   Missing: {len(result['missing'])} keywords")

    # Test with job description
    job_desc = """
    We need a Python developer with Django and REST API experience.
    Must know PostgreSQL, Docker, and AWS.
    React experience is a plus.
    """

    print("\n1.2 Testing job description matching...")
    result_jd = matcher.match_job_description(resume_text, job_desc)
    print(f"   Result: {result_jd}")
    print(f"   Percentage: {result_jd['percentage']:.1f}%")
    print(f"   Matched: {len(result_jd['matched'])} keywords")
    print(f"   Missing: {len(result_jd['missing'])} keywords")

    return result, result_jd


def test_red_flags_validator():
    """Test red flags validator component"""
    print("\n" + "="*80)
    print("TEST 2: RED FLAGS VALIDATOR")
    print("="*80)

    validator = RedFlagsValidator()

    # Test with good resume
    good_resume = create_test_resume("good")
    print("\n2.1 Testing with good resume...")
    result = validator.validate_resume(good_resume, "software_engineer", "mid")
    print(f"   Critical issues: {len(result['critical'])}")
    print(f"   Warnings: {len(result['warnings'])}")
    print(f"   Suggestions: {len(result['suggestions'])}")

    if result['critical']:
        print(f"   Critical issues:")
        for issue in result['critical'][:3]:
            print(f"      - {issue['message']}")

    # Test with poor resume
    poor_resume = create_test_resume("poor")
    print("\n2.2 Testing with poor resume...")
    result_poor = validator.validate_resume(poor_resume, "software_engineer", "mid")
    print(f"   Critical issues: {len(result_poor['critical'])}")
    print(f"   Warnings: {len(result_poor['warnings'])}")

    if result_poor['critical']:
        print(f"   Critical issues:")
        for issue in result_poor['critical'][:5]:
            print(f"      - {issue['message']}")

    return result, result_poor


def test_ats_scorer_components():
    """Test individual ATS scorer components"""
    print("\n" + "="*80)
    print("TEST 3: ATS SCORER COMPONENTS")
    print("="*80)

    scorer = ATSScorer()
    resume = create_test_resume("good")

    # Test keywords scoring
    print("\n3.1 Testing _score_keywords...")
    keywords_result = scorer._score_keywords(resume, "software_engineer", "mid", "")
    print(f"   Score: {keywords_result['score']}/{keywords_result['maxScore']}")
    print(f"   Percentage: {keywords_result['details']['percentage']:.1f}%")
    print(f"   Matched: {keywords_result['details']['matched_count']}")
    print(f"   Missing: {keywords_result['details']['missing_count']}")
    print(f"   Message: {keywords_result['details']['message']}")

    # Test with job description
    job_desc = "Python Django REST API PostgreSQL Docker developer"
    print("\n3.2 Testing _score_keywords with job description...")
    keywords_jd = scorer._score_keywords(resume, "software_engineer", "mid", job_desc)
    print(f"   Score: {keywords_jd['score']}/{keywords_jd['maxScore']}")
    print(f"   Percentage: {keywords_jd['details']['percentage']:.1f}%")

    # Test red flags scoring
    print("\n3.3 Testing _score_red_flags...")
    red_flags = scorer._score_red_flags(resume, "software_engineer", "mid")
    print(f"   Score: {red_flags['score']}/{red_flags['maxScore']}")
    print(f"   Critical: {red_flags['details']['critical_count']}")
    print(f"   Warnings: {red_flags['details']['warning_count']}")
    print(f"   Message: {red_flags['details']['message']}")

    # Test experience scoring
    print("\n3.4 Testing _score_experience...")
    experience = scorer._score_experience(resume, "mid")
    print(f"   Score: {experience['score']}/{experience['maxScore']}")
    print(f"   Total years: {experience['details']['total_years']}")
    print(f"   Years message: {experience['details'].get('years_message', 'N/A')}")
    print(f"   Recency message: {experience['details'].get('recency_message', 'N/A')}")
    print(f"   Relevance message: {experience['details'].get('relevance_message', 'N/A')}")

    # Test formatting scoring
    print("\n3.5 Testing _score_formatting...")
    formatting = scorer._score_formatting(resume)
    print(f"   Score: {formatting['score']}/{formatting['maxScore']}")
    print(f"   Page count: {formatting['details']['page_count']}")
    print(f"   File format: {formatting['details']['file_format']}")
    print(f"   Has photo: {formatting['details']['has_photo']}")
    print(f"   Word count: {formatting['details']['word_count']}")

    # Test contact info scoring
    print("\n3.6 Testing _score_contact_info...")
    contact = scorer._score_contact_info(resume)
    print(f"   Score: {contact['score']}/{contact['maxScore']}")
    print(f"   Message: {contact['details']['message']}")

    return {
        'keywords': keywords_result,
        'keywords_jd': keywords_jd,
        'red_flags': red_flags,
        'experience': experience,
        'formatting': formatting,
        'contact': contact
    }


def test_full_ats_scoring():
    """Test full ATS scoring with different scenarios"""
    print("\n" + "="*80)
    print("TEST 4: FULL ATS SCORING")
    print("="*80)

    scorer = ATSScorer()

    # Scenario 1: Good resume without JD
    print("\n4.1 Good resume without job description...")
    resume1 = create_test_resume("good")
    result1 = scorer.score(resume1, "software_engineer", "mid", "")
    print(f"   Total score: {result1['score']}/100")
    print(f"   Breakdown:")
    for category, data in result1['breakdown'].items():
        print(f"      {category}: {data['score']}/{data['maxScore']}")

    # Scenario 2: Good resume with matching JD
    print("\n4.2 Good resume with matching job description...")
    job_desc = """
    We are looking for a Python developer with Django experience.
    Must have REST API development skills and PostgreSQL database knowledge.
    Docker and Kubernetes experience required.
    AWS cloud experience preferred.
    """
    result2 = scorer.score(resume1, "software_engineer", "mid", job_desc)
    print(f"   Total score: {result2['score']}/100")
    print(f"   Breakdown:")
    for category, data in result2['breakdown'].items():
        print(f"      {category}: {data['score']}/{data['maxScore']}")

    # Scenario 3: Resume with excellent JD match
    print("\n4.3 Resume with excellent job description match...")
    resume2 = create_test_resume("with_jd_keywords")
    result3 = scorer.score(resume2, "software_engineer", "senior", job_desc)
    print(f"   Total score: {result3['score']}/100")
    print(f"   Keyword percentage: {result3['breakdown']['keywords']['details']['percentage']:.1f}%")
    print(f"   Breakdown:")
    for category, data in result3['breakdown'].items():
        print(f"      {category}: {data['score']}/{data['maxScore']}")

    # Scenario 4: Poor resume
    print("\n4.4 Poor quality resume...")
    resume3 = create_test_resume("poor")
    result4 = scorer.score(resume3, "software_engineer", "mid", "")
    print(f"   Total score: {result4['score']}/100")
    print(f"   Breakdown:")
    for category, data in result4['breakdown'].items():
        print(f"      {category}: {data['score']}/{data['maxScore']}")

    # Scenario 5: Resume without JD, different role
    print("\n4.5 Resume without job description (entry level)...")
    resume4 = create_test_resume("no_jd")
    result5 = scorer.score(resume4, "software_engineer", "entry", "")
    print(f"   Total score: {result5['score']}/100")
    print(f"   Breakdown:")
    for category, data in result5['breakdown'].items():
        print(f"      {category}: {data['score']}/{data['maxScore']}")

    return {
        'good_no_jd': result1,
        'good_with_jd': result2,
        'excellent_match': result3,
        'poor': result4,
        'no_jd_entry': result5
    }


def test_edge_cases():
    """Test edge cases and error conditions"""
    print("\n" + "="*80)
    print("TEST 5: EDGE CASES")
    print("="*80)

    scorer = ATSScorer()

    # Edge case 1: Empty resume
    print("\n5.1 Empty resume...")
    try:
        empty_resume = ResumeData(
            fileName="empty.pdf",
            contact={},
            experience=[],
            education=[],
            skills=[],
            certifications=[],
            metadata={"pageCount": 0, "wordCount": 0, "fileFormat": "pdf"}
        )
        result = scorer.score(empty_resume, "software_engineer", "mid", "")
        print(f"   Score: {result['score']}/100 (should be very low)")
    except Exception as e:
        print(f"   ERROR: {e}")

    # Edge case 2: Resume with special characters
    print("\n5.2 Resume with special characters...")
    try:
        special_resume = create_test_resume("good")
        special_resume.skills = ["C++", "C#", ".NET", "Node.js"]
        result = scorer.score(special_resume, "software_engineer", "mid", "")
        print(f"   Score: {result['score']}/100")
    except Exception as e:
        print(f"   ERROR: {e}")

    # Edge case 3: Very long job description
    print("\n5.3 Very long job description...")
    try:
        long_jd = " ".join(["Python Django REST API PostgreSQL Docker"] * 100)
        resume = create_test_resume("good")
        result = scorer.score(resume, "software_engineer", "mid", long_jd)
        print(f"   Score: {result['score']}/100")
    except Exception as e:
        print(f"   ERROR: {e}")

    # Edge case 4: Invalid role/level
    print("\n5.4 Invalid role/level combination...")
    try:
        resume = create_test_resume("good")
        result = scorer.score(resume, "invalid_role", "invalid_level", "")
        print(f"   Score: {result['score']}/100")
        if 'error' in result.get('breakdown', {}).get('keywords', {}).get('details', {}):
            print(f"   Error in keywords: {result['breakdown']['keywords']['details']['error']}")
    except Exception as e:
        print(f"   ERROR: {e}")


def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("ATS SCORER DEBUG AND TEST SUITE")
    print("="*80)
    print("\nThis script tests the ATS scorer components and identifies issues.")

    try:
        # Run all tests
        test_keyword_matcher()
        test_red_flags_validator()
        test_ats_scorer_components()
        test_full_ats_scoring()
        test_edge_cases()

        print("\n" + "="*80)
        print("ALL TESTS COMPLETED")
        print("="*80)
        print("\nSummary:")
        print("   ✓ Keyword matcher tested")
        print("   ✓ Red flags validator tested")
        print("   ✓ ATS scorer components tested")
        print("   ✓ Full scoring scenarios tested")
        print("   ✓ Edge cases tested")
        print("\nIf any issues were found, they are displayed above.")
        print("="*80 + "\n")

    except Exception as e:
        print(f"\n\nFATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
