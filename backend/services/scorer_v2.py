"""
Adaptive Scorer V2 - Stub implementation for testing
This is a minimal implementation to allow parser tests to run.
"""
from typing import Dict, Optional
from backend.services.parser import ResumeData
from backend.services.scorer import calculate_overall_score


class AdaptiveScorer:
    """Adaptive scorer that routes to appropriate scoring logic based on mode"""

    def score(
        self,
        resume_data: ResumeData,
        role_id: Optional[str] = None,
        level: Optional[str] = None,
        job_description: Optional[str] = None,
        mode: str = "quality_coach"
    ) -> Dict:
        """
        Score a resume using the appropriate mode.

        Args:
            resume_data: Parsed resume data
            role_id: Role identifier (e.g., "software_engineer")
            level: Experience level (e.g., "senior", "mid", "junior")
            job_description: Optional job description for ATS simulation mode
            mode: Scoring mode - "ats_simulation" or "quality_coach"

        Returns:
            Dict with scoring results including overallScore, categories, suggestions
        """
        # For now, delegate to the existing scorer
        # This is a stub - the real implementation would have role-based logic
        result = calculate_overall_score(resume_data)

        # Add mode info to result
        result['mode'] = mode
        result['role'] = role_id
        result['level'] = level

        return result
