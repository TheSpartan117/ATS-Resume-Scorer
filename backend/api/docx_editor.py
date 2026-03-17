"""
DOCX Binary Editor API Endpoints
Provides structure-preserving DOCX editing capabilities
"""
import uuid
import os
import logging
from pathlib import Path
from typing import List, Dict, Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.auth.dependencies import get_current_user
from backend.models.user import User
from backend.database import get_db
from backend.services.docx_structure_parser import parse_docx_structure
from backend.services.docx_structure_rebuilder import update_docx_text

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/docx-editor", tags=["docx-editor"])

DATA_DIR = (Path(__file__).parent.parent / "data").resolve()


def _validate_session_id(session_id: str) -> str:
    """Validate that session_id is a UUID to prevent path injection."""
    try:
        uuid.UUID(session_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session ID")
    return session_id


def _safe_session_path(session_id: str) -> Path:
    """Build and containment-check a path from a validated UUID session_id."""
    _validate_session_id(session_id)
    candidate = (DATA_DIR / f"{session_id}.docx").resolve()
    if not str(candidate).startswith(str(DATA_DIR) + os.sep):
        raise HTTPException(status_code=403, detail="Access denied")
    return candidate


class EditRequest(BaseModel):
    """Request model for text edits"""
    edits: List[Dict[str, Any]]


@router.get("/structure/{session_id}")
async def get_docx_structure(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Parse DOCX structure for editing. Requires authentication."""
    docx_path = _safe_session_path(session_id)

    if not docx_path.exists():
        raise HTTPException(status_code=404, detail="DOCX file not found for session")

    logger.info(f"Parsing DOCX structure for session {session_id}")

    try:
        structure = parse_docx_structure(str(docx_path))
    except Exception as e:
        logger.error(f"Failed to parse DOCX structure: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to parse document")

    return {
        "session_id": session_id,
        "structure": structure,
        "original_file": docx_path.name,
    }


@router.post("/update/{session_id}")
async def update_docx(
    session_id: str,
    request: EditRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update DOCX with edited text. Requires authentication."""
    docx_path = _safe_session_path(session_id)

    if not docx_path.exists():
        raise HTTPException(status_code=404, detail="DOCX file not found for session")

    output_name = f"{session_id}_edited.docx"
    output_path = DATA_DIR / output_name

    logger.info(f"Updating DOCX for session {session_id}")

    try:
        update_docx_text(str(docx_path), request.edits, str(output_path))
    except Exception as e:
        logger.error(f"Failed to update DOCX: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to update document")

    logger.info(f"Successfully updated DOCX: {output_name}")

    return {
        "session_id": session_id,
        "updated_file": output_name,
    }


@router.get("/download/{session_id}")
async def download_edited_docx(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Download edited DOCX. Falls back to original if no edited version. Requires authentication."""
    _validate_session_id(session_id)

    edited_path = (DATA_DIR / f"{session_id}_edited.docx").resolve()
    original_path = (DATA_DIR / f"{session_id}.docx").resolve()

    for p in (edited_path, original_path):
        if not str(p).startswith(str(DATA_DIR) + os.sep):
            raise HTTPException(status_code=403, detail="Access denied")

    if edited_path.exists():
        serve_path = edited_path
    elif original_path.exists():
        serve_path = original_path
    else:
        raise HTTPException(status_code=404, detail="DOCX file not found")

    return FileResponse(
        str(serve_path),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=serve_path.name,
    )
