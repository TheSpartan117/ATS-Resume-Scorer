# Developer Guide - Approach C Implementation

## Quick Start

### 1. Install Dependencies
```bash
cd frontend
npm install
```

### 2. Run Development Server
```bash
npm run dev
```

### 3. Build for Production
```bash
npm run build
```

### 4. Preview Production Build
```bash
npm run preview
```

---

## Architecture Overview

### Component Hierarchy
```
EditorPage
  └── ResumeEditor
      ├── Editor (contentEditable div)
      └── IssuesList
          ├── TopSection (Score & Progress)
          ├── TabNavigation
          └── SuggestionCards[]
```

### Data Flow
```typescript
Backend API
    ↓
  ScoreResult
    ↓
  IssuesList (processes issues)
    ↓
  ProcessedSuggestion[]
    ↓
  User clicks "Apply"
    ↓
  AppliedSuggestion callback
    ↓
  ResumeEditor (DOM manipulation)
    ↓
  Updated HTML content
    ↓
  onChange callback
    ↓
  EditorPage (state update)
```

---

## Key Files & Their Roles

### 1. IssuesList.tsx (Main Component)

**Responsibilities:**
- Process raw issues into categorized suggestions
- Render tabbed interface
- Track applied suggestions
- Provide before/after previews
- Emit `onApplySuggestion` events

**Props:**
```typescript
interface IssuesListProps {
  issues: {
    critical: string[]
    warnings: string[]
    suggestions: string[]
    info: string[]
  }
  overallScore: number
  onApplySuggestion?: (suggestion: AppliedSuggestion) => void
}
```

**State:**
```typescript
const [activeTab, setActiveTab] = useState<SuggestionType>('missing_content')
const [processedSuggestions, setProcessedSuggestions] = useState<ProcessedSuggestion[]>([])
const [appliedSuggestions, setAppliedSuggestions] = useState<Set<string>>(new Set())
```

**Key Functions:**
```typescript
// Categorize issues into suggestion types
function categorizeSuggestion(description: string, category: IssueCategory): ProcessedSuggestion

// Handle applying a suggestion
const handleApply = (suggestion: ProcessedSuggestion) => {
  // Mark as applied
  setAppliedSuggestions(prev => new Set([...prev, suggestion.id]))

  // Notify parent
  if (onApplySuggestion) {
    onApplySuggestion(appliedSuggestion)
  }
}

// Get count of pending suggestions per tab
const getTabCount = (type: SuggestionType) => {
  return processedSuggestions.filter(s => s.type === type && !appliedSuggestions.has(s.id)).length
}
```

---

### 2. ResumeEditor.tsx (Integration Component)

**Responsibilities:**
- Render contentEditable editor
- Integrate IssuesList component
- Handle suggestion application
- Manipulate DOM to insert/modify content

**Key Function:**
```typescript
const handleApplySuggestion = useCallback((suggestion: AppliedSuggestion) => {
  if (!editorRef.current) return
  const editor = editorRef.current

  if (suggestion.action === 'insert' && suggestion.content) {
    // Insert template at end
    const tempDiv = document.createElement('div')
    tempDiv.innerHTML = suggestion.content

    while (tempDiv.firstChild) {
      editor.appendChild(tempDiv.firstChild)
    }

    editor.scrollTop = editor.scrollHeight
    onChange(editor.innerHTML)
  }
  else if (suggestion.action === 'replace' && suggestion.searchText) {
    // Replace text
    const currentHtml = editor.innerHTML
    const newHtml = currentHtml.replace(suggestion.searchText, suggestion.replaceText)

    if (newHtml !== currentHtml) {
      editor.innerHTML = newHtml
      onChange(newHtml)
    }
  }
}, [onChange])
```

---

### 3. EditorPage.tsx (Container Component)

**Responsibilities:**
- Manage overall editor state
- Handle API calls for rescoring
- Coordinate between components
- Manage save/update operations

**Integration:**
```typescript
<ResumeEditor
  value={editorContent}
  onChange={handleEditorChange}
  currentScore={currentScore}
  isRescoring={isRescoring}
  wordCount={wordCount}
  onRescore={performRescore}
/>
```

