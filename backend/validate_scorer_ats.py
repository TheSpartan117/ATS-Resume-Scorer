#!/usr/bin/env python
"""
Simple validation script to check if scorer_ats can be imported and basic functionality works.
"""

import sys
import traceback

def validate_imports():
    """Test that all imports work correctly"""
    try:
        from services.scorer_ats import ATSScorer
        from services.keyword_matcher import KeywordMatcher
        from services.red_flags_validator import RedFlagsValidator
        from services.parser import ResumeData
        print("✓ All imports successful")
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        traceback.print_exc()
        return False

def validate_initialization():
    """Test that ATSScorer can be initialized"""
    try:
        from services.scorer_ats import ATSScorer
        scorer = ATSScorer()
        assert scorer.keyword_matcher is not None
        assert scorer.validator is not None
        print("✓ ATSScorer initialization successful")
        return True
    except Exception as e:
        print(f"✗ Initialization failed: {e}")
        traceback.print_exc()
        return False

def validate_basic_functionality():
    """Test basic scoring functionality"""
    try:
        from services.scorer_ats import ATSScorer
        from services.parser import ResumeData

        scorer = ATSScorer()

        # Create minimal test resume
        resume = ResumeData(
            fileName="test.pdf",
            contact={
                "name": "John Doe",
                "email": "john@example.com"
            },
            experience=[{
                "title": "Engineer",
                "company": "Company",
                "startDate": "Jan 2020",
                "endDate": "Present",
                "description": "Python development"
            }],
            education=[{
                "degree": "BS Computer Science",
                "institution": "University"
            }],
            skills=["Python"],
            certifications=[],
            metadata={
                "pageCount": 1,
                "wordCount": 400,
                "fileFormat": "pdf"
            }
        )

        # Test individual scoring methods
        keywords_result = scorer._score_keywords(resume, "software_engineer", "mid", "")
        assert 'score' in keywords_result
        assert 'details' in keywords_result
        print("✓ Keyword scoring works")

        red_flags_result = scorer._score_red_flags(resume, "software_engineer", "mid")
        assert 'score' in red_flags_result
        assert 'details' in red_flags_result
        print("✓ Red flags scoring works")

        experience_result = scorer._score_experience(resume, "mid")
        assert 'score' in experience_result
        assert 'details' in experience_result
        print("✓ Experience scoring works")

        formatting_result = scorer._score_formatting(resume)
        assert 'score' in formatting_result
        assert 'details' in formatting_result
        print("✓ Formatting scoring works")

        contact_result = scorer._score_contact_info(resume)
        assert 'score' in contact_result
        assert 'details' in contact_result
        print("✓ Contact info scoring works")

        # Test full scoring
        result = scorer.score(resume, "software_engineer", "mid", "")
        assert 'score' in result
        assert 'breakdown' in result
        assert result['score'] >= 0
        assert result['score'] <= 100
        print(f"✓ Full scoring works (score: {result['score']}/100)")

        # Verify all breakdown categories
        assert 'keywords' in result['breakdown']
        assert 'red_flags' in result['breakdown']
        assert 'experience' in result['breakdown']
        assert 'formatting' in result['breakdown']
        assert 'contact' in result['breakdown']
        print("✓ All breakdown categories present")

        # Verify max scores
        assert result['breakdown']['keywords']['maxScore'] == 35
        assert result['breakdown']['red_flags']['maxScore'] == 20
        assert result['breakdown']['experience']['maxScore'] == 20
        assert result['breakdown']['formatting']['maxScore'] == 20
        assert result['breakdown']['contact']['maxScore'] == 5
        print("✓ All max scores correct")

        return True
    except Exception as e:
        print(f"✗ Functionality test failed: {e}")
        traceback.print_exc()
        return False

def main():
    print("Validating ATS Scorer Implementation\n")
    print("=" * 50)

    all_passed = True

    # Run validations
    if not validate_imports():
        all_passed = False

    if not validate_initialization():
        all_passed = False

    if not validate_basic_functionality():
        all_passed = False

    print("=" * 50)
    if all_passed:
        print("\n✓ All validations passed!")
        return 0
    else:
        print("\n✗ Some validations failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
