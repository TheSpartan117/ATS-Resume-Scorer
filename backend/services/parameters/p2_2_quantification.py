"""
P2.2: Quantification Rate & Quality (10 points)

Evaluates the use of quantifiable metrics in resume bullets using weighted scoring.
Uses QuantificationClassifier to assess metric quality (HIGH/MEDIUM/LOW).

Scoring Formula:
- Weighted Rate = (HIGH_count * 1.0 + MEDIUM_count * 0.7 + LOW_count * 0.3) / total_bullets * 100%
- Points awarded based on tiered thresholds (applies to all experience levels)

Tiered Scoring Thresholds:
- ≥80% weighted = 10 pts (excellent - mostly HIGH-value metrics)
- ≥60% weighted = 8 pts (very good - strong mix of HIGH/MEDIUM)
- ≥40% weighted = 6 pts (good - decent quantification with quality)
- ≥25% weighted = 4 pts (fair - some quantification present)
- ≥10% weighted = 2 pts (weak - minimal quantification)
- <10% weighted = 0-2 pts (very weak - linear scaling)

Interpolation: Linear scoring between tier boundaries for smooth gradation

Research Basis:
- ResumeWorded: 70%+ quantification for senior roles
- Jobscan: Metrics improve ATS scores by 40%
- LinkedIn: Quantified bullets get 3x more engagement
"""

from typing import List, Dict, Any
from backend.services.quantification_classifier import QuantificationClassifier
from backend.config.scoring_thresholds import get_thresholds_for_level


