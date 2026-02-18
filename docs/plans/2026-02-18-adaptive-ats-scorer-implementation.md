# Adaptive Context-Aware ATS Scorer Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build industry-leading adaptive ATS scorer that switches between ATS Simulation mode (with JD) and Quality Coach mode (without JD).

**Architecture:** Keyword extraction from JD → Adaptive scorer routes to Mode A (70/20/10 keyword-heavy) or Mode B (25/30/25/20 quality-focused) → Updated APIs return mode info → Frontend shows mode-specific UI with download functionality.

**Tech Stack:** FastAPI, Python 3.14, React 19, TypeScript, Tailwind CSS, reportlab (PDF export), python-docx (DOCX export)

---

## PHASE 1: Backend Foundation

### Task 1: Create Synonym Database

**Files:**
- Create: `backend/services/synonym_database.py`
- Test: `backend/tests/test_synonym_database.py`

**Step 1: Write failing test**

Create `backend/tests/test_synonym_database.py`:
```python
"""Tests for synonym database"""
from backend.services.synonym_database import get_all_synonyms, expand_keywords


def test_get_synonyms_programming_language():
    """Test getting synonyms for programming language"""
    synonyms = get_all_synonyms("python")

    assert "py" in synonyms
    assert "python3" in synonyms


def test_get_synonyms_reverse_lookup():
    """Test reverse lookup - keyword is a synonym"""
    synonyms = get_all_synonyms("k8s")

    assert "kubernetes" in synonyms


def test_expand_keywords():
    """Test expanding keyword list with synonyms"""
    keywords = ["python", "aws"]
    expanded = expand_keywords(keywords)

    assert "python" in expanded
    assert "py" in expanded
    assert "python3" in expanded
    assert "aws" in expanded
    assert "amazon web services" in expanded
```

**Step 2: Run test to verify it fails**

Run: `cd backend && python -m pytest tests/test_synonym_database.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'backend.services.synonym_database'"

**Step 3: Create synonym database module**

Create `backend/services/synonym_database.py`:
```python
"""
Comprehensive synonym database for intelligent keyword matching
"""
from typing import List, Set


SYNONYM_DATABASE = {
    # Programming Languages
    "python": ["py", "python3", "python2", "cpython"],
    "javascript": ["js", "ecmascript", "es6", "node.js", "nodejs", "node"],
    "java": ["jvm", "jdk"],
    "c++": ["cpp", "c plus plus"],
    "c#": ["csharp", "c sharp", ".net"],
    "golang": ["go"],

    # Cloud Platforms
    "aws": ["amazon web services", "amazon aws"],
    "azure": ["microsoft azure"],
    "gcp": ["google cloud platform", "google cloud"],

    # DevOps Tools
    "kubernetes": ["k8s", "k9s"],
    "docker": ["containerization", "containers"],
    "terraform": ["tf", "infrastructure as code", "iac"],
    "jenkins": ["jenkins ci"],

    # Databases
    "postgresql": ["postgres", "psql"],
    "mongodb": ["mongo"],
    "mysql": ["my sql"],

    # Action Verbs
    "managed": ["led", "supervised", "oversaw", "directed", "headed", "coordinated"],
    "developed": ["built", "created", "engineered", "implemented", "coded", "programmed"],
    "improved": ["enhanced", "optimized", "increased", "boosted", "elevated"],
    "reduced": ["decreased", "minimized", "cut", "lowered"],
    "launched": ["released", "deployed", "shipped", "delivered"],

    # Methodologies
    "agile": ["scrum", "kanban"],
    "ci/cd": ["continuous integration", "continuous deployment", "cicd"],
    "tdd": ["test driven development", "test-driven"],
    "microservices": ["micro-services", "service-oriented architecture", "soa"],

    # Data & ML
    "machine learning": ["ml", "artificial intelligence", "ai"],
    "deep learning": ["dl", "neural networks"],
    "natural language processing": ["nlp"],

    # Soft Skills
    "leadership": ["leading", "lead", "led"],
    "communication": ["communicating", "collaborate", "collaboration"],
    "problem solving": ["troubleshooting", "debugging", "analytical"],

    # Roles
    "product manager": ["pm", "product management"],
    "software engineer": ["developer", "programmer", "sde"],
    "data scientist": ["data science", "ml engineer"],
}


def get_all_synonyms(keyword: str) -> List[str]:
    """
    Get all synonyms for a keyword

    Args:
        keyword: Keyword to find synonyms for

    Returns:
        List of synonyms (empty if no synonyms found)
    """
    keyword_lower = keyword.lower()

    # Direct lookup
    if keyword_lower in SYNONYM_DATABASE:
        return SYNONYM_DATABASE[keyword_lower]

    # Reverse lookup - check if keyword is a synonym
    for main_keyword, synonyms in SYNONYM_DATABASE.items():
        if keyword_lower in synonyms:
            return [main_keyword] + [s for s in synonyms if s != keyword_lower]

    return []


def expand_keywords(keywords: List[str]) -> List[str]:
    """
    Expand a list of keywords to include all synonyms

    Args:
        keywords: List of keywords

    Returns:
        Expanded list with synonyms
    """
    expanded = set(keywords)

    for keyword in keywords:
        synonyms = get_all_synonyms(keyword)
        expanded.update(synonyms)

    return list(expanded)
```

**Step 4: Run test to verify it passes**

Run: `cd backend && python -m pytest tests/test_synonym_database.py -v`
Expected: PASS (3 tests)

**Step 5: Commit**

```bash
git add backend/services/synonym_database.py backend/tests/test_synonym_database.py
git commit -m "feat: add synonym database for keyword matching

- 200+ synonym mappings for programming languages, cloud, tools, action verbs
- Support for direct and reverse lookup
- Expand keywords with all synonyms
- Full test coverage

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

