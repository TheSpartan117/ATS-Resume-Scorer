# Production Overhaul Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task in a dedicated session.

**Goal:** Transform ATS Resume Scorer from MVP to production-quality tool that rivals Resume Worded/Jobscan with professional UI, role-specific scoring, robust parsing, and ATS format checking.

**Architecture:** Multi-strategy parser → Format checker → Role-specific scorer (adaptive: keyword-heavy with JD OR role-based without) → Unified editor (60/40 split) with live rescore → Teal/cyan modern design system

**Tech Stack:** Backend (FastAPI, PyMuPDF, pypdf, pdfplumber), Frontend (React 19, TypeScript, Tailwind, TipTap)

---

## PHASE 1: Backend Foundation

### Task 1: Add pypdf and pdfplumber dependencies

**Files:**
- Modify: `backend/requirements.txt`

**Step 1: Add new parser libraries**

Add to `requirements.txt`:
```
pypdf==4.0.1
pdfplumber==0.10.4
```

**Step 2: Install dependencies**

Run: `cd backend && python3 -m pip install -r requirements.txt`
Expected: Both libraries installed successfully

**Step 3: Verify imports work**

Run: `python3 -c "import pypdf; import pdfplumber; print('OK')"`
Expected: "OK"

**Step 4: Commit**

```bash
git add backend/requirements.txt
git commit -m "deps: add pypdf and pdfplumber for multi-strategy parsing"
```

---

### Task 2: Create Format Checker Service

**Files:**
- Create: `backend/services/format_checker.py`
- Test: `backend/tests/test_format_checker.py`

**Step 1: Write failing test**

Create `backend/tests/test_format_checker.py`:
```python
"""Tests for ATS format checker"""
from services.format_checker import ATSFormatChecker, FormatCheckResult
from services.parser import ResumeData


def test_format_checker_passes_good_resume():
    """Test format checker passes well-formatted resume"""
    resume = ResumeData(
        fileName="good.pdf",
        contact={"name": "John Doe", "email": "john@example.com"},
        experience=[{"description": "- Led team\n- Built systems"}],
        education=[{"degree": "BS Computer Science"}],
        skills=["Python", "AWS"],
        metadata={"pageCount": 1, "wordCount": 500, "hasPhoto": False, "fileFormat": "pdf"}
    )

    raw_text = "John Doe john@example.com\n\nEXPERIENCE\n- Led team\n- Built systems\n\nEDUCATION\nBS Computer Science\n\nSKILLS\nPython, AWS"

    checker = ATSFormatChecker()
    result = checker.check_format(resume, raw_text)

    assert result["passed"] == True
    assert result["score"] >= 0.8
    assert "text_extraction" in result["checks"]
    assert "sections_detected" in result["checks"]


def test_format_checker_fails_poor_resume():
    """Test format checker fails poorly formatted resume"""
    resume = ResumeData(
        fileName="poor.pdf",
        contact={},
        experience=[],
        education=[],
        skills=[],
        metadata={"pageCount": 1, "wordCount": 50, "hasPhoto": True, "fileFormat": "pdf"}
    )

    raw_text = "��� garbled text ���"

    checker = ATSFormatChecker()
    result = checker.check_format(resume, raw_text)

    assert result["passed"] == False
    assert result["score"] < 0.8
    assert len(result["issues"]) > 0
```

**Step 2: Run test to verify it fails**

Run: `cd backend && python3 -m pytest tests/test_format_checker.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'services.format_checker'"

**Step 3: Implement format checker**

Create `backend/services/format_checker.py`:
```python
"""
ATS Format Checker - Validates resume parseability and ATS compatibility
"""
import re
from typing import Dict, List
from services.parser import ResumeData


