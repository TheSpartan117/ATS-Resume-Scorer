"""
P6.1: Employment Gaps Penalty (-5 points max)

Penalizes unexplained employment gaps in work history.

Penalty Structure:
- -1 point per 6 months of employment gaps
- Gaps < 3 months are ignored (normal transition time)
- Maximum penalty: -5 points

Research Basis:
- ATS systems flag gaps >3 months as concern
- 6-12 month gaps considered acceptable with explanation
- Extensive gaps (>2 years cumulative) significantly impact scoring
- Greenhouse/Workday apply graduated penalties for gaps

Calculation:
    penalty = -(total_gap_months // 6)
    capped at -5 points maximum

Example:
    7-month gap: -1 point
    18-month gap: -3 points
    35-month gap: -5 points (capped)
"""

from typing import Dict, List, Optional
from backend.services.gap_detector import get_gap_detector


class EmploymentGapsPenalty:
    """
    Calculate penalty for employment gaps using GapDetector.

    Uses the foundation layer's GapDetector to identify and measure
    employment gaps, then applies graduated penalties.

    Attributes:
        MAX_PENALTY: Maximum penalty points (-5)
        PENALTY_PER_6_MONTHS: Points deducted per 6 months gap (-1)
        GAP_THRESHOLD: Minimum gap duration to consider (3 months)
    """

    MAX_PENALTY = 5  # Maximum -5 points
    PENALTY_PER_6_MONTHS = 1  # -1 point per 6 months
    GAP_THRESHOLD = 3  # Gaps < 3 months ignored

    def __init__(self):
        """Initialize with GapDetector instance."""
        self.gap_detector = get_gap_detector()

    def score(self, employment_history: Optional[List[Dict]]) -> Dict:
        """
        Calculate employment gap penalty.

        Args:
            employment_history: List of employment records, each with:
                - start_date: str (various formats: "YYYY-MM", "MM/YYYY", "Jan 2020")
                - end_date: str ("Present", "Current" for ongoing jobs)

        Returns:
            Dictionary containing:
            {
                'penalty': int (0 to -5),           # Points deducted
                'max_penalty': int (-5),            # Maximum possible penalty
                'gaps_detected': int,               # Number of gaps ≥3 months
                'total_months': int,                # Total months of all gaps
                'gap_details': List[Dict]           # Details of each gap ≥3 months
            }

        Example:
            >>> calculator = EmploymentGapsPenalty()
            >>> history = [
            ...     {'start_date': '2018-01', 'end_date': '2019-12'},
            ...     {'start_date': '2020-06', 'end_date': 'Present'}
            ... ]
            >>> result = calculator.score(history)
            >>> result['penalty']
            -1  # 6-month gap
            >>> result['gaps_detected']
            1
        """
        # Handle edge cases
        if not employment_history:
            return {
                'penalty': 0,
                'max_penalty': -self.MAX_PENALTY,
                'gaps_detected': 0,
                'total_months': 0,
                'gap_details': []
            }

        # Use GapDetector to analyze employment history
        detection_result = self.gap_detector.detect(employment_history)

        # Extract gap information
        total_gap_months = detection_result['total_gap_months']
        gaps = detection_result['gaps']

        # Calculate penalty: -1 per 6 months, capped at -5
        penalty_count = total_gap_months // 6
        penalty = -min(penalty_count, self.MAX_PENALTY)

        # Format gap details for output
        gap_details = [
            {
                'start_date': gap['start_date'],
                'end_date': gap['end_date'],
                'duration_months': gap['duration_months']
            }
            for gap in gaps
        ]

        return {
            'penalty': penalty,
            'max_penalty': -self.MAX_PENALTY,
            'gaps_detected': len(gaps),
            'total_months': total_gap_months,
            'gap_details': gap_details
        }

    def analyze(self, employment_history: Optional[List[Dict]]) -> Dict:
        """
        Perform complete gap analysis with additional context.

        Args:
            employment_history: List of employment records

        Returns:
            Score results with additional analysis fields:
            - All fields from score()
            - employment_count: Number of jobs in history
            - has_significant_gaps: Boolean (total gaps ≥ 6 months)
            - average_gap_duration: Average months per gap (if any)

        Example:
            >>> calculator = EmploymentGapsPenalty()
            >>> result = calculator.analyze(employment_history)
            >>> result['has_significant_gaps']
            True
        """
        score_result = self.score(employment_history)

        # Calculate additional metrics
        employment_count = len(employment_history) if employment_history else 0
        has_significant_gaps = score_result['total_months'] >= 6
        average_gap_duration = (
            score_result['total_months'] / score_result['gaps_detected']
            if score_result['gaps_detected'] > 0
            else 0
        )

        return {
            **score_result,
            'employment_count': employment_count,
            'has_significant_gaps': has_significant_gaps,
            'average_gap_duration': round(average_gap_duration, 1)
        }


# Singleton instance for convenience
_penalty_calculator = None


def get_employment_gaps_penalty() -> EmploymentGapsPenalty:
    """
    Get singleton instance of EmploymentGapsPenalty.

    Returns:
        Shared EmploymentGapsPenalty instance

    Example:
        >>> calculator = get_employment_gaps_penalty()
        >>> result = calculator.score(employment_history)
    """
    global _penalty_calculator
    if _penalty_calculator is None:
        _penalty_calculator = EmploymentGapsPenalty()
    return _penalty_calculator
