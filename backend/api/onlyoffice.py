"""
OnlyOffice Document Server Integration API

This module provides endpoints for integrating with OnlyOffice Document Server:
- Generate OnlyOffice config with JWT tokens
- Handle document save callbacks from OnlyOffice
- Serve documents for editing with proper security

Requirements:
- OnlyOffice Document Server running (docker-compose up)
- JWT_SECRET environment variable set
- Documents stored in backend/data/ directory
"""

import os
import time
import jwt
import json
import hashlib
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Request, Body
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/onlyoffice", tags=["onlyoffice"])

# Configuration
ONLYOFFICE_SERVER_URL = os.getenv("ONLYOFFICE_SERVER_URL", "http://localhost:8080")
JWT_SECRET = os.getenv("ONLYOFFICE_JWT_SECRET", "your-secret-key-change-in-production")
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
DATA_DIR = Path(__file__).parent.parent / "data"

# Ensure data directory exists
DATA_DIR.mkdir(exist_ok=True)


class OnlyOfficeConfig(BaseModel):
    """OnlyOffice editor configuration model"""
    documentType: str
    document: Dict[str, Any]
    editorConfig: Dict[str, Any]
    token: Optional[str] = None


class CallbackStatus(BaseModel):
    """OnlyOffice callback request model"""
    key: str
    status: int
    url: Optional[str] = None
    users: Optional[list] = None


def generate_jwt_token(payload: Dict[str, Any]) -> str:
    """
    Generate JWT token for OnlyOffice authentication

    Args:
        payload: Data to encode in token

    Returns:
        JWT token string
    """
    return jwt.encode(
        payload,
        JWT_SECRET,
        algorithm="HS256"
    )


def verify_jwt_token(token: str) -> Dict[str, Any]:
    """
    Verify and decode JWT token from OnlyOffice

    Args:
        token: JWT token to verify

    Returns:
        Decoded payload

    Raises:
        HTTPException: If token is invalid
    """
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    except jwt.InvalidTokenError as e:
        logger.error(f"Invalid JWT token: {e}")
        raise HTTPException(status_code=403, detail="Invalid token")


def get_document_key(file_path: str) -> str:
    """
    Generate unique document key based on file path and modification time

    This ensures the document cache is invalidated when the file changes.

    Args:
        file_path: Path to document file

    Returns:
        Unique document key
    """
    full_path = DATA_DIR / file_path
    if full_path.exists():
        mtime = full_path.stat().st_mtime
        key_string = f"{file_path}_{mtime}"
    else:
        key_string = f"{file_path}_{time.time()}"

    return hashlib.md5(key_string.encode()).hexdigest()


def get_document_type(filename: str) -> str:
    """
    Determine document type from filename extension

    Args:
        filename: Document filename

    Returns:
        Document type: 'word', 'cell', or 'slide'
    """
    ext = filename.lower().split('.')[-1]

    word_exts = ['doc', 'docx', 'docm', 'dot', 'dotx', 'dotm', 'odt', 'fodt', 'ott', 'rtf', 'txt', 'html', 'htm', 'mht', 'pdf', 'djvu', 'fb2', 'epub', 'xps']
    cell_exts = ['xls', 'xlsx', 'xlsm', 'xlt', 'xltx', 'xltm', 'ods', 'fods', 'ots', 'csv']
    slide_exts = ['pps', 'ppsx', 'ppsm', 'ppt', 'pptx', 'pptm', 'pot', 'potx', 'potm', 'odp', 'fodp', 'otp']

    if ext in word_exts:
        return 'word'
    elif ext in cell_exts:
        return 'cell'
    elif ext in slide_exts:
        return 'slide'
    else:
        return 'word'  # Default to word


@router.post("/config/{session_id}")
async def get_editor_config(session_id: str, request: Request):
    """
    Generate OnlyOffice editor configuration with JWT token

    This endpoint creates the configuration object needed to initialize
    the OnlyOffice Document Editor on the frontend.

    Args:
        session_id: Unique session identifier for the document
        request: FastAPI request object

    Returns:
        OnlyOffice configuration with JWT token
    """
    try:
        # For now, use session_id as filename (you can map this to actual files)
        filename = f"{session_id}.docx"
        file_path = DATA_DIR / filename

        # Check if file exists, if not create a blank DOCX
        if not file_path.exists():
            logger.warning(f"File not found: {filename}, creating blank document")
            # Create a minimal blank DOCX file
            from docx import Document
            doc = Document()
            doc.add_paragraph("")
            doc.save(str(file_path))

        # Generate document key
        doc_key = get_document_key(filename)

        # Get document type
        doc_type = get_document_type(filename)

        # Build document URL (accessible by OnlyOffice server)
        document_url = f"{BACKEND_URL}/api/onlyoffice/download/{session_id}"

        # Build callback URL (where OnlyOffice sends save notifications)
        callback_url = f"{BACKEND_URL}/api/onlyoffice/callback"

        # User info (you can integrate with your auth system)
        user = {
            "id": session_id,
            "name": "User"
        }

        # Build configuration
        config = {
            "documentType": doc_type,
            "document": {
                "fileType": filename.split('.')[-1],
                "key": doc_key,
                "title": filename,
                "url": document_url,
                "permissions": {
                    "comment": True,
                    "download": True,
                    "edit": True,
                    "fillForms": True,
                    "modifyFilter": True,
                    "modifyContentControl": True,
                    "review": True,
                    "print": True
                }
            },
            "editorConfig": {
                "callbackUrl": callback_url,
                "mode": "edit",
                "lang": "en",
                "user": user,
                "customization": {
                    "autosave": True,
                    "forcesave": True,
                    "comments": True,
                    "compactToolbar": False,
                    "feedback": False,
                    "goback": False,
                    "help": True,
                    "hideRightMenu": False,
                    "plugins": True,
                    "toolbarNoTabs": False,
                    "uiTheme": "default-light"
                }
            }
        }

        # Generate JWT token
        token = generate_jwt_token(config)
        config["token"] = token

        logger.info(f"Generated OnlyOffice config for session: {session_id}")

        return JSONResponse(content=config)

    except Exception as e:
        logger.error(f"Error generating OnlyOffice config: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/download/{session_id}")
