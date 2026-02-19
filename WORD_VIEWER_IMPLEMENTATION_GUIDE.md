# Word Document Viewer Implementation Guide

## Status: READY FOR IMPLEMENTATION (Requires Bash Access)

**Date:** 2026-02-19
**Prepared by:** Claude Opus 4.6

## Executive Summary

All components are created and ready. The implementation requires:
1. Installing `docx-preview` package
2. Storing the original DOCX file during upload
3. Integrating ResumeViewerTabs into ResumeEditor
4. Testing and verification

**Estimated time:** 1-2 hours

---

## Prerequisites

### Required Bash Commands

```bash
# 1. Install docx-preview
cd /Users/sabuj.mondal/ats-resume-scorer/frontend
npm install docx-preview

# 2. Verify installation
npm list docx-preview

# 3. Start dev server for testing
npm run dev

# 4. Build verification
npm run build
```

---

## Implementation Steps

### Step 1: Store Original File in localStorage (5 minutes)

The original DOCX file is lost after upload. We need to store it temporarily so DocxViewer can access it.

**File:** `/Users/sabuj.mondal/ats-resume-scorer/frontend/src/components/UploadPage.tsx`

**Modify the handleSubmit function** (around line 40-67):

```typescript
const handleSubmit = async (e: React.FormEvent) => {
  e.preventDefault()

  if (!selectedFile) {
    setError('Please select a file to upload')
    return
  }

  setIsUploading(true)
  setError(null)

  try {
    // *** NEW: Store original file in localStorage if it's a DOCX ***
    if (selectedFile.name.toLowerCase().endsWith('.docx')) {
      const fileData = await selectedFile.arrayBuffer()
      const base64 = btoa(String.fromCharCode(...new Uint8Array(fileData)))
      localStorage.setItem('uploaded-cv-file', base64)
      localStorage.setItem('uploaded-cv-filename', selectedFile.name)
      localStorage.setItem('uploaded-cv-type', selectedFile.type)
    }
    // *** END NEW CODE ***

    const result: UploadResponse = await uploadResume(
      selectedFile,
      jobDescription || undefined,
      selectedRole || undefined,
      selectedLevel || undefined,
      undefined  // industry parameter kept for backward compatibility
    )

    // Navigate to results page with data
    navigate('/results', { state: { result } })
  } catch (err) {
    setError(err instanceof Error ? err.message : 'Failed to upload resume')
  } finally {
    setIsUploading(false)
  }
}
```

---

### Step 2: Retrieve Original File in EditorPage (10 minutes)

**File:** `/Users/sabuj.mondal/ats-resume-scorer/frontend/src/components/EditorPage.tsx`

**Add state and effect to retrieve file** (around line 141-150):

```typescript
// Add this state near other states (after line 150)
const [originalDocxFile, setOriginalDocxFile] = useState<File | null>(null)

// Add this effect after the existing useEffects (around line 160)
useEffect(() => {
  // Retrieve original DOCX file from localStorage
  const base64Data = localStorage.getItem('uploaded-cv-file')
  const filename = localStorage.getItem('uploaded-cv-filename')
  const filetype = localStorage.getItem('uploaded-cv-type')

  if (base64Data && filename) {
    try {
      // Decode base64 to binary
      const binaryString = atob(base64Data)
      const bytes = new Uint8Array(binaryString.length)
      for (let i = 0; i < binaryString.length; i++) {
        bytes[i] = binaryString.charCodeAt(i)
      }

      // Create File object
      const file = new File(
        [bytes],
        filename,
        { type: filetype || 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' }
      )

      setOriginalDocxFile(file)
      console.log('Original DOCX file loaded:', filename)
    } catch (err) {
      console.error('Failed to load original file:', err)
    }
  }
}, [])
```

**Update ResumeEditor props** (around line 380-387):

```typescript
<ResumeEditor
  value={editorContent}
  onChange={handleEditorChange}
  currentScore={currentScore}
  isRescoring={isRescoring}
  wordCount={wordCount}
  onRescore={performRescore}
  originalDocxFile={originalDocxFile}  // *** ADD THIS LINE ***
/>
```

