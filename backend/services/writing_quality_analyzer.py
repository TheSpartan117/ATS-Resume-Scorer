"""
Writing Quality Analyzer - Evaluates writing polish and style.

This module provides:
- Severity-weighted grammar scoring
- Word variety analysis (repetition detection)
- Sentence structure diversity analysis
"""

from typing import Dict, List
from collections import Counter


class WritingQualityAnalyzer:
    """
    Analyzes writing quality and polish.

    Components:
    - Grammar severity weighting
    - Word variety checking
    - Sentence structure analysis
    """

    # Severity weights for grammar errors
    SEVERITY_WEIGHTS = {
        'spelling': -2.0,      # Critical - unprofessional
        'grammar': -1.5,       # Serious - affects clarity
        'punctuation': -1.0,   # Moderate - minor issue
        'style': -0.5,         # Suggestion - nitpicky
        'typo': -2.0,          # Critical - careless
    }

    def score_grammar_with_severity(self, errors: List[Dict]) -> Dict:
        """
        Score grammar with severity-based weighting (max 10 pts).

        Args:
            errors: List of grammar error dictionaries with 'category' and 'message'

        Returns:
            Dictionary with score, deduction, and error breakdown
        """
        total_deduction = 0.0
        errors_by_category = {}

        for error in errors:
            category = error.get('category', 'grammar')
            weight = self.SEVERITY_WEIGHTS.get(category, -1.0)
            total_deduction += abs(weight)

            if category not in errors_by_category:
                errors_by_category[category] = []
            errors_by_category[category].append(error)

        # Cap deductions at 10
        total_deduction = min(total_deduction, 10.0)
        score = max(0, 10.0 - total_deduction)

        return {
            'score': score,
            'total_errors': len(errors),
            'deduction': total_deduction,
            'by_category': errors_by_category
        }
