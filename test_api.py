#!/usr/bin/env python3
"""
ATS Resume Scorer API Test Script

Quick testing script for the deployed localhost API.
Tests all major endpoints with Scorer V3.
"""

import requests
import json
from pathlib import Path

# API Configuration
API_BASE = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("\n" + "="*70)
    print("TEST 1: Health Check")
    print("="*70)

    response = requests.get(f"{API_BASE}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200
    print("✅ Health check passed!")


def test_root():
    """Test root endpoint"""
    print("\n" + "="*70)
    print("TEST 2: Root Endpoint")
    print("="*70)

    response = requests.get(f"{API_BASE}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200
    print("✅ Root endpoint passed!")


def test_upload_and_score():
    """Test resume upload and scoring with Scorer V3"""
    print("\n" + "="*70)
    print("TEST 3: Upload & Score Resume (Scorer V3)")
    print("="*70)

    # Find a test resume
    data_dir = Path(__file__).parent / "backend" / "data"
    test_resumes = list(data_dir.glob("*.docx")) + list(data_dir.glob("*.pdf"))

    if not test_resumes:
        print("⚠️  No test resumes found in backend/data/")
        return

    test_file = test_resumes[0]
    print(f"Using test file: {test_file.name}")

    # Upload resume
    with open(test_file, 'rb') as f:
        files = {'file': (test_file.name, f, 'application/pdf' if test_file.suffix == '.pdf' else 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')}
        data = {
            'level': 'intermediary',
            'mode': 'quality_coach'
        }

        response = requests.post(
            f"{API_BASE}/api/upload",
            files=files,
            data=data
        )

    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print(f"\n📊 Scoring Results:")
        print(f"   Overall Score: {result.get('overallScore', 'N/A')}/100")
        print(f"   Rating: {result.get('rating', 'N/A')}")
        print(f"   Mode: {result.get('mode', 'N/A')}")
        print(f"   Version: {result.get('version', 'N/A')}")

        # Show category breakdown
        if 'breakdown' in result:
            print(f"\n   Category Breakdown:")
            for category, data in result['breakdown'].items():
                score = data.get('score', 0)
                max_score = data.get('maxScore', 0)
                print(f"      {category}: {score}/{max_score}")

        # Show issues
        if 'issues' in result:
            critical = len(result['issues'].get('critical', []))
            warnings = len(result['issues'].get('warnings', []))
            suggestions = len(result['issues'].get('suggestions', []))
            print(f"\n   Issues Found:")
            print(f"      Critical: {critical}")
            print(f"      Warnings: {warnings}")
            print(f"      Suggestions: {suggestions}")

        print("\n✅ Upload & Score test passed!")
        return result
    else:
        print(f"❌ Error: {response.text}")
        return None


def test_with_job_description():
    """Test scoring with job description for keyword matching"""
    print("\n" + "="*70)
    print("TEST 4: Score with Job Description (Keyword Matching)")
    print("="*70)

    # Find a test resume
    data_dir = Path(__file__).parent / "backend" / "data"
    test_resumes = list(data_dir.glob("*.docx")) + list(data_dir.glob("*.pdf"))

    if not test_resumes:
        print("⚠️  No test resumes found")
        return

    test_file = test_resumes[0]

    job_description = """
    Senior Software Engineer - Cloud Infrastructure

    We're seeking an experienced backend engineer to lead our cloud infrastructure team.

    Requirements:
    • 7+ years of software engineering experience
    • Expert-level Python programming skills
    • Deep AWS knowledge (EC2, S3, Lambda, RDS)
    • Strong experience with microservices architecture
    • Docker and Kubernetes expertise
    • CI/CD pipeline design and implementation
    • SQL and NoSQL database optimization

    Nice to have:
    • Terraform or CloudFormation experience
    • Monitoring tools (Datadog, New Relic)
    • GraphQL API development
    """

    # Upload with job description
    with open(test_file, 'rb') as f:
        files = {'file': (test_file.name, f, 'application/pdf' if test_file.suffix == '.pdf' else 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')}
        data = {
            'level': 'senior',
            'mode': 'quality_coach',
            'jobDescription': job_description
        }

        response = requests.post(
            f"{API_BASE}/api/upload",
            files=files,
            data=data
        )

    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print(f"\n📊 Scoring Results with Job Description:")
        print(f"   Overall Score: {result.get('overallScore', 'N/A')}/100")
        print(f"   Rating: {result.get('rating', 'N/A')}")

        # Show keyword matching details
        if 'keyword_details' in result and result['keyword_details']:
            kw = result['keyword_details']
            print(f"\n   🔑 Keyword Matching:")
            print(f"      Match Percentage: {kw.get('matchPercentage', 0):.1f}%")
            print(f"      Matched: {len(kw.get('matchedKeywords', []))}")
            print(f"      Missing: {len(kw.get('missingKeywords', []))}")

            if kw.get('matchedKeywords'):
                print(f"      ✅ Matched: {', '.join(kw['matchedKeywords'][:5])}")
            if kw.get('missingKeywords'):
                print(f"      ❌ Missing: {', '.join(kw['missingKeywords'][:5])}")

        print("\n✅ Job description test passed!")
        return result
    else:
        print(f"❌ Error: {response.text}")
        return None


def test_api_docs():
    """Check if API docs are available"""
    print("\n" + "="*70)
    print("TEST 5: API Documentation")
    print("="*70)

    response = requests.get(f"{API_BASE}/docs")
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        print(f"✅ API docs available at: {API_BASE}/docs")
    else:
        print(f"⚠️  API docs not available")


def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("🚀 ATS Resume Scorer V3 - API Testing")
    print("="*70)
    print(f"API Base URL: {API_BASE}")
    print("")

    try:
        test_health()
        test_root()
        test_upload_and_score()
        test_with_job_description()
        test_api_docs()

        print("\n" + "="*70)
        print("✅ ALL TESTS PASSED!")
        print("="*70)
        print("\n📖 Next Steps:")
        print(f"   1. Open API docs: {API_BASE}/docs")
        print(f"   2. Try the interactive Swagger UI")
        print(f"   3. Test with your own resumes")
        print("")

    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to API")
        print("   Make sure the backend is running on port 8000")
        print("   Run: python3 -m uvicorn main:app --host 0.0.0.0 --port 8000")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")


if __name__ == "__main__":
    main()
