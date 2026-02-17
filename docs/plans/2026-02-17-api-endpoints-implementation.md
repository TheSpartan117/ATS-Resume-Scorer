# Phase 5: API Endpoints - Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build REST API endpoints for resume upload, scoring, authentication, and CRUD operations

**Architecture:** FastAPI-based REST API with JWT authentication, file upload handling, and database integration. Public endpoints for upload/score, protected endpoints for user data management, rate limiting on all routes.

**Tech Stack:** FastAPI, SQLAlchemy, PostgreSQL, python-jose (JWT), passlib (bcrypt), python-multipart (file uploads), slowapi (rate limiting)

---

## Context

**Current State:**
- Backend scaffold complete: main.py, database.py, models (User, Resume, AdView)
- Scoring engine complete with all 6 categories (100 points)
- Parser extracts contact info and metadata from PDF/DOCX
- Health check endpoint exists at /health

**What We're Building:**
Complete REST API with 14 endpoints across 4 categories:
1. **Public** (3): upload, score, health
2. **Authentication** (3): signup, login, me
3. **Protected Resume CRUD** (5): list, get, create, update, delete
4. **Ad Tracking** (2): log ad view, check if ad should show

---

## Task 11: Upload Endpoint

**Goal:** Accept PDF/DOCX file, parse it, score it, return results

**Files:**
- Create: `backend/api/__init__.py`
- Create: `backend/api/upload.py`
- Create: `backend/schemas/__init__.py`
- Create: `backend/schemas/resume.py`
- Create: `backend/tests/test_api_upload.py`
- Modify: `backend/main.py`

### Step 1: Create Pydantic schemas for API responses

**Create `backend/schemas/__init__.py`:**
```python
"""Pydantic schemas for API request/response validation"""
```

**Create `backend/schemas/resume.py`:**
```python
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


class UploadResponse(BaseModel):
    """Response for upload endpoint"""
    resumeId: Optional[str] = None  # Only if user is authenticated
    fileName: str
    contact: ContactInfoResponse
    metadata: MetadataResponse
    score: ScoreResponse
    uploadedAt: datetime
```

### Step 2: Write failing test for upload endpoint

**Create `backend/tests/test_api_upload.py`:**
```python
"""Tests for upload endpoint"""
import pytest
from fastapi.testclient import TestClient
from backend.main import app
import io


client = TestClient(app)


def test_upload_pdf_returns_score():
    """Test uploading a PDF resume returns a score"""
    # Create a dummy PDF file (we'll use a simple text file for testing)
    pdf_content = b"%PDF-1.4\nDummy PDF content"
    files = {"file": ("test_resume.pdf", io.BytesIO(pdf_content), "application/pdf")}

    response = client.post("/api/upload", files=files)

    assert response.status_code == 200
    data = response.json()

    # Verify response structure
    assert "fileName" in data
    assert "contact" in data
    assert "metadata" in data
    assert "score" in data
    assert "uploadedAt" in data

    # Verify score structure
    assert "overallScore" in data["score"]
    assert "breakdown" in data["score"]
    assert "issues" in data["score"]


def test_upload_invalid_file_type_returns_400():
    """Test uploading non-PDF/DOCX file returns 400"""
    txt_content = b"This is a text file"
    files = {"file": ("test.txt", io.BytesIO(txt_content), "text/plain")}

    response = client.post("/api/upload", files=files)

    assert response.status_code == 400
    assert "PDF or DOCX only" in response.json()["detail"]


def test_upload_file_too_large_returns_400():
    """Test uploading file >10MB returns 400"""
    # Create 11MB file
    large_content = b"x" * (11 * 1024 * 1024)
    files = {"file": ("large.pdf", io.BytesIO(large_content), "application/pdf")}

    response = client.post("/api/upload", files=files)

    assert response.status_code == 400
    assert "too large" in response.json()["detail"].lower()


def test_upload_with_job_description():
    """Test upload with optional job description for keyword matching"""
    pdf_content = b"%PDF-1.4\nDummy PDF content"
    files = {"file": ("test.pdf", io.BytesIO(pdf_content), "application/pdf")}
    data = {"jobDescription": "Looking for Python developer"}

    response = client.post("/api/upload", files=files, data=data)

    assert response.status_code == 200
    # Score should use job description for keyword matching
    assert response.json()["score"]["overallScore"] >= 0
```

### Step 3: Run test to verify it fails

```bash
cd /Users/sabuj.mondal/ats-resume-scorer/backend
pytest tests/test_api_upload.py::test_upload_pdf_returns_score -v
```

