"""
Preview API endpoints for serving and updating DOCX templates.
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from backend.services.docx_template_manager import DocxTemplateManager
import logging
import uuid

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/preview", tags=["preview"])

# Initialize template manager
template_manager = DocxTemplateManager()

@router.get("/{session_id}.docx")
async def get_preview_docx(session_id: str):
    """
    Serve working DOCX for Office Online viewer.

    Args:
        session_id: Session identifier

    Returns:
        DOCX file response
    """
    # Validate session_id is a valid UUID to prevent path traversal attacks
    try:
        uuid.UUID(session_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session ID format")

    working_path = template_manager.get_working_path(session_id)

    if not working_path.exists():
        raise HTTPException(status_code=404, detail="Session not found")

    return FileResponse(
        path=working_path,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=f"{session_id}.docx",
        headers={
            "Access-Control-Allow-Origin": "*",
            "Cache-Control": "no-cache, no-store, must-revalidate"
        }
    )

class UpdateSectionRequest(BaseModel):
    session_id: str
    start_para_idx: int
    end_para_idx: int
    new_content: str

@router.post("/update")
async def update_section(request: UpdateSectionRequest):
    """
    Update specific section in working DOCX.

    Args:
        request: Update request with section details

    Returns:
        Success status and new preview URL
    """
    # Validate session_id is a valid UUID to prevent path traversal attacks
    try:
        uuid.UUID(request.session_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session ID format")

    result = template_manager.update_section(
        session_id=request.session_id,
        start_para_idx=request.start_para_idx,
        end_para_idx=request.end_para_idx,
        new_content=request.new_content
    )

    if not result['success']:
        raise HTTPException(status_code=400, detail=result.get('error', 'Update failed'))

    return result
