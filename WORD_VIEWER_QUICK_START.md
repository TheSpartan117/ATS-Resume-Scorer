# Quick Start - Word Viewer Implementation

**Time Required:** 90 minutes
**Prerequisites:** Bash access

---

## Step 1: Install Package (2 minutes)

```bash
cd /Users/sabuj.mondal/ats-resume-scorer/frontend
npm install docx-preview
npm list docx-preview  # Verify installation
```

---

## Step 2: Update UploadPage.tsx (5 minutes)

**File:** `/Users/sabuj.mondal/ats-resume-scorer/frontend/src/components/UploadPage.tsx`

**Find line 51** (inside handleSubmit function, after `try {`):

**Add this code:**

```typescript
// Store original file in localStorage if it's a DOCX
if (selectedFile.name.toLowerCase().endsWith('.docx')) {
  const fileData = await selectedFile.arrayBuffer()
  const base64 = btoa(String.fromCharCode(...new Uint8Array(fileData)))
  localStorage.setItem('uploaded-cv-file', base64)
  localStorage.setItem('uploaded-cv-filename', selectedFile.name)
  localStorage.setItem('uploaded-cv-type', selectedFile.type)
}
```

---

## Step 3: Update EditorPage.tsx (10 minutes)

**File:** `/Users/sabuj.mondal/ats-resume-scorer/frontend/src/components/EditorPage.tsx`

**Step 3.1 - Add state (line 150):**

```typescript
const [originalDocxFile, setOriginalDocxFile] = useState<File | null>(null)
```

**Step 3.2 - Add effect (after existing useEffects, around line 160):**

```typescript
useEffect(() => {
  // Retrieve original DOCX file from localStorage
  const base64Data = localStorage.getItem('uploaded-cv-file')
  const filename = localStorage.getItem('uploaded-cv-filename')
  const filetype = localStorage.getItem('uploaded-cv-type')

  if (base64Data && filename) {
    try {
      const binaryString = atob(base64Data)
      const bytes = new Uint8Array(binaryString.length)
      for (let i = 0; i < binaryString.length; i++) {
        bytes[i] = binaryString.charCodeAt(i)
      }
      const file = new File([bytes], filename, {
        type: filetype || 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
      })
      setOriginalDocxFile(file)
      console.log('Original DOCX file loaded:', filename)
    } catch (err) {
      console.error('Failed to load original file:', err)
    }
  }
}, [])
```

**Step 3.3 - Update ResumeEditor props (line 380):**

```typescript
<ResumeEditor
  value={editorContent}
  onChange={handleEditorChange}
  currentScore={currentScore}
  isRescoring={isRescoring}
  wordCount={wordCount}
  onRescore={performRescore}
  originalDocxFile={originalDocxFile}  // ADD THIS LINE
/>
```

---

## Step 4: Replace ResumeEditor.tsx (10 minutes)

**File:** `/Users/sabuj.mondal/ats-resume-scorer/frontend/src/components/ResumeEditor.tsx`

**Replace entire file content with:**

```typescript
/**
 * Enhanced ResumeEditor with Tabbed Viewer
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
  originalDocxFile?: File | null;
}

export const ResumeEditor: React.FC<ResumeEditorProps> = ({
  value,
  onChange,
  currentScore,
  isRescoring: _isRescoring,
  wordCount: _wordCount,
  onRescore: _onRescore,
  originalDocxFile,
}) => {
  const editorRef = useRef<any>(null);

  const handleEditorReady = useCallback((editor: any) => {
    editorRef.current = editor;
    console.log('TiptapEditor: Editor ready');
  }, []);

  const handleApplySuggestion = useCallback((suggestion: AppliedSuggestion) => {
    const editor = editorRef.current;
    if (!editor) {
      console.warn('Editor not ready yet');
      return;
    }

    try {
      if (suggestion.action === 'insert' && suggestion.content) {
        editor.chain().focus().setContent(
          editor.getHTML() + suggestion.content
        ).run();
        console.log('Applied suggestion:', suggestion.description);
      } else if (suggestion.action === 'replace' && suggestion.searchText && suggestion.replaceText) {
        const currentHtml = editor.getHTML();
        const newHtml = currentHtml.replace(suggestion.searchText, suggestion.replaceText);
        if (newHtml !== currentHtml) {
          editor.chain().focus().setContent(newHtml).run();
          console.log('Replaced text:', suggestion.searchText, '->', suggestion.replaceText);
        }
      } else if (suggestion.action === 'format') {
        console.log('Formatting applied:', suggestion.description);
      }
    } catch (error) {
      console.error('Error applying suggestion:', error);
    }
  }, []);

  return (
    <div className="flex flex-col lg:flex-row gap-4 min-h-screen w-full">
      {/* LEFT: Tabbed Viewer (70%) */}
      <div className="lg:w-[70%] w-full">
        <ResumeViewerTabs
          originalDocx={originalDocxFile || null}
          htmlContent={value}
          onHtmlChange={onChange}
          onEditorReady={handleEditorReady}
        />
      </div>

      {/* RIGHT: Suggestions Panel (30%) */}
      <div className="lg:w-[30%] w-full flex flex-col bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden">
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

## Step 5: Add CSS (5 minutes)

**File:** `/Users/sabuj.mondal/ats-resume-scorer/frontend/src/index.css`

**Add at the end of the file:**

```css
/* DOCX Preview Styles */
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

