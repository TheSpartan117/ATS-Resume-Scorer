#!/usr/bin/env python3
"""
Test ATS scorer through API endpoint to verify end-to-end functionality.
This tests the actual API flow that users will experience.
"""

import sys
import json
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from fastapi.testclient import TestClient
from main import app

# Create test client
client = TestClient(app)


def test_api_score_ats_mode_with_jd():
    """Test /api/score endpoint with ATS mode and job description"""
    print("\n" + "="*80)
    print("TEST 1: API Score - ATS Mode with Job Description")
    print("="*80)

    request_data = {
        "fileName": "test_resume.pdf",
        "contact": {
            "name": "John Doe",
            "email": "john.doe@example.com",
            "phone": "555-1234",
            "location": "San Francisco, CA",
            "linkedin": "linkedin.com/in/johndoe"
        },
        "experience": [
            {
                "title": "Software Engineer",
                "company": "Tech Company",
                "startDate": "Jan 2020",
                "endDate": "Present",
                "description": "Developed Python applications using Django, REST APIs, PostgreSQL, Docker, and Kubernetes"
            }
        ],
        "education": [
            {
                "degree": "BS Computer Science",
                "institution": "Stanford University"
            }
        ],
        "skills": ["Python", "Django", "REST API", "PostgreSQL", "Docker", "Kubernetes"],
        "certifications": [],
        "metadata": {
            "pageCount": 1,
            "wordCount": 500,
            "fileFormat": "pdf",
            "hasPhoto": False
        },
        "jobDescription": "We are looking for a Python developer with Django experience. Must have REST API skills and PostgreSQL knowledge. Docker and Kubernetes required.",
        "role": "software_engineer",
        "level": "mid",
        "mode": "ats"
    }

    print("\nSending request to /api/score...")
    response = client.post("/api/score", json=request_data)

    print(f"Status code: {response.status_code}")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    data = response.json()
    print(f"\nResponse:")
    print(f"  Overall Score: {data['overallScore']}/100")
    print(f"  Mode: {data['mode']}")
    print(f"\nBreakdown:")
    for category, details in data['breakdown'].items():
        print(f"    {category}: {details['score']}/{details['maxScore']}")

    # Verify mode
    assert data['mode'] == 'ats_simulation', f"Expected mode='ats_simulation', got {data['mode']}"

    # Verify score is reasonable
    assert 0 <= data['overallScore'] <= 100, f"Score out of range: {data['overallScore']}"

    # Verify breakdown exists
    assert 'keywords' in data['breakdown']
    assert 'red_flags' in data['breakdown']
    assert 'experience' in data['breakdown']
    assert 'formatting' in data['breakdown']
    assert 'contact' in data['breakdown']

    print("\n✓ API score with ATS mode and JD works correctly")
    return True


def test_api_score_ats_mode_no_jd():
    """Test /api/score endpoint with ATS mode without job description"""
    print("\n" + "="*80)
    print("TEST 2: API Score - ATS Mode without Job Description")
    print("="*80)

    request_data = {
        "fileName": "test_resume.pdf",
        "contact": {
            "name": "Jane Smith",
            "email": "jane@example.com"
        },
        "experience": [
            {
                "title": "Developer",
                "company": "Company",
                "startDate": "Jan 2020",
                "endDate": "Present",
                "description": "Software development"
            }
        ],
        "education": [],
        "skills": ["Python", "JavaScript"],
        "certifications": [],
        "metadata": {
            "pageCount": 1,
            "wordCount": 400,
            "fileFormat": "pdf"
        },
        "jobDescription": "",  # No job description
        "role": "software_engineer",
        "level": "entry",
        "mode": "ats"
    }

    print("\nSending request to /api/score (no JD)...")
    response = client.post("/api/score", json=request_data)

    print(f"Status code: {response.status_code}")
    assert response.status_code == 200

    data = response.json()
    print(f"\nResponse:")
    print(f"  Overall Score: {data['overallScore']}/100")
    print(f"  Mode: {data['mode']}")

    # Should still work with role-based keywords
    assert data['mode'] == 'ats_simulation'
    assert 0 <= data['overallScore'] <= 100

    print("\n✓ API score with ATS mode (no JD) works correctly")
    return True


def test_api_score_auto_mode():
    """Test /api/score endpoint with auto mode"""
    print("\n" + "="*80)
    print("TEST 3: API Score - Auto Mode")
    print("="*80)

    # Auto mode with JD should use ATS
    request_data = {
        "fileName": "test_resume.pdf",
        "contact": {"name": "Test User"},
        "experience": [],
        "education": [],
        "skills": [],
        "certifications": [],
        "metadata": {"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"},
        "jobDescription": "Python developer needed",  # Has JD
        "role": "software_engineer",
        "level": "mid",
        "mode": "auto"  # Auto mode
    }

    print("\nSending request with auto mode and JD...")
    response = client.post("/api/score", json=request_data)

    assert response.status_code == 200
    data = response.json()

    print(f"Mode detected: {data['mode']}")
    assert data['mode'] == 'ats_simulation', "Auto mode with JD should use ATS simulation"

    print("\n✓ Auto mode detection works correctly")
    return True


