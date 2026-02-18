"""
ATS Format Checker - Validates resume parseability and ATS compatibility
"""
import re
from typing import Dict, List
from services.parser import ResumeData


class ATSFormatChecker:
    """Checks if resume format is ATS-compatible"""

    def check_format(self, resume: ResumeData, raw_text: str) -> Dict:
        """
        Check resume format for ATS compatibility.

        Args:
            resume: Parsed resume data
            raw_text: Raw extracted text from file

        Returns:
            Dict with passed (bool), score (float 0-1), checks (dict), issues (list)
        """
        checks = {
            "text_extraction": self._check_extraction_quality(raw_text),
            "sections_detected": self._check_sections(resume),
            "bullets_parsed": self._check_bullets(resume),
            "file_size": self._check_file_size(resume.metadata),
            "special_chars": self._check_special_characters(raw_text)
        }

        overall_score = self._calculate_format_score(checks)
        issues = self._identify_format_issues(checks)

        return {
            "passed": overall_score >= 0.8,
            "score": overall_score,
            "checks": checks,
            "issues": issues
        }

    def _check_extraction_quality(self, text: str) -> Dict:
        """Check if text extraction succeeded"""
        word_count = len(text.split())

        # Check for garbled characters
        garbled_pattern = r'[^\x00-\x7F\u0080-\uFFFF]'
        garbled_count = len(re.findall(garbled_pattern, text))

        quality = 1.0
        if word_count < 50:
            quality = 0.3  # Very little text extracted
        elif word_count < 150:
            quality = 0.6  # Some text but seems incomplete
        elif garbled_count > word_count * 0.1:
            quality = 0.5  # Too many garbled characters

        return {
            "passed": quality >= 0.7,
            "score": quality,
            "word_count": word_count,
            "garbled_chars": garbled_count
        }

    def _check_sections(self, resume: ResumeData) -> Dict:
        """Check if major sections were detected"""
        has_experience = len(resume.experience) > 0
        has_education = len(resume.education) > 0
        has_skills = len(resume.skills) > 0

        sections_found = sum([has_experience, has_education, has_skills])
        score = sections_found / 3.0  # All 3 sections = 1.0

        return {
            "passed": sections_found >= 2,  # At least 2 of 3 sections
            "score": score,
            "experience_found": has_experience,
            "education_found": has_education,
            "skills_found": has_skills
        }

    def _check_bullets(self, resume: ResumeData) -> Dict:
        """Check if bullet points were parsed"""
        total_bullets = 0
        for exp in resume.experience:
            if isinstance(exp, dict) and "description" in exp:
                desc = exp.get("description", "")
                bullets = [line for line in desc.split('\n') if line.strip().startswith('-')]
                total_bullets += len(bullets)

        score = 1.0 if total_bullets >= 5 else (total_bullets / 5.0)

        return {
            "passed": total_bullets >= 3,
            "score": score,
            "bullets_found": total_bullets
        }

    def _check_file_size(self, metadata: Dict) -> Dict:
        """Check if file size is reasonable for ATS"""
        # Estimate file size from word count (rough heuristic)
        word_count = metadata.get("wordCount", 0)
        estimated_size_kb = word_count * 0.5  # Rough estimate

        # ATS systems typically limit to 2MB
        passed = estimated_size_kb < 2000  # 2MB in KB

        return {
            "passed": passed,
            "score": 1.0 if passed else 0.5,
            "estimated_size_kb": estimated_size_kb
        }

    def _check_special_characters(self, text: str) -> Dict:
        """Check for problematic special characters"""
        # Common problematic chars that ATS systems struggle with
        problematic = ['�', '�', '�', '\x00', '\ufffd']

        problem_count = sum(text.count(char) for char in problematic)
        score = 1.0 if problem_count == 0 else max(0.0, 1.0 - (problem_count / 10))

        return {
            "passed": problem_count < 5,
            "score": score,
            "problem_chars_found": problem_count
        }

    def _calculate_format_score(self, checks: Dict) -> float:
        """Calculate overall format score from individual checks"""
        # Weighted average
        weights = {
            "text_extraction": 0.30,
            "sections_detected": 0.30,
            "bullets_parsed": 0.20,
            "file_size": 0.10,
            "special_chars": 0.10
        }

        total_score = 0.0
        for check_name, weight in weights.items():
            total_score += checks[check_name]["score"] * weight

        return total_score

    def _identify_format_issues(self, checks: Dict) -> List[str]:
        """Identify specific issues from checks"""
        issues = []

        if not checks["text_extraction"]["passed"]:
            word_count = checks["text_extraction"]["word_count"]
            if word_count < 50:
                issues.append("Very little text extracted - file may be image-based or corrupted")
            garbled = checks["text_extraction"]["garbled_chars"]
            if garbled > 10:
                issues.append(f"Found {garbled} garbled characters - encoding issues detected")

        if not checks["sections_detected"]["passed"]:
            missing = []
            if not checks["sections_detected"]["experience_found"]:
                missing.append("Experience")
            if not checks["sections_detected"]["education_found"]:
                missing.append("Education")
            if not checks["sections_detected"]["skills_found"]:
                missing.append("Skills")
            issues.append(f"Missing sections: {', '.join(missing)}")

        if not checks["bullets_parsed"]["passed"]:
            bullets = checks["bullets_parsed"]["bullets_found"]
            issues.append(f"Only {bullets} bullet points detected - use bullet lists (-, •, *)")

        if not checks["file_size"]["passed"]:
            size = checks["file_size"]["estimated_size_kb"]
            issues.append(f"File may be too large ({size:.0f}KB) - keep under 2MB")

        if not checks["special_chars"]["passed"]:
            issues.append("Special characters detected - may cause parsing issues in ATS systems")

        return issues


# For backward compatibility with test imports
FormatCheckResult = Dict
