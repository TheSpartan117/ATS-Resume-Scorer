"""Resume-related schemas"""
from typing import Dict, List, Optional
from pydantic import BaseModel
from datetime import datetime


class ContactInfoResponse(BaseModel):
    """Contact information in response"""
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin: Optional[str] = None
    website: Optional[str] = None


class MetadataResponse(BaseModel):
    """Resume metadata in response"""
    pageCount: int
    wordCount: int
    hasPhoto: bool
    fileFormat: str


class CategoryBreakdown(BaseModel):
    """Score breakdown for a single category"""
    score: int
    maxScore: int
    issues: List[str]


class ScoreResponse(BaseModel):
    """Complete scoring response"""
    overallScore: int
    breakdown: Dict[str, CategoryBreakdown]
    issues: Dict[str, List[str]]  # critical, warnings, suggestions, info
    strengths: List[str]


class FormatCheckResponse(BaseModel):
    """Format compatibility check result"""
    passed: bool
    score: float  # 0.0-1.0
    checks: Dict[str, Dict]  # Each check has passed, score, and additional fields
    issues: List[str]


class UploadResponse(BaseModel):
    """Response for upload endpoint"""
    resumeId: Optional[str] = None  # Only if user is authenticated
    fileName: str
    contact: ContactInfoResponse
    experience: List[Dict] = []
    education: List[Dict] = []
    skills: List[str] = []
    certifications: List[Dict] = []
    metadata: MetadataResponse
    score: ScoreResponse
    formatCheck: FormatCheckResponse
    uploadedAt: datetime
    jobDescription: Optional[str] = None
    industry: Optional[str] = None
