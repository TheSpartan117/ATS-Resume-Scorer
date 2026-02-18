"""Protected resume CRUD endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone
import uuid

from backend.database import get_db
from backend.models.user import User
from backend.models.resume import Resume as ResumeModel
from backend.auth.dependencies import get_current_user


router = APIRouter(prefix="/api", tags=["resumes"])


class ResumeCreateRequest(BaseModel):
    """Request body for creating/updating resume"""
    fileName: str
    contact: Dict[str, Optional[str]]
    experience: List[Dict] = Field(default_factory=list)
    education: List[Dict] = Field(default_factory=list)
    skills: List[str] = Field(default_factory=list)
    certifications: List[Dict] = Field(default_factory=list)
    metadata: Dict
    latestScore: Optional[Dict] = None


class ResumeResponse(BaseModel):
    """Resume response"""
    id: str
    userId: str
    fileName: str
    contact: Dict[str, Optional[str]]
    experience: List[Dict]
    education: List[Dict]
    skills: List[str]
    certifications: List[Dict]
    metadata: Dict
    latestScore: Optional[Dict]
    createdAt: datetime
    updatedAt: Optional[datetime]

    class Config:
        from_attributes = True


@router.post("/resumes", response_model=ResumeResponse, status_code=status.HTTP_201_CREATED)
async def create_resume(
    request: ResumeCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Save a resume to the database.

    Requires authentication. Resume is associated with the current user.
    """

    resume_data = {
        "contact": request.contact,
        "experience": request.experience,
        "education": request.education,
        "skills": request.skills,
        "certifications": request.certifications,
        "metadata": request.metadata
    }

    new_resume = ResumeModel(
        user_id=current_user.id,
        file_name=request.fileName,
        resume_data=resume_data,
        latest_score=request.latestScore
    )

    db.add(new_resume)
    db.commit()
    db.refresh(new_resume)

    return ResumeResponse(
        id=str(new_resume.id),
        userId=str(new_resume.user_id),
        fileName=new_resume.file_name,
        contact=resume_data["contact"],
        experience=resume_data["experience"],
        education=resume_data["education"],
        skills=resume_data["skills"],
        certifications=resume_data["certifications"],
        metadata=resume_data["metadata"],
        latestScore=new_resume.latest_score,
        createdAt=new_resume.created_at,
        updatedAt=new_resume.updated_at
    )


@router.get("/resumes", response_model=List[ResumeResponse])
async def list_resumes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all resumes for the current user.

    Returns resumes ordered by most recently updated first.
    """

    resumes = db.query(ResumeModel)\
        .filter(ResumeModel.user_id == current_user.id)\
        .order_by(ResumeModel.updated_at.desc(), ResumeModel.created_at.desc())\
        .all()

    return [
        ResumeResponse(
            id=str(resume.id),
            userId=str(resume.user_id),
            fileName=resume.file_name,
            contact=resume.resume_data.get("contact", {}),
            experience=resume.resume_data.get("experience", []),
            education=resume.resume_data.get("education", []),
            skills=resume.resume_data.get("skills", []),
            certifications=resume.resume_data.get("certifications", []),
            metadata=resume.resume_data.get("metadata", {}),
            latestScore=resume.latest_score,
            createdAt=resume.created_at,
            updatedAt=resume.updated_at
        )
        for resume in resumes
    ]


@router.get("/resumes/{resume_id}", response_model=ResumeResponse)
async def get_resume(
    resume_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific resume by ID.

    Only returns resume if it belongs to the current user.
    """

    try:
        resume_uuid = uuid.UUID(resume_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid resume ID format"
        )

    resume = db.query(ResumeModel)\
        .filter(ResumeModel.id == resume_uuid)\
        .first()

    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )

    # Check ownership
    if resume.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    return ResumeResponse(
        id=str(resume.id),
        userId=str(resume.user_id),
        fileName=resume.file_name,
        contact=resume.resume_data.get("contact", {}),
        experience=resume.resume_data.get("experience", []),
        education=resume.resume_data.get("education", []),
        skills=resume.resume_data.get("skills", []),
        certifications=resume.resume_data.get("certifications", []),
        metadata=resume.resume_data.get("metadata", {}),
        latestScore=resume.latest_score,
        createdAt=resume.created_at,
        updatedAt=resume.updated_at
    )


@router.put("/resumes/{resume_id}", response_model=ResumeResponse)
async def update_resume(
    resume_id: str,
    request: ResumeCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a resume.

    Only allows updating resumes owned by the current user.
    """

    try:
        resume_uuid = uuid.UUID(resume_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid resume ID format"
        )

    resume = db.query(ResumeModel)\
        .filter(ResumeModel.id == resume_uuid)\
        .first()

    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )

    # Check ownership
    if resume.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    # Update resume data
    resume_data = {
        "contact": request.contact,
        "experience": request.experience,
        "education": request.education,
        "skills": request.skills,
        "certifications": request.certifications,
        "metadata": request.metadata
    }

    resume.file_name = request.fileName
    resume.resume_data = resume_data
    resume.latest_score = request.latestScore
    resume.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(resume)

    return ResumeResponse(
        id=str(resume.id),
        userId=str(resume.user_id),
        fileName=resume.file_name,
        contact=resume_data["contact"],
        experience=resume_data["experience"],
        education=resume_data["education"],
        skills=resume_data["skills"],
        certifications=resume_data["certifications"],
        metadata=resume_data["metadata"],
        latestScore=resume.latest_score,
        createdAt=resume.created_at,
        updatedAt=resume.updated_at
    )


@router.delete("/resumes/{resume_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_resume(
    resume_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a resume.

    Only allows deleting resumes owned by the current user.
    """

    try:
        resume_uuid = uuid.UUID(resume_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid resume ID format"
        )

    resume = db.query(ResumeModel)\
        .filter(ResumeModel.id == resume_uuid)\
        .first()

    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )

    # Check ownership
    if resume.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    db.delete(resume)
    db.commit()

    return None
