# Phase 7: Frontend Rich Text Editor - Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add TipTap rich text editor for resume editing with real-time re-scoring, authentication-based save/load functionality, and ad integration

**Architecture:** TipTap editor with custom toolbar for resume text editing. Debounced re-scoring calls /api/score. Auth integration for save/load using JWT tokens. Ad logic checks /api/should-show-ad before re-scoring, displays ads for non-premium users after first free score.

**Tech Stack:** TipTap (rich text editor), React hooks (useDebounce, useAuth), localStorage for JWT, Axios for API calls

---

## Context

**Current State:**
- Phase 6 complete: Upload & results pages working
- Backend API complete with:
  - POST /api/score (re-scoring endpoint)
  - Auth endpoints (/api/signup, /api/login, /api/me)
  - Protected resume CRUD (/api/resumes)
  - Ad tracking (/api/ad-view, /api/should-show-ad)
- No editor component yet
- No authentication integration in frontend
- No save/load functionality

**What We're Building:**
Phase 7 adds editing capabilities and user features:
1. **TipTap Editor**: Rich text editor with toolbar for editing resume content
2. **Real-time Re-scoring**: Debounced re-scoring as user types (500ms delay)
3. **Authentication**: Signup/login forms, JWT token management, protected routes
4. **Save/Load**: Save edited resumes for authenticated users, load from saved list
5. **Ad Integration**: Show ads before re-scoring (first score free, premium exempt)

---

## Task 22: TipTap Editor Setup & Dependencies

**Goal:** Install TipTap and create basic editor component

**Files:**
- Modify: `frontend/package.json`
- Create: `frontend/src/components/RichTextEditor.tsx`
- Create: `frontend/src/hooks/useDebounce.ts`

### Step 1: Install TipTap dependencies

```bash
cd /Users/sabuj.mondal/ats-resume-scorer/frontend
npm install @tiptap/react @tiptap/starter-kit @tiptap/extension-placeholder
```

**Expected:** Dependencies installed successfully

### Step 2: Create useDebounce hook

**Create `frontend/src/hooks/useDebounce.ts`:**
```typescript
/**
 * Custom hook for debouncing values
 */
import { useEffect, useState } from 'react'

export function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value)

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value)
    }, delay)

    return () => {
      clearTimeout(handler)
    }
  }, [value, delay])

  return debouncedValue
}
```

### Step 3: Create basic RichTextEditor component

**Create `frontend/src/components/RichTextEditor.tsx`:**
```typescript
/**
 * Rich text editor component using TipTap
 */
import { useEditor, EditorContent } from '@tiptap/react'
import StarterKit from '@tiptap/starter-kit'
import Placeholder from '@tiptap/extension-placeholder'
import { useEffect } from 'react'

interface RichTextEditorProps {
  content: string
  onChange: (content: string) => void
  placeholder?: string
  editable?: boolean
}

export default function RichTextEditor({
  content,
  onChange,
  placeholder = 'Start editing your resume...',
  editable = true
}: RichTextEditorProps) {
  const editor = useEditor({
    extensions: [
      StarterKit,
      Placeholder.configure({
        placeholder
      })
    ],
    content,
    editable,
    onUpdate: ({ editor }) => {
      onChange(editor.getHTML())
    },
    editorProps: {
      attributes: {
        class: 'prose prose-sm sm:prose lg:prose-lg xl:prose-xl focus:outline-none min-h-[400px] max-w-none p-4'
      }
    }
  })

  // Update editor content when prop changes
  useEffect(() => {
    if (editor && content !== editor.getHTML()) {
      editor.commands.setContent(content)
    }
  }, [content, editor])

  // Update editable state
  useEffect(() => {
    if (editor) {
      editor.setEditable(editable)
    }
  }, [editable, editor])

  if (!editor) {
    return null
  }

  return (
    <div className="border border-gray-300 rounded-lg overflow-hidden">
      <EditorContent editor={editor} />
    </div>
  )
}
```

### Step 4: Add @tailwindcss/typography for prose styles

```bash
npm install @tailwindcss/typography
```

### Step 5: Update Tailwind config

**Modify `frontend/tailwind.config.js`:**
```javascript
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [
    require('@tailwindcss/typography'),
  ],
}
```

### Step 6: Test editor component

Create a test page to verify editor works:
```bash
npm run dev
```

Open browser console and verify TipTap loads without errors.

### Step 7: Commit

```bash
git add frontend/package.json frontend/package-lock.json frontend/src/components/RichTextEditor.tsx frontend/src/hooks/useDebounce.ts frontend/tailwind.config.js
git commit -m "feat: setup TipTap rich text editor

- Install TipTap dependencies
- Create RichTextEditor component with StarterKit
- Add placeholder extension
- Create useDebounce custom hook
- Add @tailwindcss/typography for prose styles
- Configure editor props and styling"
```

---

## Task 23: Editor Toolbar & Formatting Options

**Goal:** Add toolbar with formatting buttons (bold, italic, lists, etc.)

**Files:**
- Modify: `frontend/src/components/RichTextEditor.tsx`
- Create: `frontend/src/components/EditorToolbar.tsx`

### Step 1: Create EditorToolbar component

