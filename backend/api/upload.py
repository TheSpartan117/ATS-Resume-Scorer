"""Upload endpoint for resume file upload and initial scoring"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from typing import Optional
from datetime import datetime, timezone
import io
import os
import uuid
import logging
from pathlib import Path
from backend.services.parser import parse_pdf, parse_docx
# Removed legacy scorer import - using scorer_v2.AdaptiveScorer instead
from backend.services.scorer_v2 import AdaptiveScorer
from backend.services.format_checker import ATSFormatChecker
from backend.services.docx_to_pdf import convert_docx_to_pdf
from backend.services.document_to_html import docx_to_html, pdf_to_html
from backend.services.pdf_to_docx import convert_pdf_to_docx
from backend.services.docx_to_html_advanced import docx_to_html_advanced
from backend.services.section_detector import SectionDetector
from backend.services.docx_template_manager import DocxTemplateManager
from backend.services.scoring_utils import normalize_scoring_mode
from backend.schemas.resume import UploadResponse, ContactInfoResponse, MetadataResponse, ScoreResponse, CategoryBreakdown, FormatCheckResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["upload"])

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_TYPES = ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]

# Storage directory for uploaded files
UPLOAD_DIR = Path(__file__).parent.parent / "storage" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/upload", response_model=UploadResponse)
async def upload_resume(
    file: UploadFile = File(...),
    role: str = Form(...),
    level: str = Form(...),
    jobDescription: Optional[str] = Form(None),
    mode: Optional[str] = Form("auto"),  # "ats", "quality", or "auto" (default)
    industry: Optional[str] = Form(None)  # Kept for backward compatibility
):
    """
    Upload a resume file (PDF or DOCX), parse it, and get an initial score.

    - **file**: PDF or DOCX resume file (max 10MB)
    - **jobDescription**: (Optional) Job description for keyword matching
    - **role**: (Optional) Role identifier for tailored scoring (e.g., "software_engineer", "product_manager")
    - **level**: (Optional) Experience level ("entry", "mid", "senior", "lead", "executive")
    - **mode**: (Optional) Scoring mode: "ats", "quality", or "auto" (default: "auto")
        - "ats" or "ats_simulation": ATS Simulation mode (keyword-heavy)
        - "quality" or "quality_coach": Quality Coach mode (balanced quality)
        - "auto": Auto-detect based on job description presence
    - **industry**: (Optional, deprecated) Use role+level instead

    Returns parsed resume data with comprehensive score (0-100) in selected mode.
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
    original_content_type = file.content_type

    # Convert PDF to DOCX for better formatting preservation
    docx_content = None
    if file.content_type == "application/pdf":
        try:
            logger.info("Converting PDF to DOCX for better formatting preservation...")
            docx_content = convert_pdf_to_docx(file_content)
            logger.info(f"PDF converted to DOCX successfully ({len(docx_content)} bytes)")
        except Exception as e:
            logger.warning(f"PDF to DOCX conversion failed, will process as PDF: {str(e)}")
            # Continue with PDF if conversion fails
            docx_content = None

    # Save original file for preview
    file_id = str(uuid.uuid4())
    file_extension = ".pdf" if file.content_type == "application/pdf" else ".docx"
    file_path = UPLOAD_DIR / f"{file_id}{file_extension}"

    with open(file_path, "wb") as f:
        f.write(file_content)

    logger.info(f"Saved original file: {file_path}")

    # If we converted to DOCX, also save the converted version
    docx_file_path = None
    if docx_content:
        docx_file_path = UPLOAD_DIR / f"{file_id}_converted.docx"
        with open(docx_file_path, "wb") as f:
            f.write(docx_content)
        logger.info(f"Saved converted DOCX: {docx_file_path}")

    # For DOCX files, also convert to PDF for preview
    preview_pdf_url = None
    if file.content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        try:
            logger.info("Converting DOCX to PDF for preview...")
            pdf_bytes = convert_docx_to_pdf(file_content)
            preview_pdf_path = UPLOAD_DIR / f"{file_id}_preview.pdf"
            with open(preview_pdf_path, "wb") as f:
                f.write(pdf_bytes)
            preview_pdf_url = f"/api/files/{file_id}_preview.pdf"
            logger.info(f"Saved preview PDF: {preview_pdf_path}")
        except Exception as e:
            logger.error(f"Failed to convert DOCX to PDF: {str(e)}")
            # Continue without preview - not critical

    # Convert to editable HTML with formatting preserved
    # Use converted DOCX if available for better formatting
    editable_html = None
    try:
        logger.info("Converting document to editable HTML with advanced converter...")
        if docx_content:
            # Use converted DOCX for HTML generation with advanced converter
            editable_html = docx_to_html_advanced(docx_content)
            logger.info("Generated editable HTML from converted DOCX (advanced)")
        elif original_content_type == "application/pdf":
            editable_html = pdf_to_html(file_content)
            logger.info("Generated editable HTML from PDF")
        else:  # Original DOCX
            editable_html = docx_to_html_advanced(file_content)
            logger.info("Generated editable HTML from DOCX (advanced)")
        logger.info(f"Editable HTML length: {len(editable_html)} chars")
    except Exception as e:
        logger.error(f"Failed to convert to HTML with advanced converter: {str(e)}")
        logger.info("Falling back to basic converter...")
        try:
            if docx_content:
                editable_html = docx_to_html(docx_content)
            elif original_content_type == "application/pdf":
                editable_html = pdf_to_html(file_content)
            else:
                editable_html = docx_to_html(file_content)
            logger.info("Fallback conversion successful")
        except Exception as e2:
            logger.error(f"Fallback conversion also failed: {str(e2)}")
            # Continue without editable HTML - not critical

    # Parse resume based on file type
    # Use converted DOCX if available for better parsing
    try:
        if docx_content:
            logger.info("Parsing converted DOCX (from PDF)")
            resume_data = parse_docx(docx_content, file.filename)
        elif original_content_type == "application/pdf":
            logger.info("Parsing original PDF")
            resume_data = parse_pdf(file_content, file.filename)
        else:  # Original DOCX
            logger.info("Parsing original DOCX")
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

    # Save template and detect sections
    session_id = None
    sections = []
    preview_url = None

    # Only save template if we have DOCX content (either original or converted)
    if docx_content or original_content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        try:
            # Generate session ID
            session_id = str(uuid.uuid4())

            # Save template (use converted DOCX if available, else original DOCX)
            template_manager = DocxTemplateManager()
            template_bytes = docx_content if docx_content else file_content
            template_manager.save_template(session_id, template_bytes)

            logger.info(f"Saved template for session: {session_id}")

            # Detect sections
            section_detector = SectionDetector()
            sections = section_detector.detect(template_bytes)

            logger.info(f"Detected {len(sections)} sections")

            # Generate preview URL
            preview_url = f"/api/preview/{session_id}.docx"

        except Exception as e:
            logger.error(f"Failed to save template or detect sections: {e}")
            # Continue without template (graceful degradation)
            session_id = None
            sections = []
            preview_url = None

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

    # Normalize mode parameter using utility function
    scoring_mode = normalize_scoring_mode(mode or "auto", jobDescription or "")
    logger.info(f"Scoring mode: {scoring_mode}")

    # Use adaptive scorer
    scorer = AdaptiveScorer()

    try:
        logger.info(f"Calculating score with role={role}, level={level}, mode={scoring_mode}")
        score_result = scorer.score(
            resume_data=resume_data,
            role_id=role,
            level=level,
            job_description=jobDescription,
            mode=scoring_mode
        )
        logger.info(f"Score calculated: {score_result.get('overallScore', 0)}")

        # Enrich with enhanced suggestions
        from backend.services.suggestion_integrator import SuggestionIntegrator
        score_result = SuggestionIntegrator.enrich_score_result(
            score_result=score_result,
            resume_data=resume_data,
            role=role,
            level=level,
            job_description=jobDescription or ""
        )
        logger.info(f"Enhanced suggestions added: {len(score_result.get('enhanced_suggestions', []))}")
    except Exception as e:
        logger.error(f"Scoring failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to score resume: {str(e)}")

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

    # Calculate issue counts for frontend
    issue_counts = {
        "critical": len(issues_response.get("critical", [])),
        "warnings": len(issues_response.get("warnings", [])),
        "suggestions": len(issues_response.get("suggestions", []))
    }

    # Extract enhanced suggestions
    enhanced_suggestions = score_result.get("enhanced_suggestions", [])

    score_response = ScoreResponse(
        overallScore=score_result["overallScore"],
        breakdown=breakdown_response,
        issues=issues_response,
        strengths=score_result.get("strengths", []),
        mode=score_result.get("mode", scoring_mode),
        keywordDetails=score_result.get("keyword_details"),
        autoReject=score_result.get("auto_reject"),
        issueCounts=issue_counts,
        enhancedSuggestions=enhanced_suggestions
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
        fileId=file_id,
        originalFileUrl=f"/api/files/{file_id}{file_extension}",
        previewPdfUrl=preview_pdf_url,  # Only set for DOCX files
        editableHtml=editable_html,  # Rich HTML for WYSIWYG editing
        contact=contact_response,
        experience=resume_data.experience,
        education=resume_data.education,
        skills=resume_data.skills,
        certifications=resume_data.certifications,
        metadata=metadata_response,
        score=score_response,
        formatCheck=format_check_response,
        scoringMode=scoring_mode,
        role=role,
        level=level,
        jobDescription=jobDescription,
        uploadedAt=datetime.now(timezone.utc),
        industry=industry,
        sessionId=session_id,
        sections=sections,
        previewUrl=preview_url
    )


@router.get("/files/{file_name}")
async def get_original_file(file_name: str):
    """
    Serve original uploaded file for preview.

    Args:
        file_name: File name with extension (e.g., "uuid.pdf")

    Returns:
        File response with original uploaded file
    """
    file_path = UPLOAD_DIR / file_name

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    # Determine media type
    if file_name.endswith(".pdf"):
        media_type = "application/pdf"
    elif file_name.endswith(".docx"):
        media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    else:
        raise HTTPException(status_code=400, detail="Invalid file type")

    return FileResponse(
        path=file_path,
        media_type=media_type,
        filename=file_name
    )
