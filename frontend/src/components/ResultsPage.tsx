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
