/**
 * Editor page component with real-time re-scoring
 */
import { useState, useEffect, useCallback, useRef } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import RichTextEditor from './RichTextEditor'
import ScoreCard from './ScoreCard'
import CategoryBreakdown from './CategoryBreakdown'
import IssuesList from './IssuesList'
import LoadingSpinner from './LoadingSpinner'
import UserMenu from './UserMenu'
import AdDisplay from './AdDisplay'
import { useDebounce } from '../hooks/useDebounce'
import { useAuth } from '../hooks/useAuth'
import { rescoreResume, shouldShowAd, saveResume, updateResume, type ScoreRequest } from '../api/client'
import type { UploadResponse, ScoreResult } from '../types/resume'

// Helper function to escape HTML entities to prevent XSS
function escapeHtml(unsafe: string): string {
  return unsafe
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;")
}

/**
 * Convert resume data to editable HTML
 */
function convertResumeToHTML(result: UploadResponse): string {
  const parts: string[] = []

  // Contact Info Section
  parts.push('<h1>Contact Information</h1>')
  if (result.contact.name) {
    parts.push(`<p><strong>Name:</strong> ${escapeHtml(result.contact.name)}</p>`)
  }
  if (result.contact.email) {
    parts.push(`<p><strong>Email:</strong> ${escapeHtml(result.contact.email)}</p>`)
  }
  if (result.contact.phone) {
    parts.push(`<p><strong>Phone:</strong> ${escapeHtml(result.contact.phone)}</p>`)
  }
  if (result.contact.location) {
    parts.push(`<p><strong>Location:</strong> ${escapeHtml(result.contact.location)}</p>`)
  }
  if (result.contact.linkedin) {
    parts.push(`<p><strong>LinkedIn:</strong> ${escapeHtml(result.contact.linkedin)}</p>`)
  }
  if (result.contact.website) {
    parts.push(`<p><strong>Website:</strong> ${escapeHtml(result.contact.website)}</p>`)
  }

  // Add sections even if empty (user can fill in)
  parts.push('<h2>Professional Summary</h2>')
  parts.push('<p>Edit this section to add your professional summary...</p>')

  parts.push('<h2>Experience</h2>')
  parts.push('<p>Edit this section to add your work experience...</p>')

  parts.push('<h2>Education</h2>')
  parts.push('<p>Edit this section to add your education...</p>')

  parts.push('<h2>Skills</h2>')
  parts.push('<p>Edit this section to add your skills...</p>')

  return parts.join('\n')
}

