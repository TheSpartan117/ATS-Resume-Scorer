# Installation Checklist - Word Document Viewer

## ✅ Pre-Installation Verification

- [x] Analysis document created: `WORD_VIEWER_ANALYSIS.md`
- [x] Implementation guide created: `IMPLEMENTATION_GUIDE.md`
- [x] README created: `WORD_VIEWER_README.md`
- [x] Components created:
  - [x] `frontend/src/components/DocxViewer.tsx`
  - [x] `frontend/src/components/ResumeViewerTabs.tsx`
  - [x] `frontend/src/components/DocxViewerDemo.tsx`

---

## 🚀 Installation Steps

### Step 1: Install NPM Package ⏱️ 2 minutes

```bash
cd /Users/sabuj.mondal/ats-resume-scorer/frontend
npm install docx-preview@latest
```

**Expected output:**
```
added 1 package, and audited X packages in Xs
found 0 vulnerabilities
```

**Verify installation:**
```bash
npm list docx-preview
```

Should show:
```
ats-resume-scorer-frontend@0.0.0
└── docx-preview@2.x.x
```

---

### Step 2: Update package.json ⏱️ 1 minute

Your `package.json` should now include:

```json
{
  "dependencies": {
    "@tailwindcss/typography": "^0.5.19",
    "@tiptap/extension-color": "^3.19.0",
    "@tiptap/extension-placeholder": "^3.19.0",
    "@tiptap/extension-text-align": "^3.19.0",
    "@tiptap/extension-text-style": "^3.19.0",
    "@tiptap/extension-underline": "^3.19.0",
    "@tiptap/pm": "^3.19.0",
    "@tiptap/react": "^3.19.0",
    "@tiptap/starter-kit": "^3.19.0",
    "axios": "^1.13.5",
    "docx-preview": "^2.x.x",  // ← NEW LINE
    "mammoth": "^1.11.0",
    "react": "^19.2.0",
    "react-dom": "^19.2.0",
    "react-router-dom": "^7.13.0"
  }
}
```

---

### Step 3: Verify Components Exist ⏱️ 1 minute

Check that all component files are present:

```bash
ls -la /Users/sabuj.mondal/ats-resume-scorer/frontend/src/components/ | grep -E "(DocxViewer|ResumeViewerTabs)"
```

**Expected output:**
```
DocxViewer.tsx
DocxViewerDemo.tsx
ResumeViewerTabs.tsx
```

---

### Step 4: Test Import (Optional) ⏱️ 2 minutes

Create a temporary test file to verify imports work:

```typescript
// frontend/src/test-viewer.tsx
import DocxViewer from './components/DocxViewer';
import ResumeViewerTabs from './components/ResumeViewerTabs';
import { renderAsync } from 'docx-preview';

console.log('✅ All imports successful');
console.log('DocxViewer:', DocxViewer);
console.log('ResumeViewerTabs:', ResumeViewerTabs);
console.log('renderAsync:', renderAsync);
```

Run TypeScript compiler to check:
```bash
cd /Users/sabuj.mondal/ats-resume-scorer/frontend
npx tsc --noEmit
```

**Expected:** No errors related to docx-preview or new components.

---

### Step 5: Start Development Server ⏱️ 1 minute

```bash
cd /Users/sabuj.mondal/ats-resume-scorer/frontend
npm run dev
```

**Expected output:**
```
VITE v7.x.x  ready in XXX ms

➜  Local:   http://localhost:5173/
➜  Network: use --host to expose
```

---

### Step 6: Test Demo Component (Optional) ⏱️ 5 minutes

Add a test route to see the demo:

1. Edit `frontend/src/App.tsx`:

