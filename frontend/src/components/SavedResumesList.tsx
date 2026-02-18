/**
 * Saved resumes list component
 */
import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { getSavedResumes, deleteResume, type SavedResume } from '../api/client'
import LoadingSpinner from './LoadingSpinner'

export default function SavedResumesList() {
  const navigate = useNavigate()
  const [resumes, setResumes] = useState<SavedResume[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [deleteConfirm, setDeleteConfirm] = useState<string | null>(null)

  useEffect(() => {
    loadResumes()
  }, [])

  async function loadResumes() {
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

  async function handleDelete(id: string) {
    try {
      await deleteResume(id)
      setResumes(resumes.filter(r => r.id !== id))
      setDeleteConfirm(null)
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to delete resume')
    }
  }

  function handleEdit(resume: SavedResume) {
    // Navigate to editor with saved resume data
    navigate('/editor', {
      state: {
        result: {
          fileName: resume.fileName,
          contact: resume.content.contact,
          experience: resume.content.experience,
          education: resume.content.education,
          skills: resume.content.skills,
          certifications: resume.content.certifications,
          metadata: resume.content.metadata,
          score: resume.score,
          jobDescription: resume.content.jobDescription,
          industry: resume.content.industry
        },
        savedResumeId: resume.id
      }
    })
  }

  function formatDate(dateStr: string): string {
    const date = new Date(dateStr)
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  function getScoreColor(score: number): string {
    if (score >= 80) return 'text-green-600'
    if (score >= 60) return 'text-yellow-600'
    return 'text-red-600'
  }

  if (isLoading) {
    return (
      <div className="flex justify-center py-12">
        <LoadingSpinner />
      </div>
    )
  }

  if (error) {
    return (
      <div className="p-4 bg-red-50 border border-red-200 rounded-md">
        <p className="text-red-800">{error}</p>
        <button
          onClick={loadResumes}
          className="mt-2 text-sm text-red-600 hover:text-red-800 underline"
        >
          Try Again
        </button>
      </div>
    )
  }

  if (resumes.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-600 mb-4">You haven't saved any resumes yet.</p>
        <button
          onClick={() => navigate('/')}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
        >
          Upload a Resume
        </button>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {resumes.map((resume) => (
        <div
          key={resume.id}
          className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow"
        >
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                {resume.fileName}
              </h3>
              <div className="flex items-center space-x-4 text-sm text-gray-600">
                <div className="flex items-center">
                  <span className="font-medium mr-1">Score:</span>
                  <span className={`font-bold ${getScoreColor(resume.score.overallScore)}`}>
                    {resume.score.overallScore}/100
                  </span>
                </div>
                <div>
                  <span className="font-medium mr-1">Updated:</span>
                  {formatDate(resume.updatedAt)}
                </div>
              </div>
            </div>
            <div className="flex items-center space-x-2 ml-4">
              <button
                onClick={() => handleEdit(resume)}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors text-sm"
              >
                Edit
              </button>
              {deleteConfirm === resume.id ? (
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => handleDelete(resume.id)}
                    className="px-3 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors text-sm"
                  >
                    Confirm
                  </button>
                  <button
                    onClick={() => setDeleteConfirm(null)}
                    className="px-3 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400 transition-colors text-sm"
                  >
                    Cancel
                  </button>
                </div>
              ) : (
                <button
                  onClick={() => setDeleteConfirm(resume.id)}
                  className="px-4 py-2 bg-red-100 text-red-700 rounded-md hover:bg-red-200 transition-colors text-sm"
                >
                  Delete
                </button>
              )}
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}