**Create `frontend/src/components/EditorToolbar.tsx`:**
```typescript
/**
 * Toolbar for TipTap editor with formatting buttons
 */
import { Editor } from '@tiptap/react'

interface EditorToolbarProps {
  editor: Editor | null
}

export default function EditorToolbar({ editor }: EditorToolbarProps) {
  if (!editor) {
    return null
  }

  const ButtonClass = (isActive: boolean) =>
    `px-3 py-1 rounded text-sm font-medium transition-colors ${
      isActive
        ? 'bg-blue-600 text-white'
        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
    }`

  return (
    <div className="border-b border-gray-300 p-2 bg-gray-50 flex flex-wrap gap-2">
      {/* Text Formatting */}
      <div className="flex gap-1">
        <button
          type="button"
          onClick={() => editor.chain().focus().toggleBold().run()}
          className={ButtonClass(editor.isActive('bold'))}
          title="Bold (Ctrl+B)"
        >
          <strong>B</strong>
        </button>
        <button
          type="button"
          onClick={() => editor.chain().focus().toggleItalic().run()}
          className={ButtonClass(editor.isActive('italic'))}
          title="Italic (Ctrl+I)"
        >
          <em>I</em>
        </button>
        <button
          type="button"
          onClick={() => editor.chain().focus().toggleStrike().run()}
          className={ButtonClass(editor.isActive('strike'))}
          title="Strikethrough"
        >
          <s>S</s>
        </button>
      </div>

      {/* Divider */}
      <div className="border-l border-gray-300"></div>

      {/* Headings */}
      <div className="flex gap-1">
        <button
          type="button"
          onClick={() => editor.chain().focus().toggleHeading({ level: 1 }).run()}
          className={ButtonClass(editor.isActive('heading', { level: 1 }))}
          title="Heading 1"
        >
          H1
        </button>
        <button
          type="button"
          onClick={() => editor.chain().focus().toggleHeading({ level: 2 }).run()}
          className={ButtonClass(editor.isActive('heading', { level: 2 }))}
          title="Heading 2"
        >
          H2
        </button>
        <button
          type="button"
          onClick={() => editor.chain().focus().toggleHeading({ level: 3 }).run()}
          className={ButtonClass(editor.isActive('heading', { level: 3 }))}
          title="Heading 3"
        >
          H3
        </button>
      </div>

      {/* Divider */}
      <div className="border-l border-gray-300"></div>

      {/* Lists */}
      <div className="flex gap-1">
        <button
          type="button"
          onClick={() => editor.chain().focus().toggleBulletList().run()}
          className={ButtonClass(editor.isActive('bulletList'))}
          title="Bullet List"
        >
          • List
        </button>
        <button
          type="button"
          onClick={() => editor.chain().focus().toggleOrderedList().run()}
          className={ButtonClass(editor.isActive('orderedList'))}
          title="Numbered List"
        >
          1. List
        </button>
      </div>

      {/* Divider */}
      <div className="border-l border-gray-300"></div>

      {/* Misc */}
      <div className="flex gap-1">
        <button
          type="button"
          onClick={() => editor.chain().focus().setHorizontalRule().run()}
          className={ButtonClass(false)}
          title="Horizontal Rule"
        >
          ―
        </button>
        <button
          type="button"
          onClick={() => editor.chain().focus().undo().run()}
          disabled={!editor.can().undo()}
          className="px-3 py-1 rounded text-sm font-medium bg-gray-100 text-gray-700 hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed"
          title="Undo (Ctrl+Z)"
        >
          ↶ Undo
        </button>
        <button
          type="button"
          onClick={() => editor.chain().focus().redo().run()}
          disabled={!editor.can().redo()}
          className="px-3 py-1 rounded text-sm font-medium bg-gray-100 text-gray-700 hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed"
          title="Redo (Ctrl+Y)"
        >
          ↷ Redo
        </button>
      </div>
    </div>
  )
}
```

### Step 2: Integrate toolbar into RichTextEditor

**Modify `frontend/src/components/RichTextEditor.tsx`:**
```typescript
/**
 * Rich text editor component using TipTap
 */
import { useEditor, EditorContent } from '@tiptap/react'
import StarterKit from '@tiptap/starter-kit'
import Placeholder from '@tiptap/extension-placeholder'
import { useEffect } from 'react'
import EditorToolbar from './EditorToolbar'

interface RichTextEditorProps {
  content: string
  onChange: (content: string) => void
  placeholder?: string
  editable?: boolean
}

export default function RichTextEditor({
  content,
  onChange,
  placeholder = 'Start editing your resume...',
  editable = true
}: RichTextEditorProps) {
  const editor = useEditor({
    extensions: [
      StarterKit,
      Placeholder.configure({
        placeholder
      })
    ],
    content,
    editable,
    onUpdate: ({ editor }) => {
      onChange(editor.getHTML())
    },
    editorProps: {
      attributes: {
        class: 'prose prose-sm sm:prose lg:prose-lg xl:prose-xl focus:outline-none min-h-[400px] max-w-none p-4'
      }
    }
  })

  // Update editor content when prop changes
  useEffect(() => {
    if (editor && content !== editor.getHTML()) {
      editor.commands.setContent(content)
    }
  }, [content, editor])

  // Update editable state
  useEffect(() => {
    if (editor) {
      editor.setEditable(editable)
    }
  }, [editable, editor])

  if (!editor) {
    return null
  }

  return (
    <div className="border border-gray-300 rounded-lg overflow-hidden bg-white">
      {editable && <EditorToolbar editor={editor} />}
      <EditorContent editor={editor} />
    </div>
  )
}
```

### Step 3: Test toolbar functionality

```bash
npm run dev
```

Test:
1. Bold, italic, strikethrough buttons work
2. H1, H2, H3 heading buttons work
3. Bullet and numbered list buttons work
4. Horizontal rule button works
5. Undo/redo buttons work
6. Active states highlight correctly
7. Keyboard shortcuts work (Ctrl+B, Ctrl+I, etc.)

### Step 4: Commit

```bash
git add frontend/src/components/EditorToolbar.tsx frontend/src/components/RichTextEditor.tsx
git commit -m "feat: add editor toolbar with formatting options

- Create EditorToolbar component with formatting buttons
- Add bold, italic, strikethrough buttons
- Add H1, H2, H3 heading buttons
- Add bullet and numbered list buttons
- Add horizontal rule, undo, redo buttons
- Active state styling for toolbar buttons
- Keyboard shortcuts support
- Only show toolbar when editor is editable"
```

---

## Task 24: Editor Page with Real-time Re-scoring

**Goal:** Create editor page that converts resume to editable text and re-scores on changes

**Files:**
- Create: `frontend/src/components/EditorPage.tsx`
- Modify: `frontend/src/types/resume.ts`
- Modify: `frontend/src/api/client.ts`
- Modify: `frontend/src/App.tsx`

