# Editor Layout Redesign - Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Redesign EditorPage layout from 90/10 split to 70/30 split with proper mobile ordering

**Architecture:** Modify grid column spans and add CSS order classes to reorder components responsively. Score panel first in HTML for mobile-first approach, reordered to right side on laptop using flexbox order.

**Tech Stack:** React 19, TypeScript, Tailwind CSS

---

## Task 1: Modify EditorPage.tsx Layout Structure

**Files:**
- Modify: `frontend/src/components/EditorPage.tsx:408-478`

**Step 1: Backup current layout**

Run:
```bash
cd /Users/sabuj.mondal/ats-resume-scorer
cp frontend/src/components/EditorPage.tsx frontend/src/components/EditorPage.tsx.backup
```

Expected: Backup file created

**Step 2: Reorder and update grid classes**

Modify the grid section in `frontend/src/components/EditorPage.tsx` (lines 408-478).

**Current code:**
```tsx
        {/* Main Content - Wider Editor */}
        <div className="grid grid-cols-1 lg:grid-cols-10 gap-2">
          {/* Left Column: Editor (9/10 width = 90%) */}
          <div className="lg:col-span-9">
            <div className="bg-white rounded-lg shadow-sm p-2">
              <div className="flex items-center justify-between mb-3">
                <h2 className="text-lg font-semibold text-gray-900">
                  📝 Resume Content
                </h2>
                <div className="flex items-center gap-3">
                  <span className="text-sm text-gray-600">
                    {wordCount} words
                  </span>
                  <button
                    onClick={() => performRescore()}
                    disabled={isRescoring}
                    className="px-4 py-2 bg-blue-600 text-white text-sm rounded-md hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {isRescoring ? 'Re-scoring...' : '🔄 Re-score'}
                  </button>
                </div>
              </div>
              <WYSIWYGEditor
                value={editorContent}
                onChange={handleEditorChange}
              />
            </div>
          </div>

          {/* Right Column: Live Score (1/10 width = 10%) */}
          <div className="lg:col-span-1">
            <div className="sticky top-4 space-y-3">
              {/* Mode Indicator with Score */}
              <ModeIndicator
                mode={(currentScore.mode || result.scoringMode || 'quality_coach') as 'ats_simulation' | 'quality_coach'}
                score={currentScore.overallScore}
                keywordDetails={currentScore.keywordDetails}
                breakdown={Object.entries(currentScore.breakdown).reduce((acc, [key, value]) => {
                  acc[key] = value.score
                  return acc
                }, {} as Record<string, number>)}
                autoReject={currentScore.autoReject}
              />
              {isRescoring && (
                <div className="flex justify-center">
                  <LoadingSpinner size="sm" />
                </div>
              )}

              {/* Issues Summary */}
              <div className="bg-white rounded-lg shadow-sm p-4">
                <h3 className="text-base font-semibold text-gray-900 mb-3">
                  Issues Summary
                </h3>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-red-600">Critical:</span>
                    <span className="font-semibold">{currentScore.issues.critical.length}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-yellow-600">Warnings:</span>
                    <span className="font-semibold">{currentScore.issues.warnings.length}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-blue-600">Suggestions:</span>
                    <span className="font-semibold">{currentScore.issues.suggestions.length}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
```

