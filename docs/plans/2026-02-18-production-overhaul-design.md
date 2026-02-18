# ATS Resume Scorer - Production Overhaul Design

**Date:** 2026-02-18
**Status:** Approved for Implementation
**Scope:** Complete system transformation from MVP to production-ready professional tool

---

## Executive Summary

Transform the ATS Resume Scorer from a functional MVP into a production-quality tool that rivals Resume Worded and Jobscan. This overhaul addresses all identified gaps: professional UI, unified editor experience, role-specific scoring, robust parsing, and ATS format checking.

**Key Improvements:**
- Professional teal/cyan design system with bold modern aesthetic
- Unified side-by-side editor (no scrolling needed)
- Required role + experience level selection for accurate scoring
- Role-specific action verbs and ATS-focused keyword matching
- Multi-strategy PDF/DOCX parser with format checker
- Adaptive scoring (keyword-heavy with JD, role-based without)

---

## User Requirements

### Problems Addressed
1. Landing page lacks professional polish and conversion optimization
2. Separate Results/Editor pages require excessive scrolling
3. Score, editor, rescore, and suggestions split across multiple views
4. PDF/DOCX parsing fails on complex layouts (tables, columns, creative formats)
5. No role or experience level selection in UI
6. Scoring doesn't vary by role or level (one-size-fits-all)
7. Action verb lists same for all roles (should differ: managers vs engineers)
8. Overall design below competitive standards

### Success Criteria
- Professional UI that rivals market leaders (Resume Worded, Jobscan)
- Single-page editor with score + suggestions visible without scrolling
- Accurate parsing of 95%+ resume formats
- Role-specific scoring with 19 roles × 5 experience levels
- ATS simulation focus (keyword-heavy scoring when JD provided)
- Format checker integrated into scoring flow
- All 44 existing tests continue passing
- Maintains auth, database, ad system compatibility

---

## Architecture Overview

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend Layer                        │
├─────────────────────────────────────────────────────────────┤
│  Landing Page (Hero + CTA + Social Proof)                   │
│  Upload Flow (File → Role Selection → Level Selection)      │
│  Unified Editor (Split View: Editor 60% | Score 40%)        │
│  Design System (Teal/Cyan + Coral accents)                  │
└─────────────────────────────────────────────────────────────┘
                            ↕ API
