#!/bin/bash
# Commit script for Task 7: Update Section Endpoint

echo "=========================================="
echo "Task 7: Update Section Endpoint"
echo "Preparing to commit changes..."
echo "=========================================="
echo ""

cd /Users/sabuj.mondal/ats-resume-scorer

echo "Files to be committed:"
echo "  - backend/api/editor.py"
echo "  - backend/tests/test_update_section.py"
echo "  - backend/requirements.txt"
echo ""

# Show diff summary
echo "Changes summary:"
git diff --stat backend/api/editor.py backend/tests/test_update_section.py backend/requirements.txt
echo ""

# Add files
echo "Adding files to git..."
git add backend/api/editor.py backend/tests/test_update_section.py backend/requirements.txt

# Check if there are changes to commit
if git diff --cached --quiet; then
    echo "No changes to commit."
    exit 0
fi

echo ""
echo "Creating commit..."

# Create commit
git commit -m "$(cat <<'EOF'
feat(api): add update-section endpoint for Rich Editor

- Implement POST /api/editor/update-section endpoint
- Add HTML to DOCX text conversion using BeautifulSoup
- Integrate with DocxTemplateManager for section updates
- Add comprehensive test suite with 4 test cases
- Handle edge cases: invalid session, invalid paragraph range
- Add beautifulsoup4 dependency to requirements.txt

Test coverage:
- test_update_experience_section: Basic update flow
- test_update_section_preserves_formatting: HTML parsing
- test_update_section_invalid_range: Error handling for invalid indices
- test_update_section_invalid_session: Error handling for nonexistent session

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
EOF
)"

echo ""
echo "=========================================="
echo "Commit created successfully!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "  1. Review commit: git show HEAD"
echo "  2. Push to remote: git push origin main"
echo ""
