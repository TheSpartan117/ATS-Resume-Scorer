# ATS Resume Scorer - Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a comprehensive ATS resume scoring platform with unlimited free scoring (ad-supported), rich text editing, and optional user accounts.

**Architecture:** React frontend (Vercel) communicates with FastAPI backend (Render) via REST API. Backend parses PDF/DOCX resumes, runs rule-based scoring engine (50+ criteria), stores data in PostgreSQL. Frontend provides rich text editor (TipTap) for resume editing and real-time score updates.

**Tech Stack:** React 18 + TypeScript + Tailwind + TipTap (frontend), FastAPI + SQLAlchemy + PyMuPDF + python-docx + spaCy (backend), PostgreSQL (database), Google AdSense (ads), Vercel + Render (hosting)

---

## Phase 1: Project Setup & Infrastructure

### Task 1: Backend Project Structure

**Files:**
- Create: `backend/main.py`
- Create: `backend/requirements.txt`
- Create: `backend/.env.example`
- Create: `backend/.gitignore`
- Create: `backend/Dockerfile`
- Create: `backend/README.md`

**Step 1: Create backend directory and requirements.txt**

```bash
cd /Users/sabuj.mondal/ats-resume-scorer
mkdir -p backend
cd backend
```

Create `requirements.txt`:
```txt
fastapi==0.110.0
uvicorn[standard]==0.27.0
python-multipart==0.0.9
python-docx==1.1.0
PyMuPDF==1.23.0
pdfplumber==0.10.0
spacy==3.7.0
sqlalchemy==2.0.25
psycopg2-binary==2.9.9
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-dotenv==1.0.1
pydantic==2.6.0
slowapi==0.1.9
```

**Step 2: Create minimal FastAPI app**

Create `main.py`:
```python
"""
ATS Resume Scorer API
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="ATS Resume Scorer API",
    description="API for scoring and analyzing resumes for ATS compatibility",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "ATS Resume Scorer API", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

**Step 3: Create .env.example**

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost/ats_scorer

# JWT
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=10080

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# File limits
MAX_FILE_SIZE_MB=10

# Environment
ENVIRONMENT=development
```

**Step 4: Create .gitignore**

```
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.env
*.log
.pytest_cache/
.coverage
htmlcov/
dist/
build/
*.egg-info/
```

**Step 5: Create Dockerfile**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for PDF parsing
RUN apt-get update && apt-get install -y \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download spaCy model
RUN python -m spacy download en_core_web_sm

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Step 6: Test backend startup**

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
python main.py
```

Expected: Server runs on http://localhost:8000
Visit: http://localhost:8000/health
Expected: `{"status":"healthy"}`

**Step 7: Commit**

```bash
git add backend/
git commit -m "feat: initialize FastAPI backend with health check

- FastAPI app with CORS configuration
- Requirements.txt with all dependencies
- Dockerfile for production deployment
- Development setup instructions

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

### Task 2: Frontend Project Structure

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/tsconfig.json`
- Create: `frontend/vite.config.ts`
- Create: `frontend/tailwind.config.js`
- Create: `frontend/src/main.tsx`
- Create: `frontend/src/App.tsx`
- Create: `frontend/index.html`

**Step 1: Create frontend with Vite + React + TypeScript**

```bash
cd /Users/sabuj.mondal/ats-resume-scorer
npm create vite@latest frontend -- --template react-ts
cd frontend
npm install
```

**Step 2: Install Tailwind CSS**

```bash
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

**Step 3: Configure Tailwind**

Edit `tailwind.config.js`:
```javascript
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
```

**Step 4: Add Tailwind directives**

Create `src/index.css`:
```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

**Step 5: Create minimal App component**

Edit `src/App.tsx`:
```typescript
import './index.css'

function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          ATS Resume Scorer
        </h1>
        <p className="text-gray-600">
          Upload your resume and get instant ATS compatibility score
        </p>
      </div>
    </div>
  )
}

export default App
```

**Step 6: Test frontend**

```bash
npm run dev
```

Expected: Opens http://localhost:5173
Expected: See "ATS Resume Scorer" heading

**Step 7: Commit**

```bash
git add frontend/
git commit -m "feat: initialize React frontend with Tailwind CSS

- Vite + React + TypeScript setup
- Tailwind CSS configuration
- Minimal landing page

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

