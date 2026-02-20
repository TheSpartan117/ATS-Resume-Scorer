#!/bin/bash
# Task 14: Commit Script for RichEditor Component

cd /Users/sabuj.mondal/ats-resume-scorer

# Add the test and component files
git add frontend/src/components/__tests__/RichEditor.test.tsx
git add frontend/src/components/RichEditor.tsx

# Commit with the exact message from the plan
git commit -m "$(cat <<'EOF'
feat(components): add RichEditor component with TipTap

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
EOF
)"

echo ""
echo "✓ Task 14 committed successfully!"
echo ""
echo "Files committed:"
echo "  - frontend/src/components/__tests__/RichEditor.test.tsx"
echo "  - frontend/src/components/RichEditor.tsx"
