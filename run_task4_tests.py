#!/usr/bin/env python3
"""
Task 4 Test Runner
Run this script to verify Task 4 implementation
"""
import sys
import subprocess
from pathlib import Path

def main():
    print("=" * 50)
    print("Task 4: SuggestionGenerator Tests")
    print("=" * 50)
    print()

    # Change to backend directory
    backend_dir = Path(__file__).parent / "backend"

    print(f"Running tests from: {backend_dir}")
    print()

    # Run pytest
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/test_suggestion_generator.py", "-v", "--tb=short"],
        cwd=backend_dir,
        capture_output=False
    )

    print()
    print("=" * 50)
    if result.returncode == 0:
        print("✅ All tests PASSED!")
        print()
        print("Next step: Commit the changes")
        print("Run:")
        print("  git add backend/services/suggestion_generator.py")
        print("  git add backend/tests/test_suggestion_generator.py")
        print("  git commit -m 'Task 4: Implement SuggestionGenerator with location mapping'")
    else:
        print("❌ Tests FAILED!")
        print()
        print("Please review test output above and fix issues.")
    print("=" * 50)

    return result.returncode

if __name__ == "__main__":
    sys.exit(main())