**Expected:** FAIL - "404 Not Found" (endpoint doesn't exist yet)

### Step 4: Implement upload endpoint

**Create `backend/api/__init__.py`:**
```python
"""API route modules"""
```

**Create `backend/api/upload.py`:**
```python
"""Upload endpoint for resume file upload and initial scoring"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timezone
import io

from backend.database import get_db
from backend.services.parser import parse_pdf, parse_docx
from backend.services.scorer import calculate_overall_score
from backend.schemas.resume import UploadResponse, ContactInfoResponse, MetadataResponse, ScoreResponse, CategoryBreakdown

router = APIRouter(prefix="/api", tags=["upload"])

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_TYPES = ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]


@router.post("/upload", response_model=UploadResponse)
async def upload_resume(
    file: UploadFile = File(...),
    jobDescription: Optional[str] = Form(None),
    industry: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Upload a resume file (PDF or DOCX), parse it, and get an initial ATS score.

    - **file**: PDF or DOCX resume file (max 10MB)
    - **jobDescription**: (Optional) Job description for keyword matching
    - **industry**: (Optional) Industry for tailored scoring (e.g., "tech", "sales")

    Returns parsed resume data with comprehensive ATS score (0-100).
    """

    # Validate file type
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Please upload PDF or DOCX only"
        )

    # Read file content
    file_content = await file.read()

    # Validate file size
    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum {MAX_FILE_SIZE // (1024*1024)}MB"
        )

    # Parse resume based on file type
    try:
        if file.content_type == "application/pdf":
            resume_data = parse_pdf(file_content, file.filename)
        else:  # DOCX
            resume_data = parse_docx(file_content, file.filename)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Unable to read file. May be corrupted or password-protected: {str(e)}"
        )

    # Check if resume is empty
    if resume_data.metadata.get("wordCount", 0) < 50:
        raise HTTPException(
            status_code=400,
            detail="Resume appears empty or unreadable"
        )

    # Calculate score
    score_result = calculate_overall_score(
        resume_data,
        job_description=jobDescription or "",
        industry=industry or ""
    )

    # Format response
    contact_response = ContactInfoResponse(**resume_data.contact)
    metadata_response = MetadataResponse(**resume_data.metadata)

    # Convert score breakdown to response format
    breakdown_response = {}
    for category, details in score_result["breakdown"].items():
        breakdown_response[category] = CategoryBreakdown(
            score=details["score"],
            maxScore=details["maxScore"],
            issues=details["issues"]
        )

    score_response = ScoreResponse(
        overallScore=score_result["overallScore"],
        breakdown=breakdown_response,
        issues=score_result["issues"],
        strengths=score_result.get("strengths", [])
    )

    return UploadResponse(
        resumeId=None,  # Guest user, no saved resume
        fileName=file.filename,
        contact=contact_response,
        metadata=metadata_response,
        score=score_response,
        uploadedAt=datetime.now(timezone.utc)
    )
```

**Modify `backend/main.py`** to include the router:

Add after the CORS middleware setup (around line 42):
```python
# Import routers
from backend.api.upload import router as upload_router

# Include routers
app.include_router(upload_router)
```

### Step 5: Run tests to verify they pass

```bash
cd /Users/sabuj.mondal/ats-resume-scorer/backend
pytest tests/test_api_upload.py -v
```

**Expected:** 4 tests pass

### Step 6: Manual API test

```bash
# Start the server
cd /Users/sabuj.mondal/ats-resume-scorer/backend
python -m uvicorn backend.main:app --reload

# In another terminal, test with curl (use a real PDF file)
curl -X POST http://localhost:8000/api/upload \
  -F "file=@/path/to/resume.pdf" \
  -F "jobDescription=Python developer" \
  -F "industry=tech"
```

**Expected:** JSON response with score data

### Step 7: Commit

```bash
git add backend/api/ backend/schemas/ backend/tests/test_api_upload.py backend/main.py
git commit -m "feat: implement upload endpoint with file validation and scoring

- Add upload endpoint at POST /api/upload
- Validate file type (PDF/DOCX only) and size (max 10MB)
- Parse resume and calculate ATS score
- Return structured response with contact, metadata, and score
- Add comprehensive error handling for corrupt/empty files
- Add 4 tests covering success and error cases"
```

---

## Task 12: Score Endpoint

**Goal:** Re-score resume with updated data (for editor use case)

**Files:**
- Create: `backend/api/score.py`
- Create: `backend/tests/test_api_score.py`
- Modify: `backend/main.py`

### Step 1: Write failing test

**Create `backend/tests/test_api_score.py`:**
```python
"""Tests for score endpoint"""
import pytest
from fastapi.testclient import TestClient
from backend.main import app


client = TestClient(app)


def test_score_with_updated_resume_data():
    """Test re-scoring with updated resume data"""
    resume_data = {
        "fileName": "updated_resume.pdf",
        "contact": {
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "555-1234",
            "location": "San Francisco, CA"
        },
        "experience": [
            {"text": "Led team of 10 engineers, developed 5 applications"}
        ],
        "education": [
            {"degree": "BS Computer Science"}
        ],
        "skills": ["Python", "React", "AWS"],
        "metadata": {
            "pageCount": 1,
            "wordCount": 500,
            "hasPhoto": False,
            "fileFormat": "pdf"
        },
        "jobDescription": "Python developer",
        "industry": "tech"
    }

    response = client.post("/api/score", json=resume_data)

    assert response.status_code == 200
    data = response.json()

    assert "overallScore" in data
    assert "breakdown" in data
    assert data["overallScore"] >= 0
    assert data["overallScore"] <= 100


def test_score_requires_resume_data():
    """Test score endpoint requires resume data"""
    response = client.post("/api/score", json={})

    assert response.status_code == 422  # Validation error
```

### Step 2: Run test to verify it fails

```bash
pytest tests/test_api_score.py::test_score_with_updated_resume_data -v
```

**Expected:** FAIL - "404 Not Found"

### Step 3: Implement score endpoint

**Create `backend/api/score.py`:**
```python
"""Score endpoint for re-scoring updated resume data"""
from fastapi import APIRouter, HTTPException
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

from backend.services.parser import ResumeData
from backend.services.scorer import calculate_overall_score
from backend.schemas.resume import ScoreResponse, CategoryBreakdown


router = APIRouter(prefix="/api", tags=["score"])


class ScoreRequest(BaseModel):
    """Request body for score endpoint"""
    fileName: str
    contact: Dict[str, Optional[str]]
    experience: List[Dict] = Field(default_factory=list)
    education: List[Dict] = Field(default_factory=list)
    skills: List[str] = Field(default_factory=list)
    certifications: List[Dict] = Field(default_factory=list)
    metadata: Dict
    jobDescription: Optional[str] = ""
    industry: Optional[str] = ""


@router.post("/score", response_model=ScoreResponse)
async def score_resume(request: ScoreRequest):
    """
    Re-score a resume with updated data (e.g., after editing).

    Used by the frontend editor to get updated scores as user makes changes.

    - **request**: Complete resume data structure
    - **jobDescription**: (Optional) Job description for keyword matching
    - **industry**: (Optional) Industry for tailored scoring

    Returns updated ATS score (0-100).
    """

    # Convert request to ResumeData
    resume_data = ResumeData(
        fileName=request.fileName,
        contact=request.contact,
        experience=request.experience,
        education=request.education,
        skills=request.skills,
        certifications=request.certifications,
        metadata=request.metadata
    )

    # Calculate score
    score_result = calculate_overall_score(
        resume_data,
        job_description=request.jobDescription or "",
        industry=request.industry or ""
    )

    # Convert breakdown to response format
    breakdown_response = {}
    for category, details in score_result["breakdown"].items():
        breakdown_response[category] = CategoryBreakdown(
            score=details["score"],
            maxScore=details["maxScore"],
            issues=details["issues"]
        )

    return ScoreResponse(
        overallScore=score_result["overallScore"],
        breakdown=breakdown_response,
        issues=score_result["issues"],
        strengths=score_result.get("strengths", [])
    )
```

**Modify `backend/main.py`** to include the router:

Add after the upload router import:
```python
from backend.api.score import router as score_router

# Include routers
app.include_router(score_router)
```

### Step 4: Run tests to verify they pass

```bash
pytest tests/test_api_score.py -v
```

**Expected:** 2 tests pass

### Step 5: Commit

```bash
git add backend/api/score.py backend/tests/test_api_score.py backend/main.py
git commit -m "feat: implement score endpoint for re-scoring updated resumes

- Add score endpoint at POST /api/score
- Accept complete resume data structure
- Re-calculate ATS score with optional JD and industry
- Return updated score breakdown and issues
- Add 2 tests for success and validation"
```

---

## Task 13: Auth Utilities (JWT, Password Hashing)

**Goal:** Create utilities for JWT token generation/validation and password hashing

**Files:**
- Create: `backend/auth/__init__.py`
- Create: `backend/auth/jwt.py`
- Create: `backend/auth/password.py`
- Create: `backend/tests/test_auth_utils.py`

### Step 1: Write failing tests

**Create `backend/tests/test_auth_utils.py`:**
```python
"""Tests for authentication utilities"""
import pytest
from backend.auth.password import hash_password, verify_password
from backend.auth.jwt import create_access_token, verify_token


def test_hash_password():
    """Test password hashing"""
    password = "mySecurePassword123"
    hashed = hash_password(password)

    assert hashed != password  # Should be hashed
    assert len(hashed) > 50  # Bcrypt hash is long
    assert hashed.startswith("$2b$")  # Bcrypt format


def test_verify_password_correct():
    """Test password verification with correct password"""
    password = "mySecurePassword123"
    hashed = hash_password(password)

    assert verify_password(password, hashed) is True


def test_verify_password_incorrect():
    """Test password verification with incorrect password"""
    password = "mySecurePassword123"
    hashed = hash_password(password)

    assert verify_password("wrongPassword", hashed) is False


def test_create_access_token():
    """Test JWT token creation"""
    user_id = "123e4567-e89b-12d3-a456-426614174000"
    token = create_access_token({"sub": user_id})

    assert isinstance(token, str)
    assert len(token) > 50  # JWT tokens are long


def test_verify_token_valid():
    """Test JWT token verification with valid token"""
    user_id = "123e4567-e89b-12d3-a456-426614174000"
    token = create_access_token({"sub": user_id})

    payload = verify_token(token)

    assert payload is not None
    assert payload["sub"] == user_id


def test_verify_token_invalid():
    """Test JWT token verification with invalid token"""
    invalid_token = "invalid.jwt.token"

    payload = verify_token(invalid_token)

    assert payload is None
```

### Step 2: Run test to verify it fails

```bash
pytest tests/test_auth_utils.py::test_hash_password -v
```

**Expected:** FAIL - "ModuleNotFoundError"

### Step 3: Implement auth utilities

**Create `backend/auth/__init__.py`:**
```python
"""Authentication utilities"""
```

**Create `backend/auth/password.py`:**
```python
"""Password hashing and verification using bcrypt"""
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.

    Args:
        password: Plain text password

    Returns:
        Bcrypt hashed password
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.

    Args:
        plain_password: Plain text password to verify
        hashed_password: Bcrypt hash to compare against

    Returns:
        True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)
```

**Create `backend/auth/jwt.py`:**
```python
"""JWT token creation and verification"""
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict
from jose import JWTError, jwt
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 7


def create_access_token(data: Dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.

    Args:
        data: Data to encode in the token (typically {"sub": user_id})
        expires_delta: Custom expiration time (default: 7 days)

    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


def verify_token(token: str) -> Optional[Dict]:
    """
    Verify and decode a JWT token.

    Args:
        token: JWT token string

    Returns:
        Decoded token payload if valid, None if invalid/expired
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
```

### Step 4: Run tests to verify they pass

```bash
pytest tests/test_auth_utils.py -v
```

**Expected:** 6 tests pass

### Step 5: Commit

```bash
git add backend/auth/ backend/tests/test_auth_utils.py
git commit -m "feat: implement auth utilities for JWT and password hashing

- Add password hashing with bcrypt
- Add password verification utility
- Add JWT token creation with 7-day expiration
- Add JWT token verification and decoding
- Add 6 comprehensive tests for auth utilities"
```

---

## Task 14: Auth Endpoints (Signup, Login, Me)

**Goal:** Implement user authentication endpoints

**Files:**
- Create: `backend/api/auth.py`
- Create: `backend/auth/dependencies.py`
- Create: `backend/tests/test_api_auth.py`
- Modify: `backend/main.py`
- Modify: `.env.example`

### Step 1: Write failing tests

**Create `backend/tests/test_api_auth.py`:**
```python
"""Tests for authentication endpoints"""
import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.database import Base, engine, SessionLocal
from backend.models.user import User
from backend.auth.password import hash_password


client = TestClient(app)


# Test database setup
@pytest.fixture(scope="function", autouse=True)
def setup_database():
    """Create test database tables before each test"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_signup_creates_user():
    """Test user signup creates new account"""
    response = client.post(
        "/api/signup",
        json={
            "email": "newuser@example.com",
            "password": "securePassword123"
        }
    )

    assert response.status_code == 201
    data = response.json()

    assert "id" in data
    assert data["email"] == "newuser@example.com"
    assert "password" not in data  # Should not return password
    assert "accessToken" in data


def test_signup_duplicate_email_fails():
    """Test signup with existing email returns 400"""
    # Create first user
    client.post(
        "/api/signup",
        json={"email": "duplicate@example.com", "password": "pass123"}
    )

    # Try to create duplicate
    response = client.post(
        "/api/signup",
        json={"email": "duplicate@example.com", "password": "pass456"}
    )

    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


def test_signup_invalid_email_fails():
    """Test signup with invalid email returns 422"""
    response = client.post(
        "/api/signup",
        json={"email": "not-an-email", "password": "pass123"}
    )

    assert response.status_code == 422


def test_login_with_correct_credentials():
    """Test login with correct email/password"""
    # Create user first
    client.post(
        "/api/signup",
        json={"email": "user@example.com", "password": "myPassword123"}
    )

    # Login
    response = client.post(
        "/api/login",
        json={"email": "user@example.com", "password": "myPassword123"}
    )

    assert response.status_code == 200
    data = response.json()

    assert "accessToken" in data
    assert "user" in data
    assert data["user"]["email"] == "user@example.com"


def test_login_with_wrong_password_fails():
    """Test login with wrong password returns 401"""
    # Create user
    client.post(
        "/api/signup",
        json={"email": "user@example.com", "password": "correctPassword"}
    )

    # Try to login with wrong password
    response = client.post(
        "/api/login",
        json={"email": "user@example.com", "password": "wrongPassword"}
    )

    assert response.status_code == 401
    assert "Invalid credentials" in response.json()["detail"]


def test_login_nonexistent_user_fails():
    """Test login with non-existent user returns 401"""
    response = client.post(
        "/api/login",
        json={"email": "nonexistent@example.com", "password": "pass123"}
    )

    assert response.status_code == 401


def test_get_me_with_valid_token():
    """Test /me endpoint returns current user"""
    # Signup to get token
    signup_response = client.post(
        "/api/signup",
        json={"email": "me@example.com", "password": "pass123"}
    )
    token = signup_response.json()["accessToken"]

    # Call /me
    response = client.get(
        "/api/me",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()

    assert data["email"] == "me@example.com"
    assert "password" not in data


def test_get_me_without_token_fails():
    """Test /me endpoint without token returns 401"""
    response = client.get("/api/me")

    assert response.status_code == 401


def test_get_me_with_invalid_token_fails():
    """Test /me endpoint with invalid token returns 401"""
    response = client.get(
        "/api/me",
        headers={"Authorization": "Bearer invalid.token.here"}
    )

    assert response.status_code == 401
```

### Step 2: Run test to verify it fails

```bash
pytest tests/test_api_auth.py::test_signup_creates_user -v
```

**Expected:** FAIL - "404 Not Found"

### Step 3: Create auth dependency for protected routes

**Create `backend/auth/dependencies.py`:**
```python
"""FastAPI dependencies for authentication"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional

from backend.database import get_db
from backend.auth.jwt import verify_token
from backend.models.user import User


security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to get current authenticated user from JWT token.

    Raises:
        HTTPException: 401 if token is invalid or user not found

    Returns:
        User object of authenticated user
    """
    token = credentials.credentials
    payload = verify_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def get_current_user_optional(
    db: Session = Depends(get_db),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
) -> Optional[User]:
    """
    Optional authentication dependency - returns User if authenticated, None if not.

    Used for endpoints that work differently for authenticated vs guest users.
    """
    if credentials is None:
        return None

    try:
        return await get_current_user(credentials, db)
    except HTTPException:
        return None
```

### Step 4: Implement auth endpoints

**Create `backend/api/auth.py`:**
```python
"""Authentication endpoints (signup, login, me)"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from datetime import datetime

from backend.database import get_db
from backend.models.user import User
from backend.auth.password import hash_password, verify_password
from backend.auth.jwt import create_access_token
from backend.auth.dependencies import get_current_user


router = APIRouter(prefix="/api", tags=["auth"])


class SignupRequest(BaseModel):
    """Signup request body"""
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    """Login request body"""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """User data in response"""
    id: str
    email: str
    isPremium: bool
    createdAt: datetime

    class Config:
        from_attributes = True


class AuthResponse(BaseModel):
    """Authentication response with token"""
    accessToken: str
    user: UserResponse


@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def signup(request: SignupRequest, db: Session = Depends(get_db)):
    """
    Create a new user account.

    - **email**: Valid email address (unique)
    - **password**: Password (will be hashed)

    Returns access token and user data.
    """

    # Check if user already exists
    existing_user = db.query(User).filter(User.email == request.email.lower()).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists"
        )

    # Create new user
    hashed_password = hash_password(request.password)
    new_user = User(
        email=request.email.lower(),
        password_hash=hashed_password,
        is_premium=False
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Create access token
    access_token = create_access_token({"sub": str(new_user.id)})

    user_response = UserResponse(
        id=str(new_user.id),
        email=new_user.email,
        isPremium=new_user.is_premium,
        createdAt=new_user.created_at
    )

    return AuthResponse(accessToken=access_token, user=user_response)


@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    Login with email and password.

    - **email**: User's email address
    - **password**: User's password

    Returns access token and user data.
    """

    # Find user by email
    user = db.query(User).filter(User.email == request.email.lower()).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    # Verify password
    if not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    # Create access token
    access_token = create_access_token({"sub": str(user.id)})

    user_response = UserResponse(
        id=str(user.id),
        email=user.email,
        isPremium=user.is_premium,
        createdAt=user.created_at
    )

    return AuthResponse(accessToken=access_token, user=user_response)


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """
    Get current authenticated user's data.

    Requires valid JWT token in Authorization header.
    """

    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        isPremium=current_user.is_premium,
        createdAt=current_user.created_at
    )
```

**Modify `backend/main.py`** to include auth router:

Add after other router imports:
```python
from backend.api.auth import router as auth_router

# Include routers
app.include_router(auth_router)
```

**Update `.env.example`:**
Add:
```
JWT_SECRET_KEY=your-secret-key-change-in-production-use-openssl-rand-hex-32
```

### Step 5: Run tests to verify they pass

```bash
pytest tests/test_api_auth.py -v
```

**Expected:** 9 tests pass

### Step 6: Commit

```bash
git add backend/api/auth.py backend/auth/dependencies.py backend/tests/test_api_auth.py backend/main.py .env.example
git commit -m "feat: implement authentication endpoints (signup, login, me)

- Add POST /api/signup for user registration
- Add POST /api/login for authentication
- Add GET /api/me for current user info
- Add JWT authentication dependencies for protected routes
- Add password hashing on signup
- Add password verification on login
- Add 9 comprehensive tests for auth flow
- Update .env.example with JWT_SECRET_KEY"
```

---

## Task 15: Protected Resume CRUD Endpoints

**Goal:** Implement endpoints for saving and managing user resumes

**Files:**
- Create: `backend/api/resumes.py`
- Create: `backend/tests/test_api_resumes.py`
- Modify: `backend/main.py`

### Step 1: Write failing tests

**Create `backend/tests/test_api_resumes.py`:**
```python
"""Tests for protected resume endpoints"""
import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.database import Base, engine


client = TestClient(app)


@pytest.fixture(scope="function", autouse=True)
def setup_database():
    """Create test database tables"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def auth_token():
    """Create user and return auth token"""
    response = client.post(
        "/api/signup",
        json={"email": "testuser@example.com", "password": "pass123"}
    )
    return response.json()["accessToken"]


def test_create_resume_requires_auth():
    """Test creating resume without auth returns 401"""
    resume_data = {
        "fileName": "test.pdf",
        "contact": {"name": "John", "email": "john@example.com"},
        "metadata": {"pageCount": 1, "wordCount": 500, "hasPhoto": False, "fileFormat": "pdf"}
    }

    response = client.post("/api/resumes", json=resume_data)

    assert response.status_code == 401


def test_create_resume_saves_to_database(auth_token):
    """Test creating resume saves it to database"""
    resume_data = {
        "fileName": "my_resume.pdf",
        "contact": {"name": "Jane Doe", "email": "jane@example.com"},
        "experience": [],
        "education": [],
        "skills": ["Python", "React"],
        "metadata": {"pageCount": 1, "wordCount": 500, "hasPhoto": False, "fileFormat": "pdf"}
    }

    response = client.post(
        "/api/resumes",
        json=resume_data,
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 201
    data = response.json()

    assert "id" in data
    assert data["fileName"] == "my_resume.pdf"
    assert data["contact"]["name"] == "Jane Doe"


def test_list_resumes_returns_user_resumes(auth_token):
    """Test listing resumes returns only user's resumes"""
    # Create two resumes
    resume1 = {
        "fileName": "resume1.pdf",
        "contact": {"name": "User"},
        "metadata": {"pageCount": 1, "wordCount": 500, "hasPhoto": False, "fileFormat": "pdf"}
    }
    resume2 = {
        "fileName": "resume2.pdf",
        "contact": {"name": "User"},
        "metadata": {"pageCount": 1, "wordCount": 600, "hasPhoto": False, "fileFormat": "pdf"}
    }

    client.post("/api/resumes", json=resume1, headers={"Authorization": f"Bearer {auth_token}"})
    client.post("/api/resumes", json=resume2, headers={"Authorization": f"Bearer {auth_token}"})

    # List resumes
    response = client.get(
        "/api/resumes",
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 200
    data = response.json()

    assert len(data) == 2
    assert data[0]["fileName"] in ["resume1.pdf", "resume2.pdf"]


def test_get_resume_by_id(auth_token):
    """Test getting specific resume by ID"""
    # Create resume
    resume_data = {
        "fileName": "test.pdf",
        "contact": {"name": "Test"},
        "metadata": {"pageCount": 1, "wordCount": 500, "hasPhoto": False, "fileFormat": "pdf"}
    }
    create_response = client.post(
        "/api/resumes",
        json=resume_data,
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    resume_id = create_response.json()["id"]

    # Get resume
    response = client.get(
        f"/api/resumes/{resume_id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 200
    data = response.json()

    assert data["id"] == resume_id
    assert data["fileName"] == "test.pdf"


def test_get_nonexistent_resume_returns_404(auth_token):
    """Test getting non-existent resume returns 404"""
    fake_id = "00000000-0000-0000-0000-000000000000"

    response = client.get(
        f"/api/resumes/{fake_id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 404


def test_update_resume(auth_token):
    """Test updating resume"""
    # Create resume
    resume_data = {
        "fileName": "original.pdf",
        "contact": {"name": "Original"},
        "metadata": {"pageCount": 1, "wordCount": 500, "hasPhoto": False, "fileFormat": "pdf"}
    }
    create_response = client.post(
        "/api/resumes",
        json=resume_data,
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    resume_id = create_response.json()["id"]

    # Update resume
    updated_data = {
        "fileName": "updated.pdf",
        "contact": {"name": "Updated", "email": "new@example.com"},
        "metadata": {"pageCount": 2, "wordCount": 800, "hasPhoto": False, "fileFormat": "pdf"}
    }
    response = client.put(
        f"/api/resumes/{resume_id}",
        json=updated_data,
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 200
    data = response.json()

    assert data["fileName"] == "updated.pdf"
    assert data["contact"]["name"] == "Updated"
    assert data["metadata"]["wordCount"] == 800


def test_delete_resume(auth_token):
    """Test deleting resume"""
    # Create resume
    resume_data = {
        "fileName": "to_delete.pdf",
        "contact": {"name": "Delete Me"},
        "metadata": {"pageCount": 1, "wordCount": 500, "hasPhoto": False, "fileFormat": "pdf"}
    }
    create_response = client.post(
        "/api/resumes",
        json=resume_data,
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    resume_id = create_response.json()["id"]

    # Delete resume
    response = client.delete(
        f"/api/resumes/{resume_id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 204

    # Verify it's deleted
    get_response = client.get(
        f"/api/resumes/{resume_id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert get_response.status_code == 404


def test_user_cannot_access_other_user_resume():
    """Test user cannot access another user's resume"""
    # Create user 1 and their resume
    user1_response = client.post(
        "/api/signup",
        json={"email": "user1@example.com", "password": "pass123"}
    )
    user1_token = user1_response.json()["accessToken"]

    resume_response = client.post(
        "/api/resumes",
        json={
            "fileName": "user1_resume.pdf",
            "contact": {"name": "User 1"},
            "metadata": {"pageCount": 1, "wordCount": 500, "hasPhoto": False, "fileFormat": "pdf"}
        },
        headers={"Authorization": f"Bearer {user1_token}"}
    )
    resume_id = resume_response.json()["id"]

    # Create user 2
    user2_response = client.post(
        "/api/signup",
        json={"email": "user2@example.com", "password": "pass123"}
    )
    user2_token = user2_response.json()["accessToken"]

    # Try to access user1's resume as user2
    response = client.get(
        f"/api/resumes/{resume_id}",
        headers={"Authorization": f"Bearer {user2_token}"}
    )

    assert response.status_code == 403  # Forbidden
```

### Step 2: Run test to verify it fails

```bash
pytest tests/test_api_resumes.py::test_create_resume_requires_auth -v
```

**Expected:** FAIL - "404 Not Found"

### Step 3: Implement resume CRUD endpoints

**Create `backend/api/resumes.py`:**
```python
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
```

**Modify `backend/main.py`** to include resumes router:

Add after auth router import:
```python
from backend.api.resumes import router as resumes_router

# Include routers
app.include_router(resumes_router)
```

### Step 4: Run tests to verify they pass

```bash
pytest tests/test_api_resumes.py -v
```

**Expected:** 9 tests pass

### Step 5: Commit

```bash
git add backend/api/resumes.py backend/tests/test_api_resumes.py backend/main.py
git commit -m "feat: implement protected resume CRUD endpoints

- Add POST /api/resumes to save resume
- Add GET /api/resumes to list user's resumes
- Add GET /api/resumes/:id to get specific resume
- Add PUT /api/resumes/:id to update resume
- Add DELETE /api/resumes/:id to delete resume
- Add ownership validation (403 if accessing other user's resume)
- Add 9 comprehensive tests for CRUD operations"
```

---

## Task 16: Ad Tracking Endpoints

**Goal:** Implement endpoints for tracking ad views and determining when to show ads

**Files:**
- Create: `backend/api/ads.py`
- Create: `backend/tests/test_api_ads.py`
- Modify: `backend/main.py`

### Step 1: Write failing tests

**Create `backend/tests/test_api_ads.py`:**
```python
"""Tests for ad tracking endpoints"""
import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.database import Base, engine


client = TestClient(app)


@pytest.fixture(scope="function", autouse=True)
def setup_database():
    """Create test database tables"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_log_ad_view_as_guest():
    """Test logging ad view for guest user"""
    response = client.post(
        "/api/ad-view",
        json={
            "sessionId": "guest-session-123",
            "skipped": False
        }
    )

    assert response.status_code == 201
    data = response.json()

    assert "id" in data
    assert data["sessionId"] == "guest-session-123"
    assert data["skipped"] is False


def test_log_ad_view_authenticated_user():
    """Test logging ad view for authenticated user"""
    # Create user
    signup_response = client.post(
        "/api/signup",
        json={"email": "user@example.com", "password": "pass123"}
    )
    token = signup_response.json()["accessToken"]

    # Log ad view
    response = client.post(
        "/api/ad-view",
        json={"skipped": True},
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 201
    data = response.json()

    assert "userId" in data
    assert data["skipped"] is True


def test_should_show_ad_first_action():
    """Test should NOT show ad on first action"""
    response = client.get(
        "/api/should-show-ad",
        params={"sessionId": "new-session"}
    )

    assert response.status_code == 200
    data = response.json()

    assert data["shouldShowAd"] is False
    assert data["actionCount"] == 0


def test_should_show_ad_after_first_score():
    """Test SHOULD show ad after first free score"""
    session_id = "test-session-456"

    # Simulate first action (upload/score) - no ad
    response1 = client.get(
        "/api/should-show-ad",
        params={"sessionId": session_id, "actionCount": 1}
    )
    assert response1.json()["shouldShowAd"] is False

    # Second action - should show ad
    response2 = client.get(
        "/api/should-show-ad",
        params={"sessionId": session_id, "actionCount": 2}
    )
    assert response2.json()["shouldShowAd"] is True


def test_premium_user_never_sees_ads():
    """Test premium users don't see ads"""
    # Create user (would need to manually set is_premium in real scenario)
    # For now, test the logic with isPremium parameter

    response = client.get(
        "/api/should-show-ad",
        params={"sessionId": "premium-session", "actionCount": 10, "isPremium": True}
    )

    assert response.status_code == 200
    assert response.json()["shouldShowAd"] is False
```

### Step 2: Run test to verify it fails

```bash
pytest tests/test_api_ads.py::test_log_ad_view_as_guest -v
```

**Expected:** FAIL - "404 Not Found"

### Step 3: Implement ad tracking endpoints

**Create `backend/api/ads.py`:**
```python
"""Ad tracking endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone

from backend.database import get_db
from backend.models.ad_view import AdView
from backend.models.user import User
from backend.auth.dependencies import get_current_user_optional


router = APIRouter(prefix="/api", tags=["ads"])


class AdViewRequest(BaseModel):
    """Request body for logging ad view"""
    sessionId: Optional[str] = None  # For guest users
    skipped: bool


class AdViewResponse(BaseModel):
    """Response for ad view logging"""
    id: str
    userId: Optional[str]
    sessionId: Optional[str]
    actionCount: int
    viewedAt: datetime
    skipped: bool


class ShouldShowAdResponse(BaseModel):
    """Response for should-show-ad check"""
    shouldShowAd: bool
    actionCount: int


@router.post("/ad-view", response_model=AdViewResponse, status_code=status.HTTP_201_CREATED)
async def log_ad_view(
    request: AdViewRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Log an ad view/impression.

    Tracks when ads are shown and whether they were skipped.
    Works for both authenticated users and guest sessions.
    """

    # Count previous actions for this user/session
    if current_user:
        action_count = db.query(AdView)\
            .filter(AdView.user_id == current_user.id)\
            .count() + 1
        session_id = None
        user_id = current_user.id
    else:
        if not request.sessionId:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="sessionId required for guest users"
            )
        action_count = db.query(AdView)\
            .filter(AdView.session_id == request.sessionId)\
            .count() + 1
        session_id = request.sessionId
        user_id = None

    # Create ad view record
    ad_view = AdView(
        user_id=user_id,
        session_id=session_id,
        action_count=action_count,
        skipped=request.skipped
    )

    db.add(ad_view)
    db.commit()
    db.refresh(ad_view)

    return AdViewResponse(
        id=str(ad_view.id),
        userId=str(ad_view.user_id) if ad_view.user_id else None,
        sessionId=ad_view.session_id,
        actionCount=ad_view.action_count,
        viewedAt=ad_view.viewed_at,
        skipped=ad_view.skipped
    )


@router.get("/should-show-ad", response_model=ShouldShowAdResponse)
async def should_show_ad(
    sessionId: Optional[str] = None,
    actionCount: Optional[int] = None,
    isPremium: Optional[bool] = False,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Check if an ad should be shown for this user/session.

    Business logic:
    - First action (upload): FREE, no ad
    - Subsequent actions (re-score): Show ad
    - Premium users: Never show ads

    Query params:
    - sessionId: For guest users (required if not authenticated)
    - actionCount: Current action count (optional, will query DB if not provided)
    - isPremium: Override premium status (for testing)
    """

    # Premium users never see ads
    if current_user and current_user.is_premium:
        return ShouldShowAdResponse(shouldShowAd=False, actionCount=0)

    if isPremium:
        return ShouldShowAdResponse(shouldShowAd=False, actionCount=0)

    # Get action count
    if actionCount is not None:
        # Use provided count (for efficiency)
        current_action_count = actionCount
    else:
        # Query database
        if current_user:
            current_action_count = db.query(AdView)\
                .filter(AdView.user_id == current_user.id)\
                .count()
        elif sessionId:
            current_action_count = db.query(AdView)\
                .filter(AdView.session_id == sessionId)\
                .count()
        else:
            # New guest user, first action
            current_action_count = 0

    # Show ad if actionCount >= 1 (i.e., after first free score)
    should_show = current_action_count >= 1

    return ShouldShowAdResponse(
        shouldShowAd=should_show,
        actionCount=current_action_count
    )
```

**Modify `backend/main.py`** to include ads router:

Add after resumes router import:
```python
from backend.api.ads import router as ads_router

# Include routers
app.include_router(ads_router)
```

### Step 4: Run tests to verify they pass

```bash
pytest tests/test_api_ads.py -v
```

**Expected:** 5 tests pass

### Step 5: Commit

```bash
git add backend/api/ads.py backend/tests/test_api_ads.py backend/main.py
git commit -m "feat: implement ad tracking endpoints

- Add POST /api/ad-view to log ad impressions
- Add GET /api/should-show-ad to check if ad should display
- Support both authenticated users and guest sessions
- Track action count for ad display logic
- Premium users never see ads
- First score is free, subsequent scores show ads
- Add 5 tests for ad tracking logic"
```

---

## Verification

### Run all API tests

```bash
cd /Users/sabuj.mondal/ats-resume-scorer/backend
pytest tests/test_api_*.py -v
```

**Expected:** All tests pass (~30 tests total)

### Manual API testing

```bash
# Start server
python -m uvicorn backend.main:app --reload

# Test upload
curl -X POST http://localhost:8000/api/upload \
  -F "file=@test_resume.pdf"

# Test signup
curl -X POST http://localhost:8000/api/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"pass123"}'

# Test login
curl -X POST http://localhost:8000/api/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"pass123"}'

# Test /me (use token from login)
curl -X GET http://localhost:8000/api/me \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"

# Check docs
open http://localhost:8000/docs
```

### Check API documentation

FastAPI auto-generates OpenAPI docs at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

Verify all 14 endpoints are documented with proper schemas.

---

## Final Commit

```bash
git add .
git commit -m "chore: Phase 5 API Endpoints complete

Summary:
- 14 REST API endpoints implemented
- Public: upload, score, health
- Auth: signup, login, me
- Protected CRUD: list, get, create, update, delete resumes
- Ad tracking: log ad view, check if ad should show
- JWT authentication with bcrypt password hashing
- Comprehensive test suite (30+ tests)
- All tests passing
- OpenAPI documentation auto-generated"
```

---

## Success Metrics

Phase 5 is complete when:
- ✅ All 14 endpoints implemented and working
- ✅ All tests passing (30+ tests)
- ✅ JWT authentication functional
- ✅ Protected routes require valid token
- ✅ Users can upload, score, save, and manage resumes
- ✅ Ad tracking logic works correctly
- ✅ API documentation is accessible
- ✅ No security vulnerabilities (passwords hashed, tokens validated)

**Next Phase:** Phase 6 - Frontend Upload & Display (React UI)
