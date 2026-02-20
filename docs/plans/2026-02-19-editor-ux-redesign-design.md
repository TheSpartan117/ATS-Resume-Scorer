# Enhanced Resume Editor - UX Redesign

**Date:** February 19, 2026
**Status:** Approved - Ready for Implementation
**Approach:** Trial Run with Office Online Preview (Approach 1)

---

## Executive Summary

This design addresses critical UX issues with the current resume editor:
- ❌ **Problem 1:** Edits don't update the original CV PDF/DOCX
- ❌ **Problem 2:** Suggestions don't tell users exactly what to do
- ❌ **Problem 3:** Editor is hard to use - difficult to find where to make changes
- ❌ **Problem 4:** Re-score button missing or non-functional
- ❌ **Problem 5:** Poor user confidence - unclear if changes are applied

**Solution:** Complete editor redesign with:
- ✅ Live DOCX editing with Office Online preview
- ✅ Actionable suggestions with clear instructions and one-click fixes
- ✅ 70-30 layout with suggestions always visible
- ✅ Prominent re-score button that works
- ✅ Professional UX that builds user confidence

---

## Design Decisions

### Key User Requirements

**Approved Choices:**
1. **Editing Approach:** Option A - Live PDF/DOCX Updates
   - Changes immediately saved to DOCX backend
   - User downloads exactly what they see
   - Original preserved, working copy modified

2. **Suggestion Actions:** Option D - Comprehensive (All approaches)
   - Critical issues → One-click fix buttons
   - Content improvements → Before/After with replace option
   - Missing sections → Add templates with one click
   - Complex changes → Navigate to location with highlighting

3. **Layout:** Option A - Three-Panel with 70-30 ratio
   - Suggestions: 30% (always visible)
   - Main panel: 70% (tabbed: Rich Editor | Preview)
   - Maximum preview space for document clarity

4. **Re-scoring:** Option B - Manual Re-score Button
   - User-controlled re-scoring (not automatic)
   - Prominent button always visible
   - Builds confidence that changes are evaluated

5. **Suggestion Details:** Option B - Detailed with Full Context
   - Shows: severity, location, why it matters, action, example
   - Quick scanning with all needed context
   - No overwhelming step-by-step unless complex

6. **Fix Behavior:** Smart Hybrid
   - Missing content (phone, email) → Modal with input
   - Text changes → Navigate and highlight location
   - User always sees where change is applied

---

## Architecture Overview

### System Components

