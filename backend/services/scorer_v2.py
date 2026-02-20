"""
Adaptive ATS Scorer with dual-mode scoring.

This module provides intelligent scoring with two modes:
- Mode A (ATS Simulation): Harsh keyword-heavy scoring (70/20/10)
- Mode B (Quality Coach): Balanced quality scoring (25/30/25/20)

The mode is auto-detected based on job description presence.

Main Scorer Orchestrator:
- ResumeScorer: Main orchestrator class with interpretation and recommendations
- AdaptiveScorer: Core scoring engine with dual-mode support
"""

import re
from typing import Dict, List, Optional, Any
from backend.services.keyword_extractor import extract_keywords_from_jd, match_with_synonyms
from backend.services.role_taxonomy import ExperienceLevel, get_role_scoring_data, get_role_scoring_data_enhanced
from backend.services.parser import ResumeData
from backend.services.content_impact_analyzer import ContentImpactAnalyzer
from backend.services.writing_quality_analyzer import WritingQualityAnalyzer
from backend.services.context_aware_scorer import ContextAwareScorer
from backend.services.feedback_generator import FeedbackGenerator
from backend.services.benchmark_tracker import BenchmarkTracker


class AdaptiveScorer:
    """
    Adaptive scoring engine that switches between ATS Simulation and Quality Coach modes.
    """

    def score(
        self,
        resume_data: ResumeData,
        role_id: str,
        level: ExperienceLevel,
        job_description: Optional[str] = None,
        mode: str = "auto"
    ) -> Dict:
        """
        Main scoring entry point with auto-mode detection.

        Args:
            resume_data: Parsed resume data
            role_id: Role identifier (e.g., "software_engineer")
            level: Experience level
            job_description: Optional job description text
            mode: Scoring mode - "auto", "ats_simulation", or "quality_coach"

        Returns:
            Dictionary with overall_score, mode, breakdown, and keyword_details
        """
        # Get role-specific scoring data
        # Use enhanced version with corpus keywords for better matching
        role_data = get_role_scoring_data_enhanced(role_id, level)
        if not role_data:
            # Fallback to basic version if enhanced fails
            role_data = get_role_scoring_data(role_id, level)
        if not role_data:
            raise ValueError(f"Invalid role_id: {role_id}")

        # Auto-detect mode if mode="auto"
        if mode == "auto":
            mode = "ats_simulation" if job_description else "quality_coach"

        # Route to appropriate scoring method
        if mode == "ats_simulation":
            if not job_description:
                raise ValueError("job_description required for ATS Simulation mode")
            return self._score_ats_simulation(resume_data, role_data, job_description)
        elif mode == "quality_coach":
            return self._score_quality_coach(resume_data, role_data)
        else:
            raise ValueError(f"Invalid mode: {mode}. Use 'auto', 'ats_simulation', or 'quality_coach'")

    def _score_ats_simulation(
        self,
        resume_data: ResumeData,
        role_data: Dict,
        job_description: str
    ) -> Dict:
        """
        Mode A: ATS Simulation scoring (70/20/10).

        Breakdown:
        - Keyword Match: 70 points (50 required + 20 preferred)
        - Format Check: 20 points
        - Structure: 10 points

        Args:
            resume_data: Parsed resume data
            role_data: Role-specific scoring criteria
            job_description: Job description text

        Returns:
            Scoring results with overall_score, mode, breakdown, keyword_details, auto_reject
        """
        resume_text = self._get_resume_text(resume_data)

        # Extract keywords from job description
        jd_keywords = extract_keywords_from_jd(job_description)

        # 1. Keyword Match (70 points): 50 required + 20 preferred
        keyword_result = self._score_ats_keywords(resume_text, jd_keywords)
        keyword_score = keyword_result["score"]

        # 2. Format Check (20 points)
        format_result = self._score_format(resume_data, resume_text)
        format_score = format_result["score"]

        # 3. Structure (10 points)
        structure_result = self._score_structure(resume_data)
        structure_score = structure_result["score"]

        # Calculate overall score
        overall_score = keyword_score + format_score + structure_score

        # Determine auto-reject
        auto_reject = keyword_result["required_match_pct"] < 60.0

        # Convert details strings to issue lists
        keyword_issues = self._details_to_issues(keyword_result.get("details", ""), keyword_score, 70)
        format_issues = self._details_to_issues(format_result.get("details", ""), format_score, 20)
        structure_issues = self._details_to_issues(structure_result.get("details", ""), structure_score, 10)

        # Collect all issues for categorization
        all_issues = keyword_issues + format_issues + structure_issues

        # Categorize issues by severity
        critical_issues = [issue for issue in all_issues if issue[0] == "critical"]
        warnings = [issue for issue in all_issues if issue[0] == "warning"]
        suggestions = [issue for issue in all_issues if issue[0] == "suggestion"]
        info_issues = [issue for issue in all_issues if issue[0] == "info"]

        # Generate strengths
        strengths = []
        if keyword_result["required_match_pct"] >= 80:
            strengths.append("Strong keyword match with required skills")
        if keyword_result["preferred_match_pct"] >= 60:
            strengths.append("Good coverage of preferred qualifications")
        if format_score >= 15:
            strengths.append("ATS-compatible format")

        return {
            "overallScore": round(overall_score, 1),
            "mode": "ats_simulation",
            "breakdown": {
                "keyword_match": {
                    "score": round(keyword_score, 1),
                    "maxScore": 70,
                    "issues": keyword_issues
                },
                "format": {
                    "score": round(format_score, 1),
                    "maxScore": 20,
                    "issues": format_issues
                },
                "structure": {
                    "score": round(structure_score, 1),
                    "maxScore": 10,
                    "issues": structure_issues
                }
            },
            "issues": {
                "critical": critical_issues,
                "warnings": warnings,
                "suggestions": suggestions,
                "info": info_issues
            },
            "strengths": strengths,
            "keyword_details": {
                "required_matched": keyword_result["required_matched"],
                "required_total": keyword_result["required_total"],
                "required_match_pct": keyword_result["required_match_pct"],
                "preferred_matched": keyword_result["preferred_matched"],
                "preferred_total": keyword_result["preferred_total"],
                "preferred_match_pct": keyword_result["preferred_match_pct"]
            },
            "auto_reject": auto_reject,
            "rejection_reason": "Required keywords match < 60%" if auto_reject else None
        }

    def _score_quality_coach(
        self,
        resume_data: ResumeData,
        role_data: Dict
    ) -> Dict:
        """
        Mode B: Quality Coach scoring (25/30/25/20).

        Breakdown:
        - Role Keywords: 25 points (generous scoring)
        - Content Quality: 30 points (simplified)
        - Format: 25 points
        - Professional Polish: 20 points (simplified)

        Args:
            resume_data: Parsed resume data
            role_data: Role-specific scoring criteria

        Returns:
            Scoring results with overall_score, mode, breakdown, keyword_details, cta
        """
        resume_text = self._get_resume_text(resume_data)

        # 1. Role Keywords (25 points) - Generous scoring
        role_keyword_result = self._score_role_keywords(resume_text, role_data)
        role_keyword_score = role_keyword_result["score"]

        # 2. Content Quality (30 points) - Enhanced with ContentImpactAnalyzer
        content_result = self._score_content_quality(resume_data, resume_text, role_data, level=role_data.get("level", "mid"))
        content_score = content_result["score"]

        # 3. Format (25 points)
        format_result = self._score_format(resume_data, resume_text)
        # Scale format from 20 to 25 points for quality mode
        format_score = (format_result["score"] / 20) * 25

        # 4. Professional Polish (20 points) - Simplified
        polish_result = self._score_professional_polish(resume_data, resume_text)
        polish_score = polish_result["score"]

        # Calculate overall score
        overall_score = role_keyword_score + content_score + format_score + polish_score

        # Convert details strings to issue lists
        role_keyword_issues = self._details_to_issues(role_keyword_result.get("details", ""), role_keyword_score, 25)
        content_issues = self._details_to_issues(content_result.get("details", ""), content_score, 30)
        format_issues = self._details_to_issues(format_result.get("details", ""), format_score, 25)
        polish_issues = self._details_to_issues(polish_result.get("details", ""), polish_score, 20)

        # Collect all issues for categorization
        all_issues = role_keyword_issues + content_issues + format_issues + polish_issues

        # Categorize issues by severity
        critical_issues = [issue for issue in all_issues if issue[0] == "critical"]
        warnings = [issue for issue in all_issues if issue[0] == "warning"]
        suggestions = [issue for issue in all_issues if issue[0] == "suggestion"]
        info_issues = [issue for issue in all_issues if issue[0] == "info"]

        # Generate strengths
        strengths = []
        if role_keyword_score >= 20:
            strengths.append("Strong alignment with role requirements")
        if content_score >= 24:
            strengths.append("High-quality, well-written content")
        if format_score >= 20:
            strengths.append("Professional formatting")
        if polish_score >= 16:
            strengths.append("Polished and error-free presentation")

        # Generate enhanced feedback using FeedbackGenerator
        feedback_generator = FeedbackGenerator()
        level_str = role_data.get("level", "mid")

        # Prepare analysis data for feedback generation
        analysis_data = {
            'overall_score': overall_score,
            'achievement_strength': content_result.get('achievement_strength', content_score / 2),
            'sentence_clarity': content_result.get('sentence_clarity', 0),
            'specificity': content_result.get('specificity', 0),
            'grammar': polish_score / 2  # Grammar is half of polish score
        }

        feedback_report = feedback_generator.generate_complete_feedback(
            analysis_data,
            level=level_str,
            section="experience"
        )

        # Track score for benchmarking
        benchmark_tracker = BenchmarkTracker()
        role_id = role_data.get("role_id", "unknown")
        benchmark_tracker.track_score(
            score=overall_score,
            role=role_id,
            level=level_str,
            metadata={
                'content_score': content_score,
                'polish_score': polish_score,
                'format_score': format_score
            }
        )

        # Get competitive positioning
        benchmark_comparison = benchmark_tracker.compare_to_benchmark(
            score=overall_score,
            role=role_id,
            level=level_str
        )

        return {
            "overallScore": round(overall_score, 1),
            "mode": "quality_coach",
            "breakdown": {
                "role_keywords": {
                    "score": round(role_keyword_score, 1),
                    "maxScore": 25,
                    "issues": role_keyword_issues
                },
                "content_quality": {
                    "score": round(content_score, 1),
                    "maxScore": 30,
                    "issues": content_issues
                },
                "format": {
                    "score": round(format_score, 1),
                    "maxScore": 25,
                    "issues": format_issues
                },
                "professional_polish": {
                    "score": round(polish_score, 1),
                    "maxScore": 20,
                    "issues": polish_issues
                }
            },
            "issues": {
                "critical": critical_issues,
                "warnings": warnings,
                "suggestions": suggestions,
                "info": info_issues
            },
            "strengths": strengths,
            "keyword_details": role_keyword_result["keyword_details"],
            "cta": self._generate_cta(overall_score),
            # Enhanced feedback and benchmarking
            "enhanced_feedback": {
                "interpretation": feedback_report['interpretation'],
                "priority_actions": feedback_report['priority_actions'],
                "all_suggestions": feedback_report['suggestions'],
                "identified_strengths": feedback_report['strengths']
            },
            "benchmark_data": benchmark_comparison if benchmark_comparison.get('percentile') is not None else None
        }

    def _score_ats_keywords(self, resume_text: str, jd_keywords: Dict) -> Dict:
        """
        Score keyword matching for ATS mode.

        Args:
            resume_text: Full resume text (lowercase)
            jd_keywords: Dictionary with 'required' and 'preferred' keyword lists

        Returns:
            Dictionary with score, matched counts, and percentages
        """
        required_keywords = jd_keywords.get("required", [])
        preferred_keywords = jd_keywords.get("preferred", [])

        # Match required keywords (50 points max)
        required_matched = 0
        for keyword in required_keywords:
            if match_with_synonyms(keyword, resume_text):
                required_matched += 1

        required_total = len(required_keywords)
        required_match_pct = (required_matched / required_total * 100) if required_total > 0 else 0
        required_score = (required_matched / required_total * 50) if required_total > 0 else 0

        # Match preferred keywords (20 points max)
        preferred_matched = 0
        for keyword in preferred_keywords:
            if match_with_synonyms(keyword, resume_text):
                preferred_matched += 1

        preferred_total = len(preferred_keywords)
        preferred_match_pct = (preferred_matched / preferred_total * 100) if preferred_total > 0 else 0
        preferred_score = (preferred_matched / preferred_total * 20) if preferred_total > 0 else 0

        total_score = required_score + preferred_score

        # Cap at maximum score
        total_score = min(total_score, 70)

        return {
            "score": total_score,
            "required_matched": required_matched,
            "required_total": required_total,
            "required_match_pct": round(required_match_pct, 1),
            "preferred_matched": preferred_matched,
            "preferred_total": preferred_total,
            "preferred_match_pct": round(preferred_match_pct, 1),
            "details": f"Required: {required_matched}/{required_total} ({required_match_pct:.0f}%), "
                      f"Preferred: {preferred_matched}/{preferred_total} ({preferred_match_pct:.0f}%)"
        }

    def _score_role_keywords(self, resume_text: str, role_data: Dict) -> Dict:
        """
        Score role-specific keywords for Quality Coach mode (generous scoring).

        Args:
            resume_text: Full resume text (lowercase)
            role_data: Role-specific scoring criteria

        Returns:
            Dictionary with score and keyword details
        """
        typical_keywords = role_data.get("typical_keywords", [])
        action_verbs = role_data.get("action_verbs", [])

        # Track matched and missing keywords
        matched_keywords = []
        missing_keywords = []
        for keyword in typical_keywords:
            if match_with_synonyms(keyword, resume_text):
                matched_keywords.append(keyword)
            else:
                missing_keywords.append(keyword)

        # Track matched and missing verbs
        matched_verbs = []
        missing_verbs = []
        for verb in action_verbs:
            if match_with_synonyms(verb, resume_text):
                matched_verbs.append(verb)
            else:
                missing_verbs.append(verb)

        keyword_matched = len(matched_keywords)
        verb_matched = len(matched_verbs)
        total_keywords = len(typical_keywords) + len(action_verbs)
        total_matched = keyword_matched + verb_matched
        match_pct = (total_matched / total_keywords * 100) if total_keywords > 0 else 0

        # REALISTIC scoring thresholds for Quality Coach mode
        # With large keyword lists (100+), even good resumes only match 15-25%
        # We focus on absolute counts rather than percentages
        if total_keywords > 100:
            # Large keyword list (corpus-enhanced) - use absolute count thresholds
            if total_matched >= 40:  # Exceptional
                score = 25
            elif total_matched >= 30:  # Excellent (target for 86+ score)
                score = 23
            elif total_matched >= 20:  # Good
                score = 20
            elif total_matched >= 15:  # Decent
                score = 17
            elif total_matched >= 10:  # Fair
                score = 14
            elif total_matched >= 5:  # Minimal
                score = 10
            else:
                score = (total_matched / 5) * 10  # Linear up to 5 matches
        else:
            # Small keyword list (manual only) - use percentage thresholds
            if match_pct >= 60:
                score = 25
            elif match_pct >= 50:
                score = 22
            elif match_pct >= 40:
                score = 18
            elif match_pct >= 30:
                score = 15
            elif match_pct >= 20:
                score = 12
            else:
                score = (match_pct / 20) * 12

        # Cap at maximum score
        score = min(score, 25)

        return {
            "score": score,
            "keyword_details": {
                "keywords_matched": keyword_matched,
                "keywords_total": len(typical_keywords),
                "verbs_matched": verb_matched,
                "verbs_total": len(action_verbs),
                "overall_match_pct": round(match_pct, 1),
                "matched_keywords": matched_keywords,
                "missing_keywords": missing_keywords,
                "matched_verbs": matched_verbs,
                "missing_verbs": missing_verbs
            },
            "details": f"Keywords: {keyword_matched}/{len(typical_keywords)}, "
                      f"Action Verbs: {verb_matched}/{len(action_verbs)} "
                      f"({match_pct:.0f}% match)"
        }

    def _score_content_quality(
        self,
        resume_data: ResumeData,
        resume_text: str,
        role_data: Dict,
        level: str = "mid"
    ) -> Dict:
        """
        Score content quality using ContentImpactAnalyzer (enhanced).

        Uses:
        - Achievement strength (CAR pattern, metrics)
        - Sentence clarity (length, weak phrases, active voice)
        - Specificity (tech, metrics, actions)

        Args:
            resume_data: Parsed resume data
            resume_text: Full resume text
            role_data: Role-specific scoring criteria
            level: Experience level for context-aware scoring

        Returns:
            Dictionary with score and details
        """
        # Initialize analyzers
        impact_analyzer = ContentImpactAnalyzer()
        context_scorer = ContextAwareScorer()

        # Initialize component scores
        achievement_strength = 0
        sentence_clarity = 0
        specificity_score = 0

        # Extract experience bullets (primary content for analysis)
        bullets = []
        if resume_data.experience:
            for exp_item in resume_data.experience:
                # Extract bullets from experience items
                if isinstance(exp_item, dict):
                    if "bullets" in exp_item:
                        bullets.extend(exp_item["bullets"])
                    elif "description" in exp_item:
                        # If description is a list, use it
                        if isinstance(exp_item["description"], list):
                            bullets.extend(exp_item["description"])
                        # If description is a string, split by bullets or newlines
                        elif isinstance(exp_item["description"], str):
                            desc_bullets = [b.strip() for b in exp_item["description"].split('\n')
                                          if b.strip() and (b.strip().startswith('•')
                                                           or b.strip().startswith('-')
                                                           or b.strip().startswith('*'))]
                            if desc_bullets:
                                bullets.extend(desc_bullets)
                            else:
                                # Add the whole description as a single bullet if no bullet markers
                                bullets.append(exp_item["description"])

        # If no structured bullets, fall back to line-by-line from text
        if not bullets:
            # Extract lines that look like bullets
            lines = resume_text.split('\n')
            bullets = [line.strip() for line in lines
                      if line.strip() and (line.strip().startswith('•')
                                          or line.strip().startswith('-')
                                          or line.strip().startswith('*'))]

        # Score impact quality using ContentImpactAnalyzer
        if bullets:
            impact_result = impact_analyzer.score_impact_quality(
                bullets=bullets,
                level=level,
                section="experience"
            )

            # Apply context-aware adjustments
            quality_scores = {
                'achievement_strength': impact_result['achievement_strength'],
                'sentence_clarity': impact_result['sentence_clarity'],
                'specificity': impact_result['specificity']
            }

            adjusted = context_scorer.adjust_quality_score(
                quality_scores,
                level=level,
                section="experience"
            )

            score = adjusted['total_score']
            achievement_strength = adjusted['adjusted_scores'].get('achievement_strength', impact_result['achievement_strength'])
            sentence_clarity = adjusted['adjusted_scores'].get('sentence_clarity', impact_result['sentence_clarity'])
            specificity_score = adjusted['adjusted_scores'].get('specificity', impact_result['specificity'])

            # Generate detailed feedback
            details = [
                f"Achievement strength: {achievement_strength:.1f}/15",
                f"Sentence clarity: {sentence_clarity:.1f}/10",
                f"Specificity: {specificity_score:.1f}/5"
            ]

            if adjusted['adjustments_applied']:
                details.extend(adjusted['adjustments'])
        else:
            # Fallback: simple metrics-based scoring
            score = 10
            details = ["Limited content structure detected"]

            metrics_count = len(re.findall(r'\d+%|\d+\+|\d+x', resume_text))
            if metrics_count >= 3:
                score += 10
                achievement_strength = 5
                details.append(f"Good quantification ({metrics_count} metrics)")
            elif metrics_count >= 1:
                score += 5
                achievement_strength = 3
                details.append(f"Some quantification ({metrics_count} metrics)")

        # Check for action verbs (up to 5 points)
        action_verbs = role_data.get("action_verbs", [])
        verb_matches = sum(1 for verb in action_verbs if match_with_synonyms(verb, resume_text))
        verb_score = min(5, (verb_matches / len(action_verbs)) * 10) if action_verbs else 3

        score += verb_score
        details.append(f"Action verbs: {verb_matches}/{len(action_verbs)}")

        # Cap at maximum score
        score = min(score, 30)

        # Return with component scores for feedback generation
        return {
            "score": score,
            "details": ", ".join(details),
            "achievement_strength": achievement_strength,
            "sentence_clarity": sentence_clarity,
            "specificity": specificity_score
        }

    def _score_professional_polish(self, resume_data: ResumeData, resume_text: str) -> Dict:
        """
        Score professional polish using WritingQualityAnalyzer.

        Checks:
        - Grammar and spelling with severity weighting (10 points)
        - Word count appropriate (5 points)
        - Page count appropriate (3 points)
        - Contact info completeness (2 points)

        Args:
            resume_data: Parsed resume data
            resume_text: Full resume text

        Returns:
            Dictionary with score and details
        """
        score = 0
        details = []

        # Grammar and spelling check with severity weighting (up to 10 points)
        from backend.services.red_flags_validator import RedFlagsValidator
        validator = RedFlagsValidator()
        grammar_issues = validator.validate_grammar(resume_data)

        # Use WritingQualityAnalyzer for severity-weighted scoring
        writing_analyzer = WritingQualityAnalyzer()

        # Convert grammar issues to format expected by analyzer
        # The validator returns issues with 'type' and 'message'
        formatted_errors = []
        for issue in grammar_issues:
            issue_type = issue.get('type', 'grammar')
            # Map validator types to analyzer categories
            category_map = {
                'spelling': 'spelling',
                'grammar': 'grammar',
                'punctuation': 'punctuation',
                'style': 'style',
                'typo': 'spelling'
            }
            category = category_map.get(issue_type, 'grammar')
            formatted_errors.append({
                'category': category,
                'message': issue.get('message', '')
            })

        grammar_result = writing_analyzer.score_grammar_with_severity(formatted_errors)
        grammar_score = grammar_result['score']

        if grammar_result['total_errors'] == 0:
            details.append("Excellent grammar and spelling")
        elif grammar_result['total_errors'] <= 3:
            details.append(f"Minor grammar issues ({grammar_result['total_errors']} found, -{grammar_result['deduction']:.1f} pts)")
        elif grammar_result['total_errors'] <= 7:
            details.append(f"Several grammar issues ({grammar_result['total_errors']} found, -{grammar_result['deduction']:.1f} pts)")
        else:
            details.append(f"Many grammar issues ({grammar_result['total_errors']} found, -{grammar_result['deduction']:.1f} pts)")

        score += grammar_score

        # Word count check (up to 5 points)
        word_count = resume_data.metadata.get("wordCount", 0)
        if 400 <= word_count <= 800:
            word_score = 5
            details.append("Optimal word count")
        elif 300 <= word_count <= 1000:
            word_score = 3
            details.append("Good word count")
        else:
            word_score = 2
            details.append("Word count could be improved")

        score += word_score

        # Page count check (up to 3 points)
        page_count = resume_data.metadata.get("pageCount", 0)
        if page_count <= 2:
            page_score = 3
            details.append("Appropriate length")
        else:
            page_score = 1
            details.append("Resume is long")

        score += page_score

        # Contact info completeness (up to 2 points)
        contact = resume_data.contact
        contact_fields = sum(1 for v in [
            contact.get("name"),
            contact.get("email"),
            contact.get("phone")
        ] if v)

        if contact_fields >= 3:
            contact_score = 2
            details.append("Complete contact info")
        elif contact_fields >= 2:
            contact_score = 1
            details.append("Basic contact info")
        else:
            contact_score = 0
            details.append("Incomplete contact info")

        score += contact_score

        # Cap at maximum score
        score = min(score, 20)

        return {
            "score": score,
            "details": ", ".join(details)
        }

    def _score_format(self, resume_data: ResumeData, resume_text: str) -> Dict:
        """
        Score ATS format compatibility.

        Checks:
        - Has required sections (contact, experience, education)
        - Has skills section
        - Has contact info (email, phone)

        Args:
            resume_data: Parsed resume data
            resume_text: Full resume text

        Returns:
            Dictionary with score and details
        """
        score = 0
        details = []

        # Required sections (15 points total: 5 each)
        if resume_data.contact and (resume_data.contact.get("name") or resume_data.contact.get("email")):
            score += 5
            details.append("Has contact section")
        else:
            details.append("Missing contact section")

        if resume_data.experience and len(resume_data.experience) > 0:
            score += 5
            details.append("Has experience section")
        else:
            details.append("Missing experience section")

        if resume_data.education and len(resume_data.education) > 0:
            score += 5
            details.append("Has education section")
        else:
            details.append("Missing education section")

        # Skills section (3 points)
        if resume_data.skills and len(resume_data.skills) > 0:
            score += 3
            details.append("Has skills section")
        else:
            details.append("Missing skills section")

        # Contact info completeness (2 points)
        contact = resume_data.contact
        if contact.get("email") and contact.get("phone"):
            score += 2
            details.append("Complete contact info")
        elif contact.get("email") or contact.get("phone"):
            score += 1
            details.append("Partial contact info")
        else:
            details.append("No contact info")

        # Cap at maximum score
        score = min(score, 20)

        return {
            "score": score,
            "details": ", ".join(details)
        }

    def _score_structure(self, resume_data: ResumeData) -> Dict:
        """
        Score resume structure quality.

        Checks:
        - Number of experience entries
        - Number of education entries
        - Number of skills

        Args:
            resume_data: Parsed resume data

        Returns:
            Dictionary with score and details
        """
        score = 0
        details = []

        # Experience entries (up to 5 points)
        exp_count = len(resume_data.experience)
        if exp_count >= 3:
            exp_score = 5
            details.append(f"{exp_count} experience entries")
        elif exp_count >= 2:
            exp_score = 4
            details.append(f"{exp_count} experience entries")
        elif exp_count >= 1:
            exp_score = 3
            details.append(f"{exp_count} experience entry")
        else:
            exp_score = 0
            details.append("No experience entries")

        score += exp_score

        # Education entries (up to 3 points)
        edu_count = len(resume_data.education)
        if edu_count >= 1:
            edu_score = 3
            details.append(f"{edu_count} education entry")
        else:
            edu_score = 0
            details.append("No education entries")

        score += edu_score

        # Skills (up to 2 points)
        skills_count = len(resume_data.skills)
        if skills_count >= 5:
            skills_score = 2
            details.append(f"{skills_count} skills")
        elif skills_count >= 3:
            skills_score = 1
            details.append(f"{skills_count} skills")
        else:
            skills_score = 0
            details.append("Few skills listed")

        score += skills_score

        # Cap at maximum score
        score = min(score, 10)

        return {
            "score": score,
            "details": ", ".join(details)
        }

    def _get_resume_text(self, resume_data: ResumeData) -> str:
        """
        Extract all text from resume for keyword matching.

        Args:
            resume_data: Parsed resume data

        Returns:
            Lowercase resume text
        """
        text_parts = []

        # Contact info
        contact = resume_data.contact
        if contact:
            for value in contact.values():
                if value:
                    text_parts.append(str(value))

        # Experience
        for exp in resume_data.experience:
            if exp.get("title"):
                text_parts.append(exp["title"])
            if exp.get("company"):
                text_parts.append(exp["company"])
            if exp.get("description"):
                text_parts.append(exp["description"])

        # Education
        for edu in resume_data.education:
            if edu.get("degree"):
                text_parts.append(edu["degree"])
            if edu.get("institution"):
                text_parts.append(edu["institution"])

        # Skills
        text_parts.extend(resume_data.skills)

        # Certifications
        for cert in resume_data.certifications:
            if cert.get("name"):
                text_parts.append(cert["name"])

        return " ".join(text_parts).lower()

    def _generate_cta(self, overall_score: float) -> str:
        """
        Generate call-to-action based on score.

        Args:
            overall_score: Overall score (0-100)

        Returns:
            Call-to-action message
        """
        if overall_score >= 85:
            return "Your resume is excellent! Ready to apply."
        elif overall_score >= 70:
            return "Your resume is good. Consider minor improvements."
        elif overall_score >= 55:
            return "Your resume needs improvement. Review the feedback."
        else:
            return "Your resume needs significant work. Focus on key areas."

    def _details_to_issues(self, details, score: float, max_score: float) -> List:
        """
        Convert details string or list to issues list with severity tuples.

        Args:
            details: Details string, list, or dict from scoring methods
            score: Actual score achieved
            max_score: Maximum possible score

        Returns:
            List of (severity, message) tuples
        """
        issues = []

        # Handle string details
        if isinstance(details, str):
            if details:
                # Determine severity based on score percentage
                score_pct = (score / max_score * 100) if max_score > 0 else 0
                if score_pct >= 80:
                    severity = "info"
                elif score_pct >= 60:
                    severity = "suggestion"
                elif score_pct >= 40:
                    severity = "warning"
                else:
                    severity = "critical"
                issues.append((severity, details))

        # Handle list details
        elif isinstance(details, list):
            for item in details:
                # If already a tuple, use as-is
                if isinstance(item, tuple) and len(item) == 2:
                    issues.append(item)
                # Otherwise convert string to info tuple
                elif isinstance(item, str):
                    score_pct = (score / max_score * 100) if max_score > 0 else 0
                    if score_pct >= 80:
                        severity = "info"
                    elif score_pct >= 60:
                        severity = "suggestion"
                    elif score_pct >= 40:
                        severity = "warning"
                    else:
                        severity = "critical"
                    issues.append((severity, item))

        return issues


