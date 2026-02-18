"""
PDF and DOCX parser service for extracting structured data from resumes.
"""
import re
from io import BytesIO
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


def parse_experience_entry(text: str) -> Dict:
    """
    Parse an experience entry into structured fields.

    Args:
        text: Raw experience text

    Returns:
        Dict with title, company, location, dates, description
    """
    lines = [line.strip() for line in text.split('\n') if line.strip()]

    entry = {
        'title': '',
        'company': '',
        'location': '',
        'startDate': '',
        'endDate': '',
        'description': text  # Fallback to full text
    }

    if not lines:
        return entry

    # First line is usually the job title
    if lines:
        entry['title'] = lines[0]

    # Second line often has company - location format or company - location - dates
    if len(lines) > 1:
        second_line = lines[1]
        # Try to parse "Company - Location" or "Company, Location"
        if ' - ' in second_line:
            parts = second_line.split(' - ')
            entry['company'] = parts[0].strip()
            if len(parts) > 1:
                entry['location'] = parts[1].strip()
        elif ',' in second_line:
            parts = second_line.split(',')
            entry['company'] = parts[0].strip()
            if len(parts) > 1:
                entry['location'] = parts[1].strip()
        else:
            entry['company'] = second_line

    # Look for date patterns in third line
    if len(lines) > 2:
        third_line = lines[2]
        # Match patterns like "January 2020 - Present" or "2020-2022"
        date_pattern = r'(\w+\s+\d{4}|\d{4})\s*[-–]\s*(\w+\s+\d{4}|\d{4}|Present|Current)'
        date_match = re.search(date_pattern, third_line, re.IGNORECASE)
        if date_match:
            entry['startDate'] = date_match.group(1)
            entry['endDate'] = date_match.group(2)

    # Remaining lines are description/achievements
    if len(lines) > 3:
        entry['description'] = '\n'.join(lines[3:])
    elif len(lines) > 2:
        entry['description'] = '\n'.join(lines[2:])

    return entry


def parse_education_entry(text: str) -> Dict:
    """
    Parse an education entry into structured fields.

    Args:
        text: Raw education text

    Returns:
        Dict with degree, institution, location, graduationDate
    """
    lines = [line.strip() for line in text.split('\n') if line.strip()]

    entry = {
        'degree': '',
        'institution': '',
        'location': '',
        'graduationDate': '',
        'gpa': ''
    }

    if not lines:
        return entry

    # First line is usually the degree
    if lines:
        entry['degree'] = lines[0]

    # Second line often has institution - location
    if len(lines) > 1:
        second_line = lines[1]
        if ' - ' in second_line:
            parts = second_line.split(' - ')
            entry['institution'] = parts[0].strip()
            if len(parts) > 1:
                entry['location'] = parts[1].strip()
        elif ',' in second_line:
            parts = second_line.split(',')
            entry['institution'] = parts[0].strip()
            if len(parts) > 1:
                entry['location'] = parts[1].strip()
        else:
            entry['institution'] = second_line

    # Look for graduation date
    if len(lines) > 2:
        for line in lines[2:]:
            # Match "Graduated: 2015" or "2015" or "May 2015"
            grad_pattern = r'(?:Graduated:?\s*)?(\w+\s+\d{4}|\d{4})'
            grad_match = re.search(grad_pattern, line, re.IGNORECASE)
            if grad_match:
                entry['graduationDate'] = grad_match.group(1)

            # Look for GPA
            gpa_pattern = r'GPA:?\s*([\d.]+)'
            gpa_match = re.search(gpa_pattern, line, re.IGNORECASE)
            if gpa_match:
                entry['gpa'] = gpa_match.group(1)

    return entry


