"""
P5.2: Career Recency (3 points)

Evaluates how recently the candidate was employed, rewarding current employment
and recent job activity while penalizing extended unemployment.

Scoring:
- Currently employed (Present/ongoing): 3 pts
- Left within 3 months: 2 pts
- Left 3-12 months ago: 1 pt
- Left >12 months ago: 0 pts

Research basis:
- ATS systems prioritize actively employed or recently active candidates
- Recruiters typically view gaps >12 months as requiring explanation
- Current employment signals stability and market relevance
"""

import re
from datetime import datetime
from dateutil import parser
from typing import List, Dict, Any, Optional


class CareerRecencyScorer:
    """Scores resume based on recency of most recent employment."""

    MAX_SCORE = 3

    def __init__(self):
        """Initialize scorer."""
        pass

    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """
        Parse date string to datetime object.

        Handles formats:
        - "2020-01" (YYYY-MM)
        - "01/2020" (MM/YYYY)
        - "Jan 2020"
        - "January 2020"
        - "2020" (year only)
        - "Present", "Current", "Now", "ongoing" (returns current date)

        Args:
            date_str: Date string

        Returns:
            datetime object or None if unparseable
        """
        if not date_str:
            return None

        date_str = str(date_str).strip()

        # Handle "Present", "Current", "Now", "ongoing"
        if date_str.lower() in ['present', 'current', 'now', 'ongoing']:
            return datetime.now()

        try:
            # Try parsing with dateutil (handles many formats)
            return parser.parse(date_str, default=datetime(datetime.now().year, 1, 1))
        except:
            # Try manual parsing for YYYY-MM format
            match = re.match(r'(\d{4})-(\d{2})', date_str)
            if match:
                year, month = match.groups()
                return datetime(int(year), int(month), 1)

            # Try MM/YYYY format
            match = re.match(r'(\d{2})/(\d{4})', date_str)
            if match:
                month, year = match.groups()
                return datetime(int(year), int(month), 1)

            # Try YYYY only
            match = re.match(r'(\d{4})$', date_str)
            if match:
                year = match.group(1)
                return datetime(int(year), 1, 1)

            return None

    def _extract_dates_from_range(self, date_range: str) -> tuple[Optional[str], Optional[str]]:
        """
        Extract start and end dates from a date range string.

        Handles various separators: -, –, —

        Args:
            date_range: Date range string like "2020 - Present" or "Jan 2020 - Dec 2021"

        Returns:
            Tuple of (start_date_str, end_date_str)
        """
        if not date_range:
            return None, None

        # Replace various dash types with standard hyphen surrounded by spaces for easier splitting
        # This helps differentiate date separators from range separators
        normalized = date_range.replace('–', ' - ').replace('—', ' - ')

        # Look for pattern: something - something (with spaces around the dash)
        # This is the range separator
        match = re.search(r'\s+-\s+', normalized)

        if match:
            # Split on the first occurrence of spaced dash
            idx = match.start()
            start_date = normalized[:idx].strip()
            end_date = normalized[idx:].strip(' -').strip()
            return start_date, end_date

        # Fallback: try splitting on any dash and reconstruct intelligently
        parts = date_range.split('-')

        if len(parts) < 2:
            return None, None

        if len(parts) == 2:
            return parts[0].strip(), parts[1].strip()

        # For 3+ parts, need to determine where the range separator is
        # Common patterns:
        # "2020-01 - Present" -> ["2020", "01 ", " Present"]
        # "Jan 2020 - Dec 2021" -> ["Jan 2020 ", " Dec 2021"]

        # Strategy: Look for a part that starts with whitespace (indicates separator)
        for i in range(1, len(parts)):
            if parts[i].startswith(' ') or (i > 0 and parts[i-1].endswith(' ')):
                # This dash was a separator
                start_date = '-'.join(parts[:i]).strip()
                end_date = '-'.join(parts[i:]).strip()
                return start_date, end_date

        # Default fallback: assume last dash is the separator
        start_date = '-'.join(parts[:-1]).strip()
        end_date = parts[-1].strip()

        return start_date, end_date

    def _calculate_months_since(self, end_date: datetime) -> int:
        """
        Calculate months since the end date.

        Args:
            end_date: End date of employment

        Returns:
            Number of months since end date (0 if in future or current)
        """
        now = datetime.now()

        # If end date is in the future or very recent, consider as current
        if end_date >= now:
            return 0

        # Calculate months difference
        months = (now.year - end_date.year) * 12 + (now.month - end_date.month)

        return max(0, months)

    def _is_currently_employed(self, end_date_str: str) -> bool:
        """
        Check if the end date indicates current employment.

        Args:
            end_date_str: End date string

        Returns:
            True if currently employed
        """
        if not end_date_str:
            return False

        end_str_lower = end_date_str.strip().lower()
        return end_str_lower in ['present', 'current', 'now', 'ongoing']

    def _get_recency_score(self, months_since: int, is_current: bool) -> tuple[int, str]:
        """
        Calculate score based on months since last employment.

        Args:
            months_since: Months since employment ended
            is_current: Whether currently employed

        Returns:
            Tuple of (score, status)
        """
        if is_current or months_since == 0:
            return 3, 'currently_employed'
        elif months_since <= 3:
            return 2, 'left_within_3_months'
        elif months_since <= 12:
            return 1, 'left_3_12_months_ago'
        else:
            return 0, 'left_over_12_months_ago'

    def score(self, experience: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Score career recency based on most recent employment.

        Args:
            experience: List of experience dictionaries with 'dates' field

        Returns:
            Dictionary containing:
            - score: Points earned (0-3)
            - max_score: Maximum possible points (3)
            - recency_status: Status string
            - months_since_last: Months since last employment (None if no valid dates)
            - most_recent_end_date: Most recent end date string
            - details: Additional information
        """
        # Handle empty experience
        if not experience:
            return self._empty_result('no_experience')

        # Find most recent employment end date
        most_recent_end = None
        most_recent_end_str = None
        is_currently_employed = False

        for job in experience:
            dates = job.get('dates')
            if not dates:
                continue

            start_str, end_str = self._extract_dates_from_range(dates)

            if not end_str:
                continue

            # Check if currently employed
            if self._is_currently_employed(end_str):
                is_currently_employed = True
                most_recent_end = datetime.now()
                most_recent_end_str = end_str
                break  # Current employment trumps all

            # Parse end date
            end_date = self._parse_date(end_str)

            if end_date:
                if most_recent_end is None or end_date > most_recent_end:
                    most_recent_end = end_date
                    most_recent_end_str = end_str

        # Handle case where no valid dates found
        if most_recent_end is None and not is_currently_employed:
            return self._empty_result('no_valid_dates')

        # Calculate months since last employment
        months_since = 0 if is_currently_employed else self._calculate_months_since(most_recent_end)

        # Calculate score
        score, status = self._get_recency_score(months_since, is_currently_employed)

        return {
            'score': score,
            'max_score': self.MAX_SCORE,
            'recency_status': status,
            'months_since_last': months_since,
            'most_recent_end_date': most_recent_end_str,
            'details': {
                'is_currently_employed': is_currently_employed,
                'scoring_breakdown': {
                    'currently_employed': '3 pts',
                    'left_within_3_months': '2 pts',
                    'left_3_12_months_ago': '1 pt',
                    'left_over_12_months_ago': '0 pts'
                }
            }
        }

    def _empty_result(self, status: str) -> Dict[str, Any]:
        """
        Return result for empty or invalid experience.

        Args:
            status: Status string

        Returns:
            Result dictionary with 0 score
        """
        return {
            'score': 0,
            'max_score': self.MAX_SCORE,
            'recency_status': status,
            'months_since_last': None,
            'most_recent_end_date': None,
            'details': {
                'is_currently_employed': False,
                'scoring_breakdown': {
                    'currently_employed': '3 pts',
                    'left_within_3_months': '2 pts',
                    'left_3_12_months_ago': '1 pt',
                    'left_over_12_months_ago': '0 pts'
                }
            }
        }


def score_career_recency(experience: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Convenience function to score career recency.

    Args:
        experience: List of experience dictionaries

    Returns:
        Score result dictionary
    """
    scorer = CareerRecencyScorer()
    return scorer.score(experience)
