# Template-Based Resume Editor Design

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a template-preserving resume editor where users edit structured text on the left while seeing a pixel-perfect preview on the right, with suggestions shown in a navigable carousel.

**Architecture:** DOCX-based template system with dynamic section detection, Microsoft Office Online viewer for preview, and enhanced suggestion display.

**Tech Stack:** FastAPI (backend), React + TypeScript (frontend), python-docx (template manipulation), Office Online Viewer (preview), existing scorer services

---

## 1. Overall Architecture

### System Flow

1. **Upload Phase:**
   - User uploads DOCX/PDF resume
   - Backend stores original DOCX as template in `/storage/templates/{session_id}_original.docx`
   - Dynamically detects sections (no hardcoded section names)
   - Extracts text content per section
   - Creates working copy for editing: `/storage/templates/{session_id}_working.docx`
   - Makes working copy publicly accessible via signed URL
   - Returns: sessionId, detected sections, preview URL, initial score

2. **Editor View:**
   - **Top Bar (80px):** Compact suggestion carousel with score, issue counts, prev/next navigation
   - **Left 50%:** Dynamic section editors (collapsible textareas)
   - **Right 50%:** Microsoft Office Online viewer showing live DOCX preview

3. **Edit Flow:**
   - User types in section textarea
   - Debounced update (500ms)
   - Backend replaces specific paragraphs in working DOCX
   - Preview URL refreshed with timestamp
   - Office viewer reloads showing updated document

4. **Download:**
   - User downloads edited DOCX directly (preserves 100% formatting)
   - Optional: Convert to PDF using existing docx_to_pdf service

### Key Benefits

- **100% Format Preservation:** Original DOCX template maintains all styling, colors, layouts, images
- **Flexible:** Works with any CV format (one-column, two-column, tables, text boxes)
- **No Conversion Overhead:** Direct DOCX editing, no HTML/PDF conversion loop
- **Zero Cost:** Microsoft Office Online viewer is free for embedding

---

## 2. Component Details

### Backend Components

#### 2.1 Section Detector Service (`services/section_detector.py`)

**Purpose:** Dynamically detect sections from any DOCX format

**Detection Strategy:**
- Analyze paragraph styles: "Heading 1", "Heading 2", "Title", "Subtitle"
- Detect by font properties: Bold text + font size ≥ 14pt
- Pattern matching: ALL CAPS text on separate line
- Table headers: Bold text in first row/column
- Text box analysis: Extract from shape elements

**Output Format:**
```python
[
    {
        "title": "Professional Experience",  # As written in CV
        "content": "Full text content...",
        "section_id": "section_1",
        "start_para_idx": 5,
        "end_para_idx": 12,
        "is_in_table": False,
        "table_cell_ref": None
    },
    ...
]
```

**Edge Cases:**
- No clear headings: Fall back to paragraph-level sections ("Paragraph 1", "Paragraph 2")
- Multi-column layouts: Process column by column
- Tables: Detect section titles in cells
- Nested structures: Handle text boxes within tables

#### 2.2 DOCX Template Manager (`services/docx_template_manager.py`)

**Purpose:** Update specific sections while preserving all formatting

**Key Functions:**
```python
class DocxTemplateManager:
    def update_section(self, session_id, section_id, new_content):
        """Replace text at specific paragraph range"""

    def get_preview_url(self, session_id):
        """Generate publicly accessible signed URL"""

    def cleanup_expired_sessions(self):
        """Delete files older than 24 hours"""
```

**Update Strategy:**
- Load working DOCX
- Locate paragraphs [start_para_idx:end_para_idx]
- Delete old paragraphs
- Insert new text preserving:
  - Font family, size, color
  - Bold, italic, underline
  - Bullet/numbering styles
  - Line spacing
  - Paragraph alignment
- Save updated DOCX
- Return new preview URL with timestamp

**Complex Layouts:**
- Tables: Update specific cell content
- Text boxes: Update shape text
- Multi-column: Preserve column structure

#### 2.3 Preview Service (`api/preview.py`)

**Endpoints:**