### Step 1: Add rescoreResume function to API client

**Modify `frontend/src/api/client.ts`** (add to existing file):
```typescript
// Add to imports
import type { UploadResponse, ScoreResult } from '../types/resume'

// Add new interface for score request
export interface ScoreRequest {
  fileName: string
  contact: {
    name?: string
    email?: string
    phone?: string
    location?: string
    linkedin?: string
    website?: string
  }
  experience: any[]
  education: any[]
  skills: string[]
  certifications: any[]
  metadata: {
    pageCount: number
    wordCount: number
    hasPhoto: boolean
    fileFormat: string
  }
  jobDescription?: string
  industry?: string
}

/**
 * Re-score edited resume content
 */
export async function rescoreResume(request: ScoreRequest): Promise<ScoreResult> {
  try {
    const response = await apiClient.post<ScoreResult>('/api/score', request)
    return response.data
  } catch (error) {
    const axiosError = error as AxiosError<ApiError>
    throw new Error(axiosError.response?.data?.detail || 'Failed to re-score resume')
  }
}
```

### Step 2: Add ResumeContent interface to types

**Modify `frontend/src/types/resume.ts`** (add to existing file):
```typescript
/**
 * Editable resume content for rich text editor
 */
export interface ResumeContent {
  fileName: string
  rawText: string  // HTML content from editor
  contact: ContactInfo
  metadata: ResumeMetadata
  jobDescription?: string
  industry?: string
}
```

### Step 3: Create EditorPage component

**Create `frontend/src/components/EditorPage.tsx`:**
```typescript
/**
 * Editor page component with real-time re-scoring
 */
import { useState, useEffect, useCallback } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import RichTextEditor from './RichTextEditor'
import ScoreCard from './ScoreCard'
import CategoryBreakdown from './CategoryBreakdown'
import IssuesList from './IssuesList'
import LoadingSpinner from './LoadingSpinner'
import { useDebounce } from '../hooks/useDebounce'
import { rescoreResume, type ScoreRequest } from '../api/client'
import type { UploadResponse, ScoreResult } from '../types/resume'

export default function EditorPage() {
  const location = useLocation()
  const navigate = useNavigate()
  const result = location.state?.result as UploadResponse | undefined

  // Redirect if no result data
  useEffect(() => {
    if (!result) {
      navigate('/')
    }
  }, [result, navigate])

  // State
  const [editorContent, setEditorContent] = useState('')
  const [currentScore, setCurrentScore] = useState<ScoreResult | null>(null)
  const [isRescoring, setIsRescoring] = useState(false)
  const [rescoreError, setRescoreError] = useState<string | null>(null)

  // Initialize editor with parsed resume text (simplified - just show raw text for MVP)
  useEffect(() => {
    if (result) {
      // Convert resume data to editable HTML
      const html = convertResumeToHTML(result)
      setEditorContent(html)
      setCurrentScore(result.score)
    }
  }, [result])

  // Debounce editor content changes (500ms delay)
  const debouncedContent = useDebounce(editorContent, 500)

  // Re-score when debounced content changes
  useEffect(() => {
    if (!result || !debouncedContent) return

    const performRescore = async () => {
      setIsRescoring(true)
      setRescoreError(null)

      try {
        // Count words in HTML content
        const tempDiv = document.createElement('div')
        tempDiv.innerHTML = debouncedContent
        const textContent = tempDiv.textContent || ''
        const wordCount = textContent.split(/\s+/).filter(Boolean).length

        const scoreRequest: ScoreRequest = {
          fileName: result.fileName,
          contact: result.contact,
          experience: result.experience || [],
          education: result.education || [],
          skills: result.skills || [],
          certifications: result.certifications || [],
          metadata: {
            ...result.metadata,
            wordCount
          },
          jobDescription: result.jobDescription,
          industry: result.industry
        }

        const newScore = await rescoreResume(scoreRequest)
        setCurrentScore(newScore)
      } catch (err) {
        setRescoreError(err instanceof Error ? err.message : 'Failed to re-score')
      } finally {
        setIsRescoring(false)
      }
    }

    performRescore()
  }, [debouncedContent, result])

  // Handle editor changes
  const handleEditorChange = useCallback((content: string) => {
    setEditorContent(content)
  }, [])

  if (!result || !currentScore) {
    return null
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        {/* Header */}
        <div className="mb-8">
          <button
            onClick={() => navigate('/results', { state: { result } })}
            className="text-blue-600 hover:text-blue-800 font-medium mb-4 flex items-center"
          >
            ← Back to Results
          </button>
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">
                Edit Your Resume
              </h1>
              <p className="text-gray-600">
                {result.fileName}
              </p>
            </div>
            <div className="text-right">
              {isRescoring && (
                <div className="flex items-center text-blue-600">
                  <LoadingSpinner size="sm" />
                  <span className="ml-2 text-sm">Re-scoring...</span>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Error Message */}
        {rescoreError && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-md">
            <p className="text-sm text-red-800">{rescoreError}</p>
          </div>
        )}

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column: Editor */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">
                Resume Content
              </h2>
              <RichTextEditor
                content={editorContent}
                onChange={handleEditorChange}
                placeholder="Edit your resume content..."
              />
            </div>
          </div>

          {/* Right Column: Live Score */}
          <div className="lg:col-span-1">
            <div className="sticky top-8 space-y-6">
              {/* Score Card */}
              <div className="bg-white rounded-lg shadow-sm p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">
                  Live Score
                </h2>
                <ScoreCard score={currentScore.overallScore} />
              </div>

              {/* Category Breakdown */}
              <div className="bg-white rounded-lg shadow-sm p-6">
                <CategoryBreakdown breakdown={currentScore.breakdown} />
              </div>

              {/* Issues Summary */}
              <div className="bg-white rounded-lg shadow-sm p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
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

        {/* Full Issues List */}
        <div className="mt-6 bg-white rounded-lg shadow-sm p-6">
          <IssuesList issues={currentScore.issues} />
        </div>
      </div>
    </div>
  )
}

/**
 * Convert resume data to editable HTML
 * Simplified version - just basic text formatting
 */
function convertResumeToHTML(result: UploadResponse): string {
  const parts: string[] = []

  // Contact Info
  if (result.contact.name) {
    parts.push(`<h1>${result.contact.name}</h1>`)
  }
  const contactDetails = [
    result.contact.email,
    result.contact.phone,
    result.contact.location,
    result.contact.linkedin
  ].filter(Boolean)
  if (contactDetails.length > 0) {
    parts.push(`<p>${contactDetails.join(' • ')}</p>`)
  }

  // Experience
  if (result.experience && result.experience.length > 0) {
    parts.push('<h2>Experience</h2>')
    result.experience.forEach((exp: any) => {
      parts.push(`<p>${JSON.stringify(exp)}</p>`)
    })
  }

  // Education
  if (result.education && result.education.length > 0) {
    parts.push('<h2>Education</h2>')
    result.education.forEach((edu: any) => {
      parts.push(`<p>${JSON.stringify(edu)}</p>`)
    })
  }

  // Skills
  if (result.skills && result.skills.length > 0) {
    parts.push('<h2>Skills</h2>')
    parts.push(`<p>${result.skills.join(', ')}</p>`)
  }

  return parts.join('\n')
}
```

