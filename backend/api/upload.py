"""Upload endpoint for resume file upload and initial scoring"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional
from datetime import datetime, timezone
import io
import logging
from backend.services.parser import parse_pdf, parse_docx
from backend.services.scorer import calculate_overall_score
from backend.services.format_checker import ATSFormatChecker
from backend.schemas.resume import UploadResponse, ContactInfoResponse, MetadataResponse, ScoreResponse, CategoryBreakdown, FormatCheckResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["upload"])

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_TYPES = ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]


@router.post("/upload", response_model=UploadResponse)
async def upload_resume(
    file: UploadFile = File(...),
    jobDescription: Optional[str] = Form(None),
    role: Optional[str] = Form(None),
    level: Optional[str] = Form(None),
    industry: Optional[str] = Form(None)  # Kept for backward compatibility
):
    """
    Upload a resume file (PDF or DOCX), parse it, and get an initial ATS score.

    - **file**: PDF or DOCX resume file (max 10MB)
    - **jobDescription**: (Optional) Job description for keyword matching
    - **role**: (Optional) Role identifier for tailored scoring (e.g., "software_engineer", "product_manager")
    - **level**: (Optional) Experience level ("entry", "mid", "senior", "lead", "executive")
    - **industry**: (Optional, deprecated) Use role+level instead

    Returns parsed resume data with comprehensive ATS score (0-100).
    """

    # Validate file type
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Please upload PDF or DOCX only"
        )

    # Validate file size before reading into memory
    if hasattr(file.file, 'seek') and hasattr(file.file, 'tell'):
        file.file.seek(0, 2)  # Seek to end to get size
        file_size = file.file.tell()
        file.file.seek(0)  # Reset to beginning

        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum {MAX_FILE_SIZE // (1024*1024)}MB"
            )

    # Now read file content
    file_content = await file.read()

    # Parse resume based on file type
    try:
        if file.content_type == "application/pdf":
            resume_data = parse_pdf(file_content, file.filename)
        else:  # DOCX
            resume_data = parse_docx(file_content, file.filename)

        # Debug logging
        logger.info(f"Parsed resume - Word count: {resume_data.metadata.get('wordCount', 0)}")
        logger.info(f"Experience entries: {len(resume_data.experience)}")
        logger.info(f"Education entries: {len(resume_data.education)}")
        logger.info(f"Skills count: {len(resume_data.skills)}")
        if resume_data.experience:
            logger.info(f"First experience entry: {str(resume_data.experience[0])[:200]}")
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

    # Run format compatibility check
    try:
        format_checker = ATSFormatChecker()
        # Get raw text for format check (reconstruct from parsed data)
        raw_text = " ".join([
            " ".join([str(exp) for exp in resume_data.experience]),
            " ".join([str(edu) for edu in resume_data.education]),
            " ".join(resume_data.skills)
        ])
        logger.info(f"Running format check with raw_text length: {len(raw_text)}")
        format_check_result = format_checker.check_format(resume_data, raw_text)
        logger.info(f"Format check passed: {format_check_result.get('passed', False)}")
    except Exception as e:
        logger.error(f"Format check failed: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Format check failed: {str(e)}")

    # Calculate score with role and level (or fall back to industry for backward compatibility)
    try:
        logger.info(f"Calculating score with role={role}, level={level}")
        score_result = calculate_overall_score(
            resume_data,
            job_description=jobDescription or "",
            role_id=role or "",
            level=level or "",
            industry=industry or ""
        )
        logger.info(f"Score calculated: {score_result.get('overallScore', 0)}")
    except Exception as e:
        logger.error(f"Scoring failed: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Scoring failed: {str(e)}")

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

    # Format check response
    format_check_response = FormatCheckResponse(
        passed=format_check_result["passed"],
        score=format_check_result["score"],
        checks=format_check_result["checks"],
        issues=format_check_result["issues"]
    )

    return UploadResponse(
        resumeId=None,  # Guest user, no saved resume
        fileName=file.filename,
        contact=contact_response,
        experience=resume_data.experience,
        education=resume_data.education,
        skills=resume_data.skills,
        certifications=resume_data.certifications,
        metadata=metadata_response,
        score=score_response,
        formatCheck=format_check_response,
        uploadedAt=datetime.now(timezone.utc),
        jobDescription=jobDescription,
        industry=industry
    )