class QuantificationScorer:
    """
    Score resumes based on quantification rate and quality.

    Uses weighted scoring where:
    - HIGH quality metrics (%, $, multipliers) = 1.0 weight
    - MEDIUM quality metrics (team sizes, scale) = 0.7 weight
    - LOW quality metrics (bare numbers) = 0.3 weight
    """

    def __init__(self):
        self.classifier = QuantificationClassifier()
        self.max_score = 10  # Registry max is 10 pts

    def score(self, bullets: List[str], level: str) -> Dict[str, Any]:
        """
        Score bullets based on quantification rate and quality.

        Args:
            bullets: List of resume bullet points
            level: Experience level ('beginner', 'intermediary', 'senior')

        Returns:
            {
                'score': float (0-10),
                'max_score': int (10),
                'weighted_quantification_rate': float (0-100),
                'quantified_count': int,
                'high_count': int,
                'medium_count': int,
                'low_count': int,
                'total_bullets': int,
                'feedback': str,
                'level': str
            }
        """
        # Handle edge case: empty bullets
        if not bullets:
            return {
                'score': 0,
                'max_score': self.max_score,
                'weighted_quantification_rate': 0.0,
                'quantified_count': 0,
                'high_count': 0,
                'medium_count': 0,
                'low_count': 0,
                'total_bullets': 0,
                'feedback': 'No bullets provided to analyze.',
                'level': level
            }

        # Get classification results
        classification = self.classifier.classify_bullets(bullets)

        weighted_rate = classification['weighted_quantification_rate']
        quantified_count = classification['quantified_count']
        high_count = classification['high_count']
        medium_count = classification['medium_count']
        low_count = classification['low_count']
        total_bullets = classification['total_bullets']

        # Get level-specific thresholds
        thresholds = get_thresholds_for_level(level)

        # Determine score based on level
        score = self._calculate_score(weighted_rate, level, thresholds)

        # Generate feedback
        feedback = self._generate_feedback(
            weighted_rate,
            quantified_count,
            high_count,
            medium_count,
            low_count,
            total_bullets,
            score,
            level,
            thresholds
        )

        return {
            'score': score,
            'max_score': self.max_score,
            'weighted_quantification_rate': round(weighted_rate, 2),
            'quantified_count': quantified_count,
            'high_count': high_count,
            'medium_count': medium_count,
            'low_count': low_count,
            'total_bullets': total_bullets,
            'feedback': feedback,
            'level': level
        }

    def _calculate_score(self, weighted_rate: float, level: str, thresholds: Dict) -> float:
        """
        Calculate score based on weighted quantification rate using tiered thresholds.

        Args:
            weighted_rate: Weighted quantification rate (0-100)
            level: Experience level
            thresholds: Level-specific threshold configuration

        Returns:
            Score from 0-10 (tiered scoring)
        """
        # Tiered scoring based on weighted quantification rate
        # Rewards quality quantification more generously than linear scaling

        if weighted_rate >= 80.0:
            # Excellent - mostly HIGH-value metrics
            return 10.0
        elif weighted_rate >= 60.0:
            # Very good - strong mix of HIGH/MEDIUM metrics
            # Linear interpolation between 60% (8pts) and 80% (10pts)
            return 8.0 + ((weighted_rate - 60.0) / 20.0) * 2.0
        elif weighted_rate >= 40.0:
            # Good - decent quantification with some quality
            # Linear interpolation between 40% (6pts) and 60% (8pts)
            return 6.0 + ((weighted_rate - 40.0) / 20.0) * 2.0
        elif weighted_rate >= 25.0:
            # Fair - some quantification present
            # Linear interpolation between 25% (4pts) and 40% (6pts)
            return 4.0 + ((weighted_rate - 25.0) / 15.0) * 2.0
        elif weighted_rate >= 10.0:
            # Weak - minimal quantification
            # Linear interpolation between 10% (2pts) and 25% (4pts)
            return 2.0 + ((weighted_rate - 10.0) / 15.0) * 2.0
        else:
            # Very weak - almost no quantification
            # Linear scaling from 0% (0pts) to 10% (2pts)
            return (weighted_rate / 10.0) * 2.0

    def _generate_feedback(
        self,
        weighted_rate: float,
        quantified_count: int,
        high_count: int,
        medium_count: int,
        low_count: int,
        total_bullets: int,
        score: int,
        level: str,
        thresholds: Dict
    ) -> str:
        """Generate detailed feedback about quantification quality."""

        # Get level-specific thresholds for feedback
        if level.lower() == 'beginner':
            excellent_threshold = 30.0
            good_threshold = 20.0
        elif level.lower() == 'intermediary':
            excellent_threshold = 50.0
            good_threshold = 35.0
        elif level.lower() == 'senior':
            excellent_threshold = 60.0
            good_threshold = 45.0
        else:
            excellent_threshold = 50.0
            good_threshold = 35.0

        # Build feedback message
        feedback_parts = []

        # Overall performance
        feedback_parts.append(
            f"Quantification Score: {score}/{self.max_score} points. "
            f"Weighted quantification rate: {weighted_rate:.1f}% "
            f"({quantified_count}/{total_bullets} bullets quantified)."
        )

        # Quality breakdown
        if quantified_count > 0:
            feedback_parts.append(
                f"\nQuality breakdown: {high_count} HIGH-value (%, $, multipliers), "
                f"{medium_count} MEDIUM-value (team sizes, scale), "
                f"{low_count} LOW-value (bare numbers)."
            )

        # Performance assessment (tiered scoring)
        if weighted_rate >= 80.0:
            feedback_parts.append(
                f"\nExcellent quantification! Your {weighted_rate:.1f}% weighted rate shows "
                f"strong use of HIGH-value metrics (%, $, multipliers)."
            )
        elif weighted_rate >= 60.0:
            feedback_parts.append(
                f"\nVery good quantification at {weighted_rate:.1f}%. "
                f"Strong mix of quality metrics. Aim for 80%+ to reach full points."
            )
        elif weighted_rate >= 40.0:
            feedback_parts.append(
                f"\nGood quantification at {weighted_rate:.1f}%. "
                f"Decent use of metrics. Add more HIGH-value metrics to improve."
            )
        elif weighted_rate >= 25.0:
            feedback_parts.append(
                f"\nFair quantification at {weighted_rate:.1f}%. "
                f"Some metrics present, but need more quality quantification."
            )
        else:
            feedback_parts.append(
                f"\nQuantification needs improvement. Current rate: {weighted_rate:.1f}%. "
                f"Target: Add quantifiable metrics with context (%, $, scale indicators)."
            )

        # Specific improvement suggestions
        if score < self.max_score:
            suggestions = []

            if high_count == 0:
                suggestions.append(
                    "Add HIGH-value metrics: percentages (increased by X%), "
                    "dollar amounts ($XXK saved), or multipliers (3x faster)"
                )

            if quantified_count < total_bullets * 0.5:
                suggestions.append(
                    f"Quantify more bullets. Only {quantified_count}/{total_bullets} "
                    "bullets currently have metrics"
                )

            if low_count > high_count + medium_count:
                suggestions.append(
                    "Upgrade LOW-value metrics (bare numbers) to HIGH-value "
                    "by adding context (e.g., '5 projects' → 'delivered 5 projects, "
                    "reducing time-to-market by 30%')"
                )

            if suggestions:
                feedback_parts.append("\n\nImprovement suggestions:")
                for i, suggestion in enumerate(suggestions, 1):
                    feedback_parts.append(f"\n{i}. {suggestion}")

        return "".join(feedback_parts)


# Convenience function for direct usage
def score_quantification(bullets: List[str], level: str) -> Dict[str, Any]:
    """
    Score quantification rate and quality for resume bullets.

    Args:
        bullets: List of resume bullet points
        level: Experience level ('beginner', 'intermediary', 'senior')

    Returns:
        Scoring result dictionary

    Example:
        >>> bullets = [
        ...     "Increased revenue by 45%",
        ...     "Led team of 8 engineers",
        ...     "Completed 3 projects"
        ... ]
        >>> result = score_quantification(bullets, 'senior')
        >>> print(f"Score: {result['score']}/10")
    """
    scorer = QuantificationScorer()
    return scorer.score(bullets, level)