### Step 4: Add editor route

**Modify `frontend/src/App.tsx`:**
```typescript
import { Routes, Route } from 'react-router-dom'
import ErrorBoundary from './components/ErrorBoundary'
import UploadPage from './components/UploadPage'
import ResultsPage from './components/ResultsPage'
import EditorPage from './components/EditorPage'
import './index.css'

function App() {
  return (
    <ErrorBoundary>
      <Routes>
        <Route path="/" element={<UploadPage />} />
        <Route path="/results" element={<ResultsPage />} />
        <Route path="/editor" element={<EditorPage />} />
      </Routes>
    </ErrorBoundary>
  )
}

export default App
```

### Step 5: Add "Edit Resume" button to ResultsPage

**Modify `frontend/src/components/ResultsPage.tsx`** (update header section):
```typescript
// In the header section, after "Back to Upload" button, add:
<div className="flex items-center justify-between">
  <div>
    <button
      onClick={() => navigate('/')}
      className="text-blue-600 hover:text-blue-800 font-medium mb-4 flex items-center"
    >
      ← Back to Upload
    </button>
    <h1 className="text-3xl font-bold text-gray-900 mb-2">
      Resume Analysis Results
    </h1>
    <p className="text-gray-600">
      {result.fileName}
    </p>
  </div>
  <button
    onClick={() => navigate('/editor', { state: { result } })}
    className="px-6 py-3 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors font-semibold"
  >
    Edit Resume
  </button>
</div>
```

### Step 6: Test editor page

```bash
npm run dev
```

Test flow:
1. Upload resume
2. View results page
3. Click "Edit Resume" button
4. Verify editor loads with resume content
5. Edit text and verify re-scoring triggers after 500ms
6. Verify score updates in real-time
7. Check issues list updates

### Step 7: Commit

```bash
git add frontend/src/components/EditorPage.tsx frontend/src/types/resume.ts frontend/src/api/client.ts frontend/src/App.tsx frontend/src/components/ResultsPage.tsx
git commit -m "feat: add editor page with real-time re-scoring

- Create EditorPage component with split layout
- Add rescoreResume API function
- Add ResumeContent interface
- Implement debounced re-scoring (500ms delay)
- Convert resume data to editable HTML
- Update word count on content change
- Show live score updates
- Add loading indicator during re-scoring
- Add 'Edit Resume' button to results page
- Add /editor route"
```

---

## Task 25: Authentication Integration

**Goal:** Add signup/login functionality with JWT token management

**Files:**
- Create: `frontend/src/contexts/AuthContext.tsx`
- Create: `frontend/src/hooks/useAuth.ts`
- Create: `frontend/src/components/AuthModal.tsx`
- Modify: `frontend/src/api/client.ts`
- Modify: `frontend/src/App.tsx`

### Step 1: Add auth API functions

**Modify `frontend/src/api/client.ts`** (add to existing file):
```typescript
// Add interfaces
export interface SignupRequest {
  email: string
  password: string
}

export interface LoginRequest {
  email: string
  password: string
}

export interface AuthResponse {
  accessToken: string
  tokenType: string
  user: {
    id: string
    email: string
    createdAt: string
  }
}

export interface User {
  id: string
  email: string
  createdAt: string
}

/**
 * Set authentication token for API requests
 */
export function setAuthToken(token: string | null) {
  if (token) {
    apiClient.defaults.headers.common['Authorization'] = `Bearer ${token}`
  } else {
    delete apiClient.defaults.headers.common['Authorization']
  }
}

/**
 * Sign up new user
 */
export async function signup(data: SignupRequest): Promise<AuthResponse> {
  try {
    const response = await apiClient.post<AuthResponse>('/api/signup', data)
    return response.data
  } catch (error) {
    const axiosError = error as AxiosError<ApiError>
    throw new Error(axiosError.response?.data?.detail || 'Signup failed')
  }
}

/**
 * Login existing user
 */
export async function login(data: LoginRequest): Promise<AuthResponse> {
  try {
    const response = await apiClient.post<AuthResponse>('/api/login', data)
    return response.data
  } catch (error) {
    const axiosError = error as AxiosError<ApiError>
    throw new Error(axiosError.response?.data?.detail || 'Login failed')
  }
}

/**
 * Get current user info
 */
export async function getCurrentUser(): Promise<User> {
  try {
    const response = await apiClient.get<User>('/api/me')
    return response.data
  } catch (error) {
    const axiosError = error as AxiosError<ApiError>
    throw new Error(axiosError.response?.data?.detail || 'Failed to get user info')
  }
}
```

