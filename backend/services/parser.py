"""
PDF and DOCX parser service for extracting structured data from resumes.
"""
import re
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
import fitz  # PyMuPDF
from docx import Document


# Pydantic models for structured resume data
class ContactInfo(BaseModel):
    """Contact information extracted from resume"""
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    linkedin: Optional[str] = None
    location: Optional[str] = None


class Experience(BaseModel):
    """Work experience entry"""
    title: str
    company: str
    location: Optional[str] = None
    startDate: Optional[str] = None
    endDate: Optional[str] = None
    description: Optional[str] = None
    achievements: List[str] = Field(default_factory=list)


class Education(BaseModel):
    """Education entry"""
    degree: str
    institution: str
    location: Optional[str] = None
    graduationDate: Optional[str] = None
    gpa: Optional[str] = None
    relevantCourses: List[str] = Field(default_factory=list)


class Certification(BaseModel):
    """Certification entry"""
    name: str
    issuer: Optional[str] = None
    date: Optional[str] = None
    expirationDate: Optional[str] = None


class ResumeMetadata(BaseModel):
    """Metadata about the parsed resume"""
    pageCount: int
    wordCount: int
    hasPhoto: bool = False
    fileFormat: str  # "pdf" or "docx"


class ResumeData(BaseModel):
    """Complete structured resume data"""
    fileName: str
    contact: Dict[str, Optional[str]]
    experience: List[Dict] = Field(default_factory=list)
    education: List[Dict] = Field(default_factory=list)
    skills: List[str] = Field(default_factory=list)
    certifications: List[Dict] = Field(default_factory=list)
    metadata: Dict


# Helper functions for text extraction
def extract_email(text: str) -> Optional[str]:
    """Extract email address from text using regex"""
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    match = re.search(email_pattern, text)
    return match.group(0) if match else None


def extract_phone(text: str) -> Optional[str]:
    """Extract phone number from text using regex"""
    # Matches formats: (123) 456-7890, 123-456-7890, 123.456.7890, +1 123 456 7890
    phone_patterns = [
        r'\+?1?\s*\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}',
        r'\+?\d{1,3}[\s.-]?\d{3}[\s.-]?\d{3}[\s.-]?\d{4}',
    ]
    for pattern in phone_patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(0)
    return None


def extract_linkedin(text: str) -> Optional[str]:
    """Extract LinkedIn URL from text"""
    linkedin_pattern = r'(?:https?://)?(?:www\.)?linkedin\.com/in/[\w-]+'
    match = re.search(linkedin_pattern, text, re.IGNORECASE)
    return match.group(0) if match else None


def extract_name_from_header(text: str) -> Optional[str]:
    """
    Extract name from resume header (first few lines).
    Assumes name is on the first line or early in the document.
    """
    lines = text.strip().split('\n')
    for line in lines[:5]:  # Check first 5 lines
        line = line.strip()
        # Name is usually a short line with 2-4 words, no special characters
        if line and len(line.split()) <= 4 and not re.search(r'[@\d()]', line):
            # Skip lines that are likely section headers
            if line.lower() not in ['resume', 'cv', 'curriculum vitae', 'contact', 'profile']:
                return line
    return None


def parse_pdf(file_path: str) -> ResumeData:
    """
    Parse a PDF resume and extract structured data.

    Args:
        file_path: Path to the PDF file

    Returns:
        ResumeData object with extracted information
    """
    # Open PDF
    doc = fitz.open(file_path)

    # Extract text from all pages
    full_text = ""
    for page in doc:
        full_text += page.get_text()

    # Get metadata
    page_count = len(doc)
    word_count = len(full_text.split())

    # Close document
    doc.close()

    # Extract contact information from the header (first 500 characters)
    header_text = full_text[:500]

    name = extract_name_from_header(full_text)
    email = extract_email(header_text)
    phone = extract_phone(header_text)
    linkedin = extract_linkedin(header_text)

    contact_info = {
        "name": name,
        "email": email,
        "phone": phone,
        "linkedin": linkedin
    }

    # Metadata
    metadata = {
        "pageCount": page_count,
        "wordCount": word_count,
        "hasPhoto": False,  # TODO: Implement image detection
        "fileFormat": "pdf"
    }

    # Create ResumeData object
    resume_data = ResumeData(
        fileName=file_path.split('/')[-1],
        contact=contact_info,
        experience=[],  # TODO: Implement section extraction
        education=[],   # TODO: Implement section extraction
        skills=[],      # TODO: Implement skills extraction
        certifications=[],
        metadata=metadata
    )

    return resume_data


def parse_docx(file_path: str) -> ResumeData:
    """
    Parse a DOCX resume and extract structured data.

    Args:
        file_path: Path to the DOCX file

    Returns:
        ResumeData object with extracted information
    """
    # Open DOCX
    doc = Document(file_path)

    # Extract text from all paragraphs
    full_text = "\n".join([para.text for para in doc.paragraphs])

    # Get metadata
    word_count = len(full_text.split())

    # Extract contact information from the header
    header_text = full_text[:500]

    name = extract_name_from_header(full_text)
    email = extract_email(header_text)
    phone = extract_phone(header_text)
    linkedin = extract_linkedin(header_text)

    contact_info = {
        "name": name,
        "email": email,
        "phone": phone,
        "linkedin": linkedin
    }

    # Metadata
    metadata = {
        "pageCount": len(doc.sections),  # Approximate page count
        "wordCount": word_count,
        "hasPhoto": False,  # TODO: Implement image detection
        "fileFormat": "docx"
    }

    # Create ResumeData object
    resume_data = ResumeData(
        fileName=file_path.split('/')[-1],
        contact=contact_info,
        experience=[],  # TODO: Implement section extraction
        education=[],   # TODO: Implement section extraction
        skills=[],      # TODO: Implement skills extraction
        certifications=[],
        metadata=metadata
    )

    return resume_data