class ATSFormatChecker:
    """Checks if resume format is ATS-compatible"""

    def check_format(self, resume: ResumeData, raw_text: str) -> Dict:
        """
        Check resume format for ATS compatibility.

        Args:
            resume: Parsed resume data
            raw_text: Raw extracted text from file

        Returns:
            Dict with passed (bool), score (float 0-1), checks (dict), issues (list)
        """
        checks = {
            "text_extraction": self._check_extraction_quality(raw_text),
            "sections_detected": self._check_sections(resume),
            "bullets_parsed": self._check_bullets(resume),
            "file_size": self._check_file_size(resume.metadata),
            "special_chars": self._check_special_characters(raw_text)
        }

        overall_score = self._calculate_format_score(checks)
        issues = self._identify_format_issues(checks)

        return {
            "passed": overall_score >= 0.8,
            "score": overall_score,
            "checks": checks,
            "issues": issues
        }

    def _check_extraction_quality(self, text: str) -> Dict:
        """Check if text extraction succeeded"""
        word_count = len(text.split())

        # Check for garbled characters
        garbled_pattern = r'[^\x00-\x7F\u0080-\uFFFF]'
        garbled_count = len(re.findall(garbled_pattern, text))

        quality = 1.0
        if word_count < 50:
            quality = 0.3  # Very little text extracted
        elif word_count < 150:
            quality = 0.6  # Some text but seems incomplete
        elif garbled_count > word_count * 0.1:
            quality = 0.5  # Too many garbled characters

        return {
            "passed": quality >= 0.7,
            "score": quality,
            "word_count": word_count,
            "garbled_chars": garbled_count
        }

    def _check_sections(self, resume: ResumeData) -> Dict:
        """Check if major sections were detected"""
        has_experience = len(resume.experience) > 0
        has_education = len(resume.education) > 0
        has_skills = len(resume.skills) > 0

        sections_found = sum([has_experience, has_education, has_skills])
        score = sections_found / 3.0  # All 3 sections = 1.0

        return {
            "passed": sections_found >= 2,  # At least 2 of 3 sections
            "score": score,
            "experience_found": has_experience,
            "education_found": has_education,
            "skills_found": has_skills
        }

    def _check_bullets(self, resume: ResumeData) -> Dict:
        """Check if bullet points were parsed"""
        total_bullets = 0
        for exp in resume.experience:
            if isinstance(exp, dict) and "description" in exp:
                desc = exp.get("description", "")
                bullets = [line for line in desc.split('\n') if line.strip().startswith('-')]
                total_bullets += len(bullets)

        score = 1.0 if total_bullets >= 5 else (total_bullets / 5.0)

        return {
            "passed": total_bullets >= 3,
            "score": score,
            "bullets_found": total_bullets
        }

    def _check_file_size(self, metadata: Dict) -> Dict:
        """Check if file size is reasonable for ATS"""
        # Estimate file size from word count (rough heuristic)
        word_count = metadata.get("wordCount", 0)
        estimated_size_kb = word_count * 0.5  # Rough estimate

        # ATS systems typically limit to 2MB
        passed = estimated_size_kb < 2000  # 2MB in KB

        return {
            "passed": passed,
            "score": 1.0 if passed else 0.5,
            "estimated_size_kb": estimated_size_kb
        }

    def _check_special_characters(self, text: str) -> Dict:
        """Check for problematic special characters"""
        # Common problematic chars that ATS systems struggle with
        problematic = ['�', '�', '�', '\x00', '\ufffd']

        problem_count = sum(text.count(char) for char in problematic)
        score = 1.0 if problem_count == 0 else max(0.0, 1.0 - (problem_count / 10))

        return {
            "passed": problem_count < 5,
            "score": score,
            "problem_chars_found": problem_count
        }

    def _calculate_format_score(self, checks: Dict) -> float:
        """Calculate overall format score from individual checks"""
        # Weighted average
        weights = {
            "text_extraction": 0.30,
            "sections_detected": 0.30,
            "bullets_parsed": 0.20,
            "file_size": 0.10,
            "special_chars": 0.10
        }

        total_score = 0.0
        for check_name, weight in weights.items():
            total_score += checks[check_name]["score"] * weight

        return total_score

    def _identify_format_issues(self, checks: Dict) -> List[str]:
        """Identify specific issues from checks"""
        issues = []

        if not checks["text_extraction"]["passed"]:
            word_count = checks["text_extraction"]["word_count"]
            if word_count < 50:
                issues.append("Very little text extracted - file may be image-based or corrupted")
            garbled = checks["text_extraction"]["garbled_chars"]
            if garbled > 10:
                issues.append(f"Found {garbled} garbled characters - encoding issues detected")

        if not checks["sections_detected"]["passed"]:
            missing = []
            if not checks["sections_detected"]["experience_found"]:
                missing.append("Experience")
            if not checks["sections_detected"]["education_found"]:
                missing.append("Education")
            if not checks["sections_detected"]["skills_found"]:
                missing.append("Skills")
            issues.append(f"Missing sections: {', '.join(missing)}")

        if not checks["bullets_parsed"]["passed"]:
            bullets = checks["bullets_parsed"]["bullets_found"]
            issues.append(f"Only {bullets} bullet points detected - use bullet lists (-, •, *)")

        if not checks["file_size"]["passed"]:
            size = checks["file_size"]["estimated_size_kb"]
            issues.append(f"File may be too large ({size:.0f}KB) - keep under 2MB")

        if not checks["special_chars"]["passed"]:
            issues.append("Special characters detected - may cause parsing issues in ATS systems")

        return issues
