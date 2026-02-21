#!/usr/bin/env python3
"""
Quick validation script for P6.2 Job Hopping Penalty implementation.
"""

from services.parameters.p6_2_job_hopping import JobHoppingPenaltyScorer

def test_basic_functionality():
    """Test basic functionality of the scorer."""
    scorer = JobHoppingPenaltyScorer()

    # Test 1: No short stints
    print("Test 1: No short stints...")
    employment = [
        {'title': 'Senior Engineer', 'start_date': '2020-01', 'end_date': '2022-06'},
        {'title': 'Engineer', 'start_date': '2018-01', 'end_date': '2019-12'}
    ]
    result = scorer.score(employment)
    assert result['penalty'] == 0, f"Expected 0, got {result['penalty']}"
    assert result['short_stints_count'] == 0, f"Expected 0, got {result['short_stints_count']}"
    print("✓ PASS: No short stints = 0 penalty")

    # Test 2: One short stint
    print("\nTest 2: One short stint...")
    employment = [
        {'title': 'Senior Engineer', 'start_date': '2021-01', 'end_date': '2023-06'},
        {'title': 'Engineer', 'start_date': '2020-01', 'end_date': '2020-10'},  # 9 months
    ]
    result = scorer.score(employment)
    assert result['penalty'] == -1, f"Expected -1, got {result['penalty']}"
    assert result['short_stints_count'] == 1, f"Expected 1, got {result['short_stints_count']}"
    print("✓ PASS: One short stint = -1 penalty")

    # Test 3: Multiple short stints (capped)
    print("\nTest 3: Multiple short stints (capped at -3)...")
    employment = [
        {'title': 'Engineer A', 'start_date': '2023-01', 'end_date': '2023-08'},  # 7 months
        {'title': 'Engineer B', 'start_date': '2022-01', 'end_date': '2022-09'},  # 8 months
        {'title': 'Engineer C', 'start_date': '2021-01', 'end_date': '2021-10'},  # 9 months
        {'title': 'Engineer D', 'start_date': '2020-01', 'end_date': '2020-08'},  # 7 months
    ]
    result = scorer.score(employment)
    assert result['penalty'] == -3, f"Expected -3, got {result['penalty']}"
    assert result['short_stints_count'] == 4, f"Expected 4, got {result['short_stints_count']}"
    assert result['max_penalty'] == -3
    print("✓ PASS: Four short stints capped at -3 penalty")

    # Test 4: Contract roles excluded
    print("\nTest 4: Contract roles excluded...")
    employment = [
        {'title': 'Contract Engineer', 'start_date': '2022-01', 'end_date': '2022-08'},  # 7 months
        {'title': 'Senior Engineer', 'start_date': '2019-01', 'end_date': '2020-12'}
    ]
    result = scorer.score(employment)
    assert result['penalty'] == 0, f"Expected 0, got {result['penalty']}"
    assert result['short_stints_count'] == 0, f"Expected 0, got {result['short_stints_count']}"
    assert len(result['flagged_positions']) == 1  # Still flagged but excluded
    assert result['flagged_positions'][0]['is_excluded'] is True
    print("✓ PASS: Contract roles excluded from penalty")

    # Test 5: Exactly 12 months
    print("\nTest 5: Exactly 12 months (not penalized)...")
    employment = [
        {'title': 'Engineer', 'start_date': '2022-01', 'end_date': '2023-01'},  # Exactly 12 months
    ]
    result = scorer.score(employment)
    assert result['penalty'] == 0, f"Expected 0, got {result['penalty']}"
    print("✓ PASS: Exactly 12 months = no penalty")

    # Test 6: 11 months (penalized)
    print("\nTest 6: 11 months (penalized)...")
    employment = [
        {'title': 'Engineer', 'start_date': '2022-01', 'end_date': '2022-12'},  # 11 months
    ]
    result = scorer.score(employment)
    assert result['penalty'] == -1, f"Expected -1, got {result['penalty']}"
    print("✓ PASS: 11 months = -1 penalty")

    # Test 7: Empty employment
    print("\nTest 7: Empty employment...")
    result = scorer.score([])
    assert result['penalty'] == 0
    assert result['short_stints_count'] == 0
    print("✓ PASS: Empty employment = 0 penalty")

    print("\n" + "="*60)
    print("All basic tests passed! ✓")
    print("="*60)

if __name__ == '__main__':
    test_basic_functionality()