```
┌─────────────────────────────────────────────────────┐
│                    Frontend                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────┐ │
│  │ Suggestions  │  │ Rich Editor  │  │ Preview  │ │
│  │   Panel      │  │    Panel     │  │  Panel   │ │
│  │   (30%)      │  │    (70%)     │  │  (70%)   │ │
│  └──────────────┘  └──────────────┘  └──────────┘ │
│         ↓                  ↓                ↓       │
│    [API Calls to Backend]                          │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│                    Backend                          │
│  ┌──────────────────────────────────────────────┐  │
│  │         DOCX Template Manager                 │  │
│  │  - Stores working DOCX per session            │  │
│  │  - Section detection & editing                │  │
│  │  - Paragraph-level updates                    │  │
│  └──────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────┐  │
│  │         Suggestion Generator                  │  │
│  │  - Analyzes DOCX content                      │  │
│  │  - Maps issues to document locations          │  │
│  │  - Generates action buttons                   │  │
│  └──────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────┐  │
│  │         ATS Scorer                            │  │
│  │  - Re-scores on demand                        │  │
│  │  - Updates suggestions list                   │  │
│  └──────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

### Key Technologies

**Frontend:**
- React + TypeScript
- TipTap (rich text editor)
- Office Online API (Microsoft 365 viewer)
- Axios for API calls

**Backend:**
- Python FastAPI
- python-docx (DOCX manipulation)
- Existing ATS scorer services
- Session-based file storage

**Storage:**
- Session files: `backend/storage/sessions/{session_id}/`
  - `{session_id}_original.docx` (never modified)
  - `{session_id}_working.docx` (editable version)
  - `{session_id}_sections.json` (paragraph indices)

### Session Management

Each uploaded resume gets unique `session_id`:
- Original file preserved forever
- Working copy stores all edits
- Sections mapped to paragraph indices for navigation
- Session expires after 24 hours (configurable)
- Auto-refresh every 15 minutes to prevent timeout

---

## UI Layout & Components

### Main Layout (70-30 Split)

```
┌────────────────────────────────────────────────────────────────────────┐
│  Resume Editor - Session ID: abc123                    [Re-score] [⬇]  │
├──────────────────────────┬─────────────────────────────────────────────┤
│                          │                                             │
│   SUGGESTIONS (30%)      │      MAIN PANEL (70%)                       │
│                          │                                             │
│ ┌──────────────────────┐ │  ┌──────────────────────────────────────┐ │
│ │ 🎯 Score: 75/100     │ │  │ [Rich Editor] | [Preview]  (TABS)   │ │
│ │ Last scored: 2m ago  │ │  └──────────────────────────────────────┘ │
│ └──────────────────────┘ │                                             │
│                          │  ┌──────────────────────────────────────┐ │
│ ┌──────────────────────┐ │  │                                       │ │
│ │ CRITICAL (2)         │ │  │   [Rich Editor Content]               │ │
│ ├──────────────────────┤ │  │   OR                                  │ │
│ │ ❌ Missing phone     │ │  │   [Office Online Preview]             │ │
│ │ 📍 Contact section   │ │  │                                       │ │
│ │ 💡 ATS needs phone   │ │  │   (Fills 70% of screen)              │ │
│ │ [+ Add Phone]        │ │  │                                       │ │
│ │                      │ │  │                                       │ │
│ │ ❌ Missing LinkedIn  │ │  └──────────────────────────────────────┘ │
│ │ 📍 Contact section   │ │                                             │
│ │ [+ Add LinkedIn]     │ │                                             │
│ └──────────────────────┘ │                                             │
│                          │                                             │
│ ┌──────────────────────┐ │                                             │
│ │ WARNINGS (5)         │ │                                             │
│ ├──────────────────────┤ │                                             │
│ │ ⚠️ Weak action verb  │ │                                             │
│ │ 📍 Experience, L.15  │ │                                             │
│ │ 💡 Use "Led" not...  │ │                                             │
│ │ [Show Location]      │ │                                             │
│ └──────────────────────┘ │                                             │
│                          │                                             │
│ ┌──────────────────────┐ │                                             │
│ │ SUGGESTIONS (8)      │ │                                             │
│ │ (Collapsed)          │ │                                             │
│ └──────────────────────┘ │                                             │
└──────────────────────────┴─────────────────────────────────────────────┘
```

### Component Breakdown

#### 1. Suggestions Panel (30% width - Always visible)

**Features:**
- Fixed position, independently scrollable
- Groups: Critical → Warnings → Suggestions → Info
- Each group collapsible with count badges
- Current score prominently displayed at top
- "Re-score Resume" button (big, blue, top of panel)
- Progress indicator: "5 of 15 issues fixed"

**Suggestion Card Format:**
```
┌─────────────────────────────────────┐
│ ❌ [SEVERITY]: [Title]              │
│ 📍 Location: [Section, Line]       │
│ 💡 Why: [Brief explanation]        │
│ 📝 Example: [Sample or format]     │
│                                     │
│ Actions: [Button(s)]                │
└─────────────────────────────────────┘
```

#### 2. Main Panel (70% width - Tabbed)

**Tab 1: Rich Editor**
- TipTap editor with formatting toolbar
- Section-based editing (Contact, Experience, Education, Skills)
- Yellow highlight for "Navigate here" actions
- Real-time word count display
- Auto-saves changes to backend DOCX (debounced 2s)
- Save status indicator: "💾 Saving..." | "✓ Saved" | "❌ Error"

**Tab 2: Preview**
- Office Online embedded viewer (iframe)
- Shows live DOCX file
- Full page, minimal chrome
- Zoom controls (+/-)
- "Download PDF" / "Download DOCX" buttons
- Auto-refreshes when DOCX updates

#### 3. Top Bar

**Elements:**
- Session info (small, unobtrusive)
- **"Re-score Resume"** button (prominent, blue, always visible)
- Download dropdown: [PDF] [DOCX] [Original]
- "← Back to Results" link
- User menu (existing)

---

## Smart Suggestion System

### Suggestion Types & Behaviors

#### Type 1: Missing Content (Quick Add)

**Example:**
```
❌ CRITICAL: Missing phone number
📍 Location: Contact Information
💡 Why: ATS systems expect phone in contact
📝 Example: (555) 123-4567