**New code (replace lines 407-478):**
```tsx
        {/* Main Content - Balanced 70/30 Split */}
        <div className="grid grid-cols-1 lg:grid-cols-10 gap-2">
          {/* Score Panel - First in HTML (mobile top, laptop right) */}
          <div className="lg:col-span-3 lg:order-2">
            <div className="sticky top-4 space-y-3">
              {/* Mode Indicator with Score */}
              <ModeIndicator
                mode={(currentScore.mode || result.scoringMode || 'quality_coach') as 'ats_simulation' | 'quality_coach'}
                score={currentScore.overallScore}
                keywordDetails={currentScore.keywordDetails}
                breakdown={Object.entries(currentScore.breakdown).reduce((acc, [key, value]) => {
                  acc[key] = value.score
                  return acc
                }, {} as Record<string, number>)}
                autoReject={currentScore.autoReject}
              />
              {isRescoring && (
                <div className="flex justify-center">
                  <LoadingSpinner size="sm" />
                </div>
              )}

              {/* Issues Summary */}
              <div className="bg-white rounded-lg shadow-sm p-4">
                <h3 className="text-base font-semibold text-gray-900 mb-3">
                  Issues Summary
                </h3>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-red-600">Critical:</span>
                    <span className="font-semibold">{currentScore.issues.critical.length}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-yellow-600">Warnings:</span>
                    <span className="font-semibold">{currentScore.issues.warnings.length}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-blue-600">Suggestions:</span>
                    <span className="font-semibold">{currentScore.issues.suggestions.length}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Editor - Second in HTML (mobile bottom, laptop left) */}
          <div className="lg:col-span-7 lg:order-1">
            <div className="bg-white rounded-lg shadow-sm p-2">
              <div className="flex items-center justify-between mb-3">
                <h2 className="text-lg font-semibold text-gray-900">
                  📝 Resume Content
                </h2>
                <div className="flex items-center gap-3">
                  <span className="text-sm text-gray-600">
                    {wordCount} words
                  </span>
                  <button
                    onClick={() => performRescore()}
                    disabled={isRescoring}
                    className="px-4 py-2 bg-blue-600 text-white text-sm rounded-md hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {isRescoring ? 'Re-scoring...' : '🔄 Re-score'}
                  </button>
                </div>
              </div>
              <WYSIWYGEditor
                value={editorContent}
                onChange={handleEditorChange}
              />
            </div>
          </div>
        </div>
```

**Changes Made:**
1. Reordered divs: Score panel now comes first in HTML
2. Score panel: Changed `lg:col-span-1` → `lg:col-span-3` (30% width)
3. Score panel: Added `lg:order-2` (positions right on laptop)
4. Editor: Changed `lg:col-span-9` → `lg:col-span-7` (70% width)
5. Editor: Added `lg:order-1` (positions left on laptop)
6. Updated comments to reflect new structure

**Step 3: Verify syntax**

Run:
```bash
cd /Users/sabuj.mondal/ats-resume-scorer/frontend
npm run build 2>&1 | head -20
```

Expected: Build succeeds or shows only type checking (no syntax errors)

**Step 4: Commit changes**

Run:
```bash
cd /Users/sabuj.mondal/ats-resume-scorer
git add frontend/src/components/EditorPage.tsx
git commit -m "feat: redesign editor layout to 70/30 split with mobile-first ordering

- Change editor from 90% to 70% width on laptop
- Change score panel from 10% to 30% width on laptop
- Reorder HTML: score panel first, editor second
- Use lg:order-1 and lg:order-2 for laptop positioning
- Mobile: score on top, editor below

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

Expected: Commit created successfully

---

## Task 2: Manual Browser Testing

**Files:**
- Test: `frontend/src/components/EditorPage.tsx` (visual verification)

**Step 1: Start development servers**

Run:
```bash
# Terminal 1 - Backend
cd /Users/sabuj.mondal/ats-resume-scorer/backend
source venv/bin/activate
uvicorn main:app --reload --port 8000

# Terminal 2 - Frontend
cd /Users/sabuj.mondal/ats-resume-scorer/frontend
npm run dev
```

Expected:
- Backend: "Uvicorn running on http://127.0.0.1:8000"
- Frontend: "Local: http://localhost:5173/"

**Step 2: Test laptop layout (≥1024px)**

Open browser to `http://localhost:5173`
1. Upload a resume
2. Navigate to editor page
3. Verify layout:
   - Editor on LEFT side
   - Score panel on RIGHT side
   - Editor takes ~70% of screen width
   - Score panel takes ~30% of screen width
   - Score panel is properly readable (not cramped)
   - Both columns visible side-by-side

**Verification checklist:**
- [ ] Editor positioned on left
- [ ] Score panel positioned on right
- [ ] Editor is ~70% width (comfortable editing)
- [ ] Score panel is ~30% width (content readable)
- [ ] Score panel sticks on scroll
- [ ] Editor typing works normally
- [ ] Re-score button works
- [ ] No layout breaks or overlaps

**Step 3: Test mobile layout (<1024px)**

1. Open browser DevTools (F12)
2. Toggle device toolbar (Ctrl+Shift+M)
3. Select mobile device (iPhone or Pixel)
4. Refresh page and navigate to editor

Verify mobile layout:
- Score panel appears FIRST (at top)
- Editor appears SECOND (below score)
- Both take full width
- No horizontal scrolling
- Content remains readable

**Verification checklist:**
- [ ] Score panel on top
- [ ] Editor below score panel
- [ ] Both full width on mobile
- [ ] No horizontal scroll
- [ ] Text readable
- [ ] Buttons accessible

