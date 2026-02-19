"""
File download API endpoints.
Handles serving working DOCX files for download.
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from backend.services.docx_template_manager import DocxTemplateManager
import logging
import uuid

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/downloads", tags=["downloads"])

@router.get("/{filename}")
async def download_file(filename: str):
    """
    Download working DOCX file.

    Args:
        filename: Filename in format {session_id}_working.docx

    Returns:
        FileResponse with the working DOCX file

    Raises:
        HTTPException: 400 if filename format is invalid, 404 if file not found
    """
    # Validate filename format
    if not filename.endswith("_working.docx"):
        raise HTTPException(status_code=400, detail="Invalid filename format. Expected: {session_id}_working.docx")

    # Extract session_id from filename
    session_id = filename.replace("_working.docx", "")

    # Validate session_id is a valid UUID to prevent path traversal attacks
    try:
        uuid.UUID(session_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session ID format. Must be a valid UUID.")

    # Get file path from DocxTemplateManager
    manager = DocxTemplateManager()

    try:
        file_path = manager.get_working_path(session_id)

        if not file_path.exists():
            logger.warning(f"File not found: {file_path}")
            raise HTTPException(status_code=404, detail="File not found")

        logger.info(f"Serving file: {file_path}")

        return FileResponse(
            path=str(file_path),
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            filename=filename
        )
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error serving file: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
