"""
Quality Mode Scorer - Content-focused scoring for resume quality.

This scorer evaluates resumes based on content quality and depth:
- Content Quality (30 pts): Action verbs, quantification, depth
- Achievement Depth (20 pts): Specific metrics, impact
- Keywords/Fit (20 pts): Relevant skills for role
- Polish (15 pts): Grammar, formatting, professionalism
- Readability (15 pts): Clear structure, appropriate length
"""

import re
from typing import Dict, List, Optional
from backend.services.parser import ResumeData
from backend.services.red_flags_validator import RedFlagsValidator
from backend.services.keyword_extractor import match_with_synonyms
from backend.services.role_taxonomy import get_role_scoring_data


class QualityScorer:
    """
    Quality-focused scorer that evaluates content depth and achievement quality.
    Uses strict thresholds for action verbs (90%+) and quantification (60%+).
    """

    def __init__(self):
        """Initialize scorer with validator"""
        self.validator = RedFlagsValidator()

    def score(
        self,
        resume_data: ResumeData,
        role_id: str,
        level: str,
        job_description: Optional[str] = None
    ) -> Dict:
        """
        Score resume in Quality Mode.

        Args:
            resume_data: Parsed resume data
            role_id: Role identifier (e.g., "software_engineer")
            level: Experience level (entry, mid, senior, lead, executive)
            job_description: Optional job description for keyword matching

        Returns:
            Dictionary with score, breakdown, and detailed feedback
        """
        # Get role-specific scoring data
        role_data = get_role_scoring_data(role_id, level)
        if not role_data:
            raise ValueError(f"Invalid role_id: {role_id}")

        # Run validation to get issues
        validation_result = self.validator.validate_resume(resume_data, role_id, level)

        # Get full resume text for analysis
        resume_text = self._get_resume_text(resume_data)

        # Score each category
        content_quality = self._score_content_quality(
            resume_data, resume_text, role_data, validation_result
        )
        achievement_depth = self._score_achievement_depth(
            resume_data, resume_text, validation_result
        )
        keywords_fit = self._score_keywords_fit(
            resume_data, resume_text, role_data, job_description
        )
        polish = self._score_polish(
            resume_data, validation_result
        )
        readability = self._score_readability(
            resume_data, resume_text
        )

        # Calculate overall score
        overall_score = (
            content_quality['score'] +
            achievement_depth['score'] +
            keywords_fit['score'] +
            polish['score'] +
            readability['score']
        )

        return {
            'score': round(overall_score, 1),
            'breakdown': {
                'content_quality': content_quality,
                'achievement_depth': achievement_depth,
                'keywords_fit': keywords_fit,
                'polish': polish,
                'readability': readability
            }
        }

    def _score_content_quality(
        self,
        resume_data: ResumeData,
        resume_text: str,
        role_data: Dict,
        validation_result: Dict
    ) -> Dict:
        """
        Score content quality (30 points max).

        Breakdown:
        - Action verbs: 15 points (strict: <70%=0, 70-89%=7.5, 90%+=15)
        - Quantification: 10 points (strict: <40%=0, 40-59%=5, 60%+=10)
        - Content depth: 5 points (based on bullet completeness)

        Args:
            resume_data: Parsed resume data
            resume_text: Full resume text
            role_data: Role-specific scoring data
            validation_result: Validation issues

        Returns:
            Dictionary with score and details
        """
        score = 0
        details = {}

        # 1. Action verbs analysis (15 points) - STRICT THRESHOLDS
        action_verbs = role_data.get('action_verbs', [])
        verb_results = self._analyze_action_verbs(resume_data, action_verbs)

        verb_percentage = verb_results['percentage']
        if verb_percentage >= 90:
            verb_score = 15
            details['action_verbs_feedback'] = f"Excellent action verb usage ({verb_percentage:.0f}%)"
        elif verb_percentage >= 70:
            verb_score = 7.5
            details['action_verbs_feedback'] = f"Good action verb usage ({verb_percentage:.0f}%), but aim for 90%+"
        else:
            verb_score = 0
            details['action_verbs_feedback'] = f"Poor action verb usage ({verb_percentage:.0f}%). Minimum 70% required"

        score += verb_score
        details['action_verbs_score'] = verb_score
        details['action_verbs_count'] = verb_results['count']
        details['action_verbs_total'] = verb_results['total']

        # 2. Quantification analysis (10 points) - STRICT THRESHOLDS
        quant_results = self._analyze_quantification(resume_data)

        quant_percentage = quant_results['percentage']
        if quant_percentage >= 60:
            quant_score = 10
            details['quantification_feedback'] = f"Excellent quantification ({quant_percentage:.0f}%)"
        elif quant_percentage >= 40:
            quant_score = 5
            details['quantification_feedback'] = f"Moderate quantification ({quant_percentage:.0f}%), aim for 60%+"
        else:
            quant_score = 0
            details['quantification_feedback'] = f"Poor quantification ({quant_percentage:.0f}%). Minimum 40% required"

        score += quant_score
        details['quantification_score'] = quant_score
        details['quantified_bullets'] = quant_results['quantified_count']
        details['total_bullets'] = quant_results['total_bullets']

        # 3. Content depth (5 points) - Based on bullet completeness
        depth_score = self._analyze_content_depth(validation_result)
        score += depth_score
        details['depth_score'] = depth_score
        details['depth_feedback'] = self._get_depth_feedback(depth_score)

        return {
            'score': round(score, 1),
            'max_score': 30,
            'details': details
        }

    def _score_achievement_depth(
        self,
        resume_data: ResumeData,
        resume_text: str,
        validation_result: Dict
    ) -> Dict:
        """
        Score achievement depth (20 points max).

        Evaluates:
        - Specific metrics and impact (10 points)
        - Vague phrase avoidance (10 points)

        Args:
            resume_data: Parsed resume data
            resume_text: Full resume text
            validation_result: Validation issues

        Returns:
            Dictionary with score and details
        """
        score = 0
        details = {}

        # 1. Specific metrics and impact (10 points)
        metrics_results = self._analyze_metrics_depth(resume_text)
        metrics_score = metrics_results['score']
        score += metrics_score
        details['metrics_score'] = metrics_score
        details['metrics_found'] = metrics_results['metrics']
        details['metrics_feedback'] = metrics_results['feedback']

        # 2. Vague phrase penalty (10 points base, deduct for each vague phrase)
        vague_warnings = [
            issue for issue in validation_result.get('warnings', [])
            if issue.get('category') == 'achievement_depth'
        ]

        # Start with 10 points, deduct 2 per vague phrase (max 5 penalties)
        vague_count = min(len(vague_warnings), 5)
        vague_score = max(0, 10 - (vague_count * 2))
        score += vague_score
        details['vague_score'] = vague_score
        details['vague_phrases_found'] = vague_count
        details['vague_feedback'] = self._get_vague_feedback(vague_count)

        return {
            'score': round(score, 1),
            'max_score': 20,
            'details': details
        }

    def _score_keywords_fit(
        self,
        resume_data: ResumeData,
        resume_text: str,
        role_data: Dict,
        job_description: Optional[str]
    ) -> Dict:
        """
        Score keywords/fit for role (20 points max).

        If JD provided: Match against JD keywords
        Otherwise: Match against role typical keywords

        Args:
            resume_data: Parsed resume data
            resume_text: Full resume text
            role_data: Role-specific scoring data
            job_description: Optional job description

        Returns:
            Dictionary with score and details
        """
        details = {}

        if job_description:
            # Match against JD keywords
            from backend.services.keyword_extractor import extract_keywords_from_jd
            jd_keywords = extract_keywords_from_jd(job_description)

            required = jd_keywords.get('required', [])
            preferred = jd_keywords.get('preferred', [])

            required_matched = sum(1 for kw in required if match_with_synonyms(kw, resume_text))
            preferred_matched = sum(1 for kw in preferred if match_with_synonyms(kw, resume_text))

            required_pct = (required_matched / len(required) * 100) if required else 0
            preferred_pct = (preferred_matched / len(preferred) * 100) if preferred else 0

            # 15 points for required, 5 points for preferred
            score = (required_pct / 100 * 15) + (preferred_pct / 100 * 5)

            details['required_matched'] = required_matched
            details['required_total'] = len(required)
            details['preferred_matched'] = preferred_matched
            details['preferred_total'] = len(preferred)
            details['feedback'] = f"JD match: {required_matched}/{len(required)} required, {preferred_matched}/{len(preferred)} preferred"
        else:
            # Match against role keywords
            typical_keywords = role_data.get('typical_keywords', [])
            matched = sum(1 for kw in typical_keywords if match_with_synonyms(kw, resume_text))
            match_pct = (matched / len(typical_keywords) * 100) if typical_keywords else 0

            # Generous scoring for role match
            score = (match_pct / 100 * 20)

            details['keywords_matched'] = matched
            details['keywords_total'] = len(typical_keywords)
            details['match_percentage'] = round(match_pct, 1)
            details['feedback'] = f"Role match: {matched}/{len(typical_keywords)} keywords ({match_pct:.0f}%)"

        return {
            'score': round(score, 1),
            'max_score': 20,
            'details': details
        }

    def _score_polish(
        self,
        resume_data: ResumeData,
        validation_result: Dict
    ) -> Dict:
        """
        Score polish (15 points max).

        Evaluates:
        - Grammar: 0 errors = full points, deduct for typos/grammar
        - Professional standards (email, phone, LinkedIn)

        Args:
            resume_data: Parsed resume data
            validation_result: Validation issues

        Returns:
            Dictionary with score and details
        """
        score = 15  # Start with perfect score
        details = {}

        # 1. Grammar/typos (10 points) - deduct for errors
        grammar_warnings = [
            issue for issue in validation_result.get('warnings', [])
            if issue.get('category') in ['typo', 'grammar', 'capitalization']
        ]

        # Deduct 1 point per error (max 10 deductions)
        grammar_errors = min(len(grammar_warnings), 10)
        grammar_score = max(0, 10 - grammar_errors)

        details['grammar_score'] = grammar_score
        details['grammar_errors'] = grammar_errors
        details['grammar_feedback'] = self._get_grammar_feedback(grammar_errors)

        # 2. Professional standards (5 points)
        prof_warnings = [
            issue for issue in validation_result.get('warnings', [])
            if issue.get('category') in ['email_professionalism', 'phone_format', 'location_format']
        ]

        # Deduct 1 point per issue (max 5 deductions)
        prof_issues = min(len(prof_warnings), 5)
        prof_score = max(0, 5 - prof_issues)

        details['professional_score'] = prof_score
        details['professional_issues'] = prof_issues
        details['professional_feedback'] = self._get_professional_feedback(prof_issues)

        score = grammar_score + prof_score

        return {
            'score': round(score, 1),
            'max_score': 15,
            'details': details
        }

    def _score_readability(
        self,
        resume_data: ResumeData,
        resume_text: str
    ) -> Dict:
        """
        Score readability (15 points max).

        Evaluates:
        - Clear structure (sections, bullets)
        - Appropriate length (1-2 pages, 400-800 words)

        Args:
            resume_data: Parsed resume data
            resume_text: Full resume text

        Returns:
            Dictionary with score and details
        """
        score = 0
        details = {}

        # 1. Structure (8 points)
        structure_score = 0

        # Has required sections (3 points)
        has_sections = 0
        if resume_data.experience:
            has_sections += 1
        if resume_data.education:
            has_sections += 1
        if resume_data.skills:
            has_sections += 1
        structure_score += has_sections  # 0-3 points

        # Uses bullet points (3 points)
        bullet_count = resume_text.count('•') + resume_text.count('-')
        if bullet_count >= 10:
            structure_score += 3
        elif bullet_count >= 5:
            structure_score += 2
        else:
            structure_score += 1

        # Has proper formatting (2 points)
        if resume_data.metadata.get('pageCount', 0) <= 2:
            structure_score += 2

        score += min(structure_score, 8)
        details['structure_score'] = min(structure_score, 8)
        details['structure_feedback'] = self._get_structure_feedback(has_sections, bullet_count)

        # 2. Length appropriateness (7 points)
        word_count = resume_data.metadata.get('wordCount', 0)
        page_count = resume_data.metadata.get('pageCount', 0)

        length_score = 0
        if 400 <= word_count <= 800 and page_count <= 2:
            length_score = 7
            length_feedback = f"Optimal length ({word_count} words, {page_count} pages)"
        elif 300 <= word_count <= 1000 and page_count <= 2:
            length_score = 5
            length_feedback = f"Good length ({word_count} words, {page_count} pages)"
        elif 200 <= word_count <= 1200:
            length_score = 3
            length_feedback = f"Length acceptable ({word_count} words, {page_count} pages)"
        else:
            length_score = 1
            length_feedback = f"Length needs adjustment ({word_count} words, {page_count} pages)"

        score += length_score
        details['length_score'] = length_score
        details['length_feedback'] = length_feedback
        details['word_count'] = word_count
        details['page_count'] = page_count

        return {
            'score': round(score, 1),
            'max_score': 15,
            'details': details
        }

    def _analyze_action_verbs(self, resume_data: ResumeData, action_verbs: List[str]) -> Dict:
        """
        Analyze action verb usage in experience bullets.

        Args:
            resume_data: Parsed resume data
            action_verbs: List of expected action verbs for the role

        Returns:
            Dictionary with count, total, and percentage
        """
        if not resume_data.experience:
            return {'count': 0, 'total': 0, 'percentage': 0}

        # Parse all bullets from experience
        total_bullets = 0
        bullets_with_action_verbs = 0

        for exp in resume_data.experience:
            description = exp.get('description', '')
            if not description:
                continue

            bullets = self.validator._parse_bullets(description)
            for bullet in bullets:
                if not bullet.strip() or len(bullet.strip()) < 10:
                    continue

                total_bullets += 1

                # Check if bullet starts with any action verb
                bullet_lower = bullet.lower()
                for verb in action_verbs:
                    # Match at start of bullet (after removing bullet markers)
                    if re.match(r'^[•\-*\d.)\s]*' + re.escape(verb.lower()) + r'\b', bullet_lower):
                        bullets_with_action_verbs += 1
                        break

        percentage = (bullets_with_action_verbs / total_bullets * 100) if total_bullets > 0 else 0

        return {
            'count': bullets_with_action_verbs,
            'total': total_bullets,
            'percentage': percentage
        }

    def _analyze_quantification(self, resume_data: ResumeData) -> Dict:
        """
        Analyze quantification in experience bullets.

        Args:
            resume_data: Parsed resume data

        Returns:
            Dictionary with quantified count, total bullets, and percentage
        """
        if not resume_data.experience:
            return {'quantified_count': 0, 'total_bullets': 0, 'percentage': 0}

        total_bullets = 0
        quantified_bullets = 0

        # Patterns for quantification
        quant_patterns = [
            r'\d+%',           # Percentages: 50%
            r'\d+\+',          # Plus numbers: 100+
            r'\d+x',           # Multipliers: 2x, 10x
            r'\$\d+',          # Money: $100K
            r'\d+K',           # Thousands: 50K
            r'\d+M',           # Millions: 2M
            r'\d+\s*(?:users|customers|clients|people|engineers|developers)',  # People: 100 users
            r'\d+\s*(?:hours|days|weeks|months|years)',  # Time: 6 months
        ]

        for exp in resume_data.experience:
            description = exp.get('description', '')
            if not description:
                continue

            bullets = self.validator._parse_bullets(description)
            for bullet in bullets:
                if not bullet.strip() or len(bullet.strip()) < 10:
                    continue

                total_bullets += 1

                # Check if bullet contains any quantification
                has_quant = False
                for pattern in quant_patterns:
                    if re.search(pattern, bullet, re.IGNORECASE):
                        has_quant = True
                        break

                if has_quant:
                    quantified_bullets += 1

        percentage = (quantified_bullets / total_bullets * 100) if total_bullets > 0 else 0

        return {
            'quantified_count': quantified_bullets,
            'total_bullets': total_bullets,
            'percentage': percentage
        }

    def _analyze_content_depth(self, validation_result: Dict) -> float:
        """
        Analyze content depth based on validation issues.

        Args:
            validation_result: Validation issues

        Returns:
            Score from 0-5
        """
        # Check for bullet length and structure issues
        critical_issues = [
            issue for issue in validation_result.get('critical', [])
            if issue.get('category') in ['bullet_length', 'bullet_structure']
        ]

        warning_issues = [
            issue for issue in validation_result.get('warnings', [])
            if issue.get('category') in ['bullet_length', 'bullet_structure']
        ]

        # Start with 5 points, deduct for issues
        score = 5
        score -= len(critical_issues) * 1.0  # 1 point per critical
        score -= len(warning_issues) * 0.5   # 0.5 points per warning

        return max(0, score)

    def _analyze_metrics_depth(self, resume_text: str) -> Dict:
        """
        Analyze depth of metrics and impact statements.

        Args:
            resume_text: Full resume text

        Returns:
            Dictionary with score, metrics found, and feedback
        """
        # Advanced metrics patterns (beyond basic numbers)
        advanced_patterns = [
            r'reduced.*by\s+\d+%',
            r'increased.*by\s+\d+%',
            r'improved.*by\s+\d+%',
            r'saved.*\$\d+',
            r'generated.*\$\d+',
            r'grew.*from.*to',
            r'\d+x\s+(?:faster|improvement|increase)',
        ]

        metrics = []
        for pattern in advanced_patterns:
            matches = re.findall(pattern, resume_text, re.IGNORECASE)
            metrics.extend(matches)

        # Score based on number of impactful metrics
        metric_count = len(metrics)
        if metric_count >= 5:
            score = 10
            feedback = f"Excellent impact metrics ({metric_count} found)"
        elif metric_count >= 3:
            score = 7
            feedback = f"Good impact metrics ({metric_count} found)"
        elif metric_count >= 1:
            score = 4
            feedback = f"Some impact metrics ({metric_count} found), add more"
        else:
            score = 0
            feedback = "No clear impact metrics found. Add specific results (reduced by X%, increased Y)"

        return {
            'score': score,
            'metrics': metrics[:5],  # Return top 5 examples
            'feedback': feedback
        }

    def _get_resume_text(self, resume_data: ResumeData) -> str:
        """
        Extract all text from resume for analysis.

        Args:
            resume_data: Parsed resume data

        Returns:
            Lowercase resume text
        """
        text_parts = []

        # Contact info
        if resume_data.contact:
            for value in resume_data.contact.values():
                if value:
                    text_parts.append(str(value))

        # Experience
        for exp in resume_data.experience:
            if exp.get('title'):
                text_parts.append(exp['title'])
            if exp.get('company'):
                text_parts.append(exp['company'])
            if exp.get('description'):
                text_parts.append(exp['description'])

        # Education
        for edu in resume_data.education:
            if edu.get('degree'):
                text_parts.append(edu['degree'])
            if edu.get('institution'):
                text_parts.append(edu['institution'])

        # Skills
        text_parts.extend(resume_data.skills)

        # Certifications
        for cert in resume_data.certifications:
            if cert.get('name'):
                text_parts.append(cert['name'])

        return " ".join(text_parts).lower()

    # Feedback helper methods
    def _get_depth_feedback(self, score: float) -> str:
        """Generate feedback for content depth score"""
        if score >= 4:
            return "Excellent bullet point quality"
        elif score >= 3:
            return "Good bullet points, minor improvements needed"
        elif score >= 2:
            return "Bullets need more detail and structure"
        else:
            return "Bullets are too short or incomplete"

    def _get_vague_feedback(self, count: int) -> str:
        """Generate feedback for vague phrases"""
        if count == 0:
            return "No vague phrases detected"
        elif count <= 2:
            return f"{count} vague phrases found - replace with specific achievements"
        else:
            return f"{count} vague phrases found - use specific, measurable achievements"

    def _get_grammar_feedback(self, errors: int) -> str:
        """Generate feedback for grammar score"""
        if errors == 0:
            return "No grammar or spelling errors detected"
        elif errors <= 2:
            return f"{errors} minor errors found"
        elif errors <= 5:
            return f"{errors} errors found - proofread carefully"
        else:
            return f"{errors} errors found - requires thorough proofreading"

    def _get_professional_feedback(self, issues: int) -> str:
        """Generate feedback for professional standards"""
        if issues == 0:
            return "Professional contact info and formatting"
        elif issues <= 2:
            return f"{issues} minor professional standard issues"
        else:
            return f"{issues} professional standard issues - review contact info"

    def _get_structure_feedback(self, sections: int, bullets: int) -> str:
        """Generate feedback for structure score"""
        feedback_parts = []

        if sections == 3:
            feedback_parts.append("All required sections present")
        elif sections == 2:
            feedback_parts.append("Missing one required section")
        else:
            feedback_parts.append("Missing required sections")

        if bullets >= 10:
            feedback_parts.append("good use of bullets")
        elif bullets >= 5:
            feedback_parts.append("could use more bullets")
        else:
            feedback_parts.append("needs more bullet points")

        return ", ".join(feedback_parts)
