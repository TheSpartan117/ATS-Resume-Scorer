#!/usr/bin/env python3
"""
Quick validation script for ATS improvements.
Run this to verify changes before running full pytest suite.
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from services.keyword_matcher import KeywordMatcher
from services.parser import ResumeData
from services.scorer_ats import ATSScorer

def print_section(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def test_pydantic_optional_fields():
    """Test that ResumeData accepts None values"""
    print_section("TEST 1: Pydantic Optional Fields")
    try:
        resume = ResumeData(
            fileName="test.pdf",
            contact=None,
            experience=None,
            education=None,
            skills=None,
            certifications=None,
            metadata=None
        )
        print("✓ ResumeData accepts None values")
        print(f"  contact type: {type(resume.contact)}")
        print(f"  experience type: {type(resume.experience)}")
        print(f"  metadata type: {type(resume.metadata)}")
        return True
    except Exception as e:
        print(f"✗ FAILED: {e}")
        return False

def test_synonym_expansion():
    """Test bidirectional synonym expansion"""
    print_section("TEST 2: Synonym Expansion")
    try:
        matcher = KeywordMatcher()

        # Test ML expansion
        ml_vars = matcher.expand_with_synonyms("ml")
        print(f"'ml' expands to: {ml_vars}")

        # Test machine learning expansion
        ml_full_vars = matcher.expand_with_synonyms("machine learning")
        print(f"'machine learning' expands to: {ml_full_vars}")

        # Verify both directions work
        has_ml_in_full = 'ml' in ml_full_vars
        has_machine_learning_in_ml = 'machine learning' in ml_vars

        print(f"\n✓ 'machine learning' includes 'ml': {has_ml_in_full}")
        print(f"✓ 'ml' includes 'machine learning': {has_machine_learning_in_ml}")

        # Test AI
        ai_vars = matcher.expand_with_synonyms("ai")
        print(f"\n'ai' expands to: {ai_vars}")

        return has_ml_in_full and has_machine_learning_in_ml and len(ai_vars) > 1
    except Exception as e:
        print(f"✗ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_keyword_matching():
    """Test keyword matching with synonyms"""
    print_section("TEST 3: Keyword Matching with Synonyms")
    try:
        matcher = KeywordMatcher()

        # Test 1: Resume has "Machine Learning", keywords have "ML"
        resume_text = "Experience with Machine Learning and Artificial Intelligence"
        keywords = ["ML", "AI", "Python"]

        result = matcher.match_keywords(resume_text, keywords)
        print(f"Resume: '{resume_text}'")
        print(f"Keywords: {keywords}")
        print(f"Matched: {result['matched']}")
        print(f"Missing: {result['missing']}")
        print(f"Percentage: {result['percentage']:.1f}%")

        ml_matched = "ML" in result['matched']
        ai_matched = "AI" in result['matched']

        print(f"\n✓ ML matched: {ml_matched}")
        print(f"✓ AI matched: {ai_matched}")

        # Test 2: Resume has "ML", keywords have "machine learning"
        print("\n" + "-"*60)
        resume_text2 = "3 years of ML and AI experience"
        keywords2 = ["machine learning", "artificial intelligence"]

        result2 = matcher.match_keywords(resume_text2, keywords2)
        print(f"Resume: '{resume_text2}'")
        print(f"Keywords: {keywords2}")
        print(f"Matched: {result2['matched']}")
        print(f"Missing: {result2['missing']}")
        print(f"Percentage: {result2['percentage']:.1f}%")

        ml_matched2 = "machine learning" in result2['matched']
        ai_matched2 = "artificial intelligence" in result2['matched']

        print(f"\n✓ 'machine learning' matched: {ml_matched2}")
        print(f"✓ 'artificial intelligence' matched: {ai_matched2}")

        return ml_matched and ai_matched and ml_matched2 and ai_matched2
    except Exception as e:
        print(f"✗ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_case_insensitive():
    """Test case-insensitive matching"""
    print_section("TEST 4: Case-Insensitive Matching")
    try:
        matcher = KeywordMatcher()

        # Resume has "Python, Javascript", keywords have "python, JavaScript"
        resume_text = "Experience with Python and Javascript development"
        keywords = ["python", "JavaScript"]

        result = matcher.match_keywords(resume_text, keywords)
        print(f"Resume: '{resume_text}'")
        print(f"Keywords: {keywords}")
        print(f"Matched: {result['matched']}")
        print(f"Percentage: {result['percentage']:.1f}%")

        # Should match both
        matched_count = len(result['matched'])
        print(f"\n✓ Matched {matched_count}/2 keywords")

        return matched_count == 2
    except Exception as e:
        print(f"✗ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_scorer_with_none():
    """Test scorer handles None values gracefully"""
    print_section("TEST 5: Scorer with None Values")
    try:
        scorer = ATSScorer()
        resume = ResumeData(
            fileName="test.pdf",
            contact=None,
            experience=None,
            education=None,
            skills=None,
            certifications=None,
            metadata=None
        )

        # Test individual components
        contact_result = scorer._score_contact_info(resume)
        print(f"Contact score: {contact_result['score']}/5")

        experience_result = scorer._score_experience(resume, "mid")
        print(f"Experience score: {experience_result['score']}/20")

        formatting_result = scorer._score_formatting(resume)
        print(f"Formatting score: {formatting_result['score']}/20")

        # Test full scoring
        result = scorer.score(resume, "software_engineer", "mid")
        print(f"\nTotal score: {result['score']}/100")

        # Check no errors
        result_str = str(result).lower()
        has_error = 'error' in result_str and 'error' not in str(result['breakdown'])

        if has_error:
            print("✗ Result contains errors")
            print(result)
            return False
        else:
            print("✓ No errors in result")
            return True

    except Exception as e:
        print(f"✗ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all validation tests"""
    print("\n" + "="*60)
    print("  ATS SCORER IMPROVEMENTS - VALIDATION")
    print("="*60)

    tests = [
        ("Pydantic Optional Fields", test_pydantic_optional_fields),
        ("Synonym Expansion", test_synonym_expansion),
        ("Keyword Matching with Synonyms", test_keyword_matching),
        ("Case-Insensitive Matching", test_case_insensitive),
        ("Scorer with None Values", test_scorer_with_none),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ Unexpected error in {name}: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))

    # Summary
    print("\n" + "="*60)
    print("  SUMMARY")
    print("="*60)

    passed = sum(1 for _, r in results if r)
    total = len(results)

    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status:8} {name}")

    print(f"\nResults: {passed}/{total} tests passed")

    if passed == total:
        print("\n✅ All validation tests passed!")
        print("\nNext step: Run full pytest suite:")
        print("  cd /Users/sabuj.mondal/ats-resume-scorer/backend")
        print("  pytest tests/test_ats_improvements.py -v")
        return 0
    else:
        print(f"\n❌ {total - passed} test(s) failed")
        print("\nPlease review the output above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
