/**
 * Editor page component with real-time re-scoring and MS Word-style editing
 */
import { useState, useEffect, useCallback, useRef } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { WYSIWYGEditor } from './WYSIWYGEditor'
import IssuesList from './IssuesList'
import LoadingSpinner from './LoadingSpinner'
import UserMenu from './UserMenu'
import AdDisplay from './AdDisplay'
import { ModeIndicator } from './ModeIndicator'
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
        const textContent = debouncedContent.replace(/<[^>]*>/g, ' ')
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
    <div className="min-h-screen bg-gray-50">
      {/* Ad Display Overlay */}
      {showAd && <AdDisplay onAdViewed={handleAdViewed} />}

      <div className="container mx-auto px-4 py-4 max-w-7xl">
        {/* Header */}
        <div className="mb-4">
          <div className="flex items-center justify-between mb-2">
            <button
              onClick={() => navigate('/results', { state: { result } })}
              className="text-blue-600 hover:text-blue-800 font-medium flex items-center"
            >
              ← Back to Results
            </button>
            <div className="flex items-center space-x-4">
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
              <h1 className="text-2xl font-bold text-gray-900 mb-1">
                Edit Your Resume
              </h1>
              <p className="text-sm text-gray-600">
                {result.fileName}
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

        {/* Status Message */}
        {rescoreError && (
          <div className={`mb-3 p-3 rounded-md ${
            rescoreError.includes('successfully')
              ? 'bg-green-50 border border-green-200'
              : 'bg-red-50 border border-red-200'
          }`}>
            <p className={`text-sm ${
              rescoreError.includes('successfully')
                ? 'text-green-800'
                : 'text-red-800'
            }`}>{rescoreError}</p>
            <button
              onClick={() => setRescoreError(null)}
              className={`mt-2 text-sm underline ${
                rescoreError.includes('successfully')
                  ? 'text-green-600 hover:text-green-800'
                  : 'text-red-600 hover:text-red-800'
              }`}
            >
              Dismiss
            </button>
          </div>
        )}

        {/* Main Content - Full Width MS Word-Style Editor */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          {/* Left Column: Editor (2/3 width) */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow-sm p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold text-gray-900">
                  📝 Resume Content
                </h2>
                <span className="text-sm text-gray-600">
                  {wordCount} words
                </span>
              </div>
              <WYSIWYGEditor
                value={editorContent}
                onChange={handleEditorChange}
              />
            </div>
          </div>

          {/* Right Column: Live Score (1/3 width) */}
          <div className="lg:col-span-1">
            <div className="sticky top-4 space-y-4">
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

        {/* Full Issues List */}
        <div className="mt-4 bg-white rounded-lg shadow-sm p-4">
          <IssuesList issues={currentScore.issues} />
        </div>
      </div>
    </div>
  )
}
