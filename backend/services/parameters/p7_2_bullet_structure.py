"""
P7.2: Bullet Point Structure (3 points)

Evaluates bullet point structure quality based on two key metrics:
1. Length: 10-20 words optimal (50%+ bullets in range)
2. Action Verb Start: 25%+ bullets start with strong verb (Tier 2+)

Scoring (proportional, minimum 0.5 points):
- Both checks pass (50%+ length, 25%+ verbs): 3 points
- One check passes: 1.5 points
- Close to passing (within 10% of threshold): 1 point
- Below threshold but not zero: 0.5 points minimum

Note on lenient thresholds:
- Parser sometimes splits multi-line bullets into separate entries
- Some "bullets" are actually headers or continuation lines
- 50%/25% thresholds account for parser artifacts while still rewarding good structure
- Adjusted range to 10-20 words (was 15-25) to be more realistic
- Minimum score of 0.5 recognizes that any bullets are better than none

Research Basis:
- Harvard Career Services: 1-2 lines (10-20 words) per bullet
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
        self.length_min = 10
        self.length_max = 20
        self.length_threshold = 50.0  # 50% of bullets should be in good length range (lowered from 60%)
        self.verb_threshold = 25.0  # 25% of bullets should start with strong verbs (lowered from 30%)

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
            starts_with_strong_verb = verb_tier.points >= 2  # Tier 2+ is strong (was Tier 1+)
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
        length_check_passed = length_percentage >= self.length_threshold
        verb_check_passed = verb_percentage >= self.verb_threshold

        # Calculate score with proportional partial credit
        score = 0

        # Length check scoring
        if length_check_passed:
            score += 1.5
        elif length_percentage >= self.length_threshold * 0.8:  # Within 80% of threshold
            score += 1.0  # Close to passing
        elif length_percentage > 0:
            score += 0.5  # Has some bullets in range

        # Verb check scoring
        if verb_check_passed:
            score += 1.5
        elif verb_percentage >= self.verb_threshold * 0.6:  # Within 60% of threshold
            score += 0.5  # Close to passing
        elif verb_percentage > 0:
            score += 0.25  # Has some strong verbs

        return {
            'score': score,
            'max_score': self.max_score,
            'total_bullets': total_bullets,
            'length_check': {
                'passed': length_check_passed,
                'percentage': round(length_percentage, 2),
                'in_range_count': in_range_count,
                'threshold': self.length_threshold,
                'optimal_range': f'{self.length_min}-{self.length_max} words'
            },
            'verb_check': {
                'passed': verb_check_passed,
                'percentage': round(verb_percentage, 2),
                'strong_verb_count': strong_verb_count,
                'threshold': self.verb_threshold,
                'requirement': 'Tier 2+ verbs'
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
                'threshold': self.length_threshold,
                'optimal_range': f'{self.length_min}-{self.length_max} words'
            },
            'verb_check': {
                'passed': False,
                'percentage': 0.0,
                'strong_verb_count': 0,
                'threshold': self.verb_threshold,
                'requirement': 'Tier 2+ verbs'
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
