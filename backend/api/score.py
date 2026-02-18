"""Score endpoint for re-scoring updated resume data"""
from fastapi import APIRouter, HTTPException
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

from backend.services.parser import ResumeData
from backend.services.scorer_v2 import AdaptiveScorer
from backend.services.role_taxonomy import get_role_scoring_data, ExperienceLevel
from backend.schemas.resume import ScoreResponse, CategoryBreakdown


router = APIRouter(prefix="/api", tags=["score"])


class ScoreRequest(BaseModel):
    """Request body for score endpoint"""
    fileName: str
    contact: Dict[str, Optional[str]]
    experience: List[Dict] = Field(default_factory=list)
    education: List[Dict] = Field(default_factory=list)
    skills: List[str] = Field(default_factory=list)
    certifications: List[Dict] = Field(default_factory=list)
    metadata: Dict
    jobDescription: Optional[str] = ""
    role: Optional[str] = ""
    level: Optional[str] = ""
    industry: Optional[str] = ""  # Deprecated, kept for backward compatibility


@router.post("/score", response_model=ScoreResponse)
async def score_resume(request: ScoreRequest):
    """
    Re-score a resume with updated data (e.g., after editing).

    Used by the frontend editor to get updated scores as user makes changes.

    - **request**: Complete resume data structure
    - **jobDescription**: (Optional) Job description for keyword matching
    - **role**: (Optional) Role identifier (e.g., "software_engineer", "product_manager")
    - **level**: (Optional) Experience level ("entry", "mid", "senior", "lead", "executive")
    - **industry**: (Optional, deprecated) Use role+level instead

    Returns updated ATS score (0-100).
    """

    # Convert request to ResumeData
    resume_data = ResumeData(
        fileName=request.fileName,
        contact=request.contact,
        experience=request.experience,
        education=request.education,
        skills=request.skills,
        certifications=request.certifications,
        metadata=request.metadata
    )

    # Determine scoring mode
    scoring_mode = "ats_simulation" if request.jobDescription else "quality_coach"

    # Calculate score using AdaptiveScorer
    scorer = AdaptiveScorer()
    score_result = scorer.score(
        resume_data=resume_data,
        role_id=request.role or "software_engineer",
        level=request.level or "mid",
        job_description=request.jobDescription,
        mode=scoring_mode
    )

    # Convert breakdown to response format
    breakdown_response = {}
    for category, details in score_result["breakdown"].items():
        # Extract issue messages from tuples (severity, message)
        issue_messages = [issue[1] if isinstance(issue, tuple) else issue for issue in details["issues"]]
        breakdown_response[category] = CategoryBreakdown(
            score=details["score"],
            maxScore=details["maxScore"],
            issues=issue_messages
        )

    # Convert issues format - extract messages from tuples
    issues_response = {}
    for severity, issue_list in score_result["issues"].items():
        issues_response[severity] = [issue[1] if isinstance(issue, tuple) else issue for issue in issue_list]

    return ScoreResponse(
        overallScore=score_result["overallScore"],
        breakdown=breakdown_response,
        issues=issues_response,
        strengths=score_result.get("strengths", []),
        mode=score_result.get("mode", scoring_mode),
        keywordDetails=score_result.get("keyword_details"),
        autoReject=score_result.get("auto_reject")
    )
