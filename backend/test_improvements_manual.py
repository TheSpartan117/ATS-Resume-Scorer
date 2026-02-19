#!/usr/bin/env python3
"""
Manual test script to verify ATS improvements before running full test suite.
"""
import sys
sys.path.insert(0, '/Users/sabuj.mondal/ats-resume-scorer/backend')

from services.scorer_ats import ATSScorer
from services.parser import ResumeData
from services.keyword_matcher import KeywordMatcher

def test_pydantic_none_handling():
    """Test that ResumeData handles None values properly"""
    print("\n=== Testing Pydantic None Handling ===")
    try:
        # Test with None values
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
        print(f"  contact: {resume.contact}")
        print(f"  experience: {resume.experience}")
        print(f"  metadata: {resume.metadata}")
        return True
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False

def test_case_insensitive_matching():
    """Test case-insensitive keyword matching"""
    print("\n=== Testing Case-Insensitive Matching ===")
    try:
        scorer = ATSScorer()
        resume = ResumeData(
            fileName="test.pdf",
            contact={"name": "John Doe"},
            experience=[{
                "title": "Developer",
                "company": "Company",
                "description": "Worked with Python, Javascript, and Docker"
            }],
            skills=["Python", "JavaScript", "Docker"],
        )

        result = scorer._score_keywords(resume, "software_engineer", "entry", "")
        matched = result['details']['matched']

        print(f"  Matched keywords: {matched}")
        print(f"  Match score: {result['score']}/35")

        # Check if Python/python matched
        python_matched = any('python' in str(m).lower() for m in matched)
        print(f"  Python matched: {python_matched}")

        return result['score'] > 0
    except Exception as e:
        print(f"✗ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_synonym_matching():
    """Test ML/AI synonym matching"""
    print("\n=== Testing Synonym Matching (ML/AI) ===")
    try:
        matcher = KeywordMatcher()

        # Test expanding ML
        ml_variations = matcher.expand_with_synonyms("ML")
        print(f"  ML variations: {ml_variations}")

        # Test expanding machine learning
        ml_full_variations = matcher.expand_with_synonyms("machine learning")
        print(f"  'machine learning' variations: {ml_full_variations}")

        # Test AI
        ai_variations = matcher.expand_with_synonyms("AI")
        print(f"  AI variations: {ai_variations}")

        # Now test matching
        resume_text = "Experience with Machine Learning and Artificial Intelligence projects"
        keywords = ["ML", "AI", "deep learning"]

        result = matcher.match_keywords(resume_text, keywords)
        print(f"  Match result: {result}")
        print(f"  Matched: {result['matched']}")
        print(f"  Percentage: {result['percentage']}%")

        return len(result['matched']) > 0
    except Exception as e:
        print(f"✗ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_fuzzy_matching():
    """Test fuzzy matching for similar terms"""
    print("\n=== Testing Fuzzy Matching ===")
    try:
        matcher = KeywordMatcher()

        # Test Javascript vs JavaScript
        resume_text = "Javascript development and React"
        keywords = ["JavaScript", "React"]

        result = matcher.match_keywords(resume_text, keywords)
        print(f"  Resume: {resume_text}")
        print(f"  Keywords: {keywords}")
        print(f"  Matched: {result['matched']}")
        print(f"  Percentage: {result['percentage']}%")

        return result['percentage'] >= 50
    except Exception as e:
        print(f"✗ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_scorer_with_none_values():
    """Test scorer handles None values gracefully"""
    print("\n=== Testing Scorer with None Values ===")
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

        # Test individual scoring methods
        contact_result = scorer._score_contact_info(resume)
        print(f"  Contact score: {contact_result['score']}/5")

        experience_result = scorer._score_experience(resume, "mid")
        print(f"  Experience score: {experience_result['score']}/20")

        formatting_result = scorer._score_formatting(resume)
        print(f"  Formatting score: {formatting_result['score']}/20")

        # Test full scoring
        result = scorer.score(resume, "software_engineer", "mid")
        print(f"  Total score: {result['score']}/100")
        print(f"  No errors: {'error' not in str(result)}")

        return 'error' not in str(result).lower()
    except Exception as e:
        print(f"✗ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("ATS SCORER IMPROVEMENTS - MANUAL TESTS")
    print("=" * 60)

    tests = [
        ("Pydantic None Handling", test_pydantic_none_handling),
        ("Case-Insensitive Matching", test_case_insensitive_matching),
        ("Synonym Matching (ML/AI)", test_synonym_matching),
        ("Fuzzy Matching", test_fuzzy_matching),
        ("Scorer with None Values", test_scorer_with_none_values),
    ]

    results = []
    for name, test_func in tests:
        result = test_func()
        results.append((name, result))

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, r in results if r)
    total = len(results)

    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n✓ All manual tests passed! Ready for full test suite.")
        sys.exit(0)
    else:
        print(f"\n✗ {total - passed} test(s) failed. Need fixes.")
        sys.exit(1)
