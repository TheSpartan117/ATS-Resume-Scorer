# CV Parser Implementation Examples

**Purpose:** Ready-to-use code examples for parser improvements
**Usage:** Copy-paste into your codebase and adapt as needed

---

## Table of Contents

1. [Quick Fix #1: Clean Spacing Artifacts](#1-clean-spacing-artifacts)
2. [Quick Fix #2: Expand Section Headers](#2-expand-section-headers)
3. [Quick Fix #3: Deduplicate Education](#3-deduplicate-education)
4. [Quick Fix #4: Filter Skills](#4-filter-skills)
5. [Quick Fix #5: Generate Suggestions](#5-generate-suggestions)
6. [Hybrid Implementation: LLM Fallback](#6-hybrid-llm-fallback)
7. [Confidence Scoring](#7-confidence-scoring)
8. [Testing Utilities](#8-testing-utilities)

---

## 1. Clean Spacing Artifacts

### Problem
PDFs extract as `"I N D I A N  I N S T I T U T E"` instead of `"INDIAN INSTITUTE"`

### Solution

**File:** `/Users/sabuj.mondal/ats-resume-scorer/backend/services/parser.py`

**Add this function at line 144:**

```python
def clean_spacing_artifacts(text: str) -> str:
    """
    Fix spacing artifacts from PDF extraction.

    Examples:
        'I N D I A N' → 'INDIAN'
        'T E C H N O L O G Y' → 'TECHNOLOGY'
        'A I R  I N D I A' → 'AIR INDIA'

    Args:
        text: Text with potential spacing artifacts

    Returns:
        Cleaned text with artifacts removed
    """
    if not text:
        return text

    # Pattern 1: Single uppercase letters with spaces
    # Regex: Letter + Space + Letter + Space (repeated 3+ times)
    # Example: 'I N D I A N' has pattern ([A-Z]\s){6}
    if re.match(r'^([A-Z]\s){3,}', text):
        # Remove spaces between single uppercase letters
        cleaned = re.sub(r'([A-Z])\s+(?=[A-Z](?:\s|$))', r'\1', text)
        # Clean up any remaining multiple spaces
        cleaned = re.sub(r'\s{2,}', ' ', cleaned)
        return cleaned.strip()

    # Pattern 2: Multiple spaces between words
    # Example: 'AIR  INDIA' → 'AIR INDIA'
    cleaned = re.sub(r'\s{2,}', ' ', text)

    return cleaned.strip()
```

**Apply to extraction functions:**

```python
# Update extract_name_from_header (line 146-159)
def extract_name_from_header(text: str) -> Optional[str]:
    """Extract name from resume header (first few lines)."""
    lines = text.strip().split('\n')
    for line in lines[:5]:
        line = line.strip()
        if line and len(line.split()) <= 4 and not re.search(r'[@\d()]', line):
            if line.lower() not in ['resume', 'cv', 'curriculum vitae', 'contact', 'profile']:
                return clean_spacing_artifacts(line)  # ADD THIS LINE
    return None

# Update parse_experience_entry (line 213-217)
def parse_experience_entry(text: str) -> Dict:
    # ... existing code ...

    # Line 213: Clean company name
    if ',' in first_line:
        parts = first_line.split(',', 1)
        entry['company'] = clean_spacing_artifacts(parts[0].strip())  # ADD clean_spacing_artifacts
        entry['location'] = parts[1].strip() if len(parts) > 1 else ''
    else:
        entry['company'] = clean_spacing_artifacts(first_line)  # ADD clean_spacing_artifacts

    # ... rest of function ...

# Update parse_education_entry (line 296-312)
def parse_education_entry(text: str) -> Dict:
    # ... existing code ...

    # Line 296: Clean degree name
    if lines:
        entry['degree'] = clean_spacing_artifacts(lines[0])  # ADD clean_spacing_artifacts

    # Line 300-312: Clean institution name
    if len(lines) > 1:
        second_line = lines[1]
        if ' - ' in second_line:
            parts = second_line.split(' - ')
            entry['institution'] = clean_spacing_artifacts(parts[0].strip())  # ADD
            if len(parts) > 1:
                entry['location'] = parts[1].strip()
        elif ',' in second_line:
            parts = second_line.split(',')
            entry['institution'] = clean_spacing_artifacts(parts[0].strip())  # ADD
            if len(parts) > 1:
                entry['location'] = parts[1].strip()
        else:
            entry['institution'] = clean_spacing_artifacts(second_line)  # ADD

    # ... rest of function ...
```

**Test it:**

```python
# Test cases
assert clean_spacing_artifacts('I N D I A N') == 'INDIAN'
assert clean_spacing_artifacts('T E C H N O L O G Y') == 'TECHNOLOGY'
assert clean_spacing_artifacts('M A S T E R  O F  B U S I N E S S') == 'MASTER OF BUSINESS'
assert clean_spacing_artifacts('A I R  I N D I A') == 'AIR INDIA'
assert clean_spacing_artifacts('Normal Text') == 'Normal Text'
print("✅ All spacing artifact tests passed!")
```

---

## 2. Expand Section Headers

### Problem
Only detects 4-6 header variations per section, misses "EXPERIENCE SUMMARY", "CAREER HISTORY"

### Solution

**File:** `/Users/sabuj.mondal/ats-resume-scorer/backend/services/parser.py`

**Replace lines 414-418 with:**

```python
# Section headers to detect (lines 414-418)
experience_headers = [
    # Standard
    'experience', 'work history', 'employment', 'professional experience', 'work experience',
    # Summary variations
    'experience summary', 'professional summary', 'career summary', 'work summary',
    # Background variations
    'professional background', 'career background', 'employment history', 'work background',
    # Journey/achievements
    'professional journey', 'career history', 'career achievements', 'work achievements',
    # Profile variations
    'professional profile', 'career profile', 'profile brief', 'profile summary',
    # Other
    'positions held', 'previous roles', 'relevant experience', 'employment record'
]

education_headers = [
    # Standard
    'education', 'academic background', 'qualifications', 'academic',
    'educational background', 'educational qualifications',
    # Variations
    'academic qualifications', 'academic history', 'degrees', 'academic achievements',
    # Training
    'education and training', 'education & training', 'training', 'schooling',
    # Certifications combo
    'education & certifications', 'qualifications & certifications',
    # International
    'educational credentials', 'academic credentials', 'academic record'
]

skills_headers = [
    # Standard
    'skills', 'technical skills', 'core competencies', 'expertise', 'technologies',
    # Key skills
    'key skills', 'skill set', 'skillset', 'areas of expertise', 'core skills',
    # Proficiencies
    'technical proficiencies', 'proficiencies', 'technical competencies',
    'competencies', 'professional skills',
    # Tools
    'tools & technologies', 'tools and technologies', 'technical expertise',
    'tools', 'technical tools',
    # Other
    'areas of specialization', 'technical knowledge', 'domain expertise',
    'technical background', 'technology stack'
]

cert_headers = [
    # Standard
    'certifications', 'certificates', 'licenses', 'professional certifications',
    # Licenses
    'licenses and certifications', 'licenses & certifications',
    'professional licenses', 'credentials',
    # Training
    'training and certifications', 'training & certifications',
    'professional training', 'professional development',
    # Achievements
    'certifications and awards', 'certifications & awards',
    'professional achievements', 'accreditations', 'professional credentials'
]
```

**Add case-insensitive and cleaned matching:**

```python
# Update section detection logic (line 423-427)
for line in lines:
    line_lower = line.lower().strip()

    # Remove common prefixes/decorations
    line_clean = re.sub(r'^[•\-\*\d\.]+\s*', '', line_lower)  # Remove bullets, numbers
    line_clean = re.sub(r'[^a-z\s&]', ' ', line_clean)  # Remove special chars except &
    line_clean = re.sub(r'\s+', ' ', line_clean).strip()  # Normalize spaces

    # Detect section headers with exact match
    if any(header == line_clean for header in experience_headers):
        logger.info(f"Found experience section: '{line}'")
        if current_section and current_content:
            # Save previous section
            # ... (existing logic)
        current_section = 'experience'
        current_content = []
    elif any(header == line_clean for header in education_headers):
        logger.info(f"Found education section: '{line}'")
        # ... (similar logic)
    # ... (rest of detection)
```

---

## 3. Deduplicate Education

### Problem
Same education entry appears multiple times

### Solution

**File:** `/Users/sabuj.mondal/ats-resume-scorer/backend/services/parser.py`

**Replace `split_education_entries` function (lines 332-386):**

```python
def split_education_entries(text: str) -> List[str]:
    """
    Split multiple education entries from a single text block.

    Detects new entries by:
    - Degree keywords (Bachelor, Master, PhD, etc.)
    - Blank lines separating entries
    - Deduplicates similar entries

    Args:
        text: Raw education section text

    Returns:
        List of individual education entry texts (deduplicated)
    """
    # Degree keywords that indicate a new education entry
    degree_keywords = [
        r'\b(Bachelor|B\.?\s*[ASC]\.?|BA|BS|BBA|BEng|BTech|B\.Tech)\b',
        r'\b(Master|M\.?\s*[ASC]\.?|MA|MS|MBA|MEng|MTech|M\.Tech|MSc|M\.Sc)\b',
        r'\b(Doctor|PhD|Ph\.?D\.?|Doctorate|D\.Phil|DPhil)\b',
        r'\b(Associate|A\.?\s*[AS]\.?|AA|AS)\b',
        r'\b(Diploma|Certificate|Certification)\b',
        r'\b(High School|Higher Secondary|Secondary|XII|X|12th|10th)\b'
    ]

    lines = text.split('\n')
    entries = []
    current_entry = []

    for line in lines:
        line_stripped = line.strip()

        # Skip empty lines
        if not line_stripped:
            continue

        # Check if this line starts a new education entry
        is_new_entry = False
        for pattern in degree_keywords:
            if re.search(pattern, line_stripped, re.IGNORECASE):
                is_new_entry = True
                break

        if is_new_entry and current_entry:
            # Save current entry and start new one
            entries.append('\n'.join(current_entry))
            current_entry = [line_stripped]
        else:
            # Add to current entry
            current_entry.append(line_stripped)

    # Add last entry
    if current_entry:
        entries.append('\n'.join(current_entry))

    # CRITICAL FIX: Deduplicate entries
    seen_fingerprints = set()
    unique_entries = []

    for entry in entries:
        # Create fingerprint from first line (degree name) and second line (institution)
        entry_lines = entry.split('\n')
        if not entry_lines:
            continue

        # Fingerprint: first 60 chars of first two lines combined, lowercased
        fingerprint_text = ' '.join(entry_lines[:2])[:60].lower().strip()

        # Check if this is a duplicate
        is_duplicate = False

        if fingerprint_text in seen_fingerprints:
            is_duplicate = True
        else:
            # Also check if first line is a substring of any previous entry
            # (catches cases like "Master of Business" vs "Master of Business Administration")
            first_line = entry_lines[0].lower().strip()
            for prev_entry in unique_entries:
                prev_first_line = prev_entry.split('\n')[0].lower().strip()
                # Check if one is substring of the other (80% overlap)
                overlap = fuzz.ratio(first_line, prev_first_line)
                if overlap >= 80:
                    is_duplicate = True
                    break

        if not is_duplicate:
            seen_fingerprints.add(fingerprint_text)
            unique_entries.append(entry)
            logger.info(f"Added unique education entry: {entry_lines[0][:50]}")
        else:
            logger.info(f"Skipped duplicate education entry: {entry_lines[0][:50]}")

    return unique_entries
```

**Add fuzzy matching import at top of file:**

```python
# At top of parser.py (line 4-10)
import re
import io
import logging
from io import BytesIO
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from fuzzywuzzy import fuzz  # ADD THIS LINE
import fitz  # PyMuPDF
import pypdf
import pdfplumber
from docx import Document
```

---

## 4. Filter Skills

### Problem
Skills list contains sentence fragments like "management. Deep understanding of digital transformation"

### Solution

**File:** `/Users/sabuj.mondal/ats-resume-scorer/backend/services/parser.py`

**Replace skills extraction logic (lines 502-513):**

```python
# Special handling for skills - split by commas/bullets (keep as strings)
logger.info(f"Skills section raw data: {sections['skills']}")
if sections['skills']:
    all_skills = []
    for skill_block in sections['skills']:
        # Split by common delimiters
        raw_skills = re.split(r'[,;•|\n]+', skill_block)

        for skill in raw_skills:
            skill = skill.strip()

            # ==== VALIDATION FILTERS ====

            # 1. Length check (skills are typically 2-50 chars)
            if len(skill) < 2 or len(skill) > 50:
                continue

            # 2. Filter out sentence starters (common phrases that aren't skills)
            sentence_starters = [
                'experience', 'knowledge', 'deep understanding', 'developing',
                'advanced', 'managing', 'building', 'proficiency', 'expertise',
                'strong', 'excellent', 'proven', 'demonstrated'
            ]
            if any(skill.lower().startswith(starter) for starter in sentence_starters):
                logger.debug(f"Filtered sentence starter: {skill}")
                continue

            # 3. Filter out sentences (contains multiple common words)
            common_words = ['the', 'and', 'for', 'with', 'in', 'of', 'to', 'a',
                           'an', 'is', 'are', 'was', 'were', 'has', 'have', 'had']
            word_count = sum(1 for word in skill.lower().split() if word in common_words)
            if word_count >= 2:  # Likely a sentence, not a skill
                logger.debug(f"Filtered sentence: {skill}")
                continue

            # 4. Filter out phrases ending with periods/incomplete sentences
            if skill.endswith('.') or skill.endswith(','):
                logger.debug(f"Filtered incomplete phrase: {skill}")
                continue

            # 5. Check if skill looks valid (only letters, numbers, +, #, ., -, /, spaces)
            # Allow: "Python", "C++", "Node.js", "React.js", "ASP.NET", "CI/CD"
            if not re.match(r'^[A-Za-z0-9\s\+\#\.\-/]+$', skill):
                logger.debug(f"Filtered invalid characters: {skill}")
                continue

            # 6. Filter out very generic terms
            generic_terms = ['management', 'experience', 'knowledge', 'skills',
                           'abilities', 'other', 'various', 'multiple']
            if skill.lower() in generic_terms:
                logger.debug(f"Filtered generic term: {skill}")
                continue

            # Passed all filters - add to list
            all_skills.append(skill)

    # ==== DEDUPLICATION ====
    # Case-insensitive deduplication while preserving original case
    seen_lower = set()
    unique_skills = []
    for skill in all_skills:
        skill_lower = skill.lower()
        if skill_lower not in seen_lower:
            seen_lower.add(skill_lower)
            unique_skills.append(skill)

    # Limit to 50 skills (most relevant)
    sections['skills'] = unique_skills[:50]
    logger.info(f"Processed {len(sections['skills'])} skills: {sections['skills'][:10]}")
else:
    logger.warning("No skills section found in resume")
```

---

## 5. Generate Suggestions

### Problem
"Missing Content" tab is empty even when issues exist

### Solution

**File:** `/Users/sabuj.mondal/ats-resume-scorer/backend/services/scorer_ats.py`

**Replace `_score_contact_info` method (around line 400+):**

```python
def _score_contact_info(self, resume: ResumeData) -> Dict:
    """
    Score contact information completeness (5 points max).

    Scoring:
    - Email: 2 pts
    - Phone: 2 pts
    - LinkedIn: 1 pt

    Also generates detailed suggestions for missing items.

    Args:
        resume: Parsed resume data

    Returns:
        Dict with score, details, and suggestions
    """
    score = 0
    missing = []
    suggestions = []

    # Check email
    email = resume.contact.get('email')
    if email and '@' in email and '.' in email.split('@')[-1]:
        score += 2
        logger.info(f"Email detected: {email}")
    else:
        missing.append('email')
        suggestions.append({
            'severity': 'critical',
            'category': 'contact',
            'message': 'Missing professional email address',
            'action': 'Add your email address (e.g., yourname@email.com) at the top of your resume',
            'template': 'yourname@example.com'
        })

    # Check phone
    phone = resume.contact.get('phone')
    if phone and len(re.sub(r'[^\d]', '', phone)) >= 10:
        score += 2
        logger.info(f"Phone detected: {phone}")
    else:
        missing.append('phone')
        suggestions.append({
            'severity': 'critical',
            'category': 'contact',
            'message': 'Missing phone number',
            'action': 'Add your phone number (e.g., (555) 123-4567) for recruiters to contact you',
            'template': '(555) 123-4567'
        })

    # Check LinkedIn
    linkedin = resume.contact.get('linkedin')
    if linkedin and ('linkedin.com' in linkedin.lower() or len(linkedin) > 5):
        score += 1
        logger.info(f"LinkedIn detected: {linkedin}")
    else:
        missing.append('linkedin')
        suggestions.append({
            'severity': 'warning',
            'category': 'contact',
            'message': 'Missing LinkedIn profile',
            'action': 'Add your LinkedIn profile URL to increase credibility and networking opportunities',
            'template': 'linkedin.com/in/yourprofile'
        })

    # Check name (ensure it's not a section header by mistake)
    name = resume.contact.get('name')
    suspicious_names = ['EXPERIENCE', 'EDUCATION', 'SKILLS', 'CERTIFICATIONS',
                       'PROFILE', 'SUMMARY', 'OBJECTIVE']
    if not name or name.upper() in suspicious_names:
        suggestions.append({
            'severity': 'critical',
            'category': 'contact',
            'message': 'Name not detected correctly',
            'action': 'Ensure your full name is clearly visible at the very top of the resume, ' +
                     'separate from section headers',
            'help': 'Place your name on the first line in a larger font (14-18pt)'
        })

    # Additional contact suggestions
    location = resume.contact.get('location')
    if not location:
        suggestions.append({
            'severity': 'info',
            'category': 'contact',
            'message': 'Consider adding your location',
            'action': 'Add your city and state/country to help with location-based job searches',
            'template': 'City, State/Country'
        })

    return {
        'score': score,
        'maxScore': 5,
        'details': {
            'present': [k for k in ['email', 'phone', 'linkedin'] if k not in missing],
            'missing': missing,
            'suggestions': suggestions,
            'message': f"Contact info: {score}/5 points"
        }
    }
```

**Update API response to include suggestions:**

**File:** Backend API handler (main.py or resumes.py)

```python
# When building the response after scoring
def format_score_response(score_result: Dict) -> Dict:
    """Format scorer result for API response"""
    issues = {
        'critical': [],
        'warnings': [],
        'suggestions': [],
        'info': []
    }

    # Add contact info suggestions to issues
    contact_details = score_result['breakdown']['contact']['details']
    for suggestion in contact_details.get('suggestions', []):
        severity = suggestion['severity']
        message = suggestion['action']

        if severity == 'critical':
            issues['critical'].append(message)
        elif severity == 'warning':
            issues['warnings'].append(message)
        elif severity == 'info':
            issues['info'].append(message)
        else:
            issues['suggestions'].append(message)

    # Add other issues from validator
    # ... (existing logic)

    return {
        'score': score_result['score'],
        'breakdown': score_result['breakdown'],
        'issues': issues
    }
```

---

## 6. Hybrid LLM Fallback

### Implementation

**File:** `/Users/sabuj.mondal/ats-resume-scorer/backend/services/parser_hybrid.py` (NEW FILE)

```python
"""
Hybrid parser with LLM fallback for low-confidence cases.
"""
import os
import logging
import json
from typing import Dict
from anthropic import Anthropic

from backend.services.parser import (
    parse_pdf as parse_pdf_rules,
    parse_docx as parse_docx_rules,
    ResumeData,
    clean_spacing_artifacts
)

logger = logging.getLogger(__name__)

# Initialize Anthropic client
anthropic_client = None

def get_anthropic_client():
    """Lazy load Anthropic client"""
    global anthropic_client
    if anthropic_client is None:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
        anthropic_client = Anthropic(api_key=api_key)
    return anthropic_client


def calculate_parse_confidence(resume: ResumeData, raw_text: str) -> float:
    """
    Calculate confidence score for parsed resume (0-100).

    Confidence indicators:
    - Section completeness (40 pts)
    - Data quality checks (30 pts)
    - Entity validation (30 pts)

    Args:
        resume: Parsed resume data
        raw_text: Original extracted text

    Returns:
        Confidence score (0-100)
    """
    score = 0

    # 1. Section completeness (40 points)
    if resume.experience and len(resume.experience) > 0:
        score += 15
    if resume.education and len(resume.education) > 0:
        score += 15
    if resume.skills and len(resume.skills) >= 5:
        score += 10

    # 2. Data quality checks (30 points)
    # Valid email
    email = resume.contact.get('email', '')
    if email and '@' in email and '.' in email.split('@')[-1]:
        score += 10

    # Valid name (not a section header)
    name = resume.contact.get('name', '')
    suspicious_names = ['EXPERIENCE', 'EDUCATION', 'SKILLS', 'CERTIFICATIONS']
    if name and len(name) < 50 and name.upper() not in suspicious_names:
        score += 10

    # No spacing artifacts in name
    if name and not has_spacing_artifacts(name):
        score += 10

    # 3. Entity validation (30 points)
    # Experience entries have both title and company
    valid_exp_count = sum(1 for exp in resume.experience
                          if exp.get('title') and exp.get('company'))
    if valid_exp_count > 0:
        score += min(15, valid_exp_count * 5)

    # Education entries have both degree and institution
    valid_edu_count = sum(1 for edu in resume.education
                          if edu.get('degree') and edu.get('institution'))
    if valid_edu_count > 0:
        score += min(15, valid_edu_count * 5)

    return min(score, 100)


def has_spacing_artifacts(text: str) -> bool:
    """Check if text has spacing artifacts (e.g., 'I N D I A N')"""
    if not text:
        return False
    return bool(re.match(r'([A-Z]\s){3,}', text))


def parse_with_llm(resume_text: str, filename: str) -> ResumeData:
    """
    Parse resume using Claude Haiku API.

    Args:
        resume_text: Full resume text
        filename: Original filename

    Returns:
        ResumeData object
    """
    logger.info(f"Using LLM fallback for {filename}")

    client = get_anthropic_client()

    prompt = f"""Parse this resume and extract structured data in JSON format.

Resume text:
{resume_text[:10000]}  # Limit to 10K chars to save tokens

Return ONLY a JSON object (no markdown, no extra text) with this exact structure:
{{
  "contact": {{
    "name": "Full Name",
    "email": "email@example.com",
    "phone": "(555) 123-4567",
    "linkedin": "linkedin.com/in/profile",
    "location": "City, State"
  }},
  "experience": [
    {{
      "title": "Job Title",
      "company": "Company Name",
      "location": "City, State",
      "startDate": "Month Year",
      "endDate": "Month Year or Present",
      "description": "Job description and achievements"
    }}
  ],
  "education": [
    {{
      "degree": "Degree Name",
      "institution": "University Name",
      "location": "City, State",
      "graduationDate": "Year",
      "gpa": "GPA if available"
    }}
  ],
  "skills": ["Skill1", "Skill2", "Skill3"],
  "certifications": [
    {{
      "name": "Certification Name",
      "issuer": "Issuing Organization",
      "date": "Year"
    }}
  ]
}}

Important instructions:
1. Fix spacing artifacts (e.g., "I N D I A N" → "INDIAN")
2. Extract company and institution names carefully
3. Deduplicate entries (no duplicates)
4. For skills, only include actual skills (not sentences)
5. Use proper capitalization
6. If information is missing, use empty string or empty array
"""

    try:
        response = client.messages.create(
            model="claude-haiku-20240307",
            max_tokens=2048,
            temperature=0,  # Deterministic parsing
            messages=[{"role": "user", "content": prompt}]
        )

        # Parse JSON response
        json_text = response.content[0].text
        # Clean up potential markdown code blocks
        json_text = json_text.replace('```json', '').replace('```', '').strip()

        parsed_data = json.loads(json_text)

        # Convert to ResumeData
        return ResumeData(
            fileName=filename,
            contact=parsed_data.get('contact', {}),
            experience=parsed_data.get('experience', []),
            education=parsed_data.get('education', []),
            skills=parsed_data.get('skills', []),
            certifications=parsed_data.get('certifications', []),
            metadata={
                'pageCount': 1,  # Not available from LLM
                'wordCount': len(resume_text.split()),
                'hasPhoto': False,
                'fileFormat': 'parsed_by_llm',
                'llm_model': 'claude-haiku-20240307'
            }
        )

    except Exception as e:
        logger.error(f"LLM parsing failed: {e}")
        # Return minimal result
        return ResumeData(
            fileName=filename,
            contact={},
            experience=[],
            education=[],
            skills=[],
            certifications=[],
            metadata={'pageCount': 0, 'wordCount': 0, 'hasPhoto': False, 'fileFormat': 'pdf'}
        )


def parse_pdf_hybrid(file_content: bytes, filename: str, confidence_threshold: float = 70.0) -> ResumeData:
    """
    Parse PDF with hybrid approach: rules first, LLM fallback if low confidence.

    Args:
        file_content: PDF file bytes
        filename: Original filename
        confidence_threshold: Confidence below this triggers LLM fallback

    Returns:
        ResumeData object with highest confidence
    """
    # Step 1: Try rule-based parser
    result_rules = parse_pdf_rules(file_content, filename)

    # Step 2: Calculate confidence
    # Extract raw text for confidence check
    import fitz
    doc = fitz.open(stream=file_content, filetype="pdf")
    raw_text = ""
    for page in doc:
        raw_text += page.get_text()
    doc.close()

    confidence_rules = calculate_parse_confidence(result_rules, raw_text)
    logger.info(f"Rule-based parsing confidence: {confidence_rules}%")

    # Step 3: If low confidence, try LLM
    if confidence_rules < confidence_threshold:
        logger.info(f"Confidence {confidence_rules}% below threshold {confidence_threshold}%, using LLM fallback")
        result_llm = parse_with_llm(raw_text, filename)
        confidence_llm = calculate_parse_confidence(result_llm, raw_text)
        logger.info(f"LLM parsing confidence: {confidence_llm}%")

        # Return whichever has higher confidence
        if confidence_llm > confidence_rules:
            logger.info("Using LLM result (higher confidence)")
            result_llm.metadata['parse_method'] = 'llm_fallback'
            result_llm.metadata['parse_confidence'] = confidence_llm
            return result_llm
        else:
            logger.info("Using rule-based result (LLM didn't improve)")
            result_rules.metadata['parse_method'] = 'rules_only'
            result_rules.metadata['parse_confidence'] = confidence_rules
            return result_rules
    else:
        logger.info(f"Confidence {confidence_rules}% sufficient, using rule-based result")
        result_rules.metadata['parse_method'] = 'rules_only'
        result_rules.metadata['parse_confidence'] = confidence_rules
        return result_rules


def parse_docx_hybrid(file_content: bytes, filename: str, confidence_threshold: float = 70.0) -> ResumeData:
    """
    Parse DOCX with hybrid approach.

    Similar to parse_pdf_hybrid but for DOCX files.
    """
    # Step 1: Rule-based
    result_rules = parse_docx_rules(file_content, filename)

    # Step 2: Extract raw text
    from docx import Document
    from io import BytesIO
    doc = Document(BytesIO(file_content))
    raw_text = "\n".join([para.text for para in doc.paragraphs])

    confidence_rules = calculate_parse_confidence(result_rules, raw_text)
    logger.info(f"Rule-based DOCX parsing confidence: {confidence_rules}%")

    # Step 3: LLM fallback if needed
    if confidence_rules < confidence_threshold:
        result_llm = parse_with_llm(raw_text, filename)
        confidence_llm = calculate_parse_confidence(result_llm, raw_text)

        if confidence_llm > confidence_rules:
            result_llm.metadata['parse_method'] = 'llm_fallback'
            result_llm.metadata['parse_confidence'] = confidence_llm
            return result_llm

    result_rules.metadata['parse_method'] = 'rules_only'
    result_rules.metadata['parse_confidence'] = confidence_rules
    return result_rules
```

**Usage in main API:**

```python
# In your main API file (e.g., main.py)
from backend.services.parser_hybrid import parse_pdf_hybrid, parse_docx_hybrid

# Replace parse_pdf calls with parse_pdf_hybrid
@app.post("/api/upload")
async def upload_resume(file: UploadFile):
    # ... existing code ...

    if file.filename.endswith('.pdf'):
        result = parse_pdf_hybrid(content, file.filename)
    elif file.filename.endswith('.docx'):
        result = parse_docx_hybrid(content, file.filename)

    # ... rest of logic ...
```

---

## 7. Confidence Scoring

**Standalone utility:**

```python
# backend/scripts/check_confidence.py
#!/usr/bin/env python3
"""Check parsing confidence for a CV"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.parser_hybrid import parse_pdf_hybrid, calculate_parse_confidence

def check_confidence(cv_path: Path):
    """Check parsing confidence for a CV"""
    print(f"Analyzing: {cv_path.name}")

    with open(cv_path, 'rb') as f:
        content = f.read()
        result = parse_pdf_hybrid(content, cv_path.name)

    confidence = result.metadata.get('parse_confidence', 0)
    parse_method = result.metadata.get('parse_method', 'unknown')

    print(f"\n{'='*60}")
    print(f"Confidence Score: {confidence:.1f}%")
    print(f"Parse Method: {parse_method}")
    print(f"Status: {'✅ GOOD' if confidence >= 70 else '⚠️ NEEDS IMPROVEMENT'}")
    print(f"{'='*60}\n")

    print("Sections Detected:")
    print(f"  ✓ Experience: {len(result.experience)} entries")
    print(f"  ✓ Education: {len(result.education)} entries")
    print(f"  ✓ Skills: {len(result.skills)} items")

    print("\nContact Info:")
    print(f"  Name: {result.contact.get('name', 'NOT FOUND')}")
    print(f"  Email: {result.contact.get('email', 'NOT FOUND')}")
    print(f"  Phone: {result.contact.get('phone', 'NOT FOUND')}")
    print(f"  LinkedIn: {result.contact.get('linkedin', 'NOT FOUND')}")

    if result.education:
        print("\nEducation:")
        for i, edu in enumerate(result.education, 1):
            print(f"  {i}. {edu.get('degree', 'N/A')}")
            print(f"     {edu.get('institution', 'N/A')}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python check_confidence.py <cv_path>")
        sys.exit(1)

    check_confidence(Path(sys.argv[1]))
```

---

## 8. Testing Utilities

**Batch test runner:**

```python
# backend/scripts/test_batch.py
#!/usr/bin/env python3
"""Batch test parser on multiple CVs"""

import sys
import json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.parser_hybrid import parse_pdf_hybrid

def test_batch(cv_directory: str):
    """Test parser on batch of CVs"""
    cv_dir = Path(cv_directory)
    pdf_files = list(cv_dir.glob('*.pdf'))

    results = []
    for pdf_path in pdf_files:
        print(f"Processing: {pdf_path.name}...")

        with open(pdf_path, 'rb') as f:
            result = parse_pdf_hybrid(f.read(), pdf_path.name)

        confidence = result.metadata.get('parse_confidence', 0)
        results.append({
            'filename': pdf_path.name,
            'confidence': confidence,
            'experience_count': len(result.experience),
            'education_count': len(result.education),
            'skills_count': len(result.skills),
            'method': result.metadata.get('parse_method', 'unknown')
        })

    # Print summary
    avg_confidence = sum(r['confidence'] for r in results) / len(results)
    llm_usage = sum(1 for r in results if 'llm' in r['method'])

    print(f"\n{'='*60}")
    print(f"Batch Test Results")
    print(f"{'='*60}")
    print(f"Total CVs: {len(results)}")
    print(f"Average Confidence: {avg_confidence:.1f}%")
    print(f"LLM Fallback Used: {llm_usage}/{len(results)} ({llm_usage/len(results)*100:.1f}%)")
    print(f"{'='*60}\n")

    # Save results
    output_file = Path('batch_test_results.json')
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"Results saved to: {output_file}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python test_batch.py <cv_directory>")
        sys.exit(1)

    test_batch(sys.argv[1])
```

---

## Environment Setup

**Add to `.env` file:**

```bash
# .env
ANTHROPIC_API_KEY=your_api_key_here
PARSER_CONFIDENCE_THRESHOLD=70.0
PARSER_USE_HYBRID=true
```

**Install dependencies:**

```bash
# requirements.txt additions
anthropic>=0.18.0
fuzzywuzzy>=0.18.0
python-Levenshtein>=0.20.0  # For faster fuzzy matching
```

**Install:**
```bash
pip install -r requirements.txt
```

---

## Quick Start Guide

1. **Apply quick fixes (Day 1):**
   ```bash
   # Add spacing artifact cleaner
   # Expand section headers
   # Add deduplication
   # Improve skills filtering
   # Test with: pytest backend/tests/test_parser.py
   ```

2. **Test improvements (Day 2):**
   ```bash
   python backend/scripts/test_batch.py backend/storage/uploads/
   ```

3. **Implement hybrid (Day 3-5):**
   ```bash
   # Create parser_hybrid.py
   # Set ANTHROPIC_API_KEY in .env
   # Test with: python backend/scripts/check_confidence.py test.pdf
   ```

4. **Deploy (Day 6-7):**
   ```bash
   # Update API to use hybrid parser
   # Deploy to staging
   # Monitor confidence scores
   # Adjust threshold if needed
   ```

---

## Troubleshooting

### Issue: LLM returns invalid JSON
**Solution:** Add JSON validation and retry logic:

```python
def parse_with_llm(resume_text: str, filename: str, max_retries: int = 2) -> ResumeData:
    for attempt in range(max_retries):
        try:
            # ... existing code ...
            parsed_data = json.loads(json_text)
            return ResumeData(**parsed_data, fileName=filename)
        except json.JSONDecodeError as e:
            logger.warning(f"JSON parse error (attempt {attempt+1}/{max_retries}): {e}")
            if attempt == max_retries - 1:
                # Return empty result on final failure
                return ResumeData(fileName=filename, contact={}, ...)
```

### Issue: Confidence threshold too strict/loose
**Solution:** Tune threshold based on production data:

```python
# Start with 70%, adjust based on LLM usage %
# Target: 20-30% LLM usage
# If LLM usage > 40%: Lower threshold (e.g., 60%)
# If LLM usage < 10%: Raise threshold (e.g., 80%)
```

---

**Questions?** See full documentation in other analysis files.
