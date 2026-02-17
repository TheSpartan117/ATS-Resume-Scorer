# Phase 6: Frontend Upload & Display - Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build React UI for resume upload, file validation, score display, and results visualization

**Architecture:** React 19 + TypeScript + Tailwind CSS frontend. Component-based architecture with API integration via axios. File upload with drag-and-drop, score visualization with progress bars and issue cards, responsive design.

**Tech Stack:** React 19, TypeScript, Vite, Tailwind CSS, Axios, React Router

---

## Context

**Current State:**
- Backend API complete (Phase 5): 14 endpoints working
- Frontend scaffold exists: React 19 + TypeScript + Tailwind CSS + Vite
- Basic App.tsx with header
- No components, no routing, no API integration yet

**What We're Building:**
Phase 6 focuses on Upload & Display (Phase 7 will add the editor):
1. **Upload Page**: File drop zone, job description textarea, industry selector
2. **Results Page**: Score display, category breakdown, issues list, metadata
3. **API Integration**: Axios client for backend communication
4. **Routing**: React Router for page navigation
5. **Component Library**: Reusable UI components

---

## Task 17: Project Setup & Dependencies

**Goal:** Install required dependencies and configure API client

**Files:**
- Modify: `frontend/package.json`
- Create: `frontend/src/api/client.ts`
- Create: `frontend/src/types/resume.ts`

### Step 1: Install dependencies

```bash
cd /Users/sabuj.mondal/ats-resume-scorer/frontend
npm install axios react-router-dom
npm install --save-dev @types/react-router-dom
```

**Expected:** Dependencies installed successfully

### Step 2: Create TypeScript types

**Create `frontend/src/types/resume.ts`:**
```typescript
/**
 * TypeScript types for ATS Resume Scorer
 */

export interface ContactInfo {
  name?: string
  email?: string
  phone?: string
  location?: string
  linkedin?: string
  website?: string
}

export interface ResumeMetadata {
  pageCount: number
  wordCount: number
  hasPhoto: boolean
  fileFormat: string
}

export interface CategoryBreakdown {
  score: number
  maxScore: number
  issues: string[]
}

export interface ScoreBreakdown {
  contactInfo: CategoryBreakdown
  formatting: CategoryBreakdown
  keywords: CategoryBreakdown
  content: CategoryBreakdown
  lengthDensity: CategoryBreakdown
  industrySpecific: CategoryBreakdown
}

export interface ScoreResult {
  overallScore: number
  breakdown: ScoreBreakdown
  issues: {
    critical: string[]
    warnings: string[]
    suggestions: string[]
    info: string[]
  }
  strengths: string[]
}

export interface UploadResponse {
  resumeId?: string
  fileName: string
  contact: ContactInfo
  metadata: ResumeMetadata
  score: ScoreResult
  uploadedAt: string
}

export interface ApiError {
  detail: string
}
```

### Step 3: Create API client

**Create `frontend/src/api/client.ts`:**
```typescript
/**
 * API client for backend communication
 */
import axios, { AxiosError } from 'axios'
import type { UploadResponse, ApiError } from '../types/resume'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 seconds
})

/**
 * Upload resume file and get initial score
 */
export async function uploadResume(
  file: File,
  jobDescription?: string,
  industry?: string
): Promise<UploadResponse> {
  const formData = new FormData()
  formData.append('file', file)

  if (jobDescription) {
    formData.append('jobDescription', jobDescription)
  }

  if (industry) {
    formData.append('industry', industry)
  }

  try {
    const response = await apiClient.post<UploadResponse>('/api/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  } catch (error) {
    const axiosError = error as AxiosError<ApiError>
    throw new Error(axiosError.response?.data?.detail || 'Failed to upload resume')
  }
}

/**
 * Health check
 */
export async function healthCheck(): Promise<{ status: string }> {
  const response = await apiClient.get('/health')
  return response.data
}

export default apiClient
```