### Step 2: Create AuthContext

**Create `frontend/src/contexts/AuthContext.tsx`:**
```typescript
/**
 * Authentication context for managing user state
 */
import { createContext, useState, useEffect, ReactNode } from 'react'
import { signup, login, getCurrentUser, setAuthToken, type SignupRequest, type LoginRequest, type User } from '../api/client'

interface AuthContextType {
  user: User | null
  token: string | null
  isLoading: boolean
  isAuthenticated: boolean
  signup: (data: SignupRequest) => Promise<void>
  login: (data: LoginRequest) => Promise<void>
  logout: () => void
}

export const AuthContext = createContext<AuthContextType | undefined>(undefined)

interface AuthProviderProps {
  children: ReactNode
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null)
  const [token, setToken] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  // Initialize auth from localStorage
  useEffect(() => {
    const storedToken = localStorage.getItem('authToken')
    if (storedToken) {
      setAuthToken(storedToken)
      setToken(storedToken)

      // Fetch user info
      getCurrentUser()
        .then(setUser)
        .catch(() => {
          // Token invalid, clear it
          localStorage.removeItem('authToken')
          setAuthToken(null)
          setToken(null)
        })
        .finally(() => setIsLoading(false))
    } else {
      setIsLoading(false)
    }
  }, [])

  const handleSignup = async (data: SignupRequest) => {
    const response = await signup(data)
    const { accessToken, user: newUser } = response

    localStorage.setItem('authToken', accessToken)
    setAuthToken(accessToken)
    setToken(accessToken)
    setUser(newUser)
  }

  const handleLogin = async (data: LoginRequest) => {
    const response = await login(data)
    const { accessToken, user: loggedInUser } = response

    localStorage.setItem('authToken', accessToken)
    setAuthToken(accessToken)
    setToken(accessToken)
    setUser(loggedInUser)
  }

  const handleLogout = () => {
    localStorage.removeItem('authToken')
    setAuthToken(null)
    setToken(null)
    setUser(null)
  }

  const value: AuthContextType = {
    user,
    token,
    isLoading,
    isAuthenticated: !!user,
    signup: handleSignup,
    login: handleLogin,
    logout: handleLogout
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
```

### Step 3: Create useAuth hook

**Create `frontend/src/hooks/useAuth.ts`:**
```typescript
/**
 * Custom hook for accessing auth context
 */
import { useContext } from 'react'
import { AuthContext } from '../contexts/AuthContext'

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
```

### Step 4: Create AuthModal component

**Create `frontend/src/components/AuthModal.tsx`:**
```typescript
/**
 * Authentication modal for signup/login
 */
import { useState } from 'react'
import { useAuth } from '../hooks/useAuth'

interface AuthModalProps {
  isOpen: boolean
  onClose: () => void
  initialMode?: 'login' | 'signup'
}

export default function AuthModal({ isOpen, onClose, initialMode = 'login' }: AuthModalProps) {
  const { signup, login } = useAuth()
  const [mode, setMode] = useState<'login' | 'signup'>(initialMode)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  if (!isOpen) return null

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)

    // Validation
    if (!email || !password) {
      setError('Email and password are required')
      return
    }

    if (mode === 'signup' && password !== confirmPassword) {
      setError('Passwords do not match')
      return
    }

    setIsSubmitting(true)

    try {
      if (mode === 'signup') {
        await signup({ email, password })
      } else {
        await login({ email, password })
      }
      onClose()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Authentication failed')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-gray-900">
            {mode === 'login' ? 'Login' : 'Sign Up'}
          </h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-2xl"
          >
            ×
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Email */}
          <div>
            <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
              Email
            </label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="you@example.com"
              required
            />
          </div>

          {/* Password */}
          <div>
            <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">
              Password
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="••••••••"
              required
            />
          </div>

          {/* Confirm Password (signup only) */}
          {mode === 'signup' && (
            <div>
              <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700 mb-1">
                Confirm Password
              </label>
              <input
                id="confirmPassword"
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="••••••••"
                required
              />
            </div>
          )}

          {/* Error Message */}
          {error && (
            <div className="p-3 bg-red-50 border border-red-200 rounded-md">
              <p className="text-sm text-red-800">{error}</p>
            </div>
          )}

          {/* Submit Button */}
          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full py-2 px-4 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed font-semibold transition-colors"
          >
            {isSubmitting ? 'Please wait...' : mode === 'login' ? 'Login' : 'Sign Up'}
          </button>
        </form>

        {/* Toggle Mode */}
        <div className="mt-4 text-center text-sm text-gray-600">
          {mode === 'login' ? (
            <p>
              Don't have an account?{' '}
              <button
                type="button"
                onClick={() => setMode('signup')}
                className="text-blue-600 hover:text-blue-800 font-medium"
              >
                Sign up
              </button>
            </p>
          ) : (
            <p>
              Already have an account?{' '}
              <button
                type="button"
                onClick={() => setMode('login')}
                className="text-blue-600 hover:text-blue-800 font-medium"
              >
                Login
              </button>
            </p>
          )}
        </div>
      </div>
    </div>
  )
}
```

### Step 5: Wrap App with AuthProvider

**Modify `frontend/src/App.tsx`:**
```typescript
import { Routes, Route } from 'react-router-dom'
import ErrorBoundary from './components/ErrorBoundary'
import { AuthProvider } from './contexts/AuthContext'
import UploadPage from './components/UploadPage'
import ResultsPage from './components/ResultsPage'
import EditorPage from './components/EditorPage'
import './index.css'

function App() {
  return (
    <ErrorBoundary>
      <AuthProvider>
        <Routes>
          <Route path="/" element={<UploadPage />} />
          <Route path="/results" element={<ResultsPage />} />
          <Route path="/editor" element={<EditorPage />} />
        </Routes>
      </AuthProvider>
    </ErrorBoundary>
  )
}

export default App
```

### Step 6: Add auth UI to pages

