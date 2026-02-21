"""
Adapter layer to integrate ScorerV3 with existing API infrastructure.

This adapter converts between the ResumeData format used by the API
and the dict format expected by ScorerV3, and vice versa for responses.
"""

from typing import Dict, List, Any, Optional
import re
from backend.services.parser import ResumeData
from backend.services.scorer_v3 import ScorerV3


class ScorerV3Adapter:
    """
    Adapter to bridge ResumeData (API format) and ScorerV3 (scoring engine format).

    Responsibilities:
    - Convert ResumeData to ScorerV3 input format
    - Extract keywords from job description text
    - Map experience levels
    - Convert ScorerV3 output to API response format
    """

    def __init__(self):
        """Initialize adapter with ScorerV3 instance."""
        self.scorer = ScorerV3()

    def score(
        self,
        resume_data: ResumeData,
        job_description: Optional[str] = None,
        level: str = "mid",
        role: str = "software_engineer",
        **kwargs  # Accept but ignore other params for compatibility
    ) -> Dict[str, Any]:
        """
        Score a resume using ScorerV3 with API format compatibility.

        Args:
            resume_data: Parsed resume data from API
            job_description: Raw job description text
            level: Experience level (entry/mid/senior/lead/executive)
            role: Job role for default keyword matching (product_manager, software_engineer, etc.)

        Returns:
            Scoring result in API-compatible format
        """
        # Convert ResumeData to ScorerV3 format
        scorer_input = self._convert_resume_data(resume_data)

        # Extract job requirements from description
        job_requirements = None
        if job_description:
            job_requirements = self._extract_job_requirements(job_description)

        # Map experience level
        experience_level = self._map_experience_level(level)

        # Score with ScorerV3 (pass role for default keywords when no JD)
        result = self.scorer.score(
            resume_data=scorer_input,
            job_requirements=job_requirements,
            experience_level=experience_level,
            role=role  # Pass role for default keyword matching
        )

        # Convert result to API format
        return self._convert_to_api_format(result, job_requirements)

    def _convert_resume_data(self, resume_data: ResumeData) -> Dict[str, Any]:
        """
        Convert ResumeData object to dict format expected by ScorerV3.

        ScorerV3 expects:
        - text: Full resume text
        - sections: Dict of section_name -> {'content': str, 'word_count': int}
        - bullets: List[str] of all bullet points
        - page_count: int
        - docx_structure: Optional[Dict] for ATS formatting
        """
        # Extract full text from all fields
        full_text_parts = []

        # Contact info
        if resume_data.contact:
            contact_values = [str(v) for v in resume_data.contact.values() if v]
            full_text_parts.extend(contact_values)

        # Summary
        if resume_data.summary:
            full_text_parts.append(resume_data.summary)

        # Experience
        bullets = []
        experience_text = []
        if resume_data.experience:
            for exp in resume_data.experience:
                if isinstance(exp, dict):
                    # Add title, company, location
                    experience_text.append(exp.get('title', ''))
                    experience_text.append(exp.get('company', ''))
                    if exp.get('location'):
                        experience_text.append(exp['location'])

                    # Extract description as text AND extract bullets from it
                    if exp.get('description'):
                        description = exp['description']
                        experience_text.append(description)
                        # CRITICAL FIX: Extract bullets from description
                        # Most CVs have bullets in description, not separate achievements field
                        bullets.extend(self._split_bullets(description))

                    # ALSO extract achievements as bullets if they exist separately
                    if exp.get('achievements'):
                        achievements = exp['achievements']
                        if isinstance(achievements, list):
                            bullets.extend(achievements)
                        elif isinstance(achievements, str):
                            # Split by newlines or bullet markers
                            bullets.extend(self._split_bullets(achievements))

        full_text_parts.extend(experience_text)

        # Education
        education_text = []
        if resume_data.education:
            for edu in resume_data.education:
                if isinstance(edu, dict):
                    education_text.append(edu.get('degree', ''))
                    education_text.append(edu.get('institution', ''))
                    if edu.get('relevantCourses'):
                        courses = edu['relevantCourses']
                        if isinstance(courses, list):
                            education_text.extend(courses)

        full_text_parts.extend(education_text)

        # Skills
        if resume_data.skills:
            full_text_parts.extend(resume_data.skills)

        # Certifications
        if resume_data.certifications:
            for cert in resume_data.certifications:
                if isinstance(cert, dict):
                    full_text_parts.append(cert.get('name', ''))
                    if cert.get('issuer'):
                        full_text_parts.append(cert['issuer'])

        # Combine into full text
        full_text = '\n'.join([str(part) for part in full_text_parts if part])

        # Build sections dict
        sections = {}

        if resume_data.experience:
            exp_text = '\n'.join(experience_text)
            sections['experience'] = {
                'content': exp_text,
                'word_count': len(exp_text.split())
            }

        if resume_data.education:
            edu_text = '\n'.join(education_text)
            sections['education'] = {
                'content': edu_text,
                'word_count': len(edu_text.split())
            }

        if resume_data.skills:
            skills_text = ', '.join(resume_data.skills)
            sections['skills'] = {
                'content': skills_text,
                'word_count': len(skills_text.split())
            }

        if resume_data.summary:
            sections['summary'] = {
                'content': resume_data.summary,
                'word_count': len(resume_data.summary.split())
            }

        # Get page count from metadata
        page_count = 1
        if resume_data.metadata:
            page_count = resume_data.metadata.get('pageCount', 1)

        # Get file format
        file_format = 'docx'
        if resume_data.metadata:
            file_format = resume_data.metadata.get('fileFormat', 'docx')

        # Transform experience data for P5-P6 parameters
        # P5/P6 expect 'dates' field (e.g., "2020 - Present"), but parser provides startDate/endDate
        transformed_experience = []
        if resume_data.experience:
            for exp in resume_data.experience:
                if isinstance(exp, dict):
                    # Create a copy to avoid modifying original
                    exp_copy = exp.copy()

                    # Add 'dates' field if startDate/endDate exist
                    start = exp.get('startDate', '')
                    end = exp.get('endDate', '')
                    if start or end:
                        exp_copy['dates'] = f"{start} - {end}".strip(' -')
                    else:
                        exp_copy['dates'] = ''

                    transformed_experience.append(exp_copy)

        return {
            'text': full_text,
            'sections': sections,
            'bullets': bullets,
            'page_count': page_count,
            'format': file_format,
            'experience': transformed_experience,  # For P5-P6 parameters
            'contact': resume_data.contact if resume_data.contact else {},  # For P4.2
            'docx_structure': None  # TODO: Add if needed for P3.4
        }

    def _split_bullets(self, text: str) -> List[str]:
        """Split text into bullet points."""
        # Split by common bullet markers or newlines
        lines = text.split('\n')
        bullets = []
        for line in lines:
            line = line.strip()
            # Remove common bullet markers
            line = re.sub(r'^[•●○◦▪▫■□‣⁃-]\s*', '', line)
            if line:
                bullets.append(line)
        return bullets

    def _extract_job_requirements(self, job_description: str) -> Dict[str, List[str]]:
        """
        Extract required and preferred keywords from job description.

        Uses semantic keyword extraction (KeyBERT) for intelligent extraction.
        Falls back to simple heuristics if semantic extraction fails.

        Strategy:
        1. Use KeyBERT to extract top 25 relevant keywords/phrases
        2. Classify into required vs preferred based on context markers
        3. If semantic extraction fails, fall back to simple heuristics
        """
        if not job_description:
            return {'required_keywords': [], 'preferred_keywords': []}

        # Try semantic extraction first
        try:
            from backend.services.semantic_matcher import get_semantic_matcher

            matcher = get_semantic_matcher()

            # Extract keywords using KeyBERT (handles diversity and relevance)
            keywords = matcher.extract_keywords(
                job_description,
                top_n=25,
                diversity=0.7  # Balance between relevance and diversity
            )

            if not keywords:
                # Fall back to simple extraction if semantic fails
                return self._fallback_keyword_extraction(job_description)

            # Split into required vs preferred based on context clues
            required_keywords = []
            preferred_keywords = []

            # Convert to just the keyword strings (KeyBERT returns tuples)
            keyword_strings = [kw if isinstance(kw, str) else kw[0] for kw in keywords]

            # Analyze job description for required vs preferred markers
            jd_lower = job_description.lower()

            # Markers for required skills
            required_markers = [
                'required', 'must have', 'mandatory', 'essential',
                'required skills', 'requirements', 'must be',
                'need', 'necessary'
            ]

            # Markers for preferred skills
            preferred_markers = [
                'preferred', 'nice to have', 'bonus', 'plus',
                'desirable', 'optional', 'advantage', 'nice-to-have'
            ]

            # Check if sections are explicitly marked
            has_required_section = any(marker in jd_lower for marker in required_markers)
            has_preferred_section = any(marker in jd_lower for marker in preferred_markers)

            if has_required_section or has_preferred_section:
                # Split based on sections
                for keyword in keyword_strings:
                    keyword_lower = keyword.lower()

                    # Find keyword context in job description
                    keyword_pos = jd_lower.find(keyword_lower)
                    if keyword_pos == -1:
                        # Keyword not found directly, add to required by default
                        required_keywords.append(keyword)
                        continue

                    # Check context before keyword (200 chars)
                    context_start = max(0, keyword_pos - 200)
                    context = jd_lower[context_start:keyword_pos + len(keyword_lower)]

                    # Classify based on nearest marker
                    last_required = max((context.rfind(m) for m in required_markers), default=-1)
                    last_preferred = max((context.rfind(m) for m in preferred_markers), default=-1)

                    if last_preferred > last_required:
                        preferred_keywords.append(keyword)
                    else:
                        required_keywords.append(keyword)
            else:
                # No explicit sections - use top keywords as required, rest as preferred
                # Top 60% are required, rest are preferred
                split_point = int(len(keyword_strings) * 0.6)
                required_keywords = keyword_strings[:split_point]
                preferred_keywords = keyword_strings[split_point:]

            return {
                'required_keywords': required_keywords[:15],  # Cap at 15 required
                'preferred_keywords': preferred_keywords[:10]  # Cap at 10 preferred
            }

        except Exception as e:
            # Fall back to simple extraction if anything fails
            print(f"Semantic keyword extraction failed: {e}")
            return self._fallback_keyword_extraction(job_description)

    def _fallback_keyword_extraction(self, job_description: str) -> Dict[str, List[str]]:
        """
        Simple fallback keyword extraction using heuristics.

        Used when semantic extraction is unavailable or fails.
        """
        words = job_description.split()

        keywords = []
        for word in words:
            # Clean word
            word = re.sub(r'[^\w\s+-]', '', word).strip()
            if not word or len(word) < 2:
                continue

            # Check if it's a technical term (uppercase, or common tech pattern)
            if (word.isupper() and len(word) > 1) or \
               word[0].isupper() or \
               any(tech in word.lower() for tech in ['java', 'python', 'sql', 'aws', 'api', 'cloud']):
                keywords.append(word)

        # Deduplicate and normalize
        unique_keywords = list(set(keywords))

        return {
            'required_keywords': unique_keywords[:15],  # Top 15 as required
            'preferred_keywords': unique_keywords[15:25] if len(unique_keywords) > 15 else []
        }

    def _map_experience_level(self, level: str) -> str:
        """
        Map API experience level to ScorerV3 level.

        API: entry, mid, senior, lead, executive
        ScorerV3: beginner, intermediary, senior
        """
        level_map = {
            'entry': 'beginner',
            'junior': 'beginner',
            'mid': 'intermediary',
            'intermediate': 'intermediary',
            'senior': 'senior',
            'lead': 'senior',
            'executive': 'senior',
            'staff': 'senior',
            'principal': 'senior'
        }
        return level_map.get(level.lower(), 'intermediary')

    def _convert_to_api_format(
        self,
        scorer_result: Dict[str, Any],
        job_requirements: Optional[Dict[str, List[str]]]
    ) -> Dict[str, Any]:
        """
        Convert ScorerV3 result to API response format.

        API expects:
        - overallScore: int (0-100)
        - breakdown: Dict[category, {score, maxScore, issues}]
        - issues: Dict[severity, List[str]]
        - strengths: List[str]
        - mode: str
        - keyword_details: Optional[Dict]
        """
        # Use RAW score (not normalized) so breakdown matches overall
        # User sees actual points earned, not normalized percentage
        overall_score = scorer_result['raw_score']  # Changed from total_score to raw_score

        # Convert category scores to breakdown format
        breakdown = {}
        for category_name, category_data in scorer_result['category_scores'].items():
            issues = []

            # Extract issues from parameter details
            for param_code, param_result in category_data['parameters'].items():
                if param_result.get('status') == 'success':
                    details = param_result.get('details', {})

                    # Add feedback as issues if score is low
                    if param_result['percentage'] < 60:
                        param_name = param_code
                        issues.append(f"{param_name}: Score {param_result['percentage']:.0f}%")

            breakdown[category_name] = {
                'score': category_data['score'],
                'maxScore': category_data['max'],
                'issues': issues
            }

        # Categorize issues by severity based on score
        issues_by_severity = {
            'critical': [],
            'warnings': [],
            'suggestions': []
        }

        # Extract weaknesses as issues
        feedback = scorer_result.get('feedback', {})
        for weakness in feedback.get('weaknesses', []):
            percentage = weakness['percentage']
            msg = f"{weakness['parameter']}: {percentage:.0f}% ({weakness['score']}/{weakness.get('max_score', 10)}pts)"

            if percentage < 40:
                issues_by_severity['critical'].append(msg)
            elif percentage < 60:
                issues_by_severity['warnings'].append(msg)
            else:
                issues_by_severity['suggestions'].append(msg)

        # Add recommendations as suggestions
        for recommendation in feedback.get('recommendations', []):
            issues_by_severity['suggestions'].append(recommendation)

        # Extract strengths
        strengths = []
        for strength in feedback.get('strengths', []):
            strengths.append(f"{strength['parameter']}: {strength['percentage']:.0f}%")

        # Build keyword details if available
        keyword_details = None
        if job_requirements and 'P1.1' in scorer_result['parameter_scores']:
            p1_1_result = scorer_result['parameter_scores']['P1.1']
            if p1_1_result.get('status') == 'success':
                details = p1_1_result.get('details', {})
                keyword_details = {
                    'matchPercentage': p1_1_result.get('percentage', 0),
                    'matchedKeywords': details.get('matched', []),
                    'missingKeywords': details.get('missing', []),
                    'totalRequired': len(job_requirements.get('required_keywords', []))
                }

        return {
            'overallScore': round(overall_score),
            'breakdown': breakdown,
            'issues': issues_by_severity,
            'strengths': strengths,
            'mode': 'quality_coach',  # ScorerV3 is quality-focused
            'keyword_details': keyword_details,
            'auto_reject': scorer_result['total_score'] < 40,  # Use normalized score for auto-reject threshold
            'rating': scorer_result.get('rating', 'Fair'),
            'feedback': feedback,
            'version': scorer_result.get('version', 'v3.0')
        }
