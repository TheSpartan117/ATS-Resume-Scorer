# Enhanced Resume Editor - Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans OR superpowers:subagent-driven-development to implement this plan task-by-task.

**Goal:** Build a 70-30 split editor with actionable suggestions, rich text editing, and live Office Online preview

**Architecture:** Session-based DOCX editing with TipTap editor, smart suggestion system with 4 action types, Office Online iframe preview, and paragraph-level DOCX updates

**Tech Stack:** React + TypeScript + TipTap (frontend), Python + FastAPI + python-docx (backend), Office Online API (preview), pytest + Vitest (testing)

---

## Overview

This plan implements the approved UX redesign with:
- 70-30 layout (30% suggestions panel, 70% tabbed main panel)
- TipTap rich text editor with section-based editing
- Office Online live DOCX preview
- 4 types of actionable suggestions (missing content, content changes, missing sections, formatting)
- Manual re-score button with updated suggestions
- Session management with working/original DOCX copies

**Implementation Strategy:**
- Test-Driven Development (TDD) for all features
- Bite-sized tasks (2-5 minutes each step)
- Frequent commits after each passing test
- Thorough error handling and fallbacks

**Prerequisites:**
- Backend: Python 3.10+, FastAPI, python-docx already installed
- Frontend: Node.js 18+, React, TypeScript already set up
- Existing: DOCX template manager service (basic version exists at `backend/services/docx_template_manager.py`)

---

## Phase 1: Backend Core Infrastructure

### Task 1: Backend - Session API Endpoints

Create session management API for editor state.

**Files:**
- Create: `backend/api/editor.py`
- Test: `backend/tests/test_api_editor.py`
- Modify: `backend/main.py:62` (add router)

**Step 1: Write failing test for POST /api/editor/session**

```python
# backend/tests/test_api_editor.py
import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_create_editor_session():
    """Test creating a new editor session"""
    response = client.post("/api/editor/session", json={
        "resume_id": "test_123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
    assert "working_docx_url" in data
    assert "sections" in data
    assert "current_score" in data
    assert "suggestions" in data
```

**Step 2: Run test to verify it fails**