def test_api_score_invalid_role():
    """Test /api/score endpoint with invalid role"""
    print("\n" + "="*80)
    print("TEST 4: API Score - Invalid Role (Error Handling)")
    print("="*80)

    request_data = {
        "fileName": "test_resume.pdf",
        "contact": {"name": "Test User"},
        "experience": [],
        "education": [],
        "skills": [],
        "certifications": [],
        "metadata": {"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"},
        "jobDescription": "",
        "role": "invalid_role_xyz",  # Invalid role
        "level": "invalid_level",  # Invalid level
        "mode": "ats"
    }

    print("\nSending request with invalid role/level...")
    response = client.post("/api/score", json=request_data)

    # Should still return 200 with error in details
    assert response.status_code == 200

    data = response.json()
    print(f"Overall Score: {data['overallScore']}/100")

    # Check if error is in keyword details
    if 'error' in data['breakdown']['keywords']:
        print(f"Error properly captured: {data['breakdown']['keywords']['error']}")

    print("\n✓ Invalid role/level handled gracefully")
    return True


def test_api_score_minimal_resume():
    """Test /api/score endpoint with minimal resume data"""
    print("\n" + "="*80)
    print("TEST 5: API Score - Minimal Resume")
    print("="*80)

    request_data = {
        "fileName": "minimal.pdf",
        "contact": {},  # Empty contact
        "experience": [],  # No experience
        "education": [],  # No education
        "skills": [],  # No skills
        "certifications": [],
        "metadata": {"pageCount": 1, "wordCount": 100, "fileFormat": "pdf"},
        "jobDescription": "",
        "role": "software_engineer",
        "level": "entry",
        "mode": "ats"
    }

    print("\nSending request with minimal resume...")
    response = client.post("/api/score", json=request_data)

    assert response.status_code == 200
    data = response.json()

    print(f"Overall Score: {data['overallScore']}/100")
    print(f"\nBreakdown:")
    for category, details in data['breakdown'].items():
        print(f"    {category}: {details['score']}/{details['maxScore']}")

    # Minimal resume should get low score
    assert data['overallScore'] < 50, "Minimal resume should score low"

    print("\n✓ Minimal resume scored appropriately")
    return True


def test_api_score_excellent_resume():
    """Test /api/score endpoint with excellent resume"""
    print("\n" + "="*80)
    print("TEST 6: API Score - Excellent Resume")
    print("="*80)

    request_data = {
        "fileName": "excellent.pdf",
        "contact": {
            "name": "Dr. Jane Smith",
            "email": "jane.smith@example.com",
            "phone": "555-1234",
            "location": "San Francisco, CA",
            "linkedin": "linkedin.com/in/janesmith"
        },
        "experience": [
            {
                "title": "Senior Software Engineer",
                "company": "Google",
                "startDate": "Jan 2020",
                "endDate": "Present",
                "description": "Led development of scalable microservices using Python, Django, FastAPI, PostgreSQL, Redis, Docker, Kubernetes, and AWS. Mentored team of 5 engineers."
            }
        ],
        "education": [
            {
                "degree": "MS Computer Science",
                "institution": "Stanford University"
            }
        ],
        "skills": [
            "Python", "Django", "FastAPI", "PostgreSQL", "Redis",
            "Docker", "Kubernetes", "AWS", "Terraform", "CI/CD"
        ],
        "certifications": [
            {"name": "AWS Certified Solutions Architect"}
        ],
        "metadata": {
            "pageCount": 2,
            "wordCount": 650,
            "fileFormat": "pdf",
            "hasPhoto": False
        },
        "jobDescription": "Senior Python developer with Django and FastAPI experience. Must know PostgreSQL, Redis, Docker, Kubernetes, and AWS.",
        "role": "software_engineer",
        "level": "senior",
        "mode": "ats"
    }

    print("\nSending request with excellent resume...")
    response = client.post("/api/score", json=request_data)

    assert response.status_code == 200
    data = response.json()

    print(f"Overall Score: {data['overallScore']}/100")
    print(f"\nBreakdown:")
    for category, details in data['breakdown'].items():
        print(f"    {category}: {details['score']}/{details['maxScore']}")

    # Excellent resume should score reasonably well
    # Note: ATS is harsh, so even excellent resumes may not get 80+
    assert data['overallScore'] >= 40, f"Excellent resume should score at least 40, got {data['overallScore']}"

    print("\n✓ Excellent resume scored appropriately")
    return True


def main():
    """Run all API integration tests"""
    print("\n" + "="*80)
    print("ATS SCORER API INTEGRATION TESTS")
    print("="*80)
    print("\nTesting ATS scorer through API endpoint...")

    try:
        results = []
        results.append(("ATS Mode with JD", test_api_score_ats_mode_with_jd()))
        results.append(("ATS Mode without JD", test_api_score_ats_mode_no_jd()))
        results.append(("Auto Mode", test_api_score_auto_mode()))
        results.append(("Invalid Role", test_api_score_invalid_role()))
        results.append(("Minimal Resume", test_api_score_minimal_resume()))
        results.append(("Excellent Resume", test_api_score_excellent_resume()))

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
            print("ALL API INTEGRATION TESTS PASSED!")
            print("="*80)
            print("\nVerified:")
            print("   ✓ ATS mode with job description")
            print("   ✓ ATS mode without job description")
            print("   ✓ Auto mode detection")
            print("   ✓ Error handling for invalid inputs")
            print("   ✓ Scoring for various resume quality levels")
            print("   ✓ API endpoint returns proper response format")
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