def extract_resume_sections(text: str) -> Dict[str, List]:
    """
    Extract structured sections from resume text.

    Args:
        text: Full resume text

    Returns:
        Dictionary with sections: experience, education, skills, certifications
        - experience: List[Dict] with structured fields (title, company, dates, etc.)
        - education: List[Dict] with structured fields (degree, institution, dates, etc.)
        - skills: List[str] (strings directly)
        - certifications: List[Dict] with name field
    """
    sections = {
        'experience': [],
        'education': [],
        'skills': [],
        'certifications': []
    }

    lines = text.split('\n')
    current_section = None
    current_content = []

    # Section headers to detect
    experience_headers = ['experience', 'work history', 'employment', 'professional experience', 'work experience']
    education_headers = ['education', 'academic background', 'qualifications', 'academic']
    skills_headers = ['skills', 'technical skills', 'core competencies', 'expertise', 'technologies']
    cert_headers = ['certifications', 'certificates', 'licenses', 'professional certifications']

    for line in lines:
        line_lower = line.lower().strip()

        # Detect section headers
        if any(header in line_lower for header in experience_headers):
            if current_section and current_content:
                content_text = '\n'.join(current_content)
                if current_section == 'experience':
                    sections[current_section].append(parse_experience_entry(content_text))
                elif current_section == 'education':
                    sections[current_section].append(parse_education_entry(content_text))
                elif current_section == 'certifications':
                    sections[current_section].append({'name': content_text})
            current_section = 'experience'
            current_content = []
        elif any(header in line_lower for header in education_headers):
            if current_section and current_content:
                content_text = '\n'.join(current_content)
                if current_section == 'experience':
                    sections[current_section].append(parse_experience_entry(content_text))
                elif current_section == 'education':
                    sections[current_section].append(parse_education_entry(content_text))
                elif current_section == 'certifications':
                    sections[current_section].append({'name': content_text})
            current_section = 'education'
            current_content = []
        elif any(header in line_lower for header in skills_headers):
            if current_section and current_content:
                content_text = '\n'.join(current_content)
                if current_section == 'experience':
                    sections[current_section].append(parse_experience_entry(content_text))
                elif current_section == 'education':
                    sections[current_section].append(parse_education_entry(content_text))
                elif current_section == 'certifications':
                    sections[current_section].append({'name': content_text})
            current_section = 'skills'
            current_content = []
        elif any(header in line_lower for header in cert_headers):
            if current_section and current_content:
                content_text = '\n'.join(current_content)
                if current_section == 'experience':
                    sections[current_section].append(parse_experience_entry(content_text))
                elif current_section == 'education':
                    sections[current_section].append(parse_education_entry(content_text))
                elif current_section == 'certifications':
                    sections[current_section].append({'name': content_text})
            current_section = 'certifications'
            current_content = []
        elif current_section and line.strip():
            current_content.append(line.strip())

    # Add last section
    if current_section and current_content:
        content_text = '\n'.join(current_content)
        if current_section == 'experience':
            sections[current_section].append(parse_experience_entry(content_text))
        elif current_section == 'education':
            sections[current_section].append(parse_education_entry(content_text))
        elif current_section == 'skills':
            # For skills, just add the raw text to be processed below
            sections[current_section].append(content_text)
        elif current_section == 'certifications':
            sections[current_section].append({'name': content_text})

    # Special handling for skills - split by commas/bullets (keep as strings)
    if sections['skills']:
        all_skills = []
        for skill_block in sections['skills']:
            # Split by common delimiters
            skills = re.split(r'[,;•|\n]+', skill_block)
            all_skills.extend([s.strip() for s in skills if s.strip()])
        sections['skills'] = list(set(all_skills))[:50]  # Deduplicate, limit to 50

    return sections


def parse_pdf(file_content: bytes, filename: str) -> ResumeData:
    """
    Parse a PDF resume and extract structured data.

    Args:
        file_content: PDF file content as bytes
        filename: Original filename of the PDF

    Returns:
        ResumeData object with extracted information
    """
    # Open PDF from bytes using PyMuPDF
    doc = fitz.open(stream=file_content, filetype="pdf")

    # Extract text from all pages
    full_text = ""
    for page in doc:
        full_text += page.get_text()

    # Get metadata
    page_count = len(doc)
    word_count = len(full_text.split())

    # Close document
    doc.close()

    # Extract sections (experience, education, skills)
    sections = extract_resume_sections(full_text)

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

    # Create ResumeData object with extracted sections
    resume_data = ResumeData(
        fileName=filename,
        contact=contact_info,
        experience=sections.get('experience', []),
        education=sections.get('education', []),
        skills=sections.get('skills', []),
        certifications=sections.get('certifications', []),
        metadata=metadata
    )

    return resume_data


def parse_docx(file_content: bytes, filename: str) -> ResumeData:
    """
    Parse a DOCX resume and extract structured data including tables.

    Args:
        file_content: DOCX file content as bytes
        filename: Original filename of the DOCX

    Returns:
        ResumeData object with extracted information
    """
    # Open DOCX from bytes using BytesIO
    doc = Document(BytesIO(file_content))

    # Extract text from paragraphs AND tables (CRITICAL FIX)
    full_text_parts = []

    # Get all paragraphs
    for para in doc.paragraphs:
        if para.text.strip():
            full_text_parts.append(para.text)

    # Get all tables (THIS WAS MISSING - CAUSED EMPTY SECTIONS)
    for table in doc.tables:
        for row in table.rows:
            row_text = []
            for cell in row.cells:
                cell_text = cell.text.strip()
                if cell_text:
                    row_text.append(cell_text)
            if row_text:
                full_text_parts.append(" | ".join(row_text))

    full_text = "\n".join(full_text_parts)

    # Extract sections (experience, education, skills)
    sections = extract_resume_sections(full_text)

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

    # Create ResumeData object with extracted sections
    resume_data = ResumeData(
        fileName=filename,
        contact=contact_info,
        experience=sections.get('experience', []),
        education=sections.get('education', []),
        skills=sections.get('skills', []),
        certifications=sections.get('certifications', []),
        metadata=metadata
    )

    return resume_data