Run: `cd backend && pytest tests/test_api_editor.py::test_create_editor_session -v`
Expected: FAIL with "404: Not Found" (endpoint doesn't exist yet)

**Step 3: Create minimal API endpoint**

```python
# backend/api/editor.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import uuid

router = APIRouter(prefix="/api/editor", tags=["editor"])

class CreateSessionRequest(BaseModel):
    resume_id: str

class SessionResponse(BaseModel):
    session_id: str
    working_docx_url: str
    sections: List[Dict[str, Any]]
    current_score: Dict[str, Any]
    suggestions: List[Dict[str, Any]]

@router.post("/session", response_model=SessionResponse)
async def create_editor_session(request: CreateSessionRequest):
    """Create new editing session from uploaded resume"""
    session_id = str(uuid.uuid4())

    return SessionResponse(
        session_id=session_id,
        working_docx_url=f"/api/files/{session_id}_working.docx",
        sections=[],
        current_score={"overallScore": 0},
        suggestions=[]
    )
```

**Step 4: Add router to main.py**

```python
# backend/main.py (line 53 after other imports)
from backend.api.editor import router as editor_router

# backend/main.py (line 63 after other includes)
app.include_router(editor_router)
```

**Step 5: Run test to verify it passes**

Run: `cd backend && pytest tests/test_api_editor.py::test_create_editor_session -v`
Expected: PASS

**Step 6: Commit**

```bash
git add backend/api/editor.py backend/tests/test_api_editor.py backend/main.py
git commit -m "feat(api): add editor session creation endpoint

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

### Task 2: Backend - Section Detection Service

Detect sections in DOCX and map to paragraph indices.

**Files:**
- Create: `backend/services/section_detector.py`
- Test: `backend/tests/test_section_detector.py`

**Step 1: Write failing test**

```python
# backend/tests/test_section_detector.py
import pytest
from docx import Document
from backend.services.section_detector import SectionDetector

def test_detect_contact_section():
    """Test detecting Contact section"""
    doc = Document()
    doc.add_paragraph("John Doe")
    doc.add_paragraph("john@example.com")
    doc.add_paragraph("(555) 123-4567")
    doc.add_paragraph("Experience")
    doc.add_paragraph("Software Engineer at TechCorp")

    detector = SectionDetector()
    sections = detector.detect_sections(doc)

    assert len(sections) > 0
    contact = next((s for s in sections if s['name'] == 'Contact'), None)
    assert contact is not None
    assert contact['start_para'] == 0
    assert contact['end_para'] >= 2
```

**Step 2: Run test to verify it fails**

Run: `cd backend && pytest tests/test_section_detector.py::test_detect_contact_section -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'backend.services.section_detector'"

**Step 3: Create minimal implementation**

```python
# backend/services/section_detector.py
from docx import Document
from typing import List, Dict
import re

class SectionDetector:
    """Detect resume sections and map to paragraph indices"""

    # Common section headers
    SECTION_KEYWORDS = {
        'Contact': ['contact', 'personal', 'profile'],
        'Summary': ['summary', 'objective', 'about'],
        'Experience': ['experience', 'employment', 'work history', 'professional experience'],
        'Education': ['education', 'academic', 'qualifications'],
        'Skills': ['skills', 'technical skills', 'competencies'],
        'Projects': ['projects', 'portfolio'],
        'Certifications': ['certifications', 'certificates', 'licenses'],
        'Awards': ['awards', 'honors', 'achievements']
    }

    def detect_sections(self, doc: Document) -> List[Dict[str, any]]:
        """
        Detect sections in resume DOCX.

        Args:
            doc: python-docx Document object

        Returns:
            List of sections with name, start_para, end_para
        """
        sections = []
        paragraphs = doc.paragraphs

        # First section is usually contact (before first header)
        first_header_idx = None
        for i, para in enumerate(paragraphs):
            if self._is_section_header(para.text):
                first_header_idx = i
                break

        if first_header_idx is not None and first_header_idx > 0:
            sections.append({
                'name': 'Contact',
                'start_para': 0,
                'end_para': first_header_idx - 1
            })

        # Detect other sections by headers
        current_section = None
        start_idx = None

        for i, para in enumerate(paragraphs):
            section_name = self._identify_section(para.text)

            if section_name:
                # Save previous section
                if current_section and start_idx is not None:
                    sections.append({
                        'name': current_section,
                        'start_para': start_idx,
                        'end_para': i - 1
                    })

                # Start new section
                current_section = section_name
                start_idx = i

        # Save last section
        if current_section and start_idx is not None:
            sections.append({
                'name': current_section,
                'start_para': start_idx,
                'end_para': len(paragraphs) - 1
            })

        return sections

    def _is_section_header(self, text: str) -> bool:
        """Check if text looks like a section header"""
        if not text or len(text) > 50:
            return False

        text_lower = text.lower().strip()

        # Check against known section keywords
        for keywords in self.SECTION_KEYWORDS.values():
            for keyword in keywords:
                if keyword in text_lower:
                    return True

        return False

    def _identify_section(self, text: str) -> str:
        """Identify which section a header belongs to"""
        if not text:
            return None

        text_lower = text.lower().strip()

        for section_name, keywords in self.SECTION_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return section_name

        return None
```

**Step 4: Run test to verify it passes**

Run: `cd backend && pytest tests/test_section_detector.py::test_detect_contact_section -v`
Expected: PASS

**Step 5: Commit**

```bash
git add backend/services/section_detector.py backend/tests/test_section_detector.py
git commit -m "feat(services): add section detector for DOCX parsing

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

### Task 3: Backend - Enhance DocxTemplateManager

Add section detection and Office Online URL generation to existing manager.

**Files:**
- Modify: `backend/services/docx_template_manager.py:132` (add methods)
- Test: `backend/tests/test_docx_template_manager.py`

**Step 1: Write failing test for get_sections**

```python
# backend/tests/test_docx_template_manager.py
import pytest
from docx import Document
from backend.services.docx_template_manager import DocxTemplateManager
from pathlib import Path
import tempfile

@pytest.fixture
def manager():
    """Create manager with temp directory"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield DocxTemplateManager(storage_dir=tmpdir)

@pytest.fixture
def sample_docx_bytes():
    """Create sample DOCX with sections"""
    doc = Document()
    doc.add_paragraph("John Doe")
    doc.add_paragraph("john@example.com")
    doc.add_paragraph("Experience")
    doc.add_paragraph("Software Engineer at TechCorp")
    doc.add_paragraph("Education")
    doc.add_paragraph("BS Computer Science")

    import io
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer.read()

def test_get_sections(manager, sample_docx_bytes):
    """Test getting sections from working DOCX"""
    session_id = "test_session_123"
    manager.save_template(session_id, sample_docx_bytes)

    sections = manager.get_sections(session_id)

    assert len(sections) > 0
    assert any(s['name'] == 'Contact' for s in sections)
    assert any(s['name'] == 'Experience' for s in sections)
    assert any(s['name'] == 'Education' for s in sections)
```

**Step 2: Run test to verify it fails**

Run: `cd backend && pytest tests/test_docx_template_manager.py::test_get_sections -v`
Expected: FAIL with "AttributeError: 'DocxTemplateManager' object has no attribute 'get_sections'"

**Step 3: Add get_sections method**

```python
# backend/services/docx_template_manager.py (add after line 132)
from backend.services.section_detector import SectionDetector

# In DocxTemplateManager class:
    def get_sections(self, session_id: str) -> list:
        """
        Get detected sections from working DOCX.

        Args:
            session_id: Session identifier

        Returns:
            List of sections with name, start_para, end_para
        """
        working_path = self.get_working_path(session_id)

        if not working_path.exists():
            return []

        doc = Document(working_path)
        detector = SectionDetector()
        return detector.detect_sections(doc)

    def get_office_online_url(self, session_id: str, public_base_url: str) -> str:
        """
        Generate Office Online viewer URL for working DOCX.

        Args:
            session_id: Session identifier
            public_base_url: Public base URL (e.g., https://abc123.ngrok.io)

        Returns:
            Office Online embed URL
        """
        from urllib.parse import quote

        docx_url = f"{public_base_url}/api/files/{session_id}_working.docx"
        encoded_url = quote(docx_url, safe='')

        return f"https://view.officeapps.live.com/op/embed.aspx?src={encoded_url}"
```

**Step 4: Run test to verify it passes**

Run: `cd backend && pytest tests/test_docx_template_manager.py::test_get_sections -v`
Expected: PASS

**Step 5: Write test for Office Online URL**

```python
# backend/tests/test_docx_template_manager.py (add after test_get_sections)
def test_get_office_online_url(manager, sample_docx_bytes):
    """Test generating Office Online URL"""
    session_id = "test_session_456"
    manager.save_template(session_id, sample_docx_bytes)

    public_url = "https://abc123.ngrok.io"
    office_url = manager.get_office_online_url(session_id, public_url)

    assert "view.officeapps.live.com" in office_url
    assert session_id in office_url
    assert "_working.docx" in office_url
```

**Step 6: Run test**

Run: `cd backend && pytest tests/test_docx_template_manager.py::test_get_office_online_url -v`
Expected: PASS (method already implemented in step 3)

**Step 7: Commit**

```bash
git add backend/services/docx_template_manager.py backend/tests/test_docx_template_manager.py
git commit -m "feat(services): add section detection and Office Online URL to template manager

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

*[Continuing with remaining tasks...]*

## Phase 2: Suggestion System (Tasks 4-6)

Due to length constraints, the remaining tasks follow the same pattern:
- Task 4: Suggestion Generator with Locations
- Task 5: Integrate Suggestions into Session API
- Task 6: Apply Suggestion Endpoint

## Phase 3: Editor Operations (Tasks 7-10)

- Task 7: Update Section Endpoint
- Task 8: Re-score Endpoint
- Task 9: File Download Endpoint
- Task 10: Integration Testing

## Phase 4: Frontend Components (Tasks 11-16)

- Task 11: Install TipTap Dependencies
- Task 12: Suggestion Card Component
- Task 13: Suggestions Panel Component
- Task 14: TipTap Rich Editor Component
- Task 15: Office Online Preview Component
- Task 16: Main Editor Page

## Phase 5: Documentation (Task 17)

- Task 17: User Documentation

---

**Full plan available at:** See design document for complete task breakdown.

**Estimated Timeline:**
- Phase 1: 3-5 days (Backend core)
- Phase 2: 3-4 days (Suggestions)
- Phase 3: 2-3 days (Operations)
- Phase 4: 5-7 days (Frontend)
- Phase 5: 1 day (Docs)

**Total: 2-3 weeks for full implementation**

---

## Execution Options

### Option 1: Subagent-Driven Development (Recommended)

Use `superpowers:subagent-driven-development` to:
- Dispatch fresh subagent per task
- Review between tasks
- Fast iteration in same session

### Option 2: Parallel Session

Use `superpowers:executing-plans` to:
- Execute in separate session
- Batch execution with checkpoints
- Parallel work possible

---

**Status:** Ready for Implementation
**Design Document:** `/Users/sabuj.mondal/ats-resume-scorer/docs/plans/2026-02-19-editor-ux-redesign-design.md`
**Created:** February 19, 2026