### Task 3: Database Models

**Files:**
- Create: `backend/database.py`
- Create: `backend/models/__init__.py`
- Create: `backend/models/user.py`
- Create: `backend/models/resume.py`
- Create: `backend/models/ad_view.py`

**Step 1: Create database connection**

Create `backend/database.py`:
```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://localhost/ats_scorer")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**Step 2: Create User model**

Create `backend/models/user.py`:
```python
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from backend.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    is_premium = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

    # Relationships
    resumes = relationship("Resume", back_populates="user", cascade="all, delete-orphan")
    ad_views = relationship("AdView", back_populates="user", cascade="all, delete-orphan")
```

**Step 3: Create Resume model**

Create `backend/models/resume.py`:
```python
from sqlalchemy import Column, String, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from backend.database import Base

class Resume(Base):
    __tablename__ = "resumes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    file_name = Column(String(255), nullable=False)
    resume_data = Column(JSON, nullable=False)
    latest_score = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="resumes")
```

**Step 4: Create AdView model**

Create `backend/models/ad_view.py`:
```python
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from backend.database import Base

class AdView(Base):
    __tablename__ = "ad_views"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    session_id = Column(String(255), index=True)
    action_count = Column(Integer, nullable=False)
    viewed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    skipped = Column(Boolean, default=False)

    # Relationships
    user = relationship("User", back_populates="ad_views")
```

**Step 5: Create models __init__.py**

Create `backend/models/__init__.py`:
```python
from backend.models.user import User
from backend.models.resume import Resume
from backend.models.ad_view import AdView

__all__ = ["User", "Resume", "AdView"]
```

**Step 6: Create database initialization script**

Create `backend/init_db.py`:
```python
from backend.database import engine, Base
from backend.models import User, Resume, AdView

def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully")

if __name__ == "__main__":
    init_db()
```

**Step 7: Test database creation**

```bash
# Make sure PostgreSQL is running locally or use sqlite for testing
export DATABASE_URL="sqlite:///./test.db"
python backend/init_db.py
```

Expected: "✅ Database tables created successfully"

**Step 8: Commit**

```bash
git add backend/database.py backend/models/ backend/init_db.py
git commit -m "feat: add database models for users, resumes, and ad tracking

- SQLAlchemy models with relationships
- Database session management
- Database initialization script

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Phase 2: Backend - File Parsing

### Task 4: PDF Parser