### Step 4: Create environment file

**Create `frontend/.env.example`:**
```
VITE_API_URL=http://localhost:8000
```

**Create `frontend/.env`:**
```
VITE_API_URL=http://localhost:8000
```

### Step 5: Update .gitignore

**Modify `frontend/.gitignore`** (add if not present):
```
.env
.env.local
```

### Step 6: Test API connection

```bash
cd /Users/sabuj.mondal/ats-resume-scorer/frontend
npm run dev
```

Open browser console and test:
```javascript
fetch('http://localhost:8000/health').then(r => r.json()).then(console.log)
```

**Expected:** `{status: "healthy"}`

### Step 7: Commit

```bash
git add frontend/package.json frontend/package-lock.json frontend/src/api/ frontend/src/types/ frontend/.env.example frontend/.gitignore
git commit -m "feat: setup frontend dependencies and API client

- Install axios and react-router-dom
- Create TypeScript types for resume data
- Create API client with uploadResume function
- Add environment variable configuration
- Add health check function"
```

---

## Task 18: Upload Page Component

**Goal:** Create file upload component with drag-and-drop

**Files:**
- Create: `frontend/src/components/UploadPage.tsx`
- Create: `frontend/src/components/FileDropZone.tsx`

### Step 1: Create FileDropZone component

**Create `frontend/src/components/FileDropZone.tsx`:**
```typescript
/**
 * File drop zone component for PDF/DOCX upload
 */
import { useState, useCallback } from 'react'

interface FileDropZoneProps {
  onFileSelect: (file: File) => void
  accept?: string
  maxSize?: number // in MB
}

export default function FileDropZone({
  onFileSelect,
  accept = '.pdf,.docx',
  maxSize = 10
}: FileDropZoneProps) {
  const [isDragging, setIsDragging] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const validateFile = (file: File): boolean => {
    setError(null)

    // Check file type
    const extension = file.name.split('.').pop()?.toLowerCase()
    if (!['pdf', 'docx'].includes(extension || '')) {
      setError('Please upload a PDF or DOCX file')
      return false
    }

    // Check file size
    const fileSizeMB = file.size / (1024 * 1024)
    if (fileSizeMB > maxSize) {
      setError(`File too large. Maximum size is ${maxSize}MB`)
      return false
    }

    return true
  }

  const handleDrop = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    setIsDragging(false)

    const files = Array.from(e.dataTransfer.files)
    if (files.length > 0) {
      const file = files[0]
      if (validateFile(file)) {
        onFileSelect(file)
      }
    }
  }, [onFileSelect, maxSize])

  const handleDragOver = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    setIsDragging(true)
  }, [])

  const handleDragLeave = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    setIsDragging(false)
  }, [])

  const handleFileInput = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files
    if (files && files.length > 0) {
      const file = files[0]
      if (validateFile(file)) {
        onFileSelect(file)
      }
    }
  }, [onFileSelect, maxSize])

  return (
    <div>
      <div
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        className={`
          border-2 border-dashed rounded-lg p-12 text-center cursor-pointer
          transition-colors duration-200
          ${isDragging
            ? 'border-blue-500 bg-blue-50'
            : 'border-gray-300 hover:border-gray-400'
          }
        `}
      >
        <input
          type="file"
          id="file-upload"
          accept={accept}
          onChange={handleFileInput}
          className="hidden"
        />

        <label htmlFor="file-upload" className="cursor-pointer">
          <svg
            className="mx-auto h-12 w-12 text-gray-400"
            stroke="currentColor"
            fill="none"
            viewBox="0 0 48 48"
            aria-hidden="true"
          >
            <path
              d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
              strokeWidth={2}
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
          <p className="mt-2 text-sm text-gray-600">
            <span className="font-semibold text-blue-600">Click to upload</span> or drag and drop
          </p>
          <p className="text-xs text-gray-500 mt-1">
            PDF or DOCX (Max {maxSize}MB)
          </p>
        </label>
      </div>

      {error && (
        <p className="mt-2 text-sm text-red-600">{error}</p>
      )}
    </div>
  )
}
```

