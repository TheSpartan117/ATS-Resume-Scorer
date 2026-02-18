#!/bin/bash
# Commit script for Task 28: Score Distribution Validation

echo "========================================="
echo "Task 28: Score Distribution Validation"
echo "========================================="
echo ""

# Stage the distribution validation files
echo "Staging files..."
git add tests/test_score_distribution.py
git add tests/SCORE_DISTRIBUTION_README.md
git add validate_distribution.py
git add run_distribution_test.py
git add DISTRIBUTION_VALIDATION_SUMMARY.md

# Show what will be committed
echo ""
echo "Files to be committed:"
git status --short

# Create the commit
echo ""
echo "Creating commit..."
git commit -m "$(cat <<'EOF'
test: validate score distribution

Implemented comprehensive score distribution validation with 20 test resumes.

Changes:
- Created test_score_distribution.py with 20 diverse test resumes
- Added 4 test functions covering both scorers (Legacy + Adaptive)
- Validates distribution against harsh but realistic targets:
  * 0-40: 30% ± 10% (harsh on poor quality)
  * 41-60: 40% ± 10% (most resumes are mediocre)
  * 61-75: 20% ± 10% (good but not exceptional)
  * 76-85: 8% ± 5% (very good - rare)
  * 86-100: 2% ± 3% (exceptional - extremely rare)

Test Coverage:
- Legacy scorer (scorer_legacy.py)
- Adaptive scorer Quality Coach mode
- Adaptive scorer ATS Simulation mode
- Comparison between both scoring systems

Features:
- 20 test resumes spanning full quality spectrum
- Automatic distribution calculation
- Pass/fail validation with tolerances
- Detailed reporting with breakdowns
- Standalone validation scripts
- Comprehensive documentation

Files:
- tests/test_score_distribution.py (692 lines)
- tests/SCORE_DISTRIBUTION_README.md (documentation)
- validate_distribution.py (standalone runner)
- run_distribution_test.py (test wrapper)
- DISTRIBUTION_VALIDATION_SUMMARY.md (summary)

Usage:
  pytest tests/test_score_distribution.py -v -s
  python validate_distribution.py
  python run_distribution_test.py

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
EOF
)"

echo ""
echo "========================================="
echo "Commit created successfully!"
echo "========================================="
echo ""
echo "To push to remote:"
echo "  git push origin main"
