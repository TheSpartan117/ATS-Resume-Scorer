/**
 * Upload page component
 */
import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import FileDropZone from './FileDropZone'
import UserMenu from './UserMenu'
import { uploadResume, getRoles, type RolesResponse } from '../api/client'
import type { UploadResponse } from '../types/resume'

export default function UploadPage() {
  const navigate = useNavigate()
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [jobDescription, setJobDescription] = useState('')
  const [selectedRole, setSelectedRole] = useState('')
  const [selectedLevel, setSelectedLevel] = useState('')
  const [rolesData, setRolesData] = useState<RolesResponse | null>(null)
  const [isUploading, setIsUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Fetch roles on component mount
  useEffect(() => {
    const fetchRoles = async () => {
      try {
        const data = await getRoles()
        setRolesData(data)
      } catch (err) {
        console.error('Failed to fetch roles:', err)
      }
    }

    fetchRoles()
  }, [])

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
        selectedRole || undefined,
        selectedLevel || undefined,
        undefined  // industry parameter kept for backward compatibility
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
        <div className="flex items-center justify-between mb-8">
          <div className="flex-1">
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
          <UserMenu />
        </div>

        <div className="mb-4"></div>

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

          {/* Role Selection (Optional) */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            <label htmlFor="role" className="block text-lg font-semibold text-gray-900 mb-2">
              Role <span className="text-sm font-normal text-gray-500">(Optional)</span>
            </label>
            <p className="text-sm text-gray-600 mb-3">
              Select your target role for tailored scoring and feedback
            </p>
            <select
              id="role"
              value={selectedRole}
              onChange={(e) => {
                setSelectedRole(e.target.value)
                setSelectedLevel('')  // Reset level when role changes
              }}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">Select role...</option>
              {rolesData && Object.entries(rolesData.categories).map(([category, roles]) => (
                <optgroup key={category} label={category.toUpperCase()}>
                  {roles.map((role) => (
                    <option key={role.id} value={role.id}>
                      {role.name}
                    </option>
                  ))}
                </optgroup>
              ))}
            </select>
          </div>

          {/* Experience Level (Conditional) */}
          {selectedRole && (
            <div className="bg-white rounded-lg shadow-sm p-6">
              <label className="block text-lg font-semibold text-gray-900 mb-2">
                Experience Level
              </label>
              <p className="text-sm text-gray-600 mb-3">
                Select your experience level for more accurate scoring
              </p>
              <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
                {rolesData?.levels.map((level) => (
                  <button
                    key={level.id}
                    type="button"
                    onClick={() => setSelectedLevel(level.id)}
                    className={`
                      px-4 py-3 rounded-md text-sm font-medium transition-all duration-150
                      border-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2
                      ${selectedLevel === level.id
                        ? 'bg-blue-600 text-white border-blue-600 shadow-md'
                        : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50 hover:border-gray-400'
                      }
                    `}
                    title={level.description}
                  >
                    {level.name}
                  </button>
                ))}
              </div>
              <p className="text-xs text-gray-500 mt-3">
                {rolesData?.levels.map(l => `${l.name}: ${l.description}`).join(' • ')}
              </p>
            </div>
          )}

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