---

## Type Definitions

### Core Types

```typescript
// Suggestion type categories
type SuggestionType = 'missing_content' | 'formatting' | 'keyword' | 'writing'

// Issue severity categories
type IssueCategory = 'critical' | 'warnings' | 'suggestions' | 'info'

// Applied suggestion data passed to parent
export interface AppliedSuggestion {
  id: string
  type: SuggestionType
  category: IssueCategory
  description: string
  action: 'insert' | 'replace' | 'format'
  content?: string          // For INSERT: HTML template
  searchText?: string       // For REPLACE: text to find
  replaceText?: string      // For REPLACE: replacement text
}

// Internal suggestion processing
interface ProcessedSuggestion {
  id: string
  type: SuggestionType
  category: IssueCategory
  description: string
  template?: string         // HTML template for missing content
  quickFix?: QuickFix      // Before/after for formatting
}

// Quick fix preview
interface QuickFix {
  before: string
  after: string
  action: 'replace' | 'insert' | 'format'
}
```

---

## Smart Template System

### Adding New Templates

**Step 1:** Define template in `SMART_TEMPLATES`
```typescript
const SMART_TEMPLATES: Record<string, string> = {
  'your_template_name': `<h2>Section Title</h2>
<p>Template content with [placeholders]</p>`,
}
```

**Step 2:** Add pattern matching in `categorizeSuggestion`
```typescript
function categorizeSuggestion(description: string, category: IssueCategory) {
  const lowerDesc = description.toLowerCase()

  // Add your pattern
  if (lowerDesc.includes('your keyword')) {
    return {
      id,
      type: 'missing_content',
      category,
      description,
      template: SMART_TEMPLATES.your_template_name,
    }
  }
}
```

### Template Examples

#### Simple Text Template
```typescript
'contact_email': 'your.email@example.com'
```
Usage: Direct text insertion

#### HTML Template with Formatting
```typescript
'professional_summary': `<h2>Professional Summary</h2>
<p>Results-driven professional with [X] years of experience in [Your Field].</p>`
```
Usage: Structured section with placeholders

#### List Template
```typescript
'skills_list': `<h2>Skills</h2>
<ul>
  <li>Skill 1</li>
  <li>Skill 2</li>
  <li>Skill 3</li>
</ul>`
```
Usage: Bulleted/numbered lists

---

## Pattern Matching Guide

### Current Patterns

#### 1. Missing Content Detection
```typescript
// Triggers: "missing", "add", "include"
if (lowerDesc.includes('missing') || lowerDesc.includes('add')) {
  // Categorize as missing_content
}
```

#### 2. Formatting Issues
```typescript
// Triggers: "format", "capital", "bullet", "spacing", "consistent"
if (lowerDesc.includes('format') || lowerDesc.includes('capital')) {
  // Categorize as formatting
}
```

#### 3. Keyword Issues
```typescript
// Triggers: "keyword", "term", "include the phrase"
if (lowerDesc.includes('keyword')) {
  // Extract keyword from quotes
  const keywordMatch = description.match(/"([^"]+)"|'([^']+)'/)
  const keyword = keywordMatch ? (keywordMatch[1] || keywordMatch[2]) : ''
}
```

#### 4. Writing Improvements
```typescript
// Default fallback for all other issues
return {
  id,
  type: 'writing',
  category,
  description,
}
```

### Adding New Patterns

```typescript
// Example: Detect certification-related issues
if (lowerDesc.includes('certification') || lowerDesc.includes('certifications')) {
  return {
    id,
    type: 'missing_content',
    category,
    description,
    template: SMART_TEMPLATES.certifications_section,
  }
}

// Example: Detect date formatting issues
if (lowerDesc.includes('date format')) {
  return {
    id,
    type: 'formatting',
    category,
    description,
    quickFix: {
      before: 'MM/DD/YYYY',
      after: 'Month YYYY',
      action: 'format'
    }
  }
}
```

---

## Styling Guide

### Tailwind Classes Used

