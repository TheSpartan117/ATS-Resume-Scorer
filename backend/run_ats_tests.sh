#!/bin/bash
# ATS Scorer Improvements Test Runner
# Run this script to verify all improvements are working

echo "=========================================="
echo "ATS SCORER IMPROVEMENTS - TEST RUNNER"
echo "=========================================="
echo ""

# Change to backend directory
cd /Users/sabuj.mondal/ats-resume-scorer/backend || exit 1

echo "Running ATS improvement tests..."
echo ""

# Run tests with verbose output
python -m pytest tests/test_ats_improvements.py -v --tb=short

# Capture exit code
TEST_EXIT_CODE=$?

echo ""
echo "=========================================="

if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo "✅ ALL TESTS PASSED!"
    echo ""
    echo "Next steps:"
    echo "1. Review the changes in ATS_IMPROVEMENTS_SUMMARY.md"
    echo "2. Use code review skill: /superpowers:requesting-code-review"
    echo "3. Commit changes with:"
    echo "   git add -A"
    echo "   git commit -m 'feat: implement ATS scorer improvements'"
else
    echo "❌ SOME TESTS FAILED"
    echo ""
    echo "Please review the test output above."
    echo "Check ATS_IMPROVEMENTS_SUMMARY.md for implementation details."
fi

echo "=========================================="

exit $TEST_EXIT_CODE