Action: [+ Add Phone Number]
```

**Click Behavior:**
1. Modal pops up: "Add Phone Number"
2. Input field with format hint: `(___) ___-____`
3. User enters phone: `(555) 867-5309`
4. Click `[Add to Resume]`
5. Phone added to Contact section in DOCX
6. Suggestion marked ✅ Fixed
7. No tab switch (stays where user is)

**Applies to:**
- Missing phone, email, LinkedIn
- Missing address/location
- Missing skills section
- Missing professional summary

#### Type 2: Content Changes (Navigate & Highlight)

**Example:**
```
⚠️ WARNING: Weak action verb
📍 Location: Experience, Line 15
💡 Why: "Responsible for" is passive/weak
💪 Better: Use "Led", "Managed", "Drove"

❌ Current: "Responsible for managing team"
✅ Suggest: "Led cross-functional team of 8"

Actions: [Show Location] [Replace Text]
```

**[Show Location] Behavior:**
1. Switches to "Rich Editor" tab
2. Scrolls to Experience section, line 15
3. Highlights text in yellow: "Responsible for managing team"
4. Cursor placed at start of highlighted text
5. User can manually edit

**[Replace Text] Behavior:**
1. Shows confirmation modal: "Replace with suggested text?"
2. Shows before/after preview
3. Click `[Confirm Replace]`
4. Text automatically replaced in DOCX
5. Editor highlights new text (green flash animation)
6. Suggestion marked ✅ Fixed

**Applies to:**
- Weak action verbs
- Grammar errors
- Spelling mistakes
- Repetitive words
- Vague statements

#### Type 3: Missing Sections (Template Insert)

**Example:**
```
⚠️ WARNING: Missing Skills section
📍 Location: Should be after Experience
💡 Why: +10 ATS points with Skills listed
📝 Example: Technical + Soft skills

Action: [+ Add Skills Section]
```

**Click Behavior:**
1. Modal opens: "Add Skills Section"
2. Pre-filled template with examples:
   ```
   Skills
   - Technical Skills: [Your skills here]
   - Soft Skills: Communication, Leadership, Problem-solving
   ```
3. User can edit the template text
4. Click `[Add to Resume]`
5. New section inserted after Experience in DOCX
6. Switches to Rich Editor, scrolls to new section
7. Highlighted in green (brief animation)
8. Suggestion marked ✅ Fixed

**Applies to:**
- Missing sections (Skills, Summary, Certifications)
- Missing subsections (Projects, Awards, Publications)

#### Type 4: Formatting Issues (Navigate Only)

**Example:**
```
ℹ️ INFO: Inconsistent date format
📍 Location: Education, Line 42
💡 Why: Mix of "Jan 2020" & "1/20" formats
📝 Fix: Use consistent format throughout

Action: [Show Location]
```

**Click Behavior:**
1. Switches to Rich Editor tab
2. Scrolls to Education section, line 42
3. Highlights inconsistent dates in yellow
4. User manually fixes to consistent format
5. User clicks checkmark to mark as fixed

**Applies to:**
- Inconsistent formatting
- Spacing issues
- Font inconsistencies
- Bullet point alignment

### Suggestion State Management

**States:**
- `pending` - Not yet addressed
- `fixed` - User applied the fix
- `dismissed` - User chose to ignore

**Features:**
- Each suggestion has dismiss button (small X icon)
- "✅ Fixed" badges show completion
- Progress bar: "5 of 15 issues fixed (33%)"
- Dismissed suggestions can be un-dismissed
- Re-scoring refreshes all suggestions

---

## Data Flow & API Design

### Complete User Journey

#### 1. UPLOAD → RESULTS → CLICK "EDIT RESUME"

```
Frontend: GET /api/editor/session/{session_id}