async def download_document(session_id: str):
    """
    Serve document file for OnlyOffice to load

    This endpoint is called by OnlyOffice Document Server to download
    the document for editing.

    Args:
        session_id: Unique session identifier

    Returns:
        Document file
    """
    try:
        filename = f"{session_id}.docx"
        file_path = DATA_DIR / filename

        if not file_path.exists():
            logger.error(f"Document not found: {filename}")
            raise HTTPException(status_code=404, detail="Document not found")

        logger.info(f"Serving document: {filename}")

        return FileResponse(
            path=str(file_path),
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            filename=filename
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error serving document: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/callback")
async def handle_callback(request: Request, data: Dict[str, Any] = Body(...)):
    """
    Handle save callbacks from OnlyOffice Document Server

    OnlyOffice sends callbacks at various stages:
    - Status 1: Document is being edited
    - Status 2: Document is ready for saving
    - Status 3: Document saving error occurred
    - Status 4: Document is closed with no changes
    - Status 6: Document is being edited, but the current user has left
    - Status 7: Error has occurred while force saving the document

    Args:
        request: FastAPI request object
        data: Callback data from OnlyOffice

    Returns:
        Success response with error code 0
    """
    try:
        # Verify JWT token if present
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header[7:]
            try:
                verify_jwt_token(token)
            except HTTPException:
                logger.warning("Invalid JWT token in callback")

        status = data.get("status", 0)
        key = data.get("key", "")
        url = data.get("url")

        logger.info(f"Received callback: status={status}, key={key}")

        # Status 2 or 6: Document ready for saving
        if status in [2, 6]:
            if not url:
                logger.error("No URL provided in callback")
                return JSONResponse(content={"error": 1})

            # Download the saved document from OnlyOffice
            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=30.0)
                response.raise_for_status()

                # Find the file to save (extract session_id from key or use key as filename)
                # For simplicity, save as key.docx
                filename = f"{key}.docx"
                file_path = DATA_DIR / filename

                # Write the downloaded content
                with open(file_path, 'wb') as f:
                    f.write(response.content)

                logger.info(f"Document saved: {filename}")

        # Return success response
        return JSONResponse(content={"error": 0})

    except Exception as e:
        logger.error(f"Error handling callback: {e}", exc_info=True)
        return JSONResponse(content={"error": 1})


@router.get("/health")
async def health_check():
    """
    Check if OnlyOffice Document Server is accessible

    Returns:
        Health status
    """
    try:
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{ONLYOFFICE_SERVER_URL}/healthcheck", timeout=5.0)
            response.raise_for_status()

        return {
            "status": "healthy",
            "onlyoffice_server": ONLYOFFICE_SERVER_URL,
            "message": "OnlyOffice Document Server is accessible"
        }
    except Exception as e:
        logger.error(f"OnlyOffice health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "onlyoffice_server": ONLYOFFICE_SERVER_URL,
                "error": str(e),
                "message": "OnlyOffice Document Server is not accessible"
            }
        )


@router.post("/upload/{session_id}")
async def upload_document(session_id: str, request: Request):
    """
    Upload a document for editing

    Args:
        session_id: Unique session identifier
        request: FastAPI request with file data

    Returns:
        Success message
    """
    try:
        from fastapi import UploadFile, File

        # Read the file from request
        file_data = await request.body()

        filename = f"{session_id}.docx"
        file_path = DATA_DIR / filename

        # Save the file
        with open(file_path, 'wb') as f:
            f.write(file_data)

        logger.info(f"Document uploaded: {filename}")

        return JSONResponse(content={
            "success": True,
            "message": "Document uploaded successfully",
            "session_id": session_id
        })

    except Exception as e:
        logger.error(f"Error uploading document: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
