"""Upload endpoint for resume file upload and initial scoring"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timezone
import io

from database import get_db
from services.parser import parse_pdf, parse_docx
from services.scorer import calculate_overall_score
from schemas.resume import UploadResponse, ContactInfoResponse, MetadataResponse, ScoreResponse, CategoryBreakdown

router = APIRouter(prefix="/api", tags=["upload"])

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_TYPES = ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]


@router.post("/upload", response_model=UploadResponse)
async def upload_resume(
    file: UploadFile = File(...),
    jobDescription: Optional[str] = Form(None),
    industry: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Upload a resume file (PDF or DOCX), parse it, and get an initial ATS score.

    - **file**: PDF or DOCX resume file (max 10MB)
    - **jobDescription**: (Optional) Job description for keyword matching
    - **industry**: (Optional) Industry for tailored scoring (e.g., "tech", "sales")

    Returns parsed resume data with comprehensive ATS score (0-100).
    """

    # Validate file type
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Please upload PDF or DOCX only"
        )

    # Read file content
    file_content = await file.read()

    # Validate file size
    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum {MAX_FILE_SIZE // (1024*1024)}MB"
        )

    # Parse resume based on file type
    try:
        if file.content_type == "application/pdf":
            resume_data = parse_pdf(file_content, file.filename)
        else:  # DOCX
            resume_data = parse_docx(file_content, file.filename)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Unable to read file. May be corrupted or password-protected: {str(e)}"
        )

    # Check if resume is empty
    if resume_data.metadata.get("wordCount", 0) < 50:
        raise HTTPException(
            status_code=400,
            detail="Resume appears empty or unreadable"
        )

    # Calculate score
    score_result = calculate_overall_score(
        resume_data,
        job_description=jobDescription or "",
        industry=industry or ""
    )

    # Format response
    contact_response = ContactInfoResponse(**resume_data.contact)
    metadata_response = MetadataResponse(**resume_data.metadata)

    # Convert score breakdown to response format
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

    score_response = ScoreResponse(
        overallScore=score_result["overallScore"],
        breakdown=breakdown_response,
        issues=issues_response,
        strengths=score_result.get("strengths", [])
    )

    return UploadResponse(
        resumeId=None,  # Guest user, no saved resume
        fileName=file.filename,
        contact=contact_response,
        metadata=metadata_response,
        score=score_response,
        uploadedAt=datetime.now(timezone.utc)
    )
