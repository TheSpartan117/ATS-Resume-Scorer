"""
P2.1: Action Verb Quality & Coverage (15 points)

Evaluates resume bullets based on:
1. Coverage % (what % of bullets have action verbs)
2. Average tier quality (Tier 0-4)

Level-Specific Thresholds:
- Beginner: 70% coverage, 1.5+ avg tier
- Intermediary: 80% coverage, 2.0+ avg tier
- Senior: 90% coverage, 2.5+ avg tier

Scoring:
- Both thresholds met: 15 points
- One threshold met: 8 points
- Neither met: 0 points
"""

from typing import List, Dict, Any
from backend.services.action_verb_classifier import ActionVerbClassifier, VerbTier
from backend.config.scoring_thresholds import get_thresholds_for_level


class ActionVerbScorer:
    """Scores resume action verb quality and coverage."""

    def __init__(self):
        """Initialize scorer with action verb classifier."""
        self.classifier = ActionVerbClassifier()

    def score(self, bullets: List[str], level: str) -> Dict[str, Any]:
        """
        Score action verb quality and coverage for a resume.

        Args:
            bullets: List of resume bullet points
            level: Experience level ('beginner', 'intermediary', 'senior')

        Returns:
            Dictionary containing:
            - score: Total points (0, 8, or 15)
            - level: Experience level used
            - total_bullets: Total number of bullets
            - bullets_with_verbs: Count of bullets with recognized verbs (tier > 0)
            - coverage_percentage: % of bullets with action verbs
            - average_tier: Average tier across all bullets
            - coverage_threshold: Required coverage % for this level
            - tier_threshold: Required avg tier for this level
            - coverage_met: Whether coverage threshold was met
            - tier_met: Whether tier threshold was met
            - bullet_details: List of per-bullet analysis
        """
        # Handle empty bullets
        if not bullets:
            return self._empty_result(level)

        # Get level-specific thresholds
        thresholds = get_thresholds_for_level(level)
        coverage_threshold = thresholds['action_verb_coverage_min']
        tier_threshold = thresholds['action_verb_tier_avg_min']

        # Classify all bullets
        bullet_details = []
        tier_sum = 0
        verbs_found = 0

        for bullet in bullets:
            # Clean whitespace
            bullet_clean = bullet.strip()

            # Classify
            tier_enum = self.classifier.classify_bullet(bullet_clean)
            tier_value = tier_enum.points

            # Track details
            has_verb = tier_value > 0
            bullet_details.append({
                'text': bullet_clean,
                'tier': tier_value,
                'tier_name': tier_enum.value,
                'has_verb': has_verb
            })

            tier_sum += tier_value
            if has_verb:
                verbs_found += 1

        # Calculate metrics
        total_bullets = len(bullets)
        coverage_percentage = (verbs_found / total_bullets) * 100
        average_tier = tier_sum / total_bullets

        # Check thresholds
        coverage_met = coverage_percentage >= coverage_threshold
        tier_met = average_tier >= tier_threshold

        # Calculate score
        if coverage_met and tier_met:
            score = 15
        elif coverage_met or tier_met:
            score = 8
        else:
            score = 0

        return {
            'score': score,
            'level': level.lower().strip(),
            'total_bullets': total_bullets,
            'bullets_with_verbs': verbs_found,
            'coverage_percentage': round(coverage_percentage, 2),
            'average_tier': round(average_tier, 2),
            'coverage_threshold': coverage_threshold,
            'tier_threshold': tier_threshold,
            'coverage_met': coverage_met,
            'tier_met': tier_met,
            'bullet_details': bullet_details
        }

    def _empty_result(self, level: str) -> Dict[str, Any]:
        """Return result for empty bullet list."""
        thresholds = get_thresholds_for_level(level)

        return {
            'score': 0,
            'level': level.lower().strip(),
            'total_bullets': 0,
            'bullets_with_verbs': 0,
            'coverage_percentage': 0.0,
            'average_tier': 0.0,
            'coverage_threshold': thresholds['action_verb_coverage_min'],
            'tier_threshold': thresholds['action_verb_tier_avg_min'],
            'coverage_met': False,
            'tier_met': False,
            'bullet_details': []
        }


def score_action_verbs(bullets: List[str], level: str) -> Dict[str, Any]:
    """
    Convenience function to score action verbs.

    Args:
        bullets: List of resume bullet points
        level: Experience level ('beginner', 'intermediary', 'senior')

    Returns:
        Score result dictionary
    """
    scorer = ActionVerbScorer()
    return scorer.score(bullets, level)
