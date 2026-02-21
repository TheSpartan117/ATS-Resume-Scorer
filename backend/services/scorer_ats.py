"""
ATS Mode Scorer - Optimized for keyword matching and format compliance.

Scoring breakdown (100 points):
- Keywords (35 pts): Match against role keywords, strict thresholds
- Red Flags (20 pts): Critical issues from validator
- Experience (20 pts): Years, relevance, recency
- Formatting (20 pts): ATS-friendly format
- Contact Info (5 pts): Professional contact details
"""

from typing import Dict, List, Optional
from backend.services.parser import ResumeData
from backend.services.keyword_matcher import KeywordMatcher
from backend.services.red_flags_validator import RedFlagsValidator
from backend.services.role_taxonomy import get_role_scoring_data

# Phase 1.2: Semantic matching support
try:
    from backend.services.semantic_matcher import get_semantic_matcher
    SEMANTIC_MATCHING_AVAILABLE = True
except ImportError:
    SEMANTIC_MATCHING_AVAILABLE = False
    print("Warning: Semantic matching not available. Install: pip install sentence-transformers keybert")


class ATSScorer:
    """
    ATS Mode Scorer focusing on keyword matching and format compliance.
    Integrates with KeywordMatcher and RedFlagsValidator.
    """

    def __init__(self, use_semantic_matching: bool = True):
        """
        Initialize scorer with keyword matcher and validator.

        Args:
            use_semantic_matching: Enable semantic matching if available (default: True)
        """
        self.keyword_matcher = KeywordMatcher()
        self.validator = RedFlagsValidator()
        self.use_semantic_matching = use_semantic_matching and SEMANTIC_MATCHING_AVAILABLE

        # Initialize semantic matcher if enabled
        if self.use_semantic_matching:
            try:
                self.semantic_matcher = get_semantic_matcher()
            except Exception as e:
                print(f"Failed to initialize semantic matcher: {e}")
                self.use_semantic_matching = False
                self.semantic_matcher = None
        else:
            self.semantic_matcher = None

    def _get_role_weights(self, role: str, level: str) -> Dict:
        """
        Get role-specific scoring weights from taxonomy.

        For now, use default ATS weights for all roles.
        Future: Can customize weights per role (e.g., tech roles weight keywords higher).

        Args:
            role: Role ID
            level: Experience level

        Returns:
            Dict with weights for each scoring component
        """
        try:
            role_data = get_role_scoring_data(role, level)
            if role_data and 'scoring_weights' in role_data:
                # Map taxonomy weights to ATS scorer components
                taxonomy_weights = role_data['scoring_weights']

                # For now, use standard ATS distribution
                # In future, can map more granularly
                return {
                    'keywords': 0.35,  # Keywords most important in ATS
                    'red_flags': 0.20,  # Critical issues
                    'experience': 0.20,  # Experience alignment
                    'formatting': 0.20,  # ATS-friendly format
                    'contact': 0.05,   # Contact info
                    'use_weights': False  # Disable weighted scoring for now
                }
        except Exception:
            pass

        # Return default weights
        return {
            'keywords': 0.35,
            'red_flags': 0.20,
            'experience': 0.20,
            'formatting': 0.20,
            'contact': 0.05,
            'use_weights': False
        }

    def score(
        self,
        resume: ResumeData,
        role: str,
        level: str,
        job_description: str = ""
    ) -> Dict:
        """
        Score resume in ATS mode with role-specific weights.

        Args:
            resume: Parsed resume data
            role: Role ID (e.g., "software_engineer")
            level: Experience level (e.g., "mid", "senior")
            job_description: Optional job description for keyword matching

        Returns:
            Dict with score and detailed breakdown
        """
        # Validate inputs
        if not resume:
            raise ValueError("Resume data is required")
        if not role:
            raise ValueError("Role is required")
        if not level:
            raise ValueError("Level is required")

        # Get role-specific weights (if available)
        weights = self._get_role_weights(role, level)

        # Run all scoring components with error handling
        try:
            keywords_result = self._score_keywords(resume, role, level, job_description)
        except Exception as e:
            keywords_result = {
                'score': 0,
                'maxScore': 35,
                'details': {'error': f"Keyword scoring failed: {str(e)}", 'percentage': 0, 'matched': [], 'missing': [], 'message': 'Error in keyword matching'}
            }

        try:
            red_flags_result = self._score_red_flags(resume, role, level)
        except Exception as e:
            red_flags_result = {
                'score': 0,
                'maxScore': 20,
                'details': {'error': f"Red flags validation failed: {str(e)}", 'critical_count': 0, 'warning_count': 0, 'message': 'Error in validation'}
            }

        try:
            experience_result = self._score_experience(resume, level)
        except Exception as e:
            experience_result = {
                'score': 0,
                'maxScore': 20,
                'details': {'error': f"Experience scoring failed: {str(e)}", 'total_years': 0}
            }

        try:
            formatting_result = self._score_formatting(resume)
        except Exception as e:
            formatting_result = {
                'score': 0,
                'maxScore': 20,
                'details': {'error': f"Formatting scoring failed: {str(e)}"}
            }

        try:
            contact_result = self._score_contact_info(resume)
        except Exception as e:
            contact_result = {
                'score': 0,
                'maxScore': 5,
                'details': {'error': f"Contact info scoring failed: {str(e)}", 'missing': []}
            }

        # Apply role-specific weights if available
        if weights and 'use_weights' in weights and weights['use_weights']:
            # Normalize component scores to 0-1 range
            normalized_scores = {
                'keywords': keywords_result['score'] / keywords_result['maxScore'],
                'red_flags': red_flags_result['score'] / red_flags_result['maxScore'],
                'experience': experience_result['score'] / experience_result['maxScore'],
                'formatting': formatting_result['score'] / formatting_result['maxScore'],
                'contact': contact_result['score'] / contact_result['maxScore']
            }

            # Apply weights
            weighted_score = (
                normalized_scores['keywords'] * weights.get('keywords', 0.35) +
                normalized_scores['red_flags'] * weights.get('red_flags', 0.20) +
                normalized_scores['experience'] * weights.get('experience', 0.20) +
                normalized_scores['formatting'] * weights.get('formatting', 0.20) +
                normalized_scores['contact'] * weights.get('contact', 0.05)
            ) * 100  # Scale back to 100 points

            total_score = weighted_score
        else:
            # Use default fixed scoring
            total_score = (
                keywords_result['score'] +
                red_flags_result['score'] +
                experience_result['score'] +
                formatting_result['score'] +
                contact_result['score']
            )

        return {
            'score': round(total_score, 1),
            'breakdown': {
                'keywords': keywords_result,
                'red_flags': red_flags_result,
                'experience': experience_result,
                'formatting': formatting_result,
                'contact': contact_result
            },
            'weights_applied': weights.get('use_weights', False) if weights else False
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

        Phase 1.1: Recalibrated thresholds
        Phase 1.2: Semantic matching support (hybrid: 70% semantic + 30% exact)

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

        # Phase 1.2: Try semantic matching if enabled and job description provided
        if self.use_semantic_matching and job_description and len(job_description) > 50:
            return self._score_keywords_semantic(resume_text, job_description)

        # Fallback to traditional keyword matching
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

        # Check for errors in matching
        if 'error' in match_result:
            return {
                'score': 0,
                'maxScore': 35,
                'details': {
                    'percentage': 0,
                    'matched_count': 0,
                    'missing_count': 0,
                    'matched': [],
                    'missing': [],
                    'error': match_result['error'],
                    'message': f"Error: {match_result['error']}"
                }
            }

        # Get match percentage
        percentage = match_result.get('percentage', 0)
        matched = match_result.get('matched', [])
        missing = match_result.get('missing', [])

        # Apply recalibrated thresholds (Phase 1.1 - aligned with industry standards)
        # Using smooth sigmoid scoring to remove cliff effects
        if percentage >= 60:  # Reduced from 71% to 60% (Workday standard)
            score = 35
            message = f"Excellent keyword match: {percentage:.0f}%"
        elif percentage >= 40:  # Reduced from 51% to 40%
            score = 25
            message = f"Good keyword match: {percentage:.0f}%"
        elif percentage >= 25:  # Reduced from 31% to 25%
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
                'message': message,
                'matching_method': 'exact'
            }
        }

    def _score_keywords_semantic(self, resume_text: str, job_description: str) -> Dict:
        """
        Phase 1.2: Score keywords using semantic matching (hybrid approach).

        Combines:
        - 70% semantic similarity (understands synonyms)
        - 30% exact matching (ensures key terms are present)

        Args:
            resume_text: Full resume text
            job_description: Job description text

        Returns:
            Dict with score and details
        """
        try:
            # Extract keywords from job description
            keywords_with_scores = self.semantic_matcher.extract_keywords(
                job_description,
                top_n=20,
                diversity=0.7
            )

            # Get just the keywords (without scores)
            job_keywords = [kw[0] for kw in keywords_with_scores]

            if not job_keywords:
                # Fallback if extraction fails
                return self._score_keywords_fallback(resume_text, job_description)

            # Hybrid matching: 70% semantic + 30% exact
            hybrid_result = self.semantic_matcher.hybrid_match_score(
                resume_text,
                job_keywords,
                semantic_weight=0.7,
                exact_weight=0.3
            )

            # Convert to percentage (0-100)
            percentage = hybrid_result['hybrid_score'] * 100
            matched_keywords = hybrid_result['matched_keywords']
            missing_keywords = hybrid_result['missing_keywords']

            # Apply recalibrated thresholds
            if percentage >= 60:
                score = 35
                message = f"Excellent semantic match: {percentage:.0f}%"
            elif percentage >= 40:
                score = 25
                message = f"Good semantic match: {percentage:.0f}%"
            elif percentage >= 25:
                score = 10
                message = f"Moderate semantic match: {percentage:.0f}% - add more relevant content"
            else:
                score = 0
                message = f"Poor semantic match: {percentage:.0f}% - critical for ATS"

            return {
                'score': score,
                'maxScore': 35,
                'details': {
                    'percentage': round(percentage, 1),
                    'matched_count': len(matched_keywords),
                    'missing_count': len(missing_keywords),
                    'matched': [m['keyword'] for m in matched_keywords[:10]],
                    'missing': missing_keywords[:10],
                    'message': message,
                    'matching_method': 'semantic_hybrid',
                    'semantic_score': round(hybrid_result['semantic_score'] * 100, 1),
                    'exact_score': round(hybrid_result['exact_score'] * 100, 1)
                }
            }

        except Exception as e:
            print(f"Semantic matching failed: {e}")
            # Fallback to traditional matching
            return self._score_keywords_fallback(resume_text, job_description)

    def _score_keywords_fallback(self, resume_text: str, job_description: str) -> Dict:
        """
        Fallback keyword scoring when semantic matching fails.

        Args:
            resume_text: Full resume text
            job_description: Job description text

        Returns:
            Dict with basic score and details
        """
        # Simple word overlap
        import re

        resume_words = set(re.findall(r'\b\w+\b', resume_text.lower()))
        jd_words = set(re.findall(r'\b\w+\b', job_description.lower()))

        # Remove common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with'}
        resume_words -= stop_words
        jd_words -= stop_words

        # Calculate overlap
        common = resume_words & jd_words
        percentage = (len(common) / len(jd_words) * 100) if jd_words else 0

        # Apply thresholds
        if percentage >= 60:
            score = 35
        elif percentage >= 40:
            score = 25
        elif percentage >= 25:
            score = 10
        else:
            score = 0

        return {
            'score': score,
            'maxScore': 35,
            'details': {
                'percentage': round(percentage, 1),
                'matched_count': len(common),
                'missing_count': len(jd_words - common),
                'matched': list(common)[:10],
                'missing': list(jd_words - common)[:10],
                'message': f"Keyword overlap: {percentage:.0f}%",
                'matching_method': 'fallback'
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

        # Handle None or empty experience gracefully
        if not resume.experience:
            details['total_years'] = 0
            details['years_message'] = "No experience listed"
            details['recency_message'] = "No experience listed"
            details['relevance_message'] = "No experience listed"
            return {
                'score': 0,
                'maxScore': 20,
                'details': details
            }

        # Calculate total experience with improved detection
        total_years = self._calculate_experience_years(resume.experience)
        details['total_years'] = round(total_years, 1)

        # More flexible experience ranges with overlapping boundaries
        # This reduces false negatives by being more lenient
        level_ranges = {
            'entry': (0, 3),
            'mid': (2, 6),      # Overlaps with entry at 2-3
            'senior': (5, 12),   # Overlaps with mid at 5-6
            'lead': (8, 15),     # Overlaps with senior at 8-12
            'executive': (12, 100)  # Overlaps with lead at 12-15
        }

        min_years, max_years = level_ranges.get(level, (0, 100))

        # Score total years (10 pts) - More lenient scoring to reduce false negatives
        if min_years <= total_years <= max_years:
            score += 10
            years_message = f"Experience matches {level} level ({total_years:.1f} years)"
        elif total_years < min_years:
            # Under-qualified but be more lenient
            gap = min_years - total_years
            if gap <= 1:
                # Within 1 year is still good - give 8 points
                score += 8
                years_message = f"Experience appropriate for {level} ({total_years:.1f} years)"
            elif gap <= 2:
                # Within 2 years is acceptable - give 6 points
                score += 6
                years_message = f"Slightly less experience than typical {level} ({total_years:.1f} years)"
            else:
                # More than 2 years under - give 3 points
                score += 3
                years_message = f"Under-qualified for {level} ({total_years:.1f} years, typical {min_years}+)"
        else:
            # Over-qualified - still give 8 points (it's not a major negative)
            score += 8
            years_message = f"More experience than typical {level} ({total_years:.1f} years)"

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
        # Handle None metadata gracefully
        metadata = resume.metadata if resume.metadata else {}
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
        # Handle None contact gracefully
        contact = resume.contact if resume.contact else {}
        details = {'missing': []}  # Initialize missing list once

        # Name (1 pt)
        if contact.get('name'):
            score += 1
            details['has_name'] = True
        else:
            details['has_name'] = False
            details['missing'].append('name')

        # Email (1 pt)
        if contact.get('email'):
            score += 1
            details['has_email'] = True
        else:
            details['has_email'] = False
            details['missing'].append('email')

        # Phone (1 pt)
        if contact.get('phone'):
            score += 1
            details['has_phone'] = True
        else:
            details['has_phone'] = False
            details['missing'].append('phone')

        # Location (1 pt)
        if contact.get('location'):
            score += 1
            details['has_location'] = True
        else:
            details['has_location'] = False
            details['missing'].append('location')

        # LinkedIn (1 pt)
        if contact.get('linkedin'):
            score += 1
            details['has_linkedin'] = True
        else:
            details['has_linkedin'] = False
            details['missing'].append('linkedin')

        # Build message
        if score == 5:
            message = "Complete contact information"
        else:
            missing_fields = details['missing']
            message = f"Missing: {', '.join(missing_fields)}"

        details['message'] = message

        return {
            'score': score,
            'maxScore': 5,
            'details': details
        }

    def _calculate_experience_years(self, experience: List[Dict]) -> float:
        """
        Calculate total years of experience with improved detection.

        Features:
        - Parses duration ranges from descriptions ("5 years experience")
        - Handles date calculations from start/end dates
        - Detects overlapping roles

        Args:
            experience: List of experience entries

        Returns:
            Total years of experience
        """
        if not experience:
            return 0.0

        import re
        from datetime import datetime

        # Try to extract explicit duration from descriptions
        total_from_description = 0.0
        for exp in experience:
            if not exp:
                continue
            description = exp.get('description', '')
            if description:
                # Look for patterns like "5 years", "3+ years", "2-3 years"
                patterns = [
                    r'(\d+)\+?\s*years?\s+(?:of\s+)?experience',
                    r'(?:with\s+)?(\d+)\+?\s*years?\s+(?:in|of)',
                    r'experience[:\s]+(\d+)\+?\s*years?'
                ]
                for pattern in patterns:
                    match = re.search(pattern, description.lower())
                    if match:
                        years = int(match.group(1))
                        total_from_description = max(total_from_description, years)

        # Also calculate from dates using validator
        total_from_dates = self.validator.calculate_total_experience(experience)

        # Use the maximum of the two methods
        return max(total_from_description, total_from_dates)

    def _build_resume_text(self, resume: ResumeData) -> str:
        """
        Build full resume text for keyword matching.

        Improved to handle:
        - Table formats (pipe-separated values)
        - None/empty fields
        - Various text formats

        Args:
            resume: Parsed resume data

        Returns:
            Combined resume text
        """
        parts = []

        # Contact info - handle None
        if resume.contact:
            name = resume.contact.get('name', '')
            if name:
                parts.append(str(name))

        # Experience - handle None and missing fields
        if resume.experience:
            for exp in resume.experience:
                if exp:  # Handle None entries
                    title = exp.get('title', '')
                    company = exp.get('company', '')
                    description = exp.get('description', '')

                    parts.append(title)
                    parts.append(company)

                    # Handle table format (pipe-separated) by converting to spaces
                    if description:
                        # Replace pipes with spaces for better keyword extraction
                        cleaned_desc = description.replace('|', ' ')
                        parts.append(cleaned_desc)

        # Education - handle None and missing fields
        if resume.education:
            for edu in resume.education:
                if edu:  # Handle None entries
                    parts.append(edu.get('degree', ''))
                    parts.append(edu.get('institution', ''))

        # Skills - handle None
        if resume.skills:
            # Convert all skills to strings and filter None
            skills_str = [str(s) for s in resume.skills if s]
            parts.extend(skills_str)

        # Certifications - handle None and missing fields
        if resume.certifications:
            for cert in resume.certifications:
                if cert:  # Handle None entries
                    parts.append(cert.get('name', ''))

        # Filter out empty strings and None values, then join
        filtered_parts = [str(p) for p in parts if p]
        return ' '.join(filtered_parts)
