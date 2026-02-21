#!/usr/bin/env python3
"""
Simple test runner script for action verb scorer.
Run this to verify the implementation works correctly.
"""

import sys
from services.action_verb_scorer import ActionVerbScorer

def test_coverage_score_perfect():
    """100% coverage with Tier 2+ verbs = 7 pts"""
    scorer = ActionVerbScorer()
    bullets = [
        "Developed REST API",           # Tier 2
        "Implemented authentication",   # Tier 2
        "Led team of engineers",        # Tier 3
        "Pioneered ML infrastructure"   # Tier 4
    ]
    result = scorer.score(bullets, 'intermediary')
    assert result['coverage_score'] == 7, f"Expected 7, got {result['coverage_score']}"
    print("✓ test_coverage_score_perfect passed")

def test_tier_score_excellent():
    """Average tier 3.5+ = 8 pts"""
    scorer = ActionVerbScorer()
    bullets = [
        "Pioneered ML infrastructure",     # Tier 4
        "Revolutionized deployment",       # Tier 4
        "Transformed engineering culture", # Tier 4
        "Led cross-functional team"        # Tier 3
    ]
    result = scorer.score(bullets, 'senior')
    assert result['tier_score'] == 8, f"Expected 8, got {result['tier_score']}"
    print("✓ test_tier_score_excellent passed")

def test_perfect_score():
    """Perfect senior resume with high tier verbs"""
    scorer = ActionVerbScorer()
    bullets = [
        "Pioneered ML platform",           # Tier 4
        "Transformed engineering culture", # Tier 4
        "Led cross-functional team",       # Tier 3
        "Architected cloud infrastructure",# Tier 3 (actually Tier 4 based on data)
        "Launched product line"            # Tier 3
    ]
    result = scorer.score(bullets, 'senior')
    print(f"  Coverage: {result['coverage_percentage']}%, Score: {result['coverage_score']}/7")
    print(f"  Avg Tier: {result['average_tier']}, Score: {result['tier_score']}/8")
    print(f"  Total: {result['score']}/15")
    assert result['coverage_score'] == 7, f"Expected coverage 7, got {result['coverage_score']}"
    print("✓ test_perfect_score passed")

def test_poor_score():
    """Poor beginner with weak verbs"""
    scorer = ActionVerbScorer()
    bullets = [
        "Responsible for coding",   # Tier 0
        "Worked on features",       # Tier 0
        "Helped with deployment",   # Tier 0
        "Assisted team members",    # Tier 0 (actually Tier 1 based on "assisted")
        "Managed some tasks"        # Tier 1
    ]
    result = scorer.score(bullets, 'beginner')
    print(f"  Coverage: {result['coverage_percentage']}%, Score: {result['coverage_score']}/7")
    print(f"  Avg Tier: {result['average_tier']}, Score: {result['tier_score']}/8")
    print(f"  Total: {result['score']}/15")
    assert result['coverage_score'] == 0, f"Expected coverage 0, got {result['coverage_score']}"
    assert result['tier_score'] == 0 or result['tier_score'] == 2, f"Expected tier 0 or 2, got {result['tier_score']}"
    print("✓ test_poor_score passed")

def test_tier_distribution():
    """Tier distribution is included"""
    scorer = ActionVerbScorer()
    bullets = [
        "Pioneered platform",      # Tier 4
        "Led team",               # Tier 3
        "Developed API",          # Tier 2
        "Managed tasks",          # Tier 1
        "Responsible for work"    # Tier 0
    ]
    result = scorer.score(bullets, 'intermediary')
    dist = result['tier_distribution']
    print(f"  Tier distribution: {dist}")
    assert 'tier_distribution' in result
    assert dist[4] == 1, f"Expected 1 Tier 4, got {dist[4]}"
    assert dist[3] == 1, f"Expected 1 Tier 3, got {dist[3]}"
    assert dist[2] == 1, f"Expected 1 Tier 2, got {dist[2]}"
    assert dist[1] == 1, f"Expected 1 Tier 1, got {dist[1]}"
    assert dist[0] == 1, f"Expected 1 Tier 0, got {dist[0]}"
    print("✓ test_tier_distribution passed")

def test_empty_bullets():
    """Empty bullet list = 0 pts"""
    scorer = ActionVerbScorer()
    result = scorer.score([], 'senior')
    assert result['score'] == 0
    assert result['coverage_score'] == 0
    assert result['tier_score'] == 0
    print("✓ test_empty_bullets passed")

def main():
    print("\nRunning Action Verb Scorer Tests\n" + "="*50)

    tests = [
        test_coverage_score_perfect,
        test_tier_score_excellent,
        test_perfect_score,
        test_poor_score,
        test_tier_distribution,
        test_empty_bullets
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"✗ {test.__name__} failed: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test.__name__} error: {e}")
            failed += 1

    print("\n" + "="*50)
    print(f"Results: {passed} passed, {failed} failed")

    if failed > 0:
        sys.exit(1)
    else:
        print("\n✅ All tests passed!")
        sys.exit(0)

if __name__ == '__main__':
    main()