---

### Step 3: Update ResumeEditor to Use ResumeViewerTabs (15 minutes)

**File:** `/Users/sabuj.mondal/ats-resume-scorer/frontend/src/components/ResumeEditor.tsx`

**Replace the entire file with:**

```typescript
/**
 * Enhanced ResumeEditor with Tabbed Viewer (Original/Edit/Office Online)
 */
import React, { useRef, useCallback } from 'react';
import type { ScoreResult } from '../types/resume';
import IssuesList, { type AppliedSuggestion } from './IssuesList';
import ResumeViewerTabs from './ResumeViewerTabs';

interface ResumeEditorProps {
  value: string;
  onChange: (html: string) => void;
  currentScore: ScoreResult | null;
  isRescoring: boolean;
  wordCount: number;
  onRescore: () => void;
  originalDocxFile?: File | null;  // NEW PROP
}

export const ResumeEditor: React.FC<ResumeEditorProps> = ({
  value,
  onChange,
  currentScore,
  isRescoring: _isRescoring,
  wordCount: _wordCount,
  onRescore: _onRescore,
  originalDocxFile,  // NEW
}) => {
  const editorRef = useRef<any>(null);

  // Store editor instance when ready
  const handleEditorReady = useCallback((editor: any) => {
    editorRef.current = editor;
    console.log('TiptapEditor: Editor ready');
  }, []);

  // Handle applying suggestions from IssuesList
  const handleApplySuggestion = useCallback((suggestion: AppliedSuggestion) => {
    const editor = editorRef.current;
    if (!editor) {
      console.warn('Editor not ready yet');
      return;
    }

    try {
      if (suggestion.action === 'insert' && suggestion.content) {
        // Insert template content at the end of the document
        editor.chain().focus().setContent(
          editor.getHTML() + suggestion.content
        ).run();

        console.log('Applied suggestion:', suggestion.description);
      } else if (suggestion.action === 'replace' && suggestion.searchText && suggestion.replaceText) {
        // Replace text content
        const currentHtml = editor.getHTML();
        const newHtml = currentHtml.replace(suggestion.searchText, suggestion.replaceText);

        if (newHtml !== currentHtml) {
          editor.chain().focus().setContent(newHtml).run();
          console.log('Replaced text:', suggestion.searchText, '->', suggestion.replaceText);
        }
      } else if (suggestion.action === 'format') {
        // Apply formatting improvements (simplified for now)
        console.log('Formatting applied:', suggestion.description);
      }
    } catch (error) {
      console.error('Error applying suggestion:', error);
    }
  }, []);

  return (
    <div className="flex flex-col lg:flex-row gap-4 min-h-screen w-full">
      {/* LEFT PANEL - Tabbed Resume Viewer (70%) */}
      <div className="lg:w-[70%] w-full">
        <ResumeViewerTabs
          originalDocx={originalDocxFile || null}
          htmlContent={value}
          onHtmlChange={onChange}
          onEditorReady={handleEditorReady}
        />
      </div>

      {/* RIGHT PANEL - Enhanced Suggestions Panel (30%) */}
      <div className="lg:w-[30%] w-full flex flex-col bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden">
        {/* Mode Indicator */}
        {currentScore && (
          <div className="bg-gradient-to-r from-blue-600 to-indigo-600 px-4 py-2">
            <div className="flex items-center justify-between">
              <span className="text-white text-sm font-semibold">
                {currentScore.mode === 'ats_simulation' ? '🎯 ATS Mode' : '📝 Coach Mode'}
              </span>
              <span className="text-white text-xs opacity-90">Smart Suggestions</span>
            </div>
          </div>
        )}

        {/* Enhanced IssuesList with Tabs and Apply Actions */}
        <div className="flex-1 overflow-hidden p-4">
          {currentScore && (
            <IssuesList
              issues={currentScore.issues}
              overallScore={currentScore.overallScore}
              onApplySuggestion={handleApplySuggestion}
            />
          )}
        </div>
      </div>
    </div>
  );
};
```