```python
@router.get("/api/preview/{session_id}.docx")
async def get_preview_docx(session_id: str):
    """Serve working DOCX for Office Online viewer"""
    # Verify session exists
    # Return DOCX file with public access headers
    # CORS: Allow office.com domains

@router.post("/api/preview/update")
async def update_preview(request: UpdateRequest):
    """Update specific section and regenerate preview"""
    # Validate session_id, section_id
    # Update DOCX via template manager
    # Return new preview URL with timestamp
```

**Signed URL Strategy:**
- Generate: `https://yourserver.com/api/preview/{session_id}.docx?token={signed_token}&expires={timestamp}`
- Token expires in 2 hours
- Clean up expired tokens via background job

### Frontend Components

#### 2.4 Top Bar - Suggestion Carousel

**Component:** `SuggestionCarousel.tsx`

**Layout (80px height):**
```
Row 1: [Score Badge] [Issue Counters] [Navigation] [Re-score Button]
Row 2: [Current Suggestion Detail with actionable items]
```

**Props:**
```typescript
interface SuggestionCarouselProps {
  score: number;
  suggestions: DetailedSuggestion[];
  onRescore: () => void;
  onSuggestionClick: (sectionId?: string) => void;
}

interface DetailedSuggestion {
  id: string;
  severity: 'critical' | 'warning' | 'suggestion' | 'info';
  title: string;
  description: string;
  actionable: {
    current: string;
    target: string;
    items: string[];
  };
  affectedSection?: string;
}
```

**Features:**
- Prev/Next navigation through all suggestions
- Index display: "1/15"
- Click suggestion → highlight affected section in left panel
- Color-coded by severity
- Auto-collapse on scroll (sticky header)

#### 2.5 Section Editor (`SectionEditor.tsx`)

**Layout:**
```tsx
<div className="w-1/2 overflow-y-auto p-4 bg-gray-50">
  {sections.map(section => (
    <Collapsible
      key={section.section_id}
      title={section.title}
      icon={getIcon(section.title)}
      defaultOpen={true}
    >
      <textarea
        value={section.content}
        onChange={(e) => handleEdit(section.section_id, e.target.value)}
        className="w-full min-h-32 p-3 border rounded"
        placeholder={`Edit ${section.title}...`}
      />
    </Collapsible>
  ))}
</div>
```

**Features:**
- Dynamic section list (no hardcoded sections)
- Icon detection: Match icons to common section names (briefcase for Experience, graduation cap for Education)
- Debounced updates: 500ms after typing stops
- Auto-save indicator: "Saving..." → "Saved ✓"
- Character count per section
- Expand/collapse all button

#### 2.6 Office Viewer (`OfficeViewer.tsx`)

**Component:**
```tsx
<div className="w-1/2 border-l">
  <iframe
    src={`https://view.officeapps.live.com/op/embed.aspx?src=${encodeURIComponent(publicDocxUrl)}`}
    width="100%"
    height="100%"
    frameBorder="0"
  />
  {isUpdating && (
    <div className="absolute inset-0 bg-white/80 flex items-center justify-center">
      <Spinner /> Updating preview...
    </div>
  )}
</div>
```

**Update Strategy:**
- On edit: Show loading overlay
- Update iframe src with `?v=timestamp` to force refresh
- Wait for iframe load event
- Hide loading overlay

**Fallback:**
- If Office viewer fails to load: Show error message
- Provide download button: "Download to view in Word"

---

## 3. Data Flow & API Design

### Flow 1: Upload & Initialize

```
Client                    Backend
  │                         │
  ├─ POST /api/upload ─────►│
  │  (file: DOCX/PDF)       │
  │                         ├─ Store original DOCX
  │                         ├─ Convert PDF→DOCX if needed
  │                         ├─ Detect sections dynamically
  │                         ├─ Create working copy
  │                         ├─ Generate signed URL
  │                         ├─ Calculate initial score
  │                         │
  │◄─ Response ─────────────┤
  │  {                      │
  │    sessionId,           │
  │    sections: [...],     │
  │    previewUrl,          │
  │    score: {...}         │
  │  }                      │
  │                         │
  ├─ Render Editor ────────►│
  │  - Left: Section forms  │
  │  - Right: Office viewer │