#### Layout
```typescript
'flex flex-col h-full'               // Vertical flex container
'lg:w-[70%] w-full'                  // 70% width on desktop
'overflow-y-auto'                    // Scrollable content
'space-y-4'                          // Vertical spacing
```

#### Colors
```typescript
'bg-gradient-to-br from-blue-50 to-indigo-50'  // Gradient backgrounds
'text-gray-900'                                 // Primary text
'border-2 border-blue-200'                      // Borders
```

#### Interactive States
```typescript
'hover:bg-gray-100'                  // Hover background
'transition-all duration-300'        // Smooth transitions
'disabled:opacity-50'                // Disabled state
```

#### Responsive
```typescript
'hidden sm:inline'                   // Show on small screens+
'lg:col-span-2'                      // Grid layout on large screens
```

### Custom CSS Classes

Located in `index.css`:

```css
/* Line clamping */
.line-clamp-3 {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* Custom scrollbar */
.suggestions-scroll::-webkit-scrollbar {
  width: 6px;
}

.suggestions-scroll::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 3px;
}
```

---

## Testing Guide

### Manual Testing Checklist

#### Functionality Tests
```
[ ] Upload resume and navigate to editor
[ ] Verify score displays correctly in top section
[ ] Check progress bar shows 0% initially
[ ] Verify all 4 tabs render with correct icons
[ ] Check badge counters match issue counts
[ ] Click each tab and verify correct suggestions show
[ ] Click "Apply Change" on a suggestion
[ ] Verify suggestion marked as applied (checkmark)
[ ] Check progress bar updates
[ ] Verify badge counter decrements
[ ] Check applied counter increments
[ ] Apply all suggestions and verify 100% progress
[ ] Test with resume that has no issues (perfect score)
```

#### Template Tests
```
[ ] Apply professional summary template
[ ] Verify HTML inserted correctly in editor
[ ] Check template contains expected placeholders
[ ] Apply contact info templates (email, phone, LinkedIn)
[ ] Verify text appears in editor
[ ] Apply skills section template
[ ] Check formatting preserved (headings, lists)
```

#### Edge Cases
```
[ ] Test with empty issues object
[ ] Test with only one issue type
[ ] Test rapid clicking of "Apply Change"
[ ] Test with very long issue descriptions
[ ] Test with special characters in templates
[ ] Test undo (Ctrl+Z) after applying suggestion
```

### Browser Testing

```bash
# Test in multiple browsers
- Chrome 120+
- Firefox 121+
- Safari 17+
- Edge 120+
```

### Responsive Testing

```bash
# Test at different screen sizes
- Desktop: 1920x1080, 1366x768
- Tablet: 768x1024 (iPad)
- Mobile: 375x667 (iPhone), 360x640 (Android)
```

---

## Debugging Tips

### Issue: Suggestions not appearing

**Check:**
1. `currentScore.issues` contains data
2. `processedSuggestions` array populated (React DevTools)
3. `activeTab` matches suggestion types
4. No TypeScript errors in console

**Debug:**
```typescript
// Add logging to categorizeSuggestion
console.log('Processing issue:', description, '→', result)

// Check processed suggestions
useEffect(() => {
  console.log('Processed:', processedSuggestions)
}, [processedSuggestions])
```

### Issue: Apply button not working

**Check:**
1. `onApplySuggestion` callback passed to IssuesList
2. `editorRef.current` exists
3. No errors in console

**Debug:**
```typescript
const handleApply = (suggestion: ProcessedSuggestion) => {
  console.log('Applying:', suggestion)

  if (!onApplySuggestion) {
    console.error('No callback provided!')
    return
  }

  // ... rest of function
}
```

### Issue: Progress bar not updating

**Check:**
1. `appliedSuggestions` Set updating
2. `progressPercent` calculation correct
3. React re-rendering

**Debug:**
```typescript
useEffect(() => {
  console.log('Applied suggestions:', appliedSuggestions.size)
  console.log('Total suggestions:', processedSuggestions.length)
  console.log('Progress:', progressPercent)
}, [appliedSuggestions, processedSuggestions, progressPercent])
```

### Issue: Templates not inserting