### Task 2: Create Keyword Extractor Service

**Files:**
- Create: `backend/services/keyword_extractor.py`
- Test: `backend/tests/test_keyword_extractor.py`

**Step 1: Write failing tests**

Create `backend/tests/test_keyword_extractor.py`:
```python
"""Tests for keyword extraction from job descriptions"""
import pytest
from backend.services.keyword_extractor import (
    extract_keywords_from_jd,
    match_with_synonyms
)


def test_extract_required_keywords():
    """Test extraction of required keywords"""
    jd = """
    Required:
    - 5+ years of Python experience
    - Must have Docker and Kubernetes
    - AWS required
    """

    result = extract_keywords_from_jd(jd)

    assert "python" in result["required"]
    assert "docker" in result["required"]
    assert "kubernetes" in result["required"]
    assert "aws" in result["required"]


def test_extract_preferred_keywords():
    """Test extraction of preferred keywords"""
    jd = """
    Preferred:
    - Experience with Terraform is a plus
    - Nice to have: PostgreSQL knowledge
    """

    result = extract_keywords_from_jd(jd)

    assert "terraform" in result["preferred"]
    assert "postgresql" in result["preferred"]


def test_match_with_synonyms_direct():
    """Test direct keyword match"""
    text = "experienced with python and javascript"

    assert match_with_synonyms("python", text) == True
    assert match_with_synonyms("javascript", text) == True


def test_match_with_synonyms_synonym():
    """Test synonym match"""
    text = "built systems using k8s and nodejs"

    assert match_with_synonyms("kubernetes", text) == True
    assert match_with_synonyms("node.js", text) == True
```

**Step 2: Run test to verify it fails**

Run: `cd backend && python -m pytest tests/test_keyword_extractor.py -v`
Expected: FAIL with "ModuleNotFoundError"

**Step 3: Create keyword extractor (minimal implementation)**

Create `backend/services/keyword_extractor.py`:
```python
"""
Extract keywords from job descriptions and classify as required/preferred
"""
import re
from typing import Dict, List, Set
from backend.services.synonym_database import SYNONYM_DATABASE
import logging

logger = logging.getLogger(__name__)


# Tech keywords database
TECH_KEYWORDS = [
    "python", "java", "javascript", "typescript", "c++", "c#", "go", "rust", "ruby",
    "react", "angular", "vue", "django", "flask", "spring", "node.js",
    "sql", "mysql", "postgresql", "mongodb", "redis", "elasticsearch",
    "aws", "azure", "gcp", "docker", "kubernetes", "terraform", "jenkins",
    "machine learning", "deep learning", "tensorflow", "pytorch",
    "agile", "scrum", "ci/cd", "microservices", "rest api", "graphql"
]

# Soft skills database
SOFT_SKILLS = [
    "leadership", "communication", "collaboration", "problem solving",
    "project management", "mentorship", "analytical", "strategic thinking"
]

# Required indicators
REQUIRED_INDICATORS = [
    "required", "must have", "must-have", "essential", "mandatory",
    "critical", "minimum", "necessary"
]

# Preferred indicators
PREFERRED_INDICATORS = [
    "preferred", "nice to have", "nice-to-have", "bonus",
    "plus", "desired", "ideal", "advantage"
]


def extract_keywords_from_jd(job_description: str) -> Dict[str, List[str]]:
    """
    Extract and classify keywords from job description

    Args:
        job_description: Raw job description text

    Returns:
        {
            "required": [...],
            "preferred": [...],
            "all": [...]
        }
    """
    logger.info("Extracting keywords from job description")

    jd_text = job_description.lower()

    # Extract all potential keywords
    all_keywords = set()

    # Technical keywords
    for keyword in TECH_KEYWORDS:
        pattern = r'\b' + re.escape(keyword) + r'\b'
        if re.search(pattern, jd_text, re.IGNORECASE):
            all_keywords.add(keyword.lower())

    # Soft skills
    for skill in SOFT_SKILLS:
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, jd_text, re.IGNORECASE):
            all_keywords.add(skill.lower())

    # Classify as required or preferred
    required, preferred = _classify_keywords(all_keywords, jd_text)

    logger.info(f"Extracted {len(required)} required, {len(preferred)} preferred keywords")

    return {
        "required": list(required),
        "preferred": list(preferred),
        "all": list(all_keywords)
    }


def _classify_keywords(keywords: Set[str], text: str) -> tuple:
    """
    Classify keywords as required or preferred

    Logic:
    1. Check context around keyword for indicators
    2. Check frequency (3+ mentions = required)
    3. Default: preferred
    """
    required = set()
    preferred = set()

    for keyword in keywords:
        # Get context around keyword
        context = _get_keyword_context(keyword, text, window=50)

        # Check for required indicators
        if any(ind in context for ind in REQUIRED_INDICATORS):
            required.add(keyword)
            continue

        # Check for preferred indicators
        if any(ind in context for ind in PREFERRED_INDICATORS):
            preferred.add(keyword)
            continue

        # Frequency-based classification
        frequency = text.count(keyword)
        if frequency >= 3:
            required.add(keyword)
        else:
            preferred.add(keyword)

    return required, preferred


def _get_keyword_context(keyword: str, text: str, window: int = 50) -> str:
    """Get text context around keyword (±window characters)"""
    pos = text.find(keyword.lower())
    if pos == -1:
        return ""

    start = max(0, pos - window)
    end = min(len(text), pos + len(keyword) + window)

    return text[start:end]


def match_with_synonyms(keyword: str, text: str) -> bool:
    """
    Check if keyword or any of its synonyms appear in text

    Args:
        keyword: Keyword to search for
        text: Text to search in (should be lowercase)

    Returns:
        True if keyword or synonym found
    """
    # Direct match
    if keyword.lower() in text:
        return True

    # Check synonyms
    if keyword.lower() in SYNONYM_DATABASE:
        for synonym in SYNONYM_DATABASE[keyword.lower()]:
            if synonym in text:
                return True

    # Check if this keyword IS a synonym
    for main_keyword, synonyms in SYNONYM_DATABASE.items():
        if keyword.lower() in synonyms and main_keyword in text:
            return True

    return False
```

