"""
P2.1: Action Verb Quality & Coverage (15 points)

Evaluates resume bullets based on incremental tier-based scoring.

Each bullet point's action verb contributes points based on tier:
- Tier 4 (Strategic): 1.0 points per bullet
- Tier 3 (Leadership): 0.8 points per bullet
- Tier 2 (Achievement): 0.6 points per bullet
- Tier 1 (Operational): 0.4 points per bullet
- Tier 0 (Weak/None): 0 points

Total score = sum of all bullet points' contributions, capped at 15 points.

Examples:
- 10 bullets with Tier 4 verbs = 10 * 1.0 = 10 points
- 20 bullets with Tier 2 verbs = 20 * 0.6 = 12 points
- 5 Tier 4 + 10 Tier 3 + 10 Tier 1 = 5 + 8 + 4 = 15 points (capped)
"""

from typing import List, Dict, Any
from backend.services.action_verb_classifier import ActionVerbClassifier, VerbTier
from backend.config.scoring_thresholds import get_thresholds_for_level


# Tier point values for incremental scoring
TIER_POINTS = {
    4: 1.0,  # Strategic/Transformational
    3: 0.8,  # Leadership
    2: 0.6,  # Achievement/Execution
    1: 0.4,  # Operational/Support
    0: 0.0   # Weak/None
}


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

        # Check thresholds (for informational purposes)
        coverage_met = coverage_percentage >= coverage_threshold
        tier_met = average_tier >= tier_threshold

        # Calculate score using incremental tier-based scoring
        # Each bullet contributes points based on its tier
        score = 0.0
        for bullet_detail in bullet_details:
            tier_value = bullet_detail['tier']
            score += TIER_POINTS.get(tier_value, 0.0)

        # Cap at 15 points maximum
        score = min(score, 15.0)

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
