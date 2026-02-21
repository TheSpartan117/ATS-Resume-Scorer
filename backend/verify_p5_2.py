#!/usr/bin/env python3
"""
Quick verification script for P5.2 Career Recency implementation
"""

import sys
from datetime import datetime, timedelta

# Add backend to path
sys.path.insert(0, '/Users/sabuj.mondal/ats-resume-scorer/backend')

from services.parameters.p5_2_career_recency import CareerRecencyScorer


def run_verification():
    """Run basic verification tests"""
    scorer = CareerRecencyScorer()

    print("\n" + "="*70)
    print("P5.2 Career Recency - Implementation Verification")
    print("="*70)

    passed = 0
    failed = 0

    # Test 1: Currently employed
    print("\n[Test 1] Currently employed (Present)")
    exp1 = [{'title': 'Engineer', 'company': 'Tech', 'dates': '2020 - Present'}]
    result1 = scorer.score(exp1)
    if result1['score'] == 3 and result1['recency_status'] == 'currently_employed':
        print("✓ PASSED - Score: 3/3, Status: currently_employed")
        passed += 1
    else:
        print(f"✗ FAILED - Expected 3/currently_employed, got {result1['score']}/{result1['recency_status']}")
        failed += 1

    # Test 2: Left 2 months ago
    print("\n[Test 2] Left 2 months ago")
    two_months = (datetime.now() - timedelta(days=60)).strftime('%Y-%m')
    exp2 = [{'title': 'Engineer', 'company': 'Tech', 'dates': f'2020 - {two_months}'}]
    result2 = scorer.score(exp2)
    if result2['score'] == 2 and result2['recency_status'] == 'left_within_3_months':
        print(f"✓ PASSED - Score: 2/3, Months: {result2['months_since_last']}")
        passed += 1
    else:
        print(f"✗ FAILED - Expected 2/left_within_3_months, got {result2['score']}/{result2['recency_status']}")
        failed += 1

    # Test 3: Left 6 months ago
    print("\n[Test 3] Left 6 months ago")
    six_months = (datetime.now() - timedelta(days=180)).strftime('%Y-%m')
    exp3 = [{'title': 'Engineer', 'company': 'Tech', 'dates': f'2020 - {six_months}'}]
    result3 = scorer.score(exp3)
    if result3['score'] == 1 and result3['recency_status'] == 'left_3_12_months_ago':
        print(f"✓ PASSED - Score: 1/3, Months: {result3['months_since_last']}")
        passed += 1
    else:
        print(f"✗ FAILED - Expected 1/left_3_12_months_ago, got {result3['score']}/{result3['recency_status']}")
        failed += 1

    # Test 4: Left 2 years ago
    print("\n[Test 4] Left 2 years ago")
    exp4 = [{'title': 'Engineer', 'company': 'Old', 'dates': '2015 - 2018'}]
    result4 = scorer.score(exp4)
    if result4['score'] == 0 and result4['recency_status'] == 'left_over_12_months_ago':
        print(f"✓ PASSED - Score: 0/3, Months: {result4['months_since_last']}")
        passed += 1
    else:
        print(f"✗ FAILED - Expected 0/left_over_12_months_ago, got {result4['score']}/{result4['recency_status']}")
        failed += 1

    # Test 5: Empty experience
    print("\n[Test 5] Empty experience")
    result5 = scorer.score([])
    if result5['score'] == 0 and result5['recency_status'] == 'no_experience':
        print("✓ PASSED - Score: 0/3, Status: no_experience")
        passed += 1
    else:
        print(f"✗ FAILED - Expected 0/no_experience, got {result5['score']}/{result5['recency_status']}")
        failed += 1

    # Test 6: Multiple jobs with current
    print("\n[Test 6] Multiple jobs (most recent is current)")
    exp6 = [
        {'title': 'Junior', 'company': 'Old', 'dates': '2015 - 2018'},
        {'title': 'Senior', 'company': 'Current', 'dates': '2018 - Present'}
    ]
    result6 = scorer.score(exp6)
    if result6['score'] == 3 and result6['recency_status'] == 'currently_employed':
        print("✓ PASSED - Score: 3/3, Status: currently_employed")
        passed += 1
    else:
        print(f"✗ FAILED - Expected 3/currently_employed, got {result6['score']}/{result6['recency_status']}")
        failed += 1

    # Test 7: Date format variations
    print("\n[Test 7] Date format variations")
    formats = [
        '2020-01 - Present',
        'Jan 2020 - Present',
        'January 2020 - Present',
        '2020 - Present'
    ]
    format_passed = True
    for fmt in formats:
        exp = [{'title': 'Eng', 'company': 'Corp', 'dates': fmt}]
        result = scorer.score(exp)
        if result['score'] != 3 or result['recency_status'] != 'currently_employed':
            print(f"  ✗ Failed for format: {fmt}")
            format_passed = False

    if format_passed:
        print("✓ PASSED - All date formats handled correctly")
        passed += 1
    else:
        print("✗ FAILED - Some date formats not handled")
        failed += 1

    # Summary
    print("\n" + "="*70)
    print(f"Results: {passed}/{passed+failed} tests passed")
    print("="*70)

    if failed == 0:
        print("\n✅ All verification tests PASSED! Implementation is working correctly.")
        return 0
    else:
        print(f"\n❌ {failed} test(s) FAILED. Please review implementation.")
        return 1


if __name__ == '__main__':
    sys.exit(run_verification())
