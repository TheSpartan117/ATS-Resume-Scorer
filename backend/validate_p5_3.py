"""
Manual validation script for P5.3: Experience Depth
Tests key scenarios to ensure implementation is correct before running pytest.
"""

from services.parameters.p5_3_experience_depth import ExperienceDepthScorer


def test_scenario(name, experiences, level, expected_score, expected_count):
    """Test a specific scenario and print results"""
    scorer = ExperienceDepthScorer()
    result = scorer.score(experiences, level)

    success = (
        result['score'] == expected_score and
        result['entry_count'] == expected_count
    )

    status = "✓ PASS" if success else "✗ FAIL"
    print(f"{status} | {name}")
    print(f"  Expected: score={expected_score}, count={expected_count}")
    print(f"  Got:      score={result['score']}, count={result['entry_count']}")
    print(f"  Details:  {result['details']}")
    print()

    return success


def create_complete_entry(title, company):
    """Helper to create a complete entry"""
    return {
        'title': title,
        'company': company,
        'startDate': 'Jan 2020',
        'endDate': 'Dec 2021',
        'achievements': ['Built features', 'Led team']
    }


def main():
    """Run validation tests"""
    print("=" * 80)
    print("P5.3 Experience Depth - Manual Validation")
    print("=" * 80)
    print()

    all_pass = True

    # Test 1: Beginner with exactly 2 entries (should pass)
    print("TEST 1: Beginner - Exactly 2 entries (minimum)")
    experiences = [
        create_complete_entry("Engineer", "Company A"),
        create_complete_entry("Intern", "Company B")
    ]
    all_pass &= test_scenario(
        "Beginner with 2 entries",
        experiences, 'beginner',
        expected_score=2, expected_count=2
    )

    # Test 2: Beginner with 1 entry (should fail)
    print("TEST 2: Beginner - Only 1 entry (below minimum)")
    experiences = [
        create_complete_entry("Engineer", "Company A")
    ]
    all_pass &= test_scenario(
        "Beginner with 1 entry",
        experiences, 'beginner',
        expected_score=0, expected_count=1
    )

    # Test 3: Intermediary with exactly 3 entries (should pass)
    print("TEST 3: Intermediary - Exactly 3 entries (minimum)")
    experiences = [
        create_complete_entry("Senior Dev", "A"),
        create_complete_entry("Developer", "B"),
        create_complete_entry("Junior Dev", "C")
    ]
    all_pass &= test_scenario(
        "Intermediary with 3 entries",
        experiences, 'intermediary',
        expected_score=2, expected_count=3
    )

    # Test 4: Intermediary with 2 entries (should fail)
    print("TEST 4: Intermediary - Only 2 entries (below minimum)")
    experiences = [
        create_complete_entry("Engineer", "A"),
        create_complete_entry("Developer", "B")
    ]
    all_pass &= test_scenario(
        "Intermediary with 2 entries",
        experiences, 'intermediary',
        expected_score=0, expected_count=2
    )

    # Test 5: Senior with exactly 4 entries (should pass)
    print("TEST 5: Senior - Exactly 4 entries (minimum)")
    experiences = [
        create_complete_entry("Manager", "A"),
        create_complete_entry("Senior Eng", "B"),
        create_complete_entry("Tech Lead", "C"),
        create_complete_entry("Developer", "D")
    ]
    all_pass &= test_scenario(
        "Senior with 4 entries",
        experiences, 'senior',
        expected_score=2, expected_count=4
    )

    # Test 6: Senior with 3 entries (should fail)
    print("TEST 6: Senior - Only 3 entries (below minimum)")
    experiences = [
        create_complete_entry("Manager", "A"),
        create_complete_entry("Lead", "B"),
        create_complete_entry("Engineer", "C")
    ]
    all_pass &= test_scenario(
        "Senior with 3 entries",
        experiences, 'senior',
        expected_score=0, expected_count=3
    )

    # Test 7: Missing company (should not count)
    print("TEST 7: Entry missing company")
    experiences = [
        create_complete_entry("Engineer", "A"),
        {
            'title': 'Developer',
            # Missing company
            'startDate': 'Jan 2020',
            'endDate': 'Dec 2021',
            'achievements': ['Built features']
        }
    ]
    all_pass &= test_scenario(
        "Beginner with incomplete entry (no company)",
        experiences, 'beginner',
        expected_score=0, expected_count=1
    )

    # Test 8: Missing dates (should not count)
    print("TEST 8: Entry missing dates")
    experiences = [
        create_complete_entry("Engineer", "A"),
        {
            'title': 'Developer',
            'company': 'B',
            # Missing dates
            'achievements': ['Built features']
        }
    ]
    all_pass &= test_scenario(
        "Beginner with incomplete entry (no dates)",
        experiences, 'beginner',
        expected_score=0, expected_count=1
    )

    # Test 9: Has description but no bullets (should count)
    print("TEST 9: Entry with description only (no bullets)")
    experiences = [
        create_complete_entry("Engineer", "A"),
        {
            'title': 'Developer',
            'company': 'B',
            'startDate': 'Jan 2020',
            'endDate': 'Dec 2021',
            'description': 'Developed web applications and APIs'
        }
    ]
    all_pass &= test_scenario(
        "Beginner with description-only entry",
        experiences, 'beginner',
        expected_score=2, expected_count=2
    )

    # Test 10: Empty experience list
    print("TEST 10: Empty experience list")
    all_pass &= test_scenario(
        "Beginner with no experiences",
        [], 'beginner',
        expected_score=0, expected_count=0
    )

    # Test 11: None experience list
    print("TEST 11: None experience list")
    all_pass &= test_scenario(
        "Beginner with None experiences",
        None, 'beginner',
        expected_score=0, expected_count=0
    )

    # Print summary
    print("=" * 80)
    if all_pass:
        print("✓ ALL TESTS PASSED")
    else:
        print("✗ SOME TESTS FAILED")
    print("=" * 80)

    return all_pass


if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