**Check:**
1. Template exists in `SMART_TEMPLATES`
2. `suggestion.content` populated
3. Editor ref valid

**Debug:**
```typescript
if (suggestion.action === 'insert' && suggestion.content) {
  console.log('Inserting template:', suggestion.content)
  console.log('Editor ref:', editorRef.current)

  // ... insertion code

  console.log('New HTML:', editor.innerHTML)
}
```

---

## Performance Optimization

### Current Optimizations

#### 1. Memoization
```typescript
// Prevent unnecessary re-renders
const handleApplySuggestion = useCallback((suggestion) => {
  // ... implementation
}, [onChange])
```

#### 2. Efficient Data Structures
```typescript
// Use Set for O(1) lookups
const [appliedSuggestions, setAppliedSuggestions] = useState<Set<string>>(new Set())

// Check if applied
if (appliedSuggestions.has(suggestion.id)) return
```

#### 3. Conditional Rendering
```typescript
// Only render if tab has suggestions
{filteredSuggestions.length === 0 ? (
  <EmptyState />
) : (
  <SuggestionCards />
)}
```

### Additional Optimization Ideas

#### Virtual Scrolling (for many suggestions)
```typescript
import { FixedSizeList } from 'react-window'

<FixedSizeList
  height={400}
  itemCount={filteredSuggestions.length}
  itemSize={120}
>
  {({ index, style }) => (
    <SuggestionCard style={style} suggestion={filteredSuggestions[index]} />
  )}
</FixedSizeList>
```

#### Debounced Search
```typescript
const [searchTerm, setSearchTerm] = useState('')
const debouncedSearch = useDebounce(searchTerm, 300)

const filteredSuggestions = processedSuggestions.filter(s =>
  s.description.toLowerCase().includes(debouncedSearch.toLowerCase())
)
```

---

## API Integration

### Score Result Structure
```typescript
interface ScoreResult {
  overallScore: number
  breakdown: {
    [category: string]: {
      score: number
      maxScore: number
      issues: string[]
    }
  }
  issues: {
    critical: string[]
    warnings: string[]
    suggestions: string[]
    info: string[]
  }
  strengths: string[]
  mode: 'ats_simulation' | 'quality_coach'
}
```

### Example API Response
```json
{
  "overallScore": 72,
  "breakdown": {
    "contactInfo": { "score": 8, "maxScore": 10 },
    "formatting": { "score": 15, "maxScore": 20 },
    "keywords": { "score": 12, "maxScore": 20 },
    "content": { "score": 25, "maxScore": 30 },
    "lengthDensity": { "score": 8, "maxScore": 10 },
    "roleSpecific": { "score": 4, "maxScore": 10 }
  },
  "issues": {
    "critical": [
      "Missing email address in contact information"
    ],
    "warnings": [
      "Resume length exceeds 2 pages",
      "Inconsistent date formatting"
    ],
    "suggestions": [
      "Add professional summary section",
      "Include keyword \"Python\" in skills section",
      "Consider adding LinkedIn profile"
    ],
    "info": []
  },
  "strengths": [
    "Clear section headings",
    "Quantified achievements",
    "Relevant work experience"
  ],
  "mode": "ats_simulation"
}
```

---

## Extending the System

### Adding a New Tab

**Step 1:** Update `SuggestionType`
```typescript
type SuggestionType =
  | 'missing_content'
  | 'formatting'
  | 'keyword'
  | 'writing'
  | 'your_new_type'  // Add here
```

**Step 2:** Add tab configuration
```typescript
const TABS = [
  // ... existing tabs
  {
    id: 'your_new_type' as SuggestionType,
    label: 'Your Label',
    icon: '🆕',
    color: 'purple'
  }
]
```

**Step 3:** Add categorization logic
```typescript
function categorizeSuggestion(description: string, category: IssueCategory) {
  // ... existing logic

  if (lowerDesc.includes('your_trigger_word')) {
    return {
      id,
      type: 'your_new_type',
      category,
      description,
    }
  }
}
```

### Adding a New Action Type

**Step 1:** Update action type
```typescript
action: 'insert' | 'replace' | 'format' | 'your_new_action'
```

