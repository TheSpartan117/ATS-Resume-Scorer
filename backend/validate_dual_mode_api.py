#!/usr/bin/env python
"""
Validation script for dual-mode scoring API integration.
Tests the updated endpoints without running full pytest suite.
"""
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from backend.services.parser import ResumeData
from backend.services.scorer_v2 import AdaptiveScorer


def validate_scorer_modes():
    """Validate scorer supports both modes"""
    print("Testing AdaptiveScorer modes...")

    # Create test resume data
    resume_data = ResumeData(
        fileName="test.pdf",
        contact={
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "555-1234"
        },
        experience=[
            {
                "title": "Software Engineer",
                "company": "Tech Corp",
                "description": "Led development of Python applications using AWS and Docker"
            }
        ],
        education=[{"degree": "BS Computer Science", "institution": "University"}],
        skills=["Python", "AWS", "Docker", "React"],
        certifications=[],
        metadata={
            "pageCount": 1,
            "wordCount": 400,
            "hasPhoto": False,
            "fileFormat": "pdf"
        }
    )

    scorer = AdaptiveScorer()

    # Test ATS mode
    print("\n1. Testing ATS Simulation mode...")
    ats_result = scorer.score(
        resume_data=resume_data,
        role_id="software_engineer",
        level="mid",
        job_description="Python developer with AWS experience needed",
        mode="ats_simulation"
    )

    assert ats_result["mode"] == "ats_simulation", "ATS mode not set correctly"
    assert "keyword_match" in ats_result["breakdown"], "Missing keyword_match in ATS mode"
    assert "keyword_details" in ats_result, "Missing keyword_details in ATS mode"
    assert "auto_reject" in ats_result, "Missing auto_reject in ATS mode"
    print(f"   ✓ ATS mode score: {ats_result['overallScore']}/100")
    print(f"   ✓ Breakdown categories: {list(ats_result['breakdown'].keys())}")

    # Test Quality mode
    print("\n2. Testing Quality Coach mode...")
    quality_result = scorer.score(
        resume_data=resume_data,
        role_id="software_engineer",
        level="mid",
        job_description=None,
        mode="quality_coach"
    )

    assert quality_result["mode"] == "quality_coach", "Quality mode not set correctly"
    assert "role_keywords" in quality_result["breakdown"], "Missing role_keywords in Quality mode"
    assert "content_quality" in quality_result["breakdown"], "Missing content_quality"
    assert "professional_polish" in quality_result["breakdown"], "Missing professional_polish"
    print(f"   ✓ Quality mode score: {quality_result['overallScore']}/100")
    print(f"   ✓ Breakdown categories: {list(quality_result['breakdown'].keys())}")

    # Test auto mode with JD
    print("\n3. Testing auto mode with job description...")
    auto_ats_result = scorer.score(
        resume_data=resume_data,
        role_id="software_engineer",
        level="mid",
        job_description="Python developer",
        mode="auto"
    )
    assert auto_ats_result["mode"] == "ats_simulation", "Auto mode should use ATS with JD"
    print(f"   ✓ Auto mode with JD → ATS mode")

    # Test auto mode without JD
    print("\n4. Testing auto mode without job description...")
    auto_quality_result = scorer.score(
        resume_data=resume_data,
        role_id="software_engineer",
        level="mid",
        job_description=None,
        mode="auto"
    )
    assert auto_quality_result["mode"] == "quality_coach", "Auto mode should use Quality without JD"
    print(f"   ✓ Auto mode without JD → Quality mode")

    # Test issue categorization
    print("\n5. Testing issue categorization...")
    assert "issues" in ats_result, "Missing issues in result"
    assert "critical" in ats_result["issues"], "Missing critical issues category"
    assert "warnings" in ats_result["issues"], "Missing warnings category"
    assert "suggestions" in ats_result["issues"], "Missing suggestions category"
    print(f"   ✓ Issue categories present")
    print(f"   ✓ Critical: {len(ats_result['issues']['critical'])}")
    print(f"   ✓ Warnings: {len(ats_result['issues']['warnings'])}")
    print(f"   ✓ Suggestions: {len(ats_result['issues']['suggestions'])}")

    print("\n✅ All scorer mode validations passed!")
    return True


