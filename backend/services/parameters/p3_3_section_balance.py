"""
P3.3: Section Balance (5 points)

Detects keyword stuffing and poor content distribution.
Uses SectionBalanceAnalyzer to identify imbalances.

Converts penalty to positive score:
- 0 issues = 5 points (EXCELLENT)
- penalty -1 to -2 = 3 points (GOOD)
- penalty -3 to -4 = 1 point (FAIR)
- penalty -5 = 0 points (POOR)

Detects:
- Skills too large (>25%) = keyword stuffing
- Experience too small (<40%) = insufficient detail
- Summary too large (>15%) = too verbose
"""

from typing import Dict, Any
from services.section_balance_analyzer import SectionBalanceAnalyzer


class SectionBalanceScorer:
    """Scores resume section balance to detect keyword stuffing and imbalances."""

    def __init__(self):
        """Initialize scorer with section balance analyzer."""
        self.analyzer = SectionBalanceAnalyzer()

    def score(self, sections: Dict) -> Dict[str, Any]:
        """
        Score section balance of a resume.

        Args:
            sections: Dict of section_name -> {'content': str, 'word_count': int}

        Returns:
            Dictionary containing:
            - score: Total points (0, 1, 3, or 5)
            - rating: Quality rating (EXCELLENT, GOOD, FAIR, POOR)
            - penalty_score: Raw penalty from analyzer (-5 to 0)
            - issues: List of detected imbalances
            - section_percentages: Dict of section -> percentage
            - total_words: Total word count across all sections
            - max_penalty: Maximum possible penalty (-5)
        """
        # Handle empty sections
        if not sections:
            return self._empty_result()

        # Use analyzer to get penalty assessment
        analysis = self.analyzer.analyze(sections)

        # Extract penalty score
        penalty_score = analysis['penalty_score']

        # Convert penalty to positive score
        score = self._penalty_to_score(penalty_score)

        # Determine rating
        rating = self._get_rating(penalty_score)

        return {
            'score': score,
            'rating': rating,
            'penalty_score': penalty_score,
            'issues': analysis['issues'],
            'section_percentages': analysis['section_percentages'],
            'total_words': analysis['total_words'],
            'max_penalty': analysis['max_penalty']
        }

    def _penalty_to_score(self, penalty: int) -> int:
        """
        Convert penalty score to positive points.

        Args:
            penalty: Penalty score from analyzer (-5 to 0)

        Returns:
            Positive score (0 to 5 points)
        """
        if penalty == 0:
            return 5  # EXCELLENT
        elif penalty >= -2:
            return 3  # GOOD
        elif penalty >= -4:
            return 1  # FAIR
        else:  # penalty == -5
            return 0  # POOR

    def _get_rating(self, penalty: int) -> str:
        """
        Get quality rating based on penalty.

        Args:
            penalty: Penalty score from analyzer (-5 to 0)

        Returns:
            Rating string (EXCELLENT, GOOD, FAIR, POOR)
        """
        if penalty == 0:
            return 'EXCELLENT'
        elif penalty >= -2:
            return 'GOOD'
        elif penalty >= -4:
            return 'FAIR'
        else:  # penalty == -5
            return 'POOR'

    def _empty_result(self) -> Dict[str, Any]:
        """Return result for empty sections."""
        return {
            'score': 0,
            'rating': 'POOR',
            'penalty_score': 0,
            'issues': [],
            'section_percentages': {},
            'total_words': 0,
            'max_penalty': -5
        }


def score_section_balance(sections: Dict) -> Dict[str, Any]:
    """
    Convenience function to score section balance.

    Args:
        sections: Dict of section_name -> {'content': str, 'word_count': int}

    Returns:
        Score result dictionary
    """
    scorer = SectionBalanceScorer()
    return scorer.score(sections)