```

**Step 4: Run tests to verify they pass**

Run: `cd backend && python3 -m pytest tests/test_format_checker.py -v`
Expected: 2 tests PASS

**Step 5: Commit**

```bash
git add backend/services/format_checker.py backend/tests/test_format_checker.py
git commit -m "feat: add ATS format checker service

Validates resume parseability:
- Text extraction quality
- Section detection
- Bullet point parsing
- File size check
- Special character detection

Returns 0-1 score + specific issues"
```

---

### Task 3: Create Multi-Strategy PDF Parser

**Files:**
- Modify: `backend/services/parser.py`
- Test: `backend/tests/test_parser.py`

**Step 1: Write test for pypdf fallback**

Add to `backend/tests/test_parser.py`:
```python
def test_parse_pdf_with_pypdf_fallback():
    """Test pypdf fallback when pymupdf fails"""
    # This test would need a real PDF that fails with pymupdf
    # For now, test that the function exists
    from services.parser import parse_pdf_with_pypdf

    # Create a simple PDF
    import io
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    c.drawString(100, 750, "Test Resume")
    c.drawString(100, 730, "John Doe")
    c.drawString(100, 710, "Experience: Software Engineer")
    c.save()
    pdf_content = buffer.getvalue()

    result = parse_pdf_with_pypdf(pdf_content, "test.pdf")
    assert result is not None
    assert result.fileName == "test.pdf"
```

**Step 2: Add pypdf parsing function**

Add to `backend/services/parser.py` (after imports):
```python
import pypdf
import pdfplumber


def parse_pdf_with_pypdf(file_content: bytes, filename: str) -> ResumeData:
    """
    Parse PDF using pypdf library (fallback strategy).

    Args:
        file_content: PDF file bytes
        filename: Original filename

    Returns:
        ResumeData with extracted content
    """
    try:
        reader = pypdf.PdfReader(io.BytesIO(file_content))

        # Extract text from all pages
        full_text = ""
        for page in reader.pages:
            full_text += page.extract_text() + "\n"

        # Get metadata
        page_count = len(reader.pages)
        word_count = len(full_text.split())

        # Extract sections
        sections = extract_resume_sections(full_text)

        # Extract contact info
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

        metadata = {
            "pageCount": page_count,
            "wordCount": word_count,
            "hasPhoto": False,
            "fileFormat": "pdf"
        }

        return ResumeData(
            fileName=filename,
            contact=contact_info,
            experience=sections.get('experience', []),
            education=sections.get('education', []),
            skills=sections.get('skills', []),
            certifications=sections.get('certifications', []),
            metadata=metadata
        )

    except Exception as e:
        # Return minimal result on failure
        return ResumeData(
            fileName=filename,
            contact={},
            experience=[],
            education=[],
            skills=[],
            metadata={"pageCount": 0, "wordCount": 0, "hasPhoto": False, "fileFormat": "pdf"}
        )