### Step 2: Create UploadPage component

**Create `frontend/src/components/UploadPage.tsx`:**
```typescript
/**
 * Upload page component
 */
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import FileDropZone from './FileDropZone'
import { uploadResume } from '../api/client'
import type { UploadResponse } from '../types/resume'

export default function UploadPage() {
  const navigate = useNavigate()
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [jobDescription, setJobDescription] = useState('')
  const [industry, setIndustry] = useState('')
  const [isUploading, setIsUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleFileSelect = (file: File) => {
    setSelectedFile(file)
    setError(null)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!selectedFile) {
      setError('Please select a file to upload')
      return
    }

    setIsUploading(true)
    setError(null)

    try {
      const result: UploadResponse = await uploadResume(
        selectedFile,
        jobDescription || undefined,
        industry || undefined
      )

      // Navigate to results page with data
      navigate('/results', { state: { result } })
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to upload resume')
    } finally {
      setIsUploading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8 max-w-3xl">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            ATS Resume Scorer
          </h1>
          <p className="text-lg text-gray-600">
            Upload your resume and get instant ATS compatibility score
          </p>
          <p className="text-sm text-gray-500 mt-2">
            First score is free • No signup required
          </p>
        </div>

        {/* Upload Form */}
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* File Upload */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">
              Upload Resume
            </h2>
            <FileDropZone onFileSelect={handleFileSelect} />

            {selectedFile && (
              <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded-md">
                <p className="text-sm text-green-800">
                  ✓ <span className="font-medium">{selectedFile.name}</span> selected
                  <button
                    type="button"
                    onClick={() => setSelectedFile(null)}
                    className="ml-2 text-green-600 hover:text-green-800 text-xs underline"
                  >
                    Remove
                  </button>
                </p>
              </div>
            )}
          </div>

          {/* Job Description (Optional) */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            <label htmlFor="jobDescription" className="block text-lg font-semibold text-gray-900 mb-2">
              Job Description <span className="text-sm font-normal text-gray-500">(Optional)</span>
            </label>
            <p className="text-sm text-gray-600 mb-3">
              Paste the job description to get keyword matching analysis
            </p>
            <textarea
              id="jobDescription"
              rows={6}
              value={jobDescription}
              onChange={(e) => setJobDescription(e.target.value)}
              placeholder="Looking for a Senior Software Engineer with 5+ years of experience in React, TypeScript, and Node.js..."
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {/* Industry (Optional) */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            <label htmlFor="industry" className="block text-lg font-semibold text-gray-900 mb-2">
              Industry <span className="text-sm font-normal text-gray-500">(Optional)</span>
            </label>
            <p className="text-sm text-gray-600 mb-3">
              Select your target industry for tailored scoring
            </p>
            <select
              id="industry"
              value={industry}
              onChange={(e) => setIndustry(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">Select industry...</option>
              <option value="tech">Technology / Software</option>
              <option value="sales">Sales / Marketing</option>
              <option value="finance">Finance / Accounting</option>
              <option value="healthcare">Healthcare</option>
              <option value="education">Education</option>
              <option value="other">Other</option>
            </select>
          </div>

          {/* Error Message */}
          {error && (
            <div className="p-4 bg-red-50 border border-red-200 rounded-md">
              <p className="text-sm text-red-800">{error}</p>
            </div>
          )}

          {/* Submit Button */}
          <button
            type="submit"
            disabled={!selectedFile || isUploading}
            className={`
              w-full py-3 px-4 rounded-md font-semibold text-white
              transition-colors duration-200
              ${selectedFile && !isUploading
                ? 'bg-blue-600 hover:bg-blue-700 cursor-pointer'
                : 'bg-gray-300 cursor-not-allowed'
              }
            `}
          >
            {isUploading ? (
              <span className="flex items-center justify-center">
                <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Analyzing Resume...
              </span>
            ) : (
              'Get ATS Score'
            )}
          </button>
        </form>
      </div>
    </div>
  )
}
```