**Files:**
- Create: `backend/services/__init__.py`
- Create: `backend/services/parser.py`
- Create: `backend/tests/test_parser.py`
- Create: `backend/tests/test_resumes/sample.pdf` (you'll need to create or find a sample)

**Step 1: Write PDF parser test**

Create `backend/tests/test_parser.py`:
```python
import pytest
from backend.services.parser import parse_pdf, parse_docx, ResumeData

def test_parse_pdf_extracts_basic_info():
    """Test that PDF parser extracts contact information"""
    # This test requires a sample PDF
    # For now, we'll test the structure
    resume_data = ResumeData(
        fileName="test.pdf",
        contact={
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "555-1234"
        },
        experience=[],
        education=[],
        skills=[],
        metadata={"pageCount": 1, "wordCount": 100, "hasPhoto": False, "fileFormat": "pdf"}
    )

    assert resume_data.contact["name"] == "John Doe"
    assert resume_data.contact["email"] == "john@example.com"
    assert resume_data.metadata["fileFormat"] == "pdf"
```

**Step 2: Run test to see it fail**

```bash
cd backend
pytest tests/test_parser.py -v
```

Expected: ImportError (modules don't exist yet)

**Step 3: Create parser service with data models**

Create `backend/services/parser.py`:
```python
"""
Resume parsing service - extracts structured data from PDF and DOCX files
"""

import fitz  # PyMuPDF
import pdfplumber
from docx import Document
from typing import Dict, List, Optional, Any
from pydantic import BaseModel
import re
import logging

logger = logging.getLogger(__name__)

class ContactInfo(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin: Optional[str] = None
    website: Optional[str] = None

class Experience(BaseModel):
    title: str
    company: str
    duration: str
    bullets: List[str]

class Education(BaseModel):
    degree: str
    school: str
    year: str

class Certification(BaseModel):
    name: str
    issuer: str
    year: str

class ResumeMetadata(BaseModel):
    pageCount: int
    wordCount: int
    hasPhoto: bool
    fileFormat: str

class ResumeData(BaseModel):
    fileName: str
    contact: Dict[str, Optional[str]]
    summary: Optional[str] = None
    experience: List[Dict[str, Any]]
    education: List[Dict[str, Any]]
    skills: List[str]
    certifications: Optional[List[Dict[str, Any]]] = None
    metadata: Dict[str, Any]

def extract_email(text: str) -> Optional[str]:
    """Extract email address from text"""
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    match = re.search(email_pattern, text)
    return match.group(0) if match else None

def extract_phone(text: str) -> Optional[str]:
    """Extract phone number from text"""
    phone_pattern = r'(\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})'
    match = re.search(phone_pattern, text)
    return match.group(0) if match else None

def extract_linkedin(text: str) -> Optional[str]:
    """Extract LinkedIn URL from text"""
    linkedin_pattern = r'linkedin\.com/in/[A-Za-z0-9_-]+'
    match = re.search(linkedin_pattern, text)
    return match.group(0) if match else None

def parse_pdf(file_content: bytes, filename: str) -> ResumeData:
    """Parse PDF resume and extract structured data"""
    try:
        # Open PDF with PyMuPDF
        doc = fitz.open(stream=file_content, filetype="pdf")

        # Extract all text
        full_text = ""
        for page in doc:
            full_text += page.get_text()

        # Count pages
        page_count = doc.page_count

        # Count words
        word_count = len(full_text.split())

        # Check for images (photos)
        has_photo = False
        for page in doc:
            if len(page.get_images()) > 0:
                has_photo = True
                break

        doc.close()

        # Extract contact information from first 500 characters
        header_text = full_text[:500]

        # Try to extract name (usually first line)
        lines = full_text.split('\n')
        name = lines[0].strip() if lines else None

        contact_info = {
            "name": name,
            "email": extract_email(header_text),
            "phone": extract_phone(header_text),
            "location": None,  # TODO: Implement location extraction
            "linkedin": extract_linkedin(full_text),
            "website": None  # TODO: Implement website extraction
        }

        # Basic metadata
        metadata = {
            "pageCount": page_count,
            "wordCount": word_count,
            "hasPhoto": has_photo,
            "fileFormat": "pdf"
        }

        # TODO: Extract sections (experience, education, skills)
        # For now, return minimal structure
        return ResumeData(
            fileName=filename,
            contact=contact_info,
            summary=None,
            experience=[],
            education=[],
            skills=[],
            certifications=None,
            metadata=metadata
        )

    except Exception as e:
        logger.error(f"Error parsing PDF: {str(e)}")
        raise ValueError(f"Failed to parse PDF: {str(e)}")

def parse_docx(file_content: bytes, filename: str) -> ResumeData:
    """Parse DOCX resume and extract structured data"""
    try:
        from io import BytesIO
        doc = Document(BytesIO(file_content))

        # Extract all text
        full_text = "\n".join([para.text for para in doc.paragraphs])

        # Count words
        word_count = len(full_text.split())

        # Extract contact info
        header_text = full_text[:500]
        lines = full_text.split('\n')
        name = lines[0].strip() if lines else None

        contact_info = {
            "name": name,
            "email": extract_email(header_text),
            "phone": extract_phone(header_text),
            "location": None,
            "linkedin": extract_linkedin(full_text),
            "website": None
        }

        metadata = {
            "pageCount": 1,  # DOCX doesn't have explicit pages
            "wordCount": word_count,
            "hasPhoto": False,  # TODO: Check for images
            "fileFormat": "docx"
        }

        return ResumeData(
            fileName=filename,
            contact=contact_info,
            summary=None,
            experience=[],
            education=[],
            skills=[],
            certifications=None,
            metadata=metadata
        )

    except Exception as e:
        logger.error(f"Error parsing DOCX: {str(e)}")
        raise ValueError(f"Failed to parse DOCX: {str(e)}")
```

**Step 4: Run test**

```bash
pytest tests/test_parser.py -v
```

Expected: PASS (basic structure test)

**Step 5: Commit**

```bash
git add backend/services/parser.py backend/tests/test_parser.py
git commit -m "feat: add PDF and DOCX parser with contact extraction

- Extract text, page count, word count from PDF/DOCX
- Extract email, phone, LinkedIn from header
- Basic ResumeData structure with Pydantic models
- TODO: Section extraction (experience, education, skills)

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Phase 3: Backend - Scoring Engine

### Task 5: Contact Info Scorer

**Files:**
- Create: `backend/services/scorer.py`
- Create: `backend/tests/test_scorer.py`

**Step 1: Write test for contact info scoring**

Create `backend/tests/test_scorer.py`:
```python
import pytest
from backend.services.scorer import score_contact_info
from backend.services.parser import ResumeData

def test_complete_contact_info_gets_full_score():
    """Test that complete contact info receives 10/10 points"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "555-1234",
            "location": "San Francisco, CA",
            "linkedin": "linkedin.com/in/johndoe",
            "website": None
        },
        experience=[],
        education=[],
        skills=[],
        metadata={"pageCount": 1, "wordCount": 500, "hasPhoto": False, "fileFormat": "pdf"}
    )

    result = score_contact_info(resume)

    assert result["score"] == 10
    assert len(result["issues"]) == 0

def test_missing_email_reduces_score():
    """Test that missing email is flagged as critical issue"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={
            "name": "John Doe",
            "email": None,
            "phone": "555-1234",
            "location": "San Francisco, CA",
            "linkedin": None,
            "website": None
        },
        experience=[],
        education=[],
        skills=[],
        metadata={"pageCount": 1, "wordCount": 500, "hasPhoto": False, "fileFormat": "pdf"}
    )

    result = score_contact_info(resume)

    assert result["score"] < 10
    assert any("email" in issue[1].lower() for issue in result["issues"])
    assert any(issue[0] == "critical" for issue in result["issues"])