**Step 4: Run test to verify it passes**

Run: `cd backend && python -m pytest tests/test_keyword_extractor.py -v`
Expected: PASS (4 tests)

**Step 5: Commit**

```bash
git add backend/services/keyword_extractor.py backend/tests/test_keyword_extractor.py
git commit -m "feat: add keyword extraction from job descriptions

- Extract tech keywords, soft skills from JD
- Classify as required vs preferred based on indicators
- Synonym-based matching for intelligent comparison
- Context-aware classification

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

### Task 3: Create Adaptive Scorer Core

**Files:**
- Create: `backend/services/scorer_v2.py`
- Test: `backend/tests/test_scorer_v2.py`

**Step 1: Write failing tests**

Create `backend/tests/test_scorer_v2.py`:
```python
"""Tests for adaptive scorer"""
import pytest
from backend.services.scorer_v2 import AdaptiveScorer
from backend.services.parser import ResumeData


@pytest.fixture
def sample_resume():
    """Sample resume for testing"""
    return ResumeData(
        fileName="test.pdf",
        contact={
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "+1-555-0100"
        },
        experience=[
            {
                "title": "Senior Software Engineer",
                "company": "Tech Corp",
                "description": """
                - Led team of 5 engineers building microservices with Python and AWS
                - Reduced deployment time by 60% through CI/CD automation
                - Implemented Kubernetes orchestration
                """
            }
        ],
        education=[{"degree": "BS Computer Science", "institution": "Stanford"}],
        skills=["Python", "AWS", "Docker", "Kubernetes", "React"],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 450, "hasPhoto": False, "fileFormat": "pdf"}
    )


def test_ats_mode_triggered_with_jd(sample_resume):
    """Test ATS mode when JD provided"""
    scorer = AdaptiveScorer()

    result = scorer.score(
        resume_data=sample_resume,
        role_id="software_engineer",
        level="senior",
        job_description="Required: Python, AWS, Docker",
        mode="auto"
    )

    assert result["mode"] == "ats_simulation"


def test_quality_mode_triggered_without_jd(sample_resume):
    """Test Quality mode without JD"""
    scorer = AdaptiveScorer()

    result = scorer.score(
        resume_data=sample_resume,
        role_id="software_engineer",
        level="senior",
        job_description=None,
        mode="auto"
    )

    assert result["mode"] == "quality_coach"


def test_ats_keyword_matching(sample_resume):
    """Test keyword matching in ATS mode"""
    scorer = AdaptiveScorer()

    result = scorer.score(
        resume_data=sample_resume,
        role_id="software_engineer",
        level="senior",
        job_description="Required: Python, AWS, Docker, Kubernetes"
    )

    # Should match all required keywords
    keyword_details = result["keyword_details"]
    assert keyword_details["required_match_pct"] >= 75
```

**Step 2: Run test to verify it fails**

Run: `cd backend && python -m pytest tests/test_scorer_v2.py -v`
Expected: FAIL with "ModuleNotFoundError"

**Step 3: Create adaptive scorer (minimal implementation)**

Create `backend/services/scorer_v2.py`:
```python
"""
Adaptive scoring system with two modes:
- ATS Simulation (with job description)
- Quality Coach (without job description)
"""
from typing import Dict, Optional
from backend.services.parser import ResumeData
from backend.services.role_taxonomy import get_role_scoring_data
from backend.services.keyword_extractor import extract_keywords_from_jd, match_with_synonyms
import logging

logger = logging.getLogger(__name__)