### Step 3: Test component (manual)

```bash
npm run dev
```

Open http://localhost:5173, verify:
- File drop zone renders
- Can select file via click
- Can drag and drop file
- Job description textarea works
- Industry dropdown works
- Submit button enables when file selected

### Step 4: Commit

```bash
git add frontend/src/components/
git commit -m "feat: implement upload page with file drop zone

- Create FileDropZone component with drag-and-drop
- File type validation (PDF/DOCX only)
- File size validation (max 10MB)
- Create UploadPage with form
- Add job description textarea (optional)
- Add industry dropdown (optional)
- Loading state with spinner
- Error handling and display"
```

---

## Task 19: Results Page Component

**Goal:** Create results page to display score and breakdown

**Files:**
- Create: `frontend/src/components/ResultsPage.tsx`
- Create: `frontend/src/components/ScoreCard.tsx`
- Create: `frontend/src/components/CategoryBreakdown.tsx`
- Create: `frontend/src/components/IssuesList.tsx`

### Step 1: Create ScoreCard component

**Create `frontend/src/components/ScoreCard.tsx`:**
```typescript
/**
 * Overall score display component
 */
interface ScoreCardProps {
  score: number
}

export default function ScoreCard({ score }: ScoreCardProps) {
  const getScoreColor = (score: number): string => {
    if (score >= 80) return 'text-green-600'
    if (score >= 60) return 'text-yellow-600'
    return 'text-red-600'
  }

  const getScoreLabel = (score: number): string => {
    if (score >= 80) return 'Excellent'
    if (score >= 60) return 'Good'
    if (score >= 40) return 'Fair'
    return 'Needs Work'
  }

  const getScoreBgColor = (score: number): string => {
    if (score >= 80) return 'bg-green-50'
    if (score >= 60) return 'bg-yellow-50'
    return 'bg-red-50'
  }

  return (
    <div className={`rounded-lg p-8 text-center ${getScoreBgColor(score)}`}>
      <h2 className="text-lg font-semibold text-gray-700 mb-2">
        ATS Compatibility Score
      </h2>
      <div className={`text-6xl font-bold ${getScoreColor(score)} mb-2`}>
        {score}
        <span className="text-3xl">/100</span>
      </div>
      <p className={`text-xl font-semibold ${getScoreColor(score)}`}>
        {getScoreLabel(score)}
      </p>
    </div>
  )
}
```

### Step 2: Create CategoryBreakdown component

