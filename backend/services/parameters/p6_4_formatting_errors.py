"""
P6.4 - Date/Formatting Errors Penalty (-2 pts max)

Penalizes date and formatting inconsistencies in experience section.

Error types:
1. Invalid dates (Feb 31, 13th month, etc.): -1 pt
2. Inconsistent formatting (mixing formats): -1 pt

Maximum penalty: -2 pts

Research basis:
- Date consistency is a basic professionalism indicator
- Invalid dates suggest carelessness or data errors
- Inconsistent formatting shows lack of attention to detail
- ATS systems may fail to parse inconsistent date formats
"""

import re
from typing import Dict, List, Any, Optional
from datetime import datetime


class DateFormattingScorer:
    """Scores date formatting quality and consistency in experience section."""

    def __init__(self):
        """Initialize scorer with date pattern definitions."""
        # Date format patterns
        self.patterns = {
            'month_year': re.compile(
                r'\b(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|'
                r'Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)'
                r'\s+\d{4}\b',
                re.IGNORECASE
            ),
            'yyyy_mm': re.compile(r'\b\d{4}[-/]\d{2}\b'),
            'mm_yyyy': re.compile(r'\b\d{2}[-/]\d{4}\b'),
            'year_only': re.compile(r'\b\d{4}\b'),
            'day_month_year': re.compile(
                r'\b\d{1,2}\s+(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|'
                r'Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)'
                r'\s+\d{4}\b',
                re.IGNORECASE
            ),
            'dd_mm_yyyy': re.compile(r'\b\d{2}[-/]\d{2}[-/]\d{4}\b')
        }

        # Month name to number mapping
        self.month_map = {
            'jan': 1, 'january': 1,
            'feb': 2, 'february': 2,
            'mar': 3, 'march': 3,
            'apr': 4, 'april': 4,
            'may': 5,
            'jun': 6, 'june': 6,
            'jul': 7, 'july': 7,
            'aug': 8, 'august': 8,
            'sep': 9, 'september': 9,
            'oct': 10, 'october': 10,
            'nov': 11, 'november': 11,
            'dec': 12, 'december': 12
        }

        # Days in month (non-leap year)
        self.days_in_month = {
            1: 31, 2: 29, 3: 31, 4: 30, 5: 31, 6: 30,
            7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31
        }

        # Ongoing role keywords
        self.ongoing_keywords = {'present', 'current', 'now'}

    def score(self, experience: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Score date formatting quality in experience section.

        Args:
            experience: List of experience entries with 'dates' field

        Returns:
            Dictionary containing:
            - penalty: Penalty points (0 to -2)
            - error_types: List of error type names
            - error_details: Detailed breakdown of each error type
            - has_invalid_dates: Boolean flag for invalid dates
            - has_inconsistent_formatting: Boolean flag for inconsistent formatting
            - parameter: Parameter identifier
            - name: Parameter name
            - max_penalty: Maximum possible penalty
        """
        # Initialize result
        result = {
            'penalty': 0,
            'error_types': [],
            'error_details': {
                'invalid_dates': [],
                'inconsistent_formatting': []
            },
            'has_invalid_dates': False,
            'has_inconsistent_formatting': False,
            'parameter': 'P6.4',
            'name': 'Date/Formatting Errors',
            'max_penalty': -2
        }

        # Handle empty or invalid input
        if not experience:
            return result

        # Extract and clean date strings
        date_strings = []
        for entry in experience:
            if 'dates' in entry and entry['dates']:
                date_str = str(entry['dates']).strip()
                if date_str:
                    date_strings.append(date_str)

        # If no valid dates, return 0 penalty
        if not date_strings:
            return result

        # Check for invalid dates (-1 pt)
        invalid_dates = self._check_invalid_dates(date_strings)
        if invalid_dates:
            result['penalty'] -= 1
            result['has_invalid_dates'] = True
            result['error_types'].append('invalid_dates')
            result['error_details']['invalid_dates'] = invalid_dates

        # Check for inconsistent formatting (-1 pt)
        # Only check if there are 2+ date strings
        if len(date_strings) >= 2:
            inconsistent_formatting = self._check_inconsistent_formatting(date_strings)
            if inconsistent_formatting:
                result['penalty'] -= 1
                result['has_inconsistent_formatting'] = True
                result['error_types'].append('inconsistent_formatting')
                result['error_details']['inconsistent_formatting'] = inconsistent_formatting

        # Cap penalty at -2
        result['penalty'] = max(result['penalty'], -2)

        return result

    def _check_invalid_dates(self, date_strings: List[str]) -> List[Dict[str, Any]]:
        """
        Check for invalid dates (month 13, Feb 31, day 32, etc.).

        Args:
            date_strings: List of date strings to check

        Returns:
            List of invalid date details
        """
        invalid_dates = []

        for date_str in date_strings:
            # Check each date component in the string
            errors = self._validate_date_components(date_str)
            if errors:
                invalid_dates.append({
                    'date_string': date_str,
                    'errors': errors
                })

        return invalid_dates

    def _validate_date_components(self, date_str: str) -> List[str]:
        """
        Validate individual date components in a date string.

        Args:
            date_str: Date string to validate

        Returns:
            List of error messages
        """
        errors = []

        # Remove ongoing keywords for validation
        date_str_clean = date_str.lower()
        for keyword in self.ongoing_keywords:
            date_str_clean = date_str_clean.replace(keyword, '')

        # Check YYYY-MM or MM-YYYY formats for invalid months
        yyyy_mm_matches = re.findall(r'\b(\d{4})[-/](\d{2})\b', date_str_clean)
        for year, month in yyyy_mm_matches:
            month_int = int(month)
            if month_int < 1 or month_int > 12:
                errors.append(f"Invalid month: {month}")

        mm_yyyy_matches = re.findall(r'\b(\d{2})[-/](\d{4})\b', date_str_clean)
        for month, year in mm_yyyy_matches:
            month_int = int(month)
            if month_int < 1 or month_int > 12:
                errors.append(f"Invalid month: {month}")

        # Check DD/MM/YYYY or DD-MM-YYYY formats
        dd_mm_yyyy_matches = re.findall(r'\b(\d{2})[-/](\d{2})[-/](\d{4})\b', date_str_clean)
        for day, month, year in dd_mm_yyyy_matches:
            day_int = int(day)
            month_int = int(month)

            # Validate month
            if month_int < 1 or month_int > 12:
                errors.append(f"Invalid month: {month}")
            else:
                # Validate day
                max_days = self.days_in_month.get(month_int, 31)
                if day_int < 1 or day_int > max_days:
                    errors.append(f"Invalid day: {day} for month {month}")

        # Check month names with days (e.g., "Feb 31 2020")
        month_day_matches = re.findall(
            r'\b(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|'
            r'Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)'
            r'\s+(\d{1,2})\s+(\d{4})\b',
            date_str_clean,
            re.IGNORECASE
        )
        for month_name, day, year in month_day_matches:
            month_int = self.month_map.get(month_name.lower())
            day_int = int(day)

            if month_int:
                max_days = self.days_in_month.get(month_int, 31)
                if day_int < 1 or day_int > max_days:
                    errors.append(f"Invalid day: {day} for {month_name}")

        # Check day-month-year format (e.g., "31 Feb 2020")
        day_month_matches = re.findall(
            r'\b(\d{1,2})\s+(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|'
            r'Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)'
            r'\s+(\d{4})\b',
            date_str_clean,
            re.IGNORECASE
        )
        for day, month_name, year in day_month_matches:
            month_int = self.month_map.get(month_name.lower())
            day_int = int(day)

            if month_int:
                max_days = self.days_in_month.get(month_int, 31)
                if day_int < 1 or day_int > max_days:
                    errors.append(f"Invalid day: {day} for {month_name}")

        return errors

    def _check_inconsistent_formatting(self, date_strings: List[str]) -> List[Dict[str, Any]]:
        """
        Check for inconsistent date formatting across entries.

        Args:
            date_strings: List of date strings to check

        Returns:
            List of inconsistency details
        """
        # Classify each date string by format type
        format_classifications = []

        for date_str in date_strings:
            format_type = self._classify_date_format(date_str)
            format_classifications.append({
                'date_string': date_str,
                'format_type': format_type
            })

        # Check if all formats are the same
        format_types = [fc['format_type'] for fc in format_classifications]
        unique_formats = set(format_types)

        # Remove None from unique formats (dates that couldn't be classified)
        unique_formats.discard(None)

        # If more than one unique format, it's inconsistent
        if len(unique_formats) > 1:
            return [{
                'formats_found': list(unique_formats),
                'examples': format_classifications
            }]

        return []

    def _classify_date_format(self, date_str: str) -> Optional[str]:
        """
        Classify the format type of a date string.

        Args:
            date_str: Date string to classify

        Returns:
            Format type identifier or None if unclassifiable
        """
        # Remove ongoing keywords for classification
        date_str_clean = date_str.lower()
        for keyword in self.ongoing_keywords:
            date_str_clean = date_str_clean.replace(keyword, '')

        # Remove separators (-, to, –, —) to get just the date parts
        date_str_clean = re.sub(r'\s*[-–—]\s*|\s+to\s+', ' ', date_str_clean)

        # Check for each format type
        # Priority: more specific formats first

        # DD Month YYYY or Month DD YYYY
        if self.patterns['day_month_year'].search(date_str):
            return 'day_month_year'

        # DD/MM/YYYY or DD-MM-YYYY
        if self.patterns['dd_mm_yyyy'].search(date_str):
            return 'dd_mm_yyyy'

        # Month YYYY or YYYY Month
        if self.patterns['month_year'].search(date_str):
            return 'month_year'

        # YYYY-MM or YYYY/MM
        if self.patterns['yyyy_mm'].search(date_str):
            return 'yyyy_mm'

        # MM/YYYY or MM-YYYY
        if self.patterns['mm_yyyy'].search(date_str):
            return 'mm_yyyy'

        # Year only (must be after other checks to avoid false positives)
        # Only classify as year_only if no other patterns match
        year_matches = self.patterns['year_only'].findall(date_str)
        if year_matches:
            # Check if this is truly year-only format
            # by ensuring no month indicators are present
            has_month_name = bool(re.search(
                r'jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec',
                date_str_clean
            ))
            has_month_number = bool(re.search(r'[-/]\d{2}', date_str_clean))

            if not has_month_name and not has_month_number:
                return 'year_only'

        return None


def create_scorer() -> DateFormattingScorer:
    """
    Factory function to create DateFormattingScorer instance.

    Returns:
        DateFormattingScorer instance
    """
    return DateFormattingScorer()