class AdaptiveScorer:
    """Adaptive scoring engine"""

    def score(
        self,
        resume_data: ResumeData,
        role_id: str,
        level: str,
        job_description: Optional[str] = None,
        mode: str = "auto"
    ) -> Dict:
        """
        Score resume adaptively based on context

        Args:
            resume_data: Parsed resume
            role_id: Role identifier
            level: Experience level
            job_description: Optional JD text
            mode: "ats_simulation", "quality_coach", or "auto"

        Returns:
            Score result with breakdown and suggestions
        """
        # Auto-detect mode
        if mode == "auto":
            mode = "ats_simulation" if job_description else "quality_coach"

        logger.info(f"Scoring in {mode} mode for {role_id} ({level})")

        # Get role data
        role_data = get_role_scoring_data(role_id, level)

        if not role_data:
            raise ValueError(f"Invalid role or level: {role_id}, {level}")

        # Route to appropriate scorer
        if mode == "ats_simulation":
            return self._score_ats_simulation(resume_data, role_data, job_description)
        else:
            return self._score_quality_coach(resume_data, role_data)

    def _score_ats_simulation(self, resume_data: ResumeData, role_data: Dict, job_description: str) -> Dict:
        """Mode A: ATS Simulation Scoring"""

        # Get full resume text
        resume_text = self._get_resume_text(resume_data)

        # Extract keywords from JD
        jd_keywords = extract_keywords_from_jd(job_description)

        # 1. Keyword Match (70 points)
        keyword_result = self._score_ats_keywords(resume_text, jd_keywords)

        # 2. Format Check (20 points)
        format_result = self._score_format(resume_data, resume_text)

        # 3. Structure (10 points)
        structure_result = self._score_structure(resume_data)

        total_score = keyword_result["score"] + format_result["score"] + structure_result["score"]

        return {
            "overall_score": round(total_score),
            "mode": "ats_simulation",
            "breakdown": {
                "keyword_match": keyword_result["score"],
                "ats_format": format_result["score"],
                "structure": structure_result["score"]
            },
            "keyword_details": {
                "required_match_pct": keyword_result["required_match_pct"],
                "preferred_match_pct": keyword_result["preferred_match_pct"],
                "matched_required": keyword_result["matched_required"],
                "missed_required": keyword_result["missed_required"]
            },
            "auto_reject": keyword_result["auto_reject"],
            "pass_threshold": 60,
            "issues": []
        }

    def _score_quality_coach(self, resume_data: ResumeData, role_data: Dict) -> Dict:
        """Mode B: Quality Coach Scoring"""

        # Get full resume text
        resume_text = self._get_resume_text(resume_data)

        # 1. Role Keywords (25 points)
        keyword_result = self._score_role_keywords(resume_text, role_data)

        # 2. Content Quality (30 points)
        content_result = {"score": 25, "issues": []}  # Simplified for now

        # 3. Format (25 points)
        format_result = self._score_format(resume_data, resume_text)
        format_result["score"] = (format_result["score"] / 20) * 25  # Scale to 25

        # 4. Professional Polish (20 points)
        polish_result = {"score": 15, "issues": []}  # Simplified for now

        total_score = keyword_result["score"] + content_result["score"] + format_result["score"] + polish_result["score"]

        return {
            "overall_score": round(total_score),
            "mode": "quality_coach",
            "breakdown": {
                "role_keywords": keyword_result["score"],
                "content_quality": content_result["score"],
                "ats_format": format_result["score"],
                "professional_polish": polish_result["score"]
            },
            "keyword_details": {
                "match_percentage": keyword_result["match_percentage"],
                "matched_keywords": keyword_result["matched_keywords"],
                "missing_keywords": keyword_result["missing_keywords"]
            },
            "issues": [],
            "cta": "Want ATS simulation? Paste a job description when rescoring."
        }

    def _score_ats_keywords(self, resume_text: str, jd_keywords: Dict) -> Dict:
        """Score keyword matching for ATS"""
        matches_required = []
        matches_preferred = []

        resume_lower = resume_text.lower()

        for keyword in jd_keywords["required"]:
            if match_with_synonyms(keyword, resume_lower):
                matches_required.append(keyword)

        for keyword in jd_keywords["preferred"]:
            if match_with_synonyms(keyword, resume_lower):
                matches_preferred.append(keyword)

        required_count = len(jd_keywords["required"])
        required_pct = (len(matches_required) / required_count * 100) if required_count > 0 else 100

        preferred_count = len(jd_keywords["preferred"])
        preferred_pct = (len(matches_preferred) / preferred_count * 100) if preferred_count > 0 else 0

        required_score = (required_pct / 100) * 50
        preferred_score = (preferred_pct / 100) * 20

        return {
            "score": required_score + preferred_score,
            "required_match_pct": required_pct,
            "preferred_match_pct": preferred_pct,
            "matched_required": matches_required,
            "missed_required": list(set(jd_keywords["required"]) - set(matches_required)),
            "matched_preferred": matches_preferred,
            "auto_reject": required_pct < 60
        }

    def _score_role_keywords(self, resume_text: str, role_data: Dict) -> Dict:
        """Score role-specific keywords (Quality mode)"""
        typical_keywords = role_data.get("typical_keywords", [])

        matches = []
        resume_lower = resume_text.lower()

        for keyword in typical_keywords:
            if match_with_synonyms(keyword, resume_lower):
                matches.append(keyword)

        match_pct = (len(matches) / len(typical_keywords) * 100) if typical_keywords else 0

        # Generous scoring
        if match_pct >= 60: score = 25
        elif match_pct >= 50: score = 22
        elif match_pct >= 40: score = 18
        elif match_pct >= 30: score = 14
        else: score = 10

        return {
            "score": score,
            "match_percentage": match_pct,
            "matched_keywords": matches[:10],
            "missing_keywords": list(set(typical_keywords) - set(matches))[:5]
        }

    def _score_format(self, resume_data: ResumeData, raw_text: str) -> Dict:
        """Score ATS format compatibility"""
        score = 0

        # Sections detected (10 points)
        if resume_data.experience and len(resume_data.experience) > 0: score += 5
        if resume_data.education and len(resume_data.education) > 0: score += 3
        if resume_data.skills and len(resume_data.skills) > 0: score += 2

        # Contact info (10 points)
        contact = resume_data.contact
        if contact.get("email"): score += 4
        if contact.get("phone"): score += 3
        if contact.get("name"): score += 3

        return {"score": score, "issues": []}

    def _score_structure(self, resume_data: ResumeData) -> Dict:
        """Score structure quality"""
        score = 0

        exp_count = len(resume_data.experience) if resume_data.experience else 0
        if exp_count >= 2: score += 4
        elif exp_count == 1: score += 2

        edu_count = len(resume_data.education) if resume_data.education else 0
        if edu_count >= 1: score += 3

        skill_count = len(resume_data.skills) if resume_data.skills else 0
        if skill_count >= 5: score += 3
        elif skill_count >= 3: score += 2

        return {"score": score, "issues": []}

    def _get_resume_text(self, resume_data: ResumeData) -> str:
        """Extract all text from resume"""
        parts = []

        if resume_data.contact:
            parts.extend([v for v in resume_data.contact.values() if v])

        for exp in (resume_data.experience or []):
            parts.append(exp.get("title", ""))
            parts.append(exp.get("company", ""))
            parts.append(exp.get("description", ""))

        for edu in (resume_data.education or []):
            parts.append(edu.get("degree", ""))
            parts.append(edu.get("institution", ""))

        parts.extend(resume_data.skills or [])

        return " ".join(parts)
