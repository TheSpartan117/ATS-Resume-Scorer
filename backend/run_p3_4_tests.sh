#!/bin/bash

# Script to run P3.4 ATS Formatting tests
# Task 19 verification

echo "========================================"
echo "Running P3.4 ATS Formatting Tests"
echo "========================================"
echo ""

cd /Users/sabuj.mondal/ats-resume-scorer/backend

# Run the tests
python -m pytest tests/services/parameters/test_p3_4_ats_formatting.py -v

# Check exit code
if [ $? -eq 0 ]; then
    echo ""
    echo "========================================"
    echo "✓ All tests passed!"
    echo "========================================"
    echo ""
    echo "Next step: Commit the changes"
    echo ""
    echo "Run the following commands:"
    echo "  git add backend/services/parameters/p3_4_ats_formatting.py"
    echo "  git add backend/tests/services/parameters/test_p3_4_ats_formatting.py"
    echo "  git commit -m \"feat(P3.4): implement ATS formatting scorer with parsing issue detection (7pts)\""
else
    echo ""
    echo "========================================"
    echo "✗ Tests failed!"
    echo "========================================"
    echo "Please review the errors above."
fi
