"""
P6.2: Job Hopping Penalty (-3 points maximum)

Penalizes pattern of frequent job changes (positions held <1 year).

Research basis:
- Recruiters/ATS systems flag candidates with 3+ jobs <1 year as unstable
- Career coaches recommend minimum 1-2 years per position for credibility
- Exception: Contract, internship, temporary roles are exempt

Penalty structure:
- Each position <12 months: -1 point
- Maximum penalty: -3 points
- Exceptions: Contract, internship, temporary, consultant roles

Calculation: penalty = -min(short_stints_count, 3)
"""

from typing import List, Dict, Any
from backend.services.job_hopping_detector import get_job_hopping_detector


class JobHoppingPenaltyScorer:
    """
    Scores job hopping penalties based on short employment stints.

    Uses JobHoppingDetector from foundation layer for detection logic.
    """

    MAX_PENALTY = 3  # Maximum -3 points

    def __init__(self):
        """Initialize scorer with job hopping detector."""
        self.detector = get_job_hopping_detector()

    def score(self, employment_history: List[Dict]) -> Dict[str, Any]:
        """
        Calculate job hopping penalty for employment history.

        Args:
            employment_history: List of employment records, each with:
                - title: str (job title)
                - start_date: str
                - end_date: str

        Returns:
            Dictionary containing:
            - penalty: int (0 to -3) - negative penalty points
            - short_stints_count: int - count of penalized short stints
            - flagged_positions: list - details of all short stints
            - details: dict - additional context
            - max_penalty: int (-3) - maximum possible penalty
        """
        # Handle empty employment history
        if not employment_history:
            return self._empty_result()

        # Use JobHoppingDetector for analysis
        detection_result = self.detector.detect(employment_history)

        # Extract results
        short_stints_count = detection_result['short_stints_count']
        penalty_score = detection_result['penalty_score']
        short_stints = detection_result['short_stints']

        # Build flagged positions list
        flagged_positions = []
        for stint in short_stints:
            position = {
                'title': stint['title'],
                'duration_months': stint['duration_months'],
                'is_excluded': stint['is_excluded']
            }
            if stint['is_excluded']:
                position['exclusion_reason'] = stint['exclusion_reason']

            flagged_positions.append(position)

        # Build details
        details = {
            'total_positions': len(employment_history),
            'positions_analyzed': len([job for job in employment_history
                                       if job.get('start_date') and job.get('end_date')])
        }

        # Add warning if exceeds max penalty
        if short_stints_count > self.MAX_PENALTY:
            details['exceeds_max_penalty'] = True
            details['actual_short_stints'] = short_stints_count
            details['message'] = f'Found {short_stints_count} short stints, but penalty capped at -{self.MAX_PENALTY} points'

        return {
            'penalty': penalty_score,  # Already negative (0 to -3)
            'short_stints_count': short_stints_count,
            'flagged_positions': flagged_positions,
            'details': details,
            'max_penalty': -self.MAX_PENALTY
        }

    def _empty_result(self) -> Dict[str, Any]:
        """Return result for empty employment history."""
        return {
            'penalty': 0,
            'short_stints_count': 0,
            'flagged_positions': [],
            'details': {
                'total_positions': 0,
                'positions_analyzed': 0
            },
            'max_penalty': -self.MAX_PENALTY
        }


def score_job_hopping(employment_history: List[Dict]) -> Dict[str, Any]:
    """
    Convenience function to calculate job hopping penalty.

    Args:
        employment_history: List of employment records with title, start_date, end_date

    Returns:
        Score result dictionary with penalty, flagged positions, and details

    Example:
        >>> employment = [
        ...     {'title': 'Engineer', 'start_date': '2022-01', 'end_date': '2022-08'},  # 7 months
        ...     {'title': 'Senior Engineer', 'start_date': '2020-01', 'end_date': '2021-12'}  # 23 months
        ... ]
        >>> result = score_job_hopping(employment)
        >>> result['penalty']
        -1
        >>> result['short_stints_count']
        1
    """
    scorer = JobHoppingPenaltyScorer()
    return scorer.score(employment_history)