**Create `frontend/src/components/UserMenu.tsx`:**
```typescript
/**
 * User menu component for authenticated users
 */
import { useState } from 'react'
import { useAuth } from '../hooks/useAuth'
import AuthModal from './AuthModal'

export default function UserMenu() {
  const { user, isAuthenticated, logout } = useAuth()
  const [showAuthModal, setShowAuthModal] = useState(false)
  const [showDropdown, setShowDropdown] = useState(false)

  if (!isAuthenticated) {
    return (
      <>
        <button
          onClick={() => setShowAuthModal(true)}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors font-medium"
        >
          Login / Sign Up
        </button>
        <AuthModal
          isOpen={showAuthModal}
          onClose={() => setShowAuthModal(false)}
        />
      </>
    )
  }

  return (
    <div className="relative">
      <button
        onClick={() => setShowDropdown(!showDropdown)}
        className="flex items-center gap-2 px-4 py-2 bg-gray-100 rounded-md hover:bg-gray-200 transition-colors"
      >
        <span className="text-sm font-medium text-gray-700">{user?.email}</span>
        <svg className="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {showDropdown && (
        <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg py-1 z-10">
          <button
            onClick={() => {
              logout()
              setShowDropdown(false)
            }}
            className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
          >
            Logout
          </button>
        </div>
      )}
    </div>
  )
}
```

Add UserMenu to page headers (UploadPage, ResultsPage, EditorPage).

### Step 7: Test authentication

```bash
npm run dev
```

Test:
1. Click "Login / Sign Up" button
2. Sign up with email/password
3. Verify modal closes and user menu shows
4. Logout and verify UI updates
5. Login again with same credentials
6. Verify token persists after page refresh

### Step 8: Commit

```bash
git add frontend/src/contexts/ frontend/src/hooks/useAuth.ts frontend/src/components/AuthModal.tsx frontend/src/components/UserMenu.tsx frontend/src/api/client.ts frontend/src/App.tsx
git commit -m "feat: add authentication with JWT token management

- Create AuthContext for user state management
- Create useAuth hook for accessing auth context
- Add signup, login, getCurrentUser API functions
- Add setAuthToken for axios interceptor
- Create AuthModal component for signup/login
- Create UserMenu component with dropdown
- Store JWT token in localStorage
- Auto-load user on app init
- Add logout functionality
- Wrap App with AuthProvider
- Add auth UI to page headers"
```

---

## Task 26: Save/Load Resume & Ad Integration

**Goal:** Add save/load functionality for authenticated users and ad integration logic

**Files:**
- Modify: `frontend/src/api/client.ts`
- Modify: `frontend/src/components/EditorPage.tsx`
- Create: `frontend/src/components/SavedResumesList.tsx`
- Create: `frontend/src/components/AdDisplay.tsx`

### Step 1: Add resume CRUD API functions

**Modify `frontend/src/api/client.ts`** (add to existing file):
```typescript
// Add interfaces
export interface SavedResume {
  id: string
  fileName: string
  content: any
  score: ScoreResult
  createdAt: string
  updatedAt: string
}

/**
 * Save resume for authenticated user
 */
export async function saveResume(data: ScoreRequest): Promise<SavedResume> {
  try {
    const response = await apiClient.post<SavedResume>('/api/resumes', data)
    return response.data
  } catch (error) {
    const axiosError = error as AxiosError<ApiError>
    throw new Error(axiosError.response?.data?.detail || 'Failed to save resume')
  }
}

/**
 * Get all saved resumes
 */
export async function getSavedResumes(): Promise<SavedResume[]> {
  try {
    const response = await apiClient.get<SavedResume[]>('/api/resumes')
    return response.data
  } catch (error) {
    const axiosError = error as AxiosError<ApiError>
    throw new Error(axiosError.response?.data?.detail || 'Failed to load resumes')
  }
}

/**
 * Get single saved resume
 */
export async function getSavedResume(id: string): Promise<SavedResume> {
  try {
    const response = await apiClient.get<SavedResume>(`/api/resumes/${id}`)
    return response.data
  } catch (error) {
    const axiosError = error as AxiosError<ApiError>
    throw new Error(axiosError.response?.data?.detail || 'Failed to load resume')
  }
}

/**
 * Update saved resume
 */
export async function updateResume(id: string, data: ScoreRequest): Promise<SavedResume> {
  try {
    const response = await apiClient.put<SavedResume>(`/api/resumes/${id}`, data)
    return response.data
  } catch (error) {
    const axiosError = error as AxiosError<ApiError>
    throw new Error(axiosError.response?.data?.detail || 'Failed to update resume')
  }
}

/**
 * Delete saved resume
 */
export async function deleteResume(id: string): Promise<void> {
  try {
    await apiClient.delete(`/api/resumes/${id}`)
  } catch (error) {
    const axiosError = error as AxiosError<ApiError>
    throw new Error(axiosError.response?.data?.detail || 'Failed to delete resume')
  }
}
```

### Step 2: Add ad tracking API functions

**Modify `frontend/src/api/client.ts`** (add to existing file):
```typescript
/**
 * Check if ad should be shown
 */
export async function shouldShowAd(): Promise<{ showAd: boolean; message?: string }> {
  try {
    const response = await apiClient.get<{ showAd: boolean; message?: string }>('/api/should-show-ad')
    return response.data
  } catch (error) {
    // If not authenticated, show ad after first score
    return { showAd: true, message: 'Ad required for additional scoring' }
  }
}

/**
 * Track ad view
 */
export async function trackAdView(): Promise<void> {
  try {
    await apiClient.post('/api/ad-view')
  } catch (error) {
    console.error('Failed to track ad view:', error)
  }
}
```

### Step 3: Create AdDisplay component

