"""Resume-related schemas"""
from typing import Dict, List, Optional
from pydantic import BaseModel
from datetime import datetime


class SectionInfo(BaseModel):
    """Detected resume section"""
    title: str
    content: str
    section_id: str
    start_para_idx: int
    end_para_idx: int
    is_in_table: bool
    table_cell_ref: Optional[str] = None


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
    score: float
    maxScore: float
    issues: List[str]


class EnhancedSuggestion(BaseModel):
    """Enhanced suggestion with template and examples"""
    id: str
    type: str  # missing_content, keyword, formatting, writing
    severity: str  # high, medium, low
    title: str
    description: str
    template: Optional[str] = None
    quickFix: Optional[Dict] = None
    keywords: Optional[List[str]] = None


class ScoreResponse(BaseModel):
    """Complete scoring response"""
    overallScore: float
    breakdown: Dict[str, CategoryBreakdown]
    issues: Dict[str, List[str]]  # critical, warnings, suggestions, info
    strengths: List[str]
    mode: str  # "ats_simulation" or "quality_coach"
    keywordDetails: Optional[Dict] = None  # Keyword matching details for ATS mode
    autoReject: Optional[bool] = None  # Auto-reject flag for ATS mode
    issueCounts: Optional[Dict[str, int]] = None  # Count of critical, warnings, suggestions
    enhancedSuggestions: Optional[List[EnhancedSuggestion]] = None  # Detailed actionable suggestions


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
    fileId: Optional[str] = None  # ID to retrieve original file
    originalFileUrl: Optional[str] = None  # URL to access original file
    previewPdfUrl: Optional[str] = None  # URL to preview PDF (for DOCX files)
    editableHtml: Optional[str] = None  # Rich HTML for WYSIWYG editing
    contact: ContactInfoResponse
    experience: List[Dict] = []
    education: List[Dict] = []
    skills: List[str] = []
    certifications: List[Dict] = []
    metadata: MetadataResponse
    score: ScoreResponse
    formatCheck: FormatCheckResponse
    scoringMode: str  # "ats_simulation" or "quality_coach"
    role: str
    level: str
    jobDescription: Optional[str] = None
    uploadedAt: datetime
    industry: Optional[str] = None
    sessionId: Optional[str] = None  # Session ID for template editing
    sections: Optional[List[SectionInfo]] = None  # Detected sections
    previewUrl: Optional[str] = None  # Preview URL for Office viewer
