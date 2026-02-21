#!/usr/bin/env python3
"""
Quick test runner for quantification scorer.
Run with: python run_quantification_scorer_tests.py
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from services.quantification_scorer import QuantificationScorer


def test_basic_functionality():
    """Test basic functionality without pytest."""
    print("Testing QuantificationScorer...")

    scorer = QuantificationScorer()

    # Test 1: Beginner excellent
    print("\n1. Testing beginner excellent quantification...")
    bullets = [
        "Increased revenue by 45%",
        "Reduced costs by $200K annually",
        "Led team of 12 engineers",
        "Completed project in 6 months",
        "Worked on various projects",
        "Improved system performance"
    ]
    result = scorer.score(bullets, 'beginner')
    print(f"   Score: {result['score']}/10 (expected: 10)")
    print(f"   Weighted rate: {result['weighted_quantification_rate']}%")
    print(f"   High: {result['high_count']}, Medium: {result['medium_count']}, Low: {result['low_count']}")
    print(f"   ✓ PASS" if result['score'] == 10 else f"   ✗ FAIL")

    # Test 2: Intermediary good
    print("\n2. Testing intermediary good quantification...")
    bullets = [
        "Improved performance 2x faster",
        "Managed 15 concurrent projects",
        "Worked on backend services",
        "Developed REST APIs",
        "Collaborated with teams"
    ]
    result = scorer.score(bullets, 'intermediary')
    print(f"   Score: {result['score']}/10 (expected: 6)")
    print(f"   Weighted rate: {result['weighted_quantification_rate']}%")
    print(f"   ✓ PASS" if result['score'] == 6 else f"   ✗ FAIL")

    # Test 3: Senior excellent
    print("\n3. Testing senior excellent quantification...")
    bullets = [
        "Scaled system to handle 10M+ users (3x growth)",
        "Reduced infrastructure costs by $500K (40%)",
        "Increased team productivity by 60%",
        "Led cross-functional team of 20",
        "Architected microservices"
    ]
    result = scorer.score(bullets, 'senior')
    print(f"   Score: {result['score']}/10 (expected: 10)")
    print(f"   Weighted rate: {result['weighted_quantification_rate']}%")
    print(f"   High: {result['high_count']}, Medium: {result['medium_count']}, Low: {result['low_count']}")
    print(f"   ✓ PASS" if result['score'] == 10 else f"   ✗ FAIL")

    # Test 4: Empty bullets
    print("\n4. Testing empty bullets...")
    result = scorer.score([], 'intermediary')
    print(f"   Score: {result['score']}/10 (expected: 0)")
    print(f"   Weighted rate: {result['weighted_quantification_rate']}%")
    print(f"   ✓ PASS" if result['score'] == 0 else f"   ✗ FAIL")

    # Test 5: Detailed breakdown
    print("\n5. Testing detailed breakdown...")
    bullets = [
        "Increased revenue by 45%",
        "Reduced costs by $100K",
        "Led team of 10",
        "Serving 50K users",
        "Fixed 15 bugs",
        "Worked on features"
    ]
    result = scorer.score(bullets, 'intermediary')
    print(f"   Score: {result['score']}/10")
    print(f"   Total bullets: {result['total_bullets']} (expected: 6)")
    print(f"   Quantified: {result['quantified_count']} (expected: 5)")
    print(f"   High: {result['high_count']} (expected: 2)")
    print(f"   Medium: {result['medium_count']} (expected: 2)")
    print(f"   Low: {result['low_count']} (expected: 1)")

    checks = [
        result['total_bullets'] == 6,
        result['quantified_count'] == 5,
        result['high_count'] == 2,
        result['medium_count'] == 2,
        result['low_count'] == 1,
        'explanation' in result,
        'threshold' in result
    ]
    print(f"   ✓ PASS" if all(checks) else f"   ✗ FAIL")

    # Test 6: Recommendations
    print("\n6. Testing recommendations...")
    recommendations = scorer.get_recommendations(result)
    print(f"   Generated {len(recommendations)} recommendations")
    for i, rec in enumerate(recommendations, 1):
        print(f"   {i}. {rec[:80]}...")
    print(f"   ✓ PASS" if len(recommendations) > 0 else f"   ✗ FAIL")

    print("\n" + "="*70)
    print("Basic tests complete! Run full test suite with:")
    print("  python -m pytest tests/services/test_quantification_scorer.py -v")
    print("="*70)


if __name__ == "__main__":
    test_basic_functionality()