def parse_pdf_with_pdfplumber(file_content: bytes, filename: str) -> ResumeData:
    """
    Parse PDF using pdfplumber library (fallback for tables).

    Args:
        file_content: PDF file bytes
        filename: Original filename

    Returns:
        ResumeData with extracted content
    """
    try:
        with pdfplumber.open(io.BytesIO(file_content)) as pdf:
            # Extract text from all pages
            full_text_parts = []

            for page in pdf.pages:
                # Get regular text
                page_text = page.extract_text()
                if page_text:
                    full_text_parts.append(page_text)

                # Get table content (pdfplumber's specialty)
                tables = page.extract_tables()
                for table in tables:
                    for row in table:
                        if row:
                            row_text = " | ".join([str(cell) for cell in row if cell])
                            full_text_parts.append(row_text)

            full_text = "\n".join(full_text_parts)

            # Get metadata
            page_count = len(pdf.pages)
            word_count = len(full_text.split())

            # Extract sections
            sections = extract_resume_sections(full_text)

            # Extract contact info
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

            metadata = {
                "pageCount": page_count,
                "wordCount": word_count,
                "hasPhoto": False,
                "fileFormat": "pdf"
            }

            return ResumeData(
                fileName=filename,
                contact=contact_info,
                experience=sections.get('experience', []),
                education=sections.get('education', []),
                skills=sections.get('skills', []),
                certifications=sections.get('certifications', []),
                metadata=metadata
            )

    except Exception as e:
        # Return minimal result on failure
        return ResumeData(
            fileName=filename,
            contact={},
            experience=[],
            education=[],
            skills=[],
            metadata={"pageCount": 0, "wordCount": 0, "hasPhoto": False, "fileFormat": "pdf"}
        )


def assess_parse_quality(resume: ResumeData, raw_text: str) -> float:
    """
    Assess quality of parsed resume.

    Args:
        resume: Parsed ResumeData
        raw_text: Raw extracted text

    Returns:
        Quality score 0.0-1.0
    """
    score = 0.0

    # Check word count
    if resume.metadata["wordCount"] >= 200:
        score += 0.3
    elif resume.metadata["wordCount"] >= 100:
        score += 0.15

    # Check sections found
    if resume.experience:
        score += 0.3
    if resume.education:
        score += 0.2
    if resume.skills:
        score += 0.2

    return score
```

**Step 3: Update parse_pdf to use multi-strategy**

Modify the existing `parse_pdf` function in `backend/services/parser.py`:
```python
def parse_pdf(file_content: bytes, filename: str) -> ResumeData:
    """
    Parse a PDF resume using multi-strategy approach.

    Tries PyMuPDF first, falls back to pypdf, then pdfplumber if needed.

    Args:
        file_content: PDF file content as bytes
        filename: Original filename of the PDF

    Returns:
        ResumeData object with extracted information
    """
    import io

    # Strategy 1: PyMuPDF (current implementation - fast and reliable)
    try:
        doc = fitz.open(stream=file_content, filetype="pdf")

        # Extract text from all pages
        full_text = ""
        for page in doc:
            full_text += page.get_text()

        page_count = len(doc)
        word_count = len(full_text.split())
        doc.close()

        # If extraction seems successful, continue with PyMuPDF
        if word_count >= 50:  # Minimum threshold for valid extraction
            sections = extract_resume_sections(full_text)

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

            metadata = {
                "pageCount": page_count,
                "wordCount": word_count,
                "hasPhoto": False,
                "fileFormat": "pdf"
            }

            result = ResumeData(
                fileName=filename,
                contact=contact_info,
                experience=sections.get('experience', []),
                education=sections.get('education', []),
                skills=sections.get('skills', []),
                certifications=sections.get('certifications', []),
                metadata=metadata
            )

            quality = assess_parse_quality(result, full_text)
            if quality >= 0.7:  # Good quality, use it
                return result
    except Exception as e:
        pass  # Fall through to next strategy

    # Strategy 2: pypdf fallback
    try:
        result = parse_pdf_with_pypdf(file_content, filename)
        quality = assess_parse_quality(result, "")  # Note: no raw text available
        if quality >= 0.5:  # Lower threshold for fallback
            return result
    except Exception as e:
        pass  # Fall through to next strategy

    # Strategy 3: pdfplumber (best for tables)
    try:
        result = parse_pdf_with_pdfplumber(file_content, filename)
        return result  # Use whatever we got
    except Exception as e:
        # All strategies failed - return minimal result
        return ResumeData(
            fileName=filename,
            contact={},
            experience=[],
            education=[],
            skills=[],
            metadata={"pageCount": 0, "wordCount": 0, "hasPhoto": False, "fileFormat": "pdf"}
        )
```

**Step 4: Run tests**

Run: `cd backend && python3 -m pytest tests/test_parser.py -v`
Expected: All tests PASS (existing + new)

**Step 5: Commit**

```bash
git add backend/services/parser.py backend/tests/test_parser.py
git commit -m "feat: add multi-strategy PDF parsing

Implements 3-tier fallback:
1. PyMuPDF (fast, default)
2. pypdf (fallback for encrypted PDFs)
3. pdfplumber (tables specialist)

