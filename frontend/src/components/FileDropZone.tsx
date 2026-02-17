/**
 * File drop zone component for PDF/DOCX upload
 */
import { useState, useCallback } from 'react'

interface FileDropZoneProps {
  onFileSelect: (file: File) => void
  accept?: string
  maxSize?: number // in MB
}

export default function FileDropZone({
  onFileSelect,
  accept = '.pdf,.docx',
  maxSize = 10
}: FileDropZoneProps) {
  const [isDragging, setIsDragging] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const validateFile = (file: File): boolean => {
    setError(null)

    // Check file type
    const extension = file.name.split('.').pop()?.toLowerCase()
    if (!['pdf', 'docx'].includes(extension || '')) {
      setError('Please upload a PDF or DOCX file')
      return false
    }

    // Check file size
    const fileSizeMB = file.size / (1024 * 1024)
    if (fileSizeMB > maxSize) {
      setError(`File too large. Maximum size is ${maxSize}MB`)
      return false
    }

    return true
  }

  const handleDrop = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    setIsDragging(false)

    const files = Array.from(e.dataTransfer.files)
    if (files.length > 0) {
      const file = files[0]
      if (validateFile(file)) {
        onFileSelect(file)
      }
    }
  }, [onFileSelect, maxSize])

  const handleDragOver = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    setIsDragging(true)
  }, [])

  const handleDragLeave = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    setIsDragging(false)
  }, [])

  const handleFileInput = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files
    if (files && files.length > 0) {
      const file = files[0]
      if (validateFile(file)) {
        onFileSelect(file)
      }
    }
  }, [onFileSelect, maxSize])

  return (
    <div>
      <div
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        className={`
          border-2 border-dashed rounded-lg p-12 text-center cursor-pointer
          transition-colors duration-200
          ${isDragging
            ? 'border-blue-500 bg-blue-50'
            : 'border-gray-300 hover:border-gray-400'
          }
        `}
      >
        <input
          type="file"
          id="file-upload"
          accept={accept}
          onChange={handleFileInput}
          className="hidden"
        />

        <label htmlFor="file-upload" className="cursor-pointer">
          <svg
            className="mx-auto h-12 w-12 text-gray-400"
            stroke="currentColor"
            fill="none"
            viewBox="0 0 48 48"
            aria-hidden="true"
          >
            <path
              d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
              strokeWidth={2}
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
          <p className="mt-2 text-sm text-gray-600">
            <span className="font-semibold text-blue-600">Click to upload</span> or drag and drop
          </p>
          <p className="text-xs text-gray-500 mt-1">
            PDF or DOCX (Max {maxSize}MB)
          </p>
        </label>
      </div>

      {error && (
        <p className="mt-2 text-sm text-red-600">{error}</p>
      )}
    </div>
  )
}
