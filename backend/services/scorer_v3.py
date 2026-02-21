"""
Scorer V3 - Comprehensive ATS Resume Scorer with Full Parameter Integration

Integrates all 23 scoring parameters (P1.1-P7.3) for production-ready
resume evaluation based on 4+ days of ATS research + Phase 1 enhancements.

Total: 100 points across 7 categories:
- Keyword Matching (25pts): P1.1-P1.2
- Content Quality (35pts): P2.1-P2.5 (includes CAR Framework + Impact Scope)
- Format & Structure (15pts): P3.1-P3.4
- Professional Polish (10pts): P4.1-P4.2
- Experience Validation (10pts): P5.1-P5.3
- Red Flags (0pts, penalties only): P6.1-P6.4
- Readability (5pts): P7.1-P7.3

Research Foundation:
- Workday (60% keyword threshold)
- Greenhouse, Lever, LinkedIn standards
- ResumeWorded benchmarks (CAR framework scoring)
- Jobscan achievement analysis
- Industry best practices
"""

from typing import Dict, List, Any, Optional
from backend.services.parameters.registry import get_parameter_registry


class ScorerV3:
    """
    Production-ready ATS scorer integrating all 11 core parameters.

    Uses ParameterRegistry for centralized access to all scorers.
    Provides detailed breakdown by category and parameter.
    """

    def __init__(self):
        """Initialize with parameter registry."""
        self.registry = get_parameter_registry()
        self._load_scorers()

    def _load_scorers(self):
        """Load all scorer instances from registry."""
        all_params = self.registry.get_all_scorers()

        self.scorers = {}
        for code, param_info in all_params.items():
            scorer_class = param_info['scorer_class']
            self.scorers[code] = scorer_class()

    def score(
        self,
        resume_data: Dict[str, Any],
        job_requirements: Optional[Dict[str, Any]] = None,
        experience_level: str = "intermediary",
        role: str = "software_engineer"
    ) -> Dict[str, Any]:
        """
        Score a resume across all parameters.

        Args:
            resume_data: Parsed resume data containing:
                - text: Full resume text
                - sections: Dict of section_name -> {'content': str, 'word_count': int}
                - bullets: List[str] of bullet points
                - page_count: int
                - docx_structure: Optional[Dict] for ATS formatting analysis
            job_requirements: Optional job description data:
                - required_keywords: List[str]
                - preferred_keywords: List[str]
            experience_level: Experience level (beginner, intermediary, senior)

        Returns:
            Comprehensive scoring result with:
            - total_score: Overall score (0-100)
            - category_scores: Scores by category
            - parameter_scores: Individual parameter results
            - rating: Overall rating (Excellent/Good/Fair/Poor)
            - feedback: Actionable recommendations
        """
        # Normalize experience level
        experience_level = experience_level.lower().strip()

        # Initialize results structure
        parameter_results = {}
        category_scores = {
            'Keyword Matching': {'score': 0, 'max': 25, 'parameters': {}},
            'Content Quality': {'score': 0, 'max': 35, 'parameters': {}},
            'Format & Structure': {'score': 0, 'max': 15, 'parameters': {}},
            'Professional Polish': {'score': 0, 'max': 10, 'parameters': {}},
            'Experience Validation': {'score': 0, 'max': 10, 'parameters': {}},
            'Red Flags': {'score': 0, 'max': 0, 'parameters': {}},  # Penalties only
            'Readability': {'score': 0, 'max': 5, 'parameters': {}}
        }

        # Score all parameters
        all_params = self.registry.get_all_scorers()

        for code, param_info in all_params.items():
            try:
                result = self._score_parameter(
                    code,
                    param_info,
                    resume_data,
                    job_requirements,
                    experience_level,
                    role  # Pass role for default keyword matching
                )

                parameter_results[code] = result

                # Add to category total
                category = param_info['category']
                category_scores[category]['score'] += result['score']
                category_scores[category]['parameters'][code] = result

            except Exception as e:
                # Handle scoring errors gracefully (log but don't crash)
                parameter_results[code] = {
                    'score': 0,
                    'max_score': param_info['max_score'],
                    'percentage': 0,
                    'error': str(e),
                    'status': 'error',
                    'details': {}
                }

        # Calculate total score and available maximum
        raw_score = sum(
            category['score']
            for category in category_scores.values()
        )

        # Calculate max available points (exclude skipped parameters)
        max_available = 0
        for code, result in parameter_results.items():
            if result.get('status') != 'skipped':
                max_available += result.get('max_score', 0)

        # Normalize to 100-point scale based on available points
        # If max_available is 0, default to 100 to avoid division by zero
        if max_available > 0:
            # Scale the score: (raw_score / max_available) * 100
            total_score = (raw_score / max_available) * 100
            # Cap at 100 (some parameters can give bonuses)
            total_score = min(total_score, 100)
        else:
            total_score = 0

        # Determine overall rating
        rating = self._calculate_rating(total_score)

        # Generate feedback
        feedback = self._generate_feedback(
            parameter_results,
            category_scores,
            total_score
        )

        return {
            'total_score': round(total_score, 1),
            'max_score': 100,
            'raw_score': round(raw_score, 1),
            'max_available': max_available,
            'percentage': round(total_score, 1),
            'rating': rating,
            'experience_level': experience_level,
            'category_scores': category_scores,
            'parameter_scores': parameter_results,
            'feedback': feedback,
            'version': 'v3.0'
        }

    def _score_parameter(
        self,
        code: str,
        param_info: Dict[str, Any],
        resume_data: Dict[str, Any],
        job_requirements: Optional[Dict[str, Any]],
        experience_level: str,
        role: str = "software_engineer"
    ) -> Dict[str, Any]:
        """
        Score a single parameter.

        Routes to appropriate scorer method based on parameter code.
        Uses role for default keyword matching when no JD provided.
        """
        scorer = self.scorers[code]
        max_score = param_info['max_score']

        # P1.1: Required Keywords Match (25pts)
        if code == 'P1.1':
            # Use role-specific default keywords if no JD provided
            if not job_requirements or 'required_keywords' not in job_requirements:
                from backend.services.role_keywords import get_role_keywords
                role_keywords = get_role_keywords(role)
                keywords = role_keywords['required']
            else:
                keywords = job_requirements['required_keywords']

            result = scorer.score(
                keywords=keywords,
                resume_text=resume_data.get('text', ''),
                level=experience_level
            )

        # P1.2: Preferred Keywords Match (10pts)
        elif code == 'P1.2':
            # Use role-specific default keywords if no JD provided
            if not job_requirements or 'preferred_keywords' not in job_requirements:
                from backend.services.role_keywords import get_role_keywords
                role_keywords = get_role_keywords(role)
                preferred = role_keywords['preferred']
            else:
                preferred = job_requirements['preferred_keywords']

            result = scorer.score(
                preferred_keywords=preferred,
                resume_text=resume_data.get('text', ''),
                experience_level=experience_level
            )

        # P2.1: Action Verb Quality (15pts)
        elif code == 'P2.1':
            bullets = resume_data.get('bullets', [])
            if not bullets:
                return self._missing_data_result(max_score, 'No bullet points found')

            result = scorer.score(bullets=bullets, level=experience_level)

        # P2.2: Quantification Rate (10pts)
        elif code == 'P2.2':
            bullets = resume_data.get('bullets', [])
            if not bullets:
                return self._missing_data_result(max_score, 'No bullet points found')

            result = scorer.score(bullets=bullets, level=experience_level)

        # P2.3: Achievement Depth (5pts)
        elif code == 'P2.3':
            bullets = resume_data.get('bullets', [])
            if not bullets:
                return self._missing_data_result(max_score, 'No bullet points found')

            result = scorer.score(bullets=bullets)

        # P2.4: CAR/STAR Framework (15pts)
        elif code == 'P2.4':
            bullets = resume_data.get('bullets', [])
            if not bullets:
                return self._missing_data_result(max_score, 'No bullet points found')

            result = scorer.score(bullets=bullets, level=experience_level)

        # P2.5: Impact Scope (10pts)
        elif code == 'P2.5':
            bullets = resume_data.get('bullets', [])
            if not bullets:
                return self._missing_data_result(max_score, 'No bullet points found')

            result = scorer.score(bullets=bullets)

        # P3.1: Page Count (5pts)
        elif code == 'P3.1':
            page_count = resume_data.get('page_count', 0)
            if page_count == 0:
                return self._missing_data_result(max_score, 'Page count not provided')

            result = scorer.score(page_count=page_count, level=experience_level)

        # P3.2: Word Count (3pts)
        elif code == 'P3.2':
            # Use full text for accurate word count (includes all sections + contact)
            text = resume_data.get('text', '')
            if not text:
                return self._missing_data_result(max_score, 'No text provided')

            result = scorer.score(content=text, level=experience_level)

        # P3.3: Section Balance (5pts)
        elif code == 'P3.3':
            sections = resume_data.get('sections', {})
            if not sections:
                return self._missing_data_result(max_score, 'No sections data provided')

            result = scorer.score(sections=sections)

        # P3.4: ATS Formatting (7pts)
        elif code == 'P3.4':
            # P3.4 expects the full resume object, not individual fields
            result = scorer.score(
                resume=resume_data,
                docx_structure=resume_data.get('docx_structure'),
                file_format=resume_data.get('format', 'docx')
            )

        # P4.1: Grammar & Spelling (10pts)
        elif code == 'P4.1':
            text = resume_data.get('text', '')
            if not text:
                return self._missing_data_result(max_score, 'No text provided')

            result = scorer.score(text=text)

        # P4.2: Professional Standards (5pts)
        elif code == 'P4.2':
            text = resume_data.get('text', '')
            bullets = resume_data.get('bullets', [])
            contact = resume_data.get('contact', {})

            if not text:
                return self._missing_data_result(max_score, 'No text provided')

            result = scorer.score(
                contact=contact,
                bullets=bullets,
                full_text=text
            )

        # P5.1: Years Alignment (10pts)
        elif code == 'P5.1':
            experience = resume_data.get('experience', [])
            if not experience:
                return self._missing_data_result(max_score, 'No experience data provided')

            result = scorer.score(experience=experience, level=experience_level)

        # P5.2: Career Recency (3pts)
        elif code == 'P5.2':
            experience = resume_data.get('experience', [])
            if not experience:
                return self._missing_data_result(max_score, 'No experience data provided')

            result = scorer.score(experience=experience)  # No level parameter

        # P5.3: Experience Depth (2pts)
        elif code == 'P5.3':
            experience = resume_data.get('experience', [])
            if not experience:
                return self._missing_data_result(max_score, 'No experience data provided')

            result = scorer.score(experiences=experience, level=experience_level)  # Note: 'experiences' plural

        # P6.1: Employment Gaps (penalty -5pts max)
        elif code == 'P6.1':
            experience = resume_data.get('experience', [])
            if not experience:
                return self._missing_data_result(max_score, 'No experience data provided')

            result = scorer.score(employment_history=experience)

        # P6.2: Job Hopping (penalty -3pts max)
        elif code == 'P6.2':
            experience = resume_data.get('experience', [])
            if not experience:
                return self._missing_data_result(max_score, 'No experience data provided')

            result = scorer.score(employment_history=experience)  # Parameter name is employment_history

        # P6.3: Word Repetition (penalty -5pts max)
        elif code == 'P6.3':
            bullets = resume_data.get('bullets', [])
            if not bullets:
                return self._missing_data_result(max_score, 'No bullet points found')

            result = scorer.score(bullets=bullets)

        # P6.4: Formatting Errors (penalty -2pts max)
        elif code == 'P6.4':
            experience = resume_data.get('experience', [])
            if not experience:
                return self._missing_data_result(max_score, 'No experience data provided')

            result = scorer.score(experience=experience)

        # P7.1: Readability Score (5pts)
        elif code == 'P7.1':
            text = resume_data.get('text', '')
            if not text:
                return self._missing_data_result(max_score, 'No text provided')

            result = scorer.score(text=text)

        # P7.2: Bullet Structure (3pts)
        elif code == 'P7.2':
            bullets = resume_data.get('bullets', [])
            if not bullets:
                return self._missing_data_result(max_score, 'No bullet points found')

            result = scorer.score(bullets=bullets)

        # P7.3: Passive Voice (2pts)
        elif code == 'P7.3':
            bullets = resume_data.get('bullets', [])
            if not bullets:
                return self._missing_data_result(max_score, 'No bullet points found')

            result = scorer.score(bullets=bullets)

        else:
            return self._missing_data_result(max_score, f'Unknown parameter: {code}')

        # Standardize result format and CAP score at registry max
        raw_score = result.get('score', 0)
        capped_score = min(raw_score, max_score)  # CRITICAL: Cap at registry max

        return {
            'score': capped_score,
            'max_score': max_score,
            'percentage': round((capped_score / max_score) * 100, 1) if max_score > 0 else 0,
            'status': 'success',
            'details': result
        }

    def _missing_data_result(self, max_score: int, reason: str) -> Dict[str, Any]:
        """Return result for missing required data."""
        return {
            'score': 0,
            'max_score': max_score,
            'percentage': 0,
            'status': 'skipped',
            'reason': reason,
            'details': {}
        }

    def _calculate_rating(self, total_score: float) -> str:
        """
        Calculate overall rating based on total score.

        Ratings aligned with ResumeWorded benchmarks:
        - Excellent: 85-100 (top 10%)
        - Good: 70-84 (top 30%)
        - Fair: 55-69 (average)
        - Poor: 0-54 (needs work)
        """
        if total_score >= 85:
            return 'Excellent'
        elif total_score >= 70:
            return 'Good'
        elif total_score >= 55:
            return 'Fair'
        else:
            return 'Poor'

    def _generate_feedback(
        self,
        parameter_results: Dict[str, Dict],
        category_scores: Dict[str, Dict],
        total_score: float
    ) -> Dict[str, Any]:
        """
        Generate actionable feedback based on scoring results.

        Identifies top strengths and weaknesses with specific recommendations.
        """
        strengths = []
        weaknesses = []
        recommendations = []

        # Analyze each parameter
        for code, result in parameter_results.items():
            if result['status'] != 'success':
                continue

            percentage = result['percentage']
            param_name = self.registry.get_scorer(code)['name']

            # Identify strengths (>80%)
            if percentage >= 80:
                strengths.append({
                    'parameter': param_name,
                    'code': code,
                    'score': result['score'],
                    'percentage': percentage
                })

            # Identify weaknesses (<60%)
            elif percentage < 60:
                weaknesses.append({
                    'parameter': param_name,
                    'code': code,
                    'score': result['score'],
                    'percentage': percentage
                })

        # Sort by severity (lowest scores first)
        weaknesses.sort(key=lambda x: x['percentage'])
        strengths.sort(key=lambda x: x['percentage'], reverse=True)

        # Generate specific recommendations
        for weakness in weaknesses[:5]:  # Top 5 weaknesses
            recommendations.append(self._get_recommendation(weakness['code']))

        return {
            'overall_rating': self._calculate_rating(total_score),
            'total_score': total_score,
            'strengths': strengths[:5],  # Top 5 strengths
            'weaknesses': weaknesses[:5],  # Top 5 weaknesses
            'recommendations': recommendations,
            'category_breakdown': {
                name: {
                    'score': cat['score'],
                    'max': cat['max'],
                    'percentage': round((cat['score'] / cat['max']) * 100, 1) if cat['max'] > 0 else 0
                }
                for name, cat in category_scores.items()
            }
        }

    def _get_recommendation(self, code: str) -> str:
        """Get specific recommendation for a parameter."""
        recommendations = {
            'P1.1': 'Add more required keywords from the job description to your resume',
            'P1.2': 'Include relevant preferred skills and technologies mentioned in the posting',
            'P2.1': 'Use stronger action verbs (Led, Architected, Pioneered) instead of weak verbs',
            'P2.2': 'Add specific metrics and numbers to quantify your achievements',
            'P2.3': 'Replace vague phrases like "responsible for" with concrete achievements',
            'P3.1': 'Adjust resume length to match your experience level standards',
            'P3.2': 'Optimize word count to fall within the ideal range for your level',
            'P3.3': 'Rebalance sections - expand experience section and reduce skills section',
            'P3.4': 'Use ATS-friendly formatting: standard fonts, no tables/images in headers',
            'P4.1': 'Fix grammar and spelling errors - use a spell checker',
            'P4.2': 'Use professional language and avoid personal pronouns (I, me, my)'
        }
        return recommendations.get(code, 'Review and improve this section')


def score_resume_v3(
    resume_data: Dict[str, Any],
    job_requirements: Optional[Dict[str, Any]] = None,
    experience_level: str = "intermediary"
) -> Dict[str, Any]:
    """
    Convenience function to score a resume using Scorer V3.

    Args:
        resume_data: Parsed resume data
        job_requirements: Optional job requirements
        experience_level: Experience level

    Returns:
        Comprehensive scoring result
    """
    scorer = ScorerV3()
    return scorer.score(resume_data, job_requirements, experience_level)
