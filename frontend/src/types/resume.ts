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
  roleSpecific: CategoryBreakdown
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
  mode: string  // "ats_simulation" or "quality_coach"
  keywordDetails?: {
    required_matched?: number
    required_total?: number
    required_match_pct?: number
    preferred_matched?: number
    preferred_total?: number
    preferred_match_pct?: number
    match_percentage?: number
  }
  autoReject?: boolean
}

export interface FormatCheckResult {
  passed: boolean
  score: number
  checks: {
    [key: string]: any
  }
  issues: string[]
}

export interface UploadResponse {
  resumeId?: string
  fileName: string
  fileId?: string
  originalFileUrl?: string
  previewPdfUrl?: string
  editableHtml?: string
  contact: ContactInfo
  experience?: any[]
  education?: any[]
  skills?: string[]
  certifications?: any[]
  metadata: ResumeMetadata
  score: ScoreResult
  formatCheck: FormatCheckResult
  uploadedAt: string
  jobDescription?: string
  role?: string
  level?: string
  scoringMode?: string  // "ats_simulation" or "quality_coach"
  industry?: string  // Kept for backward compatibility
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
  role?: string
  level?: string
  industry?: string  // Kept for backward compatibility
}