```

### Flow 2: Edit Section

```
Client                    Backend
  │                         │
  ├─ User types ───────────►│
  │  (debounced 500ms)      │
  │                         │
  ├─ POST /preview/update ─►│
  │  {                      │
  │    sessionId,           │
  │    sectionId,           │
  │    newContent           │
  │  }                      │
  │                         ├─ Load working DOCX
  │                         ├─ Update specific paragraphs
  │                         ├─ Save DOCX
  │                         ├─ Generate new signed URL
  │                         │
  │◄─ Response ─────────────┤
  │  {                      │
  │    success: true,       │
  │    previewUrl: "...?v=timestamp"
  │  }                      │
  │                         │
  ├─ Update iframe src ────►│
  │  Office viewer reloads  │
```

### Flow 3: Download

```
Client                    Backend
  │                         │
  ├─ Click Download DOCX ──►│
  │                         │
  ├─ GET /download/{session}.docx
  │                         ├─ Return working DOCX file
  │◄─ File download ────────┤
  │                         │
  │  OR                     │
  │                         │
  ├─ Click Download PDF ───►│
  │                         │
  ├─ GET /download/{session}.pdf
  │                         ├─ Convert DOCX → PDF
  │◄─ File download ────────┤
```

### API Endpoints Summary

| Endpoint | Method | Purpose | Request | Response |
|----------|--------|---------|---------|----------|
| `/api/upload` | POST | Upload & initialize | DOCX/PDF file | sessionId, sections, previewUrl, score |
| `/api/preview/{sessionId}.docx` | GET | Serve working DOCX | - | DOCX file with CORS headers |
| `/api/preview/update` | POST | Update section | sessionId, sectionId, content | success, new previewUrl |
| `/api/download/{sessionId}.docx` | GET | Download edited DOCX | - | DOCX file |
| `/api/download/{sessionId}.pdf` | GET | Download as PDF | - | PDF file |
| `/api/rescore` | POST | Re-score with edits | sessionId | Updated score with detailed suggestions |

---

## 4. Error Handling & Edge Cases

### 4.1 PDF Upload Handling
- **Problem:** User uploads PDF (not directly editable)
- **Solution:** Auto-convert using `pdf2docx` (already installed)
- **Fallback:** If conversion fails or quality is poor:
  - Show warning: "For best results, upload original DOCX"
  - Allow text extraction but mention formatting may not be preserved perfectly

### 4.2 Section Detection Failures
- **Problem:** CV has no clear headings (plain text resume)
- **Solution:** Fall back to paragraph-level editing
  - Show: "Paragraph 1", "Paragraph 2", etc.
  - User can still edit, updates replace entire paragraphs

### 4.3 Complex Layouts
- **Tables:** Detect section titles in table cells, update cell content
- **Multi-column:** Process columns sequentially, maintain column structure
- **Text boxes:** Extract and update shape text elements
- **Images:** Preserve all images, don't allow editing through this interface
- **Headers/Footers:** Preserve, don't show in editor (typically contain page numbers)

### 4.4 Office Viewer Issues
- **Problem:** Requires publicly accessible URL
- **Solution:**
  - Development: Use ngrok or local tunnel for testing
  - Production: Ensure server has public IP/domain
  - Alternative: Generate signed URLs with 2-hour expiry
- **Fallback:** If viewer fails, show "Download to edit in Word" button

### 4.5 Preview Refresh
- **Race condition:** User types fast, multiple updates in flight
- **Solution:** Cancel previous update request when new one starts
- **Loading state:** Show spinner overlay during update
- **Error handling:** If update fails, retry once; if fails again, show error toast

### 4.6 Session Management
- **Storage:** SQLite DB or JSON file storing:
  ```python
  {
    "session_id": "abc123",
    "original_path": "/storage/templates/abc123_original.docx",
    "working_path": "/storage/templates/abc123_working.docx",
    "created_at": "2026-02-19T10:00:00Z",
    "last_accessed": "2026-02-19T12:30:00Z"
  }
  ```
- **Cleanup:** Background cron job deletes files older than 24 hours
- **Concurrent edits:** Single user per session (no collaboration)

### 4.7 Download Formats
- **Primary:** DOCX (edited template with all formatting)
- **Secondary:** PDF (convert using existing `docx_to_pdf` service)
- **Filename:** `{original_filename}_edited.docx` or `_edited.pdf`

---

## 5. Enhanced Suggestion System

### Backend: Structured Suggestions

**Modify Scorer Services** to return detailed, actionable suggestions instead of plain text.

**New Suggestion Format:**
```python
{
    "title": "Missing Keywords",
    "severity": "warning",
    "description": "Add these 5 keywords to improve ATS score",
    "actionable": {
        "current": "12/20 keywords matched (60%)",
        "target": "16/20 keywords (80%)",
        "items": ["python", "docker", "kubernetes", "terraform", "aws"],
        "present_items": ["javascript", "react", "node.js"]  # Show what they have
    },
    "affected_section": "Experience",  # Highlight this section
    "category": "keywords"
}
```

**Example Suggestions:**

1. **Missing Keywords:**
```json
{
  "title": "Missing Role Keywords",
  "severity": "critical",
  "description": "Your resume is missing key technical skills for this role",
  "actionable": {
    "current": "8/15 required keywords (53%)",
    "target": "12/15 keywords (80%)",
    "items": ["python", "docker", "kubernetes", "aws", "terraform"],
    "present_items": ["javascript", "react", "typescript"]
  },
  "affected_section": "Technical Skills"
}
```

2. **Length Issue:**
```json
{
  "title": "Resume Too Short",
  "severity": "warning",
  "description": "Resume should be 400-600 words for mid-level roles",
  "actionable": {
    "current": "285 words",
    "target": "400-600 words",
    "items": ["Add 2-3 more achievements per job", "Quantify your impact with metrics"]
  },
  "affected_section": "Experience"
}
```

3. **Missing Quantification:**
```json
{
  "title": "Add Measurable Results",
  "severity": "suggestion",
  "description": "Resumes with metrics get 40% more responses",
  "actionable": {
    "current": "2 metrics found",
    "target": "5-8 metrics",
    "items": [
      "Add percentages (e.g., 'Increased sales by 30%')",
      "Add scale (e.g., 'Managed team of 5')",
      "Add timeframes (e.g., 'Reduced bugs by 50% in 3 months')"
    ]
  },
  "affected_section": "Experience"
}
```

### Frontend: Suggestion Carousel

**Navigation:**
- Sort by severity: Critical → Warning → Suggestion → Info
- Current index: "1/15"
- Prev/Next buttons
- Keyboard shortcuts: ← → arrow keys

**Display Format:**
```
┌─────────────────────────────────────────────────────────────────┐
│ [75/100 🟡] │ 🚨 2 │ ⚠️ 5 │ 💡 8 │ [←] 3/15 [→] │ [Re-score]  │
├─────────────────────────────────────────────────────────────────┤
│ ⚠️ Missing Role Keywords                                        │
│ Your resume is missing key technical skills for this role       │
│ • Missing: python, docker, kubernetes, aws, terraform           │
│ • ✓ Present: javascript, react, typescript                     │
│ Current: 8/15 (53%) → Target: 12/15 (80%)                      │
│ [View in Experience section →]                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Interaction:**
- Click suggestion → Scroll left panel to "Experience" section
- Highlight affected section with yellow border for 2 seconds
- User can immediately start editing

