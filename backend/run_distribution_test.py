#!/usr/bin/env python3
"""
Standalone script to run score distribution validation.

This script can be run directly to validate score distribution without pytest:
    python run_distribution_test.py
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import test functions
from tests.test_score_distribution import (
    test_score_all_resumes_legacy_scorer,
    test_score_all_resumes_adaptive_scorer_quality_mode,
    test_score_all_resumes_adaptive_scorer_ats_mode,
    test_score_distribution_comparison
)


def main():
    """Run all distribution tests and generate report."""
    print("="*80)
    print("SCORE DISTRIBUTION VALIDATION")
    print("Testing 20 diverse resumes across both scoring systems")
    print("="*80)

    try:
        # Test 1: Legacy Scorer
        print("\n\nTest 1/4: Legacy Scorer (scorer.py)")
        test_score_all_resumes_legacy_scorer()

        # Test 2: Adaptive Scorer - Quality Coach Mode
        print("\n\nTest 2/4: Adaptive Scorer - Quality Coach Mode")
        test_score_all_resumes_adaptive_scorer_quality_mode()

        # Test 3: Adaptive Scorer - ATS Simulation Mode
        print("\n\nTest 3/4: Adaptive Scorer - ATS Simulation Mode")
        test_score_all_resumes_adaptive_scorer_ats_mode()

        # Test 4: Comparison
        print("\n\nTest 4/4: Scorer Comparison")
        test_score_distribution_comparison()

        # Summary
        print("\n" + "="*80)
        print("ALL DISTRIBUTION TESTS PASSED")
        print("="*80)
        print("\nValidation Summary:")
        print("- All 20 test resumes were scored successfully")
        print("- Score distributions match harsh but realistic targets")
        print("- Both scoring systems produce appropriate distributions")
        print("\nTarget Distribution:")
        print("  0-40:   30% ± 10% (harsh on poor quality)")
        print("  41-60:  40% ± 10% (most resumes are mediocre)")
        print("  61-75:  20% ± 10% (good but not excellent)")
        print("  76-85:  8% ± 5%   (very good)")
        print("  86-100: 2% ± 3%   (exceptional - rare)")
        print("\nConclusion: Scoring system is properly calibrated for harsh but realistic evaluation.")
        print("="*80)

        return 0

    except AssertionError as e:
        print(f"\n\nTEST FAILED: {e}")
        print("\nThe score distribution does not match the target distribution.")
        print("This indicates the scoring system may be too lenient or too harsh.")
        return 1

    except Exception as e:
        print(f"\n\nERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