---

### Step 4: Add CSS for docx-preview (5 minutes)

**File:** `/Users/sabuj.mondal/ats-resume-scorer/frontend/src/index.css`

**Add these styles at the end of the file:**

```css
/* DOCX Preview Styles - docx-preview library support */
.docx-wrapper {
  background: white;
  padding: 1in;
  font-family: 'Calibri', 'Arial', sans-serif;
  font-size: 11pt;
  color: #000;
  line-height: 1.15;
}

.docx-wrapper section.docx {
  margin-bottom: 0;
}

/* Preserve table styling from Word */
.docx-wrapper table {
  border-collapse: collapse;
  margin: 10pt 0;
  width: 100%;
}

.docx-wrapper table td,
.docx-wrapper table th {
  padding: 4pt 6pt;
  vertical-align: top;
  line-height: 1.2;
}

.docx-wrapper table p {
  margin: 0;
}

/* Word-style list spacing */
.docx-wrapper ul,
.docx-wrapper ol {
  margin: 6pt 0;
  padding-left: 0.5in;
}

.docx-wrapper li {
  margin: 3pt 0;
  line-height: 1.15;
}

/* Headings */
.docx-wrapper h1 {
  font-size: 20pt;
  font-weight: bold;
  margin: 12pt 0 6pt 0;
}

.docx-wrapper h2 {
  font-size: 16pt;
  font-weight: bold;
  margin: 10pt 0 5pt 0;
}

.docx-wrapper h3 {
  font-size: 14pt;
  font-weight: bold;
  margin: 8pt 0 4pt 0;
}

/* Paragraphs */
.docx-wrapper p {
  margin: 6pt 0;
  line-height: 1.15;
}
```

---

## Testing Checklist

Once npm packages are installed, follow this test plan:

### Phase 1: Basic Functionality

```bash
# Start dev server
npm run dev
```

1. **Upload Test**
   - Go to http://localhost:5173
   - Upload a DOCX resume
   - Verify localStorage contains 'uploaded-cv-file'
   - Check browser console for "Original DOCX file loaded: [filename]"

2. **Tab Navigation Test**
   - Navigate to editor page
   - Verify 3 tabs appear: "Original Document", "Edit Mode", "Office Online" (if available)
   - Click each tab - should switch without errors
   - Check browser console for no React errors

3. **Original Document Tab**
   - Should show the DOCX with 85-95% accuracy
   - Tables should render
   - Formatting should be preserved
   - Check loading spinner appears briefly

4. **Edit Mode Tab**
   - Should show TipTap editor with HTML content
   - Test editing - changes should work
   - Toolbar should be functional

5. **Right Panel (Suggestions)**
   - Should display alongside tabs
   - ATS Mode indicator should show
   - Suggestions should list properly

### Phase 2: Edge Cases

1. **Non-DOCX Files**
   - Upload a PDF
   - Original Document tab should show "No document loaded"
   - Edit Mode should still work

2. **Large Files**
   - Upload a large DOCX (5MB+)
   - Check loading performance
   - Verify rendering completes

3. **Complex Formatting**
   - Upload a resume with tables, images, columns
   - Check rendering accuracy
   - Note any formatting issues

4. **Tab Switching During Load**
   - Upload file
   - Quickly switch tabs while loading
   - Should not crash

### Phase 3: Production Build

```bash
# Build for production
npm run build

# Preview build
npm run preview
```

- Verify no build errors
- Test in production build
- Check bundle size increase (should be ~200KB for docx-preview)

---

## Known Issues and Limitations

### Expected Issues

1. **Font Substitution**
   - docx-preview may substitute fonts not available in browser
   - Expected: 85-95% accuracy (as documented)

2. **Advanced Word Features**
   - Some advanced features (SmartArt, embedded objects) may not render
   - Fallback: Users can use Office Online tab

3. **localStorage Limits**
   - localStorage has ~5MB limit
   - Very large files may fail to store
   - Solution: Implement backend storage if needed

