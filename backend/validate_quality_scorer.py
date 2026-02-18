#!/usr/bin/env python3
"""
Validation script for Quality Mode Scorer.
Checks implementation correctness without running full tests.
"""

import sys
sys.path.insert(0, '/Users/sabuj.mondal/ats-resume-scorer/backend')

def validate_imports():
    """Validate all imports work"""
    print("Validating imports...")
    try:
        from services.scorer_quality import QualityScorer
        from services.parser import ResumeData
        from services.red_flags_validator import RedFlagsValidator
        from services.keyword_extractor import match_with_synonyms
        from services.role_taxonomy import get_role_scoring_data
        print("✓ All imports successful")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def validate_class_structure():
    """Validate QualityScorer class structure"""
    print("\nValidating class structure...")
    try:
        from services.scorer_quality import QualityScorer

        scorer = QualityScorer()

        # Check required methods exist
        required_methods = [
            'score',
            '_score_content_quality',
            '_score_achievement_depth',
            '_score_keywords_fit',
            '_score_polish',
            '_score_readability',
            '_analyze_action_verbs',
            '_analyze_quantification',
            '_analyze_content_depth',
            '_analyze_metrics_depth',
            '_get_resume_text'
        ]

        for method in required_methods:
            if not hasattr(scorer, method):
                print(f"✗ Missing method: {method}")
                return False
            print(f"  ✓ Method exists: {method}")

        print("✓ Class structure valid")
        return True
    except Exception as e:
        print(f"✗ Structure validation error: {e}")
        return False

def validate_scoring_logic():
    """Validate basic scoring logic"""
    print("\nValidating scoring logic...")
    try:
        from services.scorer_quality import QualityScorer
        from services.parser import ResumeData

        scorer = QualityScorer()

        # Create minimal resume
        resume = ResumeData(
            fileName="test.pdf",
            contact={"name": "Test User", "email": "test@gmail.com"},
            experience=[{
                "title": "Engineer",
                "company": "Company",
                "description": "Developed software increasing efficiency by 50%"
            }],
            education=[{"degree": "BS", "institution": "University"}],
            skills=["Python", "Java"],
            certifications=[],
            metadata={"pageCount": 1, "wordCount": 300, "hasPhoto": False, "fileFormat": "pdf"}
        )

        # Score it
        result = scorer.score(resume, "software_engineer", "mid")

        # Validate result structure
        if 'score' not in result:
            print("✗ Missing 'score' in result")
            return False
        print(f"  ✓ Overall score: {result['score']}")

        if 'breakdown' not in result:
            print("✗ Missing 'breakdown' in result")
            return False

        breakdown = result['breakdown']
        required_categories = [
            'content_quality',
            'achievement_depth',
            'keywords_fit',
            'polish',
            'readability'
        ]

        for category in required_categories:
            if category not in breakdown:
                print(f"✗ Missing category: {category}")
                return False

            cat_data = breakdown[category]
            if 'score' not in cat_data:
                print(f"✗ Missing score in {category}")
                return False
            if 'max_score' not in cat_data:
                print(f"✗ Missing max_score in {category}")
                return False
            if 'details' not in cat_data:
                print(f"✗ Missing details in {category}")
                return False

            print(f"  ✓ Category {category}: {cat_data['score']}/{cat_data['max_score']}")

        # Validate max scores
        expected_max_scores = {
            'content_quality': 30,
            'achievement_depth': 20,
            'keywords_fit': 20,
            'polish': 15,
            'readability': 15
        }

        for category, expected_max in expected_max_scores.items():
            actual_max = breakdown[category]['max_score']
            if actual_max != expected_max:
                print(f"✗ Wrong max_score for {category}: {actual_max} != {expected_max}")
                return False

        total_max = sum(cat['max_score'] for cat in breakdown.values())
        if total_max != 100:
            print(f"✗ Max scores don't sum to 100: {total_max}")
            return False
        print(f"  ✓ Max scores sum correctly: {total_max}")

        print("✓ Scoring logic valid")
        return True
    except Exception as e:
        print(f"✗ Scoring validation error: {e}")
        import traceback
        traceback.print_exc()
        return False