export default function EditorPage() {
  const location = useLocation()
  const navigate = useNavigate()
  const result = location.state?.result as UploadResponse | undefined
  const savedResumeId = location.state?.savedResumeId as string | undefined
  const isMountedRef = useRef(true)
  const { isAuthenticated } = useAuth()

  // Redirect if no result data
  useEffect(() => {
    if (!result) {
      navigate('/')
    }

    return () => {
      isMountedRef.current = false
    }
  }, [result, navigate])

  // State
  const [editorContent, setEditorContent] = useState('')
  const [currentScore, setCurrentScore] = useState<ScoreResult | null>(null)
  const [isRescoring, setIsRescoring] = useState(false)
  const [rescoreError, setRescoreError] = useState<string | null>(null)
  const [wordCount, setWordCount] = useState(0)
  const [showAd, setShowAd] = useState(false)
  const [adCheckPending, setAdCheckPending] = useState(false)
  const [currentSavedResumeId, setCurrentSavedResumeId] = useState<string | undefined>(savedResumeId)
  const [isSaving, setIsSaving] = useState(false)
  const isInitialMount = useRef(true)

  // Initialize editor with parsed resume text
  useEffect(() => {
    if (result) {
      const html = convertResumeToHTML(result)
      setEditorContent(html)
      setCurrentScore(result.score)
      setWordCount(result.metadata.wordCount)
    }
  }, [result])

  // Debounce editor content changes (500ms delay)
  const debouncedContent = useDebounce(editorContent, 500)

  // Re-score when debounced content changes
  useEffect(() => {
    if (!result || !debouncedContent) return

    // Skip the initial mount
    if (isInitialMount.current) {
      isInitialMount.current = false
      return
    }

    const performRescore = async () => {
      if (!isMountedRef.current) return

      // Check if ad should be shown before re-scoring
      setAdCheckPending(true)
      try {
        const adResult = await shouldShowAd()
        if (adResult.showAd) {
          setShowAd(true)
          setAdCheckPending(false)
          return
        }
      } catch (err) {
        console.error('Ad check failed:', err)
      }
      setAdCheckPending(false)

      setIsRescoring(true)
      setRescoreError(null)

      try {
        // Count words in HTML content by stripping tags
        const textContent = debouncedContent.replace(/<[^>]*>/g, ' ')
        const words = textContent.trim().split(/\s+/).filter(Boolean).length
        setWordCount(words)

        // NOTE: This is an MVP limitation - we're only updating word count
        // Full structured parsing of HTML back to resume sections is a future enhancement
        const scoreRequest: ScoreRequest = {
          fileName: result.fileName,
          contact: result.contact,
          experience: [],
          education: [],
          skills: [],
          certifications: [],
          metadata: {
            ...result.metadata,
            wordCount: words
          }
        }

        const newScore = await rescoreResume(scoreRequest)

        if (isMountedRef.current) {
          setCurrentScore(newScore)
        }
      } catch (err) {
        if (isMountedRef.current) {
          setRescoreError(err instanceof Error ? err.message : 'Failed to re-score')
        }
      } finally {
        if (isMountedRef.current) {
          setIsRescoring(false)
        }
      }
    }

    performRescore()
  }, [debouncedContent, result])

  // Handle ad viewed callback
  const handleAdViewed = useCallback(() => {
    setShowAd(false)
    // Ad tracking is already done in AdDisplay component
  }, [])

  // Handle save/update resume
  const handleSave = async () => {
    if (!result || !currentScore || !isAuthenticated) {
      alert('You must be logged in to save resumes')
      return
    }

    setIsSaving(true)
    try {
      // Count words
      const textContent = editorContent.replace(/<[^>]*>/g, ' ')
      const words = textContent.trim().split(/\s+/).filter(Boolean).length

      const scoreRequest: ScoreRequest = {
        fileName: result.fileName,
        contact: result.contact,
        experience: result.experience || [],
        education: result.education || [],
        skills: result.skills || [],
        certifications: result.certifications || [],
        metadata: {
          ...result.metadata,
          wordCount: words
        },
        jobDescription: result.jobDescription,
        industry: result.industry
      }

      if (currentSavedResumeId) {
        // Update existing
        await updateResume(currentSavedResumeId, scoreRequest)
        alert('Resume updated successfully!')
      } else {
        // Save new
        const saved = await saveResume(scoreRequest)
        setCurrentSavedResumeId(saved.id)
        alert('Resume saved successfully!')
      }
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to save resume')
    } finally {
      setIsSaving(false)
    }
  }

  // Handle editor changes
  const handleEditorChange = useCallback((content: string) => {
    setEditorContent(content)
  }, [])

  if (!result || !currentScore) {
    return null
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Ad Display Overlay */}
      {showAd && <AdDisplay onAdViewed={handleAdViewed} />}

      <div className="container mx-auto px-4 py-8 max-w-7xl">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <button
              onClick={() => navigate('/results', { state: { result } })}
              className="text-blue-600 hover:text-blue-800 font-medium flex items-center"
            >
              ← Back to Results
            </button>
            <div className="flex items-center space-x-4">
              {isAuthenticated && (
                <button
                  onClick={handleSave}
                  disabled={isSaving}
                  className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors font-semibold text-sm disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isSaving ? 'Saving...' : currentSavedResumeId ? 'Update Resume' : 'Save Resume'}
                </button>
              )}
              <UserMenu />
            </div>
          </div>
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">
                Edit Your Resume
              </h1>
              <p className="text-gray-600">
                {result.fileName}
              </p>
              <p className="text-sm text-gray-500 mt-1">
                MVP Note: Text edits update word count. Full section parsing coming soon.
              </p>
            </div>
            <div className="text-right">
              {adCheckPending && (
                <div className="flex items-center text-blue-600">
                  <LoadingSpinner size="sm" />
                  <span className="ml-2 text-sm">Checking...</span>
                </div>
              )}
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
            <button
              onClick={() => setRescoreError(null)}
              className="mt-2 text-sm text-red-600 hover:text-red-800 underline"
            >
              Dismiss
            </button>
          </div>
        )}

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column: Editor */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow-sm p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold text-gray-900">
                  Resume Content
                </h2>
                <span className="text-sm text-gray-600">
                  {wordCount} words
                </span>
              </div>
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
                {isRescoring && (
                  <div className="mt-4 flex justify-center">
                    <LoadingSpinner size="sm" />
                  </div>
                )}
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
