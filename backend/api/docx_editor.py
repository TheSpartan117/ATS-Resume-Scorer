"""
DOCX Binary Editor API Endpoints
Provides structure-preserving DOCX editing capabilities
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import logging
import os
from pathlib import Path

from backend.services.docx_structure_parser import parse_docx_structure
from backend.services.docx_structure_rebuilder import update_docx_text

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/docx-editor", tags=["docx-editor"])


class EditRequest(BaseModel):
    """Request model for text edits"""
    edits: List[Dict[str, Any]]


@router.get("/structure/{session_id}")
async def get_docx_structure(session_id: str):
    """
    Parse DOCX structure for editing

    Args:
        session_id: Session ID

    Returns:
        Document structure with editable text and formatting metadata
    """
    try:
        # Find the DOCX file for this session
        data_dir = Path("backend/data")
        docx_path = None

        # Look for session file
        for file in data_dir.glob(f"{session_id}*.docx"):
            docx_path = str(file)
            break

        if not docx_path or not os.path.exists(docx_path):
            raise HTTPException(status_code=404, detail="DOCX file not found for session")

        logger.info(f"Parsing DOCX structure for session {session_id}: {docx_path}")

        # Parse document structure
        structure = parse_docx_structure(docx_path)

        return {
            "session_id": session_id,
            "structure": structure,
            "original_file": os.path.basename(docx_path)
        }

    except Exception as e:
        logger.error(f"Failed to parse DOCX structure: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to parse document: {str(e)}")


@router.post("/update/{session_id}")
async def update_docx(session_id: str, request: EditRequest):
    """
    Update DOCX with edited text

    Args:
        session_id: Session ID
        request: Edit request with text changes

    Returns:
        Updated document path
    """
    try:
        # Find the original DOCX file
        data_dir = Path("backend/data")
        docx_path = None

        for file in data_dir.glob(f"{session_id}*.docx"):
            docx_path = str(file)
            break

        if not docx_path or not os.path.exists(docx_path):
            raise HTTPException(status_code=404, detail="DOCX file not found for session")

        logger.info(f"Updating DOCX for session {session_id}: {docx_path}")

        # Create output path
        original_name = Path(docx_path).stem
        output_path = str(data_dir / f"{original_name}_edited.docx")

        # Update document with edits
        update_docx_text(docx_path, request.edits, output_path)

        logger.info(f"Successfully updated DOCX: {output_path}")

        return {
            "session_id": session_id,
            "updated_file": os.path.basename(output_path),
            "file_path": output_path
        }

    except Exception as e:
        logger.error(f"Failed to update DOCX: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to update document: {str(e)}")


@router.get("/download/{session_id}")
async def download_edited_docx(session_id: str):
    """
    Download edited DOCX file

    Args:
        session_id: Session ID

    Returns:
        File download response
    """
    from fastapi.responses import FileResponse

    try:
        # Find the edited DOCX file
        data_dir = Path("backend/data")
        edited_path = None

        for file in data_dir.glob(f"{session_id}*_edited.docx"):
            edited_path = str(file)
            break

        if not edited_path or not os.path.exists(edited_path):
            # Fall back to original if no edited version
            for file in data_dir.glob(f"{session_id}*.docx"):
                if "_edited" not in file.name:
                    edited_path = str(file)
                    break

        if not edited_path or not os.path.exists(edited_path):
            raise HTTPException(status_code=404, detail="DOCX file not found")

        filename = Path(edited_path).name
        return FileResponse(
            edited_path,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            filename=filename
        )

    except Exception as e:
        logger.error(f"Failed to download DOCX: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to download document: {str(e)}")