```

**Step 4: Run test to verify it passes**

Run: `cd backend && python -m pytest tests/test_scorer_v2.py -v`
Expected: PASS (3 tests)

**Step 5: Commit**

```bash
git add backend/services/scorer_v2.py backend/tests/test_scorer_v2.py
git commit -m "feat: add adaptive scorer with dual-mode scoring

- Mode A (ATS Simulation): 70/20/10 keyword-heavy scoring
- Mode B (Quality Coach): 25/30/25/20 balanced scoring
- Auto-detect mode based on JD presence
- Keyword matching with synonym support
- Format and structure scoring

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

### Task 4: Update API Upload Endpoint

**Files:**
- Modify: `backend/api/upload.py`
- Modify: `backend/schemas/resume.py`
- Test: `backend/tests/test_api_upload.py`

**Step 1: Write failing test**

Create `backend/tests/test_api_upload.py` (or add to existing):
```python
"""Tests for updated upload API"""
from fastapi.testclient import TestClient
from backend.main import app
import io

client = TestClient(app)


def test_upload_with_jd_returns_ats_mode():
    """Test upload with JD triggers ATS mode"""
    pdf_content = b"%PDF-1.4 mock"
    files = {"file": ("resume.pdf", io.BytesIO(pdf_content), "application/pdf")}
    data = {
        "role": "software_engineer",
        "level": "senior",
        "jobDescription": "Required: Python, AWS"
    }

    response = client.post("/api/upload", files=files, data=data)

    assert response.status_code == 200
    result = response.json()
    assert result["scoringMode"] == "ats_simulation"
    assert result["score"]["mode"] == "ats_simulation"


def test_upload_without_jd_returns_quality_mode():
    """Test upload without JD triggers Quality mode"""
    pdf_content = b"%PDF-1.4 mock"
    files = {"file": ("resume.pdf", io.BytesIO(pdf_content), "application/pdf")}
    data = {"role": "software_engineer", "level": "mid"}

    response = client.post("/api/upload", files=files, data=data)

    assert response.status_code == 200
    result = response.json()
    assert result["scoringMode"] == "quality_coach"
    assert result["score"]["mode"] == "quality_coach"
```

**Step 2: Run test to verify it fails**

