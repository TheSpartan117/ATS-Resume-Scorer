# Resume Editor - User Guide

## Overview

The Resume Editor provides an interactive interface for improving your resume based on ATS (Applicant Tracking System) scoring and suggestions. The editor features a 70-30 split layout with suggestions on the left and editing/preview on the right.

## Getting Started

### Accessing the Editor

1. Upload your resume (DOCX format) on the main page
2. Click **"Edit Resume"** after scoring completes
3. The editor opens with your resume and improvement suggestions

### Editor Layout

```
┌────────────────────────────────────────────────────────┐
│  Header: Session ID | Re-score | Download              │
├──────────────┬─────────────────────────────────────────┤
│ Suggestions  │  Rich Editor / Preview Tabs             │
│ Panel (30%)  │  (70%)                                  │
│              │                                         │
│ 🎯 Score     │  [Rich Editor] | [Preview]             │
│ ✅ Fixed     │                                         │
│ ❌ Critical  │  Your resume content                    │
│ ⚠️  Warnings │  appears here                           │
│ 💡 Info      │                                         │
└──────────────┴─────────────────────────────────────────┘
```

## Features

### 1. Suggestions Panel (Left - 30%)

The left panel displays your current ATS score and improvement suggestions grouped by severity:

#### Score Display
- **Overall Score**: 0-100 scale
- **Last Scored**: Timestamp of last scoring
- **Progress**: Shows fixed vs. pending suggestions

#### Suggestion Groups
1. **CRITICAL** (Red ❌): Must-fix issues
   - Missing contact information
   - Missing required sections
   - Major ATS compatibility problems

2. **WARNINGS** (Yellow ⚠️): Should-fix issues
   - Weak action verbs
   - Missing keywords
   - Formatting inconsistencies

3. **SUGGESTIONS** (Blue 💡): Nice-to-have improvements
   - Additional sections to add
   - Content enhancements

4. **INFO** (Gray ℹ️): Minor improvements
   - Formatting tips
   - Style suggestions

### 2. Main Panel (Right - 70%)

#### Rich Editor Tab
- **WYSIWYG Editing**: Edit your resume with rich text formatting
- **Formatting Toolbar**:
  - Bold, Italic, Underline
  - Bullet lists, numbered lists
  - Text alignment (left, center, right)
  - Undo/Redo
- **Section-Based**: Edit specific resume sections
- **Auto-Save**: Changes save automatically after 2 seconds

#### Preview Tab
- **Office Online Preview**: See your resume as it will appear in DOCX format
- **Live Updates**: Preview refreshes when you save changes
- **Zoom Controls**: Adjust preview size
- **Refresh Button**: Manually refresh preview

### 3. Header Actions

#### Re-score Button
- Click to re-analyze your resume after making changes
- Updates suggestions based on current content
- Shows new score and remaining issues

#### Download Button
- Downloads your edited resume as DOCX
- Preserves all formatting
- Includes all your changes

## Using Suggestions

### Types of Suggestion Actions

#### 1. Add Missing Content
**Example**: "Missing phone number"

**Actions**:
- Click **[+ Add Phone]** button
- Modal opens with input field
- Enter phone number: `(555) 123-4567`
- Click **Save**
- Phone number added to Contact section automatically

#### 2. Replace Text
**Example**: "Weak action verb - 'Responsible for'"

**Shows**:
- **Current**: "Responsible for managing team"
- **Suggested**: "Led cross-functional team"

**Actions**:
- Click **[Replace Text]** button
- Text automatically replaced in document
- Editor scrolls to location

#### 3. Add Missing Section
**Example**: "Missing Skills section"

**Actions**:
- Click **[+ Add Skills Section]** button
- Modal opens with section template
- Edit template content
- Click **Add to Resume**
- Section inserted at recommended location

#### 4. Show Location
**Example**: "Inconsistent date format"

**Actions**:
- Click **[Show Location]** button
- Editor tab opens
- Scrolls to problem location
- Text highlighted in yellow
- Manually fix the issue

## Workflow

### Typical Editing Session

1. **Review Score**: Check your initial ATS score (e.g., 75/100)

2. **Address Critical Issues First**:
   - Click on critical suggestions
   - Use one-click fixes where available
   - Verify changes in Preview tab

3. **Fix Warnings**:
   - Replace weak action verbs
   - Add missing keywords
   - Fix formatting issues

4. **Manual Edits** (Rich Editor tab):
   - Improve content quality
   - Add specific achievements
   - Tailor to job description

5. **Re-score**:
   - Click **Re-score Resume** button
   - Review new score and suggestions
   - Repeat until satisfied

6. **Download**:
   - Click **Download DOCX** button
   - Save final version

### Tips for Best Results

**Start with Critical Issues**:
- Address all red (critical) items first
- These have the biggest impact on ATS score

**Use Suggested Text**:
- Suggestion text is ATS-optimized
- Can be edited after applying

**Re-score Frequently**:
- Check impact of your changes
- Catch new issues early

**Preview Before Downloading**:
- Verify formatting looks correct
- Check for layout issues

**Save Progress**:
- Download working versions periodically
- Original file is preserved

## Keyboard Shortcuts

### Rich Editor
- **Ctrl/Cmd + B**: Bold
- **Ctrl/Cmd + I**: Italic
- **Ctrl/Cmd + U**: Underline
- **Ctrl/Cmd + Z**: Undo
- **Ctrl/Cmd + Shift + Z**: Redo

### Navigation
- **Tab**: Switch between tabs
- **Escape**: Close modals

## Troubleshooting

### Preview Not Loading

**Symptom**: Preview tab shows "Loading..." indefinitely