```typescript
import DocxViewerDemo from './components/DocxViewerDemo'

function App() {
  return (
    <ErrorBoundary>
      <AuthProvider>
        <Routes>
          <Route path="/" element={<UploadPage />} />
          <Route path="/results" element={<ResultsPage />} />
          <Route path="/editor" element={<EditorPage />} />
          <Route path="/my-resumes" element={<SavedResumesPage />} />
          <Route path="/demo" element={<DocxViewerDemo />} />  {/* NEW */}
        </Routes>
      </AuthProvider>
    </ErrorBoundary>
  )
}
```

2. Visit `http://localhost:5173/demo`
3. Upload a DOCX file
4. Test viewer functionality

---

### Step 7: Integration into ResumeEditor ⏱️ 15 minutes

Follow the detailed instructions in `IMPLEMENTATION_GUIDE.md` Step 3.

**Quick integration snippet:**

```typescript
// In frontend/src/components/ResumeEditor.tsx

import ResumeViewerTabs from './ResumeViewerTabs';

interface ResumeEditorProps {
  value: string;
  onChange: (html: string) => void;
  currentScore: ScoreResult | null;
  originalFile?: File;  // ADD THIS
  previewUrl?: string;  // ADD THIS
  // ... other props
}

export const ResumeEditor: React.FC<ResumeEditorProps> = ({
  value,
  onChange,
  currentScore,
  originalFile,    // ADD THIS
  previewUrl,      // ADD THIS
  // ... other props
}) => {
  return (
    <div className="flex flex-col lg:flex-row gap-4 min-h-screen w-full">
      <div className="lg:w-[70%] w-full">
        {originalFile ? (
          <ResumeViewerTabs
            originalDocx={originalFile}
            htmlContent={value}
            onHtmlChange={onChange}
            previewUrl={previewUrl}
          />
        ) : (
          <TiptapEditor content={value} onChange={onChange} />
        )}
      </div>
      {/* ... rest of component */}
    </div>
  );
};
```

---

### Step 8: Update Upload Flow ⏱️ 10 minutes

Ensure original file is passed through navigation state:

```typescript
// In UploadPage.tsx or wherever upload happens

const handleSubmit = async (e: React.FormEvent) => {
  e.preventDefault();

  if (!selectedFile) return;

  try {
    const result = await uploadResume(selectedFile, ...);

    navigate('/results', {
      state: {
        result,
        originalFile: selectedFile,  // ADD THIS
      }
    });
  } catch (err) {
    // handle error
  }
};
```

---

## 🧪 Testing Checklist

### Basic Tests (5 minutes)

- [ ] Development server starts without errors
- [ ] No console errors about missing modules
- [ ] Can import components successfully
- [ ] TypeScript compilation passes

### Component Tests (10 minutes)

- [ ] DocxViewer renders a DOCX file
- [ ] Loading spinner appears during render
- [ ] Error message shows for invalid files
- [ ] Retry button works after error

### Integration Tests (15 minutes)

- [ ] ResumeViewerTabs shows all 3 tabs
- [ ] Can switch between tabs
- [ ] Original Document tab shows DOCX
- [ ] Edit Mode tab shows TipTap editor
- [ ] Changes in Edit Mode don't affect Original
- [ ] Suggestions panel still works

### Real-World Tests (20 minutes)

Test with these document types:

1. **Simple Resume** (text only)
   - [ ] Text renders correctly
   - [ ] Formatting preserved
   - [ ] Fonts readable

2. **Standard Resume** (with tables)
   - [ ] Tables display
   - [ ] Column alignment correct
   - [ ] Cell borders visible

3. **Complex Resume** (with images)
   - [ ] Images load
   - [ ] Colors preserved
   - [ ] Layout correct

4. **Edge Cases**
   - [ ] Large file (5+ pages)
   - [ ] Special characters (résumé, café)
   - [ ] Non-Latin text (if applicable)

---

## 🐛 Troubleshooting

### Issue: "Module not found: docx-preview"

```bash
# Solution 1: Reinstall
cd /Users/sabuj.mondal/ats-resume-scorer/frontend
npm install docx-preview --force

# Solution 2: Clear cache
rm -rf node_modules package-lock.json
npm install

# Solution 3: Check Node version
node --version  # Should be 18+
```