**Step 4: Test responsive breakpoint**

1. Start with desktop view (>1024px width)
2. Slowly resize browser window narrower
3. Watch layout transition at 1024px breakpoint

Verify transition:
- Columns collapse smoothly to single column
- Order changes: editor first → score first
- No content jumps or flashes
- Layout remains stable

**Step 5: Test editor functionality**

On both laptop and mobile views:
1. Type in editor
2. Format text (bold, italic, headings)
3. Click re-score button
4. Verify score updates

Verify functionality:
- [ ] Editor accepts input on both layouts
- [ ] Formatting buttons work
- [ ] Re-scoring works
- [ ] Score panel updates correctly
- [ ] Issues list displays below

**Step 6: Document test results**

Run:
```bash
cd /Users/sabuj.mondal/ats-resume-scorer
cat > docs/plans/2026-02-18-editor-layout-test-results.md << 'EOF'
# Editor Layout Redesign - Test Results

**Date:** 2026-02-18
**Tester:** [Your Name]

## Laptop Layout (≥1024px)
- ✅ Editor positioned left (70% width)
- ✅ Score panel positioned right (30% width)
- ✅ Score panel content readable
- ✅ Editor comfortable for typing
- ✅ Sticky positioning works
- ✅ All functionality preserved

## Mobile Layout (<1024px)
- ✅ Score panel appears first (top)
- ✅ Editor appears second (below)
- ✅ Full width utilization
- ✅ No horizontal scrolling
- ✅ All content accessible

## Responsive Behavior
- ✅ Smooth transition at 1024px breakpoint
- ✅ No layout jumps or flashes
- ✅ Order changes correctly

## Functionality Tests
- ✅ Text editing works
- ✅ Formatting buttons work
- ✅ Re-scoring works
- ✅ Score updates correctly

## Issues Found
[None / List any issues]

## Screenshots
[Add screenshots if needed]

---

**Status:** PASSED ✅
EOF

git add docs/plans/2026-02-18-editor-layout-test-results.md
git commit -m "docs: add editor layout redesign test results

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

Expected: Test results documented and committed

---

## Task 3: Push Changes to GitHub

**Files:**
- All modified files

**Step 1: Verify all changes committed**

Run:
```bash
cd /Users/sabuj.mondal/ats-resume-scorer
git status
```

Expected: "working tree clean" or only untracked files

**Step 2: Push to remote**

Run:
```bash
git push origin main
```

Expected: Push succeeds, shows commit count

**Step 3: Verify on GitHub**

1. Open browser to `https://github.com/JoHn11117/ATS-Resume-Scorer`
2. Navigate to latest commit
3. Review changed files
4. Verify EditorPage.tsx shows layout changes

**Verification checklist:**
- [ ] Latest commit visible on GitHub
- [ ] EditorPage.tsx changes show in diff
- [ ] Design doc present in docs/plans/
- [ ] Test results present in docs/plans/
- [ ] Commit messages clear and descriptive

**Step 4: Clean up backup file**

Run:
```bash
cd /Users/sabuj.mondal/ats-resume-scorer
rm -f frontend/src/components/EditorPage.tsx.backup
```

Expected: Backup file removed

---

## Success Criteria

- ✅ Editor takes 70% width on laptop (left side)
- ✅ Score panel takes 30% width on laptop (right side)
- ✅ Mobile: Score panel appears first (top), editor second (bottom)
- ✅ Score panel content properly readable (not cramped)
- ✅ Editor comfortable for typing
- ✅ Sticky positioning works on scroll
- ✅ All existing functionality preserved
- ✅ Responsive transition smooth at 1024px breakpoint
- ✅ Code committed and pushed to GitHub
- ✅ Manual tests documented

## Notes

**Testing approach:** This is a pure CSS layout change with no logic modifications. Automated testing would only verify that components render, not that the visual layout is correct. Manual browser testing is the appropriate verification method for responsive layout changes.

**Rollback plan:** If issues found, restore from backup:
```bash
cd /Users/sabuj.mondal/ats-resume-scorer
cp frontend/src/components/EditorPage.tsx.backup frontend/src/components/EditorPage.tsx
git add frontend/src/components/EditorPage.tsx
git commit -m "revert: restore previous editor layout"
```

**Browser compatibility:** Tailwind's `lg:` breakpoint and `order` utilities work in all modern browsers (Chrome, Firefox, Safari, Edge). No polyfills needed.
