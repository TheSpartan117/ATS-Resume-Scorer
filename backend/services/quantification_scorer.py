"""
P2.2 - Quantification Rate & Quality Scorer (10 pts)

Evaluates the quality and rate of quantified achievements in resume bullets.
Uses weighted scoring based on metric quality (HIGH/MEDIUM/LOW) and
level-aware thresholds.

Research basis:
- Quantified achievements are more credible (ResumeWorded, Jobscan)
- Quality matters: Business impact > scope > bare numbers
- Level-appropriate expectations: Senior requires higher quantification

Scoring Formula:
- Weighted rate = (sum of quality weights) / total_bullets * 100
- Quality weights: HIGH=1.0, MEDIUM=0.7, LOW=0.3

Level-aware thresholds:
- Beginner: 30% weighted rate
- Intermediary: 40% weighted rate
- Senior: 50% weighted rate

Tiered scoring:
- >= threshold: 10 points
- >= (threshold - 10%): 6 points
- >= (threshold - 20%): 3 points
- < (threshold - 20%): 0 points
"""

from typing import Dict, List, Any
from services.quantification_classifier import QuantificationClassifier, MetricQuality
from config.scoring_thresholds import get_thresholds_for_level


class QuantificationScorer:
    """
    Score resume bullets based on quantification rate and quality.

    Uses the QuantificationClassifier to assess metric quality and applies
    level-aware thresholds with tiered scoring.
    """

    def __init__(self):
        """Initialize the scorer with QuantificationClassifier."""
        self.classifier = QuantificationClassifier()

        # Maximum points for this parameter
        self.MAX_POINTS = 10

        # Level-specific thresholds (from config)
        self.thresholds = {
            'beginner': 30,      # 30% weighted rate
            'intermediary': 40,  # 40% weighted rate
            'senior': 50         # 50% weighted rate
        }

    def score(self, bullets: List[str], level: str) -> Dict[str, Any]:
        """
        Score bullets based on quantification rate and quality.

        Args:
            bullets: List of resume bullet points
            level: Experience level ('beginner', 'intermediary', 'senior')

        Returns:
            Dictionary containing:
            - score: Points awarded (0-10)
            - weighted_quantification_rate: Weighted % of quantified bullets
            - quantified_count: Number of bullets with metrics
            - total_bullets: Total number of bullets
            - high_count: Number of high-quality metrics
            - medium_count: Number of medium-quality metrics
            - low_count: Number of low-quality metrics
            - level: Experience level used
            - threshold: Threshold used for scoring
            - explanation: Human-readable explanation
        """
        # Normalize level
        level_lower = str(level).lower().strip()
        if level_lower not in self.thresholds:
            level_lower = 'intermediary'  # Default to intermediary

        # Get threshold for this level
        threshold = self.thresholds[level_lower]

        # Classify all bullets
        classification = self.classifier.classify_bullets(bullets)

        # Extract metrics
        weighted_rate = classification['weighted_quantification_rate']
        quantified_count = classification['quantified_count']
        total_bullets = classification['total_bullets']
        high_count = classification['high_count']
        medium_count = classification['medium_count']
        low_count = classification['low_count']

        # Calculate score based on tiered thresholds
        score = self._calculate_tiered_score(weighted_rate, threshold)

        # Generate explanation
        explanation = self._generate_explanation(
            score, weighted_rate, threshold, quantified_count, total_bullets,
            high_count, medium_count, low_count, level_lower
        )

        return {
            'score': score,
            'weighted_quantification_rate': round(weighted_rate, 1),
            'quantified_count': quantified_count,
            'total_bullets': total_bullets,
            'high_count': high_count,
            'medium_count': medium_count,
            'low_count': low_count,
            'level': level_lower,
            'threshold': threshold,
            'explanation': explanation
        }

    def _calculate_tiered_score(self, weighted_rate: float, threshold: float) -> int:
        """
        Calculate score based on tiered thresholds.

        Tiers:
        - >= threshold: 10 points (excellent)
        - >= (threshold - 10%): 6 points (good)
        - >= (threshold - 20%): 3 points (acceptable)
        - < (threshold - 20%): 0 points (poor)

        Args:
            weighted_rate: Weighted quantification rate (%)
            threshold: Level-specific threshold (%)

        Returns:
            Points awarded (0, 3, 6, or 10)
        """
        if weighted_rate >= threshold:
            return 10
        elif weighted_rate >= (threshold - 10):
            return 6
        elif weighted_rate >= (threshold - 20):
            return 3
        else:
            return 0

    def _generate_explanation(
        self,
        score: int,
        weighted_rate: float,
        threshold: float,
        quantified_count: int,
        total_bullets: int,
        high_count: int,
        medium_count: int,
        low_count: int,
        level: str
    ) -> str:
        """
        Generate human-readable explanation of the score.

        Args:
            score: Points awarded
            weighted_rate: Weighted quantification rate (%)
            threshold: Level-specific threshold (%)
            quantified_count: Number of quantified bullets
            total_bullets: Total bullets
            high_count: High-quality metrics count
            medium_count: Medium-quality metrics count
            low_count: Low-quality metrics count
            level: Experience level

        Returns:
            Explanation string
        """
        # Build quality breakdown
        quality_parts = []
        if high_count > 0:
            quality_parts.append(f"{high_count} high-value")
        if medium_count > 0:
            quality_parts.append(f"{medium_count} medium-value")
        if low_count > 0:
            quality_parts.append(f"{low_count} low-value")

        quality_breakdown = ", ".join(quality_parts) if quality_parts else "no metrics"

        # Generate explanation based on score
        if score == 10:
            return (
                f"Excellent quantification! {weighted_rate:.1f}% weighted rate "
                f"(>= {threshold}% threshold for {level}). "
                f"Found {quantified_count}/{total_bullets} quantified bullets: {quality_breakdown}."
            )
        elif score == 6:
            return (
                f"Good quantification. {weighted_rate:.1f}% weighted rate "
                f"(>= {threshold-10}% but < {threshold}%). "
                f"Found {quantified_count}/{total_bullets} quantified bullets: {quality_breakdown}. "
                f"Add more business-impact metrics to reach {threshold}% for {level} level."
            )
        elif score == 3:
            return (
                f"Acceptable quantification. {weighted_rate:.1f}% weighted rate "
                f"(>= {threshold-20}% but < {threshold-10}%). "
                f"Found {quantified_count}/{total_bullets} quantified bullets: {quality_breakdown}. "
                f"Need more quantified achievements (target: {threshold}% for {level})."
            )
        else:
            return (
                f"Insufficient quantification. {weighted_rate:.1f}% weighted rate "
                f"(< {threshold-20}%). "
                f"Found only {quantified_count}/{total_bullets} quantified bullets: {quality_breakdown}. "
                f"Add metrics like percentages, dollar amounts, scale indicators. "
                f"Target: {threshold}% for {level} level."
            )

    def get_recommendations(self, result: Dict[str, Any]) -> List[str]:
        """
        Generate actionable recommendations based on scoring result.

        Args:
            result: Result dictionary from score() method

        Returns:
            List of recommendation strings
        """
        recommendations = []

        score = result['score']
        weighted_rate = result['weighted_quantification_rate']
        threshold = result['threshold']
        high_count = result['high_count']
        medium_count = result['medium_count']
        low_count = result['low_count']
        quantified_count = result['quantified_count']
        total_bullets = result['total_bullets']

        # If perfect score, give maintenance advice
        if score == 10:
            recommendations.append(
                "Excellent quantification! Maintain this level of specificity in all bullets."
            )
            return recommendations

        # Calculate how many more bullets need quantification
        bullets_needed = int(
            ((threshold - weighted_rate) / 100 * total_bullets) + 1
        )

        # General quantification advice
        if quantified_count < total_bullets * 0.5:
            recommendations.append(
                f"Add metrics to {bullets_needed}+ more bullets. "
                f"Target: {threshold}% quantification for your level."
            )

        # Quality-specific advice
        if high_count == 0:
            recommendations.append(
                "Add high-value metrics: percentages (↑50%), dollar amounts ($500K), "
                "multipliers (3x faster), before/after comparisons."
            )

        if medium_count == 0 and high_count < 3:
            recommendations.append(
                "Include scope indicators: team sizes (led 10 engineers), "
                "durations (in 6 months), user scale (500K+ users)."
            )

        if low_count > high_count + medium_count:
            recommendations.append(
                "Improve metric quality. Bare numbers like 'fixed 20 bugs' are weak. "
                "Add business impact: 'reduced bug count by 40% (from 50 to 30)'."
            )

        # Level-specific advice
        level = result['level']
        if level == 'senior' and high_count < 2:
            recommendations.append(
                "Senior level requires strong business impact. Add 2+ high-value metrics "
                "showing revenue, cost savings, efficiency gains, or scale improvements."
            )

        if level == 'intermediary' and quantified_count < total_bullets * 0.5:
            recommendations.append(
                "Intermediary level: At least 50% of bullets should be quantified. "
                "Show project scope, team sizes, and measurable outcomes."
            )

        return recommendations
