"""
ActionVerbScorer Service for P2.1 Parameter

Scores resume action verb quality and coverage with two sub-scores:
1. Coverage Score (7 points max): % of bullets with Tier 2+ verbs
2. Tier Score (8 points max): Average tier quality

Total: 15 points maximum

Level-Aware Thresholds:
- Beginner: 70% coverage, 1.5 avg tier
- Intermediary: 75% coverage, 2.0 avg tier
- Senior: 80% coverage, 2.5 avg tier

Scoring is tiered (non-linear) for both components.
"""

from typing import List, Dict, Any
from services.action_verb_classifier import ActionVerbClassifier, VerbTier
from config.scoring_thresholds import get_thresholds_for_level


class ActionVerbScorer:
    """
    Scores resume action verb quality and coverage.

    Uses ActionVerbClassifier to analyze bullet points and applies
    level-aware thresholds with tiered scoring.
    """

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
            - score: Total points (0-15)
            - coverage_score: Coverage sub-score (0-7)
            - tier_score: Tier quality sub-score (0-8)
            - level: Experience level used
            - total_bullets: Total number of bullets
            - bullets_with_tier2plus: Count of bullets with Tier 2+ verbs
            - coverage_percentage: % of bullets with Tier 2+ verbs
            - average_tier: Average tier across all bullets (0-4)
            - tier_distribution: Dict with counts per tier {0: n, 1: n, ...}
            - bullet_details: List of per-bullet analysis
        """
        # Handle empty bullets
        if not bullets:
            return self._empty_result(level)

        # Normalize level
        level = level.lower().strip()

        # Get level-specific thresholds from config
        thresholds = get_thresholds_for_level(level)

        # Classify all bullets
        bullet_details = []
        tier_sum = 0
        tier_distribution = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0}
        tier2plus_count = 0

        for bullet in bullets:
            # Clean whitespace
            bullet_clean = bullet.strip()

            # Skip empty bullets
            if not bullet_clean:
                continue

            # Classify
            tier_enum = self.classifier.classify_bullet(bullet_clean)
            tier_value = tier_enum.points

            # Track details
            bullet_details.append({
                'text': bullet_clean,
                'tier': tier_value,
                'tier_name': tier_enum.value
            })

            # Update counters
            tier_sum += tier_value
            tier_distribution[tier_value] += 1

            # Count Tier 2+ bullets
            if tier_value >= 2:
                tier2plus_count += 1

        # Calculate metrics
        total_bullets = len([b for b in bullets if b.strip()])
        coverage_percentage = (tier2plus_count / total_bullets * 100) if total_bullets > 0 else 0
        average_tier = (tier_sum / total_bullets) if total_bullets > 0 else 0.0

        # Calculate coverage sub-score (7 points max)
        coverage_score = self._calculate_coverage_score(coverage_percentage)

        # Calculate tier sub-score (8 points max)
        tier_score = self._calculate_tier_score(average_tier)

        # Total score
        total_score = coverage_score + tier_score

        return {
            'score': total_score,
            'coverage_score': coverage_score,
            'tier_score': tier_score,
            'level': level,
            'total_bullets': total_bullets,
            'bullets_with_tier2plus': tier2plus_count,
            'coverage_percentage': round(coverage_percentage, 1),
            'average_tier': round(average_tier, 1),
            'tier_distribution': tier_distribution,
            'bullet_details': bullet_details
        }

    def _calculate_coverage_score(self, coverage_pct: float) -> int:
        """
        Calculate coverage sub-score (7 points max).

        Tiered scoring (non-linear):
        - 95-100%: 7 points
        - 85-94%: 6 points
        - 70-84%: 4 points
        - 50-69%: 2 points
        - <50%: 0 points

        Args:
            coverage_pct: Coverage percentage (0-100)

        Returns:
            Score from 0-7
        """
        if coverage_pct >= 95:
            return 7
        elif coverage_pct >= 85:
            return 6
        elif coverage_pct >= 70:
            return 4
        elif coverage_pct >= 50:
            return 2
        else:
            return 0

    def _calculate_tier_score(self, avg_tier: float) -> int:
        """
        Calculate tier quality sub-score (8 points max).

        Tiered scoring (non-linear):
        - 3.5+: 8 points (mostly Tier 4)
        - 2.5-3.4: 6 points (mix of Tier 3-4)
        - 1.5-2.4: 4 points (mix of Tier 2-3)
        - 0.5-1.4: 2 points (mostly Tier 1)
        - <0.5: 0 points (mostly Tier 0)

        Args:
            avg_tier: Average tier (0-4)

        Returns:
            Score from 0-8
        """
        if avg_tier >= 3.5:
            return 8
        elif avg_tier >= 2.5:
            return 6
        elif avg_tier >= 1.5:
            return 4
        elif avg_tier >= 0.5:
            return 2
        else:
            return 0

    def _empty_result(self, level: str) -> Dict[str, Any]:
        """Return result for empty bullet list."""
        level = level.lower().strip()

        return {
            'score': 0,
            'coverage_score': 0,
            'tier_score': 0,
            'level': level,
            'total_bullets': 0,
            'bullets_with_tier2plus': 0,
            'coverage_percentage': 0.0,
            'average_tier': 0.0,
            'tier_distribution': {0: 0, 1: 0, 2: 0, 3: 0, 4: 0},
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