**Step 2:** Handle in ResumeEditor
```typescript
const handleApplySuggestion = useCallback((suggestion: AppliedSuggestion) => {
  // ... existing actions

  if (suggestion.action === 'your_new_action') {
    // Implement your custom action
    console.log('Performing custom action:', suggestion)
  }
}, [onChange])
```

---

## Deployment Checklist

### Pre-Deployment
```
[ ] All TypeScript errors resolved
[ ] All tests passing
[ ] No console errors in production build
[ ] Bundle size acceptable (<250KB gzipped)
[ ] Lighthouse score >90
[ ] All browsers tested
[ ] Mobile responsive verified
```

### Build Commands
```bash
# Development
npm run dev

# Production build
npm run build

# Preview production
npm run preview

# Type check
npm run type-check

# Lint
npm run lint
```

### Environment Variables
```bash
# .env.production
VITE_API_URL=https://api.yourapp.com
```

### Build Output
```
dist/
  ├── index.html
  ├── assets/
  │   ├── index-[hash].js      # Main bundle
  │   ├── index-[hash].css     # Styles
  │   └── vendor-[hash].js     # Dependencies
  └── ...
```

---

## Troubleshooting Common Issues

### Build Fails with Type Errors

**Solution:**
```bash
# Check specific errors
npm run type-check

# Fix unused imports
# Remove or prefix with underscore: _unusedVar
```

### Suggestions Not Categorizing

**Solution:**
```typescript
// Add more inclusive patterns
if (
  lowerDesc.includes('missing') ||
  lowerDesc.includes('add') ||
  lowerDesc.includes('need') ||          // Add more
  lowerDesc.includes('required')          // triggers
) {
  // ...
}
```

### Apply Button Doesn't Update Editor

**Solution:**
```typescript
// Ensure onChange is called
onChange(editor.innerHTML)

// Force re-render if needed
editor.dispatchEvent(new Event('input', { bubbles: true }))
```

### Progress Bar Stuck

**Solution:**
```typescript
// Check calculation
const progressPercent = totalIssues > 0
  ? Math.round((appliedCount / totalIssues) * 100)
  : 100  // Handle division by zero

// Ensure state updates
setAppliedSuggestions(prev => new Set([...prev, suggestion.id]))
```

---

## Best Practices

### Code Style
```typescript
// Use descriptive names
const handleApplySuggestion = () => {}  // Good
const handle = () => {}                 // Bad

// Type everything
interface Props { ... }                 // Good
const props: any                        // Bad

// Extract magic numbers
const TAB_COUNT = 4                     // Good
if (tabs.length === 4)                  // Bad
```

### Component Organization
```typescript
// 1. Imports
import React from 'react'

// 2. Types/Interfaces
interface Props { ... }

// 3. Constants
const TABS = [...]

// 4. Helper Functions
function categorizeSuggestion() { ... }

// 5. Component
export default function Component() {
  // State
  const [state, setState] = useState()

  // Effects
  useEffect(() => {}, [])

  // Handlers
  const handleClick = () => {}

  // Render
  return <div>...</div>
}
```

### Performance
```typescript
// Use keys in lists
{items.map(item => (
  <Card key={item.id} />  // Good
))}

// Memoize expensive calculations
const filtered = useMemo(() =>
  items.filter(/* ... */),
  [items]
)

// Debounce rapid actions
const debouncedSave = useDebounce(save, 500)
```

---

## Support & Resources

### Internal Documentation
- `/IMPLEMENTATION_SUMMARY.md` - Complete feature overview
- `/UI_MOCKUP.md` - Visual design reference
- `/DEVELOPER_GUIDE.md` - This file

### External Resources
- [React Documentation](https://react.dev/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [Vite Guide](https://vitejs.dev/guide/)

### Getting Help

**TypeScript Errors:**
```bash
npm run type-check 2>&1 | less
```

**Bundle Analysis:**
```bash
npm run build -- --mode analyze
```

**React DevTools:**
- Install browser extension
- Inspect component tree
- Check props/state

---

**END OF DEVELOPER GUIDE**
