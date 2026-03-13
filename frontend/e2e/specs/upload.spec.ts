/**
 * E2E tests: Resume upload and initial scoring flow
 *
 * Covers the critical path: upload file → score results displayed.
 * Uses page.route() to mock the backend so tests run without a live API.
 */
import { test, expect } from '@playwright/test'
import path from 'path'
import { fileURLToPath } from 'url'
import { UploadPage } from '../pages/UploadPage'
import { ResultsPage } from '../pages/ResultsPage'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)
const FIXTURE_PDF = path.join(__dirname, '../fixtures/test-resume.pdf')

const MOCK_SCORE_RESULT = {
  resumeId: null,
  fileName: 'test-resume.pdf',
  fileId: 'test-file-id',
  originalFileUrl: '/api/files/test-file-id.pdf',
  previewPdfUrl: null,
  editableHtml: null,
  contact: {
    name: 'John Doe',
    email: 'john.doe@example.com',
    phone: '(555) 123-4567',
    location: 'San Francisco, CA',
  },
  summary: null,
  experience: [
    {
      title: 'Software Engineer',
      company: 'Tech Corp',
      startDate: '2020-01',
      endDate: 'Present',
      description: 'Developed scalable web applications using Python and React',
    },
  ],
  education: [
    {
      degree: 'BS Computer Science',
      institution: 'Tech University',
      graduationDate: '2020',
    },
  ],
  skills: ['Python', 'JavaScript', 'React', 'AWS', 'Docker'],
  certifications: [],
  metadata: { pageCount: 1, wordCount: 350, hasPhoto: false, fileFormat: 'pdf' },
  score: {
    overallScore: 72,
    breakdown: {
      keywords: { score: 18, maxScore: 25, issues: [] },
      experience: { score: 18, maxScore: 20, issues: [] },
      education: { score: 12, maxScore: 15, issues: [] },
      contact: { score: 5, maxScore: 5, issues: [] },
      skills: { score: 10, maxScore: 12, issues: [] },
      format: { score: 9, maxScore: 13, issues: [] },
    },
    issues: { critical: [], warnings: ['Missing LinkedIn URL'], suggestions: [], info: [] },
    strengths: ['Strong technical skills', 'Quantified achievements'],
    mode: 'quality_coach',
    keywordDetails: null,
    autoReject: false,
    issueCounts: { critical: 0, warnings: 1, suggestions: 0 },
    enhancedSuggestions: [],
    prioritizedSuggestions: null,
    passProbability: null,
  },
  formatCheck: { passed: true, score: 90, checks: {}, issues: [] },
  scoringMode: 'quality_coach',
  role: 'software_engineer',
  level: 'mid',
  jobDescription: null,
  uploadedAt: new Date().toISOString(),
  industry: null,
  sessionId: 'test-session-id',
  sections: [],
  previewUrl: null,
}

const MOCK_ROLES = {
  categories: {
    engineering: [
      { id: 'software_engineer', name: 'Software Engineer', description: '' },
      { id: 'data_scientist', name: 'Data Scientist', description: '' },
    ],
  },
  levels: [
    { id: 'entry', name: 'Entry', description: '0-2 years' },
    { id: 'mid', name: 'Mid', description: '2-5 years' },
    { id: 'senior', name: 'Senior', description: '5+ years' },
  ],
}

test.describe('Resume Upload Flow', () => {
  let uploadPage: UploadPage
  let resultsPage: ResultsPage

  test.beforeEach(async ({ page }) => {
    // Mock API calls
    await page.route('**/api/roles', (route) =>
      route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(MOCK_ROLES) })
    )
    await page.route('**/api/upload', (route) =>
      route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(MOCK_SCORE_RESULT) })
    )

    uploadPage = new UploadPage(page)
    resultsPage = new ResultsPage(page)
  })

  test('should load upload page with correct elements', async ({ page }) => {
    await uploadPage.goto()

    await expect(page.locator('h1', { hasText: 'ATS Resume Scorer' })).toBeVisible()
    await expect(uploadPage.fileDropzone).toBeVisible()
    await expect(uploadPage.jobDescriptionInput).toBeVisible()
    await expect(uploadPage.roleSelect).toBeVisible()
    await expect(uploadPage.analyzeBtn).toBeDisabled()
  })

  test('analyze button enables only after file selection', async () => {
    await uploadPage.goto()
    await expect(uploadPage.analyzeBtn).toBeDisabled()

    await uploadPage.uploadFile(FIXTURE_PDF)
    await expect(uploadPage.analyzeBtn).toBeEnabled()
  })

  test('should upload PDF and navigate to results', async ({ page }) => {
    await uploadPage.goto()
    await uploadPage.uploadFile(FIXTURE_PDF)
    await uploadPage.clickAnalyze()
    await uploadPage.waitForResults()

    await resultsPage.assertLoaded()
    await resultsPage.assertScoreInRange(0, 100)

    await page.screenshot({ path: 'artifacts/upload-success.png' })
  })

  test('should display correct score from API response', async () => {
    await uploadPage.goto()
    await uploadPage.uploadFile(FIXTURE_PDF)
    await uploadPage.clickAnalyze()
    await uploadPage.waitForResults()

    const score = await resultsPage.getOverallScore()
    expect(score).toBe(72)
  })

  test('should upload with job description and role', async ({ page }) => {
    await uploadPage.goto()

    // Wait for role select to be enabled (roles loaded from API)
    await expect(uploadPage.roleSelect).toBeEnabled({ timeout: 15_000 })

    await uploadPage.uploadFile(FIXTURE_PDF)
    await uploadPage.setJobDescription('Looking for a Senior Software Engineer with React experience')
    await uploadPage.selectRole('software_engineer')
    await uploadPage.clickAnalyze()
    await uploadPage.waitForResults()

    await resultsPage.assertLoaded()
  })

  test('should show error on server failure', async ({ page }) => {
    await page.route('**/api/upload', (route) =>
      route.fulfill({ status: 500, contentType: 'application/json', body: JSON.stringify({ detail: 'Internal server error' }) })
    )

    await uploadPage.goto()
    await uploadPage.uploadFile(FIXTURE_PDF)
    await uploadPage.clickAnalyze()

    await expect(uploadPage.uploadError).toBeVisible({ timeout: 15_000 })
  })

  test('should navigate back to upload from results', async () => {
    await uploadPage.goto()
    await uploadPage.uploadFile(FIXTURE_PDF)
    await uploadPage.clickAnalyze()
    await uploadPage.waitForResults()

    await resultsPage.goBack()
    await expect(uploadPage.page.locator('[data-testid="upload-page"]')).toBeVisible()
  })

  test('should reject unsupported file types in dropzone', async ({ page }) => {
    await uploadPage.goto()

    // Try to set a .txt file (unsupported)
    await uploadPage.fileInput.setInputFiles({
      name: 'resume.txt',
      mimeType: 'text/plain',
      buffer: Buffer.from('plain text resume'),
    })

    // Analyze button should remain disabled
    await expect(uploadPage.analyzeBtn).toBeDisabled()

    // Error should appear in dropzone
    await expect(page.locator('text=Please upload a PDF or DOCX file')).toBeVisible()
  })
})