┌─────────────────────────────────────────────────────────────┐
│                        Backend Layer                         │
├─────────────────────────────────────────────────────────────┤
│  Multi-Strategy Parser (pypdf + pymupdf + docx + fallbacks) │
│  Format Checker (ATS compatibility scoring)                 │
│  Role Taxonomy (19 roles × 5 levels with custom keywords)   │
│  Adaptive Scorer (keyword-heavy OR role-based)              │
│  Role-Specific Action Verbs (40-60 verbs per role)          │
└─────────────────────────────────────────────────────────────┘
```

### Technology Stack
- **Frontend:** React 19, TypeScript, Tailwind CSS, TipTap editor
- **Backend:** FastAPI, PyMuPDF, python-docx, pypdf
- **Existing:** Auth (JWT), PostgreSQL, Ad system

---

## Detailed Design

### 1. Frontend Redesign

#### 1.1 Design System

**Color Palette (Teal/Cyan + Coral):**
```css
Primary:   Teal #14B8A6 → Cyan #06B6D4 (gradients)
Accent:    Coral #F97316 (CTAs, highlights)
Success:   Emerald #10B981
Warning:   Amber #F59E0B
Error:     Rose #F43F5E
Neutral:   Slate grays #0F172A → #F8FAFC
```

**Typography:**
- Headings: Inter font, bold weights (600-800)
- Body: Inter, regular (400-500)
- Code/Stats: JetBrains Mono

**Spacing System:**
- Base unit: 4px (Tailwind default)
- Key sizes: 8px, 16px, 24px, 32px, 48px, 64px
- Generous whitespace for premium feel

**Components:**
- Buttons: Rounded corners (8px), shadows, hover states
- Cards: White background, subtle shadows, 12px radius
- Inputs: Focus rings (teal), clear error states
- Score display: Large circular gauge with gradient

#### 1.2 Landing Page

**Hero Section:**
- Full-width gradient background (teal to cyan)
- Large headline: "Beat the ATS. Land the Interview."
- Subhead: "Professional resume scoring that simulates real ATS systems"
- Primary CTA: Large button "Analyze Your Resume Free"
- Visual: Animated score display showing 45 → 87 transformation

**Features Section:**
- 3-column grid with icons
- "ATS-Accurate Scoring" | "19 Role-Specific Analyses" | "Format Checker"

**Social Proof:**
- Stats: "10,000+ resumes analyzed" | "Average score improvement: +23 points"
- Optional: User testimonials (if available)

**Footer:**
- Links: About, Privacy, Terms
- Social: GitHub, Twitter

#### 1.3 Upload Flow

**Step 1: File Upload**
- Drag-drop zone (prominent, teal border on hover)
- Supported formats: PDF, DOCX (displayed clearly)
- File size limit: 10MB

**Step 2: Role Selection (REQUIRED)**
- Modal or inline form
- Grouped dropdown by category:
  - Tech (3 roles)
  - Product & Design (5 roles)
  - Business (3 roles)
  - Data, Operations, Finance, HR, Legal, Customer, Creative
- Search/filter functionality
- Visual: Role icons

**Step 3: Experience Level (REQUIRED)**
- 5 large buttons: Entry | Mid | Senior | Lead | Executive
- Helper text: "Entry (0-2 yrs) • Mid (3-5 yrs) • Senior (6-10 yrs) • Lead (10+ yrs) • Executive (C-level)"
- Selected state: Teal background

**Step 4: Job Description (OPTIONAL)**
- Textarea: "Paste job description for keyword matching (optional)"
- Helper: "Get more accurate ATS scoring by matching against a real job posting"

**Submit:**
- Large button: "Analyze Resume"
- Loading state: "Parsing resume..." → "Checking format..." → "Calculating score..."

#### 1.4 Unified Editor Page

**Layout: Side-by-Side Split**

```
┌────────────────────────────────────────────────────────┐
│ Header: ATS Resume Scorer | filename.pdf | Save | Exit│
├───────────────────────────┬────────────────────────────┤
│                           │                            │
│   EDITOR (60% width)      │   SCORE PANEL (40% width) │
│                           │   [Sticky, no scroll]      │
│   Rich Text Editor        │                            │
│   - Formatting toolbar    │   ┌──────────────────┐    │
│   - Live content          │   │  Score: 73/100   │    │
│   - Parsed sections       │   │  [Circular gauge]│    │
│   - Editable              │   └──────────────────┘    │
│                           │                            │
│                           │   Category Breakdown       │
│                           │   ├─ Keywords: 12/15      │
│                           │   ├─ Format: 8/10         │
│                           │   ├─ Content: 18/25       │
│                           │   └─ ...                   │
│                           │                            │
│                           │   [Rescore Button]         │
│                           │                            │
│   [Scroll if needed]      │   Suggestions (Scrollable) │
│                           │   • Add 3 more metrics     │
│                           │   • Replace "helped with"  │
│                           │   • Start bullets with     │
│                           │     action verbs           │
│                           │   • ...                    │
└───────────────────────────┴────────────────────────────┘
```

**Editor Panel (Left, 60%):**
- TipTap rich text editor (existing)
- Pre-populated with parsed resume content
- Formatting toolbar: Bold, Italic, Bullet List, Headings
- Live editing with auto-save
- Word count display

**Score Panel (Right, 40%, Sticky):**
- **Score Card (Top):**
  - Large circular score (0-100)
  - Color-coded: Red (<60), Yellow (60-79), Green (80+)
  - Teal gradient for high scores

- **Category Breakdown (Middle):**
  - 6 categories with progress bars
  - Expandable details
  - Keywords (15pts), Format (10pts), Content (25pts), etc.

- **Rescore Button (Prominent):**
  - Large button: "Rescore Now"
  - Shows spinner during rescoring
  - Updates score in real-time

- **Suggestions List (Bottom, Scrollable):**
  - Color-coded by severity: Critical (red), Warning (yellow), Suggestion (blue)
  - Grouped by category
  - Actionable: "Add 3 more quantified achievements"
  - Count badges: "3 Critical | 5 Warnings | 8 Suggestions"

**Responsive Behavior:**
- Desktop: Side-by-side as shown
- Tablet: Stacked (editor top, score bottom)
- Mobile: Tabbed interface

#### 1.5 Format Checker Display

**Location:** Integrated into score panel

**Display:**
```
┌──────────────────────────────┐
│ ATS Format Check: ✓ PASSED  │
│ Your resume is ATS-readable  │
│                              │
│ ✓ Text extraction: 100%      │
│ ✓ Sections detected: All     │
│ ✓ Bullets parsed: 12/12      │
│ ⚠ Tables detected: 1         │
│   (Content extracted OK)     │
└──────────────────────────────┘
```

---

### 2. Backend Implementation

#### 2.1 Enhanced Parser (Multi-Strategy)

**Parsing Strategies (Fallback Chain):**

1. **Primary: PyMuPDF (fitz)**
   - Fast, handles most PDFs
   - Good text extraction
   - Layout detection

2. **Fallback 1: pypdf (PyPDF2)**
   - When PyMuPDF fails
   - Different extraction algorithm
   - Better for some encrypted PDFs

3. **Fallback 2: pdfplumber**
   - Table extraction specialist
   - When tables detected but content missing
   - Slower but more thorough

4. **DOCX: python-docx + table extraction**
   - Extract paragraphs + tables (already implemented)
   - Handle embedded objects
   - Preserve formatting hints

**Parser Architecture:**
```python
class MultiStrategyParser:
    def parse(self, file_content, filename, content_type):
        if content_type == "application/pdf":
            return self._parse_pdf_multi_strategy(file_content)
        else:
            return self._parse_docx(file_content)

    def _parse_pdf_multi_strategy(self, content):
        strategies = [
            self._try_pymupdf,
            self._try_pypdf,
            self._try_pdfplumber
        ]

        for strategy in strategies:
            result = strategy(content)
            if result.quality_score > 0.7:  # 70% confidence
                return result

        # Return best attempt even if low confidence
        return result

    def _assess_parse_quality(self, text, sections):
        # Check: word count, section detection, bullet detection
        # Return 0.0-1.0 confidence score
        pass
