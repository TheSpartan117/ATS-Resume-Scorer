/**
 * Saved resumes page
 */
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import { useEffect } from 'react'
import SavedResumesList from './SavedResumesList'
import UserMenu from './UserMenu'

export default function SavedResumesPage() {
  const navigate = useNavigate()
  const { isAuthenticated, isLoading } = useAuth()

  // Redirect to home if not authenticated
  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      navigate('/')
    }
  }, [isAuthenticated, isLoading, navigate])

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <p className="text-gray-600">Loading...</p>
      </div>
    )
  }

  if (!isAuthenticated) {
    return null
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8 max-w-4xl">
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
          <h1 className="text-3xl font-bold text-gray-900">
            My Saved Resumes
          </h1>
          <p className="text-gray-600 mt-2">
            View and manage your saved resumes
          </p>
        </div>

        {/* Resumes List */}
        <SavedResumesList />
      </div>
    </div>
  )
}
