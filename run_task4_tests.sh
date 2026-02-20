#!/bin/bash
# Task 4 Test Runner
# Run this script to verify Task 4 implementation

echo "=========================================="
echo "Task 4: SuggestionGenerator Tests"
echo "=========================================="
echo ""

cd "$(dirname "$0")/backend"

echo "Running suggestion_generator tests..."
echo ""

python -m pytest tests/test_suggestion_generator.py -v --tb=short

TEST_RESULT=$?

echo ""
echo "=========================================="
if [ $TEST_RESULT -eq 0 ]; then
    echo "✅ All tests PASSED!"
    echo ""
    echo "Next step: Commit the changes"
    echo "Run: git add backend/services/suggestion_generator.py backend/tests/test_suggestion_generator.py"
    echo "Then: git commit -m 'Task 4: Implement SuggestionGenerator with location mapping'"
else
    echo "❌ Tests FAILED!"
    echo ""
    echo "Please review test output above and fix issues."
fi
echo "=========================================="

exit $TEST_RESULT
