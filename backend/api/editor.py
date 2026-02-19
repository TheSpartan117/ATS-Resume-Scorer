from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import uuid

router = APIRouter(prefix="/api/editor", tags=["editor"])

class CreateSessionRequest(BaseModel):
    resume_id: str

class SessionResponse(BaseModel):
    session_id: str
    working_docx_url: str
    sections: List[Dict[str, Any]]
    current_score: Dict[str, Any]
    suggestions: List[Dict[str, Any]]

@router.post("/session", response_model=SessionResponse)
async def create_editor_session(request: CreateSessionRequest):
    """Create new editing session from uploaded resume"""
    session_id = str(uuid.uuid4())

    return SessionResponse(
        session_id=session_id,
        working_docx_url=f"/api/files/{session_id}_working.docx",
        sections=[],
        current_score={"overallScore": 0},
        suggestions=[]
    )
