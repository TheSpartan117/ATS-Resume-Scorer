#!/usr/bin/env python3
"""
Manual test script for ResumeScorer to verify basic functionality.
"""

import sys
sys.path.insert(0, '/Users/sabuj.mondal/ats-resume-scorer/backend')

from services.scorer_v2 import ResumeScorer
from services.parser import ResumeData
from services.role_taxonomy import ExperienceLevel


def test_basic_functionality():
    """Test basic scorer functionality"""
    print("Testing ResumeScorer...")

    # Create a sample resume
    sample_resume = ResumeData(
        fileName="test.pdf",
        contact={"name": "John Doe", "email": "john@example.com", "phone": "+1-555-0100"},
        experience=[{
            "title": "Senior Software Engineer",
            "company": "Tech Corp",
            "description": """
            - Led team of 5 engineers building microservices with Python and AWS
            - Reduced deployment time by 60% through CI/CD automation
            - Implemented Kubernetes orchestration
            """
        }],
        education=[{"degree": "BS Computer Science", "institution": "Stanford"}],
        skills=["Python", "AWS", "Docker", "Kubernetes", "React"],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 450, "hasPhoto": False, "fileFormat": "pdf"}
    )

    # Create scorer
    scorer = ResumeScorer()
    print("✓ ResumeScorer initialized")

    # Test ATS mode
    job_description = """
    Required: Python, AWS, Docker, Kubernetes
    Preferred: React, TypeScript
    """

    print("\nTesting ATS mode...")
    try:
        ats_result = scorer.score(
            resume=sample_resume,
            role="software_engineer",
            level=ExperienceLevel.SENIOR,
            mode='ats',
            job_description=job_description
        )

        print(f"✓ ATS mode completed")
        print(f"  Score: {ats_result['score']}")
        print(f"  Interpretation: {ats_result['interpretation']}")
        print(f"  Mode: {ats_result['mode']}")
        print(f"  Recommendations: {len(ats_result['recommendations'])} items")

        # Verify structure
        assert 'score' in ats_result
        assert 'mode' in ats_result
        assert 'interpretation' in ats_result
        assert 'breakdown' in ats_result
        assert 'recommendations' in ats_result
        print("✓ ATS result structure valid")

    except Exception as e:
        print(f"✗ ATS mode failed: {e}")
        return False

    # Test Quality mode
    print("\nTesting Quality mode...")
    try:
        quality_result = scorer.score(
            resume=sample_resume,
            role="software_engineer",
            level=ExperienceLevel.SENIOR,
            mode='quality'
        )

        print(f"✓ Quality mode completed")
        print(f"  Score: {quality_result['score']}")
        print(f"  Interpretation: {quality_result['interpretation']}")
        print(f"  Mode: {quality_result['mode']}")
        print(f"  Recommendations: {len(quality_result['recommendations'])} items")

        # Verify structure
        assert 'score' in quality_result
        assert 'mode' in quality_result
        assert 'interpretation' in quality_result
        assert 'breakdown' in quality_result
        assert 'recommendations' in quality_result
        print("✓ Quality result structure valid")

    except Exception as e:
        print(f"✗ Quality mode failed: {e}")
        return False

    # Test interpretation
    print("\nTesting interpretation layer...")
    test_cases = [
        (95, "Excellent"),
        (80, "Very good"),
        (70, "Good"),
        (50, "Needs improvement"),
        (30, "Needs significant improvement")
    ]

    for score, expected in test_cases:
        result = scorer._interpret_score(score)
        if result == expected:
            print(f"✓ Score {score} -> {result}")
        else:
            print(f"✗ Score {score} -> {result} (expected {expected})")
            return False

    # Test caching
    print("\nTesting cache functionality...")
    test_hash = "test123"
    test_data = {"test": "data"}
    scorer.cache_validation_results(test_hash, test_data)
    cached = scorer.get_cached_validation(test_hash)
    if cached == test_data:
        print("✓ Cache store/retrieve works")
    else:
        print("✗ Cache failed")
        return False

    scorer.clear_cache()
    cached = scorer.get_cached_validation(test_hash)
    if cached is None:
        print("✓ Cache clear works")
    else:
        print("✗ Cache clear failed")
        return False

    # Test error handling
    print("\nTesting error handling...")
    try:
        scorer.score(
            resume=sample_resume,
            role="software_engineer",
            level=ExperienceLevel.SENIOR,
            mode='ats'  # Missing job_description
        )
        print("✗ Should have raised error for missing job_description")
        return False
    except ValueError as e:
        if "job_description is required" in str(e):
            print("✓ Correctly raises error for missing job_description")
        else:
            print(f"✗ Wrong error: {e}")
            return False

    try:
        scorer.score(
            resume=sample_resume,
            role="software_engineer",
            level=ExperienceLevel.SENIOR,
            mode='invalid_mode'
        )
        print("✗ Should have raised error for invalid mode")
        return False
    except ValueError as e:
        if "Invalid mode" in str(e):
            print("✓ Correctly raises error for invalid mode")
        else:
            print(f"✗ Wrong error: {e}")
            return False

    print("\n" + "="*50)
    print("All tests passed! ✓")
    print("="*50)
    return True


if __name__ == "__main__":
    try:
        success = test_basic_functionality()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
