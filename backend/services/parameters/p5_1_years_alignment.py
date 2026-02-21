"""
P5.1 - Years of Experience Alignment (10 pts)

Validates that resume experience years match selected experience level.

Research basis:
- Experience level misalignment is a top reason for ATS rejection
- Candidates listing 10+ years experience for "entry-level" positions get auto-rejected
- Conversely, candidates with <5 years applying to "senior" roles rarely pass initial screen
- Accurate experience alignment improves match quality and reduces wasted applications

Implementation:
- Calculate total years from experience dates in resume
- Compare against selected experience level expectations:
  - Beginner: 0-3 years
  - Intermediary: 3-7 years
  - Senior: 7+ years
- Scoring:
  - 10 pts if years align with level
  - 5 pts if close (within 1 year either direction)
  - 0 pts if misaligned (completely outside range)

References:
- LinkedIn Talent Insights (2024): Experience level filtering
- Workday HCM: Experience range validation
- Greenhouse ATS: Level-based screening criteria
"""

from typing import Dict, List
from datetime import datetime
import re
import logging

logger = logging.getLogger(__name__)


class YearsAlignmentScorer:
    """
    Score resume based on years of experience alignment with selected level.

    Scoring:
    - 10 points: Years align with level range
    - 5 points: Years close to range (within 1 year)
    - 0 points: Years misaligned with level

    Experience Level Ranges:
    - Beginner: 0-3 years
    - Intermediary: 3-7 years
    - Senior: 7+ years
    """

    def __init__(self):
        """Initialize years alignment scorer"""
        self.max_points = 10

        # Experience level ranges
        # Boundaries overlap: 3 years can be beginner or intermediary, 7 can be intermediary or senior
        self.level_ranges = {
            'beginner': (0, 3),
            'intermediary': (3, 7),
            'senior': (7, 100)  # 100 as effective infinity
        }

    def score(self, experience: List[Dict], level: str) -> Dict:
        """
        Score experience years alignment with selected level.

        Args:
            experience: List of experience entries with dates
            level: Experience level ('beginner', 'intermediary', 'senior')

        Returns:
            Dictionary with:
            - score: Points (0, 5, or 10)
            - max_score: Maximum possible points (10)
            - years_calculated: Total years calculated from resume
            - level: Selected experience level
            - aligned: Boolean indicating if aligned
            - details: Human-readable feedback
            - parameter: Parameter ID (P5.1)
            - name: Parameter name
        """
        # Handle empty experience
        if not experience or len(experience) == 0:
            return {
                'score': 0,
                'max_score': self.max_points,
                'years_calculated': 0,
                'level': level,
                'aligned': False,
                'details': 'No experience entries found to calculate years',
                'parameter': 'P5.1',
                'name': 'Years of Experience Alignment'
            }

        # Calculate total years
        years = self._calculate_total_years(experience)

        # Get expected range for level (case-insensitive)
        level_lower = level.lower()
        expected_range = self.level_ranges.get(level_lower, self.level_ranges['intermediary'])

        # Determine alignment
        alignment_result = self._check_alignment(years, expected_range, level)

        # Build result
        result = {
            'score': alignment_result['score'],
            'max_score': self.max_points,
            'years_calculated': round(years, 1),
            'level': level,
            'aligned': alignment_result['aligned'],
            'details': alignment_result['details'],
            'parameter': 'P5.1',
            'name': 'Years of Experience Alignment'
        }

        return result

    def _calculate_total_years(self, experience: List[Dict]) -> float:
        """
        Calculate total years of experience from all positions.

        Args:
            experience: List of experience entries

        Returns:
            Total years (float)
        """
        total_years = 0.0
        current_year = datetime.now().year
        current_month = datetime.now().month

        for entry in experience:
            dates = entry.get('dates', '')
            if not dates:
                continue

            # Parse date range
            years = self._parse_date_range(dates, current_year, current_month)
            total_years += years

        return total_years

    def _parse_date_range(self, dates: str, current_year: int, current_month: int) -> float:
        """
        Parse a date range string and calculate years.

        Supports formats:
        - "2020 - Present"
        - "2018 - 2020"
        - "Jan 2020 - Jun 2022"
        - "January 2020 - December 2022"
        - "2020-2022"

        Args:
            dates: Date range string
            current_year: Current year
            current_month: Current month

        Returns:
            Years duration (float)
        """
        try:
            # Split on common separators
            dates = dates.replace('–', '-').replace('—', '-')  # Normalize dashes
            parts = re.split(r'\s*(?:-|to)\s*', dates, flags=re.IGNORECASE)

            if len(parts) != 2:
                logger.warning(f"Could not parse date range: {dates}")
                return 0.0

            start_str = parts[0].strip()
            end_str = parts[1].strip()

            # Parse start date
            start_year, start_month = self._parse_date(start_str)
            if start_year is None:
                return 0.0

            # Parse end date
            if end_str.lower() in ['present', 'current', 'now']:
                end_year = current_year
                end_month = current_month
            else:
                end_year, end_month = self._parse_date(end_str)
                if end_year is None:
                    return 0.0

            # Calculate years with month precision
            years = (end_year - start_year) + (end_month - start_month) / 12.0

            return max(0.0, years)

        except Exception as e:
            logger.warning(f"Error parsing date range '{dates}': {e}")
            return 0.0

    def _parse_date(self, date_str: str) -> tuple:
        """
        Parse a date string to extract year and month.

        Args:
            date_str: Date string (e.g., "2020", "Jan 2020", "January 2020")

        Returns:
            Tuple of (year, month) or (None, None) if parsing fails
        """
        date_str = date_str.strip()

        # Month name mappings
        months = {
            'january': 1, 'jan': 1,
            'february': 2, 'feb': 2,
            'march': 3, 'mar': 3,
            'april': 4, 'apr': 4,
            'may': 5,
            'june': 6, 'jun': 6,
            'july': 7, 'jul': 7,
            'august': 8, 'aug': 8,
            'september': 9, 'sep': 9, 'sept': 9,
            'october': 10, 'oct': 10,
            'november': 11, 'nov': 11,
            'december': 12, 'dec': 12
        }

        # Try to extract year (4 digits)
        year_match = re.search(r'\b(19|20)\d{2}\b', date_str)
        if not year_match:
            return (None, None)

        year = int(year_match.group(0))

        # Try to extract month
        month = 1  # Default to January if no month specified
        for month_name, month_num in months.items():
            if month_name in date_str.lower():
                month = month_num
                break

        return (year, month)

    def _check_alignment(self, years: float, expected_range: tuple, level: str) -> Dict:
        """
        Check if years align with expected range.

        Args:
            years: Calculated years
            expected_range: (min, max) tuple for level
            level: Experience level name

        Returns:
            Dictionary with score, aligned, and details
        """
        min_years, max_years = expected_range

        # Perfect alignment: within range (with 0.5 year buffer for month precision at boundaries)
        # This allows values like 3.1 to still count as perfect for beginner (0-3) range
        if min_years <= years <= (max_years + 0.5):
            return {
                'score': 10,
                'aligned': True,
                'details': f'{years:.1f} years experience shows perfect alignment with {level} level ({min_years}-{max_years} years expected)'
            }

        # Close alignment: within 1 year of range boundaries (with 0.5 year buffer for month precision)
        if (min_years - 1.5) <= years < min_years:
            return {
                'score': 5,
                'aligned': False,
                'details': f'{years:.1f} years experience is close to {level} level (within 1 year of {min_years}-{max_years} years expected)'
            }

        if max_years < years <= (max_years + 1.5) and max_years < 90:  # Don't apply upper tolerance to senior
            return {
                'score': 5,
                'aligned': False,
                'details': f'{years:.1f} years experience is close to {level} level (within 1 year of {min_years}-{max_years} years expected)'
            }

        # Misaligned: outside range and not close
        if years < min_years:
            return {
                'score': 0,
                'aligned': False,
                'details': f'{years:.1f} years experience is below {level} level expectations ({min_years}-{max_years} years expected)'
            }
        else:
            return {
                'score': 0,
                'aligned': False,
                'details': f'{years:.1f} years experience exceeds {level} level expectations ({min_years}-{max_years} years expected)'
            }


def create_scorer() -> YearsAlignmentScorer:
    """
    Factory function to create YearsAlignmentScorer instance.

    Returns:
        YearsAlignmentScorer instance
    """
    return YearsAlignmentScorer()
