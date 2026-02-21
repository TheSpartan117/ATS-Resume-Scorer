#!/usr/bin/env python
"""
Demo script for P3.3 Section Balance Scorer

Shows example outputs for different resume section distributions.
"""

import sys
import json
sys.path.insert(0, '/Users/sabuj.mondal/ats-resume-scorer')

from backend.services.parameters.p3_3_section_balance import SectionBalanceScorer


def print_result(title, sections, result):
    """Pretty print a scoring result"""
    print(f"\n{'=' * 80}")
    print(f"{title}")
    print(f"{'=' * 80}")

    # Show section distribution
    total_words = sum(sec.get('word_count', 0) for sec in sections.values())
    print(f"\nSection Distribution (Total: {total_words} words):")
    print("-" * 80)

    for section, data in sections.items():
        word_count = data.get('word_count', 0)
        percentage = (word_count / total_words * 100) if total_words > 0 else 0
        bar = "█" * int(percentage / 2)
        print(f"  {section:12} {word_count:4} words ({percentage:5.1f}%) {bar}")

    # Show scoring result
    print(f"\nScoring Result:")
    print("-" * 80)
    print(f"  Score:        {result['score']}/5 points")
    print(f"  Rating:       {result['rating']}")
    print(f"  Penalty:      {result['penalty_score']}")

    # Show issues if any
    if result['issues']:
        print(f"\nIssues Detected ({len(result['issues'])}):")
        print("-" * 80)
        for i, issue in enumerate(result['issues'], 1):
            print(f"  {i}. {issue['issue']}")
            print(f"     Penalty: {issue['penalty']} points")
    else:
        print(f"\n✓ No issues detected - perfect balance!")

    print()


def demo_excellent():
    """Demo: Perfect balance (5 points)"""
    scorer = SectionBalanceScorer()
    sections = {
        'experience': {'content': '...', 'word_count': 500},
        'skills': {'content': '...', 'word_count': 200},
        'education': {'content': '...', 'word_count': 150},
        'summary': {'content': '...', 'word_count': 100}
    }
    result = scorer.score(sections)
    print_result("Example 1: EXCELLENT Balance (5 points)", sections, result)


def demo_keyword_stuffing():
    """Demo: Keyword stuffing (3 points)"""
    scorer = SectionBalanceScorer()
    sections = {
        'experience': {'content': '...', 'word_count': 500},
        'skills': {'content': '...', 'word_count': 350},  # Too large!
        'education': {'content': '...', 'word_count': 100},
        'summary': {'content': '...', 'word_count': 50}
    }
    result = scorer.score(sections)
    print_result("Example 2: Keyword Stuffing (3 points)", sections, result)


def demo_insufficient_experience():
    """Demo: Insufficient experience (3 points)"""
    scorer = SectionBalanceScorer()
    sections = {
        'experience': {'content': '...', 'word_count': 300},  # Too small!
        'skills': {'content': '...', 'word_count': 200},
        'education': {'content': '...', 'word_count': 300},
        'summary': {'content': '...', 'word_count': 200}
    }
    result = scorer.score(sections)
    print_result("Example 3: Insufficient Experience (3 points)", sections, result)


def demo_verbose_summary():
    """Demo: Verbose summary (3 points)"""
    scorer = SectionBalanceScorer()
    sections = {
        'experience': {'content': '...', 'word_count': 500},
        'skills': {'content': '...', 'word_count': 200},
        'education': {'content': '...', 'word_count': 100},
        'summary': {'content': '...', 'word_count': 200}  # Too large!
    }
    result = scorer.score(sections)
    print_result("Example 4: Verbose Summary (3 points)", sections, result)


def demo_multiple_issues():
    """Demo: Multiple issues (1 point)"""
    scorer = SectionBalanceScorer()
    sections = {
        'experience': {'content': '...', 'word_count': 300},  # Too small
        'skills': {'content': '...', 'word_count': 350},      # Too large
        'education': {'content': '...', 'word_count': 150},
        'summary': {'content': '...', 'word_count': 200}      # Too large
    }
    result = scorer.score(sections)
    print_result("Example 5: Multiple Issues (1 point)", sections, result)


def demo_poor():
    """Demo: Poor balance (0 points)"""
    scorer = SectionBalanceScorer()
    sections = {
        'experience': {'content': '...', 'word_count': 150},  # Very small
        'skills': {'content': '...', 'word_count': 600},      # Very large
        'education': {'content': '...', 'word_count': 50},
        'summary': {'content': '...', 'word_count': 200}      # Too large
    }
    result = scorer.score(sections)
    print_result("Example 6: Poor Balance (0 points)", sections, result)


def main():
    """Run all demos"""
    print("\n" + "=" * 80)
    print("P3.3 SECTION BALANCE SCORER - DEMONSTRATION")
    print("=" * 80)
    print("\nThis demo shows how the scorer evaluates different section distributions.")
    print("Optimal: Experience 40-60%, Skills <25%, Summary <15%")

    demos = [
        demo_excellent,
        demo_keyword_stuffing,
        demo_insufficient_experience,
        demo_verbose_summary,
        demo_multiple_issues,
        demo_poor
    ]

    for demo in demos:
        try:
            demo()
        except Exception as e:
            print(f"\n✗ Error in demo: {e}\n")

    print("=" * 80)
    print("DEMONSTRATION COMPLETE")
    print("=" * 80)
    print("\nNext steps:")
    print("1. Run validation: python validate_p3_3.py")
    print("2. Run full tests: python test_p3_3_runner.py")
    print("3. Commit if all tests pass")
    print()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n✗ Fatal error: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)