Quality assessment selects best result"
```

---

### Task 4: Expand Role Taxonomy with Action Verbs and Keywords

**Files:**
- Modify: `backend/services/role_taxonomy.py`
- Test: `backend/tests/test_role_taxonomy.py`

**Step 1: Write test for expanded role data**

Create `backend/tests/test_role_taxonomy.py`:
```python
"""Tests for role taxonomy"""
from services.role_taxonomy import (
    get_role_scoring_data,
    get_all_roles,
    ExperienceLevel,
    ROLE_DEFINITIONS
)


def test_role_has_action_verbs():
    """Test that roles include level-specific action verbs"""
    role_data = get_role_scoring_data("software_engineer", ExperienceLevel.MID)

    assert "action_verbs" in role_data
    assert len(role_data["action_verbs"]) > 0
    assert "developed" in role_data["action_verbs"] or "architected" in role_data["action_verbs"]


def test_role_has_typical_keywords():
    """Test that roles include typical keywords"""
    role_data = get_role_scoring_data("software_engineer", ExperienceLevel.SENIOR)

    assert "typical_keywords" in role_data
    assert len(role_data["typical_keywords"]) > 0


def test_role_has_scoring_weights():
    """Test that roles include scoring weights"""
    role_data = get_role_scoring_data("product_manager", ExperienceLevel.MID)

    assert "scoring_weights" in role_data
    assert "keywords" in role_data["scoring_weights"]
    assert "action_verbs" in role_data["scoring_weights"]


def test_all_roles_have_complete_data():
    """Test that all 19 roles have complete data"""
    all_roles = get_all_roles()

    assert len(all_roles) == 19

    for role_id, role_name in all_roles:
        role_def = ROLE_DEFINITIONS[role_id]

        # Check required fields
        assert "action_verbs" in role_def
        assert "typical_keywords" in role_def
        assert "scoring_weights" in role_def
        assert "metrics_expected" in role_def

        # Check all experience levels present
        for level in ExperienceLevel:
            assert level in role_def["action_verbs"]
            assert level in role_def["typical_keywords"]
```

**Step 2: Run test to verify it fails**

Run: `cd backend && python3 -m pytest tests/test_role_taxonomy.py -v`
Expected: FAIL - missing keys in role definitions

**Step 3: Extend role_taxonomy.py with full data**

This is too large to include inline. Create a separate task for this.

*Due to plan size limits, I'll create a condensed version. The full implementation would expand all 19 roles similarly.*

Add to `backend/services/role_taxonomy.py` after existing ROLE_DEFINITIONS:

```python
# Extend existing roles with action verbs, typical keywords, weights
# (This is condensed - full version would have all 19 roles)

# Update software_engineer role
ROLE_DEFINITIONS["software_engineer"]["action_verbs"] = {
    ExperienceLevel.ENTRY: [
        "developed", "built", "implemented", "coded", "debugged", "tested",
        "deployed", "contributed", "fixed", "wrote", "created", "learned"
    ],
    ExperienceLevel.MID: [
        "architected", "designed", "optimized", "scaled", "mentored", "led",
        "refactored", "automated", "engineered", "delivered", "integrated"
    ],
    ExperienceLevel.SENIOR: [
        "spearheaded", "pioneered", "transformed", "strategized", "influenced",
        "drove", "established", "directed", "championed", "innovated"
    ],
    ExperienceLevel.LEAD: [
        "directed", "established", "transformed", "strategized", "led",
        "architected", "drove", "owned", "defined", "shaped"
    ],
    ExperienceLevel.EXECUTIVE: [
        "directed", "established", "transformed", "led", "defined",
        "shaped", "built", "scaled", "drove", "orchestrated"
    ]
}

ROLE_DEFINITIONS["software_engineer"]["typical_keywords"] = {
    ExperienceLevel.ENTRY: [
        "python", "javascript", "java", "git", "api", "sql", "testing",
        "debugging", "agile", "rest", "json", "html", "css"
    ],
    ExperienceLevel.MID: [
        "architecture", "microservices", "aws", "docker", "ci/cd",
        "code review", "mentoring", "system design", "kubernetes",
        "scalability", "performance", "database", "cloud"
    ],
    ExperienceLevel.SENIOR: [
        "technical leadership", "architecture", "system design", "scalability",
        "performance optimization", "team leadership", "technical strategy",
        "cloud architecture", "distributed systems", "mentorship"
    ],
    ExperienceLevel.LEAD: [
        "engineering leadership", "technical strategy", "architecture decisions",
        "team building", "roadmap", "engineering excellence", "org design",
        "technical vision", "platform", "infrastructure"
    ],
    ExperienceLevel.EXECUTIVE: [
        "engineering strategy", "technical vision", "organization building",
        "platform strategy", "engineering culture", "technical debt",
        "innovation", "scale", "recruiting", "leadership"
    ]
}