Backend Response:
{
  "session_id": "abc123",
  "working_docx_url": "/api/files/abc123_working.docx",
  "office_viewer_url": "https://view.officeapps.live.com/...",
  "sections": [
    {"name": "Contact", "start_para": 0, "end_para": 5},
    {"name": "Experience", "start_para": 6, "end_para": 25},
    {"name": "Education", "start_para": 26, "end_para": 32}
  ],
  "current_score": {
    "overallScore": 75,
    "breakdown": {...}
  },
  "suggestions": [...]
}
```

#### 2. USER EDITS IN RICH EDITOR

```
Frontend:
- User types in TipTap editor
- After 2s of no typing (debounced)
- POST /api/editor/update-section

Request:
{
  "session_id": "abc123",
  "section": "Experience",
  "content": "<p>Led team of 8 engineers...</p>",
  "start_para": 6,
  "end_para": 10
}

Backend:
- Updates working DOCX file
- Preserves formatting
- Returns: {"success": true, "updated_url": "..."}
```

#### 3. USER CLICKS "RE-SCORE RESUME"

```
Frontend: POST /api/editor/rescore

Request:
{
  "session_id": "abc123"
}

Backend:
- Reads current working DOCX
- Parses content
- Runs ATS scorer
- Generates new suggestions with locations

Response:
{
  "score": {
    "overallScore": 82,
    "breakdown": {...}
  },
  "suggestions": [
    {
      "id": "sug_001",
      "type": "missing_content",
      "severity": "critical",
      "title": "Missing phone number",
      "description": "ATS systems expect phone in contact info",
      "location": {"section": "Contact", "line": null},
      "action": "add_phone",
      "example": "(555) 123-4567"
    },
    {
      "id": "sug_002",
      "type": "content_change",
      "severity": "warning",
      "title": "Weak action verb",
      "description": "Replace 'Responsible for' with stronger verb",
      "location": {"section": "Experience", "line": 15, "para_idx": 8},
      "current_text": "Responsible for managing team",
      "suggested_text": "Led cross-functional team",
      "action": "replace_text"
    }
  ]
}
```

#### 4. USER CLICKS [+ ADD PHONE] SUGGESTION

```
Frontend:
- Opens modal with input
- User enters: (555) 867-5309
- POST /api/editor/apply-suggestion

Request:
{
  "session_id": "abc123",
  "suggestion_id": "sug_001",
  "action": "add_phone",
  "value": "(555) 867-5309"
}

Backend:
- Inserts phone into Contact section of DOCX
- Marks suggestion as applied

Response:
{
  "success": true,
  "updated_section": "Contact",
  "content": "<p>Phone: (555) 867-5309</p>"
}
```

#### 5. USER CLICKS [SHOW LOCATION] SUGGESTION

```
Frontend only (no API call):
- Switch to "Rich Editor" tab
- Scroll to section based on suggestion.location
- Highlight paragraph using para_idx
- Yellow background on target text
- Cursor placed at start
```

#### 6. USER SWITCHES TO "PREVIEW" TAB

```
Frontend:
- Embeds Office Online viewer with iframe
- URL: office_viewer_url from initial load
- Office Online shows live DOCX
- Auto-refreshes when DOCX updates
```

#### 7. USER CLICKS "DOWNLOAD DOCX"

```
Frontend: GET /api/files/{session_id}_working.docx

Backend: Returns updated DOCX file with all edits
```

### New API Endpoints

```python
# Backend API Routes

POST /api/editor/session
"""
Creates editing session from uploaded resume
Input: resume_id or upload new file
Output: session_id, working DOCX URL, sections map, initial suggestions
"""

GET /api/editor/session/{session_id}
"""
Returns current session state
Output: score, suggestions, document structure, office viewer URL
"""

POST /api/editor/update-section
"""
Updates specific section in working DOCX
Input: session_id, section_name, content, para_indices
Output: success status, updated URL
"""

POST /api/editor/rescore
"""
Re-runs ATS scorer on current DOCX
Input: session_id
Output: new score + updated suggestions with locations
"""

POST /api/editor/apply-suggestion
"""
Applies suggestion action to DOCX
Input: session_id, suggestion_id, action_type, value
Output: success status, updated content
"""

GET /api/files/{session_id}_working.docx
"""
Downloads current working DOCX file
Output: DOCX file stream
"""

POST /api/editor/refresh-preview
"""
Refreshes Office Online preview URL
Input: session_id
Output: new office_viewer_url with fresh timestamp
"""
```

### Office Online Integration

```javascript
// Frontend: Office Online Viewer Setup