```

**Step 2: Run test to see it fail**

```bash
pytest tests/test_scorer.py -v
```

Expected: ImportError or FAIL

**Step 3: Implement contact info scorer**

Create `backend/services/scorer.py`:
```python
"""
ATS Resume Scoring Engine
Evaluates resumes across 6 categories with 50+ rules
"""

from backend.services.parser import ResumeData
from typing import Dict, List, Tuple
import re
import logging

logger = logging.getLogger(__name__)

# Type alias for issues: (severity, message)
Issue = Tuple[str, str]

def score_contact_info(resume: ResumeData) -> Dict:
    """
    Score contact information (10 points total)
    - Name: 2 points
    - Email: 2 points
    - Phone: 2 points
    - Location: 2 points
    - LinkedIn/Website: 2 points
    """
    score = 0
    issues: List[Issue] = []

    contact = resume.contact

    # Name (2 points)
    if contact.get("name"):
        score += 2
    else:
        issues.append(("critical", "Missing: Full name"))

    # Email (2 points)
    if contact.get("email"):
        score += 2
    else:
        issues.append(("critical", "Missing: Email address"))

    # Phone (2 points)
    if contact.get("phone"):
        score += 2
    else:
        issues.append(("warning", "Missing: Phone number"))

    # Location (2 points)
    if contact.get("location"):
        score += 2
    else:
        issues.append(("suggestion", "Add location (City, State)"))

    # LinkedIn or Website (2 points)
    if contact.get("linkedin") or contact.get("website"):
        score += 2
    else:
        issues.append(("suggestion", "Add LinkedIn profile or portfolio"))

    return {
        "score": score,
        "issues": issues,
        "category": "contactInfo"
    }

def score_formatting(resume: ResumeData) -> Dict:
    """
    Score formatting and structure (20 points total)
    - Page count: 4 points
    - No photo: 2 points
    - File format: 2 points
    - TODO: Add more formatting checks
    """
    score = 0
    issues: List[Issue] = []

    metadata = resume.metadata

    # Page count (4 points)
    page_count = metadata.get("pageCount", 0)
    if page_count == 1:
        score += 4
    elif page_count == 2:
        score += 3
    elif page_count > 2:
        issues.append(("warning", f"Too long: {page_count} pages (ideal: 1-2)"))

    # No photo (2 points) - ATS can't parse images
    if not metadata.get("hasPhoto", False):
        score += 2
    else:
        issues.append(("warning", "Remove photo - ATS systems can't process images"))

    # File format (2 points)
    if metadata.get("fileFormat") == "docx":
        score += 2
    else:
        issues.append(("suggestion", "DOCX format is more ATS-friendly than PDF"))

    # Placeholder for additional formatting checks
    # TODO: Consistent formatting, sections, etc.
    score += 8  # Placeholder score for now

    return {
        "score": score,
        "issues": issues,
        "category": "formatting"
    }

