/**
 * TypeScript types for ATS Resume Scorer
 */

export interface ContactInfo {
  name?: string
  email?: string
  phone?: string
  location?: string
  linkedin?: string
  website?: string
}

export interface ResumeMetadata {
  pageCount: number
  wordCount: number
  hasPhoto: boolean
  fileFormat: string
}

export interface CategoryBreakdown {
  score: number
  maxScore: number
  issues: string[]
}

export interface ScoreBreakdown {
  contactInfo: CategoryBreakdown
  formatting: CategoryBreakdown
  keywords: CategoryBreakdown
  content: CategoryBreakdown
  lengthDensity: CategoryBreakdown
  industrySpecific: CategoryBreakdown
}

export interface ScoreResult {
  overallScore: number
  breakdown: ScoreBreakdown
  issues: {
    critical: string[]
    warnings: string[]
    suggestions: string[]
    info: string[]
  }
  strengths: string[]
}

export interface UploadResponse {
  resumeId?: string
  fileName: string
  contact: ContactInfo
  experience?: any[]
  education?: any[]
  skills?: string[]
  certifications?: any[]
  metadata: ResumeMetadata
  score: ScoreResult
  uploadedAt: string
  jobDescription?: string
  industry?: string
}

export interface ApiError {
  detail: string
}

/**
 * Editable resume content for rich text editor
 */
export interface ResumeContent {
  fileName: string
  rawText: string  // HTML content from editor
  contact: ContactInfo
  metadata: ResumeMetadata
  jobDescription?: string
  industry?: string
}