// Backend must provide publicly accessible DOCX URL
// Options for trial:
// 1. ngrok for local development
// 2. Temporary signed URL (if using S3/Azure)
// 3. Public endpoint with expiring token

const officeViewerUrl = `https://view.officeapps.live.com/op/embed.aspx?src=${encodeURIComponent(docxPublicUrl)}`;

<iframe
  src={officeViewerUrl}
  width="100%"
  height="100%"
  frameBorder="0"
  title="Resume Preview"
/>
```

---

## Error Handling & Edge Cases

### Critical Error Scenarios

#### 1. Office Online Viewer Fails

**Problem:** Office Online API unavailable or DOCX can't be viewed

**Fallback:**
- Show PDF preview instead (convert DOCX to PDF)
- Display message: "⚠️ Live preview unavailable, showing PDF version"
- All editing still works via Rich Editor
- User can still download DOCX
- Log error for investigation

#### 2. Session Expires

**Problem:** User leaves editor open for hours, session times out

**Handling:**
- Auto-refresh session every 15 minutes (silent)
- If session lost after 24h, show modal: "Session expired"
- Options: `[Reload Editor]` or `[Back to Results]`
- Working DOCX saved for 24 hours, can be recovered
- Show warning at 23 hours: "Session expires in 1 hour"

#### 3. DOCX Update Fails

**Problem:** Backend can't update DOCX file (permissions, corruption)

**Handling:**
- Show error toast: "❌ Failed to save changes"
- `[Try Again]` button available
- Changes kept in frontend (TipTap) until successful save
- After 3 failed attempts, offer: `[Export as HTML]`
- User can copy content and paste into their own editor

#### 4. Re-score Takes Too Long

**Problem:** Re-scoring backend takes >10 seconds

**Handling:**
- Show loading indicator: "🔄 Re-scoring... (5s)"
- Progress bar if possible
- Timeout after 30 seconds with message
- Show partial results if scorer returns early
- User can continue editing while scoring runs
- "Cancel Re-score" button appears after 10s

#### 5. Suggestion Action Fails

**Problem:** "Add Phone" button clicked but insert fails

**Handling:**
- Show error: "❌ Couldn't add phone number"
- `[Try Again]` button
- Fall back to: `[Show Location]` for manual edit
- Log error details for debugging
- Suggestion stays in pending state

#### 6. Invalid DOCX Structure

**Problem:** Uploaded resume has unusual DOCX structure

**Handling:**
- Section detector might fail to map paragraphs
- Show warning: "⚠️ Some sections couldn't be detected automatically"
- "Navigate" features disabled for unmapped sections
- Manual editing still works for all content
- Show "Edit Full Document" mode as fallback
- Suggestions work but without precise locations

### Edge Cases

#### 1. Multiple Browser Tabs

**Scenario:** User opens editor in 2 tabs

**Handling:**
- Each tab has same session_id
- Backend handles concurrent edits (last write wins)
- Show warning: "⚠️ Editor open in another tab"
- Option to `[Take Control]` (read-only mode for other tabs)
- Session lock for 5 minutes after last edit

#### 2. Very Large Resume (10+ pages)

**Scenario:** Resume is 15 pages long

**Handling:**
- Rich Editor might be slow
- Paginate sections (edit one section at a time)
- Preview tab works fine (Office Online handles large files)
- Suggestion navigation still works
- Show warning: "Large file - editing may be slower"

#### 3. No Suggestions Found

**Scenario:** Resume scores 95/100, almost perfect

**Handling:**
- Show success message: "🎉 Excellent resume! Only 2 minor suggestions"
- Hide empty suggestion categories
- Still show "Re-score" button (user might make changes)
- User can manually edit anyway
- Provide positive feedback

#### 4. Missing Original File

**Scenario:** User uploads HTML/text instead of DOCX

**Handling:**
- Create new DOCX from parsed content
- Show info: "ℹ️ Converted to DOCX format for editing"
- Template might be basic, but editable
- Suggestions work normally
- Preview shows converted DOCX

### User Experience Safeguards

**Auto-save Indicator:**
```javascript
<div className="editor-status">
  {saveStatus === 'saving' && '💾 Saving...'}
  {saveStatus === 'saved' && '✓ Saved 2 seconds ago'}
  {saveStatus === 'error' && '❌ Error saving - Click to retry'}