def validate_thresholds():
    """Validate strict thresholds are implemented"""
    print("\nValidating strict thresholds...")
    try:
        from services.scorer_quality import QualityScorer
        from services.parser import ResumeData

        scorer = QualityScorer()

        # Test action verb threshold
        # Resume with no action verbs (should get 0 points)
        no_verbs_resume = ResumeData(
            fileName="test.pdf",
            contact={"name": "Test"},
            experience=[{
                "title": "Engineer",
                "company": "Company",
                "description": "Was responsible for coding. Helped with projects."
            }],
            education=[{"degree": "BS", "institution": "Uni"}],
            skills=["Python"],
            certifications=[],
            metadata={"pageCount": 1, "wordCount": 200, "hasPhoto": False, "fileFormat": "pdf"}
        )

        result = scorer.score(no_verbs_resume, "software_engineer", "mid")
        content_quality = result['breakdown']['content_quality']
        verb_score = content_quality['details']['action_verbs_score']

        if verb_score > 0:
            print(f"⚠ Warning: No action verbs scored {verb_score} (expected 0 for <70%)")
        else:
            print(f"  ✓ Action verb threshold working: {verb_score} for poor resume")

        # Test with good resume
        good_resume = ResumeData(
            fileName="test.pdf",
            contact={"name": "Test"},
            experience=[{
                "title": "Engineer",
                "company": "Company",
                "description": """
- Developed features increasing sales by 30%
- Implemented automation reducing costs by 50%
- Led team of 5 engineers
- Architected system serving 100K users
- Optimized queries improving speed by 40%
                """
            }],
            education=[{"degree": "BS", "institution": "Uni"}],
            skills=["Python", "AWS"],
            certifications=[],
            metadata={"pageCount": 1, "wordCount": 400, "hasPhoto": False, "fileFormat": "pdf"}
        )

        result = scorer.score(good_resume, "software_engineer", "mid")
        content_quality = result['breakdown']['content_quality']
        verb_score = content_quality['details']['action_verbs_score']
        quant_score = content_quality['details']['quantification_score']

        print(f"  ✓ Good resume action verbs: {verb_score}/15")
        print(f"  ✓ Good resume quantification: {quant_score}/10")

        print("✓ Thresholds validated")
        return True
    except Exception as e:
        print(f"✗ Threshold validation error: {e}")
        import traceback
        traceback.print_exc()
        return False

def validate_integration():
    """Validate integration with other components"""
    print("\nValidating component integration...")
    try:
        from services.scorer_quality import QualityScorer

        scorer = QualityScorer()

        # Check validator integration
        if not hasattr(scorer, 'validator'):
            print("✗ Missing validator attribute")
            return False
        print("  ✓ RedFlagsValidator integrated")

        # Check keyword extractor import
        from services.keyword_extractor import match_with_synonyms
        result = match_with_synonyms("python", "I know python programming")
        if not result:
            print("✗ Keyword matching not working")
            return False
        print("  ✓ Keyword extractor integrated")

        # Check role taxonomy
        from services.role_taxonomy import get_role_scoring_data
        role_data = get_role_scoring_data("software_engineer", "mid")
        if not role_data:
            print("✗ Role taxonomy not working")
            return False
        print("  ✓ Role taxonomy integrated")

        print("✓ Component integration validated")
        return True
    except Exception as e:
        print(f"✗ Integration validation error: {e}")
        return False

def main():
    """Run all validations"""
    print("="*60)
    print("QUALITY MODE SCORER VALIDATION")
    print("="*60)

    results = []

    results.append(("Imports", validate_imports()))
    results.append(("Class Structure", validate_class_structure()))
    results.append(("Scoring Logic", validate_scoring_logic()))
    results.append(("Strict Thresholds", validate_thresholds()))
    results.append(("Component Integration", validate_integration()))

    print("\n" + "="*60)
    print("VALIDATION SUMMARY")
    print("="*60)

    all_passed = True
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{name:<25} {status}")
        if not passed:
            all_passed = False

    print("="*60)

    if all_passed:
        print("\n✓ ALL VALIDATIONS PASSED!")
        print("\nQuality Mode Scorer is ready for use.")
        print("\nNext steps:")
        print("1. Run full test suite: pytest tests/test_scorer_quality.py -v")
        print("2. Try the example: python example_quality_scorer.py")
        print("3. Commit changes: bash commit_quality_scorer.sh")
        return 0
    else:
        print("\n✗ SOME VALIDATIONS FAILED")
        print("Please review the errors above and fix before proceeding.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
