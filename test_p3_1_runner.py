#!/usr/bin/env python3
"""
Simple test runner for P3.1 Page Count Scorer
This allows testing without pytest if needed
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.services.parameters.p3_1_page_count import PageCountScorer, score_page_count

def test_basic_functionality():
    """Test basic functionality"""
    scorer = PageCountScorer()

    print("Testing P3.1 Page Count Scorer...")
    print("=" * 60)

    # Test beginner
    print("\n1. BEGINNER TESTS:")
    result = scorer.score(1, 'beginner')
    print(f"   1 page: {result['score']} pts (expected: 5) ✓" if result['score'] == 5 else f"   1 page: {result['score']} pts (expected: 5) ✗")

    result = scorer.score(2, 'beginner')
    print(f"   2 pages: {result['score']} pts (expected: 3) ✓" if result['score'] == 3 else f"   2 pages: {result['score']} pts (expected: 3) ✗")

    result = scorer.score(3, 'beginner')
    print(f"   3 pages: {result['score']} pts (expected: 0) ✓" if result['score'] == 0 else f"   3 pages: {result['score']} pts (expected: 0) ✗")

    # Test intermediary
    print("\n2. INTERMEDIARY TESTS:")
    result = scorer.score(1, 'intermediary')
    print(f"   1 page: {result['score']} pts (expected: 5) ✓" if result['score'] == 5 else f"   1 page: {result['score']} pts (expected: 5) ✗")

    result = scorer.score(2, 'intermediary')
    print(f"   2 pages: {result['score']} pts (expected: 5) ✓" if result['score'] == 5 else f"   2 pages: {result['score']} pts (expected: 5) ✗")

    result = scorer.score(3, 'intermediary')
    print(f"   3 pages: {result['score']} pts (expected: 2) ✓" if result['score'] == 2 else f"   3 pages: {result['score']} pts (expected: 2) ✗")

    result = scorer.score(4, 'intermediary')
    print(f"   4 pages: {result['score']} pts (expected: 0) ✓" if result['score'] == 0 else f"   4 pages: {result['score']} pts (expected: 0) ✗")

    # Test senior
    print("\n3. SENIOR TESTS:")
    result = scorer.score(1, 'senior')
    print(f"   1 page: {result['score']} pts (expected: 2) ✓" if result['score'] == 2 else f"   1 page: {result['score']} pts (expected: 2) ✗")

    result = scorer.score(2, 'senior')
    print(f"   2 pages: {result['score']} pts (expected: 5) ✓" if result['score'] == 5 else f"   2 pages: {result['score']} pts (expected: 5) ✗")

    result = scorer.score(3, 'senior')
    print(f"   3 pages: {result['score']} pts (expected: 4) ✓" if result['score'] == 4 else f"   3 pages: {result['score']} pts (expected: 4) ✗")

    result = scorer.score(4, 'senior')
    print(f"   4 pages: {result['score']} pts (expected: 0) ✓" if result['score'] == 0 else f"   4 pages: {result['score']} pts (expected: 0) ✗")

    # Test convenience function
    print("\n4. CONVENIENCE FUNCTION TEST:")
    result = score_page_count(2, 'senior')
    print(f"   score_page_count(2, 'senior'): {result['score']} pts (expected: 5) ✓" if result['score'] == 5 else f"   score_page_count(2, 'senior'): {result['score']} pts (expected: 5) ✗")

    # Test edge cases
    print("\n5. EDGE CASES:")
    result = scorer.score(0, 'intermediary')
    print(f"   0 pages: {result['score']} pts (expected: 0) ✓" if result['score'] == 0 else f"   0 pages: {result['score']} pts (expected: 0) ✗")

    result = scorer.score(-1, 'senior')
    print(f"   -1 pages: {result['score']} pts (expected: 0) ✓" if result['score'] == 0 else f"   -1 pages: {result['score']} pts (expected: 0) ✗")

    # Test case insensitivity
    print("\n6. CASE INSENSITIVITY:")
    result1 = scorer.score(2, 'SENIOR')
    result2 = scorer.score(2, 'Senior')
    result3 = scorer.score(2, 'senior')
    all_match = result1['score'] == result2['score'] == result3['score'] == 5
    print(f"   'SENIOR', 'Senior', 'senior' all return 5 pts: ✓" if all_match else "   Case insensitivity test: ✗")

    print("\n" + "=" * 60)
    print("Basic functionality tests completed!")
    print("\nExample output:")
    print("-" * 60)
    result = scorer.score(3, 'beginner')
    print(f"Page Count: {result['page_count']}")
    print(f"Level: {result['level']}")
    print(f"Score: {result['score']}/5")
    print(f"Optimal: {result['optimal_pages']}")
    print(f"Recommendation: {result['recommendation']}")

if __name__ == '__main__':
    test_basic_functionality()
