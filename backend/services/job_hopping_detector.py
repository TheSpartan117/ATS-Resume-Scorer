"""
Job Hopping Detector

Detects patterns of frequent job changes (positions held <1 year).

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

import re
from datetime import datetime
from dateutil import parser
from typing import Dict, List, Optional


class JobHoppingDetector:
    """
    Detect job hopping patterns in employment history.

    Penalty structure:
    - Each position <12 months: -1 point
    - Maximum penalty: -3 points
    - Exceptions: Contract, intern, consultant, temporary roles
    """

    SHORT_STINT_THRESHOLD_MONTHS = 12  # <12 months = short stint
    MAX_PENALTY = 3                    # Maximum -3 points

    # Keywords indicating exempt roles (contract, intern, etc.)
    EXEMPT_KEYWORDS = {
        'contract', 'contractor', 'contracting',
        'intern', 'internship',
        'consultant', 'consulting',
        'temporary', 'temp',
        'freelance', 'freelancer',
        'part-time', 'part time'
    }

    def __init__(self):
        """Initialize job hopping detector."""
        pass

    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """
        Parse date string to datetime object.

        Handles same formats as GapDetector.
        """
        if not date_str:
            return None

        date_str = str(date_str).strip()

        # Handle "Present", "Current"
        if date_str.lower() in ['present', 'current', 'now', 'ongoing']:
            return datetime.now()

        try:
            return parser.parse(date_str, default=datetime(datetime.now().year, 1, 1))
        except:
            # Try manual parsing for YYYY-MM
            match = re.match(r'(\d{4})-(\d{2})', date_str)
            if match:
                year, month = match.groups()
                return datetime(int(year), int(month), 1)

            # Try MM/YYYY
            match = re.match(r'(\d{2})/(\d{4})', date_str)
            if match:
                month, year = match.groups()
                return datetime(int(year), int(month), 1)

            return None

    def _calculate_duration_months(self, start_date: datetime, end_date: datetime) -> int:
        """Calculate duration in months between two dates."""
        if not start_date or not end_date:
            return 0

        months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
        return max(0, months)

    def _is_exempt_role(self, title: str) -> bool:
        """
        Check if role is exempt from job hopping penalty.

        Args:
            title: Job title

        Returns:
            True if role is contract/intern/consultant/temp
        """
        if not title:
            return False

        title_lower = title.lower()

        return any(keyword in title_lower for keyword in self.EXEMPT_KEYWORDS)

    def detect(self, employment_history: List[Dict]) -> Dict:
        """
        Detect job hopping pattern in employment history.

        Args:
            employment_history: List of employment records, each with:
                - title: str (job title)
                - start_date: str
                - end_date: str

        Returns:
            {
                'short_stints_count': int,
                'penalty_score': int (0 to -3),
                'short_stints': [
                    {
                        'title': str,
                        'duration_months': int,
                        'is_excluded': bool,
                        'exclusion_reason': str (if excluded)
                    }
                ],
                'max_penalty': int (-3)
            }
        """
        if not employment_history:
            return {
                'short_stints_count': 0,
                'penalty_score': 0,
                'short_stints': [],
                'max_penalty': -self.MAX_PENALTY
            }

        short_stints = []

        for job in employment_history:
            title = job.get('title', 'Unknown')
            start = self._parse_date(job.get('start_date'))
            end = self._parse_date(job.get('end_date'))

            if not start or not end:
                continue

            duration_months = self._calculate_duration_months(start, end)

            # Check if short stint (<12 months)
            if duration_months < self.SHORT_STINT_THRESHOLD_MONTHS:
                is_excluded = self._is_exempt_role(title)

                stint_info = {
                    'title': title,
                    'duration_months': duration_months,
                    'is_excluded': is_excluded
                }

                if is_excluded:
                    stint_info['exclusion_reason'] = 'Contract/Intern/Consultant/Temp role'

                short_stints.append(stint_info)

        # Count only non-excluded short stints for penalty
        penalized_stints_count = sum(1 for s in short_stints if not s['is_excluded'])

        # Calculate penalty: -1 per short stint, capped at -3
        penalty_score = -min(penalized_stints_count, self.MAX_PENALTY)

        return {
            'short_stints_count': penalized_stints_count,
            'penalty_score': penalty_score,
            'short_stints': short_stints,
            'max_penalty': -self.MAX_PENALTY
        }

    def analyze(self, employment_history: List[Dict]) -> Dict:
        """
        Complete job hopping analysis with additional context.

        Args:
            employment_history: List of employment records

        Returns:
            Detection results with additional analysis
        """
        detection = self.detect(employment_history)

        total_positions = len(employment_history)
        short_stints_count = detection['short_stints_count']

        return {
            **detection,
            'total_positions': total_positions,
            'hopping_rate': (short_stints_count / total_positions * 100) if total_positions > 0 else 0.0,
            'has_job_hopping_pattern': short_stints_count >= 2
        }


# Singleton instance
_detector_instance = None

def get_job_hopping_detector() -> JobHoppingDetector:
    """Get singleton instance of JobHoppingDetector."""
    global _detector_instance
    if _detector_instance is None:
        _detector_instance = JobHoppingDetector()
    return _detector_instance