**Empty State:**
- No critical/warning issues: "✅ Excellent! Your resume looks great"
- Only show info/suggestions for further improvement

---

## 6. Implementation Notes

### Technology Stack

**Backend:**
- FastAPI (existing)
- python-docx (DOCX manipulation)
- pdf2docx (PDF conversion)
- Existing scorer services (enhanced with structured suggestions)
- SQLite for session storage (or JSON file)

**Frontend:**
- React + TypeScript (existing)
- Tailwind CSS (styling)
- Microsoft Office Online Viewer (embedded iframe)
- React hooks for state management

**Storage:**
- Local filesystem: `/storage/templates/`
- Session metadata: SQLite or JSON
- Cleanup: Cron job (celery or simple scheduler)

### Dependencies (Already Installed)
- ✅ python-docx
- ✅ pdf2docx
- ✅ mammoth (not needed for this approach)
- ✅ reportlab (for PDF generation)
- ✅ PyMuPDF (PDF handling)

### Performance Considerations

1. **DOCX Updates:** ~100-300ms per section update (acceptable with debounce)
2. **Office Viewer Refresh:** ~500ms-1s (show loading indicator)
3. **PDF Conversion:** ~1-2s for download (async, show progress)
4. **Session Cleanup:** Run every hour, delete files >24h old

