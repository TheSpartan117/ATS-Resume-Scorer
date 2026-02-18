# Editor Page Layout Redesign - Design Document

**Date:** 2026-02-18
**Status:** Approved
**Goal:** Redesign EditorPage layout to use screen space effectively with a balanced 70/30 split

---

## Problem Statement

Current editor page layout issues:
1. **Cramped editor**: Editor width insufficient for comfortable editing
2. **Narrow score panel**: 10% width (1/10 columns) too narrow to display content properly
3. **Poor space utilization**: Full screen width not utilized effectively

User feedback:
- "Editor width is very less, making it very lengthy. Use space properly - widen the Editor"
- "Please fix these- even the page is not full screen"

## Design Solution: Balanced Two-Column Layout (70/30 Split)

### Layout Architecture

**Grid System:**
- Grid container: `grid-cols-1 lg:grid-cols-10`
- **Laptop/Desktop (≥1024px):**
  - Editor: 7 columns = 70% width (left side)
  - Score panel: 3 columns = 30% width (right side)
- **Mobile (<1024px):**
  - Full width stack
  - Score panel appears FIRST (on top)
  - Editor appears SECOND (below score)

**Container:**
- Full width: `w-full`
- Minimal padding: `px-2 py-4`
- Maintains edge-to-edge space utilization

### Component Structure

**HTML/JSX Order:**
```tsx
<div className="w-full px-2 py-4">
  <div className="grid grid-cols-1 lg:grid-cols-10 gap-2">

    {/* Score Panel - First in DOM */}
    <div className="lg:col-span-3 lg:order-2">
      <div className="sticky top-4 space-y-3">
        {/* Mode Indicator with Score */}
        {/* Issues Summary */}
      </div>
    </div>

    {/* Editor - Second in DOM */}
    <div className="lg:col-span-7 lg:order-1">
      <div className="bg-white rounded-lg shadow-sm p-2">
        {/* Header with word count and re-score button */}
        {/* WYSIWYGEditor */}
      </div>
    </div>

  </div>

  {/* Full Issues List - Below both columns */}
  <div className="mt-4 bg-white rounded-lg shadow-sm p-4">
    <IssuesList />
  </div>
</div>
```

**Key Ordering Strategy:**
- Score panel is **first in HTML** for mobile-first approach
- Uses `lg:order-1` and `lg:order-2` to reorder on laptop
- Natural mobile stacking: score top, editor bottom
- Grid positioning: editor left (70%), score right (30%) on laptop

### Responsive Behavior

**Mobile (<1024px):**
- Single column stack
- Score panel: Full width, appears first (top)
- Editor: Full width, appears second (below)
- Issues list: Full width, appears third (bottom)

**Laptop/Desktop (≥1024px):**
- Two columns side-by-side
- Editor: Left side, 70% width, order: 1
- Score panel: Right side, 30% width, order: 2, sticky positioning
- Issues list: Full width below both columns

### Styling Details

**Score Panel (30% width):**
- Container: `lg:col-span-3 lg:order-2`
- Sticky positioning: `sticky top-4` (stays visible on scroll)
- Spacing: `space-y-3` between cards
- Cards: Mode indicator + Issues summary

**Editor (70% width):**
- Container: `lg:col-span-7 lg:order-1`
- Background: White card with rounded corners, shadow
- Padding: `p-2` (minimal)
- Maintains current WYSIWYGEditor styling:
  - Georgia serif font
  - 800px min-height
  - Prose classes for typography
  - Colorful heading styles (blue/indigo)

**Gap Between Columns:**
- Grid gap: `gap-2` (8px)
- Clean separation without wasted space

## Files to Modify

### Primary Changes
- **frontend/src/components/EditorPage.tsx** (lines ~408-477)
  - Change grid from `lg:grid-cols-10` to `lg:grid-cols-10` (keep same)
  - Change editor from `lg:col-span-9` to `lg:col-span-7`
  - Change score panel from `lg:col-span-1` to `lg:col-span-3`
  - Add `lg:order-2` to score panel div
  - Add `lg:order-1` to editor div
  - Reorder divs: score panel first, editor second

### No Changes Needed
- **frontend/src/components/WYSIWYGEditor.tsx** - No changes
- **frontend/src/index.css** - No changes
- Editor content styling remains the same

## Implementation Approach

**Change Type:** Layout adjustment only
- No new components needed
- No state management changes
- No API changes
- Pure CSS/Tailwind class modifications

**Testing:**
1. Verify 70/30 split on laptop screens (≥1024px)
2. Verify mobile stacking (score on top)
3. Verify sticky score panel behavior on scroll
4. Verify editor remains fully functional
5. Test responsive breakpoints

## Success Criteria

- ✅ Editor has 70% width on laptop (increased from 90%)
- ✅ Score panel has 30% width on laptop (increased from 10%)
- ✅ Full screen width utilized effectively
- ✅ Mobile: Score panel appears on top
- ✅ Score panel content displays properly (not cramped)
- ✅ Editor remains comfortable for typing
- ✅ Existing functionality preserved

## Trade-offs

**Pros:**
- Simple implementation (just grid ratio changes)
- Both editor and score always visible on laptop
- Score panel has reasonable width (3x larger than before)
- Editor gets significant width increase (70% vs previous cramped state)
- Mobile-first ordering ensures good UX on all devices

**Cons:**
- Editor not full width (70% instead of 100%)
- Fixed ratio (can't be adjusted by user)
- Score panel always visible (can't be hidden)

**Rationale:**
User requested proper space utilization with both elements visible. This balanced approach provides comfortable editing width while giving score panel enough space to display content properly.

---

## Approved By
- User on 2026-02-18

## Next Steps
1. Create implementation plan using writing-plans skill
2. Modify EditorPage.tsx grid layout and ordering
3. Test on laptop and mobile viewports
4. Verify sticky positioning works
5. Commit and push changes