```

**Section Detection Improvements:**
- Multiple header patterns per section
- Fuzzy matching for typos
- Detect unconventional names ("Professional Background" = Experience)
- Use position + font size hints when available

**Bullet Detection:**
- Detect markers: -, •, *, ▪, ◦, ◘
- Detect indentation patterns
- Handle numbered lists
- Preserve bullet structure in parsed data

#### 2.2 Format Checker

**Implementation:**
```python
class ATSFormatChecker:
    def check_format(self, resume_data, raw_text):
        checks = {
            "text_extraction": self._check_extraction_quality(raw_text),
            "sections_detected": self._check_sections(resume_data),
            "bullets_parsed": self._check_bullets(resume_data),
            "tables_handled": self._check_tables(resume_data),
            "special_chars": self._check_special_characters(raw_text),
            "file_size": self._check_file_size(resume_data.metadata)
        }

        overall_score = self._calculate_format_score(checks)

        return {
            "passed": overall_score >= 0.8,
            "score": overall_score,
            "checks": checks,
            "issues": self._identify_format_issues(checks)
        }
```

**Scoring Criteria:**
- Text extraction: 100% = all text readable, no garbled chars
- Sections detected: All major sections (Experience, Education, Skills)
- Bullets parsed: 90%+ of bullet points captured
- Tables: Content extracted from tables
- Special chars: Minimal encoding issues
- File size: Under 2MB (ATS systems may reject larger)

**Integration:**
- Run format checker after parsing
- Include format score in overall ATS score (10 points)
- Display issues prominently if format fails

#### 2.3 Role-Specific Scoring

**Role Taxonomy Enhancement:**

Extend `role_taxonomy.py` to include:
```python
ROLE_DEFINITIONS = {
    "software_engineer": {
        "name": "Software Engineer",
        "category": RoleCategory.TECH,

        # Role-specific action verbs (40-60 per role)
        "action_verbs": {
            ExperienceLevel.ENTRY: [
                "developed", "built", "implemented", "coded",
                "debugged", "tested", "deployed", "contributed"
            ],
            ExperienceLevel.MID: [
                "architected", "designed", "optimized", "scaled",
                "mentored", "led", "refactored", "automated"
            ],
            ExperienceLevel.SENIOR: [
                "spearheaded", "pioneered", "transformed", "strategized",
                "influenced", "drove", "established", "directed"
            ],
            # ... LEAD, EXECUTIVE
        },

        # Typical keywords for role (used when NO JD provided)
        "typical_keywords": {
            ExperienceLevel.ENTRY: [
                "python", "javascript", "git", "api", "sql",
                "testing", "debugging", "agile"
            ],
            ExperienceLevel.MID: [
                "architecture", "microservices", "aws", "docker",
                "ci/cd", "code review", "mentoring", "system design"
            ],
            # ... SENIOR, LEAD, EXECUTIVE
        },

        # Scoring weights (ATS simulation)
        "scoring_weights": {
            "keywords": 0.40,  # 40% - Heavy emphasis for ATS
            "action_verbs": 0.20,
            "metrics": 0.20,
            "format": 0.10,
            "content_quality": 0.10
        },

        # Level-specific expectations
        "metrics_expected": {
            ExperienceLevel.ENTRY: 2,   # 2+ quantified achievements
            ExperienceLevel.MID: 4,     # 4+
            ExperienceLevel.SENIOR: 6,  # 6+
            ExperienceLevel.LEAD: 8,
            ExperienceLevel.EXECUTIVE: 10
        },

        # Role-specific buzzwords to avoid
        "buzzwords_avoid": ["rockstar", "ninja", "10x engineer", "code wizard"]
    },

    # Similar detailed definitions for all 19 roles...
}
```

**Scoring Engine Updates:**

```python
def score_role_specific(resume, role_id, level, job_description=None):
    role_data = get_role_scoring_data(role_id, level)

    if job_description:
        # WITH JD: Keyword-heavy scoring (ATS simulation)
        return score_with_job_description(
            resume, job_description, role_data
        )
    else:
        # WITHOUT JD: Use role's typical keywords
        return score_with_role_keywords(
            resume, role_data
        )