**Solutions**:
1. Click the **Refresh** button
2. Check internet connection (Office Online requires connection)
3. Switch to Rich Editor tab and back
4. Try re-scoring

### Changes Not Saving

**Symptom**: Edits disappear after switching tabs

**Solutions**:
1. Wait 2 seconds after typing (auto-save delay)
2. Manually click outside editor before switching tabs
3. Re-score to ensure changes are captured

### Score Not Improving

**Symptom**: Score stays the same after fixes

**Issue**: Need to re-score manually

**Solution**: Click **Re-score Resume** button to recalculate

### Download Issues

**Symptom**: Downloaded file doesn't open or is corrupted

**Solutions**:
1. Ensure changes are saved (wait 2 seconds)
2. Re-score before downloading
3. Try downloading again
4. Check file extension is `.docx`

## Understanding Suggestions

### Suggestion Anatomy

Each suggestion card shows:

```
❌ CRITICAL: Missing phone number
📍 Location: Contact section
💡 Why: ATS systems expect phone number in contact info
📝 Example: (555) 123-4567

[+ Add Phone]  [Dismiss]
```

**Components**:
- **Severity Icon**: ❌ Critical, ⚠️ Warning, 💡 Suggestion, ℹ️ Info
- **Title**: Brief description of issue
- **Location**: Where in resume (section, line number)
- **Why**: Explanation of why this matters
- **Example**: Sample of correct format
- **Actions**: Buttons to fix or dismiss

### Dismissing Suggestions

If a suggestion doesn't apply to you:
1. Click the **[Dismiss]** button (small X)
2. Suggestion is hidden but not deleted
3. Will reappear if you re-score and issue still exists

## API Endpoints Reference

### For Developers

The editor uses these API endpoints:

**GET** `/api/editor/session/{sessionId}`
- Loads session data, score, and suggestions

**POST** `/api/editor/apply-suggestion`
- Applies suggestion action (add_phone, replace_text, etc.)

**POST** `/api/editor/update-section`
- Updates section content from Rich Editor

**POST** `/api/editor/rescore`
- Re-scores resume and generates new suggestions

**GET** `/api/downloads/{sessionId}_working.docx`
- Downloads edited DOCX file

## Session Management

### How Sessions Work

1. **Session Creation**: Created when you click "Edit Resume"
2. **Session ID**: UUID like `abc123-def456-...`
3. **Files Stored**:
   - `{sessionId}_original.docx` (never modified)
   - `{sessionId}_working.docx` (your edits)
4. **Expiration**: 24 hours (configurable)

### Resuming Sessions

Currently, editor doesn't support resuming. To continue editing:
1. Download your current version
2. Re-upload to create new session
3. (Future feature: Save and resume sessions)

## Best Practices

### Content Quality

**Do**:
- Use strong action verbs (Led, Architected, Delivered)
- Include metrics (increased by 30%, saved $50K)
- Tailor to specific job posting
- Use industry keywords

**Don't**:
- Use passive voice ("Responsible for...")
- Include personal pronouns (I, me, my)
- Use generic phrases ("team player")
- Repeat same words/phrases

### Formatting

**Do**:
- Use consistent date formats (Jan 2020 or 01/2020)
- Keep bullet points parallel
- Use standard section names
- Maintain clean hierarchy

**Don't**:
- Mix font styles/sizes excessively
- Use tables or columns (ATS issues)
- Include graphics/images
- Use headers/footers for important info

### ATS Optimization

**Key Sections** (in order):
1. Contact Information
2. Professional Summary
3. Experience
4. Education
5. Skills
6. Certifications (if applicable)

**Must-Have Contact Info**:
- Full name
- Phone number
- Email address
- LinkedIn profile (recommended)
- Location (City, State)

## FAQ

### Q: Can I edit multiple resumes at once?
**A**: No, each editor session handles one resume. Download and start a new session for another resume.

### Q: Will my changes affect the original file?
**A**: No, the original is preserved. You download a new version with your changes.

### Q: How is the score calculated?
**A**: Score based on 5 categories:
- Keywords (35 points)
- Red Flags (20 points)
- Experience (20 points)
- Formatting (20 points)
- Contact Info (5 points)

### Q: Can I undo changes?
**A**: Use Ctrl/Cmd+Z in Rich Editor. The original file is always preserved.

### Q: What file formats are supported?
**A**: Currently DOCX only. PDF support planned for future release.

### Q: Do I need an internet connection?
**A**: Yes, for the Office Online preview. Rich Editor works offline.

## Support

### Getting Help

- **Issues**: Report at GitHub repository
- **Feature Requests**: Open GitHub issue with "enhancement" label
- **Documentation**: See `/docs` folder for technical docs

### Known Limitations

1. **PDF not supported**: Only DOCX format currently
2. **No offline mode**: Requires internet for preview
3. **Session not persistent**: Download to save progress
4. **Complex formatting**: Tables/columns may have issues

## Version History

### v1.0.0 (Current)
- 70-30 split layout with suggestions panel
- TipTap rich text editor
- Office Online preview integration
- 4 types of actionable suggestions
- Manual re-scoring
- Session-based editing
- DOCX download

### Planned Features (Future)
- PDF support
- Session persistence and resuming
- Collaborative editing
- Template library
- AI-powered content suggestions
- Mobile responsive design

---

**For technical documentation, see:**
- `/docs/plans/2026-02-19-editor-ux-redesign-design.md` (Design document)
- `/docs/plans/2026-02-19-enhanced-editor-ux-implementation.md` (Implementation plan)
- `backend/api/editor.py` (API endpoints)
- `frontend/src/pages/EditorPage.tsx` (Main component)