### Security Considerations

1. **Signed URLs:** Prevent unauthorized access to user documents
2. **File Validation:** Check DOCX/PDF structure before processing
3. **Path Traversal:** Sanitize session_id, prevent directory traversal
4. **File Size Limits:** Max 10MB upload (existing)
5. **CORS:** Allow office.com for viewer embedding

---

## 7. Testing Strategy

### Unit Tests
- Section detector: Various CV formats (one-column, two-column, tables)
- DOCX updater: Preserve formatting after text replacement
- Suggestion formatter: Structured output validation

### Integration Tests
- Upload DOCX → Edit sections → Download → Verify formatting preserved
- Upload PDF → Convert → Edit → Download
- Concurrent edits: Multiple sections updated rapidly

### Manual Testing Scenarios
1. **Simple CV:** One-column, clear headings
2. **Complex CV:** Two-column, tables, colored backgrounds, images
3. **Plain CV:** No headings, paragraph-based
4. **PDF CV:** Converted from PDF, verify quality
5. **Edge cases:** Very short CV (1 page), very long CV (5 pages)

### User Acceptance Criteria
- ✅ Left side shows editable text from original CV
- ✅ Right side shows pixel-perfect preview
- ✅ Edits in left update preview in <2 seconds
- ✅ Downloaded DOCX maintains 100% original formatting
- ✅ Suggestions show specific, actionable improvements
- ✅ Works with varied CV formats (not just template-based)

---

## 8. Migration from Current Editor

### Current State
- Multiple editor components: ResumeEditorLive, ResumeEditorSimple, etc.
- HTML-based editing (loses formatting)
- No true WYSIWYG preview

### Migration Plan
1. Keep existing upload flow (`/api/upload`)
2. Add new session-based flow (`/api/upload-template`)
3. Create new route: `/editor-template/{sessionId}` (new template-based editor)
4. Keep old route: `/editor/{sessionId}` (legacy HTML editor)
5. Add toggle: "Try new editor" button on results page
6. Deprecate old editors after 2 weeks of testing

### Rollback Plan
- If template editor has issues, redirect to legacy editor
- Maintain both for 1 month minimum
- User feedback will determine full migration

---

## Success Metrics

1. **Format Preservation:** 100% of original formatting maintained in downloads
2. **Edit Performance:** <2 seconds from edit to preview update
3. **User Satisfaction:** Users prefer template editor over HTML editor
4. **Compatibility:** Works with 95%+ of uploaded resumes (various formats)
5. **Actionability:** Users can act on 80%+ of suggestions directly

---

## Future Enhancements (Out of Scope)

- Real-time collaboration (multiple users editing same resume)
- Version history (track changes over time)
- AI-powered content suggestions (not just formatting feedback)
- Mobile editing support
- Offline editing mode
- Template library (user selects from pre-made templates)

---

## Conclusion

This design provides a **template-based editing experience** that:
- ✅ Preserves 100% of original formatting
- ✅ Works with any CV format (dynamic section detection)
- ✅ Provides pixel-perfect preview using Office Online
- ✅ Shows detailed, actionable suggestions
- ✅ Zero-cost solution (no paid services)
- ✅ Leverages existing backend infrastructure

The system is flexible enough to handle varied CV formats while maintaining the exact look and feel of the original document.