</div>
```

**File Versioning:**
- Backend keeps last 5 versions of working DOCX
- `{session_id}_working_v1.docx`
- `{session_id}_working_v2.docx`
- ...
- User can rollback if needed via dropdown

**Conflict Resolution:**
If frontend and backend out of sync:
- Show modal: "Your changes conflict with server"
- Options: `[Use My Version]` `[Use Server Version]` `[View Diff]`
- Most recent save wins by default
- User can manually resolve

### Performance Optimization

**1. Debounce Editor Changes**
- 2 second delay before API call
- Don't hit API on every keystroke
- Batch multiple changes into single update
- Show "Saving..." indicator during debounce

**2. Lazy Load Suggestions**
- Load Critical first (highest priority)
- Load Warnings/Suggestions on scroll
- Virtualize list for 100+ suggestions
- Only render visible suggestion cards

**3. Cache Office Online Embed**
- Don't reload iframe unnecessarily
- Refresh only when DOCX actually changes
- Use unique URL with timestamp to force refresh
- Preload preview when user hovers tab

**4. Optimize DOCX Operations**
- Use paragraph indices (fast lookups)
- Avoid full document rewrites
- Update only changed sections
- Keep document structure in memory

---

## Testing Strategy & Success Metrics

### Trial Run Success Criteria

For Approach 1 to be considered successful:

#### ✅ Must Have (Core Functionality)

1. **DOCX Editing Works**
   - User can edit text in Rich Editor
   - Changes save to backend DOCX file within 2 seconds
   - Downloaded DOCX reflects all edits correctly
   - Formatting is preserved (bold, italics, bullets)

2. **Office Online Preview Works**
   - DOCX renders in Office Online viewer
   - Updates visible within 5 seconds of switching to Preview tab
   - Zoom and navigation work properly
   - No authentication issues

3. **Suggestions Are Actionable**
   - "Add" buttons work for missing content (phone, email, etc.)
   - "Show Location" navigates to correct paragraph
   - "Replace" buttons update text correctly
   - At least 80% of suggestions are actionable
   - Users understand what action to take

4. **Re-score Functions**
   - Button triggers re-scoring
   - Score updates within 15 seconds
   - New suggestions appear after re-score
   - Completed fixes don't reappear in suggestions

#### ✅ Should Have (Good UX)

5. **Layout Is Usable**
   - 70-30 split displays properly on 1920x1080 screens
   - Tab switching works smoothly
   - Suggestions panel scrolls independently
   - Responsive on laptop screens (1366x768 minimum)

6. **Navigation Works**
   - Clicking "Show Location" highlights correct text in yellow
   - Switching tabs maintains scroll position
   - Highlighting is visible and helpful
   - User can find the text to change within 5 seconds

7. **Performance Acceptable**
   - Editor responds to typing in <500ms
   - DOCX updates complete in <3 seconds
   - Office Online loads in <5 seconds
   - Re-scoring completes in <15 seconds
   - No noticeable lag or freezing

#### ❌ Known Limitations for Trial

- Office Online may have rate limits (test with 10-20 resumes max)
- DOCX URL must be publicly accessible (use ngrok for local dev)
- Some complex DOCX formatting might not preserve perfectly
- Large files (>5MB) might be slow
- Table editing might not work in rich editor
- Images/charts editing not supported in trial

### Testing Plan

#### Phase 1: Technical Validation (Week 1)

**Test Cases:**
1. Upload sample resume → Create editing session ✓
2. Edit text in Rich Editor → Verify DOCX updates ✓
3. View in Office Online → Confirm rendering ✓
4. Click "Add Phone" → Verify insertion ✓
5. Click "Show Location" → Verify navigation ✓
6. Click "Replace Text" → Verify update ✓
7. Click "Re-score" → Verify new score ✓
8. Download DOCX → Verify all changes included ✓
9. Session timeout → Verify recovery ✓
10. Error scenarios → Verify fallbacks ✓

**Tools:**
- Manual testing with 5 different resume formats
- Browsers: Chrome, Safari, Firefox
- Network throttling: 3G to test performance
- Large file test: 10 page resume

**Success:** All 10 test cases pass with <3 retries each

#### Phase 2: User Experience Testing (Week 2)

**Test with 3-5 real users:**

Give them a resume with 10 known issues, ask them to:
1. Fix all issues using the editor
2. Re-score after making changes
3. Download the updated resume

**Measure:**
- Time to fix all 10 issues (target: <15 minutes)
- Number of suggestions successfully applied (target: >8/10)
- User confusion points via screen recording
- Overall satisfaction rating (1-10 scale)
- Net Promoter Score: "Would you recommend this editor?"

**Success Criteria:**
- Average satisfaction >7/10
- >80% of issues successfully fixed
- <5 minutes average to understand the interface
- Positive feedback on suggestion clarity

#### Phase 3: Decision Point

After Phase 2, evaluate results:

**✅ If Successful (>80% suggestions work, users rate >7/10):**
- Proceed with full Approach 1 implementation
- Plan production deployment with real Office 365 API
- Add polish and production features
- Estimate: 2-3 weeks for production-ready version

**❌ If Office Online Issues (rate limits, rendering problems):**
- Fall back to Approach 2 (PDF preview)
- Keep the suggestion system (works independently)
- Replace Office Online iframe with PDF viewer
- Estimate: 1 week to swap preview component

**❌ If Fundamental DOCX Editing Issues:**
- Reassess architecture completely
- Consider Approach 3 or hybrid solution
- Gather more user feedback
- Re-design if necessary

### Metrics to Track

**Analytics Events:**
```javascript
{
  "session_start": {
    "resume_format": "docx",
    "file_size_kb": 245,
    "initial_score": 67,
    "suggestion_count": 15
  },
  "suggestion_clicked": {
    "type": "add_phone",
    "success": true,
    "time_ms": 1234
  },
  "editor_edit": {
    "section": "Experience",
    "chars_changed": 45,
    "save_success": true,
    "save_time_ms": 890
  },
  "rescore_triggered": {
    "old_score": 67,
    "new_score": 75,
    "time_taken_ms": 8500,
    "suggestions_fixed": 5
  },
  "preview_loaded": {
    "method": "office_online",
    "load_time_ms": 3200,
    "success": true
  },
  "tab_switched": {
    "from": "editor",
    "to": "preview",
    "count": 5
  },
  "session_complete": {
    "total_edits": 12,
    "suggestions_applied": 8,
    "suggestions_dismissed": 2,
    "final_score": 82,
    "duration_minutes": 15,
    "downloaded": true
  }
}
```

**Key Metrics Dashboard:**
- Average session duration
- Suggestions applied rate
- Score improvement average
- Office Online load success rate
- Error rate by type
- User satisfaction scores

### Rollback Plan

If trial fails completely, we can:

1. **Keep the new suggestion system** - Works independently of editor
2. **Swap Office Online for PDF preview** - One component change (Approach 2)
3. **Keep the 70-30 layout** - Works with any preview method
4. **Keep the DOCX editing backend** - Reusable for other approaches
5. **Keep the new API endpoints** - Minimal changes needed

**Only the preview component needs changing** - 90% of development work is reusable.

---

## Implementation Phases

### Phase 1: Core Infrastructure (Week 1)

**Backend:**
- Session management system
- DOCX storage and versioning
- Update-section API endpoint
- Section detection service

**Frontend:**
- 70-30 layout shell
- Tabbed interface (Editor | Preview)
- Basic TipTap editor integration
- Suggestions panel component

**Deliverable:** Can edit text and see changes in DOCX file

### Phase 2: Suggestion System (Week 2)

**Backend:**
- Enhanced suggestion generator
- Map suggestions to locations
- Apply-suggestion API endpoint
- Re-score API endpoint

**Frontend:**
- Suggestion cards with all details
- Click handlers for all 4 types
- Modal for "Add" actions
- Navigate and highlight for "Show Location"

**Deliverable:** All suggestion types are actionable

### Phase 3: Office Online Integration (Week 3)

**Backend:**
- Public URL generation for DOCX
- Office Online URL builder
- Preview refresh endpoint

**Frontend:**
- Office Online iframe integration
- Auto-refresh on DOCX change
- Fallback to PDF on failure
- Download buttons

**Deliverable:** Live preview of DOCX working

### Phase 4: Polish & Testing (Week 4)

**All:**
- Error handling for all scenarios
- Performance optimization
- User testing and feedback
- Bug fixes and refinements

**Deliverable:** Production-ready trial version

---

## Technical Risks & Mitigation

### Risk 1: Office Online Rate Limits

**Risk:** Microsoft may limit free tier to X requests/day

**Impact:** High - core feature unavailable

**Mitigation:**
- Use enterprise Office 365 API ($5-20/mo)
- Implement caching (refresh only when DOCX changes)
- Fall back to PDF preview automatically
- Monitor usage and warn users at 80% limit

**Probability:** Medium | **Impact:** High | **Mitigation Cost:** Low

### Risk 2: DOCX Public URL Required

**Risk:** Office Online requires publicly accessible URL

**Impact:** High - won't work on localhost without workaround

**Mitigation:**
- Use ngrok for local development
- Use S3/Azure signed URLs for production
- Implement temporary public endpoint with short expiry
- Document setup clearly for developers

**Probability:** High | **Impact:** Medium | **Mitigation Cost:** Low

### Risk 3: DOCX Formatting Loss

**Risk:** Editing might lose complex formatting

**Impact:** Medium - user dissatisfaction

**Mitigation:**
- Only edit paragraph text, preserve styles
- Use paragraph indices, not full rewrites
- Test with diverse resume formats
- Show preview to user before download
- Keep original file always available

**Probability:** Medium | **Impact:** Medium | **Mitigation Cost:** Medium

### Risk 4: Performance with Large Files

**Risk:** 10+ page resumes might be slow

**Impact:** Medium - poor UX for some users

**Mitigation:**
- Paginate editing by section
- Lazy load suggestions
- Optimize DOCX operations
- Show file size warning upfront
- Consider file size limits

**Probability:** Low | **Impact:** Medium | **Mitigation Cost:** Low

### Risk 5: Browser Compatibility

**Risk:** Office Online might not work in all browsers

**Impact:** Medium - some users can't use feature

**Mitigation:**
- Test on Chrome, Safari, Firefox, Edge
- Detect browser and show compatibility warning
- Fallback to PDF preview for unsupported browsers
- Document browser requirements

**Probability:** Low | **Impact:** Medium | **Mitigation Cost:** Low

---

## Success Metrics

Trial is considered successful if:

✅ **Technical Success:**
- 90% of DOCX edits save correctly
- Office Online loads in <5 seconds 80% of the time
- Re-scoring works within 15 seconds
- <5% error rate on suggestion actions

✅ **User Success:**
- Average satisfaction score >7/10
- >80% of users fix 8+ out of 10 issues
- Users rate suggestions as "clear and actionable"
- <5 minutes to understand the interface

✅ **Business Success:**
- Users prefer new editor over old (A/B test)
- Resume download rate increases
- Time-to-completion decreases by >30%
- Positive user feedback/reviews

If these criteria are met → Proceed with full implementation

---

## Next Steps

1. **Design Approval** ✓ - This document
2. **Create Implementation Plan** - Use writing-plans skill
3. **Phase 1 Development** - Core infrastructure
4. **Internal Testing** - Validate technical functionality
5. **User Testing** - 3-5 users with real resumes
6. **Decision Point** - Continue or pivot to Approach 2
7. **Production Deployment** - If trial successful

---

## Appendix

### Related Documents

- `2026-02-19-split-view-editor-implementation.md` - Previous editor implementation
- `2026-02-19-template-based-editor-design.md` - Template system design
- `CODE_REVIEW_FIXES.md` - Recent bug fixes applied

### Open Questions

1. Office 365 API pricing - need to research exact costs
2. DOCX public URL strategy - S3 vs temporary endpoint?
3. Should we support PDF uploads? (currently DOCX only)
4. Session timeout duration - 24 hours optimal?

### Future Enhancements (Post-Trial)

- AI-powered suggestion generation
- Collaborative editing (multiple users)
- Template library with pre-made sections
- Real-time scoring (as you type)
- Mobile/tablet support
- Undo/redo with full history
- Comments and annotations

---

**Design Status:** ✅ **APPROVED - Ready for Implementation**

**Next Action:** Invoke `writing-plans` skill to create detailed implementation plan