**Create `frontend/src/components/CategoryBreakdown.tsx`:**
```typescript
/**
 * Category-by-category score breakdown
 */
import type { ScoreBreakdown } from '../types/resume'

interface CategoryBreakdownProps {
  breakdown: ScoreBreakdown
}

interface CategoryDisplay {
  key: keyof ScoreBreakdown
  label: string
  description: string
}

const categories: CategoryDisplay[] = [
  {
    key: 'contactInfo',
    label: 'Contact Information',
    description: 'Name, email, phone, location, links'
  },
  {
    key: 'formatting',
    label: 'Formatting & Structure',
    description: 'Page count, sections, consistency'
  },
  {
    key: 'keywords',
    label: 'Keyword Optimization',
    description: 'Match with job description'
  },
  {
    key: 'content',
    label: 'Content Quality',
    description: 'Action verbs, achievements, buzzwords'
  },
  {
    key: 'lengthDensity',
    label: 'Length & Density',
    description: 'Word count, white space'
  },
  {
    key: 'industrySpecific',
    label: 'Industry-Specific',
    description: 'Role-specific requirements'
  }
]

export default function CategoryBreakdown({ breakdown }: CategoryBreakdownProps) {
  const getPercentage = (score: number, maxScore: number): number => {
    return Math.round((score / maxScore) * 100)
  }

  const getBarColor = (percentage: number): string => {
    if (percentage >= 80) return 'bg-green-500'
    if (percentage >= 60) return 'bg-yellow-500'
    return 'bg-red-500'
  }

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">
        Category Breakdown
      </h3>

      {categories.map((category) => {
        const categoryData = breakdown[category.key]
        const percentage = getPercentage(categoryData.score, categoryData.maxScore)

        return (
          <div key={category.key} className="border-b border-gray-200 pb-4 last:border-0">
            <div className="flex justify-between items-start mb-2">
              <div className="flex-1">
                <h4 className="font-semibold text-gray-900">{category.label}</h4>
                <p className="text-sm text-gray-600">{category.description}</p>
              </div>
              <div className="text-right ml-4">
                <span className="text-lg font-bold text-gray-900">
                  {categoryData.score}/{categoryData.maxScore}
                </span>
              </div>
            </div>

            {/* Progress Bar */}
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className={`h-2 rounded-full transition-all duration-500 ${getBarColor(percentage)}`}
                style={{ width: `${percentage}%` }}
              />
            </div>

            {/* Category-specific issues */}
            {categoryData.issues.length > 0 && (
              <ul className="mt-2 space-y-1">
                {categoryData.issues.map((issue, idx) => (
                  <li key={idx} className="text-sm text-gray-700 flex items-start">
                    <span className="text-red-500 mr-2">•</span>
                    <span>{issue}</span>
                  </li>
                ))}
              </ul>
            )}
          </div>
        )
      })}
    </div>
  )
}
```

### Step 3: Create IssuesList component

**Create `frontend/src/components/IssuesList.tsx`:**
```typescript
/**
 * Issues list component with severity badges
 */
interface IssuesListProps {
  issues: {
    critical: string[]
    warnings: string[]
    suggestions: string[]
    info: string[]
  }
}

interface IssueCategory {
  key: keyof IssuesListProps['issues']
  label: string
  icon: string
  bgColor: string
  textColor: string
  badgeColor: string
}

const issueCategories: IssueCategory[] = [
  {
    key: 'critical',
    label: 'Critical Issues',
    icon: '⚠️',
    bgColor: 'bg-red-50',
    textColor: 'text-red-900',
    badgeColor: 'bg-red-100 text-red-800'
  },
  {
    key: 'warnings',
    label: 'Warnings',
    icon: '⚡',
    bgColor: 'bg-yellow-50',
    textColor: 'text-yellow-900',
    badgeColor: 'bg-yellow-100 text-yellow-800'
  },
  {
    key: 'suggestions',
    label: 'Suggestions',
    icon: '💡',
    bgColor: 'bg-blue-50',
    textColor: 'text-blue-900',
    badgeColor: 'bg-blue-100 text-blue-800'
  },
  {
    key: 'info',
    label: 'Info',
    icon: 'ℹ️',
    bgColor: 'bg-gray-50',
    textColor: 'text-gray-900',
    badgeColor: 'bg-gray-100 text-gray-800'
  }
]

export default function IssuesList({ issues }: IssuesListProps) {
  const totalIssues = Object.values(issues).reduce((sum, arr) => sum + arr.length, 0)

  if (totalIssues === 0) {
    return (
      <div className="text-center py-8 text-gray-600">
        <p className="text-lg">✨ No issues found! Your resume looks great!</p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">
        Issues & Recommendations ({totalIssues})
      </h3>

      {issueCategories.map((category) => {
        const categoryIssues = issues[category.key]

        if (categoryIssues.length === 0) {
          return null
        }

        return (
          <div key={category.key} className={`rounded-lg p-4 ${category.bgColor}`}>
            <div className="flex items-center mb-3">
              <span className="text-2xl mr-2">{category.icon}</span>
              <h4 className={`font-semibold ${category.textColor}`}>
                {category.label}
              </h4>
              <span className={`ml-auto px-2 py-1 text-xs font-semibold rounded-full ${category.badgeColor}`}>
                {categoryIssues.length}
              </span>
            </div>

            <ul className="space-y-2">
              {categoryIssues.map((issue, idx) => (
                <li key={idx} className={`text-sm ${category.textColor} flex items-start`}>
                  <span className="mr-2 mt-0.5">•</span>
                  <span>{issue}</span>
                </li>
              ))}
            </ul>
          </div>
        )
      })}
    </div>
  )
}
```

