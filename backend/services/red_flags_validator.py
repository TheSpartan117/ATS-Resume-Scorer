"""
Red flags validator - comprehensive resume validation.
Checks all 44 parameters and returns issues by severity.
"""

import re
import hashlib
from datetime import datetime
from typing import Dict, List, Optional
from backend.services.parser import ResumeData

try:
    import language_tool_python
    LANGUAGE_TOOL_AVAILABLE = True
except ImportError:
    LANGUAGE_TOOL_AVAILABLE = False


class RedFlagsValidator:
    """
    Validates resume against 44 parameters.
    Returns issues categorized by severity: critical, warning, suggestion.
    """

    def __init__(self):
        """Initialize validator with grammar checker support"""
        self._language_tool = None
        self._lt_init_failed = False
        self._grammar_cache = {}  # Cache grammar results by text hash

    def _get_language_tool(self):
        """Get or initialize LanguageTool instance"""
        if self._lt_init_failed:
            return None

        if self._language_tool is None and LANGUAGE_TOOL_AVAILABLE:
            try:
                self._language_tool = language_tool_python.LanguageTool('en-US')
            except Exception:
                # If initialization fails, mark it and don't try again
                self._lt_init_failed = True
                return None

        return self._language_tool

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
        all_issues.extend(self.validate_section_completeness(resume))
        all_issues.extend(self.validate_professional_standards(resume))
        all_issues.extend(self.validate_grammar(resume))
        all_issues.extend(self.validate_metadata(resume))
        all_issues.extend(self.validate_content_analysis(resume))

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

    def validate_section_completeness(self, resume: ResumeData) -> List[Dict]:
        """
        Validate section completeness and ordering.
        Parameters 10-13 from design doc:
        - P10: Required Sections (Experience, Education, Skills)
        - P11: Section Ordering (Experience before Education for 2+ years exp)
        - P12: Recency Check (Most recent role within 2 years)
        - P13: Summary/Objective presence
        """
        issues = []

        # P10: Check required sections
        if not resume.experience or len(resume.experience) == 0:
            issues.append({
                'severity': 'critical',
                'category': 'required_section',
                'message': 'Required section missing: Experience. All resumes must include work experience.'
            })

        if not resume.education or len(resume.education) == 0:
            issues.append({
                'severity': 'critical',
                'category': 'required_section',
                'message': 'Required section missing: Education. All resumes must include educational background.'
            })

        if not resume.skills or len(resume.skills) == 0:
            issues.append({
                'severity': 'critical',
                'category': 'required_section',
                'message': 'Required section missing: Skills. List relevant technical and professional skills.'
            })

        # P12: Recency check - most recent role should be within 2 years
        if resume.experience and len(resume.experience) > 0:
            # Find most recent role by end date
            most_recent_role = None
            most_recent_end_date = None

            for exp in resume.experience:
                end_date = self.parse_date(exp.get('endDate', ''))
                if end_date:
                    if not most_recent_end_date or end_date > most_recent_end_date:
                        most_recent_end_date = end_date
                        most_recent_role = exp

            if most_recent_end_date:
                # Calculate months since most recent role ended
                now = datetime.now()
                months_since = (now.year - most_recent_end_date.year) * 12 + \
                              (now.month - most_recent_end_date.month)

                # Only flag if role ended >2 years ago (24 months)
                # Don't flag if role is current (Present/Current)
                if months_since > 24:
                    end_date_str = most_recent_role.get('endDate', '')
                    if end_date_str.lower() not in ['present', 'current']:
                        issues.append({
                            'severity': 'warning',
                            'category': 'recency',
                            'message': f'Most recent role ended more than 2 years ago '
                                      f'({most_recent_role.get("title", "position")} at '
                                      f'{most_recent_role.get("company", "company")}). '
                                      f'Consider adding recent experience or explaining career break.'
                        })

        # P13: Summary/Objective presence (suggestion)
        has_summary = False
        if resume.contact:
            # Check if contact has summary, objective, or profile fields
            summary_fields = ['summary', 'objective', 'profile', 'about']
            for field in summary_fields:
                if field in resume.contact and resume.contact[field]:
                    # Check if it's not empty or just whitespace
                    summary_text = str(resume.contact[field]).strip()
                    if len(summary_text) > 10:  # At least 10 chars to be meaningful
                        has_summary = True
                        break

        if not has_summary:
            issues.append({
                'severity': 'suggestion',
                'category': 'summary',
                'message': 'Consider adding a professional summary or objective statement '
                          'at the top of your resume to highlight key qualifications.'
            })

        # P11: Section ordering - Note: Current data structure doesn't preserve section order
        # This would require parser to track section positions in raw document
        # Leaving as future enhancement when parser is updated with section metadata

        return issues

    def validate_professional_standards(self, resume: ResumeData) -> List[Dict]:
        """
        Validate professional standards for contact information.
        Parameters 14-17 from design doc:
        - P14: Email Professionalism (format, provider, characters)
        - P15: LinkedIn URL Validation (format, presence)
        - P16: Phone Format Consistency
        - P17: Location Format (City, State/Country)
        """
        issues = []

        if not resume.contact:
            # No contact info - just flag missing LinkedIn
            issues.append({
                'severity': 'suggestion',
                'category': 'linkedin',
                'message': 'Consider adding LinkedIn profile URL to enhance professional presence'
            })
            return issues

        contact = resume.contact

        # P14: Email professionalism
        email = contact.get('email', '')
        if email:
            # Check for outdated email providers
            outdated_providers = ['aol.com', 'yahoo.com', 'hotmail.com']
            email_lower = email.lower()

            for provider in outdated_providers:
                if provider in email_lower:
                    issues.append({
                        'severity': 'warning',
                        'category': 'email_professionalism',
                        'message': f'Email uses outdated provider ({provider}). '
                                  f'Consider using Gmail or a professional domain email.'
                    })
                    break

            # Extract username part (before @)
            if '@' in email:
                username = email.split('@')[0]

                # Check for numbers
                if re.search(r'\d', username):
                    issues.append({
                        'severity': 'warning',
                        'category': 'email_professionalism',
                        'message': 'Email contains numbers. Use professional format like firstname.lastname@domain.com'
                    })

                # Check for underscores
                if '_' in username:
                    issues.append({
                        'severity': 'warning',
                        'category': 'email_professionalism',
                        'message': 'Email contains underscores. Use professional format like firstname.lastname@domain.com'
                    })

        # P15: LinkedIn URL validation
        linkedin = contact.get('linkedin', '')
        if not linkedin:
            issues.append({
                'severity': 'suggestion',
                'category': 'linkedin',
                'message': 'Consider adding LinkedIn profile URL to enhance professional presence'
            })
        elif linkedin:
            # Check if it's a company page (not personal profile)
            if '/company/' in linkedin.lower():
                issues.append({
                    'severity': 'warning',
                    'category': 'linkedin',
                    'message': 'LinkedIn URL appears to be a company page, not a personal profile. '
                              'Use format: linkedin.com/in/username'
                })
            # Check for proper format (linkedin.com/in/username)
            elif not re.search(r'linkedin\.com/in/[\w-]+', linkedin, re.IGNORECASE):
                # Allow "LinkedIn (see resume)" type placeholder
                if 'linkedin' in linkedin.lower() and 'see resume' not in linkedin.lower():
                    issues.append({
                        'severity': 'warning',
                        'category': 'linkedin',
                        'message': 'LinkedIn URL format should be: linkedin.com/in/username'
                    })

        # P16: Phone format consistency
        phone = contact.get('phone', '')
        if phone:
            # Detect phone format in contact
            contact_phone_formats = self._detect_phone_formats([phone])

            # Check for phone numbers in experience descriptions
            experience_phones = []
            if resume.experience:
                for exp in resume.experience:
                    description = exp.get('description', '')
                    if description:
                        # Look for phone numbers in description
                        phone_patterns = [
                            r'\+?1?\s*\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}',
                            r'\+?\d{1,3}[\s.-]?\d{3}[\s.-]?\d{3}[\s.-]?\d{4}',
                        ]
                        for pattern in phone_patterns:
                            matches = re.findall(pattern, description)
                            experience_phones.extend(matches)

            # Check consistency if we found phones in experience
            if experience_phones:
                exp_phone_formats = self._detect_phone_formats(experience_phones)
                all_formats = contact_phone_formats + exp_phone_formats

                if len(set(all_formats)) > 1:
                    issues.append({
                        'severity': 'warning',
                        'category': 'phone_format',
                        'message': 'Phone number format is inconsistent throughout resume. '
                                  'Use same format everywhere (e.g., "123-456-7890")'
                    })

        # P17: Location format validation
        location = contact.get('location', '')
        if location:
            # Check for proper "City, State" or "City, Country" format
            # Should have a comma separating city from state/country
            if ',' not in location:
                issues.append({
                    'severity': 'warning',
                    'category': 'location_format',
                    'message': 'Location should use format "City, State" or "City, Country" '
                              '(e.g., "San Francisco, CA" or "Mumbai, India")'
                })
            else:
                # Check if format looks reasonable (has 2 parts)
                parts = [p.strip() for p in location.split(',')]
                if len(parts) < 2 or not parts[0] or not parts[1]:
                    issues.append({
                        'severity': 'warning',
                        'category': 'location_format',
                        'message': 'Location format appears incomplete. Use "City, State" or "City, Country"'
                    })

        return issues

    def _detect_phone_formats(self, phone_numbers: List[str]) -> List[str]:
        """
        Detect phone number formats from a list of phone numbers.

        Returns list of format identifiers:
        - 'dashes': 123-456-7890
        - 'parens': (123) 456-7890
        - 'dots': 123.456.7890
        - 'spaces': 123 456 7890
        - 'mixed': Mixed format
        """
        formats = []

        for phone in phone_numbers:
            if not phone:
                continue

            # Detect format based on separators
            if '(' in phone and ')' in phone:
                formats.append('parens')
            elif '-' in phone:
                formats.append('dashes')
            elif '.' in phone:
                formats.append('dots')
            elif ' ' in phone.strip() and '(' not in phone:
                formats.append('spaces')
            else:
                formats.append('other')

        return formats

    def validate_grammar(self, resume: ResumeData) -> List[Dict]:
        """
        Validate grammar, spelling, and capitalization in resume text.
        Parameters 18-21 from design doc:
        - P18: Typo Detection (using LanguageTool)
        - P19: Grammar Errors (sentence structure, agreement)
        - P20: Verb Tense Consistency (checked via grammar)
        - P21: Capitalization (proper nouns, job titles)
        """
        issues = []

        # Check if LanguageTool is available
        lt = self._get_language_tool()
        if lt is None:
            return []  # Return empty list if LanguageTool unavailable

        # Collect all text sections to check
        text_sections = []

        # Check summary/objective
        if resume.contact:
            summary_fields = ['summary', 'objective', 'profile', 'about']
            for field in summary_fields:
                if field in resume.contact and resume.contact[field]:
                    text = str(resume.contact[field]).strip()
                    if text:
                        text_sections.append({
                            'text': text,
                            'section': 'summary',
                            'context': 'Professional summary'
                        })

        # Check experience descriptions
        if resume.experience:
            for exp in resume.experience:
                description = exp.get('description', '')
                if description:
                    # Parse bullets to check each one
                    bullets = self._parse_bullets(description)
                    for bullet in bullets:
                        bullet_text = bullet.strip()
                        if bullet_text and len(bullet_text) > 10:  # Only check substantial bullets
                            text_sections.append({
                                'text': bullet_text,
                                'section': 'experience',
                                'context': f"{exp.get('title', 'Position')} at {exp.get('company', 'company')}"
                            })

        # Check education descriptions/degrees
        if resume.education:
            for edu in resume.education:
                degree = edu.get('degree', '')
                if degree and len(degree) > 5:
                    text_sections.append({
                        'text': degree,
                        'section': 'education',
                        'context': f"Education: {edu.get('institution', 'institution')}"
                    })

                # Check education description if present
                description = edu.get('description', '')
                if description:
                    text_sections.append({
                        'text': description,
                        'section': 'education',
                        'context': f"Education: {edu.get('institution', 'institution')}"
                    })

        # Check each text section for grammar issues
        issue_counts = {'typo': 0, 'grammar': 0, 'capitalization': 0}
        max_per_category = 10  # Limit issues to avoid spam

        for section in text_sections:
            text = section['text']
            section_name = section['section']
            context = section['context']

            # Check cache first
            text_hash = hashlib.md5(text.encode()).hexdigest()
            if text_hash in self._grammar_cache:
                matches = self._grammar_cache[text_hash]
            else:
                # Check grammar with LanguageTool
                try:
                    matches = lt.check(text)
                    self._grammar_cache[text_hash] = matches
                except Exception:
                    continue  # Skip this text if check fails

            # Process matches and categorize
            for match in matches:
                # Map LanguageTool rule types to our categories
                rule_id = match.ruleId
                rule_category = match.category.upper() if hasattr(match, 'category') else ''

                # Determine category and severity
                category = None
                severity = None

                # P18: Typo detection (MISSPELLING)
                if 'TYPO' in rule_category or 'SPELL' in rule_category or rule_id.startswith('MORFOLOGIK'):
                    category = 'typo'
                    severity = 'warning'
                # P21: Capitalization (CASING)
                elif 'CASING' in rule_category or 'UPPERCASE' in rule_id or 'LOWERCASE' in rule_id:
                    category = 'capitalization'
                    severity = 'suggestion'
                # P19: Grammar errors (GRAMMAR, agreement, etc.)
                elif 'GRAMMAR' in rule_category or 'AGREEMENT' in rule_id or 'VERB' in rule_category:
                    category = 'grammar'
                    severity = 'warning'
                # Default to grammar for other issues
                else:
                    category = 'grammar'
                    severity = 'warning'

                # Check if we've hit the limit for this category
                if issue_counts[category] >= max_per_category:
                    continue

                # Extract error context
                error_text = text[match.offset:match.offset + match.errorLength]
                suggestion = match.replacements[0] if match.replacements else None

                # Build message
                message = f"{context}: {match.message}"
                if error_text:
                    message += f" ('{error_text}')"
                if suggestion:
                    message += f" - Suggestion: '{suggestion}'"

                issues.append({
                    'severity': severity,
                    'category': category,
                    'message': message,
                    'section': section_name
                })

                issue_counts[category] += 1

        return issues

    def validate_metadata(self, resume: ResumeData) -> List[Dict]:
        """
        Validate metadata and document quality.
        Parameters 36-44 from design doc:
        - P36: Page Count (1-2 pages optimal)
        - P37: Word Count (400-800 optimal)
        - P38: File Format (PDF preferred)
        - P39: File Size (<2MB recommended) - Note: Not available in metadata
        - P40: Readability Score (Flesch-Kincaid)
        - P41: Keyword Density (not over-stuffed)
        - P42: Section Balance (experience should be 50-60% of content)
        - P43: White Space (adequate margins/spacing) - Note: Difficult to assess from parsed data
        - P44: ATS Compatibility (no images/tables blocking parsing)
        """
        issues = []

        if not resume.metadata:
            return issues

        metadata = resume.metadata

        # P36: Page Count validation
        page_count = metadata.get('pageCount', 0)
        if page_count > 4:
            issues.append({
                'severity': 'critical',
                'category': 'page_count',
                'message': f'Resume is {page_count} pages long. Optimal length is 1-2 pages. '
                          f'Consider condensing to most relevant experience.'
            })
        elif page_count > 3:
            issues.append({
                'severity': 'warning',
                'category': 'page_count',
                'message': f'Resume is {page_count} pages long. Optimal length is 1-2 pages. '
                          f'Recruiters prefer concise resumes.'
            })
        elif page_count < 1:
            issues.append({
                'severity': 'critical',
                'category': 'page_count',
                'message': 'Resume appears to have no content or failed to parse properly.'
            })

        # P37: Word Count validation
        word_count = metadata.get('wordCount', 0)
        if word_count < 300:
            issues.append({
                'severity': 'warning',
                'category': 'word_count',
                'message': f'Resume has only {word_count} words. Optimal range is 400-800 words. '
                          f'Add more detail to experience and achievements.'
            })
        elif word_count > 1200:
            issues.append({
                'severity': 'warning',
                'category': 'word_count',
                'message': f'Resume has {word_count} words. Optimal range is 400-800 words. '
                          f'Consider being more concise and removing less relevant details.'
            })
        elif word_count < 400:
            issues.append({
                'severity': 'suggestion',
                'category': 'word_count',
                'message': f'Resume has {word_count} words. Consider adding more detail to reach optimal range of 400-800 words.'
            })
        elif word_count > 800:
            issues.append({
                'severity': 'suggestion',
                'category': 'word_count',
                'message': f'Resume has {word_count} words. Consider condensing to optimal range of 400-800 words.'
            })

        # P38: File Format validation
        file_format = metadata.get('fileFormat', '').lower()
        if file_format in ['doc', 'docx']:
            issues.append({
                'severity': 'warning',
                'category': 'file_format',
                'message': 'Resume is in Word format. PDF is preferred for better ATS compatibility '
                          'and consistent formatting across systems.'
            })
        elif file_format not in ['pdf', 'doc', 'docx']:
            issues.append({
                'severity': 'critical',
                'category': 'file_format',
                'message': f'Unsupported file format: {file_format}. Use PDF or DOCX format.'
            })

        # P40: Readability Score (Flesch-Kincaid grade level)
        readability_score = self._calculate_readability(resume)
        if readability_score is not None:
            if readability_score < 8:
                issues.append({
                    'severity': 'suggestion',
                    'category': 'readability',
                    'message': f'Readability score is {readability_score:.1f} grade level (too simple). '
                              f'Aim for 8-12 grade level to demonstrate professional communication.'
                })
            elif readability_score > 14:
                issues.append({
                    'severity': 'warning',
                    'category': 'readability',
                    'message': f'Readability score is {readability_score:.1f} grade level (too complex). '
                              f'Aim for 8-12 grade level for better clarity.'
                })
            elif readability_score > 12:
                issues.append({
                    'severity': 'suggestion',
                    'category': 'readability',
                    'message': f'Readability score is {readability_score:.1f} grade level. '
                              f'Consider simplifying slightly to 8-12 grade level range.'
                })

        # P41: Keyword Density (check for over-stuffing)
        keyword_issues = self._check_keyword_density(resume)
        issues.extend(keyword_issues)

        # P42: Section Balance (experience should be 50-60% of content)
        balance_issues = self._check_section_balance(resume)
        issues.extend(balance_issues)

        # P44: ATS Compatibility
        ats_issues = self._check_ats_compatibility(resume, metadata)
        issues.extend(ats_issues)

        return issues

    def _calculate_readability(self, resume: ResumeData) -> Optional[float]:
        """
        Calculate Flesch-Kincaid grade level for resume text.
        Returns None if calculation fails.
        """
        try:
            # Collect all text from resume
            text_parts = []

            # Add experience descriptions
            if resume.experience:
                for exp in resume.experience:
                    description = exp.get('description', '')
                    if description:
                        text_parts.append(description)

            # Add summary/objective
            if resume.contact:
                for field in ['summary', 'objective', 'profile', 'about']:
                    if field in resume.contact and resume.contact[field]:
                        text_parts.append(str(resume.contact[field]))

            # Add education descriptions
            if resume.education:
                for edu in resume.education:
                    description = edu.get('description', '')
                    if description:
                        text_parts.append(description)

            if not text_parts:
                return None

            full_text = ' '.join(text_parts)

            # Calculate Flesch-Kincaid grade level
            # Formula: 0.39 * (words/sentences) + 11.8 * (syllables/words) - 15.59
            sentences = self._count_sentences(full_text)
            words = len(full_text.split())
            syllables = self._count_syllables(full_text)

            if sentences == 0 or words == 0:
                return None

            grade_level = 0.39 * (words / sentences) + 11.8 * (syllables / words) - 15.59
            return max(0, grade_level)  # Can't be negative

        except Exception:
            return None

    def _count_sentences(self, text: str) -> int:
        """Count sentences in text"""
        # Split by sentence endings
        sentences = re.split(r'[.!?]+', text)
        # Filter out empty strings and very short fragments
        sentences = [s for s in sentences if len(s.strip()) > 10]
        return max(1, len(sentences))  # At least 1 sentence

    def _count_syllables(self, text: str) -> int:
        """
        Estimate syllable count using vowel groups.
        This is an approximation but works well for English.
        """
        text = text.lower()
        syllables = 0
        words = text.split()

        for word in words:
            # Remove non-alphabetic characters
            word = re.sub(r'[^a-z]', '', word)
            if len(word) == 0:
                continue

            # Count vowel groups
            vowel_groups = re.findall(r'[aeiouy]+', word)
            syllable_count = len(vowel_groups)

            # Adjust for silent 'e' at end
            if word.endswith('e') and syllable_count > 1:
                syllable_count -= 1

            # Every word has at least 1 syllable
            syllables += max(1, syllable_count)

        return syllables

    def _check_keyword_density(self, resume: ResumeData) -> List[Dict]:
        """
        Check for keyword over-stuffing.
        Warns if same keywords appear too frequently.
        """
        issues = []

        # Collect all text
        text_parts = []
        if resume.experience:
            for exp in resume.experience:
                description = exp.get('description', '')
                if description:
                    text_parts.append(description)

        if resume.contact:
            for field in ['summary', 'objective', 'profile', 'about']:
                if field in resume.contact and resume.contact[field]:
                    text_parts.append(str(resume.contact[field]))

        if not text_parts:
            return issues

        full_text = ' '.join(text_parts).lower()
        words = re.findall(r'\b[a-z]{3,}\b', full_text)  # Words 3+ chars

        if len(words) == 0:
            return issues

        # Count word frequencies
        word_counts = {}
        for word in words:
            # Skip common words
            if word in ['the', 'and', 'for', 'with', 'from', 'have', 'this', 'that', 'was', 'are', 'been']:
                continue
            word_counts[word] = word_counts.get(word, 0) + 1

        # Check for over-stuffing (word appears in >8% of text)
        total_words = len(words)
        for word, count in word_counts.items():
            density = count / total_words
            if density > 0.08:  # 8% threshold
                issues.append({
                    'severity': 'warning',
                    'category': 'keyword_density',
                    'message': f"Keyword '{word}' appears {count} times ({density*100:.1f}% of text). "
                              f"This may appear as keyword stuffing to ATS systems."
                })
            elif density > 0.06:  # 6% threshold
                issues.append({
                    'severity': 'suggestion',
                    'category': 'keyword_density',
                    'message': f"Keyword '{word}' appears {count} times ({density*100:.1f}% of text). "
                              f"Consider using synonyms to avoid repetition."
                })

        return issues

    def _check_section_balance(self, resume: ResumeData) -> List[Dict]:
        """
        Check if experience section takes appropriate portion of resume.
        Experience should be 50-60% of total content.
        """
        issues = []

        # Count words in each section
        experience_words = 0
        if resume.experience:
            for exp in resume.experience:
                description = exp.get('description', '')
                if description:
                    experience_words += len(description.split())
                # Count title and company
                experience_words += len(exp.get('title', '').split())
                experience_words += len(exp.get('company', '').split())

        education_words = 0
        if resume.education:
            for edu in resume.education:
                education_words += len(edu.get('degree', '').split())
                education_words += len(edu.get('institution', '').split())
                description = edu.get('description', '')
                if description:
                    education_words += len(description.split())

        skills_words = 0
        if resume.skills:
            skills_words = sum(len(skill.split()) for skill in resume.skills)

        summary_words = 0
        if resume.contact:
            for field in ['summary', 'objective', 'profile', 'about']:
                if field in resume.contact and resume.contact[field]:
                    summary_words += len(str(resume.contact[field]).split())

        total_words = experience_words + education_words + skills_words + summary_words

        if total_words == 0:
            return issues

        experience_percentage = (experience_words / total_words) * 100

        if experience_percentage < 40:
            issues.append({
                'severity': 'warning',
                'category': 'section_balance',
                'message': f'Experience section is only {experience_percentage:.0f}% of resume content. '
                          f'Optimal range is 50-60%. Add more detail to work experience.'
            })
        elif experience_percentage < 50:
            issues.append({
                'severity': 'suggestion',
                'category': 'section_balance',
                'message': f'Experience section is {experience_percentage:.0f}% of resume content. '
                          f'Consider expanding to 50-60% range.'
            })
        elif experience_percentage > 70:
            issues.append({
                'severity': 'warning',
                'category': 'section_balance',
                'message': f'Experience section is {experience_percentage:.0f}% of resume content. '
                          f'Optimal range is 50-60%. Balance with other sections like skills and education.'
            })
        elif experience_percentage > 60:
            issues.append({
                'severity': 'suggestion',
                'category': 'section_balance',
                'message': f'Experience section is {experience_percentage:.0f}% of resume content. '
                          f'Consider condensing to 50-60% range.'
            })

        return issues

    def _check_ats_compatibility(self, resume: ResumeData, metadata: Dict) -> List[Dict]:
        """
        Check for ATS compatibility issues.
        Looks for signs that images, tables, or complex formatting may block parsing.
        """
        issues = []

        # Check if resume has photos (from metadata)
        has_photo = metadata.get('hasPhoto', False)
        if has_photo:
            issues.append({
                'severity': 'warning',
                'category': 'ats_compatibility',
                'message': 'Resume contains a photo. Many ATS systems cannot parse photos and they '
                          'may cause parsing errors. Consider removing photo for better ATS compatibility.'
            })

        # Check for very low word count relative to page count (indicates tables/graphics)
        page_count = metadata.get('pageCount', 1)
        word_count = metadata.get('wordCount', 0)

        if page_count > 0:
            words_per_page = word_count / page_count
            if words_per_page < 150:
                issues.append({
                    'severity': 'warning',
                    'category': 'ats_compatibility',
                    'message': f'Resume has very few words per page ({words_per_page:.0f} words/page). '
                              f'This suggests heavy use of tables, graphics, or formatting that may not '
                              f'parse well in ATS systems. Use simple text-based formatting.'
                })

        # Check for incomplete parsing (missing critical sections could indicate parsing failure)
        parsing_issues = []
        if not resume.experience or len(resume.experience) == 0:
            parsing_issues.append('experience')
        if not resume.contact or not resume.contact.get('name'):
            parsing_issues.append('contact info')
        if not resume.education or len(resume.education) == 0:
            parsing_issues.append('education')

        if len(parsing_issues) >= 2:
            issues.append({
                'severity': 'warning',
                'category': 'ats_compatibility',
                'message': f'Multiple sections appear to be missing or failed to parse: {", ".join(parsing_issues)}. '
                          f'This may indicate complex formatting that ATS systems cannot read. '
                          f'Use simple, standard section headings and avoid tables/text boxes.'
            })

        return issues
    def validate_content_analysis(self, resume: ResumeData) -> List[Dict]:
        """
        Validate content analysis for quality and professionalism.
        Parameters 26-35 from design doc:
        - P26: Action Verbs (% bullets starting with strong verbs)
        - P27: Quantified Achievements (% bullets with metrics)
        - P28: Passive Voice (count passive constructions)
        - P29: Professional Language (no first-person pronouns)
        - P30: Buzzword Density (empty buzzwords: synergy, rockstar, ninja)
        - P31: Skills Density (skills mentioned in experience)
        - P32: Keyword Context (keywords in achievement context)
        - P33: Sentence Structure (proper bullet length, no run-ons)
        - P34: First-Person Pronouns (should use third-person)
        - P35: Informal Language (avoid "stuff", "things", "lots of")
        """
        issues = []

        if not resume.experience or len(resume.experience) == 0:
            return issues

        # Collect all bullets from experience
        all_bullets = []
        for exp in resume.experience:
            description = exp.get('description', '')
            if description:
                bullets = self._parse_bullets(description)
                for bullet in bullets:
                    bullet_text = bullet.strip()
                    if bullet_text and len(bullet_text) > 3:
                        all_bullets.append({
                            'text': bullet_text,
                            'company': exp.get('company', 'company'),
                            'title': exp.get('title', 'position')
                        })

        if not all_bullets:
            return issues

        total_bullets = len(all_bullets)

        # P26: Action Verbs - Check if bullets start with strong action verbs
        strong_action_verbs = [
            'achieved', 'accelerated', 'accomplished', 'analyzed', 'architected',
            'built', 'created', 'designed', 'developed', 'drove', 'delivered',
            'engineered', 'enhanced', 'established', 'executed', 'generated',
            'implemented', 'improved', 'increased', 'launched', 'led', 'managed',
            'optimized', 'orchestrated', 'pioneered', 'reduced', 'resolved',
            'scaled', 'spearheaded', 'streamlined', 'transformed'
        ]

        action_verb_count = 0
        for bullet in all_bullets:
            text = bullet['text'].lower()
            # Check if bullet starts with strong action verb
            for verb in strong_action_verbs:
                if text.startswith(verb):
                    action_verb_count += 1
                    break

        action_verb_percentage = (action_verb_count / total_bullets) * 100

        if action_verb_percentage < 70:
            issues.append({
                'severity': 'critical',
                'category': 'action_verbs',
                'message': f'Only {action_verb_percentage:.0f}% of bullets start with strong action verbs. '
                          f'Aim for at least 90% (currently {action_verb_count}/{total_bullets}). '
                          f'Start bullets with: built, developed, achieved, led, etc.'
            })
        elif action_verb_percentage < 90:
            issues.append({
                'severity': 'warning',
                'category': 'action_verbs',
                'message': f'Only {action_verb_percentage:.0f}% of bullets start with strong action verbs. '
                          f'Aim for at least 90% (currently {action_verb_count}/{total_bullets}).'
            })

        # P27: Quantified Achievements - Check for metrics/numbers
        quantified_count = 0
        number_patterns = [
            r'\d+%',  # Percentages
            r'\d+[xX]',  # Multipliers (2x, 3X)
            r'\$\d+',  # Dollar amounts
            r'\d+\+',  # Numbers with plus (10+)
            r'\d+\s*(million|billion|thousand|k|m|b)',  # Large numbers
            r'\d+\s*(hours|days|weeks|months|years)',  # Time metrics
            r'\d+\s*(users|customers|clients|requests|transactions)',  # Count metrics
        ]

        for bullet in all_bullets:
            text = bullet['text']
            # Check if bullet contains any quantification
            has_metric = False
            for pattern in number_patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    has_metric = True
                    break
            if has_metric:
                quantified_count += 1

        quantified_percentage = (quantified_count / total_bullets) * 100

        if quantified_percentage < 40:
            issues.append({
                'severity': 'critical',
                'category': 'quantified_achievements',
                'message': f'Only {quantified_percentage:.0f}% of bullets include metrics. '
                          f'Aim for at least 60% (currently {quantified_count}/{total_bullets}). '
                          f'Add specific numbers, percentages, and measurable results.'
            })
        elif quantified_percentage < 60:
            issues.append({
                'severity': 'warning',
                'category': 'quantified_achievements',
                'message': f'Only {quantified_percentage:.0f}% of bullets include metrics. '
                          f'Aim for at least 60% (currently {quantified_count}/{total_bullets}).'
            })

        # P28: Passive Voice Detection
        passive_patterns = [
            r'\bwas\s+\w+ed\b',  # was completed, was developed
            r'\bwere\s+\w+ed\b',  # were implemented
            r'\bbeen\s+\w+ed\b',  # has been implemented
            r'\bis\s+being\s+\w+ed\b',  # is being developed
            r'\bhave\s+been\s+\w+ed\b',  # have been completed
            r'\bhas\s+been\s+\w+ed\b',  # has been developed
        ]

        passive_voice_count = 0
        passive_examples = []
        for bullet in all_bullets:
            text = bullet['text']
            for pattern in passive_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    passive_voice_count += len(matches)
                    if len(passive_examples) < 3:
                        passive_examples.append({
                            'text': text[:80] + '...' if len(text) > 80 else text,
                            'company': bullet['company']
                        })
                    break

        if passive_voice_count > 5:
            examples_str = '; '.join([f"{ex['company']}: {ex['text']}" for ex in passive_examples[:2]])
            issues.append({
                'severity': 'warning',
                'category': 'passive_voice',
                'message': f'Detected {passive_voice_count} instances of passive voice. '
                          f'Use active voice for stronger impact. Examples: {examples_str}'
            })

        # P29 & P34: First-Person Pronouns Detection
        first_person_pronouns = [
            r'\bI\b', r'\bmy\b', r'\bme\b', r'\bmine\b', r'\bmyself\b',
            r'\bwe\b', r'\bour\b', r'\bus\b', r'\bours\b', r'\bourselves\b'
        ]

        pronoun_count = 0
        pronoun_examples = []
        for bullet in all_bullets:
            text = bullet['text']
            for pattern in first_person_pronouns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    pronoun_count += len(matches)
                    if len(pronoun_examples) < 3:
                        pronoun_examples.append({
                            'text': text[:80] + '...' if len(text) > 80 else text,
                            'company': bullet['company'],
                            'pronoun': matches[0]
                        })

        if pronoun_count > 0:
            examples_str = '; '.join([f"{ex['company']}: '{ex['pronoun']}' in '{ex['text']}'"
                                     for ex in pronoun_examples[:2]])
            issues.append({
                'severity': 'warning',
                'category': 'first_person_pronouns',
                'message': f'Detected {pronoun_count} first-person pronouns. '
                          f'Use third-person for professional tone. Examples: {examples_str}'
            })

        # P30: Buzzword Density - Empty buzzwords to avoid
        buzzwords = [
            r'\bsynergy\b', r'\bsynergies\b', r'\brockstar\b', r'\bninja\b',
            r'\bguru\b', r'\bthought leader\b', r'\bworld-class\b',
            r'\bbest of breed\b', r'\bbest-in-class\b', r'\bgame changer\b',
            r'\bdisruptive\b', r'\binnovative\b(?!\s+solution)',  # innovative alone is vague
            r'\bgo-getter\b', r'\bself-starter\b', r'\bteam player\b',
            r'\bhard worker\b', r'\bresults-oriented\b', r'\bdetail-oriented\b'
        ]

        buzzword_count = 0
        buzzword_examples = []
        for bullet in all_bullets:
            text = bullet['text']
            for pattern in buzzwords:
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    buzzword_count += len(matches)
                    if len(buzzword_examples) < 3:
                        buzzword_examples.append({
                            'text': text[:80] + '...' if len(text) > 80 else text,
                            'company': bullet['company'],
                            'buzzword': matches[0]
                        })

        if buzzword_count > 3:
            examples_str = '; '.join([f"'{ex['buzzword']}'" for ex in buzzword_examples[:3]])
            issues.append({
                'severity': 'warning',
                'category': 'buzzword_density',
                'message': f'Detected {buzzword_count} empty buzzwords ({examples_str}). '
                          f'Replace with specific achievements and technical details.'
            })

        # P31: Skills Density - Check if skills are mentioned in experience context
        if resume.skills and len(resume.skills) > 0:
            skills_in_context = set()
            for skill in resume.skills:
                skill_lower = skill.lower()
                for bullet in all_bullets:
                    text = bullet['text'].lower()
                    if skill_lower in text:
                        skills_in_context.add(skill)
                        break

            skills_density_percentage = (len(skills_in_context) / len(resume.skills)) * 100

            if skills_density_percentage < 40:
                issues.append({
                    'severity': 'warning',
                    'category': 'skills_density',
                    'message': f'Only {skills_density_percentage:.0f}% of listed skills appear in experience descriptions '
                              f'({len(skills_in_context)}/{len(resume.skills)} skills). '
                              f'Demonstrate skills with concrete examples in bullet points.'
                })

            # P32: Keyword Context - Ensure keywords appear in achievement context
            # Check that technical skills/keywords are used with action verbs and metrics
            skills_with_context = set()
            for skill in resume.skills:
                skill_lower = skill.lower()
                for bullet in all_bullets:
                    text = bullet['text'].lower()
                    if skill_lower in text:
                        # Check if used with action verb or metric
                        has_context = False
                        for verb in strong_action_verbs:
                            if verb in text:
                                has_context = True
                                break
                        for pattern in number_patterns:
                            if re.search(pattern, text, re.IGNORECASE):
                                has_context = True
                                break
                        if has_context:
                            skills_with_context.add(skill)
                            break

            if skills_in_context and len(skills_in_context) > 0:
                context_percentage = (len(skills_with_context) / len(skills_in_context)) * 100
                if context_percentage < 60:
                    issues.append({
                        'severity': 'suggestion',
                        'category': 'keyword_context',
                        'message': f'Only {context_percentage:.0f}% of mentioned skills include achievement context '
                                  f'({len(skills_with_context)}/{len(skills_in_context)} skills). '
                                  f'Pair technical skills with action verbs and measurable results.'
                    })

        # P33: Sentence Structure - Check for run-on sentences
        # Run-on detection: sentences with multiple independent clauses without proper punctuation
        run_on_count = 0
        run_on_examples = []
        for bullet in all_bullets:
            text = bullet['text']
            # Count coordinating conjunctions without proper punctuation
            # Look for patterns like: "... and ... and ..." or very long sentences with multiple "and"
            and_count = len(re.findall(r'\band\b', text, re.IGNORECASE))
            comma_count = text.count(',')

            # If >2 "and" with few commas, likely run-on
            if and_count > 2 and comma_count < and_count - 1:
                run_on_count += 1
                if len(run_on_examples) < 2:
                    run_on_examples.append({
                        'text': text[:100] + '...' if len(text) > 100 else text,
                        'company': bullet['company']
                    })

        if run_on_count > 0:
            examples_str = '; '.join([f"{ex['company']}: {ex['text']}" for ex in run_on_examples[:2]])
            issues.append({
                'severity': 'suggestion',
                'category': 'sentence_structure',
                'message': f'Detected {run_on_count} potential run-on sentences. '
                          f'Break long sentences into multiple bullets. Examples: {examples_str}'
            })

        # P35: Informal Language Detection
        informal_phrases = [
            r'\bstuff\b', r'\bthings\b', r'\blots of\b', r'\ba lot of\b',
            r'\bkinda\b', r'\bsorta\b', r'\bgonna\b', r'\bwanna\b',
            r'\bpretty good\b', r'\breally\b', r'\bvery\b(?!\s+large|\s+high)',
            r'\bbasically\b', r'\bjust\b(?!\s+in\s+time)'
        ]

        informal_count = 0
        informal_examples = []
        for bullet in all_bullets:
            text = bullet['text']
            for pattern in informal_phrases:
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    informal_count += len(matches)
                    if len(informal_examples) < 3:
                        informal_examples.append({
                            'text': text[:80] + '...' if len(text) > 80 else text,
                            'company': bullet['company'],
                            'phrase': matches[0]
                        })

        if informal_count > 0:
            examples_str = '; '.join([f"'{ex['phrase']}'" for ex in informal_examples[:3]])
            issues.append({
                'severity': 'warning',
                'category': 'informal_language',
                'message': f'Detected {informal_count} instances of informal language ({examples_str}). '
                          f'Use professional, precise language.'
            })

        return issues

    def validate_formatting(self, resume: ResumeData) -> List[Dict]:
        """
        Validate formatting consistency and ATS-compatibility.
        Parameters 22-25 from design doc:
        - P22: Bullet Consistency (all bullets same marker)
        - P23: Font Readability (no decorative fonts that break ATS)
        - P24: Section Header Consistency (all CAPS or Title Case)
        - P25: Header/Footer Content (critical info shouldn't be there)
        """
        issues = []

        # P22: Bullet marker consistency across all experience
        if resume.experience:
            bullet_markers = []

            for exp in resume.experience:
                description = exp.get('description', '')
                if not description:
                    continue

                # Detect bullet markers used in this experience
                lines = description.split('\n')
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue

                    # Detect bullet marker type
                    if line.startswith('•'):
                        bullet_markers.append('bullet')
                    elif re.match(r'^\d+[\.)]\s', line):
                        bullet_markers.append('numbered')
                    elif line.startswith('-'):
                        bullet_markers.append('dash')
                    elif line.startswith('*'):
                        bullet_markers.append('asterisk')

            # Check for inconsistency
            unique_markers = set(bullet_markers)
            if len(unique_markers) > 1:
                marker_names = {
                    'bullet': '•',
                    'dash': '-',
                    'asterisk': '*',
                    'numbered': '1., 2., etc.'
                }
                used_markers = [marker_names.get(m, m) for m in unique_markers]
                issues.append({
                    'severity': 'warning',
                    'category': 'bullet_consistency',
                    'message': f'Inconsistent bullet markers used: {", ".join(used_markers)}. '
                              f'Use the same bullet style throughout (recommend •).'
                })

        # P23: Font detection from metadata (if available)
        if resume.metadata:
            fonts = resume.metadata.get('fonts', [])
            if fonts:
                # List of problematic decorative fonts
                decorative_fonts = [
                    'comic sans', 'papyrus', 'curlz', 'brush script',
                    'lucida handwriting', 'freestyle script', 'zapfino',
                    'mistral', 'vivaldi', 'edwardian script'
                ]

                # Check for decorative fonts
                font_names_lower = [f.lower() if isinstance(f, str) else '' for f in fonts]
                for decorative in decorative_fonts:
                    if any(decorative in font_name for font_name in font_names_lower):
                        issues.append({
                            'severity': 'critical',
                            'category': 'font_readability',
                            'message': f'Decorative font detected ({decorative}). '
                                      f'Use standard fonts like Arial, Calibri, or Times New Roman for ATS compatibility.'
                        })
                        break

                # Check for too many fonts (>2 is excessive)
                unique_fonts = set(fonts) if isinstance(fonts, list) else set()
                if len(unique_fonts) > 2:
                    issues.append({
                        'severity': 'warning',
                        'category': 'font_readability',
                        'message': f'Multiple fonts detected ({len(unique_fonts)} different fonts). '
                                  f'Use 1-2 standard fonts for consistency.'
                    })

        # P24: Section header consistency
        section_headers = []

        # Extract section headers from raw text if available
        if resume.metadata and 'rawText' in resume.metadata:
            raw_text = resume.metadata.get('rawText', '')
            lines = raw_text.split('\n')

            # Common section header keywords
            header_keywords = [
                'experience', 'education', 'skills', 'certifications',
                'work history', 'employment', 'professional experience',
                'technical skills', 'core competencies', 'projects',
                'achievements', 'summary', 'objective', 'profile'
            ]

            for line in lines:
                line_stripped = line.strip()
                line_lower = line_stripped.lower()

                # Check if line contains a section header keyword
                if any(keyword in line_lower for keyword in header_keywords):
                    # Check if it's likely a header (short line, not a sentence)
                    if len(line_stripped) < 50 and not line_stripped.endswith('.'):
                        section_headers.append(line_stripped)

        # Analyze header consistency
        if len(section_headers) >= 2:
            all_caps = []
            title_case = []
            other = []

            for header in section_headers:
                if header.isupper():
                    all_caps.append(header)
                elif header.istitle() or (header[0].isupper() and any(c.isupper() for c in header[1:])):
                    title_case.append(header)
                else:
                    other.append(header)

            # Check for inconsistency
            styles_used = sum([len(all_caps) > 0, len(title_case) > 0, len(other) > 0])
            if styles_used > 1:
                issues.append({
                    'severity': 'warning',
                    'category': 'header_consistency',
                    'message': 'Section headers use inconsistent capitalization. '
                              'Use either ALL CAPS or Title Case consistently for all headers.'
                })

        # P25: Header/Footer content check
        if resume.metadata:
            # Check for header content in metadata
            header_content = resume.metadata.get('headerContent', '')
            footer_content = resume.metadata.get('footerContent', '')

            # Critical contact info that shouldn't be in header/footer
            critical_patterns = [
                (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', 'email address'),
                (r'\+?1?\s*\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}', 'phone number'),
                (r'linkedin\.com/in/[\w-]+', 'LinkedIn URL')
            ]

            for content, location in [(header_content, 'header'), (footer_content, 'footer')]:
                if content:
                    for pattern, info_type in critical_patterns:
                        if re.search(pattern, content, re.IGNORECASE):
                            issues.append({
                                'severity': 'critical',
                                'category': 'header_footer_content',
                                'message': f'Critical contact information ({info_type}) detected in {location}. '
                                          f'ATS systems may not parse {location} content correctly. '
                                          f'Place all contact info in the main document body.'
                            })

        return issues
