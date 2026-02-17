/**
 * API client for backend communication
 */
import axios, { AxiosError } from 'axios'
import type { UploadResponse, ApiError, ScoreResult } from '../types/resume'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 seconds
})

/**
 * Upload resume file and get initial score
 */
export async function uploadResume(
  file: File,
  jobDescription?: string,
  industry?: string
): Promise<UploadResponse> {
  const formData = new FormData()
  formData.append('file', file)

  if (jobDescription) {
    formData.append('jobDescription', jobDescription)
  }

  if (industry) {
    formData.append('industry', industry)
  }

  try {
    const response = await apiClient.post<UploadResponse>('/api/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  } catch (error) {
    const axiosError = error as AxiosError<ApiError>
    throw new Error(axiosError.response?.data?.detail || 'Failed to upload resume')
  }
}

/**
 * Health check
 */
export async function healthCheck(): Promise<{ status: string }> {
  const response = await apiClient.get('/health')
  return response.data
}

// Add new interface for score request
export interface ScoreRequest {
  fileName: string
  contact: {
    name?: string
    email?: string
    phone?: string
    location?: string
    linkedin?: string
    website?: string
  }
  experience: any[]
  education: any[]
  skills: string[]
  certifications: any[]
  metadata: {
    pageCount: number
    wordCount: number
    hasPhoto: boolean
    fileFormat: string
  }
  jobDescription?: string
  industry?: string
}

/**
 * Re-score edited resume content
 */
export async function rescoreResume(request: ScoreRequest): Promise<ScoreResult> {
  try {
    const response = await apiClient.post<ScoreResult>('/api/score', request)
    return response.data
  } catch (error) {
    const axiosError = error as AxiosError<ApiError>
    throw new Error(axiosError.response?.data?.detail || 'Failed to re-score resume')
  }
}

export default apiClient
