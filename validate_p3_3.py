#!/usr/bin/env python
"""
Quick validation script for P3.3 Section Balance Scorer

This script runs a few basic test cases to verify the implementation.
"""

import sys
sys.path.insert(0, '/Users/sabuj.mondal/ats-resume-scorer')

from backend.services.parameters.p3_3_section_balance import SectionBalanceScorer


def test_perfect_balance():
    """Test perfect section balance"""
    print("Test 1: Perfect section balance")
    scorer = SectionBalanceScorer()
    sections = {
        'experience': {'content': 'Experience content here ' * 50, 'word_count': 500},
        'skills': {'content': 'Skills content here ' * 20, 'word_count': 200},
        'education': {'content': 'Education content here ' * 15, 'word_count': 150},
        'summary': {'content': 'Summary content here ' * 10, 'word_count': 100}
    }
    # Total: 950 words
    # Experience: 500/950 = 52.6% (within 40-100% range)
    # Skills: 200/950 = 21.1% (below 25% threshold)
    # Summary: 100/950 = 10.5% (below 15% threshold)

    result = scorer.score(sections)
    print(f"  Score: {result['score']} (expected: 5)")
    print(f"  Rating: {result['rating']} (expected: EXCELLENT)")
    print(f"  Penalty: {result['penalty_score']} (expected: 0)")
    print(f"  Issues: {len(result['issues'])} (expected: 0)")
    print(f"  ✓ PASS" if result['score'] == 5 else f"  ✗ FAIL")
    print()
    return result['score'] == 5


def test_skills_too_large():
    """Test skills section too large"""
    print("Test 2: Skills too large (keyword stuffing)")
    scorer = SectionBalanceScorer()
    sections = {
        'experience': {'content': '', 'word_count': 500},  # 50%
        'skills': {'content': '', 'word_count': 300},      # 30% (>25%)
        'education': {'content': '', 'word_count': 100},   # 10%
        'summary': {'content': '', 'word_count': 100}      # 10%
    }
    # Total: 1000 words
    # Skills >25% = -2 penalty

    result = scorer.score(sections)
    print(f"  Score: {result['score']} (expected: 3)")
    print(f"  Rating: {result['rating']} (expected: GOOD)")
    print(f"  Penalty: {result['penalty_score']} (expected: -2)")
    print(f"  Issues: {len(result['issues'])} (expected: 1)")
    if result['issues']:
        print(f"  Issue: {result['issues'][0]['issue']}")
    print(f"  ✓ PASS" if result['score'] == 3 else f"  ✗ FAIL")
    print()
    return result['score'] == 3


def test_multiple_issues():
    """Test multiple section issues"""
    print("Test 3: Multiple issues (POOR)")
    scorer = SectionBalanceScorer()
    sections = {
        'experience': {'content': '', 'word_count': 200},  # 20% (<40%)
        'skills': {'content': '', 'word_count': 400},      # 40% (>25%)
        'education': {'content': '', 'word_count': 200},   # 20%
        'summary': {'content': '', 'word_count': 200}      # 20% (>15%)
    }
    # Total: 1000 words
    # Experience <40% = -2
    # Skills >25% = -2
    # Summary >15% = -1
    # Total = -5 (capped)

    result = scorer.score(sections)
    print(f"  Score: {result['score']} (expected: 0)")
    print(f"  Rating: {result['rating']} (expected: POOR)")
    print(f"  Penalty: {result['penalty_score']} (expected: -5)")
    print(f"  Issues: {len(result['issues'])} (expected: 3)")
    for issue in result['issues']:
        print(f"    - {issue['issue']}")
    print(f"  ✓ PASS" if result['score'] == 0 else f"  ✗ FAIL")
    print()
    return result['score'] == 0


def test_empty_sections():
    """Test empty sections"""
    print("Test 4: Empty sections")
    scorer = SectionBalanceScorer()
    result = scorer.score({})
    print(f"  Score: {result['score']} (expected: 0)")
    print(f"  Rating: {result['rating']} (expected: POOR)")
    print(f"  Penalty: {result['penalty_score']} (expected: 0)")
    print(f"  Total words: {result['total_words']} (expected: 0)")
    print(f"  ✓ PASS" if result['score'] == 0 else f"  ✗ FAIL")
    print()
    return result['score'] == 0


def main():
    """Run all validation tests"""
    print("=" * 80)
    print("P3.3 Section Balance Scorer - Quick Validation")
    print("=" * 80)
    print()

    tests = [
        test_perfect_balance,
        test_skills_too_large,
        test_multiple_issues,
        test_empty_sections
    ]

    results = []
    for test in tests:
        try:
            results.append(test())
        except Exception as e:
            print(f"  ✗ EXCEPTION: {e}")
            results.append(False)

    print("=" * 80)
    print(f"Results: {sum(results)}/{len(results)} tests passed")
    print("=" * 80)

    if all(results):
        print("SUCCESS! All validation tests passed.")
        print()
        print("Next steps:")
        print("1. Run full test suite: python test_p3_3_runner.py")
        print("2. If all tests pass, commit the changes")
        return 0
    else:
        print("FAILED! Some validation tests failed.")
        print("Review the implementation and fix issues.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
