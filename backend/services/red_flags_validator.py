"""
Red flags validator - comprehensive resume validation.
Checks all 44 parameters and returns issues by severity.
"""

import re
from datetime import datetime
from typing import Dict, List, Optional
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
        all_issues.extend(self.validate_content_depth(resume))

        # Categorize by severity
        return {
            'critical': [i for i in all_issues if i['severity'] == 'critical'],
            'warnings': [i for i in all_issues if i['severity'] == 'warning'],
            'suggestions': [i for i in all_issues if i['severity'] == 'suggestion']
        }

    def parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date string into datetime, returns None if unparseable"""
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
        """Calculate gap in months between two dates using proper month arithmetic"""
        if not end_date1 or not start_date2:
            return 0

        # Calculate month difference accounting for day of month
        months = (start_date2.year - end_date1.year) * 12 + \
                 (start_date2.month - end_date1.month)

        # Adjust if we haven't reached the day in the target month
        if start_date2.day < end_date1.day:
            months -= 1

        return max(0, months)

    def calculate_total_experience(self, experience: List[Dict]) -> float:
        """Calculate total years of experience accounting for days"""
        total_months = 0

        for exp in experience:
            start = self.parse_date(exp.get('startDate', ''))
            end = self.parse_date(exp.get('endDate', ''))

            if start and end:
                months = (end.year - start.year) * 12 + (end.month - start.month)
                # Add partial month if we've passed the start day
                if end.day >= start.day:
                    months += 1
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

        # P2: Date validation (end before start, future dates, unparseable dates)
        for exp in resume.experience:
            start = self.parse_date(exp.get('startDate', ''))
            end = self.parse_date(exp.get('endDate', ''))

            # Check for unparseable dates
            start_date_str = exp.get('startDate', '')
            end_date_str = exp.get('endDate', '')

            if start_date_str and not start:
                issues.append({
                    'severity': 'critical',
                    'category': 'date_error',
                    'message': f"{exp.get('title', 'Job')} at {exp.get('company', 'company')}: "
                              f"Unable to parse start date '{start_date_str}'"
                })

            if end_date_str and not end and end_date_str.lower() not in ['present', 'current']:
                issues.append({
                    'severity': 'critical',
                    'category': 'date_error',
                    'message': f"{exp.get('title', 'Job')} at {exp.get('company', 'company')}: "
                              f"Unable to parse end date '{end_date_str}'"
                })

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
                # Add partial month if we've passed the start day
                if end.day >= start.day:
                    tenure_months += 1
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
            # Critical if significantly under-qualified (2+ years below minimum)
            # Warning if slightly under-qualified (1-2 years below minimum)
            # This buffer zone accounts for overlapping experience level ranges
            severity = 'critical' if total_years < min_years - 1 else 'warning'
            issues.append({
                'severity': severity,
                'category': 'experience_level',
                'message': f"Claiming '{level.capitalize()}' level with only "
                          f"{total_years:.1f} years experience (typical range: {min_years}-{max_years} years)"
            })

        return issues

    def validate_content_depth(self, resume: ResumeData) -> List[Dict]:
        """
        Validate content depth and quality of experience descriptions.
        Parameters 7-9 from design doc:
        - P7: Achievement Depth (vague phrases)
        - P8: Bullet Point Length (50-150 chars optimal)
        - P9: Bullet Structure (complete thoughts)
        """
        issues = []

        # P7: Vague phrases to detect
        vague_phrases = [
            r'\bresponsible for\b',
            r'\bworked on\b',
            r'\bhelped with\b',
            r'\bassisted with\b',
            r'\binvolved in\b',
            r'\bparticipated in\b'
        ]

        # P9: Weak verbs that indicate fragments
        weak_verbs = [r'\bwas\b', r'\bis\b', r'\bbeen\b', r'\bhas been\b', r'\bhave been\b']

        if not resume.experience:
            return issues

        for exp in resume.experience:
            company = exp.get('company', 'company')
            title = exp.get('title', 'position')
            description = exp.get('description', '')

            if not description:
                continue

            # Parse bullets from description
            bullets = self._parse_bullets(description)

            for bullet in bullets:
                bullet_text = bullet.strip()
                if not bullet_text:
                    continue

                # P7: Check for vague phrases
                for phrase_pattern in vague_phrases:
                    if re.search(phrase_pattern, bullet_text, re.IGNORECASE):
                        phrase_match = re.search(phrase_pattern, bullet_text, re.IGNORECASE)
                        phrase = phrase_match.group(0) if phrase_match else 'vague phrase'
                        issues.append({
                            'severity': 'warning',
                            'category': 'achievement_depth',
                            'message': f"{title} at {company}: Vague phrase detected '{phrase}'. "
                                      f"Use specific achievements with metrics instead."
                        })
                        break  # Only report once per bullet

                # P8: Check bullet length
                bullet_length = len(bullet_text)

                if bullet_length < 30:
                    issues.append({
                        'severity': 'critical',
                        'category': 'bullet_length',
                        'message': f"{title} at {company}: Bullet too short ({bullet_length} chars). "
                                  f"Minimum 30 characters recommended."
                    })
                elif bullet_length < 50:
                    issues.append({
                        'severity': 'warning',
                        'category': 'bullet_length',
                        'message': f"{title} at {company}: Bullet could be more detailed ({bullet_length} chars). "
                                  f"Aim for 50-150 characters."
                    })
                elif bullet_length > 200:
                    issues.append({
                        'severity': 'critical',
                        'category': 'bullet_length',
                        'message': f"{title} at {company}: Bullet too long ({bullet_length} chars). "
                                  f"Maximum 200 characters recommended."
                    })
                elif bullet_length > 150:
                    issues.append({
                        'severity': 'warning',
                        'category': 'bullet_length',
                        'message': f"{title} at {company}: Bullet could be more concise ({bullet_length} chars). "
                                  f"Aim for 50-150 characters."
                    })

                # P9: Check for fragments (less than 3 words)
                word_count = len(bullet_text.split())
                if word_count < 3:
                    issues.append({
                        'severity': 'warning',
                        'category': 'bullet_structure',
                        'message': f"{title} at {company}: Incomplete bullet (fragment). "
                                  f"Use complete thoughts with action verb + object."
                    })
                    continue  # Skip weak verb check for very short bullets

                # P9: Check for weak verbs at start of bullet
                for weak_verb_pattern in weak_verbs:
                    # Check if bullet starts with weak verb (after bullet marker)
                    if re.match(r'^[•\-*\d.)\s]*' + weak_verb_pattern, bullet_text, re.IGNORECASE):
                        issues.append({
                            'severity': 'warning',
                            'category': 'bullet_structure',
                            'message': f"{title} at {company}: Weak verb detected. "
                                      f"Start with strong action verbs (built, developed, achieved)."
                        })
                        break  # Only report once per bullet

        return issues

    def _parse_bullets(self, description: str) -> List[str]:
        """
        Parse bullet points from experience description.

        Args:
            description: Raw description text with bullets

        Returns:
            List of individual bullet point texts
        """
        if not description:
            return []

        # Split by common bullet markers
        # Matches: •, -, *, or numbered lists (1., 2.), or newlines
        lines = description.split('\n')
        bullets = []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Remove bullet markers at start: •, -, *, numbers followed by . or )
            cleaned = re.sub(r'^[•\-*\d.)\s]+', '', line).strip()
            if cleaned:
                bullets.append(cleaned)

        return bullets
