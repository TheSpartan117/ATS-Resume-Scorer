"""
Adaptive ATS Scorer with dual-mode scoring.

This module provides intelligent scoring with two modes:
- Mode A (ATS Simulation): Harsh keyword-heavy scoring (70/20/10)
- Mode B (Quality Coach): Balanced quality scoring (25/30/25/20)

The mode is auto-detected based on job description presence.
"""

import re
from typing import Dict, List, Optional
from services.keyword_extractor import extract_keywords_from_jd, match_with_synonyms
from services.role_taxonomy import ExperienceLevel, get_role_scoring_data
from services.parser import ResumeData


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

        # 2. Content Quality (30 points) - Simplified
        content_result = self._score_content_quality(resume_data, resume_text, role_data)
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
            "cta": self._generate_cta(overall_score)
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

        # Count keyword matches
        keyword_matched = 0
        for keyword in typical_keywords:
            if match_with_synonyms(keyword, resume_text):
                keyword_matched += 1

        # Count action verb matches
        verb_matched = 0
        for verb in action_verbs:
            if match_with_synonyms(verb, resume_text):
                verb_matched += 1

        total_keywords = len(typical_keywords) + len(action_verbs)
        total_matched = keyword_matched + verb_matched
        match_pct = (total_matched / total_keywords * 100) if total_keywords > 0 else 0

        # Generous scoring thresholds for Quality Coach mode
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
            score = (match_pct / 20) * 12  # Linear up to 20%

        return {
            "score": score,
            "keyword_details": {
                "keywords_matched": keyword_matched,
                "keywords_total": len(typical_keywords),
                "verbs_matched": verb_matched,
                "verbs_total": len(action_verbs),
                "overall_match_pct": round(match_pct, 1)
            },
            "details": f"Keywords: {keyword_matched}/{len(typical_keywords)}, "
                      f"Action Verbs: {verb_matched}/{len(action_verbs)} "
                      f"({match_pct:.0f}% match)"
        }

    def _score_content_quality(
        self,
        resume_data: ResumeData,
        resume_text: str,
        role_data: Dict
    ) -> Dict:
        """
        Score content quality (simplified for MVP).

        Checks:
        - Metrics/quantification (numbers with %)
        - Bullet point format
        - Action verbs usage

        Args:
            resume_data: Parsed resume data
            resume_text: Full resume text
            role_data: Role-specific scoring criteria

        Returns:
            Dictionary with score and details
        """
        score = 0
        details = []

        # Check for metrics (up to 15 points)
        metrics_count = len(re.findall(r'\d+%|\d+\+|\d+x', resume_text))
        metrics_expected = role_data.get("metrics_expected", 3)

        if metrics_count >= metrics_expected:
            metrics_score = 15
            details.append(f"Excellent quantification ({metrics_count} metrics)")
        elif metrics_count >= metrics_expected * 0.7:
            metrics_score = 12
            details.append(f"Good quantification ({metrics_count} metrics)")
        elif metrics_count >= metrics_expected * 0.4:
            metrics_score = 8
            details.append(f"Some quantification ({metrics_count} metrics)")
        else:
            metrics_score = 5
            details.append(f"Limited quantification ({metrics_count} metrics)")

        score += metrics_score

        # Check for bullet points (up to 10 points)
        bullet_count = resume_text.count('•') + resume_text.count('-')
        if bullet_count >= 10:
            bullet_score = 10
            details.append("Good use of bullet points")
        elif bullet_count >= 5:
            bullet_score = 7
            details.append("Some bullet points")
        else:
            bullet_score = 4
            details.append("Limited bullet points")

        score += bullet_score

        # Check for action verbs (up to 5 points)
        action_verbs = role_data.get("action_verbs", [])
        verb_matches = sum(1 for verb in action_verbs if match_with_synonyms(verb, resume_text))
        verb_score = min(5, (verb_matches / len(action_verbs)) * 10) if action_verbs else 3

        score += verb_score
        details.append(f"Action verbs: {verb_matches}/{len(action_verbs)}")

        return {
            "score": score,
            "details": ", ".join(details)
        }

    def _score_professional_polish(self, resume_data: ResumeData, resume_text: str) -> Dict:
        """
        Score professional polish (simplified for MVP).

        Checks:
        - Word count appropriate
        - No obvious typos
        - Professional formatting

        Args:
            resume_data: Parsed resume data
            resume_text: Full resume text

        Returns:
            Dictionary with score and details
        """
        score = 0
        details = []

        # Word count check (up to 10 points)
        word_count = resume_data.metadata.get("wordCount", 0)
        if 400 <= word_count <= 800:
            word_score = 10
            details.append("Optimal word count")
        elif 300 <= word_count <= 1000:
            word_score = 7
            details.append("Good word count")
        else:
            word_score = 4
            details.append("Word count could be improved")

        score += word_score

        # Page count check (up to 5 points)
        page_count = resume_data.metadata.get("pageCount", 0)
        if page_count <= 2:
            page_score = 5
            details.append("Appropriate length")
        else:
            page_score = 2
            details.append("Resume is long")

        score += page_score

        # Contact info completeness (up to 5 points)
        contact = resume_data.contact
        contact_fields = sum(1 for v in [
            contact.get("name"),
            contact.get("email"),
            contact.get("phone")
        ] if v)

        if contact_fields >= 3:
            contact_score = 5
            details.append("Complete contact info")
        elif contact_fields >= 2:
            contact_score = 3
            details.append("Basic contact info")
        else:
            contact_score = 1
            details.append("Incomplete contact info")

        score += contact_score

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