**Create `frontend/src/components/AdDisplay.tsx`:**
```typescript
/**
 * Ad display component (placeholder for MVP)
 */
import { useEffect } from 'react'
import { trackAdView } from '../api/client'

interface AdDisplayProps {
  onAdViewed: () => void
}

export default function AdDisplay({ onAdViewed }: AdDisplayProps) {
  useEffect(() => {
    // Track ad view on mount
    trackAdView()

    // Simulate ad view delay (3 seconds)
    const timer = setTimeout(() => {
      onAdViewed()
    }, 3000)

    return () => clearTimeout(timer)
  }, [onAdViewed])

  return (
    <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-8 text-center">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">
          Advertisement
        </h2>
        <div className="bg-gray-200 h-64 flex items-center justify-center mb-4 rounded">
          <p className="text-gray-500">
            [Ad Space - 300x250]
          </p>
        </div>
        <p className="text-sm text-gray-600 mb-4">
          Thanks for using our service! This ad helps keep it free.
        </p>
        <div className="flex items-center justify-center gap-2 text-sm text-gray-500">
          <svg className="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <span>Continuing in 3 seconds...</span>
        </div>
      </div>
    </div>
  )
}
```

### Step 4: Integrate ad logic into EditorPage

**Modify `frontend/src/components/EditorPage.tsx`** (add ad logic):
```typescript
// Add imports
import { shouldShowAd, saveResume, updateResume } from '../api/client'
import { useAuth } from '../hooks/useAuth'
import AdDisplay from './AdDisplay'

// Add state
const { isAuthenticated } = useAuth()
const [showAd, setShowAd] = useState(false)
const [adCheckPending, setAdCheckPending] = useState(false)
const [savedResumeId, setSavedResumeId] = useState<string | null>(null)
const [isSaving, setIsSaving] = useState(false)

// Modify re-score effect to check for ads
useEffect(() => {
  if (!result || !debouncedContent) return

  const performRescore = async () => {
    // Check if ad should be shown
    if (!adCheckPending) {
      setAdCheckPending(true)
      try {
        const adCheck = await shouldShowAd()
        if (adCheck.showAd) {
          setShowAd(true)
          return // Don't re-score until ad is viewed
        }
      } catch (err) {
        console.error('Ad check failed:', err)
      }
    }

    setIsRescoring(true)
    setRescoreError(null)

    try {
      // ... existing re-score logic
    } catch (err) {
      setRescoreError(err instanceof Error ? err.message : 'Failed to re-score')
    } finally {
      setIsRescoring(false)
    }
  }

  performRescore()
}, [debouncedContent, result, adCheckPending])

// Add save handler
const handleSave = async () => {
  if (!isAuthenticated) {
    alert('Please login to save your resume')
    return
  }

  setIsSaving(true)
  try {
    const tempDiv = document.createElement('div')
    tempDiv.innerHTML = editorContent
    const textContent = tempDiv.textContent || ''
    const wordCount = textContent.split(/\s+/).filter(Boolean).length

    const scoreRequest: ScoreRequest = {
      fileName: result.fileName,
      contact: result.contact,
      experience: result.experience || [],
      education: result.education || [],
      skills: result.skills || [],
      certifications: result.certifications || [],
      metadata: {
        ...result.metadata,
        wordCount
      },
      jobDescription: result.jobDescription,
      industry: result.industry
    }

    if (savedResumeId) {
      await updateResume(savedResumeId, scoreRequest)
    } else {
      const saved = await saveResume(scoreRequest)
      setSavedResumeId(saved.id)
    }

    alert('Resume saved successfully!')
  } catch (err) {
    alert(err instanceof Error ? err.message : 'Failed to save resume')
  } finally {
    setIsSaving(false)
  }
}

// Add ad viewed handler
const handleAdViewed = () => {
  setShowAd(false)
  setAdCheckPending(false)
}

// Add to JSX (before closing div):
{showAd && <AdDisplay onAdViewed={handleAdViewed} />}

// Add save button to header:
<button
  onClick={handleSave}
  disabled={isSaving || !isAuthenticated}
  className="px-6 py-3 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors font-semibold"
>
  {isSaving ? 'Saving...' : savedResumeId ? 'Update' : 'Save'}
</button>
```

### Step 5: Create SavedResumesList component

**Create `frontend/src/components/SavedResumesList.tsx`:**
```typescript
/**
 * List of saved resumes for authenticated users
 */
import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { getSavedResumes, deleteResume, type SavedResume } from '../api/client'
import { useAuth } from '../hooks/useAuth'
import LoadingSpinner from './LoadingSpinner'

export default function SavedResumesList() {
  const navigate = useNavigate()
  const { isAuthenticated } = useAuth()
  const [resumes, setResumes] = useState<SavedResume[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!isAuthenticated) {
      setIsLoading(false)
      return
    }

    loadResumes()
  }, [isAuthenticated])

  const loadResumes = async () => {
    setIsLoading(true)
    setError(null)
    try {
      const data = await getSavedResumes()
      setResumes(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load resumes')
    } finally {
      setIsLoading(false)
    }
  }

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this resume?')) {
      return
    }

    try {
      await deleteResume(id)
      setResumes(resumes.filter(r => r.id !== id))
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to delete resume')
    }
  }

  if (!isAuthenticated) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-600 mb-4">Login to save and access your resumes</p>
      </div>
    )
  }

  if (isLoading) {
    return (
      <div className="flex justify-center py-12">
        <LoadingSpinner size="lg" text="Loading resumes..." />
      </div>
    )
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-red-600">{error}</p>
        <button
          onClick={loadResumes}
          className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
        >
          Retry
        </button>
      </div>
    )
  }

  if (resumes.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-600">No saved resumes yet</p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {resumes.map((resume) => (
        <div
          key={resume.id}
          className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
        >
          <div className="flex items-center justify-between">
            <div className="flex-1">
              <h3 className="font-semibold text-gray-900">{resume.fileName}</h3>
              <p className="text-sm text-gray-600">
                Score: {resume.score.overallScore}/100
              </p>
              <p className="text-xs text-gray-500">
                Updated: {new Date(resume.updatedAt).toLocaleDateString()}
              </p>
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => navigate('/editor', { state: { result: resume } })}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 text-sm"
              >
                Edit
              </button>
              <button
                onClick={() => handleDelete(resume.id)}
                className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 text-sm"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}
```

