"""
P4.1 - Grammar & Spelling (10 pts)

Professional writing quality with tiered penalties.

Research basis:
- Critical errors (grammar, spelling): Most visible and damaging to credibility
- Minor errors (style, punctuation): Less critical but still affects professionalism
- Tiered scoring: Graduated penalties based on error count and severity

Implementation:
- Uses LanguageTool for professional-grade grammar checking
- Error classification: Critical vs Minor
- Tiered scoring: 0 errors = 10pts, escalating penalties
"""

from typing import Dict, List
from backend.services.grammar_checker import get_grammar_checker


class GrammarScorer:
    """
    Score resume based on grammar and spelling quality.

    Scoring tiers:
    - 0 errors = 10 points (excellent)
    - 1-2 minor = 9 points (very good)
    - 1 critical or 3-4 minor = 7 points (good)
    - 2-3 critical or 5-7 minor = 5 points (acceptable)
    - 4-5 critical or 8-11 minor = 3 points (needs work)
    - 6+ critical or 12+ minor = 0 points (poor)

    Error weights:
    - Critical (grammar, spelling): -0.5 pts each
    - Minor (style, punctuation): -0.25 pts each
    """

    def __init__(self):
        """Initialize grammar scorer"""
        self.grammar_checker = get_grammar_checker()
        self.max_points = 10

        # Error category mapping
        self.critical_categories = {'grammar', 'spelling', 'typo'}
        self.minor_categories = {'style', 'punctuation', 'capitalization', 'other'}

    def score(self, text: str) -> Dict:
        """
        Score text for grammar and spelling quality.

        Args:
            text: Resume text to analyze

        Returns:
            Dictionary with:
            - score: Points (0-10)
            - total_errors: Total error count
            - critical_errors: Count of critical errors
            - minor_errors: Count of minor errors
            - errors: List of error details
            - tier: Quality tier name
            - message: Human-readable feedback
        """
        # Handle empty/very short text
        if not text or len(text.strip()) < 5:
            return {
                'score': 10,
                'total_errors': 0,
                'critical_errors': 0,
                'minor_errors': 0,
                'errors': [],
                'tier': 'excellent',
                'message': 'Text too short to analyze - assuming perfect',
                'parameter': 'P4.1',
                'name': 'Grammar & Spelling',
                'max_points': self.max_points
            }

        # Run grammar check
        check_result = self.grammar_checker.check(text)

        # Classify errors by severity
        critical_errors = 0
        minor_errors = 0
        error_details = []

        for issue in check_result.get('issues', []):
            category = issue.get('category', 'other')
            severity = self._classify_severity(category, issue)

            error_detail = {
                'message': issue.get('message', ''),
                'category': category,
                'severity': severity,
                'context': issue.get('context', ''),
                'replacements': issue.get('replacements', [])
            }
            error_details.append(error_detail)

            if severity == 'critical':
                critical_errors += 1
            else:
                minor_errors += 1

        # Calculate score
        result = self._calculate_score(critical_errors, minor_errors)
        result['errors'] = error_details
        result['parameter'] = 'P4.1'
        result['name'] = 'Grammar & Spelling'
        result['max_points'] = self.max_points

        return result

    def _classify_severity(self, category: str, issue: Dict) -> str:
        """
        Classify error severity.

        Args:
            category: Error category
            issue: Full issue details

        Returns:
            'critical' or 'minor'
        """
        # Check if already classified by grammar checker
        if issue.get('severity') == 'critical':
            return 'critical'

        # Classify based on category
        if category in self.critical_categories:
            return 'critical'
        else:
            return 'minor'

    def _calculate_score(self, critical_errors: int, minor_errors: int) -> Dict:
        """
        Calculate score based on error counts.

        Tiered scoring:
        - 0 errors = 10 points
        - 1-2 minor = 9 points
        - 1 critical or 3-4 minor = 7 points
        - 2-3 critical or 5-7 minor = 5 points
        - 4-5 critical or 8-11 minor = 3 points
        - 6+ critical or 12+ minor = 0 points

        Args:
            critical_errors: Count of critical errors
            minor_errors: Count of minor errors

        Returns:
            Dictionary with score, tier, and message
        """
        total_errors = critical_errors + minor_errors

        # Tier 1: Perfect (10 points)
        if total_errors == 0:
            return {
                'score': 10,
                'total_errors': 0,
                'critical_errors': 0,
                'minor_errors': 0,
                'tier': 'excellent',
                'message': 'No grammar or spelling errors detected'
            }

        # Tier 2: Very good (9 points) - 1-2 minor only
        if critical_errors == 0 and minor_errors <= 2:
            return {
                'score': 9,
                'total_errors': total_errors,
                'critical_errors': critical_errors,
                'minor_errors': minor_errors,
                'tier': 'very_good',
                'message': f'{minor_errors} minor error(s) - excellent overall'
            }

        # Tier 3: Good (7 points) - 1 critical OR 3-4 minor
        if (critical_errors == 1 and minor_errors <= 2) or \
           (critical_errors == 0 and 3 <= minor_errors <= 4):
            return {
                'score': 7,
                'total_errors': total_errors,
                'critical_errors': critical_errors,
                'minor_errors': minor_errors,
                'tier': 'good',
                'message': f'{critical_errors} critical, {minor_errors} minor error(s) - minor corrections needed'
            }

        # Tier 4: Acceptable (5 points) - 2-3 critical OR 5-7 minor
        if (2 <= critical_errors <= 3) or \
           (critical_errors <= 1 and 5 <= minor_errors <= 7):
            return {
                'score': 5,
                'total_errors': total_errors,
                'critical_errors': critical_errors,
                'minor_errors': minor_errors,
                'tier': 'acceptable',
                'message': f'{critical_errors} critical, {minor_errors} minor error(s) - requires proofreading'
            }

        # Tier 5: Needs work (3 points) - 4-5 critical OR 8-11 minor
        if (4 <= critical_errors <= 5) or \
           (critical_errors <= 3 and 8 <= minor_errors <= 11):
            return {
                'score': 3,
                'total_errors': total_errors,
                'critical_errors': critical_errors,
                'minor_errors': minor_errors,
                'tier': 'needs_work',
                'message': f'{critical_errors} critical, {minor_errors} minor error(s) - significant proofreading needed'
            }

        # Tier 6: Poor (0 points) - 6+ critical OR 12+ minor
        return {
            'score': 0,
            'total_errors': total_errors,
            'critical_errors': critical_errors,
            'minor_errors': minor_errors,
            'tier': 'poor',
            'message': f'{critical_errors} critical, {minor_errors} minor error(s) - thorough revision required'
        }


def create_scorer() -> GrammarScorer:
    """
    Factory function to create GrammarScorer instance.

    Returns:
        GrammarScorer instance
    """
    return GrammarScorer()
