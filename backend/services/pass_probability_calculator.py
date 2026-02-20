"""
Pass Probability Calculator - Calculates overall ATS pass probability.

This module implements Phase 3.2 of the Unified Implementation Plan:
- Calculates overall pass probability (0-100%)
- Breaks down by platform (Taleo, Workday, Greenhouse)
- Determines confidence level (High, Moderate, Low)
"""

from typing import Dict, List, Optional
from enum import Enum


class ConfidenceLevel(str, Enum):
    """Confidence levels for pass probability"""
    HIGH = "high"
    MODERATE = "moderate"
    LOW = "low"


class ATSPlatform(str, Enum):
    """Major ATS platforms"""
    TALEO = "Taleo"
    WORKDAY = "Workday"
    GREENHOUSE = "Greenhouse"
    ICIMS = "iCIMS"
    JOBVITE = "Jobvite"


class PassProbabilityCalculator:
    """
    Calculates ATS pass probability based on resume score and analysis.

    Calculation methodology:
    1. Base probability from overall score
    2. Adjustments for critical issues (auto-reject flags)
    3. Platform-specific calculations
    4. Confidence level based on data quality
    """

    # Platform difficulty levels (how strict each platform is)
    PLATFORM_DIFFICULTY = {
        ATSPlatform.TALEO: 0.85,  # Strictest - multiplier for difficulty
        ATSPlatform.WORKDAY: 0.90,  # Moderate
        ATSPlatform.GREENHOUSE: 0.95,  # Most lenient
        ATSPlatform.ICIMS: 0.88,
        ATSPlatform.JOBVITE: 0.92,
    }

    # Market share for weighted average
    PLATFORM_MARKET_SHARE = {
        ATSPlatform.TALEO: 0.30,  # 30% market share
        ATSPlatform.WORKDAY: 0.25,  # 25%
        ATSPlatform.GREENHOUSE: 0.20,  # 20%
        ATSPlatform.ICIMS: 0.15,  # 15%
        ATSPlatform.JOBVITE: 0.10,  # 10%
    }

    def __init__(self):
        """Initialize the pass probability calculator"""
        pass

    def _calculate_base_probability(self, overall_score: float) -> float:
        """
        Calculate base pass probability from overall score.

        Mapping:
        - 90+: 95% pass probability
        - 80-89: 85% pass probability
        - 70-79: 70% pass probability
        - 60-69: 50% pass probability
        - 50-59: 30% pass probability
        - <50: 15% pass probability

        Args:
            overall_score: Overall resume score (0-100)

        Returns:
            Base pass probability (0-100)
        """
        if overall_score >= 90:
            return 95.0
        elif overall_score >= 80:
            return 85.0
        elif overall_score >= 70:
            return 70.0
        elif overall_score >= 60:
            return 50.0
        elif overall_score >= 50:
            return 30.0
        else:
            return 15.0

    def _apply_critical_adjustments(
        self,
        base_probability: float,
        auto_reject: bool,
        critical_issues: List[str]
    ) -> float:
        """
        Apply adjustments for critical issues.

        Args:
            base_probability: Base probability
            auto_reject: Whether resume has auto-reject flags
            critical_issues: List of critical issues

        Returns:
            Adjusted probability
        """
        adjusted = base_probability

        # Auto-reject flag severely reduces probability
        if auto_reject:
            adjusted *= 0.3  # Reduce by 70%

        # Each critical issue reduces probability
        for _ in critical_issues:
            adjusted *= 0.95  # Reduce by 5% per critical issue

        return max(0, min(100, adjusted))

    def _calculate_platform_probability(
        self,
        base_probability: float,
        platform: ATSPlatform,
        format_score: float
    ) -> float:
        """
        Calculate pass probability for a specific ATS platform.

        Args:
            base_probability: Base pass probability
            platform: ATS platform
            format_score: Formatting score (0-100)

        Returns:
            Platform-specific pass probability
        """
        difficulty = self.PLATFORM_DIFFICULTY[platform]

        # Format score is more important for stricter platforms
        if platform == ATSPlatform.TALEO:
            # Taleo heavily penalizes poor formatting
            format_weight = 0.4
        elif platform == ATSPlatform.WORKDAY:
            format_weight = 0.3
        else:
            format_weight = 0.2

        # Weighted average of base probability and format score
        platform_prob = (
            base_probability * (1 - format_weight) +
            format_score * format_weight
        ) * difficulty

        return max(0, min(100, platform_prob))

    def _determine_confidence_level(
        self,
        has_job_description: bool,
        keyword_match_rate: Optional[float],
        format_score: float
    ) -> ConfidenceLevel:
        """
        Determine confidence level for the probability estimate.

        Args:
            has_job_description: Whether job description was provided
            keyword_match_rate: Keyword match rate (0-1) if available
            format_score: Formatting score (0-100)

        Returns:
            Confidence level
        """
        # High confidence if we have job description and good data
        if has_job_description and keyword_match_rate is not None:
            if format_score >= 80:
                return ConfidenceLevel.HIGH
            else:
                return ConfidenceLevel.MODERATE

        # Moderate confidence if we have some data
        if has_job_description or format_score >= 70:
            return ConfidenceLevel.MODERATE

        # Low confidence otherwise
        return ConfidenceLevel.LOW

    def _get_interpretation(self, overall_probability: float) -> str:
        """
        Get human-readable interpretation of pass probability.

        Args:
            overall_probability: Overall pass probability (0-100)

        Returns:
            Interpretation string
        """
        if overall_probability >= 80:
            return "High chance of passing ATS"
        elif overall_probability >= 60:
            return "Moderate chance of passing ATS"
        elif overall_probability >= 40:
            return "Fair chance of passing ATS"
        else:
            return "Low chance of passing ATS - needs improvement"

    def calculate_pass_probability(
        self,
        overall_score: float,
        breakdown: Dict[str, Dict],
        auto_reject: bool = False,
        critical_issues: Optional[List[str]] = None,
        keyword_details: Optional[Dict] = None,
        job_description: Optional[str] = None
    ) -> Dict:
        """
        Calculate comprehensive pass probability analysis.

        Args:
            overall_score: Overall resume score (0-100)
            breakdown: Score breakdown by category
            auto_reject: Whether resume has auto-reject flags
            critical_issues: List of critical issues
            keyword_details: Keyword matching details
            job_description: Job description if provided

        Returns:
            Dictionary with:
                - overall_probability: Overall pass probability (0-100)
                - platform_breakdown: Probability for each platform
                - confidence_level: Confidence level (high/moderate/low)
                - interpretation: Human-readable interpretation
                - color_code: Color for UI (green/yellow/red)
        """
        critical_issues = critical_issues or []

        # Calculate base probability
        base_probability = self._calculate_base_probability(overall_score)

        # Apply critical adjustments
        adjusted_probability = self._apply_critical_adjustments(
            base_probability,
            auto_reject,
            critical_issues
        )

        # Get format score from breakdown
        format_score = 70.0  # Default
        if breakdown and "formatting" in breakdown:
            format_details = breakdown["formatting"]
            if isinstance(format_details, dict) and "score" in format_details:
                max_score = format_details.get("maxScore", 100)
                format_score = (format_details["score"] / max_score) * 100

        # Calculate platform-specific probabilities
        platform_breakdown = {}
        for platform in [ATSPlatform.TALEO, ATSPlatform.WORKDAY, ATSPlatform.GREENHOUSE]:
            platform_prob = self._calculate_platform_probability(
                adjusted_probability,
                platform,
                format_score
            )
            platform_breakdown[platform.value] = {
                "probability": round(platform_prob, 1),
                "status": self._get_platform_status(platform_prob),
            }

        # Calculate weighted average across platforms
        overall_probability = sum(
            platform_breakdown[platform.value]["probability"] *
            self.PLATFORM_MARKET_SHARE[platform]
            for platform in [ATSPlatform.TALEO, ATSPlatform.WORKDAY, ATSPlatform.GREENHOUSE]
        ) / sum(
            self.PLATFORM_MARKET_SHARE[platform]
            for platform in [ATSPlatform.TALEO, ATSPlatform.WORKDAY, ATSPlatform.GREENHOUSE]
        )

        # Determine confidence level
        keyword_match_rate = None
        if keyword_details and "match_rate" in keyword_details:
            keyword_match_rate = keyword_details["match_rate"]

        confidence_level = self._determine_confidence_level(
            has_job_description=bool(job_description),
            keyword_match_rate=keyword_match_rate,
            format_score=format_score
        )

        # Get interpretation
        interpretation = self._get_interpretation(overall_probability)

        # Determine color code
        if overall_probability >= 80:
            color_code = "green"
        elif overall_probability >= 60:
            color_code = "yellow"
        else:
            color_code = "red"

        return {
            "overall_probability": round(overall_probability, 1),
            "platform_breakdown": platform_breakdown,
            "confidence_level": confidence_level.value,
            "interpretation": interpretation,
            "color_code": color_code,
            "based_on_score": overall_score,
        }

    def _get_platform_status(self, probability: float) -> str:
        """
        Get status label for platform probability.

        Args:
            probability: Platform probability (0-100)

        Returns:
            Status label
        """
        if probability >= 80:
            return "excellent"
        elif probability >= 60:
            return "good"
        elif probability >= 40:
            return "fair"
        else:
            return "poor"