### Step 6: Add saved resumes page

**Modify `frontend/src/App.tsx`** (add route):
```typescript
import SavedResumesPage from './components/SavedResumesPage'

// In Routes:
<Route path="/my-resumes" element={<SavedResumesPage />} />
```

**Create `frontend/src/components/SavedResumesPage.tsx`:**
```typescript
/**
 * Page for viewing saved resumes
 */
import { useNavigate } from 'react-router-dom'
import SavedResumesList from './SavedResumesList'
import UserMenu from './UserMenu'

export default function SavedResumesPage() {
  const navigate = useNavigate()

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8 max-w-4xl">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <button
              onClick={() => navigate('/')}
              className="text-blue-600 hover:text-blue-800 font-medium mb-4 flex items-center"
            >
              ← Back to Upload
            </button>
            <h1 className="text-3xl font-bold text-gray-900">
              My Saved Resumes
            </h1>
          </div>
          <UserMenu />
        </div>

        {/* Saved Resumes List */}
        <SavedResumesList />
      </div>
    </div>
  )
}
```

### Step 7: Add "My Resumes" link to UserMenu

**Modify `frontend/src/components/UserMenu.tsx`:**
```typescript
// In dropdown, before Logout button:
<button
  onClick={() => {
    navigate('/my-resumes')
    setShowDropdown(false)
  }}
  className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
>
  My Resumes
</button>
```

### Step 8: Test save/load and ad functionality

```bash
npm run dev
```

Test:
1. Login as authenticated user
2. Edit resume and click "Save" button
3. Navigate to "My Resumes" page
4. Verify saved resume appears in list
5. Click "Edit" to load saved resume
6. Update and save again
7. Logout and edit resume - verify ad shows before re-scoring
8. View ad for 3 seconds, verify re-scoring continues after

### Step 9: Commit

```bash
git add frontend/src/api/client.ts frontend/src/components/EditorPage.tsx frontend/src/components/SavedResumesList.tsx frontend/src/components/SavedResumesPage.tsx frontend/src/components/AdDisplay.tsx frontend/src/components/UserMenu.tsx frontend/src/App.tsx
git commit -m "feat: add save/load functionality and ad integration

- Add resume CRUD API functions (save, get, update, delete)
- Add ad tracking API functions (shouldShowAd, trackAdView)
- Create AdDisplay component with 3-second delay
- Integrate ad check into re-scoring flow
- Add save/update functionality to EditorPage
- Create SavedResumesList component
- Create SavedResumesPage for managing saved resumes
- Add 'My Resumes' link to UserMenu
- Add /my-resumes route
- First score free, ads for subsequent re-scoring
- Premium users (future) exempt from ads"
```

---

## Verification

### Run full stack

**Terminal 1 - Backend:**
```bash
cd /Users/sabuj.mondal/ats-resume-scorer/backend
python -m uvicorn backend.main:app --reload
```

**Terminal 2 - Frontend:**
```bash
cd /Users/sabuj.mondal/ats-resume-scorer/frontend
npm run dev
```

### Test complete Phase 7 flow

1. **Upload & Initial Score**
   - Upload resume on homepage
   - Get initial score (first score is free)
   - Click "Edit Resume" button

2. **Editor Page**
   - Verify editor loads with resume content
   - Edit text using toolbar (bold, italic, headings, lists)
   - Verify score updates in real-time after 500ms
   - Check live issues list updates

3. **Authentication**
   - Click "Login / Sign Up"
   - Sign up with new account
   - Verify modal closes and user menu appears
   - Logout and login again

4. **Save/Load**
   - Login
   - Edit resume and click "Save"
   - Verify success message
   - Go to "My Resumes" page
   - Verify resume appears in list
   - Click "Edit" to load
   - Make changes and click "Update"

5. **Ad Integration**
   - Logout
   - Edit resume (first edit is free)
   - Edit again - verify ad appears
   - Wait 3 seconds
   - Verify re-scoring continues after ad

---

## Final Commit

```bash
git add .
git commit -m "chore: Phase 7 Frontend Rich Text Editor complete

Summary:
- TipTap rich text editor with formatting toolbar
- Bold, italic, strikethrough, headings, lists
- Horizontal rule, undo, redo
- Real-time re-scoring with 500ms debounce
- Live score updates in sidebar
- Authentication with JWT token management
- Signup/login modal with email/password
- Token persistence in localStorage
- Save/load functionality for authenticated users
- My Resumes page with CRUD operations
- Ad integration (first score free, ads for re-scoring)
- Ad display component with 3-second delay
- Premium users exempt (future enhancement)

Phase 7 complete - full ATS Resume Scorer MVP ready!"
```

---

## Success Metrics

Phase 7 is complete when:
- ✅ TipTap editor renders with toolbar
- ✅ Formatting buttons work (bold, italic, headings, lists)
- ✅ Editor content is editable
- ✅ Re-scoring triggers after 500ms of no changes
- ✅ Score updates live in sidebar
- ✅ Signup/login modal works
- ✅ JWT token persists after refresh
- ✅ User can save edited resume
- ✅ Saved resumes appear in "My Resumes" page
- ✅ User can load and edit saved resumes
- ✅ Ad displays before re-scoring (non-authenticated)
- ✅ Ad can be bypassed after 3 seconds
- ✅ Re-scoring continues after ad view

**MVP Complete!** All core features implemented:
1. ✅ Resume upload (PDF/DOCX)
2. ✅ 100-point ATS scoring system
3. ✅ Rich text editor for resume editing
4. ✅ Real-time re-scoring
5. ✅ Authentication & user accounts
6. ✅ Save/load functionality
7. ✅ Ad integration (first score free)

**Future Enhancements:**
- Phase 8: Premium subscription (ad-free, unlimited scoring)
- Phase 9: Resume templates library
- Phase 10: AI-powered improvement suggestions
- Phase 11: Export to PDF with formatting
