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

                    # Add snake_case aliases for gap/job-hopping detectors
                    start = exp.get('startDate', '') or exp.get('start_date', '')
                    end = exp.get('endDate', '') or exp.get('end_date', '')
                    exp_copy['start_date'] = start
                    exp_copy['end_date'] = end
                    exp_copy['dates'] = f"{start} - {end}".strip(' -') if (start or end) else ''

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
            # New 3-tier vocabulary (from roles API)
            'beginner': 'beginner',
            'intermediary': 'intermediary',
            # Old 5-tier vocabulary (legacy / default values in upload.py)
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

    # Human-readable issue messages for each parameter code.
    # Two entries per code: (zero_score_message, partial_score_message)
    # zero_score_message    — used when percentage == 0
    # partial_score_message — used when 0 < percentage < 60
    _ISSUE_MESSAGES = {
        'P1.1': (
            "Required Keywords Match: Resume is missing key terms from the job description — add the exact keywords listed under 'Requirements'",
            "Required Keywords Match: Resume is missing several key terms from the job description — review and add missing required keywords",
        ),
        'P1.2': (
            "Preferred Keywords Match: Resume lacks all preferred/bonus keywords from the job description — include at least a few 'nice-to-have' skills",
            "Preferred Keywords Match: Resume is missing some preferred keywords from the job description — consider adding relevant bonus skills",
        ),
        'P2.1': (
            "Action Verb Quality: Bullet points use no strong action verbs — replace weak phrases like 'responsible for' with verbs like 'led', 'built', 'drove', 'launched'",
            "Action Verb Quality: Some bullet points use weak or passive verbs — strengthen them with impactful action verbs like 'architected', 'pioneered', 'delivered'",
        ),
        'P2.2': (
            "Quantification Rate: No achievements include numbers or metrics — add specific figures (e.g., 'reduced load time by 40%', 'managed a team of 8')",
            "Quantification Rate: Most achievements lack numbers or metrics — add measurable results to at least 50% of bullet points",
        ),
        'P2.3': (
            "Achievement Depth: All experience descriptions are vague or generic — replace filler phrases with concrete outcomes and specific contributions",
            "Achievement Depth: Several experience descriptions are vague — remove generic filler and describe what you actually built, fixed, or improved",
        ),
        'P3.1': (
            "Page Count: Resume page count is well outside the recommended range for your experience level — trim or expand to fit the standard",
            "Page Count: Resume page count is outside the recommended range — adjust length to match best practices for your experience level",
        ),
        'P3.2': (
            "Word Count: Resume has far too few or too many words — aim for the optimal word count range for your experience level",
            "Word Count: Resume word count is outside the ideal range — add more detail or condense content to fit recommended length",
        ),
        'P3.3': (
            "Section Balance: Content is extremely unevenly distributed — the experience section should contain the majority of the resume's content",
            "Section Balance: Content is unevenly distributed across sections — expand thin sections and reduce over-stuffed ones",
        ),
        'P3.4': (
            "ATS Formatting: Resume has ATS-unfriendly formatting — remove all tables, graphics, text boxes, and non-standard fonts",
            "ATS Formatting: Resume may have some ATS-unfriendly elements — check for tables, graphics, or unusual fonts that could confuse parsers",
        ),
        'P4.1': (
            "Grammar & Spelling: Resume contains numerous grammar or spelling errors — run a full spell-check and proofread carefully",
            "Grammar & Spelling: Resume contains some grammar or spelling errors — proofread and correct all mistakes before submitting",
        ),
        'P4.2': (
            "Professional Standards: Resume language is informal or unprofessional — remove personal pronouns (I, me, my), slang, and casual tone",
            "Professional Standards: Resume has some informal or unprofessional language — review tone and remove any casual phrasing or personal pronouns",
        ),
        'P5.1': (
            "Years of Experience: Claimed experience level doesn't match resume history at all — ensure your dates and role history clearly reflect your level",
            "Years of Experience: Claimed experience level only partially matches resume history — review dates to ensure total experience aligns with your stated level",
        ),
        'P5.2': (
            "Career Recency: Recent experience is entirely missing or all roles are outdated — include current or recent positions to show active career progression",
            "Career Recency: Recent experience appears thin or outdated — ensure your most recent roles are clearly listed with up-to-date dates",
        ),
        'P5.3': (
            "Experience Depth: All role descriptions lack sufficient detail — add at least 3-5 bullet points per role describing responsibilities and achievements",
            "Experience Depth: Some role descriptions lack sufficient detail — expand thin job entries with more specific accomplishments and responsibilities",
        ),
        'P6.1': (
            "Employment Gaps: Significant unexplained gaps found between jobs — add dates or a brief note to account for gaps (e.g., freelance work, education, caregiving)",
            "Employment Gaps: Potential employment gaps detected — review your date ranges and add context for any gaps longer than 3 months",
        ),
        'P6.2': (
            "Job Hopping: Multiple very short-tenure positions detected (under 1 year each) — add context or consolidate contract/freelance roles under one entry",
            "Job Hopping: Several short-tenure positions detected — consider adding context (e.g., 'contract role') to explain brief stints",
        ),
        'P6.3': (
            "Repetition: The same words or phrases are used excessively throughout — diversify your vocabulary and avoid repeating the same verbs or nouns",
            "Repetition: Some words or phrases are repeated too often — vary your language to keep the resume engaging and avoid keyword stuffing",
        ),
        'P6.4': (
            "Date Formatting: Employment dates are inconsistently formatted or missing — use a consistent format (e.g., 'Jan 2021 – Mar 2023') for every role",
            "Date Formatting: Some employment dates are inconsistently formatted — standardise all date formats across the resume",
        ),
        'P7.1': (
            "Readability: Text is extremely difficult to read or scan — use shorter sentences, plain language, and clear section headers",
            "Readability: Text could be clearer — simplify complex sentences and use plain, direct language that is easy to skim",
        ),
        'P7.2': (
            "Bullet Structure: Bullets are missing or very poorly structured — each role should have 3-5 concise bullets starting with a strong action verb",
            "Bullet Structure: Some bullets are poorly structured — ensure each bullet is concise, starts with an action verb, and communicates a clear outcome",
        ),
        'P7.3': (
            "Passive Voice: Resume uses passive voice almost exclusively — rewrite sentences to be active (e.g., 'Led a team' instead of 'A team was led by me')",
            "Passive Voice: Too much passive voice detected — rewrite passive constructions to active voice to sound more direct and confident",
        ),
    }

    def _get_issue_message(self, param_code: str, percentage: float) -> str:
        """
        Return a human-readable, actionable issue description for a parameter.

        Uses zero-score wording when percentage == 0, and gentler partial-score
        wording for 0 < percentage < 60.
        """
        messages = self._ISSUE_MESSAGES.get(param_code)
        if messages is None:
            # Fallback: should not happen for known codes
            param_name = param_code
            return f"{param_name}: Score {percentage:.0f}% — review and improve this area"
        zero_msg, partial_msg = messages
        return zero_msg if percentage == 0 else partial_msg

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
                    # Add feedback as issues if score is low
                    if param_result['percentage'] < 60:
                        issues.append(
                            self._get_issue_message(param_code, param_result['percentage'])
                        )

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

        # Build keyword details from P1.1 result (shown for both JD and role-default paths)
        keyword_details = None
        if 'P1.1' in scorer_result['parameter_scores']:
            p1_1_result = scorer_result['parameter_scores']['P1.1']
            if p1_1_result.get('status') == 'success':
                details = p1_1_result.get('details', {})
                # Use actual binary match rate from P1.1 scorer, not score/max percentage
                actual_match_pct = details.get('match_percentage', p1_1_result.get('percentage', 0))
                # P1.1 returns matched_keywords / unmatched_keywords (not matched / missing)
                matched = details.get('matched_keywords', details.get('matched', []))
                missing = details.get('unmatched_keywords', details.get('missing', []))
                total_req = (
                    len(job_requirements.get('required_keywords', []))
                    if job_requirements
                    else len(matched) + len(missing)
                )
                keyword_details = {
                    'matchPercentage': round(actual_match_pct, 1),
                    'matchedKeywords': matched,
                    'missingKeywords': missing,
                    'totalRequired': total_req
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