### Step 4: Create ResultsPage component

**Create `frontend/src/components/ResultsPage.tsx`:**
```typescript
/**
 * Results page component
 */
import { useLocation, useNavigate } from 'react-router-dom'
import { useEffect } from 'react'
import type { UploadResponse } from '../types/resume'
import ScoreCard from './ScoreCard'
import CategoryBreakdown from './CategoryBreakdown'
import IssuesList from './IssuesList'

export default function ResultsPage() {
  const location = useLocation()
  const navigate = useNavigate()
  const result = location.state?.result as UploadResponse | undefined

  useEffect(() => {
    // Redirect if no result data
    if (!result) {
      navigate('/')
    }
  }, [result, navigate])

  if (!result) {
    return null
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8 max-w-6xl">
        {/* Header */}
        <div className="mb-8">
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

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column: Score Card */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-sm p-6 sticky top-8">
              <ScoreCard score={result.score.overallScore} />

              {/* Metadata */}
              <div className="mt-6 pt-6 border-t border-gray-200 space-y-3">
                <h3 className="font-semibold text-gray-900 mb-3">Resume Info</h3>
                <div className="text-sm space-y-2">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Pages:</span>
                    <span className="font-medium">{result.metadata.pageCount}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Words:</span>
                    <span className="font-medium">{result.metadata.wordCount}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Format:</span>
                    <span className="font-medium uppercase">{result.metadata.fileFormat}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Photo:</span>
                    <span className="font-medium">
                      {result.metadata.hasPhoto ? '❌ Yes' : '✓ No'}
                    </span>
                  </div>
                </div>
              </div>

              {/* Contact Info */}
              {result.contact.name && (
                <div className="mt-6 pt-6 border-t border-gray-200">
                  <h3 className="font-semibold text-gray-900 mb-3">Contact</h3>
                  <div className="text-sm space-y-1 text-gray-700">
                    {result.contact.name && <p>{result.contact.name}</p>}
                    {result.contact.email && <p>{result.contact.email}</p>}
                    {result.contact.phone && <p>{result.contact.phone}</p>}
                    {result.contact.location && <p>{result.contact.location}</p>}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Right Column: Details */}
          <div className="lg:col-span-2 space-y-6">
            {/* Category Breakdown */}
            <div className="bg-white rounded-lg shadow-sm p-6">
              <CategoryBreakdown breakdown={result.score.breakdown} />
            </div>

            {/* Issues List */}
            <div className="bg-white rounded-lg shadow-sm p-6">
              <IssuesList issues={result.score.issues} />
            </div>

            {/* Strengths */}
            {result.score.strengths.length > 0 && (
              <div className="bg-green-50 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-green-900 mb-4">
                  ✨ Strengths
                </h3>
                <ul className="space-y-2">
                  {result.score.strengths.map((strength, idx) => (
                    <li key={idx} className="text-sm text-green-900 flex items-start">
                      <span className="text-green-600 mr-2">✓</span>
                      <span>{strength}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
```

### Step 5: Test component (manual)

```bash
npm run dev
```

Test flow:
1. Upload a resume on homepage
2. Verify navigation to /results
3. Check score card displays correctly
4. Check category breakdown shows all 6 categories
5. Check issues are categorized and displayed
6. Check metadata displays
7. Click "Back to Upload" button

