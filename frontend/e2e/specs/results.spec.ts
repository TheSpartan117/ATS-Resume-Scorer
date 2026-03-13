/**
 * E2E tests: Results page — score display, navigation, back flow
 */
import { test, expect } from '@playwright/test'
import path from 'path'
import { fileURLToPath } from 'url'
import { UploadPage } from '../pages/UploadPage'
import { ResultsPage } from '../pages/ResultsPage'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)
const FIXTURE_PDF = path.join(__dirname, '../fixtures/test-resume.pdf')

const makeScoreResult = (overallScore: number, mode = 'quality_coach') => ({
  resumeId: null,
  fileName: 'test-resume.pdf',
  fileId: 'file-id',
  originalFileUrl: '/api/files/file-id.pdf',
  previewPdfUrl: null,
  editableHtml: null,
  contact: { name: 'Jane Smith', email: 'jane@example.com', phone: '555-0000', location: 'NYC' },
  summary: null,
  experience: [],
  education: [],
  skills: ['Python', 'React'],
  certifications: [],
  metadata: { pageCount: 1, wordCount: 200, hasPhoto: false, fileFormat: 'pdf' },
  score: {
    overallScore,
    breakdown: {
      keywords: { score: 15, maxScore: 25, issues: [] },
      experience: { score: 12, maxScore: 20, issues: ['Missing quantified achievements'] },
      contact: { score: 5, maxScore: 5, issues: [] },
      skills: { score: 8, maxScore: 12, issues: [] },
      format: { score: 10, maxScore: 13, issues: [] },
    },
    issues: {
      critical: ['No LinkedIn URL provided'],
      warnings: ['Experience descriptions lack metrics'],
      suggestions: ['Add a professional summary'],
      info: [],
    },
    strengths: ['Good contact information', 'Relevant skills'],
    mode,
    keywordDetails: null,
    autoReject: false,
    issueCounts: { critical: 1, warnings: 1, suggestions: 1 },
    enhancedSuggestions: [],
    prioritizedSuggestions: null,
    passProbability: null,
  },
  formatCheck: { passed: true, score: 85, checks: {}, issues: [] },
  scoringMode: mode,
  role: 'software_engineer',
  level: 'mid',
  jobDescription: null,
  uploadedAt: new Date().toISOString(),
  industry: null,
  sessionId: 'session-id',
  sections: [],
  previewUrl: null,
})

test.describe('Results Page', () => {
  let uploadPage: UploadPage
  let resultsPage: ResultsPage

  test.beforeEach(async ({ page }) => {
    await page.route('**/api/roles', (route) =>
      route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ categories: {}, levels: [] }) })
    )

    uploadPage = new UploadPage(page)
    resultsPage = new ResultsPage(page)
  })

  test('should display score prominently', async ({ page }) => {
    await page.route('**/api/upload', (route) =>
      route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(makeScoreResult(78)) })
    )

    await uploadPage.goto()
    await uploadPage.uploadFile(FIXTURE_PDF)
    await uploadPage.clickAnalyze()
    await uploadPage.waitForResults()

    await resultsPage.assertLoaded()
    expect(await resultsPage.getOverallScore()).toBe(78)

    await page.screenshot({ path: 'artifacts/results-score.png', fullPage: true })
  })

  test('should redirect to upload if no result data in state', async ({ page }) => {
    // Navigate directly to /results without going through upload flow
    await page.goto('/results')
    await page.waitForURL('/', { timeout: 5_000 })
    await expect(page.locator('[data-testid="upload-page"]')).toBeVisible()
  })

  test('should show score in valid 0-100 range', async ({ page }) => {
    await page.route('**/api/upload', (route) =>
      route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(makeScoreResult(55)) })
    )

    await uploadPage.goto()
    await uploadPage.uploadFile(FIXTURE_PDF)
    await uploadPage.clickAnalyze()
    await uploadPage.waitForResults()

    await resultsPage.assertScoreInRange(0, 100)
  })

  test('should show back button and navigate back', async ({ page }) => {
    await page.route('**/api/upload', (route) =>
      route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(makeScoreResult(60)) })
    )

    await uploadPage.goto()
    await uploadPage.uploadFile(FIXTURE_PDF)
    await uploadPage.clickAnalyze()
    await uploadPage.waitForResults()

    await resultsPage.goBack()
    await expect(page.locator('[data-testid="upload-page"]')).toBeVisible()
  })

  test('should show Edit Resume button', async ({ page }) => {
    await page.route('**/api/upload', (route) =>
      route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(makeScoreResult(70)) })
    )

    await uploadPage.goto()
    await uploadPage.uploadFile(FIXTURE_PDF)
    await uploadPage.clickAnalyze()
    await uploadPage.waitForResults()

    await expect(resultsPage.editResumeBtn).toBeVisible()
  })

  test('should show high-score result correctly', async ({ page }) => {
    await page.route('**/api/upload', (route) =>
      route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(makeScoreResult(92)) })
    )

    await uploadPage.goto()
    await uploadPage.uploadFile(FIXTURE_PDF)
    await uploadPage.clickAnalyze()
    await uploadPage.waitForResults()

    expect(await resultsPage.getOverallScore()).toBe(92)
    await resultsPage.assertScoreInRange(85, 100)
  })

  test('should show ATS mode indicator when in ATS mode', async ({ page }) => {
    await page.route('**/api/upload', (route) =>
      route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(makeScoreResult(65, 'ats_simulation')) })
    )

    await uploadPage.goto()
    await uploadPage.uploadFile(FIXTURE_PDF)
    await uploadPage.clickAnalyze()
    await uploadPage.waitForResults()

    // ModeIndicator should display ATS mode
    await expect(page.locator('text=/ATS|ats/i').first()).toBeVisible()
  })
})
