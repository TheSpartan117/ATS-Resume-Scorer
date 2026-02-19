/**
 * Editor page component with split-view editing and real-time scoring
 */
import { useState, useEffect, useCallback, useRef } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { ResumeEditor } from './ResumeEditor'
import LoadingSpinner from './LoadingSpinner'
import UserMenu from './UserMenu'
import AdDisplay from './AdDisplay'
import { DownloadMenu } from './DownloadMenu'
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

  // Professional Summary Section
  parts.push('<h2>Professional Summary</h2>')
  parts.push('<p>Edit this section to add your professional summary...</p>')

  // Experience Section - Display parsed experience
  parts.push('<h2>Experience</h2>')
  if (result.experience && result.experience.length > 0) {
    result.experience.forEach((exp: any) => {
      if (exp.title) {
        parts.push(`<p><strong>${escapeHtml(exp.title)}</strong></p>`)
      }
      if (exp.company || exp.location) {
        const companyLocation = [exp.company, exp.location].filter(Boolean).join(', ')
        parts.push(`<p><em>${escapeHtml(companyLocation)}</em></p>`)
      }
      if (exp.startDate || exp.endDate) {
        const dates = [exp.startDate, exp.endDate].filter(Boolean).join(' - ')
        parts.push(`<p>${escapeHtml(dates)}</p>`)
      }
      if (exp.description) {
        // Convert newlines to paragraphs
        const descLines = exp.description.split('\n').filter((line: string) => line.trim())
        descLines.forEach((line: string) => {
          parts.push(`<p>${escapeHtml(line)}</p>`)
        })
      }
      parts.push('<br>')
    })
  } else {
    parts.push('<p>Edit this section to add your work experience...</p>')
  }

  // Education Section - Display parsed education
  parts.push('<h2>Education</h2>')
  if (result.education && result.education.length > 0) {
    result.education.forEach((edu: any) => {
      if (edu.degree) {
        parts.push(`<p><strong>${escapeHtml(edu.degree)}</strong></p>`)
      }
      if (edu.institution || edu.location) {
        const institutionLocation = [edu.institution, edu.location].filter(Boolean).join(', ')
        parts.push(`<p><em>${escapeHtml(institutionLocation)}</em></p>`)
      }
      if (edu.graduationDate) {
        parts.push(`<p>Graduated: ${escapeHtml(edu.graduationDate)}</p>`)
      }
      if (edu.gpa) {
        parts.push(`<p>GPA: ${escapeHtml(edu.gpa)}</p>`)
      }
      parts.push('<br>')
    })
  } else {
    parts.push('<p>Edit this section to add your education...</p>')
  }

  // Skills Section - Display parsed skills
  parts.push('<h2>Skills</h2>')
  if (result.skills && result.skills.length > 0) {
    parts.push(`<p>${result.skills.map(skill => escapeHtml(skill)).join(', ')}</p>`)
  } else {
    parts.push('<p>Edit this section to add your skills...</p>')
  }

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
  }, [result, navigate])

  // Track component mount status
  useEffect(() => {
    isMountedRef.current = true
    return () => {
      isMountedRef.current = false
    }
  }, [])

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

  // Initialize editor with editable HTML from backend
  useEffect(() => {
    if (result) {
      // Use rich HTML from backend if available, otherwise fallback to converted text
      const html = result.editableHtml || convertResumeToHTML(result)
      setEditorContent(html)
      setCurrentScore(result.score)
      setWordCount(result.metadata.wordCount)
    }
  }, [result])

  // Debounce editor content changes (500ms delay)
  const debouncedContent = useDebounce(editorContent, 500)

  // Manual re-score function
  const performRescore = useCallback(async (content: string = editorContent) => {
    if (!result || !isMountedRef.current) return

    // Check if ad should be shown before re-scoring
    setAdCheckPending(true)
    try {
      const adResult = await shouldShowAd()
      if (adResult.showAd) {
        setShowAd(true)
        setAdCheckPending(false)
        return // Exit early to prevent re-scoring
      }
    } catch (err) {
      console.error('Ad check failed:', err)
    } finally {
      setAdCheckPending(false)
    }

    setIsRescoring(true)
    setRescoreError(null)

    try {
      // Count words in HTML content by stripping tags
      const textContent = content.replace(/<[^>]*>/g, ' ')
      const words = textContent.trim().split(/\s+/).filter(Boolean).length
      setWordCount(words)

      // Include actual parsed data for accurate re-scoring
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

      const newScore = await rescoreResume(scoreRequest)

      if (isMountedRef.current) {
        setCurrentScore(newScore)
        setRescoreError('✓ Resume re-scored successfully')
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
  }, [result, editorContent])

  // Re-score when debounced content changes
  useEffect(() => {
    if (!result || !debouncedContent) return

    // Skip the initial mount
    if (isInitialMount.current) {
      isInitialMount.current = false
      return
    }

    performRescore(debouncedContent)
  }, [debouncedContent, result, performRescore])

  // Handle ad viewed callback
  const handleAdViewed = useCallback(() => {
    setShowAd(false)
    // Ad tracking is already done in AdDisplay component
  }, [])

  // Handle save/update resume
  const handleSave = async () => {
    if (!result || !currentScore || !isAuthenticated) {
      setRescoreError('You must be logged in to save resumes')
      setTimeout(() => setRescoreError(null), 3000)
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
        setRescoreError('Resume updated successfully!')
        setTimeout(() => setRescoreError(null), 3000)
      } else {
        // Save new
        const saved = await saveResume(scoreRequest)
        setCurrentSavedResumeId(saved.id)
        setRescoreError('Resume saved successfully!')
        setTimeout(() => setRescoreError(null), 3000)
      }
    } catch (err) {
      setRescoreError(err instanceof Error ? err.message : 'Failed to save resume')
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
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      {/* Ad Display Overlay */}
      {showAd && <AdDisplay onAdViewed={handleAdViewed} />}

      <div className="container mx-auto px-4 py-6">
        {/* Header */}
        <div className="mb-6 bg-white rounded-xl shadow-sm border border-gray-200 p-4">
          <div className="flex items-center justify-between mb-3">
            <button
              onClick={() => navigate('/results', { state: { result } })}
              className="text-blue-600 hover:text-blue-800 font-semibold flex items-center transition-colors"
            >
              <svg className="w-5 h-5 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              Back to Results
            </button>
            <div className="flex items-center space-x-3">
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
              <DownloadMenu
                resumeContent={editorContent}
                resumeName={result.contact?.name || 'Resume'}
                resumeData={{
                  fileName: result.fileName,
                  contact: result.contact,
                  experience: result.experience || [],
                  education: result.education || [],
                  skills: result.skills || [],
                  certifications: result.certifications || [],
                  metadata: result.metadata,
                  jobDescription: result.jobDescription,
                  industry: result.industry
                }}
                scoreData={{
                  overallScore: currentScore.overallScore,
                  breakdown: currentScore.breakdown,
                  issues: currentScore.issues,
                  strengths: currentScore.strengths,
                  mode: currentScore.mode || result.scoringMode || 'quality_coach'
                }}
                mode={currentScore.mode || result.scoringMode || 'quality_coach'}
                role={result.role || 'Software Engineer'}
                level={result.level || 'Mid-Level'}
              />
              {isAuthenticated && (
                <button
                  onClick={handleSave}
                  disabled={isSaving}
                  className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors font-semibold text-sm disabled:opacity-50 disabled:cursor-not-allowed shadow-sm"
                >
                  {isSaving ? 'Saving...' : currentSavedResumeId ? 'Update Resume' : 'Save Resume'}
                </button>
              )}
              <UserMenu />
            </div>
          </div>
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-1">
                Resume Editor
              </h1>
              <p className="text-sm text-gray-600 flex items-center">
                <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z" clipRule="evenodd" />
                </svg>
                {result.fileName}
              </p>
            </div>
          </div>
        </div>

        {/* Status Message */}
        {rescoreError && (
          <div className={`mb-4 p-4 rounded-xl shadow-sm ${
            rescoreError.includes('successfully')
              ? 'bg-green-50 border-2 border-green-200'
              : 'bg-red-50 border-2 border-red-200'
          }`}>
            <div className="flex items-start justify-between">
              <div className="flex items-start">
                <div className={`flex-shrink-0 ${
                  rescoreError.includes('successfully') ? 'text-green-500' : 'text-red-500'
                }`}>
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                    {rescoreError.includes('successfully') ? (
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                    ) : (
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                    )}
                  </svg>
                </div>
                <p className={`ml-3 text-sm font-medium ${
                  rescoreError.includes('successfully')
                    ? 'text-green-800'
                    : 'text-red-800'
                }`}>{rescoreError}</p>
              </div>
              <button
                onClick={() => setRescoreError(null)}
                className={`flex-shrink-0 ml-4 inline-flex ${
                  rescoreError.includes('successfully')
                    ? 'text-green-500 hover:text-green-700'
                    : 'text-red-500 hover:text-red-700'
                }`}
              >
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                </svg>
              </button>
            </div>
          </div>
        )}

        {/* Main Split-View Editor */}
        <ResumeEditor
          value={editorContent}
          onChange={handleEditorChange}
          currentScore={currentScore}
          isRescoring={isRescoring}
          wordCount={wordCount}
          onRescore={performRescore}
        />
      </div>
    </div>
  )
}