### Step 6: Commit

```bash
git add frontend/src/components/
git commit -m "feat: implement results page with score visualization

- Create ScoreCard component with color-coded scores
- Create CategoryBreakdown with progress bars
- Create IssuesList with severity badges
- Create ResultsPage layout
- Display metadata (pages, words, format)
- Display contact information
- Display strengths list
- Responsive design with grid layout"
```

---

## Task 20: Routing Setup

**Goal:** Configure React Router for navigation

**Files:**
- Modify: `frontend/src/App.tsx`
- Modify: `frontend/src/main.tsx`

### Step 1: Update main.tsx

**Modify `frontend/src/main.tsx`:**
```typescript
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import './index.css'
import App from './App.tsx'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </StrictMode>,
)
```

### Step 2: Update App.tsx with routes

**Modify `frontend/src/App.tsx`:**
```typescript
import { Routes, Route } from 'react-router-dom'
import UploadPage from './components/UploadPage'
import ResultsPage from './components/ResultsPage'
import './index.css'

function App() {
  return (
    <Routes>
      <Route path="/" element={<UploadPage />} />
      <Route path="/results" element={<ResultsPage />} />
    </Routes>
  )
}

export default App
```

### Step 3: Test routing

```bash
npm run dev
```

Test:
1. Go to http://localhost:5173/ - should show upload page
2. Go to http://localhost:5173/results - should redirect to upload (no data)
3. Upload a resume - should navigate to /results
4. Click back button - should go to /

### Step 4: Commit

```bash
git add frontend/src/App.tsx frontend/src/main.tsx
git commit -m "feat: setup React Router for page navigation

- Configure BrowserRouter in main.tsx
- Add routes for / (upload) and /results
- Remove hardcoded content from App.tsx
- Enable navigation between pages"
```

---

## Task 21: Error Handling & Loading States

**Goal:** Add comprehensive error handling and loading UX

**Files:**
- Create: `frontend/src/components/ErrorBoundary.tsx`
- Create: `frontend/src/components/LoadingSpinner.tsx`
- Modify: `frontend/src/App.tsx`

### Step 1: Create LoadingSpinner component

**Create `frontend/src/components/LoadingSpinner.tsx`:**
```typescript
/**
 * Reusable loading spinner component
 */
interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg'
  text?: string
}

export default function LoadingSpinner({ size = 'md', text }: LoadingSpinnerProps) {
  const sizeClasses = {
    sm: 'h-4 w-4',
    md: 'h-8 w-8',
    lg: 'h-12 w-12'
  }

  return (
    <div className="flex flex-col items-center justify-center">
      <svg
        className={`animate-spin ${sizeClasses[size]} text-blue-600`}
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
        viewBox="0 0 24 24"
      >
        <circle
          className="opacity-25"
          cx="12"
          cy="12"
          r="10"
          stroke="currentColor"
          strokeWidth="4"
        />
        <path
          className="opacity-75"
          fill="currentColor"
          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
        />
      </svg>
      {text && (
        <p className="mt-2 text-sm text-gray-600">{text}</p>
      )}
    </div>
  )
}
```

### Step 2: Create ErrorBoundary component

**Create `frontend/src/components/ErrorBoundary.tsx`:**
```typescript
/**
 * Error boundary for catching React errors
 */
import { Component, ReactNode } from 'react'

interface Props {
  children: ReactNode
}

interface State {
  hasError: boolean
  error?: Error
}

export default class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: unknown) {
    console.error('Error caught by boundary:', error, errorInfo)
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
          <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-8 text-center">
            <div className="text-6xl mb-4">⚠️</div>
            <h1 className="text-2xl font-bold text-gray-900 mb-2">
              Oops! Something went wrong
            </h1>
            <p className="text-gray-600 mb-6">
              We're sorry, but something unexpected happened. Please try refreshing the page.
            </p>
            <button
              onClick={() => window.location.reload()}
              className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
            >
              Refresh Page
            </button>
            {this.state.error && (
              <details className="mt-4 text-left">
                <summary className="text-sm text-gray-500 cursor-pointer">
                  Error details
                </summary>
                <pre className="mt-2 text-xs text-red-600 overflow-auto">
                  {this.state.error.message}
                </pre>
              </details>
            )}
          </div>
        </div>
      )
    }

    return this.props.children
  }
}
```

