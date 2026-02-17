/**
 * Editor page with real-time re-scoring
 */
import { useLocation, useNavigate } from 'react-router-dom'
import { useEffect, useState } from 'react'
import type { UploadResponse, ScoreResult } from '../types/resume'
import { rescoreResume, type ScoreRequest } from '../api/client'
import { useDebounce } from '../hooks/useDebounce'
import RichTextEditor from './RichTextEditor'
import ScoreCard from './ScoreCard'
import CategoryBreakdown from './CategoryBreakdown'
import IssuesList from './IssuesList'
import LoadingSpinner from './LoadingSpinner'

/**
 * Convert resume data to editable HTML
 */
function convertResumeToHTML(result: UploadResponse): string {
  const parts: string[] = []

  // Contact section
  if (result.contact.name || result.contact.email || result.contact.phone || result.contact.location) {
    parts.push('<h2>Contact Information</h2>')
    if (result.contact.name) parts.push(`<p><strong>Name:</strong> ${result.contact.name}</p>`)
    if (result.contact.email) parts.push(`<p><strong>Email:</strong> ${result.contact.email}</p>`)
    if (result.contact.phone) parts.push(`<p><strong>Phone:</strong> ${result.contact.phone}</p>`)
    if (result.contact.location) parts.push(`<p><strong>Location:</strong> ${result.contact.location}</p>`)
    if (result.contact.linkedin) parts.push(`<p><strong>LinkedIn:</strong> ${result.contact.linkedin}</p>`)
    if (result.contact.website) parts.push(`<p><strong>Website:</strong> ${result.contact.website}</p>`)
  }

  // Placeholder sections
  parts.push('<h2>Professional Summary</h2>')
  parts.push('<p>Add your professional summary here...</p>')

  parts.push('<h2>Experience</h2>')
  parts.push('<p>Add your work experience here...</p>')

  parts.push('<h2>Education</h2>')
  parts.push('<p>Add your education here...</p>')

  parts.push('<h2>Skills</h2>')
  parts.push('<p>Add your skills here...</p>')

  return parts.join('\n')
}

export default function EditorPage() {
  const location = useLocation()
  const navigate = useNavigate()
  const result = location.state?.result as UploadResponse | undefined

  const [editorContent, setEditorContent] = useState('')
  const [score, setScore] = useState<ScoreResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [wordCount, setWordCount] = useState(0)

  // Debounce editor content changes (500ms delay)
  const debouncedContent = useDebounce(editorContent, 500)

  // Initialize editor content from resume
  useEffect(() => {
    if (!result) {
      navigate('/')
      return
    }

    // Set initial content
    const html = convertResumeToHTML(result)
    setEditorContent(html)
    setScore(result.score)
    setWordCount(result.metadata.wordCount)
  }, [result, navigate])

  // Re-score when debounced content changes
  useEffect(() => {
    if (!result || !debouncedContent || debouncedContent === convertResumeToHTML(result)) {
      return
    }

    const rescore = async () => {
      setLoading(true)
      setError(null)

      try {
        // Count words in HTML content (strip tags for accurate count)
        const text = debouncedContent.replace(/<[^>]*>/g, ' ').trim()
        const words = text.split(/\s+/).filter(w => w.length > 0).length
        setWordCount(words)

        // Build score request
        const request: ScoreRequest = {
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

        // Re-score
        const newScore = await rescoreResume(request)
        setScore(newScore)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to re-score resume')
      } finally {
        setLoading(false)
      }
    }

    rescore()
  }, [debouncedContent, result])

  if (!result) {
    return null
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <button
              onClick={() => navigate('/results', { state: { result } })}
              className="text-blue-600 hover:text-blue-800 font-medium mb-4 flex items-center"
            >
              ← Back to Results
            </button>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              Edit Resume
            </h1>
            <p className="text-gray-600">
              {result.fileName} • {wordCount} words
            </p>
          </div>
        </div>

        {/* Split Layout: Editor (2 cols) + Score (1 col) */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Editor (2 columns) */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow-sm p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold text-gray-900">Resume Content</h2>
                {loading && (
                  <div className="flex items-center text-sm text-gray-600">
                    <LoadingSpinner size="sm" />
                    <span className="ml-2">Re-scoring...</span>
                  </div>
                )}
              </div>
              <RichTextEditor
                content={editorContent}
                onChange={setEditorContent}
                placeholder="Start editing your resume..."
              />
            </div>
          </div>

          {/* Score Panel (1 column) */}
          <div className="lg:col-span-1">
            <div className="sticky top-8 space-y-6">
              {/* Score Card */}
              <div className="bg-white rounded-lg shadow-sm p-6">
                {score ? (
                  <ScoreCard score={score.overallScore} />
                ) : (
                  <div className="text-center py-8">
                    <LoadingSpinner />
                    <p className="text-sm text-gray-600 mt-2">Loading score...</p>
                  </div>
                )}
              </div>

              {/* Error Display */}
              {error && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                  <p className="text-sm text-red-800">{error}</p>
                </div>
              )}

              {/* Category Breakdown */}
              {score && (
                <div className="bg-white rounded-lg shadow-sm p-6">
                  <CategoryBreakdown breakdown={score.breakdown} />
                </div>
              )}

              {/* Issues List */}
              {score && (
                <div className="bg-white rounded-lg shadow-sm p-6">
                  <IssuesList issues={score.issues} />
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
