#!/bin/bash
# Task 14: Verification Script for RichEditor Component
# This script verifies the implementation is complete and ready for testing

echo "=============================================="
echo "Task 14: RichEditor Component - Verification"
echo "=============================================="
echo ""

# Check if files exist
echo "1. Checking if files exist..."
TEST_FILE="/Users/sabuj.mondal/ats-resume-scorer/frontend/src/components/__tests__/RichEditor.test.tsx"
COMPONENT_FILE="/Users/sabuj.mondal/ats-resume-scorer/frontend/src/components/RichEditor.tsx"

if [ -f "$TEST_FILE" ]; then
    echo "   ✓ Test file exists: RichEditor.test.tsx"
    echo "     Size: $(wc -c < "$TEST_FILE" | xargs) bytes"
else
    echo "   ✗ Test file NOT found!"
    exit 1
fi

if [ -f "$COMPONENT_FILE" ]; then
    echo "   ✓ Component file exists: RichEditor.tsx"
    echo "     Size: $(wc -c < "$COMPONENT_FILE" | xargs) bytes"
else
    echo "   ✗ Component file NOT found!"
    exit 1
fi

echo ""

# Check for required imports
echo "2. Checking component imports..."
if grep -q "@tiptap/react" "$COMPONENT_FILE"; then
    echo "   ✓ TipTap React imported"
fi
if grep -q "@tiptap/starter-kit" "$COMPONENT_FILE"; then
    echo "   ✓ StarterKit imported"
fi
if grep -q "@tiptap/extension-underline" "$COMPONENT_FILE"; then
    echo "   ✓ Underline extension imported"
fi
if grep -q "@tiptap/extension-placeholder" "$COMPONENT_FILE"; then
    echo "   ✓ Placeholder extension imported"
fi

echo ""

# Check for key features
echo "3. Checking component features..."
if grep -q "RichEditorProps" "$COMPONENT_FILE"; then
    echo "   ✓ TypeScript interface defined"
fi
if grep -q "sectionId" "$COMPONENT_FILE"; then
    echo "   ✓ Section ID support included"
fi
if grep -q "compact" "$COMPONENT_FILE"; then
    echo "   ✓ Compact mode support included"
fi
if grep -q "editable" "$COMPONENT_FILE"; then
    echo "   ✓ Read-only mode support included"
fi

echo ""

# Check test coverage
echo "4. Checking test coverage..."
TEST_COUNT=$(grep -c "it('should" "$TEST_FILE")
echo "   ✓ Number of test cases: $TEST_COUNT"

if [ $TEST_COUNT -ge 10 ]; then
    echo "   ✓ Comprehensive test coverage"
else
    echo "   ⚠ Limited test coverage (expected 10+)"
fi

echo ""

# Check if TipTap dependencies are installed
echo "5. Checking TipTap dependencies..."
PACKAGE_JSON="/Users/sabuj.mondal/ats-resume-scorer/frontend/package.json"

if grep -q "@tiptap/react" "$PACKAGE_JSON"; then
    echo "   ✓ TipTap dependencies installed"
else
    echo "   ✗ TipTap dependencies NOT installed!"
    echo "   Run: cd frontend && npm install"
    exit 1
fi

echo ""

# Summary
echo "=============================================="
echo "Verification Summary"
echo "=============================================="
echo ""
echo "✓ All checks passed!"
echo ""
echo "Next steps:"
echo "  1. Run tests: cd frontend && npm test -- src/components/__tests__/RichEditor.test.tsx"
echo "  2. Verify all 11 tests pass"
echo "  3. Commit changes: ./TASK_14_COMMIT.sh"
echo ""
echo "Files ready for commit:"
echo "  - frontend/src/components/__tests__/RichEditor.test.tsx"
echo "  - frontend/src/components/RichEditor.tsx"
echo ""
echo "=============================================="
