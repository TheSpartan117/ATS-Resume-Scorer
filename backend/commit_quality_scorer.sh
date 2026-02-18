#!/bin/bash
# Commit script for Quality Mode Scorer implementation

echo "Adding files to git..."
git add services/scorer_quality.py
git add tests/test_scorer_quality.py
git add QUALITY_SCORER_README.md
git add example_quality_scorer.py

echo "Creating commit..."
git commit -m "feat: implement quality mode scorer

- Created QualityScorer class with comprehensive scoring logic
- Implements strict thresholds for action verbs (90%+) and quantification (60%+)
- 5 scoring categories: content quality (30), achievement depth (20), keywords/fit (20), polish (15), readability (15)
- Integrates with RedFlagsValidator for grammar and content validation
- Analyzes action verbs, quantification, metrics depth, vague phrases
- Penalizes grammar errors and unprofessional contact info
- Evaluates structure, bullet points, and document length
- Includes 30+ comprehensive tests covering all scoring categories
- Added documentation and example usage

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"

echo "Done! Run 'git push' to push to remote."