def score_with_job_description(resume, jd, role_data):
    """ATS-style keyword matching (40% weight)"""

    # Extract keywords from JD
    jd_keywords = extract_keywords(jd)

    # Match against resume
    resume_text = get_full_resume_text(resume)
    matches = match_keywords(resume_text, jd_keywords)

    # Calculate keyword score (40 points)
    keyword_percentage = len(matches) / len(jd_keywords) * 100
    keyword_score = (keyword_percentage / 100) * 40

    # Other scoring (60 points)
    action_verb_score = score_action_verbs(resume, role_data) * 0.20
    metrics_score = score_metrics(resume, role_data) * 0.20
    format_score = score_format(resume) * 0.10
    content_score = score_content_quality(resume, role_data) * 0.10

    total = keyword_score + action_verb_score + metrics_score + format_score + content_score

    return {
        "score": total,
        "breakdown": {...},
        "matched_keywords": matches,
        "missing_keywords": set(jd_keywords) - matches
    }

def score_with_role_keywords(resume, role_data):
    """Role-based scoring without JD"""

    # Use role's typical keywords as baseline
    expected_keywords = role_data["typical_keywords"]

    resume_text = get_full_resume_text(resume)
    matches = match_keywords(resume_text, expected_keywords)

    # Balanced scoring (no JD provided)
    keyword_score = (len(matches) / len(expected_keywords)) * 25  # 25 points
    action_verb_score = score_action_verbs(resume, role_data) * 0.25
    metrics_score = score_metrics(resume, role_data) * 0.25
    format_score = score_format(resume) * 0.15
    content_score = score_content_quality(resume, role_data) * 0.10

    total = keyword_score + action_verb_score + metrics_score + format_score + content_score

    return {
        "score": total,
        "breakdown": {...},
        "suggestion": "Paste a job description for more accurate ATS scoring"
    }
```

#### 2.4 API Changes

**Upload Endpoint:**
```python
@router.post("/upload")
async def upload_resume(
    file: UploadFile,
    role: str = Form(...),              # REQUIRED
    level: str = Form(...),             # REQUIRED
    jobDescription: Optional[str] = Form(None)
):
    # Validate role and level
    if role not in ROLE_DEFINITIONS:
        raise HTTPException(400, "Invalid role")

    if level not in ["entry", "mid", "senior", "lead", "executive"]:
        raise HTTPException(400, "Invalid experience level")

    # Parse resume
    resume_data = parse_resume(file)

    # Check format
    format_check = check_ats_format(resume_data)

    # Score with role+level context
    score = calculate_score(
        resume_data,
        role_id=role,
        level=level,
        job_description=jobDescription
    )

    return {
        "resume": resume_data,
        "score": score,
        "format_check": format_check,
        "role": role,
        "level": level
    }
```

**Rescore Endpoint:**
```python
@router.post("/score")
async def rescore_resume(request: ScoreRequest):
    # Requires role + level in request
    score = calculate_score(
        request.resume_data,
        role_id=request.role,
        level=request.level,
        job_description=request.jobDescription
    )

    return score