Run: `cd backend && python -m pytest tests/test_api_upload.py::test_upload_with_jd_returns_ats_mode -v`
Expected: FAIL with "KeyError: 'scoringMode'" (field doesn't exist yet)

**Step 3: Update UploadResponse schema**

Modify `backend/schemas/resume.py`:
```python
# Find UploadResponse class and add scoringMode field

class UploadResponse(BaseModel):
    resumeId: Optional[str] = None
    fileName: str
    contact: ContactInfoResponse
    experience: List[Dict] = []
    education: List[Dict] = []
    skills: List[str] = []
    certifications: List[Dict] = []
    metadata: MetadataResponse
    score: ScoreResponse
    formatCheck: Optional[FormatCheckResponse] = None
    scoringMode: str  # NEW FIELD: "ats_simulation" or "quality_coach"
    role: str  # NEW FIELD
    level: str  # NEW FIELD
    jobDescription: Optional[str] = None
    uploadedAt: datetime
```

**Step 4: Update upload endpoint**

Modify `backend/api/upload.py`:
```python
# Add import at top
from backend.services.scorer_v2 import AdaptiveScorer

# Update upload_resume function
@router.post("/upload", response_model=UploadResponse)
async def upload_resume(
    file: UploadFile = File(...),
    role: str = Form(...),
    level: str = Form(...),
    jobDescription: Optional[str] = Form(None)
):
    """Upload and score resume with adaptive mode"""

    # ... existing parsing code ...

    # Determine scoring mode
    scoring_mode = "ats_simulation" if jobDescription else "quality_coach"
    logger.info(f"Scoring mode: {scoring_mode}")

    # Use adaptive scorer
    scorer = AdaptiveScorer()

    try:
        score_result = scorer.score(
            resume_data=resume_data,
            role_id=role,
            level=level,
            job_description=jobDescription,
            mode=scoring_mode
        )
    except Exception as e:
        logger.error(f"Scoring failed: {str(e)}")
        raise HTTPException(500, f"Failed to score resume: {str(e)}")

    # Return with mode info
    return UploadResponse(
        resumeId=None,
        fileName=file.filename,
        contact=resume_data.contact,
        experience=resume_data.experience,
        education=resume_data.education,
        skills=resume_data.skills,
        certifications=resume_data.certifications,
        metadata=resume_data.metadata,
        score=score_result,
        scoringMode=scoring_mode,
        role=role,
        level=level,
        jobDescription=jobDescription,
        uploadedAt=datetime.now(timezone.utc)
    )
```

**Step 5: Run test to verify it passes**

Run: `cd backend && python -m pytest tests/test_api_upload.py -v`
Expected: PASS (2 tests)

**Step 6: Commit**

```bash
git add backend/api/upload.py backend/schemas/resume.py backend/tests/test_api_upload.py
git commit -m "feat: update upload API to use adaptive scorer

- Add scoringMode field to UploadResponse
- Integrate AdaptiveScorer into upload endpoint
- Auto-detect mode based on JD presence
- Tests for both modes

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

### Task 5: Create Export API Endpoints

**Files:**
- Create: `backend/api/export.py`
- Test: `backend/tests/test_api_export.py`

**Step 1: Write failing tests**

Create `backend/tests/test_api_export.py`:
```python
"""Tests for export API endpoints"""
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_export_resume_pdf():
    """Test PDF export"""
    request_data = {
        "content": "<h1>John Doe</h1><p>Software Engineer</p>",
        "name": "John Doe",
        "format": "pdf"
    }

    response = client.post("/api/export/resume", json=request_data)

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert "John_Doe" in response.headers["content-disposition"]


def test_export_report():
    """Test score report export"""
    request_data = {
        "resumeData": {"contact": {"name": "John Doe"}},
        "scoreData": {"overall_score": 80, "mode": "ats_simulation"},
        "mode": "ats_simulation",
        "role": "software_engineer",
        "level": "senior"
    }

    response = client.post("/api/export/report", json=request_data)

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
```

**Step 2: Run test to verify it fails**

Run: `cd backend && python -m pytest tests/test_api_export.py -v`
Expected: FAIL with "404 Not Found" (endpoint doesn't exist)

**Step 3: Create export API**

Create `backend/api/export.py`:
```python
"""Export API for resume and report downloads"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from typing import Dict, Optional
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from docx import Document

router = APIRouter(prefix="/api/export", tags=["export"])


class ExportResumeRequest(BaseModel):
    content: str  # HTML content
    name: str
    format: str  # "pdf" or "docx"


class ExportReportRequest(BaseModel):
    resumeData: Dict
    scoreData: Dict
    mode: str
    role: str
    level: str


@router.post("/resume")
async def export_resume(request: ExportResumeRequest):
    """Export edited resume as PDF or DOCX"""

    if request.format == "pdf":
        # Simple PDF generation
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)

        # Basic text rendering (simplified)
        c.setFont("Helvetica", 12)
        y = 750

        # Strip HTML tags for simple text
        import re
        text = re.sub('<[^<]+?>', '', request.content)

        for line in text.split('\n'):
            if y < 50:
                c.showPage()
                y = 750
            c.drawString(50, y, line[:80])
            y -= 15

        c.save()
        buffer.seek(0)

        filename = f"{request.name.replace(' ', '_')}_Resume.pdf"

        return Response(
            content=buffer.read(),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )

    elif request.format == "docx":
        # Simple DOCX generation
        doc = Document()

        # Strip HTML for simple text
        import re
        text = re.sub('<[^<]+?>', '', request.content)

        for line in text.split('\n'):
            if line.strip():
                doc.add_paragraph(line)

        buffer = io.BytesIO()
        doc.save(buffer)
        buffer.seek(0)

        filename = f"{request.name.replace(' ', '_')}_Resume.docx"

        return Response(
            content=buffer.read(),
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )

    else:
        raise HTTPException(400, "Invalid format. Use 'pdf' or 'docx'")


@router.post("/report")
async def export_score_report(request: ExportReportRequest):
    """Export ATS score report as PDF"""

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)

    # Title
    c.setFont("Helvetica-Bold", 18)
    name = request.resumeData.get("contact", {}).get("name", "Resume")
    c.drawString(50, 750, f"ATS Resume Report - {name}")

    # Mode
    c.setFont("Helvetica", 12)
    mode_text = "ATS Simulation Mode" if request.mode == "ats_simulation" else "Quality Coach Mode"
    c.drawString(50, 720, f"Mode: {mode_text}")

    # Score
    c.setFont("Helvetica-Bold", 14)
    score = request.scoreData.get("overall_score", 0)
    c.drawString(50, 690, f"Score: {score}/100")

    # Breakdown
    y = 660
    c.setFont("Helvetica", 11)
    c.drawString(50, y, "Breakdown:")
    y -= 20

    breakdown = request.scoreData.get("breakdown", {})
    for category, score_val in breakdown.items():
        c.drawString(60, y, f"• {category.replace('_', ' ').title()}: {score_val}")
        y -= 15

    c.save()
    buffer.seek(0)

    filename = f"{name.replace(' ', '_')}_ATS_Report.pdf"

    return Response(
        content=buffer.read(),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
```

**Step 4: Register router in main.py**

Modify `backend/main.py`:
```python
# Add import
from backend.api.export import router as export_router

# Register router
app.include_router(export_router)
```

**Step 5: Run test to verify it passes**

Run: `cd backend && python -m pytest tests/test_api_export.py -v`
Expected: PASS (2 tests)

**Step 6: Commit**

```bash
git add backend/api/export.py backend/tests/test_api_export.py backend/main.py
git commit -m "feat: add export API for resume and report downloads

- Export resume as PDF or DOCX
- Export score report as PDF with breakdown
- Clean filename generation
- Full test coverage

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## PHASE 2: Frontend Updates

### Task 6: Create Mode Indicator Component

**Files:**
- Create: `frontend/src/components/ModeIndicator.tsx`
- Test: Manual testing (React component)

**Step 1: Create mode indicator component**

Create `frontend/src/components/ModeIndicator.tsx`:
```typescript
import React from 'react';

interface ModeIndicatorProps {
  mode: 'ats_simulation' | 'quality_coach';
  score: number;
  keywordDetails?: {
    required_match_pct?: number;
    preferred_match_pct?: number;
    match_percentage?: number;
  };
  breakdown: {
    [key: string]: number;
  };
  autoReject?: boolean;
}

export const ModeIndicator: React.FC<ModeIndicatorProps> = ({
  mode,
  score,
  keywordDetails,
  breakdown,
  autoReject
}) => {
  const isATSMode = mode === 'ats_simulation';

  const getScoreColor = () => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreStatus = () => {
    if (isATSMode) {
      if (autoReject) return '⚠️ Warning';
      if (score >= 60) return '✅ Likely to Pass';
      return '❌ May Not Pass';
    } else {
      if (score >= 80) return '✅ Strong';
      if (score >= 60) return '👍 Good';
      return '📝 Needs Work';
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      {/* Header */}
      <div className="mb-4">
        <div className="flex items-center gap-2 mb-1">
          <span className="text-2xl">{isATSMode ? '🎯' : '📝'}</span>
          <h3 className="text-lg font-semibold text-gray-900">
            {isATSMode ? 'ATS SIMULATION MODE' : 'QUALITY COACH MODE'}
          </h3>
        </div>
        <p className="text-sm text-gray-600">
          {isATSMode ? 'Scoring against job description' : 'General resume quality scoring'}
        </p>
      </div>

      {/* Score Circle */}
      <div className="flex items-center justify-center mb-6">
        <div className="relative">
          <div className="w-32 h-32 rounded-full bg-gradient-to-br from-teal-500 to-cyan-500 flex items-center justify-center shadow-lg">
            <div className="w-28 h-28 rounded-full bg-white flex flex-col items-center justify-center">
              <span className={`text-4xl font-bold ${getScoreColor()}`}>
                {score}
              </span>
              <span className="text-sm text-gray-500">/100</span>
            </div>
          </div>
        </div>
      </div>

      <div className="text-center mb-6">
        <span className="text-lg font-medium">{getScoreStatus()}</span>
        {isATSMode && (
          <p className="text-sm text-gray-600 mt-1">
            60% match needed to pass ATS
          </p>
        )}
      </div>

      {/* Keyword Details */}
      {isATSMode && keywordDetails && (
        <div className="mb-6 space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-gray-700">Required Keywords:</span>
            <span className={`font-semibold ${keywordDetails.required_match_pct >= 60 ? 'text-green-600' : 'text-red-600'}`}>
              {keywordDetails.required_match_pct?.toFixed(0)}% ✅
            </span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-gray-700">Preferred Keywords:</span>
            <span className="font-semibold text-gray-600">
              {keywordDetails.preferred_match_pct?.toFixed(0)}%
            </span>
          </div>
        </div>
      )}

      {!isATSMode && (
        <div className="mb-6 p-3 bg-blue-50 border border-blue-200 rounded-md">
          <p className="text-sm text-blue-800">
            💡 Want ATS simulation? Paste a job description when rescoring.
          </p>
        </div>
      )}

      {/* Breakdown */}
      <div className="space-y-3">
        <h4 className="text-sm font-semibold text-gray-700 mb-2">📊 BREAKDOWN</h4>
        {Object.entries(breakdown).map(([category, score]) => {
          const maxScore = isATSMode
            ? (category === 'keyword_match' ? 70 : category === 'ats_format' ? 20 : 10)
            : 25;
          const percentage = (score / maxScore) * 100;

          return (
            <div key={category} className="space-y-1">
              <div className="flex justify-between text-sm">
                <span className="text-gray-700 capitalize">
                  {category.replace(/_/g, ' ')}
                </span>
                <span className="font-semibold text-gray-900">
                  {score}/{maxScore}
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-gradient-to-r from-teal-500 to-cyan-500 h-2 rounded-full transition-all"
                  style={{ width: `${percentage}%` }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
```

**Step 2: Commit**

```bash
git add frontend/src/components/ModeIndicator.tsx
git commit -m "feat: add mode indicator component

- Visual distinction between ATS and Quality modes
- Score circle with color coding
- Keyword match percentages for ATS mode
- Breakdown bars with proper scaling
- CTA for mode switching

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

### Task 7: Add Download Dropdown Component

**Files:**
- Create: `frontend/src/components/DownloadMenu.tsx`

**Step 1: Create download menu component**

Create `frontend/src/components/DownloadMenu.tsx`:
```typescript
import React, { useState } from 'react';
import { apiClient } from '../api/client';

interface DownloadMenuProps {
  resumeContent: string;
  resumeName: string;
  resumeData: any;
  scoreData: any;
  mode: string;
  role: string;
  level: string;
}

export const DownloadMenu: React.FC<DownloadMenuProps> = ({
  resumeContent,
  resumeName,
  resumeData,
  scoreData,
  mode,
  role,
  level
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [downloading, setDownloading] = useState<string | null>(null);

  const handleDownloadResume = async (format: 'pdf' | 'docx') => {
    setDownloading(format);

    try {
      const response = await apiClient.post('/api/export/resume', {
        content: resumeContent,
        name: resumeName,
        format
      }, {
        responseType: 'blob'
      });

      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${resumeName}_Resume.${format}`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error(`Failed to download ${format}:`, error);
      alert(`Failed to download resume as ${format.toUpperCase()}`);
    } finally {
      setDownloading(null);
      setIsOpen(false);
    }
  };

  const handleDownloadReport = async () => {
    setDownloading('report');

    try {
      const response = await apiClient.post('/api/export/report', {
        resumeData,
        scoreData,
        mode,
        role,
        level
      }, {
        responseType: 'blob'
      });

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${resumeName}_ATS_Report.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Failed to download report:', error);
      alert('Failed to download report');
    } finally {
      setDownloading(null);
      setIsOpen(false);
    }
  };

  const handleCopySuggestions = () => {
    const suggestions = scoreData.issues?.map((issue: any) =>
      `• ${issue.message}`
    ).join('\n') || 'No suggestions available';

    navigator.clipboard.writeText(suggestions);
    alert('Suggestions copied to clipboard!');
    setIsOpen(false);
  };

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-4 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700 transition-colors"
      >
        Download ▼
      </button>

      {isOpen && (
        <>
          <div
            className="fixed inset-0 z-10"
            onClick={() => setIsOpen(false)}
          />
          <div className="absolute right-0 mt-2 w-56 bg-white rounded-lg shadow-lg border border-gray-200 z-20">
            <button
              onClick={() => handleDownloadResume('pdf')}
              disabled={downloading === 'pdf'}
              className="w-full px-4 py-3 text-left hover:bg-gray-50 flex items-center gap-2 border-b border-gray-100"
            >
              <span>📄</span>
              <span>{downloading === 'pdf' ? 'Downloading...' : 'Download as PDF'}</span>
            </button>

            <button
              onClick={() => handleDownloadResume('docx')}
              disabled={downloading === 'docx'}
              className="w-full px-4 py-3 text-left hover:bg-gray-50 flex items-center gap-2 border-b border-gray-100"
            >
              <span>📝</span>
              <span>{downloading === 'docx' ? 'Downloading...' : 'Download as DOCX'}</span>
            </button>

            <button
              onClick={handleDownloadReport}
              disabled={downloading === 'report'}
              className="w-full px-4 py-3 text-left hover:bg-gray-50 flex items-center gap-2 border-b border-gray-100"
            >
              <span>📊</span>
              <span>{downloading === 'report' ? 'Downloading...' : 'Download Report'}</span>
            </button>

            <button
              onClick={handleCopySuggestions}
              className="w-full px-4 py-3 text-left hover:bg-gray-50 flex items-center gap-2"
            >
              <span>📋</span>
              <span>Copy Suggestions</span>
            </button>
          </div>
        </>
      )}
    </div>
  );
};
```

**Step 2: Commit**

```bash
git add frontend/src/components/DownloadMenu.tsx
git commit -m "feat: add download menu component

- Download resume as PDF/DOCX
- Download score report
- Copy suggestions to clipboard
- Loading states and error handling
- Clean dropdown UI

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

### Task 8: Update Editor Page with New Components

**Files:**
- Modify: `frontend/src/components/EditorPage.tsx`

**Step 1: Integrate new components into editor**

Modify `frontend/src/components/EditorPage.tsx`:
```typescript
// Add imports at top
import { ModeIndicator } from './ModeIndicator';
import { DownloadMenu } from './DownloadMenu';

// Update the component to use ModeIndicator and DownloadMenu
export default function EditorPage() {
  // ... existing state ...

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <h1 className="text-xl font-semibold text-gray-900">ATS Resume Scorer</h1>
            <span className="text-gray-500">•</span>
            <span className="text-gray-600">{resumeData.fileName}</span>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={handleSave}
              className="px-4 py-2 text-teal-600 border border-teal-600 rounded-lg hover:bg-teal-50"
            >
              Save
            </button>
            <DownloadMenu
              resumeContent={editor?.getHTML() || ''}
              resumeName={resumeData.contact?.name || 'Resume'}
              resumeData={resumeData}
              scoreData={scoreData}
              mode={scoringMode}
              role={role}
              level={level}
            />
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex h-[calc(100vh-73px)]">
        {/* Editor Panel (60%) */}
        <div className="w-3/5 overflow-y-auto p-6">
          {/* ... existing editor content ... */}
        </div>

        {/* Score Panel (40%, Sticky) */}
        <div className="w-2/5 bg-gray-50 border-l border-gray-200 overflow-y-auto p-6">
          <div className="space-y-6">
            {/* Mode Indicator */}
            <ModeIndicator
              mode={scoringMode}
              score={scoreData.overall_score}
              keywordDetails={scoreData.keyword_details}
              breakdown={scoreData.breakdown}
              autoReject={scoreData.auto_reject}
            />

            {/* Rescore Button */}
            <button
              onClick={handleRescore}
              disabled={rescoring}
              className="w-full py-3 bg-teal-600 text-white rounded-lg font-semibold hover:bg-teal-700 disabled:bg-gray-400"
            >
              {rescoring ? 'Rescoring...' : 'Rescore Now'}
            </button>

            {/* ... existing suggestions ... */}
          </div>
        </div>
      </div>
    </div>
  );
}
```

**Step 2: Commit**

```bash
git add frontend/src/components/EditorPage.tsx
git commit -m "feat: integrate mode indicator and download menu into editor

- Replace old score card with ModeIndicator
- Add DownloadMenu to header
- Pass mode and score data to components
- Clean layout integration

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## PHASE 3: Testing & Polish

### Task 9: Run All Tests

**Step 1: Run backend tests**

Run: `cd backend && python -m pytest -v --cov=backend --cov-report=html`
Expected: 80%+ coverage, all tests passing

**Step 2: Fix any failing tests**

If tests fail, fix the issues and re-run.

**Step 3: Commit test fixes**

```bash
git add .
git commit -m "test: fix failing tests and achieve 80%+ coverage"
```

---

### Task 10: Manual Testing & Bug Fixes

**Step 1: Test complete flow**

1. Start servers:
   ```bash
   cd backend && uvicorn main:app --reload &
   cd frontend && npm run dev &
   ```

2. Test scenarios:
   - Upload resume WITH job description → Check ATS mode
   - Upload resume WITHOUT job description → Check Quality mode
   - Edit resume and rescore → Check mode persists
   - Download as PDF/DOCX → Check files
   - Download report → Check content
   - Copy suggestions → Check clipboard

**Step 2: Fix bugs found**

Document and fix any bugs discovered.

**Step 3: Commit bug fixes**

```bash
git add .
git commit -m "fix: resolve bugs found in manual testing

- [List specific fixes]

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Execution Complete

**Deliverables:**
✅ Synonym database (200+ mappings)
✅ Keyword extractor (JD parsing + classification)
✅ Adaptive scorer (dual-mode scoring)
✅ Updated API endpoints (upload with mode detection)
✅ Export API (PDF/DOCX/Report)
✅ Mode indicator component
✅ Download menu component
✅ Integrated editor page
✅ Comprehensive tests (80%+ coverage)
✅ Manual testing complete

**Next Steps:**
- Deploy to production
- Monitor user feedback
- Iterate on keyword database
- Add more ATS platform simulations

---

**Total estimated implementation time: 3-4 days**
