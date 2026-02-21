#!/usr/bin/env python3
"""
Manual test script for P4.1 Grammar Scorer
Run this to verify the implementation works before running pytest
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.parameters.p4_1_grammar import GrammarScorer


def test_perfect_text():
    """Test with perfect grammar"""
    print("\n=== Test 1: Perfect Text ===")
    scorer = GrammarScorer()
    text = "Led team of 5 engineers to develop scalable microservices architecture."
    result = scorer.score(text)

    print(f"Score: {result['score']}/10")
    print(f"Total errors: {result['total_errors']}")
    print(f"Critical errors: {result['critical_errors']}")
    print(f"Minor errors: {result['minor_errors']}")
    print(f"Tier: {result['tier']}")
    print(f"Message: {result['message']}")

    assert result['score'] == 10, f"Expected 10, got {result['score']}"
    assert result['total_errors'] == 0, f"Expected 0 errors, got {result['total_errors']}"
    print("✓ PASSED")


def test_spelling_errors():
    """Test with spelling errors"""
    print("\n=== Test 2: Spelling Errors ===")
    scorer = GrammarScorer()
    text = "I am a softwere enginer with excelent skils in Python."
    result = scorer.score(text)

    print(f"Score: {result['score']}/10")
    print(f"Total errors: {result['total_errors']}")
    print(f"Critical errors: {result['critical_errors']}")
    print(f"Minor errors: {result['minor_errors']}")
    print(f"Tier: {result['tier']}")
    print(f"Message: {result['message']}")

    if result['errors']:
        print(f"\nErrors found:")
        for i, error in enumerate(result['errors'][:3], 1):
            print(f"  {i}. {error['category']}: {error['message']}")

    assert result['score'] < 10, f"Should lose points for spelling errors"
    print("✓ PASSED")


def test_calculate_score_logic():
    """Test the score calculation logic directly"""
    print("\n=== Test 3: Score Calculation Logic ===")
    scorer = GrammarScorer()

    # Test tier 1: 0 errors = 10 points
    result = scorer._calculate_score(0, 0)
    assert result['score'] == 10, f"0 errors should give 10 points, got {result['score']}"
    print(f"✓ 0 errors = {result['score']} points")

    # Test tier 2: 1-2 minor = 9 points
    result = scorer._calculate_score(0, 2)
    assert result['score'] == 9, f"2 minor should give 9 points, got {result['score']}"
    print(f"✓ 2 minor errors = {result['score']} points")

    # Test tier 3: 1 critical = 7 points
    result = scorer._calculate_score(1, 0)
    assert result['score'] == 7, f"1 critical should give 7 points, got {result['score']}"
    print(f"✓ 1 critical error = {result['score']} points")

    # Test tier 4: 2 critical = 5 points
    result = scorer._calculate_score(2, 0)
    assert result['score'] == 5, f"2 critical should give 5 points, got {result['score']}"
    print(f"✓ 2 critical errors = {result['score']} points")

    # Test tier 5: 4 critical = 3 points
    result = scorer._calculate_score(4, 0)
    assert result['score'] == 3, f"4 critical should give 3 points, got {result['score']}"
    print(f"✓ 4 critical errors = {result['score']} points")

    # Test tier 6: 6 critical = 0 points
    result = scorer._calculate_score(6, 0)
    assert result['score'] == 0, f"6 critical should give 0 points, got {result['score']}"
    print(f"✓ 6 critical errors = {result['score']} points")

    print("✓ PASSED")


def test_empty_text():
    """Test with empty text"""
    print("\n=== Test 4: Empty Text ===")
    scorer = GrammarScorer()
    result = scorer.score("")

    print(f"Score: {result['score']}/10")
    print(f"Message: {result['message']}")

    assert result['score'] == 10, "Empty text should get max score"
    print("✓ PASSED")


def test_result_structure():
    """Test result structure"""
    print("\n=== Test 5: Result Structure ===")
    scorer = GrammarScorer()
    text = "Led team to develop new features."
    result = scorer.score(text)

    required_fields = [
        'score', 'total_errors', 'critical_errors', 'minor_errors',
        'errors', 'tier', 'message', 'parameter', 'name', 'max_points'
    ]

    for field in required_fields:
        assert field in result, f"Missing required field: {field}"
        print(f"✓ Has field: {field}")

    assert result['parameter'] == 'P4.1'
    assert result['name'] == 'Grammar & Spelling'
    assert result['max_points'] == 10

    print("✓ PASSED")


def main():
    """Run all tests"""
    print("=" * 60)
    print("P4.1 Grammar Scorer - Manual Test Suite")
    print("=" * 60)

    try:
        test_perfect_text()
        test_spelling_errors()
        test_calculate_score_logic()
        test_empty_text()
        test_result_structure()

        print("\n" + "=" * 60)
        print("ALL TESTS PASSED ✓")
        print("=" * 60)

    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