```

---

### 3. Data Flow

**Complete User Journey:**

1. **Landing Page**
   - User sees bold hero, clicks "Analyze Resume Free"

2. **Upload Flow**
   - Upload file (PDF/DOCX)
   - Select role (grouped dropdown, searchable)
   - Select level (5 buttons)
   - Optional: Paste job description
   - Click "Analyze Resume"

3. **Processing**
   - Parse with multi-strategy parser
   - Check ATS format compatibility
   - Score with role-specific criteria
   - If JD provided: keyword-heavy scoring
   - If no JD: role typical keywords

4. **Unified Editor**
   - Navigate to editor page
   - Editor (left): Pre-populated with parsed content
   - Score panel (right, sticky): Live score + suggestions
   - User edits resume
   - Clicks "Rescore Now"
   - Score updates in real-time (maintains role+level context)

5. **Save/Export**
   - User can save (if authenticated)
   - Export to PDF (future: with suggestions applied)

---

### 4. Testing Strategy

**Backend Tests:**
- [ ] Multi-strategy parser with 10+ resume formats
- [ ] Format checker accuracy (true/false positives)
- [ ] Role-specific scoring (each role + level combination)
- [ ] Keyword matching with/without JD
- [ ] API endpoints (role+level validation)
- [ ] All 44 existing tests still pass

**Frontend Tests:**
- [ ] Landing page renders and loads fast
- [ ] Role selection (all 19 roles accessible)
- [ ] Level selection (all 5 levels)
- [ ] Unified editor layout (responsive)
- [ ] Live rescore functionality
- [ ] Format checker display

**Integration Tests:**
- [ ] Complete flow: upload → parse → score → edit → rescore
- [ ] Role-specific scoring produces different results
- [ ] JD vs no-JD scoring differs appropriately
- [ ] Format checker catches bad formats

**Performance:**
- [ ] Landing page load: <2s
- [ ] Parse + score: <5s for typical resume
- [ ] Rescore: <2s
- [ ] Editor remains responsive during typing

---

### 5. Migration & Compatibility

**Backward Compatibility:**
- Existing resumes without role/level: Prompt user to select
- Old API calls without role/level: Return 400 with helpful error
- Database: Add optional role/level columns to resume table
- No data loss: All existing functionality preserved

**Migration Steps:**
1. Deploy backend with new parser + scorer
2. Update API to require role+level
3. Deploy new frontend
4. Update existing saved resumes: prompt users to add role+level
5. Monitor error rates and parsing success

---

## Implementation Phases

### Phase 1: Backend Foundation (Week 1)
- Multi-strategy parser
- Format checker
- Role taxonomy expansion (action verbs, weights, keywords)
- Role-specific scorer
- API updates
- Tests

### Phase 2: Frontend Overhaul (Week 1-2)
- Design system implementation
- Landing page
- Role/level selection flow
- Unified editor layout
- Score panel with suggestions
- Format checker display

### Phase 3: Integration & Polish (Week 2)
- End-to-end testing
- Performance optimization
- Bug fixes
- Documentation
- Deployment

---

## Success Metrics

**Quality Metrics:**
- Parse success rate: >95%
- Format checker accuracy: >90%
- Score consistency: <5% variance on rescore
- Test coverage: >80%

**UX Metrics:**
- Page load time: <2s
- Time to first score: <10s
- Editor responsiveness: <100ms input lag
- User completes flow: >70% completion rate

**Business Metrics:**
- Looks professional (subjective - user feedback)
- Competitive with Resume Worded/Jobscan (feature parity)
- Users find scoring accurate (feedback surveys)

---

## Risks & Mitigations

**Risk:** Multi-strategy parser increases complexity
- **Mitigation:** Extensive testing, fallback to existing parser if all fail

**Risk:** Role-specific scoring too complex
- **Mitigation:** Start with 3-5 roles, expand incrementally

**Risk:** Unified editor performance issues
- **Mitigation:** Debounce rescore, optimize React rendering

**Risk:** Users frustrated by required role selection
- **Mitigation:** Make selection fast (search, good UX), explain value

---

## Conclusion

This design transforms the ATS scorer into a production-ready, competitive tool that:
- **Looks professional** with modern teal/cyan design
- **Functions smoothly** with unified editor (no scrolling)
- **Scores accurately** with role-specific, ATS-focused logic
- **Parses reliably** with multi-strategy approach
- **Provides value** with format checker and detailed suggestions

The implementation maintains backward compatibility while delivering a quantum leap in quality and user experience.

**Next Steps:** Create detailed implementation plan and begin development.
