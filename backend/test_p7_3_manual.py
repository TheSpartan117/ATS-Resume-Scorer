#!/usr/bin/env python3
"""
Manual test script for P7.3 Passive Voice Detection
Run this to verify the implementation works correctly
"""

from services.parameters.p7_3_passive_voice import PassiveVoiceScorer


def test_basic_functionality():
    """Test basic passive voice detection"""
    scorer = PassiveVoiceScorer()

    print("Test 1: No passive voice (should be 2.0 pts)")
    bullets = [
        "Led team of 10 engineers",
        "Developed scalable API",
        "Increased revenue by 50%"
    ]
    result = scorer.score(bullets)
    print(f"  Score: {result['score']}, Passive count: {result['passive_count']}")
    assert result['score'] == 2.0, f"Expected 2.0, got {result['score']}"
    print("  ✓ PASSED\n")

    print("Test 2: One passive bullet (should be 1.5 pts)")
    bullets = [
        "Led development team",
        "Was responsible for API development",  # Passive
        "Launched new feature"
    ]
    result = scorer.score(bullets)
    print(f"  Score: {result['score']}, Passive count: {result['passive_count']}")
    print(f"  Passive bullets: {[b['text'] for b in result['passive_bullets']]}")
    assert result['score'] == 1.5, f"Expected 1.5, got {result['score']}"
    assert result['passive_count'] == 1, f"Expected 1 passive, got {result['passive_count']}"
    print("  ✓ PASSED\n")

    print("Test 3: Two passive bullets (should be 1.0 pt)")
    bullets = [
        "Was assigned to mobile project",  # Passive
        "Were tasked with improving performance",  # Passive
        "Implemented CI/CD pipeline"
    ]
    result = scorer.score(bullets)
    print(f"  Score: {result['score']}, Passive count: {result['passive_count']}")
    assert result['score'] == 1.0, f"Expected 1.0, got {result['score']}"
    assert result['passive_count'] == 2, f"Expected 2 passive, got {result['passive_count']}"
    print("  ✓ PASSED\n")

    print("Test 4: Four passive bullets (should be 0.0 pts - capped)")
    bullets = [
        "Was responsible for frontend development",  # Passive
        "Were tasked with API implementation",  # Passive
        "Has been assigned to mobile team",  # Passive
        "Had been given project leadership role",  # Passive
        "Improved system performance"
    ]
    result = scorer.score(bullets)
    print(f"  Score: {result['score']}, Passive count: {result['passive_count']}")
    assert result['score'] == 0.0, f"Expected 0.0, got {result['score']}"
    assert result['passive_count'] == 4, f"Expected 4 passive, got {result['passive_count']}"
    print("  ✓ PASSED\n")

    print("Test 5: Various passive patterns")
    bullets = [
        "Was developed by engineering",  # was + verb
        "Were implemented across systems",  # were + verb
        "Has been tested thoroughly",  # has been + verb
        "Have been optimized for performance",  # have been + verb
        "Had been created before launch",  # had been + verb
    ]
    result = scorer.score(bullets)
    print(f"  Score: {result['score']}, Passive count: {result['passive_count']}")
    print(f"  Patterns found: {result['details']['patterns_found']}")
    assert result['passive_count'] == 5, f"Expected 5 passive, got {result['passive_count']}"
    assert result['score'] == 0.0, f"Expected 0.0 (capped), got {result['score']}"
    print("  ✓ PASSED\n")

    print("Test 6: Empty bullets (should be 2.0 pts)")
    result = scorer.score([])
    print(f"  Score: {result['score']}, Passive count: {result['passive_count']}")
    assert result['score'] == 2.0, f"Expected 2.0, got {result['score']}"
    print("  ✓ PASSED\n")

    print("Test 7: Case insensitive detection")
    bullets = [
        "WAS DEVELOPED BY TEAM",
        "Were Implemented Across Systems",
        "has been tested thoroughly"
    ]
    result = scorer.score(bullets)
    print(f"  Score: {result['score']}, Passive count: {result['passive_count']}")
    assert result['passive_count'] == 3, f"Expected 3 passive, got {result['passive_count']}"
    print("  ✓ PASSED\n")

    print("=" * 60)
    print("ALL TESTS PASSED! ✓")
    print("=" * 60)


if __name__ == '__main__':
    test_basic_functionality()
