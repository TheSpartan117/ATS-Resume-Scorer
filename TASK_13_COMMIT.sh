#!/bin/bash

# Task 13: Frontend - Suggestions Panel Component
# Commit script following the implementation plan

cd /Users/sabuj.mondal/ats-resume-scorer

echo "=== Task 13: Committing SuggestionsPanel Component ==="

# Stage the files
git add frontend/src/components/SuggestionsPanel.tsx
git add frontend/src/components/__tests__/SuggestionsPanel.test.tsx
git add frontend/TEST_INSTRUCTIONS.md

# Commit with the exact message format from the plan
git commit -m "feat(frontend): add SuggestionsPanel component with grouped suggestions

Implements Task 13 from enhanced editor UX redesign:
- Displays current ATS score prominently
- Groups suggestions by severity (Critical, Warnings, Suggestions, Info)
- Collapsible groups with count badges
- Re-score button at the top
- Progress indicator showing fixed count
- Last scored timestamp display
- Empty state handling
- Independent scrolling
- Integrates with SuggestionCard component

Tests include:
- Score display
- Severity grouping
- Count badges
- Re-score button functionality
- Toggle groups
- Suggestion click handling
- Last scored timestamp
- Empty state
- Progress indicator
- Scrollable container

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"

echo ""
echo "✅ Task 13 committed successfully!"
echo ""
echo "Next steps:"
echo "1. Run tests: cd frontend && npm test -- __tests__/SuggestionsPanel.test.tsx --run"
echo "2. Verify all tests pass"
echo "3. Push to remote if needed: git push origin main"
