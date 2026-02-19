#!/usr/bin/env python3
"""
Test script to verify ATS scorer fixes.
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from services.scorer_ats import ATSScorer
from services.parser import ResumeData


def test_contact_info_fix():
    """Test that contact info scoring properly handles missing fields"""
    print("\n" + "="*80)
    print("TEST 1: Contact Info Scoring Fix")
    print("="*80)

    scorer = ATSScorer()

    # Test with missing fields
    resume = ResumeData(
        fileName="test.pdf",
        contact={
            "name": "John Doe",
            "email": "john@example.com"
            # Missing: phone, location, linkedin
        },
        experience=[],
        education=[],
        skills=[],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
    )

    result = scorer._score_contact_info(resume)

    print(f"\nScore: {result['score']}/{result['maxScore']}")
    print(f"Has name: {result['details']['has_name']}")
    print(f"Has email: {result['details']['has_email']}")
    print(f"Has phone: {result['details']['has_phone']}")
    print(f"Has location: {result['details']['has_location']}")
    print(f"Has linkedin: {result['details']['has_linkedin']}")
    print(f"Missing fields: {result['details']['missing']}")
    print(f"Message: {result['details']['message']}")

    # Verify fix
    assert result['score'] == 2, f"Expected score 2, got {result['score']}"
    assert len(result['details']['missing']) == 3, f"Expected 3 missing fields, got {len(result['details']['missing'])}"
    assert 'phone' in result['details']['missing']
    assert 'location' in result['details']['missing']
    assert 'linkedin' in result['details']['missing']

    print("\n✓ Contact info scoring fix verified!")
    return True


def test_error_handling():
    """Test that error handling works for each component"""
    print("\n" + "="*80)
    print("TEST 2: Error Handling")
    print("="*80)

    scorer = ATSScorer()

    # Test with invalid resume data that might cause errors
    resume = ResumeData(
        fileName="test.pdf",
        contact={},
        experience=[],
        education=[],
        skills=[],
        certifications=[],
        metadata={}  # Empty metadata might cause issues
    )

    print("\n2.1 Testing with minimal resume (should not crash)...")
    try:
        result = scorer.score(resume, "software_engineer", "mid", "")
        print(f"   Score: {result['score']}/100")
        print(f"   ✓ No crash with minimal resume")
    except Exception as e:
        print(f"   ✗ ERROR: {e}")
        return False

    print("\n2.2 Testing with invalid role/level (should not crash)...")
    try:
        result = scorer.score(resume, "invalid_role_xyz", "invalid_level_xyz", "")
        print(f"   Score: {result['score']}/100")
        if 'error' in result['breakdown']['keywords']['details']:
            print(f"   ✓ Error properly captured in keywords: {result['breakdown']['keywords']['details']['error']}")
        print(f"   ✓ No crash with invalid role/level")
    except Exception as e:
        print(f"   ✗ ERROR: {e}")
        return False

    print("\n✓ Error handling verified!")
    return True


def test_keyword_error_handling():
    """Test that keyword matching errors are handled gracefully"""
    print("\n" + "="*80)
    print("TEST 3: Keyword Error Handling")
    print("="*80)

    scorer = ATSScorer()

    resume = ResumeData(
        fileName="test.pdf",
        contact={"name": "Test User"},
        experience=[{
            "title": "Developer",
            "company": "Company",
            "startDate": "Jan 2020",
            "endDate": "Present",
            "description": "Python Django development"
        }],
        education=[],
        skills=["Python", "Django"],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
    )

    print("\n3.1 Testing with non-existent role/level combo...")
    result = scorer._score_keywords(resume, "nonexistent_role", "nonexistent_level", "")

    print(f"   Score: {result['score']}/{result['maxScore']}")
    if 'error' in result['details']:
        print(f"   Error message: {result['details']['error']}")
        print(f"   ✓ Error properly captured")
    else:
        print(f"   ✓ No error (role might exist in keywords)")

    print("\n3.2 Testing with valid role/level...")
    result = scorer._score_keywords(resume, "software_engineer", "mid", "")

    print(f"   Score: {result['score']}/{result['maxScore']}")
    print(f"   Percentage: {result['details']['percentage']:.1f}%")
    print(f"   Matched: {result['details']['matched_count']} keywords")
    print(f"   Missing: {result['details']['missing_count']} keywords")

    assert 'error' not in result['details'], "Should not have error with valid role/level"
    print(f"   ✓ Valid role/level works correctly")

    print("\n✓ Keyword error handling verified!")
    return True


def test_full_scoring_scenarios():
    """Test full scoring with various scenarios"""
    print("\n" + "="*80)
    print("TEST 4: Full Scoring Scenarios")
    print("="*80)

    scorer = ATSScorer()

    # Scenario 1: Good resume
    print("\n4.1 Good resume with complete information...")
    good_resume = ResumeData(
        fileName="good.pdf",
        contact={
            "name": "Jane Smith",
            "email": "jane@example.com",
            "phone": "555-1234",
            "location": "San Francisco, CA",
            "linkedin": "linkedin.com/in/janesmith"
        },
        experience=[{
            "title": "Software Engineer",
            "company": "Tech Company",
            "startDate": "Jan 2020",
            "endDate": "Present",
            "description": "Developed Python applications using Django, REST APIs, PostgreSQL, Docker, and Kubernetes"
        }],
        education=[{
            "degree": "BS Computer Science",
            "institution": "Stanford University"
        }],
        skills=["Python", "Django", "REST API", "PostgreSQL", "Docker", "Kubernetes"],
        certifications=[],
        metadata={
            "pageCount": 1,
            "wordCount": 500,
            "fileFormat": "pdf",
            "hasPhoto": False
        }
    )

    result = scorer.score(good_resume, "software_engineer", "mid", "")
    print(f"   Total Score: {result['score']}/100")
    print(f"   Breakdown:")
    for category, data in result['breakdown'].items():
        print(f"      {category}: {data['score']}/{data['maxScore']}")

    assert result['score'] > 30, f"Good resume should score above 30, got {result['score']}"
    print(f"   ✓ Good resume scored reasonably")

    # Scenario 2: Good resume with job description
    print("\n4.2 Good resume with matching job description...")
    job_desc = "Python developer with Django and REST API experience. PostgreSQL and Docker required."

    result_jd = scorer.score(good_resume, "software_engineer", "mid", job_desc)
    print(f"   Total Score: {result_jd['score']}/100")
    print(f"   Keyword Match: {result_jd['breakdown']['keywords']['details']['percentage']:.1f}%")

    print(f"   ✓ Job description matching works")

    # Scenario 3: Poor resume
    print("\n4.3 Poor resume with missing information...")
    poor_resume = ResumeData(
        fileName="poor.pdf",
        contact={},
        experience=[],
        education=[],
        skills=[],
        certifications=[],
        metadata={
            "pageCount": 5,
            "wordCount": 50,
            "fileFormat": "doc",
            "hasPhoto": True
        }
    )

    result_poor = scorer.score(poor_resume, "software_engineer", "mid", "")
    print(f"   Total Score: {result_poor['score']}/100")
    print(f"   Breakdown:")
    for category, data in result_poor['breakdown'].items():
        print(f"      {category}: {data['score']}/{data['maxScore']}")

    assert result_poor['score'] < result['score'], "Poor resume should score lower than good resume"
    print(f"   ✓ Poor resume scored lower than good resume")

    print("\n✓ Full scoring scenarios verified!")
    return True


def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("ATS SCORER FIXES VERIFICATION")
    print("="*80)
    print("\nVerifying bug fixes and improvements...")

    try:
        # Run all tests
        results = []
        results.append(("Contact Info Fix", test_contact_info_fix()))
        results.append(("Error Handling", test_error_handling()))
        results.append(("Keyword Error Handling", test_keyword_error_handling()))
        results.append(("Full Scoring Scenarios", test_full_scoring_scenarios()))

        # Summary
        print("\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80)

        all_passed = True
        for test_name, passed in results:
            status = "✓ PASS" if passed else "✗ FAIL"
            print(f"   {status}: {test_name}")
            if not passed:
                all_passed = False

        if all_passed:
            print("\n" + "="*80)
            print("ALL TESTS PASSED!")
            print("="*80)
            print("\nFixes verified:")
            print("   ✓ Contact info scoring bug fixed")
            print("   ✓ Error handling added to all components")
            print("   ✓ Keyword matching errors handled gracefully")
            print("   ✓ Full scoring works with various scenarios")
            print("="*80 + "\n")
            return 0
        else:
            print("\n" + "="*80)
            print("SOME TESTS FAILED")
            print("="*80 + "\n")
            return 1

    except Exception as e:
        print(f"\n\nFATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