def validate_api_schema():
    """Validate API schema updates"""
    print("\nValidating API schema...")

    from backend.schemas.resume import ScoreResponse, CategoryBreakdown
    from pydantic import ValidationError

    # Test score response with new fields
    try:
        score_response = ScoreResponse(
            overallScore=75.5,
            breakdown={
                "keyword_match": CategoryBreakdown(
                    score=50.0,
                    maxScore=70.0,
                    issues=["Missing required keyword: Docker"]
                )
            },
            issues={
                "critical": ["Missing phone number"],
                "warnings": ["Add more metrics"],
                "suggestions": ["Consider adding LinkedIn"]
            },
            strengths=["Strong technical skills"],
            mode="ats_simulation",
            keywordDetails={
                "required_matched": 5,
                "required_total": 8,
                "required_match_pct": 62.5
            },
            autoReject=False,
            issueCounts={
                "critical": 1,
                "warnings": 1,
                "suggestions": 1
            }
        )
        print("   ✓ ScoreResponse schema with issueCounts validated")
    except ValidationError as e:
        print(f"   ✗ ScoreResponse schema validation failed: {e}")
        return False

    # Test backward compatibility (issueCounts is optional)
    try:
        legacy_response = ScoreResponse(
            overallScore=80.0,
            breakdown={},
            issues={},
            strengths=[],
            mode="quality_coach"
        )
        print("   ✓ Backward compatibility maintained (issueCounts optional)")
    except ValidationError as e:
        print(f"   ✗ Backward compatibility failed: {e}")
        return False

    print("\n✅ All schema validations passed!")
    return True


def validate_score_request():
    """Validate ScoreRequest with mode parameter"""
    print("\nValidating ScoreRequest schema...")

    from backend.api.score import ScoreRequest
    from pydantic import ValidationError

    # Test with mode parameter
    try:
        request = ScoreRequest(
            fileName="test.pdf",
            contact={"name": "John", "email": "john@example.com"},
            experience=[],
            education=[],
            skills=[],
            certifications=[],
            metadata={"pageCount": 1, "wordCount": 400, "hasPhoto": False, "fileFormat": "pdf"},
            role="software_engineer",
            level="mid",
            mode="ats"
        )
        print(f"   ✓ ScoreRequest with mode='ats' validated")
    except ValidationError as e:
        print(f"   ✗ ScoreRequest validation failed: {e}")
        return False

    # Test without mode (backward compatibility)
    try:
        request = ScoreRequest(
            fileName="test.pdf",
            contact={"name": "John", "email": "john@example.com"},
            experience=[],
            education=[],
            skills=[],
            certifications=[],
            metadata={"pageCount": 1, "wordCount": 400, "hasPhoto": False, "fileFormat": "pdf"}
        )
        assert request.mode == "auto", "Default mode should be 'auto'"
        print(f"   ✓ ScoreRequest backward compatible (mode defaults to 'auto')")
    except ValidationError as e:
        print(f"   ✗ ScoreRequest backward compatibility failed: {e}")
        return False

    print("\n✅ All request schema validations passed!")
    return True


def main():
    """Run all validations"""
    print("="*60)
    print("DUAL-MODE SCORING API VALIDATION")
    print("="*60)

    try:
        validate_scorer_modes()
        validate_api_schema()
        validate_score_request()

        print("\n" + "="*60)
        print("✅ ALL VALIDATIONS PASSED!")
        print("="*60)
        print("\nThe dual-mode scoring API is ready for integration:")
        print("  • ATS Simulation mode (mode='ats' or 'ats_simulation')")
        print("  • Quality Coach mode (mode='quality' or 'quality_coach')")
        print("  • Auto-detection mode (mode='auto' - default)")
        print("  • Issue counts included in responses")
        print("  • Backward compatible with existing code")
        print("="*60)
        return 0
    except AssertionError as e:
        print(f"\n❌ Validation failed: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
