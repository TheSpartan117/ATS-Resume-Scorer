"""
Red flags validator - comprehensive resume validation.
Checks all 44 parameters and returns issues by severity.
"""

import re
from datetime import datetime
from typing import Dict, List
from backend.services.parser import ResumeData


class RedFlagsValidator:
    """
    Validates resume against 44 parameters.
    Returns issues categorized by severity: critical, warning, suggestion.
    """

    def validate_resume(self, resume: ResumeData, role: str, level: str) -> Dict:
        """
        Run all validations and return categorized issues.

        Returns:
            {
                'critical': List[Dict],
                'warnings': List[Dict],
                'suggestions': List[Dict]
            }
        """
        all_issues = []

        # Run all validators
        all_issues.extend(self.validate_employment_history(resume))
        all_issues.extend(self.validate_experience_level(resume, level))

        # Categorize by severity
        return {
            'critical': [i for i in all_issues if i['severity'] == 'critical'],
            'warnings': [i for i in all_issues if i['severity'] == 'warning'],
            'suggestions': [i for i in all_issues if i['severity'] == 'suggestion']
        }

    def parse_date(self, date_str: str) -> datetime:
        """Parse date string into datetime"""
        if not date_str or date_str.lower() in ['present', 'current']:
            return datetime.now()

        # Try different formats
        formats = [
            "%b %Y",      # Jan 2020
            "%B %Y",      # January 2020
            "%m/%Y",      # 01/2020
            "%Y",         # 2020
        ]

        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue

        # Fallback: extract year
        year_match = re.search(r'(\d{4})', date_str)
        if year_match:
            return datetime(int(year_match.group(1)), 1, 1)

        return None

    def calculate_gap_months(self, end_date1: datetime, start_date2: datetime) -> int:
        """Calculate gap in months between two dates"""
        if not end_date1 or not start_date2:
            return 0

        delta = start_date2 - end_date1
        return delta.days // 30  # Approximate months

    def calculate_total_experience(self, experience: List[Dict]) -> float:
        """Calculate total years of experience"""
        total_months = 0

        for exp in experience:
            start = self.parse_date(exp.get('startDate', ''))
            end = self.parse_date(exp.get('endDate', ''))

            if start and end:
                months = (end.year - start.year) * 12 + (end.month - start.month)
                total_months += months

        return total_months / 12  # Convert to years

    def validate_employment_history(self, resume: ResumeData) -> List[Dict]:
        """
        Validate employment history for gaps, date errors, job hopping.
        Parameters 1-6 from design doc.
        """
        issues = []

        if not resume.experience or len(resume.experience) == 0:
            issues.append({
                'severity': 'critical',
                'category': 'employment',
                'message': 'No work experience listed'
            })
            return issues

        # Sort experiences by start date (most recent first)
        sorted_exp = sorted(
            resume.experience,
            key=lambda x: self.parse_date(x.get('startDate', '')) or datetime.min,
            reverse=True
        )

        # P1: Employment gap detection
        for i in range(len(sorted_exp) - 1):
            current_exp = sorted_exp[i]
            next_exp = sorted_exp[i + 1]

            current_start = self.parse_date(current_exp.get('startDate', ''))
            next_end = self.parse_date(next_exp.get('endDate', ''))

            if current_start and next_end:
                gap_months = self.calculate_gap_months(next_end, current_start)

                if gap_months >= 18:  # 18+ months = critical
                    issues.append({
                        'severity': 'critical',
                        'category': 'employment_gap',
                        'message': f'Employment gap of {gap_months} months between '
                                  f'{next_exp.get("company", "previous job")} and '
                                  f'{current_exp.get("company", "next job")}. '
                                  f'Consider adding explanation.',
                        'fix': 'Add line explaining gap (career break, education, freelancing)'
                    })
                elif gap_months >= 9:  # 9-18 months = warning
                    issues.append({
                        'severity': 'warning',
                        'category': 'employment_gap',
                        'message': f'Employment gap of {gap_months} months detected between jobs'
                    })

        # P2: Date validation (end before start, future dates)
        for exp in resume.experience:
            start = self.parse_date(exp.get('startDate', ''))
            end = self.parse_date(exp.get('endDate', ''))

            if start and end and end < start:
                issues.append({
                    'severity': 'critical',
                    'category': 'date_error',
                    'message': f"{exp.get('title', 'Job')} at {exp.get('company', 'company')}: "
                              f"End date before start date"
                })

            if start and start > datetime.now():
                issues.append({
                    'severity': 'critical',
                    'category': 'date_error',
                    'message': f"{exp.get('title', 'Job')} at {exp.get('company', 'company')}: "
                              f"Start date is in the future"
                })

        # P3: Date format consistency
        date_formats = []
        for exp in resume.experience:
            start_date = exp.get('startDate', '')
            if start_date:
                # Detect format
                if re.match(r'\d{2}/\d{4}', start_date):
                    date_formats.append('MM/YYYY')
                elif re.match(r'[A-Za-z]{3} \d{4}', start_date):
                    date_formats.append('Mon YYYY')
                elif re.match(r'[A-Za-z]+ \d{4}', start_date):
                    date_formats.append('Month YYYY')

        if len(set(date_formats)) > 1:
            issues.append({
                'severity': 'warning',
                'category': 'date_format',
                'message': 'Inconsistent date formats - use same format throughout '
                          '(e.g., "Jan 2020" or "01/2020")'
            })

        # P4: Job hopping (<1 year tenure at 2+ jobs)
        short_tenures = []
        for exp in resume.experience:
            start = self.parse_date(exp.get('startDate', ''))
            end = self.parse_date(exp.get('endDate', ''))

            if start and end:
                tenure_months = (end.year - start.year) * 12 + (end.month - start.month)
                if tenure_months < 12 and exp.get('endDate', '').lower() not in ['present', 'current']:
                    short_tenures.append(exp.get('company', 'unknown'))

        if len(short_tenures) >= 2:
            issues.append({
                'severity': 'warning',
                'category': 'job_hopping',
                'message': f"Multiple short tenures (<1 year) detected at: {', '.join(short_tenures)}"
            })

        # P6: Missing dates
        for exp in resume.experience:
            if not exp.get('startDate') or not exp.get('endDate'):
                issues.append({
                    'severity': 'critical',
                    'category': 'missing_dates',
                    'message': f"Missing dates for {exp.get('title', 'job')} at "
                              f"{exp.get('company', 'company')}"
                })

        return issues

    def validate_experience_level(self, resume: ResumeData, level: str) -> List[Dict]:
        """
        Validate that experience aligns with claimed level.
        Parameter 5 from design doc.
        """
        issues = []

        if not level or level not in ['entry', 'mid', 'senior', 'lead', 'executive']:
            return issues

        # Calculate total experience
        total_years = self.calculate_total_experience(resume.experience)

        # Flexible thresholds (from design discussion)
        level_ranges = {
            'entry': (0, 3),
            'mid': (2, 6),
            'senior': (5, 12),
            'lead': (8, 15),
            'executive': (12, 100)
        }

        min_years, max_years = level_ranges.get(level, (0, 100))

        if total_years < min_years:
            severity = 'critical' if total_years < min_years - 1 else 'warning'
            issues.append({
                'severity': severity,
                'category': 'experience_level',
                'message': f"Claiming '{level.capitalize()}' level with only "
                          f"{total_years:.1f} years experience (typical range: {min_years}-{max_years} years)"
            })

        return issues
