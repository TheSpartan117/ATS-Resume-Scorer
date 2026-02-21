"""
P5.1 - Years of Experience Alignment (10 pts)

Validates that resume experience years match selected experience level using gradient scoring.

Research basis:
- Experience level misalignment is a top reason for ATS rejection
- However, relevant experience quality matters more than quantity
- High-impact candidates with shorter but relevant experience should not be auto-rejected
- Overlap between levels reflects real-world hiring practices

Implementation:
- Calculate total years from experience dates in resume
- Use gradient scoring with overlap between levels:
  - Beginner: 0-3 years ideal, up to 5 acceptable
  - Intermediary: 3-7 years ideal, 1.5-10 acceptable with overlap
  - Senior: 7+ years ideal, 5+ acceptable for strong experience, 3+ if high-impact
- Scoring uses 2-10 point scale (never auto-rejects at 0)
- Allows exceptional candidates to qualify with less traditional experience

References:
- LinkedIn Talent Insights (2024): Experience level filtering
- Workday HCM: Experience range validation
- Greenhouse ATS: Level-based screening criteria
- ResumeWorded: Quality over quantity approach
"""

from typing import Dict, List
from datetime import datetime
import re
import logging

logger = logging.getLogger(__name__)


class YearsAlignmentScorer:
    """
    Score resume based on years of experience alignment with selected level.

    Uses gradient scoring with overlap to reflect real-world hiring:

    Beginner (0-3 years ideal):
    - 10 pts: 0-3.5 years
    - 8 pts: 3.5-5 years (overlap with intermediary)
    - 5 pts: 5-7 years
    - 3 pts: 7+ years (overqualified)

    Intermediary (3-7 years ideal):
    - 10 pts: 2.5-8 years (allows overlap)
    - 7 pts: 1.5-2.5 years
    - 8 pts: 8-10 years
    - 4-5 pts: outside range

    Senior (7+ years ideal):
    - 10 pts: 7+ years
    - 8 pts: 5-7 years (strong intermediary)
    - 6 pts: 3-5 years (high-impact acceptable)
    - 4 pts: 2-3 years (relevant experience critical)
    - 2 pts: <2 years
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
        Check if years align with expected range using gradient scoring.

        Uses gradient scoring with overlap between levels to reflect real-world hiring:
        - Relevant experience matters more than total years
        - Exceptional candidates with shorter but relevant experience should not be auto-rejected
        - Allows overlap between level boundaries

        Args:
            years: Calculated years
            expected_range: (min, max) tuple for level
            level: Experience level name

        Returns:
            Dictionary with score, aligned, and details
        """
        min_years, max_years = expected_range

        # Gradient scoring based on level
        if level.lower() == 'beginner':
            # Beginner: 0-3 years ideal
            if years <= 3.5:
                score = 10  # Perfect
                aligned = True
                details = f'{years:.1f} years experience aligns well with {level} level'
            elif years <= 5:
                score = 8  # Still good, overlaps with intermediary
                aligned = True
                details = f'{years:.1f} years experience aligns with {level} level (acceptable overlap)'
            elif years <= 7:
                score = 5  # Getting experienced
                aligned = False
                details = f'{years:.1f} years experience suggests intermediary level'
            else:
                score = 3  # Overqualified
                aligned = False
                details = f'{years:.1f} years experience suggests senior level'

        elif level.lower() == 'intermediary':
            # Intermediary: 3-7 years ideal
            if 2.5 <= years <= 8:
                score = 10  # Perfect fit with overlap
                aligned = True
                details = f'{years:.1f} years experience aligns well with {level} level'
            elif 1.5 <= years < 2.5:
                score = 7  # Junior but acceptable
                aligned = True
                details = f'{years:.1f} years experience is acceptable for {level} level'
            elif 8 < years <= 10:
                score = 8  # Senior but acceptable
                aligned = True
                details = f'{years:.1f} years experience is acceptable for {level} level'
            elif years < 1.5:
                score = 4  # Too junior
                aligned = False
                details = f'{years:.1f} years experience suggests beginner level'
            else:
                score = 5  # Too senior
                aligned = False
                details = f'{years:.1f} years experience suggests senior level'

        else:  # senior
            # Senior: 7+ years ideal, but allow high-impact candidates with less
            if years >= 7:
                score = 10  # Perfect
                aligned = True
                details = f'{years:.1f} years experience aligns well with {level} level'
            elif years >= 5:
                score = 8  # Strong intermediary, acceptable for senior
                aligned = True
                details = f'{years:.1f} years experience is acceptable for {level} level (strong experience)'
            elif years >= 3:
                score = 6  # Intermediary, possible if high-impact
                aligned = False
                details = f'{years:.1f} years experience is below typical {level} level but acceptable for high-impact roles'
            elif years >= 2:
                score = 4  # Junior but don't auto-reject if relevant
                aligned = False
                details = f'{years:.1f} years experience is below {level} level expectations; ensure highly relevant experience'
            else:
                score = 2  # Very junior
                aligned = False
                details = f'{years:.1f} years experience is significantly below {level} level expectations'

        return {
            'score': score,
            'aligned': aligned,
            'details': details
        }


def create_scorer() -> YearsAlignmentScorer:
    """
    Factory function to create YearsAlignmentScorer instance.

    Returns:
        YearsAlignmentScorer instance
    """
    return YearsAlignmentScorer()