### Step 3: Wrap App with ErrorBoundary

**Modify `frontend/src/App.tsx`:**
```typescript
import { Routes, Route } from 'react-router-dom'
import ErrorBoundary from './components/ErrorBoundary'
import UploadPage from './components/UploadPage'
import ResultsPage from './components/ResultsPage'
import './index.css'

function App() {
  return (
    <ErrorBoundary>
      <Routes>
        <Route path="/" element={<UploadPage />} />
        <Route path="/results" element={<ResultsPage />} />
      </Routes>
    </ErrorBoundary>
  )
}

export default App
```

### Step 4: Test error handling

Test scenarios:
1. Backend offline - try uploading (should show error message)
2. Invalid file type - select .txt file (should show validation error)
3. Large file - select 15MB file (should show size error)
4. Navigate to /results without data (should redirect)

### Step 5: Commit

```bash
git add frontend/src/components/ErrorBoundary.tsx frontend/src/components/LoadingSpinner.tsx frontend/src/App.tsx
git commit -m "feat: add error handling and loading states

- Create LoadingSpinner component with sizes
- Create ErrorBoundary for React errors
- Wrap App with ErrorBoundary
- Improve error messaging throughout
- Handle backend offline scenario"
```

---

## Verification

### Run frontend dev server

```bash
cd /Users/sabuj.mondal/ats-resume-scorer/frontend
npm run dev
```

### Run backend API

```bash
cd /Users/sabuj.mondal/ats-resume-scorer/backend
python -m uvicorn backend.main:app --reload
```

### Test full flow

1. **Upload Page** - http://localhost:5173/
   - File drop zone works (click and drag)
   - File validation (PDF/DOCX only, max 10MB)
   - Job description textarea
   - Industry dropdown
   - Submit button enables when file selected
   - Loading spinner shows during upload

2. **Results Page** - http://localhost:5173/results
   - Score card displays (0-100)
   - Color coding (green/yellow/red)
   - Category breakdown (6 categories with progress bars)
   - Issues list (critical, warnings, suggestions, info)
   - Metadata display (pages, words, format)
   - Contact info display
   - Back button navigates to upload

3. **Error Handling**
   - Invalid file type shows error
   - File too large shows error
   - Backend offline shows error
   - No data redirects to upload

---

## Final Commit

```bash
git add .
git commit -m "chore: Phase 6 Frontend Upload & Display complete

Summary:
- Upload page with drag-and-drop file zone
- File validation (PDF/DOCX, max 10MB)
- Optional job description and industry fields
- Results page with score visualization
- 6-category breakdown with progress bars
- Issues list with severity badges
- Metadata and contact info display
- React Router navigation
- Error boundary and loading states
- Responsive design with Tailwind CSS
- Full API integration via Axios

Phase 6 complete - ready for Phase 7 (Rich Text Editor)"
```

---

## Success Metrics

Phase 6 is complete when:
- ✅ Upload page renders with file drop zone
- ✅ File validation works (type and size)
- ✅ Resume uploads successfully to backend
- ✅ Results page displays score and breakdown
- ✅ All 6 categories show with progress bars
- ✅ Issues are categorized and displayed
- ✅ Navigation works between pages
- ✅ Error handling covers common scenarios
- ✅ Loading states provide feedback
- ✅ Responsive design works on mobile

**Next Phase:** Phase 7 - Frontend Rich Text Editor (TipTap integration for resume editing)