### Issue: TypeScript errors

```bash
# Regenerate types
npm install @types/node --save-dev

# Or skip type checking temporarily
npm run dev -- --no-type-check
```

### Issue: Build fails

```bash
# Check for conflicting dependencies
npm ls

# Try clean build
rm -rf node_modules dist
npm install
npm run build
```

### Issue: Runtime errors in browser

1. Open browser console (F12)
2. Look for errors
3. Check Network tab for failed requests
4. Verify file is valid DOCX format

---

## ✅ Verification Steps

### Final Checklist

- [ ] Package installed: `npm list docx-preview` shows version
- [ ] Components exist: All 3 `.tsx` files present
- [ ] No TypeScript errors: `npx tsc --noEmit` passes
- [ ] Dev server runs: No startup errors
- [ ] Can upload DOCX: File upload works
- [ ] Original tab shows: DOCX renders in viewer
- [ ] Edit tab works: TipTap editor functional
- [ ] Tabs switch: Can navigate between tabs
- [ ] No console errors: Clean browser console
- [ ] Performance good: Load time < 2 seconds

---

## 📊 Installation Summary

| Step | Time | Status |
|------|------|--------|
| 1. Install NPM package | 2 min | ⬜ |
| 2. Verify package.json | 1 min | ⬜ |
| 3. Check components | 1 min | ⬜ |
| 4. Test imports | 2 min | ⬜ |
| 5. Start dev server | 1 min | ⬜ |
| 6. Test demo (optional) | 5 min | ⬜ |
| 7. Integration | 15 min | ⬜ |
| 8. Update upload flow | 10 min | ⬜ |
| **TOTAL** | **37 min** | |

---

## 🎯 Success Criteria

Installation is successful when:

✅ No build errors
✅ Dev server starts
✅ Components import successfully
✅ Can upload DOCX file
✅ Document renders in viewer
✅ Tabs switch smoothly
✅ Edit mode works
✅ No runtime errors

---

## 📚 Next Steps After Installation

1. **Test with real resumes** (30 min)
   - Upload actual user resumes
   - Check accuracy
   - Note any issues

2. **Gather feedback** (ongoing)
   - Show to team members
   - Test with users
   - Collect improvement ideas

3. **Optimize** (1-2 days)
   - Add loading states
   - Improve error messages
   - Performance tuning

4. **Document** (1 day)
   - User guide
   - Internal documentation
   - API documentation (if backend changes)

---

## 🆘 Getting Help

**Installation issues?**
- Check `IMPLEMENTATION_GUIDE.md` troubleshooting section
- Review browser console for errors
- Verify all prerequisites met

**Integration questions?**
- See `WORD_VIEWER_ANALYSIS.md` for architecture
- Review component inline comments
- Check example code in guides

**Performance problems?**
- Test with smaller files first
- Check browser compatibility
- Monitor memory usage

**Feature requests?**
- Read "Future Enhancements" in README
- Consider phased approach
- Prioritize based on user needs

---

## 📅 Timeline

**Immediate (Today):**
- [x] Research completed
- [x] Components created
- [x] Documentation written
- [ ] Package installed
- [ ] Basic testing done

**This Week:**
- [ ] Full integration
- [ ] Team review
- [ ] User testing
- [ ] Bug fixes

**Next Sprint:**
- [ ] Backend enhancements
- [ ] Office Online integration
- [ ] Performance optimization
- [ ] Analytics

---

**Installation Checklist Version:** 1.0
**Date:** February 19, 2026
**Status:** Ready for installation

---

## Quick Command Reference

```bash
# Install
npm install docx-preview

# Verify
npm list docx-preview

# Start dev server
npm run dev

# Build for production
npm run build

# Type check
npx tsc --noEmit

# Clean install
rm -rf node_modules package-lock.json && npm install
```

**Ready to begin? Start with Step 1! ⬆️**
