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

/**
 * Set authentication token for API requests
 */
export function setAuthToken(token: string | null) {
  if (token) {
    apiClient.defaults.headers.common['Authorization'] = `Bearer ${token}`
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

export default apiClient
