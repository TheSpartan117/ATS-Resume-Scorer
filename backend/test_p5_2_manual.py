#!/usr/bin/env python3
"""
Manual test script for P5.2 Career Recency
"""

from datetime import datetime, timedelta
from services.parameters.p5_2_career_recency import CareerRecencyScorer


def test_basic_functionality():
    """Test basic functionality"""
    scorer = CareerRecencyScorer()

    print("=" * 60)
    print("Testing P5.2 Career Recency Scorer")
    print("=" * 60)

    # Test 1: Currently employed
    print("\nTest 1: Currently employed (Present)")
    experience1 = [
        {
            'title': 'Senior Engineer',
            'company': 'Tech Corp',
            'dates': '2020 - Present'
        }
    ]
    result1 = scorer.score(experience1)
    print(f"Score: {result1['score']}/3")
    print(f"Status: {result1['recency_status']}")
    print(f"Months since: {result1['months_since_last']}")
    assert result1['score'] == 3, "Currently employed should be 3 pts"
    print("✓ PASSED")

    # Test 2: Left 1 month ago
    print("\nTest 2: Left 1 month ago")
    one_month_ago = (datetime.now() - timedelta(days=30)).strftime('%Y-%m')
    experience2 = [
        {
            'title': 'Engineer',
            'company': 'Tech Corp',
            'dates': f'2020 - {one_month_ago}'
        }
    ]
    result2 = scorer.score(experience2)
    print(f"Score: {result2['score']}/3")
    print(f"Status: {result2['recency_status']}")
    print(f"Months since: {result2['months_since_last']}")
    assert result2['score'] == 2, "Left 1 month ago should be 2 pts"
    print("✓ PASSED")

    # Test 3: Left 6 months ago
    print("\nTest 3: Left 6 months ago")
    six_months_ago = (datetime.now() - timedelta(days=180)).strftime('%Y-%m')
    experience3 = [
        {
            'title': 'Engineer',
            'company': 'Tech Corp',
            'dates': f'2020 - {six_months_ago}'
        }
    ]
    result3 = scorer.score(experience3)
    print(f"Score: {result3['score']}/3")
    print(f"Status: {result3['recency_status']}")
    print(f"Months since: {result3['months_since_last']}")
    assert result3['score'] == 1, "Left 6 months ago should be 1 pt"
    print("✓ PASSED")

    # Test 4: Left 2 years ago
    print("\nTest 4: Left 2 years ago")
    experience4 = [
        {
            'title': 'Engineer',
            'company': 'Old Corp',
            'dates': '2010 - 2018'
        }
    ]
    result4 = scorer.score(experience4)
    print(f"Score: {result4['score']}/3")
    print(f"Status: {result4['recency_status']}")
    print(f"Months since: {result4['months_since_last']}")
    assert result4['score'] == 0, "Left 2 years ago should be 0 pts"
    print("✓ PASSED")

    # Test 5: Multiple jobs, most recent is current
    print("\nTest 5: Multiple jobs, most recent is current")
    experience5 = [
        {
            'title': 'Junior Engineer',
            'company': 'Old Corp',
            'dates': '2015 - 2018'
        },
        {
            'title': 'Senior Engineer',
            'company': 'Current Corp',
            'dates': '2018 - Present'
        }
    ]
    result5 = scorer.score(experience5)
    print(f"Score: {result5['score']}/3")
    print(f"Status: {result5['recency_status']}")
    print(f"Months since: {result5['months_since_last']}")
    assert result5['score'] == 3, "Most recent current job should be 3 pts"
    print("✓ PASSED")

    # Test 6: Empty experience
    print("\nTest 6: Empty experience")
    result6 = scorer.score([])
    print(f"Score: {result6['score']}/3")
    print(f"Status: {result6['recency_status']}")
    assert result6['score'] == 0, "Empty experience should be 0 pts"
    print("✓ PASSED")

    # Test 7: Date format variations
    print("\nTest 7: Date format variations")
    test_dates = [
        '2020-01 - Present',
        'Jan 2020 - Present',
        'January 2020 - Present',
        '2020 - Present'
    ]
    for dates in test_dates:
        experience = [{'title': 'Engineer', 'company': 'Corp', 'dates': dates}]
        result = scorer.score(experience)
        print(f"  {dates}: {result['score']}/3 - {result['recency_status']}")
        assert result['score'] == 3, f"Failed for format: {dates}"
    print("✓ PASSED")

    print("\n" + "=" * 60)
    print("All manual tests PASSED!")
    print("=" * 60)


if __name__ == '__main__':
    test_basic_functionality()
