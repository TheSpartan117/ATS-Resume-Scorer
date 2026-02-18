/**
 * Results page component
 */
import { useLocation, useNavigate } from 'react-router-dom'
import { useEffect } from 'react'
import type { UploadResponse } from '../types/resume'
import { ModeIndicator } from './ModeIndicator'
import { DownloadMenu } from './DownloadMenu'
import IssuesList from './IssuesList'
import UserMenu from './UserMenu'

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

  // Build resume content text from parsed data
  const buildResumeContent = (): string => {
    if (!result) return ''

    const parts: string[] = []

    // Contact Information
    if (result.contact) {
      parts.push('Contact Information')
      if (result.contact.name) parts.push(`Name: ${result.contact.name}`)
      if (result.contact.email) parts.push(`Email: ${result.contact.email}`)
      if (result.contact.phone) parts.push(`Phone: ${result.contact.phone}`)
      if (result.contact.location) parts.push(`Location: ${result.contact.location}`)
      if (result.contact.linkedin) parts.push(`LinkedIn: ${result.contact.linkedin}`)
      parts.push('')
    }

    // Experience
    if (result.experience && result.experience.length > 0) {
      parts.push('Experience')
      parts.push('')
      result.experience.forEach((exp: any) => {
        if (exp.title) parts.push(exp.title)
        if (exp.company) parts.push(exp.company)
        if (exp.startDate || exp.endDate) {
          parts.push(`${exp.startDate || ''} - ${exp.endDate || 'Present'}`)
        }
        if (exp.location) parts.push(exp.location)
        if (exp.description) {
          parts.push('')
          parts.push(exp.description)
        }
        parts.push('')
      })
    }

    // Education
    if (result.education && result.education.length > 0) {
      parts.push('Education')
      parts.push('')
      result.education.forEach((edu: any) => {
        if (edu.degree) parts.push(edu.degree)
        if (edu.institution) parts.push(edu.institution)
        if (edu.graduationDate) parts.push(`Graduated: ${edu.graduationDate}`)
        if (edu.location) parts.push(edu.location)
        if (edu.gpa) parts.push(`GPA: ${edu.gpa}`)
        parts.push('')
      })
    }

    // Skills
    if (result.skills && result.skills.length > 0) {
      parts.push('Skills')
      parts.push('')
      parts.push(result.skills.join(', '))
      parts.push('')
    }

    // Certifications
    if (result.certifications && result.certifications.length > 0) {
      parts.push('Certifications')
      parts.push('')
      result.certifications.forEach((cert: any) => {
        if (cert.name) parts.push(cert.name)
        if (cert.issuer) parts.push(`Issued by: ${cert.issuer}`)
        if (cert.date) parts.push(`Date: ${cert.date}`)
        parts.push('')
      })
    }

    return parts.join('\n')
  }

  if (!result) {
    return null
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8 max-w-6xl">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <button
              onClick={() => navigate('/')}
              className="text-blue-600 hover:text-blue-800 font-medium flex items-center"
            >
              ← Back to Upload
            </button>
            <UserMenu />
          </div>
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">
                Resume Analysis Results
              </h1>
              <p className="text-gray-600">
                {result.fileName}
              </p>
            </div>
            <div className="flex items-center gap-3">
              <DownloadMenu
                resumeContent={buildResumeContent()}
                resumeName={result.contact?.name || 'Resume'}
                resumeData={result}
                scoreData={result.score}
                mode={result.scoringMode || 'quality_coach'}
                role={result.role || 'software_engineer'}
                level={result.level || 'mid'}
              />
              <button
                onClick={() => navigate('/editor', { state: { result } })}
                className="px-6 py-3 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors font-semibold"
              >
                Edit Resume
              </button>
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column: Mode Indicator */}
          <div className="lg:col-span-1">
            <ModeIndicator
              mode={result.scoringMode || result.score.mode || 'quality_coach'}
              score={result.score.overallScore}
              keywordDetails={result.score.keywordDetails}
              breakdown={Object.fromEntries(
                Object.entries(result.score.breakdown).map(([key, value]: [string, any]) => [
                  key,
                  typeof value === 'object' && 'score' in value ? value.score : value
                ])
              )}
              autoReject={result.score.autoReject}
            />

            {/* Metadata */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mt-6">
              <div className="space-y-3">
                <h3 className="font-semibold text-gray-900 mb-3">📄 Resume Info</h3>
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
                  <h3 className="font-semibold text-gray-900 mb-3">👤 Contact</h3>
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

            {/* Parsed Experience Section */}
            {result.experience && result.experience.length > 0 && (
              <div className="bg-white rounded-lg shadow-sm p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  💼 Extracted Experience
                </h3>
                <div className="space-y-4">
                  {result.experience.map((exp: any, idx: number) => (
                    <div key={idx} className="border-l-4 border-blue-500 pl-4">
                      {exp.title && (
                        <h4 className="font-semibold text-gray-900">{exp.title}</h4>
                      )}
                      {(exp.company || exp.location) && (
                        <p className="text-sm text-gray-600">
                          {[exp.company, exp.location].filter(Boolean).join(', ')}
                        </p>
                      )}
                      {(exp.startDate || exp.endDate) && (
                        <p className="text-xs text-gray-500 mb-2">
                          {[exp.startDate, exp.endDate].filter(Boolean).join(' - ')}
                        </p>
                      )}
                      {exp.description && (
                        <div className="text-sm text-gray-700 whitespace-pre-line">
                          {exp.description}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Parsed Education Section */}
            {result.education && result.education.length > 0 && (
              <div className="bg-white rounded-lg shadow-sm p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  🎓 Extracted Education
                </h3>
                <div className="space-y-4">
                  {result.education.map((edu: any, idx: number) => (
                    <div key={idx} className="border-l-4 border-purple-500 pl-4">
                      {edu.degree && (
                        <h4 className="font-semibold text-gray-900">{edu.degree}</h4>
                      )}
                      {(edu.institution || edu.location) && (
                        <p className="text-sm text-gray-600">
                          {[edu.institution, edu.location].filter(Boolean).join(', ')}
                        </p>
                      )}
                      {edu.graduationDate && (
                        <p className="text-xs text-gray-500">
                          Graduated: {edu.graduationDate}
                        </p>
                      )}
                      {edu.gpa && (
                        <p className="text-xs text-gray-500">GPA: {edu.gpa}</p>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Parsed Skills Section */}
            {result.skills && result.skills.length > 0 && (
              <div className="bg-white rounded-lg shadow-sm p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  ⚡ Extracted Skills
                </h3>
                <div className="flex flex-wrap gap-2">
                  {result.skills.map((skill: string, idx: number) => (
                    <span
                      key={idx}
                      className="px-3 py-1 bg-blue-50 text-blue-700 rounded-full text-sm font-medium border border-blue-200"
                    >
                      {skill}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
