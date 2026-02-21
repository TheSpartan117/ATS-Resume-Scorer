"""
P6.3: Word Repetition Penalty (-5 points max)

Penalizes poor vocabulary diversity when action verbs are overused.

Penalty structure:
- Each verb used 3+ times: -1 point
- Maximum penalty: -5 points

Research basis:
- Career coaches recommend max 2 uses of same verb per resume
- Excessive repetition indicates limited vocabulary
- ATS systems flag keyword stuffing when same term repeated 3+ times
- Hiring managers notice and negatively judge repetitive writing

This parameter enforces vocabulary diversity for professional writing quality.
"""

from typing import List, Dict, Any
from backend.services.repetition_detector import RepetitionDetector


class RepetitionPenaltyScorer:
    """Scores resume based on word repetition penalties."""

    def __init__(self):
        """
        Initialize scorer with RepetitionDetector.

        Uses threshold=3 (penalty kicks in at 3+ uses) and max_penalty=5.
        """
        # RepetitionDetector with threshold=3, max_penalty=5
        self.detector = RepetitionDetector(
            repetition_threshold=3,
            max_penalty=5
        )

    def score(self, bullets: List[str]) -> Dict[str, Any]:
        """
        Calculate repetition penalty for resume bullets.

        Args:
            bullets: List of resume bullet points

        Returns:
            Dictionary containing:
            - penalty: Penalty points (0 to -5)
            - repeated_verbs: List of verbs that triggered penalties
            - repetition_details: List of dicts with word, count, penalty
        """
        # Handle empty bullets
        if not bullets:
            return self._empty_result()

        # Use RepetitionDetector to analyze
        detection_result = self.detector.detect(bullets)

        # Extract penalty score (already negative)
        penalty = detection_result['penalty_score']

        # Extract repeated verbs list (just the words)
        repeated_verbs = [
            item['word']
            for item in detection_result['repeated_words']
        ]

        # Extract full repetition details
        repetition_details = detection_result['repeated_words']

        return {
            'penalty': penalty,
            'repeated_verbs': repeated_verbs,
            'repetition_details': repetition_details
        }

    def _empty_result(self) -> Dict[str, Any]:
        """Return result for empty bullet list."""
        return {
            'penalty': 0,
            'repeated_verbs': [],
            'repetition_details': []
        }


def score_repetition_penalty(bullets: List[str]) -> Dict[str, Any]:
    """
    Convenience function to score word repetition penalties.

    Args:
        bullets: List of resume bullet points

    Returns:
        Score result dictionary with penalty, repeated_verbs, repetition_details
    """
    scorer = RepetitionPenaltyScorer()
    return scorer.score(bullets)
