/**
 * Upload page component
 */
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import FileDropZone from './FileDropZone'
import { uploadResume } from '../api/client'
import type { UploadResponse } from '../types/resume'

export default function UploadPage() {
  const navigate = useNavigate()
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [jobDescription, setJobDescription] = useState('')
  const [industry, setIndustry] = useState('')
  const [isUploading, setIsUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)

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
        industry || undefined
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
        <div className="text-center mb-12">
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

          {/* Industry (Optional) */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            <label htmlFor="industry" className="block text-lg font-semibold text-gray-900 mb-2">
              Industry <span className="text-sm font-normal text-gray-500">(Optional)</span>
            </label>
            <p className="text-sm text-gray-600 mb-3">
              Select your target industry for tailored scoring
            </p>
            <select
              id="industry"
              value={industry}
              onChange={(e) => setIndustry(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">Select industry...</option>
              <option value="tech">Technology / Software</option>
              <option value="sales">Sales / Marketing</option>
              <option value="finance">Finance / Accounting</option>
              <option value="healthcare">Healthcare</option>
              <option value="education">Education</option>
              <option value="other">Other</option>
            </select>
          </div>

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
