"""Score endpoint for re-scoring updated resume data"""
from fastapi import APIRouter, HTTPException
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

from services.parser import ResumeData
from services.scorer import calculate_overall_score
from schemas.resume import ScoreResponse, CategoryBreakdown


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
    industry: Optional[str] = ""


@router.post("/score", response_model=ScoreResponse)
async def score_resume(request: ScoreRequest):
    """
    Re-score a resume with updated data (e.g., after editing).

    Used by the frontend editor to get updated scores as user makes changes.

    - **request**: Complete resume data structure
    - **jobDescription**: (Optional) Job description for keyword matching
    - **industry**: (Optional) Industry for tailored scoring

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

    # Calculate score
    score_result = calculate_overall_score(
        resume_data,
        job_description=request.jobDescription or "",
        industry=request.industry or ""
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
        strengths=score_result.get("strengths", [])
    )
