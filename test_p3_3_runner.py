#!/usr/bin/env python
"""
Test runner for P3.3 Section Balance Scorer

Run this script to test the implementation:
    python test_p3_3_runner.py
"""

import sys
import subprocess

def run_tests():
    """Run tests for P3.3 Section Balance Scorer"""
    print("=" * 80)
    print("Testing P3.3: Section Balance Scorer (5 points)")
    print("=" * 80)
    print()

    # Step 1: Run tests to verify they fail (if not implemented)
    print("Step 1: Running tests to verify implementation...")
    print("-" * 80)

    result = subprocess.run(
        ["python", "-m", "pytest",
         "backend/tests/services/parameters/test_p3_3_section_balance.py",
         "-v", "--tb=short"],
        cwd="/Users/sabuj.mondal/ats-resume-scorer"
    )

    print()
    print("=" * 80)

    if result.returncode == 0:
        print("SUCCESS: All tests passed!")
        print("=" * 80)
        print()
        print("Next step: Review the implementation and commit with:")
        print('git add backend/services/parameters/p3_3_section_balance.py')
        print('git add backend/tests/services/parameters/test_p3_3_section_balance.py')
        print('git commit -m "feat(P3.3): implement section balance scorer with keyword stuffing detection (5pts)"')
        return 0
    else:
        print("FAILED: Some tests failed.")
        print("=" * 80)
        print("Review the errors above and fix the implementation.")
        return 1

if __name__ == "__main__":
    sys.exit(run_tests())