4. **Performance**
   - Large DOCX files (10+ pages) may take 2-3 seconds to render
   - Add loading spinner (already implemented)

### Not Issues (Expected Behavior)

- Office Online tab only appears if public URL available
- PDF files won't show in Original Document tab (by design)
- Slight formatting differences vs. Word (acceptable at 85-95%)

---

## Rollback Plan

If issues occur, rollback is simple:

1. **Restore original ResumeEditor.tsx:**
   - Simply revert to TipTap-only version
   - Remove `originalDocxFile` prop

2. **Remove localStorage code:**
   - Remove from UploadPage.tsx handleSubmit

3. **Uninstall package (if needed):**
   ```bash
   npm uninstall docx-preview
   ```

---

## Performance Metrics

Expected performance after implementation:

- **First load:** +200KB bundle size (docx-preview library)
- **Render time:** < 1 second for typical 1-2 page resumes
- **Memory usage:** +5-10MB while viewing DOCX
- **Tab switch:** < 100ms

---

## Architecture Diagram

```
User uploads DOCX
       ↓
UploadPage stores in localStorage
       ↓
Navigate to EditorPage
       ↓
EditorPage retrieves from localStorage
       ↓
Pass to ResumeEditor as prop
       ↓
ResumeEditor → ResumeViewerTabs
       ↓
    ┌──────────┴─────────┬──────────────┐
    ↓                    ↓              ↓
Original Document    Edit Mode    Office Online
(DocxViewer)      (TipTapEditor)  (OfficeViewer)
    ↓                    ↓              ↓
docx-preview lib     Existing      Microsoft API
```

---

## Files Modified Summary

### New Files (Already Created)
- `/Users/sabuj.mondal/ats-resume-scorer/frontend/src/components/DocxViewer.tsx` ✅
- `/Users/sabuj.mondal/ats-resume-scorer/frontend/src/components/ResumeViewerTabs.tsx` ✅
- `/Users/sabuj.mondal/ats-resume-scorer/frontend/src/components/DocxViewerDemo.tsx` ✅

### Files to Modify
1. `/Users/sabuj.mondal/ats-resume-scorer/frontend/package.json` (npm install)
2. `/Users/sabuj.mondal/ats-resume-scorer/frontend/src/components/UploadPage.tsx` (store file)
3. `/Users/sabuj.mondal/ats-resume-scorer/frontend/src/components/EditorPage.tsx` (retrieve file)
4. `/Users/sabuj.mondal/ats-resume-scorer/frontend/src/components/ResumeEditor.tsx` (integrate tabs)
5. `/Users/sabuj.mondal/ats-resume-scorer/frontend/src/index.css` (add styles)

---

## Success Criteria

- ✅ docx-preview package installed
- ✅ ResumeViewerTabs integrated
- ✅ Three tabs working (Original/Edit/Office Online)
- ✅ Original document displays with 85-95% accuracy
- ✅ Edit mode functional with TipTap
- ✅ Suggestions panel visible
- ✅ No console errors
- ✅ Smooth tab switching
- ✅ Dev server running without issues
- ✅ Production build succeeds

---

## Next Steps After Implementation

1. **User Testing**
   - Upload various resume formats
   - Test with different DOCX versions
   - Gather user feedback on accuracy

2. **Optional Enhancements**
   - Add "Download Original" button
   - Implement backend file storage (replace localStorage)
   - Add zoom controls for DOCX viewer
   - Export edited content back to DOCX

3. **Documentation**
   - Update user guide
   - Add tooltips explaining tabs
   - Create video tutorial

---

## Contact & Support

If issues arise during implementation:
1. Check browser console for errors
2. Verify all files modified correctly
3. Ensure docx-preview installed: `npm list docx-preview`
4. Check localStorage contains file: DevTools → Application → Local Storage

---

**Implementation Status:** READY
**Next Action:** Run npm install docx-preview
**Estimated Completion:** 1-2 hours after Bash access granted