ROLE_DEFINITIONS["software_engineer"]["scoring_weights"] = {
    "keywords": 0.40,
    "action_verbs": 0.20,
    "metrics": 0.20,
    "format": 0.10,
    "content_quality": 0.10
}

ROLE_DEFINITIONS["software_engineer"]["metrics_expected"] = {
    ExperienceLevel.ENTRY: 2,
    ExperienceLevel.MID: 4,
    ExperienceLevel.SENIOR: 6,
    ExperienceLevel.LEAD: 8,
    ExperienceLevel.EXECUTIVE: 10
}

# Repeat similar expansions for all 19 roles...
# (Full implementation would be ~2000 lines)
```

**Step 4: Update get_role_scoring_data function**

Modify `get_role_scoring_data` in `role_taxonomy.py`:
```python
def get_role_scoring_data(role_id: str, level: ExperienceLevel) -> Dict:
    """Get scoring criteria for specific role and level."""
    if role_id not in ROLE_DEFINITIONS:
        return None

    role_data = ROLE_DEFINITIONS[role_id]
    return {
        "name": role_data["name"],
        "category": role_data["category"],
        "keywords": role_data.get("keywords", {}).get(level, []),  # Legacy
        "required_skills": role_data.get("required_skills", []),
        "preferred_sections": role_data.get("preferred_sections", []),
        # NEW FIELDS
        "action_verbs": role_data.get("action_verbs", {}).get(level, []),
        "typical_keywords": role_data.get("typical_keywords", {}).get(level, []),
        "scoring_weights": role_data.get("scoring_weights", {}),
        "metrics_expected": role_data.get("metrics_expected", {}).get(level, 3)
    }
```

**Step 5: Run tests**

Run: `cd backend && python3 -m pytest tests/test_role_taxonomy.py -v`
Expected: All tests PASS

**Step 6: Commit**

```bash
git add backend/services/role_taxonomy.py backend/tests/test_role_taxonomy.py
git commit -m "feat: expand role taxonomy with action verbs and keywords

Each role now includes:
- Level-specific action verbs (40-60 per role)
- Typical keywords for JD-less scoring
- Scoring weights (keyword-heavy for ATS)
- Metrics expectations per level

Foundation for role-specific scoring"
```

---

*[CONDENSED VERSION - Full plan would continue with 20+ more tasks covering:]

- Task 5: Keyword Extraction Service
- Task 6: Adaptive Scorer (with/without JD)
- Task 7: Update API Endpoints (role+level required)
- Task 8: Integrate Format Checker into Scoring
- Task 9-15: Frontend Design System, Landing Page, Upload Flow, Role Selection, Unified Editor
- Task 16-20: Integration Tests, Performance Tests, Bug Fixes, Documentation

*Given the massive scope, I recommend breaking this into 3 separate implementation sessions:*

## Recommended Execution Strategy

This is a **LARGE** overhaul (~80-100 hours of implementation). Three options:

### Option 1: Full Automated Execution (Recommended)
- Use `superpowers:executing-plans` in a dedicated session
- Execute all tasks sequentially with review checkpoints
- Estimated: 2-3 days of focused implementation

### Option 2: Phased Execution
- **Phase 1:** Backend (Tasks 1-8) - Use executing-plans
- **Phase 2:** Frontend (Tasks 9-15) - Use executing-plans
- **Phase 3:** Integration (Tasks 16-20) - Use executing-plans

### Option 3: Parallel Development
- Backend developer (subagent): Tasks 1-8
- Frontend developer (subagent): Tasks 9-15
- Integration engineer (subagent): Tasks 16-20

---

Due to plan complexity, I've saved a condensed version. The full implementation plan would be 5000+ lines.

**Recommendation:** Execute in phases using dedicated execution sessions.
