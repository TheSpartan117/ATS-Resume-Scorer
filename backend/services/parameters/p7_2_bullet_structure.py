"""
P7.2: Bullet Point Structure (3 points)

Evaluates bullet point structure quality based on two key metrics:
1. Length: 15-25 words optimal (80%+ bullets in range)
2. Action Verb Start: 80%+ bullets start with strong verb (Tier 1+)

Scoring:
- Both checks pass: 3 points
- One check passes: 2 points
- Neither passes: 0 points

Research Basis:
- Harvard Career Services: 1-2 lines (15-25 words) per bullet
- Indeed Resume Guide: Start with strong action verbs
- Jobscan: Concise bullets (1-2 lines) perform better in ATS
"""

from typing import List, Dict, Any
import re
from backend.services.action_verb_classifier import ActionVerbClassifier, VerbTier


class BulletStructureScorer:
    """Scores resume bullet point structure quality."""

    def __init__(self):
        """Initialize scorer with action verb classifier."""
        self.classifier = ActionVerbClassifier()
        self.max_score = 3
        self.length_min = 15
        self.length_max = 25
        self.threshold = 80.0  # 80% threshold for both checks

    def score(self, bullets: List[str]) -> Dict[str, Any]:
        """
        Score bullet point structure quality.

        Args:
            bullets: List of resume bullet points

        Returns:
            Dictionary containing:
            - score: Total points (0, 2, or 3)
            - max_score: Maximum possible score (3)
            - total_bullets: Total number of bullets
            - length_check: {
                'passed': bool,
                'percentage': float,
                'in_range_count': int,
                'threshold': float
              }
            - verb_check: {
                'passed': bool,
                'percentage': float,
                'strong_verb_count': int,
                'threshold': float
              }
            - bullet_details: List of per-bullet analysis
        """
        # Handle empty bullets
        if not bullets:
            return self._empty_result()

        # Analyze each bullet
        bullet_details = []
        in_range_count = 0
        strong_verb_count = 0

        for bullet in bullets:
            # Clean whitespace
            bullet_clean = bullet.strip()

            # Count words (split by whitespace, filter out empty strings)
            words = re.findall(r'\b\w+\b', bullet_clean)
            word_count = len(words)

            # Check if in optimal length range
            in_length_range = self.length_min <= word_count <= self.length_max
            if in_length_range:
                in_range_count += 1

            # Check if starts with strong action verb
            verb_tier = self.classifier.classify_bullet(bullet_clean)
            starts_with_strong_verb = verb_tier.points >= 1  # Tier 1+ is strong
            if starts_with_strong_verb:
                strong_verb_count += 1

            # Store details
            bullet_details.append({
                'text': bullet_clean,
                'word_count': word_count,
                'in_length_range': in_length_range,
                'starts_with_strong_verb': starts_with_strong_verb,
                'verb_tier': verb_tier.points
            })

        # Calculate percentages
        total_bullets = len(bullets)
        length_percentage = (in_range_count / total_bullets) * 100
        verb_percentage = (strong_verb_count / total_bullets) * 100

        # Check thresholds
        length_check_passed = length_percentage >= self.threshold
        verb_check_passed = verb_percentage >= self.threshold

        # Calculate score
        if length_check_passed and verb_check_passed:
            score = 3
        elif length_check_passed or verb_check_passed:
            score = 2
        else:
            score = 0

        return {
            'score': score,
            'max_score': self.max_score,
            'total_bullets': total_bullets,
            'length_check': {
                'passed': length_check_passed,
                'percentage': round(length_percentage, 2),
                'in_range_count': in_range_count,
                'threshold': self.threshold
            },
            'verb_check': {
                'passed': verb_check_passed,
                'percentage': round(verb_percentage, 2),
                'strong_verb_count': strong_verb_count,
                'threshold': self.threshold
            },
            'bullet_details': bullet_details
        }

    def _empty_result(self) -> Dict[str, Any]:
        """Return result for empty bullet list."""
        return {
            'score': 0,
            'max_score': self.max_score,
            'total_bullets': 0,
            'length_check': {
                'passed': False,
                'percentage': 0.0,
                'in_range_count': 0,
                'threshold': self.threshold
            },
            'verb_check': {
                'passed': False,
                'percentage': 0.0,
                'strong_verb_count': 0,
                'threshold': self.threshold
            },
            'bullet_details': []
        }


def score_bullet_structure(bullets: List[str]) -> Dict[str, Any]:
    """
    Convenience function to score bullet point structure.

    Args:
        bullets: List of resume bullet points

    Returns:
        Score result dictionary

    Example:
        >>> bullets = [
        ...     "Developed scalable microservices architecture serving millions of users",
        ...     "Led cross-functional team of 12 engineers to deliver critical features",
        ...     "Implemented automated testing framework reducing deployment time by 60%"
        ... ]
        >>> result = score_bullet_structure(bullets)
        >>> print(f"Score: {result['score']}/3")
    """
    scorer = BulletStructureScorer()
    return scorer.score(bullets)
