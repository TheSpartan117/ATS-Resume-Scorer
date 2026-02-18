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

// Add interfaces
export interface SignupRequest {
  email: string
  password: string
}

export interface LoginRequest {
  email: string
  password: string
}

export interface AuthResponse {
  accessToken: string
  user: {
    id: string
    email: string
    isPremium: boolean
    createdAt: string
  }
}

export interface User {
  id: string
  email: string
  isPremium: boolean
  createdAt: string
}

export interface SavedResume {
  id: string
  fileName: string
  content: any
  score: ScoreResult
  createdAt: string
  updatedAt: string
}

/**
 * Set authentication token for API requests
 * Validates token format and expiration before setting
 */
export function setAuthToken(token: string | null) {
  if (token) {
    // Basic JWT validation: check format and expiration
    try {
      const parts = token.split('.')
      if (parts.length !== 3) {
        console.warn('Invalid JWT format')
        return
      }

      // Decode payload to check expiration
      const payload = JSON.parse(atob(parts[1]))
      if (payload.exp && payload.exp * 1000 < Date.now()) {
        console.warn('Token expired')
        return
      }

      apiClient.defaults.headers.common['Authorization'] = `Bearer ${token}`
    } catch (error) {
      console.error('Failed to validate token:', error)
    }
  } else {
    delete apiClient.defaults.headers.common['Authorization']
  }
}

/**
 * Sign up new user
 */
export async function signup(data: SignupRequest): Promise<AuthResponse> {
  try {
    const response = await apiClient.post<AuthResponse>('/api/signup', data)
    return response.data
  } catch (error) {
    const axiosError = error as AxiosError<ApiError>
    throw new Error(axiosError.response?.data?.detail || 'Signup failed')
  }
}

/**
 * Login existing user
 */
export async function login(data: LoginRequest): Promise<AuthResponse> {
  try {
    const response = await apiClient.post<AuthResponse>('/api/login', data)
    return response.data
  } catch (error) {
    const axiosError = error as AxiosError<ApiError>
    throw new Error(axiosError.response?.data?.detail || 'Login failed')
  }
}

/**
 * Get current user info
 */
export async function getCurrentUser(): Promise<User> {
  try {
    const response = await apiClient.get<User>('/api/me')
    return response.data
  } catch (error) {
    const axiosError = error as AxiosError<ApiError>
    throw new Error(axiosError.response?.data?.detail || 'Failed to get user info')
  }
}

/**
 * Save resume for authenticated user
 */
export async function saveResume(data: ScoreRequest): Promise<SavedResume> {
  try {
    const response = await apiClient.post<SavedResume>('/api/resumes', data)
    return response.data
  } catch (error) {
    const axiosError = error as AxiosError<ApiError>
    throw new Error(axiosError.response?.data?.detail || 'Failed to save resume')
  }
}

/**
 * Get all saved resumes
 */
export async function getSavedResumes(): Promise<SavedResume[]> {
  try {
    const response = await apiClient.get<SavedResume[]>('/api/resumes')
    return response.data
  } catch (error) {
    const axiosError = error as AxiosError<ApiError>
    throw new Error(axiosError.response?.data?.detail || 'Failed to load resumes')
  }
}

/**
 * Get single saved resume
 */
export async function getSavedResume(id: string): Promise<SavedResume> {
  try {
    const response = await apiClient.get<SavedResume>(`/api/resumes/${id}`)
    return response.data
  } catch (error) {
    const axiosError = error as AxiosError<ApiError>
    throw new Error(axiosError.response?.data?.detail || 'Failed to load resume')
  }
}

/**
 * Update saved resume
 */
export async function updateResume(id: string, data: ScoreRequest): Promise<SavedResume> {
  try {
    const response = await apiClient.put<SavedResume>(`/api/resumes/${id}`, data)
    return response.data
  } catch (error) {
    const axiosError = error as AxiosError<ApiError>
    throw new Error(axiosError.response?.data?.detail || 'Failed to update resume')
  }
}

/**
 * Delete saved resume
 */
export async function deleteResume(id: string): Promise<void> {
  try {
    await apiClient.delete(`/api/resumes/${id}`)
  } catch (error) {
    const axiosError = error as AxiosError<ApiError>
    throw new Error(axiosError.response?.data?.detail || 'Failed to delete resume')
  }
}

/**
 * Check if ad should be shown
 */
export async function shouldShowAd(): Promise<{ showAd: boolean; message?: string }> {
  try {
    const response = await apiClient.get<{ showAd: boolean; message?: string }>('/api/should-show-ad')
    return response.data
  } catch (error) {
    // If not authenticated, show ad after first score
    return { showAd: true, message: 'Ad required for additional scoring' }
  }
}

/**
 * Track ad view
 */
export async function trackAdView(): Promise<void> {
  try {
    await apiClient.post('/api/ad-view')
  } catch (error) {
    console.error('Failed to track ad view:', error)
  }
}

export default apiClient