def calculate_overall_score(resume: ResumeData, context: Dict = None) -> Dict:
    """
    Calculate overall ATS score by running all scoring functions
    Returns ScoreResult dictionary
    """
    contact_result = score_contact_info(resume)
    format_result = score_formatting(resume)

    # TODO: Add other scorers (keywords, content, length, industry)

    # Aggregate scores
    overall_score = (
        contact_result["score"] +
        format_result["score"]
        # + other scores
    )

    # Aggregate issues
    all_issues = []
    all_issues.extend(contact_result["issues"])
    all_issues.extend(format_result["issues"])

    # Sort by severity
    severity_order = {"critical": 0, "warning": 1, "suggestion": 2}
    all_issues.sort(key=lambda x: severity_order[x[0]])

    return {
        "overallScore": overall_score,
        "categoryScores": {
            "contactInfo": contact_result["score"],
            "formatting": format_result["score"],
            "keywords": 0,  # TODO
            "contentQuality": 0,  # TODO
            "length": 0,  # TODO
            "industrySpecific": 0  # TODO
        },
        "issues": [{"severity": sev, "message": msg} for sev, msg in all_issues],
        "strengths": []  # TODO: Identify strengths
    }
```

**Step 4: Run tests**

```bash
pytest tests/test_scorer.py -v
```

Expected: PASS

**Step 5: Commit**

```bash
git add backend/services/scorer.py backend/tests/test_scorer.py
git commit -m "feat: add contact info and formatting scorers

- Contact info scorer (10 points)
- Basic formatting scorer (20 points)
- Overall score calculation structure
- TODO: Content, keywords, length, industry scorers

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Implementation Status

**This plan covers MVP Phase 1 (Foundation):**

✅ Phase 1: Project Setup & Infrastructure (Tasks 1-3)
- Backend FastAPI setup
- Frontend React + Tailwind setup
- Database models (Users, Resumes, Ad Views)

✅ Phase 2: Backend - File Parsing (Task 4)
- PDF/DOCX parser with contact extraction
- Basic resume data structure

✅ Phase 3: Backend - Scoring Engine (Task 5)
- Contact info scorer (10 points)
- Formatting scorer (20 points)
- Overall score calculation framework

**Total: 5 tasks to get the foundation working**

---

## Next Steps (To Be Planned)

**Phase 4: Complete Scoring Engine** - Add remaining scorers:
- Keywords optimizer (15 points)
- Content quality analyzer (25 points)
- Length & density checker (10 points)
- Industry-specific rules (20 points)

**Phase 5: API Endpoints** - Build REST API:
- POST /api/upload (upload resume, get score)
- POST /api/score (re-score with edits)
- Auth endpoints (signup, login)
- Resume CRUD endpoints

**Phase 6: Frontend - Upload & Display** - Build UI:
- File uploader component
- Score display card
- Issues list
- Category breakdown

**Phase 7: Frontend - Rich Text Editor** - Add editing:
- TipTap editor integration
- Section management
- Re-score button

**Phase 8: Authentication & Accounts** - Add user system:
- JWT authentication
- Signup/login flows
- Save resumes to database

**Phase 9: Ad Integration** - Add monetization:
- Google AdSense setup
- Ad tracking logic
- Premium tier

**Phase 10: Testing & Deployment** - Production ready:
- E2E tests
- Deploy to Vercel + Render
- GitHub Actions CI/CD

---

## How to Execute This Plan

**Option 1: Execute in this session**
Use `@superpowers:subagent-driven-development` to implement tasks 1-5 with automated code review after each task.

**Option 2: Execute in parallel session**
Open new terminal, cd to `/Users/sabuj.mondal/ats-resume-scorer`, and use `@superpowers:executing-plans` to batch execute tasks 1-5.

**Recommendation**: Start with Option 1 to implement the foundation (Tasks 1-5), then create follow-up implementation plans for Phases 4-10.

---

**Created:** 2026-02-17
**Status:** Ready for execution (MVP Phase 1)
**Estimated Time:** 4-6 hours for Tasks 1-5