.docx-wrapper ul,
.docx-wrapper ol {
  margin: 6pt 0;
  padding-left: 0.5in;
}

.docx-wrapper li {
  margin: 3pt 0;
  line-height: 1.15;
}

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

.docx-wrapper p {
  margin: 6pt 0;
  line-height: 1.15;
}
```

---

## Step 6: Test (30 minutes)

```bash
# Start dev server
npm run dev
```

### Test Checklist

**Basic Tests:**
1. Go to http://localhost:5173
2. Upload a DOCX file
3. Click "Get My ATS Score"
4. Verify editor page loads
5. Check 3 tabs appear: "Original Document", "Edit Mode", "Office Online"
6. Click "Original Document" tab
7. Verify DOCX renders (may take 1-2 seconds)
8. Click "Edit Mode" tab
9. Verify TipTap editor works
10. Check suggestions panel on right side
11. Switch tabs multiple times - should be smooth

**Edge Cases:**
12. Upload PDF - Original tab should say "No document loaded"
13. Upload large DOCX (5MB+) - check loading spinner
14. Rapid tab switching - should not crash

**Console Check:**
15. Open browser DevTools (F12)
16. Check Console tab - should see "Original DOCX file loaded: [filename]"
17. No red errors should appear

---

## Step 7: Build Test (5 minutes)

```bash
npm run build
```

- Should complete without errors
- Check for warnings
- Bundle size should increase by ~200KB (acceptable)

---

## Step 8: Verify Success ✅

**Success Criteria:**

- ✅ docx-preview installed
- ✅ Original Document tab shows DOCX
- ✅ Edit Mode tab shows TipTap editor
- ✅ Suggestions panel visible on right
- ✅ Tab switching works smoothly
- ✅ No console errors
- ✅ Build succeeds

**If all ✅ → Implementation complete!**

---

## Troubleshooting

### Issue: "Cannot find module 'docx-preview'"

**Solution:**
```bash
npm install docx-preview
npm run dev  # Restart dev server
```

### Issue: "Original DOCX file loaded" not in console

**Solution:**
- Check UploadPage.tsx - localStorage code added?
- Check EditorPage.tsx - useEffect added?
- Try uploading file again

### Issue: DOCX not rendering

**Solution:**
- Check browser console for errors
- Verify file is actually DOCX (not renamed PDF)
- Try smaller file (< 5MB)
- Check if docx-preview CSS loaded (inspect element)

### Issue: Tabs not showing

**Solution:**
- Verify ResumeViewerTabs imported in ResumeEditor.tsx
- Check for React errors in console
- Restart dev server

### Issue: Build fails

**Solution:**
```bash
# Clear cache and rebuild
rm -rf node_modules/.vite
npm run build
```

---

## Rollback (If Needed)

```bash
# Revert changes
git checkout HEAD -- src/components/ResumeEditor.tsx
git checkout HEAD -- src/components/EditorPage.tsx
git checkout HEAD -- src/components/UploadPage.tsx
git checkout HEAD -- src/index.css

# Uninstall package
npm uninstall docx-preview

# Restart
npm run dev
```

---

## Next Steps After Success

1. **User Testing**
   - Test with various DOCX files
   - Gather feedback on accuracy

2. **Documentation**
   - Update user guide
   - Add tooltips

3. **Optional Enhancements**
   - Backend storage (replace localStorage)
   - Zoom controls
   - Export to DOCX

---

## Help

- **Full Guide:** `WORD_VIEWER_IMPLEMENTATION_GUIDE.md`
- **Status Report:** `IMPLEMENTATION_STATUS.md`
- **Components:** `/frontend/src/components/DocxViewer.tsx`, `ResumeViewerTabs.tsx`

**Good luck! The implementation should take ~90 minutes.**
