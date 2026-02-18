"""
ATS Mode Scorer - Optimized for keyword matching and format compliance.

Scoring breakdown (100 points):
- Keywords (35 pts): Match against role keywords, strict thresholds
- Red Flags (20 pts): Critical issues from validator
- Experience (20 pts): Years, relevance, recency
- Formatting (20 pts): ATS-friendly format
- Contact Info (5 pts): Professional contact details
"""

from typing import Dict, List
from backend.services.parser import ResumeData
from backend.services.keyword_matcher import KeywordMatcher
from backend.services.red_flags_validator import RedFlagsValidator


class ATSScorer:
    """
    ATS Mode Scorer focusing on keyword matching and format compliance.
    Integrates with KeywordMatcher and RedFlagsValidator.
    """

    def __init__(self):
        """Initialize scorer with keyword matcher and validator"""
        self.keyword_matcher = KeywordMatcher()
        self.validator = RedFlagsValidator()

    def score(
        self,
        resume: ResumeData,
        role: str,
        level: str,
        job_description: str = ""
    ) -> Dict:
        """
        Score resume in ATS mode.

        Args:
            resume: Parsed resume data
            role: Role ID (e.g., "software_engineer")
            level: Experience level (e.g., "mid", "senior")
            job_description: Optional job description for keyword matching

        Returns:
            Dict with score and detailed breakdown
        """
        # Run all scoring components
        keywords_result = self._score_keywords(resume, role, level, job_description)
        red_flags_result = self._score_red_flags(resume, role, level)
        experience_result = self._score_experience(resume, level)
        formatting_result = self._score_formatting(resume)
        contact_result = self._score_contact_info(resume)

        # Calculate total score
        total_score = (
            keywords_result['score'] +
            red_flags_result['score'] +
            experience_result['score'] +
            formatting_result['score'] +
            contact_result['score']
        )

        return {
            'score': total_score,
            'breakdown': {
                'keywords': keywords_result,
                'red_flags': red_flags_result,
                'experience': experience_result,
                'formatting': formatting_result,
                'contact': contact_result
            }
        }

    def _score_keywords(
        self,
        resume: ResumeData,
        role: str,
        level: str,
        job_description: str = ""
    ) -> Dict:
        """
        Score keyword matching (35 points max).

        Strict thresholds from design:
        - 0-30% match = 0 pts
        - 31-50% match = 10 pts
        - 51-70% match = 25 pts
        - 71%+ match = 35 pts

        Args:
            resume: Parsed resume data
            role: Role ID
            level: Experience level
            job_description: Optional job description

        Returns:
            Dict with score and details
        """
        # Build resume text
        resume_text = self._build_resume_text(resume)

        # Match keywords
        if job_description:
            # Use job description for matching
            match_result = self.keyword_matcher.match_job_description(
                resume_text,
                job_description
            )
        else:
            # Use role-based keywords
            match_result = self.keyword_matcher.match_role_keywords(
                resume_text,
                role,
                level
            )

        # Get match percentage
        percentage = match_result.get('percentage', 0)
        matched = match_result.get('matched', [])
        missing = match_result.get('missing', [])

        # Apply strict thresholds
        if percentage >= 71:
            score = 35
            message = f"Excellent keyword match: {percentage:.0f}%"
        elif percentage >= 51:
            score = 25
            message = f"Good keyword match: {percentage:.0f}%"
        elif percentage >= 31:
            score = 10
            message = f"Moderate keyword match: {percentage:.0f}% - add more keywords"
        else:
            score = 0
            message = f"Poor keyword match: {percentage:.0f}% - critical for ATS"

        return {
            'score': score,
            'maxScore': 35,
            'details': {
                'percentage': percentage,
                'matched_count': len(matched),
                'missing_count': len(missing),
                'matched': matched[:10],  # Top 10 matched
                'missing': missing[:10],  # Top 10 missing
                'message': message
            }
        }

    def _score_red_flags(self, resume: ResumeData, role: str, level: str) -> Dict:
        """
        Score based on red flags validation (20 points max).

        Scoring:
        - 0 critical = 20 pts
        - 1-2 critical = 12 pts
        - 3-4 critical = 6 pts
        - 5+ critical = 0 pts
        - Each warning = -1 pt (max -5)

        Args:
            resume: Parsed resume data
            role: Role ID
            level: Experience level

        Returns:
            Dict with score and details
        """
        # Run validation
        validation_result = self.validator.validate_resume(resume, role, level)

        critical_issues = validation_result.get('critical', [])
        warning_issues = validation_result.get('warnings', [])
        suggestion_issues = validation_result.get('suggestions', [])

        # Calculate score based on critical issues
        critical_count = len(critical_issues)
        if critical_count == 0:
            score = 20
        elif critical_count <= 2:
            score = 12
        elif critical_count <= 4:
            score = 6
        else:
            score = 0

        # Deduct for warnings (max -5)
        warning_deduction = min(len(warning_issues), 5)
        score = max(0, score - warning_deduction)

        # Build message
        if critical_count == 0:
            message = "No critical issues detected"
        else:
            message = f"{critical_count} critical issue(s) found - major impact on ATS"

        return {
            'score': score,
            'maxScore': 20,
            'details': {
                'critical_count': critical_count,
                'warning_count': len(warning_issues),
                'suggestion_count': len(suggestion_issues),
                'critical_issues': [issue['message'] for issue in critical_issues[:5]],
                'warning_issues': [issue['message'] for issue in warning_issues[:5]],
                'message': message
            }
        }

    def _score_experience(self, resume: ResumeData, level: str) -> Dict:
        """
        Score experience alignment with level (20 points max).

        Scoring:
        - Total years match level = 10 pts
        - Recency (role within 6 months) = 5 pts
        - Relevance (proper descriptions) = 5 pts

        Args:
            resume: Parsed resume data
            level: Experience level

        Returns:
            Dict with score and details
        """
        score = 0
        details = {}

        # Calculate total experience
        total_years = self.validator.calculate_total_experience(resume.experience)
        details['total_years'] = round(total_years, 1)

        # Expected ranges from validator
        level_ranges = {
            'entry': (0, 3),
            'mid': (2, 6),
            'senior': (5, 12),
            'lead': (8, 15),
            'executive': (12, 100)
        }

        min_years, max_years = level_ranges.get(level, (0, 100))

        # Score total years (10 pts)
        if min_years <= total_years <= max_years:
            score += 10
            years_message = f"Experience matches {level} level ({total_years:.1f} years)"
        elif total_years < min_years:
            # Under-qualified
            gap = min_years - total_years
            if gap <= 1:
                score += 6
                years_message = f"Slightly under-qualified for {level} ({total_years:.1f} years)"
            else:
                score += 3
                years_message = f"Under-qualified for {level} ({total_years:.1f} years, need {min_years}+)"
        else:
            # Over-qualified
            score += 8
            years_message = f"Over-qualified for {level} ({total_years:.1f} years)"

        details['years_message'] = years_message

        # Score recency (5 pts)
        from datetime import datetime
        if resume.experience and len(resume.experience) > 0:
            # Find most recent role
            most_recent_end = None
            for exp in resume.experience:
                end_date = self.validator.parse_date(exp.get('endDate', ''))
                if end_date:
                    if not most_recent_end or end_date > most_recent_end:
                        most_recent_end = end_date

            if most_recent_end:
                now = datetime.now()
                months_since = (now.year - most_recent_end.year) * 12 + \
                              (now.month - most_recent_end.month)

                if months_since <= 6:  # Within 6 months
                    score += 5
                    recency_message = "Recent experience (within 6 months)"
                elif months_since <= 12:  # Within 1 year
                    score += 3
                    recency_message = "Fairly recent (within 1 year)"
                elif months_since <= 24:  # Within 2 years
                    score += 1
                    recency_message = "Experience within 2 years"
                else:
                    recency_message = f"Experience gap: {months_since} months since last role"

                details['recency_message'] = recency_message
                details['months_since_last_role'] = months_since
            else:
                details['recency_message'] = "Unable to determine recency"
        else:
            details['recency_message'] = "No experience listed"

        # Score relevance (5 pts)
        # Check if descriptions are present and substantial
        descriptions_count = 0
        substantial_descriptions = 0

        for exp in resume.experience:
            description = exp.get('description', '')
            if description:
                descriptions_count += 1
                if len(description) >= 50:  # Substantial description
                    substantial_descriptions += 1

        if len(resume.experience) > 0:
            relevance_ratio = substantial_descriptions / len(resume.experience)
            if relevance_ratio >= 0.8:
                score += 5
                relevance_message = "Strong experience descriptions"
            elif relevance_ratio >= 0.5:
                score += 3
                relevance_message = "Adequate experience descriptions"
            else:
                score += 1
                relevance_message = "Weak experience descriptions - add more detail"

            details['relevance_message'] = relevance_message
            details['descriptions_count'] = descriptions_count
        else:
            details['relevance_message'] = "No experience listed"

        return {
            'score': score,
            'maxScore': 20,
            'details': details
        }

    def _score_formatting(self, resume: ResumeData) -> Dict:
        """
        Score ATS-friendly formatting (20 points max).

        Scoring:
        - Page count (1-2 pages) = 8 pts
        - No photo = 4 pts
        - PDF format = 4 pts
        - Word count = 4 pts

        Args:
            resume: Parsed resume data

        Returns:
            Dict with score and details
        """
        score = 0
        metadata = resume.metadata
        details = {}

        # Page count (8 pts)
        page_count = metadata.get('pageCount', 0)
        details['page_count'] = page_count

        if page_count in [1, 2]:
            score += 8
            page_message = f"Optimal page count: {page_count}"
        elif page_count == 3:
            score += 4
            page_message = "3 pages - consider condensing to 2"
        else:
            score += 2
            page_message = f"{page_count} pages - should be 1-2 pages"

        details['page_message'] = page_message

        # Photo check (4 pts)
        has_photo = metadata.get('hasPhoto', False)
        if not has_photo:
            score += 4
            photo_message = "No photo (ATS-friendly)"
        else:
            photo_message = "Contains photo - remove for ATS compatibility"

        details['has_photo'] = has_photo
        details['photo_message'] = photo_message

        # File format (4 pts)
        file_format = metadata.get('fileFormat', '').lower()
        details['file_format'] = file_format

        if file_format == 'pdf':
            score += 4
            format_message = "PDF format (optimal for ATS)"
        elif file_format == 'docx':
            score += 3
            format_message = "DOCX format (acceptable)"
        else:
            score += 1
            format_message = f"Unusual format: {file_format}"

        details['format_message'] = format_message

        # Word count (4 pts)
        word_count = metadata.get('wordCount', 0)
        details['word_count'] = word_count

        if 300 <= word_count <= 800:
            score += 4
            word_message = f"Optimal word count: {word_count}"
        elif 200 <= word_count < 300 or 800 < word_count <= 1000:
            score += 2
            if word_count < 300:
                word_message = f"Brief ({word_count} words) - add more detail"
            else:
                word_message = f"Lengthy ({word_count} words) - be more concise"
        else:
            score += 1
            if word_count < 200:
                word_message = f"Too brief: {word_count} words"
            else:
                word_message = f"Too lengthy: {word_count} words"

        details['word_message'] = word_message

        return {
            'score': score,
            'maxScore': 20,
            'details': details
        }

    def _score_contact_info(self, resume: ResumeData) -> Dict:
        """
        Score contact information completeness (5 points max).

        Scoring:
        - Name = 1 pt
        - Email = 1 pt
        - Phone = 1 pt
        - Location = 1 pt
        - LinkedIn = 1 pt

        Args:
            resume: Parsed resume data

        Returns:
            Dict with score and details
        """
        score = 0
        contact = resume.contact
        details = {}

        # Name (1 pt)
        if contact.get('name'):
            score += 1
            details['has_name'] = True
        else:
            details['has_name'] = False
            details['missing'] = details.get('missing', []) + ['name']

        # Email (1 pt)
        if contact.get('email'):
            score += 1
            details['has_email'] = True
        else:
            details['has_email'] = False
            details['missing'] = details.get('missing', []) + ['email']

        # Phone (1 pt)
        if contact.get('phone'):
            score += 1
            details['has_phone'] = True
        else:
            details['has_phone'] = False
            details['missing'] = details.get('missing', []) + ['phone']

        # Location (1 pt)
        if contact.get('location'):
            score += 1
            details['has_location'] = True
        else:
            details['has_location'] = False
            details['missing'] = details.get('missing', []) + ['location']

        # LinkedIn (1 pt)
        if contact.get('linkedin'):
            score += 1
            details['has_linkedin'] = True
        else:
            details['has_linkedin'] = False
            details['missing'] = details.get('missing', []) + ['linkedin']

        # Build message
        if score == 5:
            message = "Complete contact information"
        else:
            missing_fields = details.get('missing', [])
            message = f"Missing: {', '.join(missing_fields)}"

        details['message'] = message

        return {
            'score': score,
            'maxScore': 5,
            'details': details
        }

    def _build_resume_text(self, resume: ResumeData) -> str:
        """
        Build full resume text for keyword matching.

        Args:
            resume: Parsed resume data

        Returns:
            Combined resume text
        """
        parts = []

        # Contact info
        if resume.contact:
            parts.append(str(resume.contact.get('name', '')))

        # Experience
        for exp in resume.experience:
            parts.append(exp.get('title', ''))
            parts.append(exp.get('company', ''))
            parts.append(exp.get('description', ''))

        # Education
        for edu in resume.education:
            parts.append(edu.get('degree', ''))
            parts.append(edu.get('institution', ''))

        # Skills
        parts.extend(resume.skills)

        # Certifications
        for cert in resume.certifications:
            parts.append(cert.get('name', ''))

        return ' '.join(parts)
