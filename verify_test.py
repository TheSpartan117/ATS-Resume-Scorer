#!/usr/bin/env python3
"""
Quick verification script to check if the distribution test will pass.
"""
import subprocess
import sys

def run_test():
    """Run the specific failing test."""
    cmd = [
        "pytest",
        "backend/tests/test_score_distribution.py::test_score_all_resumes_adaptive_scorer_quality_mode",
        "-v",
        "--tb=short"
    ]

    print("Running test: test_score_all_resumes_adaptive_scorer_quality_mode")
    print("=" * 80)

    result = subprocess.run(cmd, cwd="/Users/sabuj.mondal/ats-resume-scorer")

    return result.returncode

def run_all_distribution_tests():
    """Run all distribution tests."""
    cmd = [
        "pytest",
        "backend/tests/test_score_distribution.py",
        "-v"
    ]

    print("\n\nRunning all distribution tests...")
    print("=" * 80)

    result = subprocess.run(cmd, cwd="/Users/sabuj.mondal/ats-resume-scorer")

    return result.returncode

if __name__ == "__main__":
    # First run the specific test
    result1 = run_test()

    # Then run all distribution tests
    result2 = run_all_distribution_tests()

    if result1 == 0 and result2 == 0:
        print("\n" + "=" * 80)
        print("SUCCESS: All tests passed!")
        print("=" * 80)
        sys.exit(0)
    else:
        print("\n" + "=" * 80)
        print("FAILURE: Some tests failed")
        print("=" * 80)
        sys.exit(1)