class ResumeScorer:
    """
    Main Scorer Orchestrator - coordinates dual-mode scoring with interpretation.

    Features:
    - Dual-mode support: 'ats' (ATS Simulation) and 'quality' (Quality Coach)
    - Score interpretation layer (0-40: Needs significant improvement, etc.)
    - Caching of validator results for quick mode switching
    - Actionable recommendations based on issues
    - Job description matching support
    """

    def __init__(self):
        """Initialize scorer with caching support"""
        self._adaptive_scorer = AdaptiveScorer()
        self._validation_cache = {}  # Cache validator results by resume hash

    def score(
        self,
        resume: ResumeData,
        role: str,
        level: ExperienceLevel,
        mode: str = 'ats',
        job_description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Score a resume with interpretation and recommendations.

        Args:
            resume: Parsed resume data
            role: Role identifier (e.g., "software_engineer")
            level: Experience level enum
            mode: Scoring mode - 'ats' or 'quality' (default: 'ats')
            job_description: Optional job description for ATS mode

        Returns:
            Dictionary with:
            - score: Overall score (0-100)
            - mode: Scoring mode used
            - interpretation: Human-readable score interpretation
            - breakdown: Detailed scoring breakdown
            - recommendations: List of actionable recommendations
            - issues: Categorized issues (critical, warnings, suggestions, info)
            - strengths: List of resume strengths
            - keyword_details: Keyword matching details
        """
        # Validate mode
        if mode not in ['ats', 'quality']:
            raise ValueError(f"Invalid mode: {mode}. Use 'ats' or 'quality'")

        # For ATS mode, require job description
        if mode == 'ats' and not job_description:
            raise ValueError("job_description is required for ATS mode")

        # Map mode to adaptive scorer mode names
        adaptive_mode = 'ats_simulation' if mode == 'ats' else 'quality_coach'

        # Get score from adaptive scorer
        result = self._adaptive_scorer.score(
            resume_data=resume,
            role_id=role,
            level=level,
            job_description=job_description,
            mode=adaptive_mode
        )

        # Get overall score
        overall_score = result.get('overallScore', 0)

        # Add interpretation layer
        interpretation = self._interpret_score(overall_score)

        # Generate actionable recommendations
        recommendations = self._generate_recommendations(result, mode)

        # Build return structure
        return {
            'score': overall_score,
            'mode': mode,
            'interpretation': interpretation,
            'breakdown': result.get('breakdown', {}),
            'recommendations': recommendations,
            'issues': result.get('issues', {}),
            'strengths': result.get('strengths', []),
            'keyword_details': result.get('keyword_details', {}),
            # Include mode-specific fields
            **({'auto_reject': result.get('auto_reject'),
                'rejection_reason': result.get('rejection_reason')} if mode == 'ats' else {}),
            **({'cta': result.get('cta')} if mode == 'quality' else {})
        }

    def _interpret_score(self, score: float) -> str:
        """
        Interpret score with human-readable labels.

        Score ranges:
        - 0-40: Needs significant improvement
        - 41-60: Needs improvement
        - 61-75: Good
        - 76-85: Very good
        - 86-100: Excellent

        Args:
            score: Overall score (0-100)

        Returns:
            Human-readable interpretation
        """
        if score >= 86:
            return "Excellent"
        elif score >= 76:
            return "Very good"
        elif score >= 61:
            return "Good"
        elif score >= 41:
            return "Needs improvement"
        else:
            return "Needs significant improvement"

    def _generate_recommendations(self, result: Dict, mode: str) -> List[str]:
        """
        Generate actionable recommendations based on issues.

        Args:
            result: Scoring result from adaptive scorer
            mode: Scoring mode ('ats' or 'quality')

        Returns:
            List of actionable recommendation strings
        """
        recommendations = []
        issues = result.get('issues', {})
        breakdown = result.get('breakdown', {})

        # Process critical issues first
        critical_issues = issues.get('critical', [])
        for severity, message in critical_issues:
            recommendations.append(f"CRITICAL: {message}")

        # Process warnings
        warnings = issues.get('warnings', [])
        for severity, message in warnings[:3]:  # Top 3 warnings
            recommendations.append(f"WARNING: {message}")

        # Mode-specific recommendations based on breakdown
        if mode == 'ats':
            keyword_details = result.get('keyword_details', {})

            # Keyword recommendations
            if keyword_details.get('required_match_pct', 0) < 80:
                required_matched = keyword_details.get('required_matched', 0)
                required_total = keyword_details.get('required_total', 0)
                missing = required_total - required_matched
                recommendations.append(
                    f"Add {missing} missing required keywords to improve ATS compatibility"
                )

            if keyword_details.get('preferred_match_pct', 0) < 60:
                preferred_matched = keyword_details.get('preferred_matched', 0)
                preferred_total = keyword_details.get('preferred_total', 0)
                missing = preferred_total - preferred_matched
                recommendations.append(
                    f"Include {missing} more preferred keywords to stand out"
                )

            # Format recommendations
            format_data = breakdown.get('format', {})
            if format_data.get('score', 0) < 15:
                recommendations.append(
                    "Improve resume format: ensure all required sections are present"
                )

            # Structure recommendations
            structure_data = breakdown.get('structure', {})
            if structure_data.get('score', 0) < 7:
                recommendations.append(
                    "Add more details to experience and skills sections"
                )

        else:  # quality mode
            # Role keywords recommendations with specific details
            role_kw_data = breakdown.get('role_keywords', {})
            kw_details = role_kw_data.get('keyword_details', {})

            if role_kw_data.get('score', 0) < 18:
                missing_kw = kw_details.get('missing_keywords', [])
                missing_verbs = kw_details.get('missing_verbs', [])
                matched_kw = kw_details.get('matched_keywords', [])
                matched_verbs = kw_details.get('matched_verbs', [])

                # Build detailed recommendation
                if missing_kw:
                    top_missing = missing_kw[:5]  # Show top 5 missing
                    recommendations.append(
                        f"Missing role keywords: {', '.join(top_missing)}" +
                        (f" +{len(missing_kw)-5} more" if len(missing_kw) > 5 else "")
                    )

                if missing_verbs:
                    top_missing_verbs = missing_verbs[:5]
                    recommendations.append(
                        f"Missing action verbs: {', '.join(top_missing_verbs)}" +
                        (f" +{len(missing_verbs)-5} more" if len(missing_verbs) > 5 else "")
                    )

                if matched_kw:
                    recommendations.append(
                        f"✓ Present: {', '.join(matched_kw[:3])}" +
                        (f" +{len(matched_kw)-3} more" if len(matched_kw) > 3 else "")
                    )

            # Content quality recommendations
            content_data = breakdown.get('content_quality', {})
            if content_data.get('score', 0) < 24:
                recommendations.append(
                    "Quantify achievements with metrics (percentages, numbers, impact)"
                )
                recommendations.append(
                    "Use more bullet points and strong action verbs"
                )

            # Format recommendations
            format_data = breakdown.get('format', {})
            if format_data.get('score', 0) < 20:
                recommendations.append(
                    "Ensure all standard resume sections are complete and well-formatted"
                )

            # Professional polish recommendations
            polish_data = breakdown.get('professional_polish', {})
            if polish_data.get('score', 0) < 15:
                recommendations.append(
                    "Optimize resume length and ensure complete contact information"
                )

        # Add suggestions if we have room (max 7 recommendations)
        suggestions = issues.get('suggestions', [])
        remaining_slots = 7 - len(recommendations)
        for severity, message in suggestions[:remaining_slots]:
            recommendations.append(f"TIP: {message}")

        # If no specific recommendations, add generic positive message
        if not recommendations:
            recommendations.append("Your resume looks great! Keep it updated regularly.")

        return recommendations[:7]  # Cap at 7 recommendations

    def cache_validation_results(self, resume_hash: str, validation_results: Dict):
        """
        Cache validator results for quick mode switching.

        Args:
            resume_hash: Unique hash of resume content
            validation_results: Validation results to cache
        """
        self._validation_cache[resume_hash] = validation_results

    def get_cached_validation(self, resume_hash: str) -> Optional[Dict]:
        """
        Get cached validator results if available.

        Args:
            resume_hash: Unique hash of resume content

        Returns:
            Cached validation results or None
        """
        return self._validation_cache.get(resume_hash)

    def clear_cache(self):
        """Clear all cached validation results"""
        self._validation_cache.clear()
