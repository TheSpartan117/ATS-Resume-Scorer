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
import { useAuth } from '../hooks/useAuth'
import { rescoreResume, shouldShowAd, saveResume, updateResume, type ScoreRequest } from '../api/client'
import { ERROR_AUTO_DISMISS_MS } from '../config/timeouts'
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
 * Convert resume data to editable HTML with proper styling
 */
function convertResumeToHTML(result: UploadResponse): string {
  const parts: string[] = []

  // Contact Info Section
  parts.push('<h1 style="color: #1e3a8a; font-size: 2rem; font-weight: bold; margin-top: 1.5rem; margin-bottom: 1rem; border-bottom: 2px solid #bfdbfe; padding-bottom: 0.5rem;">Contact Information</h1>')
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
  parts.push('<h2 style="color: #3730a3; font-size: 1.5rem; font-weight: bold; margin-top: 1.25rem; margin-bottom: 0.75rem;">Professional Summary</h2>')
  parts.push('<p>Edit this section to add your professional summary...</p>')

  // Experience Section - Display parsed experience
  parts.push('<h2 style="color: #3730a3; font-size: 1.5rem; font-weight: bold; margin-top: 1.25rem; margin-bottom: 0.75rem;">Experience</h2>')
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
  parts.push('<h2 style="color: #3730a3; font-size: 1.5rem; font-weight: bold; margin-top: 1.25rem; margin-bottom: 0.75rem;">Education</h2>')
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
  parts.push('<h2 style="color: #3730a3; font-size: 1.5rem; font-weight: bold; margin-top: 1.25rem; margin-bottom: 0.75rem;">Skills</h2>')
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
      navigate('/', { replace: true })
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
  const [originalDocxFile, setOriginalDocxFile] = useState<File | null>(null)

  // Retrieve original DOCX file from localStorage
  useEffect(() => {
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
        if (import.meta.env.DEV) {
          console.log('Original DOCX file loaded:', filename)
        }
      } catch (err) {
        if (import.meta.env.DEV) {
          console.error('Failed to load original file:', err)
        }
      }
    }
  }, [])

  // Initialize editor with editable HTML from backend
  useEffect(() => {
    if (result && !editorContent) {
      // Use rich HTML from backend if available, otherwise fallback to converted text
      const html = result.editableHtml || convertResumeToHTML(result)
      setEditorContent(html)
      setCurrentScore(result.score)
      setWordCount(result.metadata.wordCount)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  // Manual re-score function
  const performRescore = useCallback(async () => {
    const content = editorContent;
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
      if (import.meta.env.DEV) {
        console.error('Ad check failed:', err)
      }
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

  // Note: Auto re-scoring on content changes is disabled for the simple ResumeEditor
  // Users can manually trigger re-scoring if needed

  // Handle ad viewed callback
  const handleAdViewed = useCallback(() => {
    setShowAd(false)
    // Ad tracking is already done in AdDisplay component
  }, [])

  // Handle save/update resume
  const handleSave = async () => {
    if (!result || !currentScore || !isAuthenticated) {
      setRescoreError('You must be logged in to save resumes')
      setTimeout(() => setRescoreError(null), ERROR_AUTO_DISMISS_MS)
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
        setTimeout(() => setRescoreError(null), ERROR_AUTO_DISMISS_MS)
      } else {
        // Save new
        const saved = await saveResume(scoreRequest)
        setCurrentSavedResumeId(saved.id)
        setRescoreError('Resume saved successfully!')
        setTimeout(() => setRescoreError(null), ERROR_AUTO_DISMISS_MS)
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
    <div className="h-screen w-screen flex flex-col overflow-hidden bg-white">
      {/* Ad Display Overlay */}
      {showAd && <AdDisplay onAdViewed={handleAdViewed} />}

      {/* Compact Header Bar */}
      <div className="flex-none">
        <div className="bg-white border-b border-gray-200 px-4 py-2 flex items-center justify-between shadow-sm">
          {/* Left: Back button and filename */}
          <div className="flex items-center space-x-4">
            <button
              onClick={() => navigate('/results', { state: { result } })}
              className="text-blue-600 hover:text-blue-800 font-semibold flex items-center transition-colors text-sm"
            >
              <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              Back
            </button>
            <div className="flex items-center text-sm text-gray-600">
              <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z" clipRule="evenodd" />
              </svg>
              {result.fileName}
            </div>
          </div>

          {/* Right: Actions */}
          <div className="flex items-center space-x-3">
              {(adCheckPending || isRescoring) && (
                <div className="flex items-center text-blue-600">
                  <LoadingSpinner size="sm" />
                  <span className="ml-2 text-xs">
                    {adCheckPending ? 'Checking...' : 'Re-scoring...'}
                  </span>
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
                  className="px-3 py-1.5 bg-green-600 text-white rounded hover:bg-green-700 transition-colors font-medium text-xs disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isSaving ? 'Saving...' : currentSavedResumeId ? 'Update' : 'Save'}
                </button>
              )}
              <UserMenu />
            </div>
          </div>

        {/* Toast Status Message (if needed) */}
        {rescoreError && (
          <div className={`absolute top-16 right-4 z-50 p-3 rounded-lg shadow-lg text-sm ${
            rescoreError.includes('successfully')
              ? 'bg-green-600 text-white'
              : 'bg-red-600 text-white'
          }`}>
            {rescoreError}
          </div>
        )}
      </div>

      {/* Main Split-View Editor - Full Screen */}
      <div className="flex-1 overflow-hidden">
        <ResumeEditor
          value={editorContent}
          onChange={handleEditorChange}
          currentScore={currentScore}
          isRescoring={isRescoring}
          wordCount={wordCount}
          onRescore={performRescore}
          originalDocxFile={originalDocxFile}
        />
      </div>
    </div>
  )
}
