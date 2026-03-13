import { type Page, type Locator, expect } from '@playwright/test'

export class UploadPage {
  readonly page: Page
  readonly fileDropzone: Locator
  readonly fileInput: Locator
  readonly jobDescriptionInput: Locator
  readonly roleSelect: Locator
  readonly analyzeBtn: Locator
  readonly uploadError: Locator

  constructor(page: Page) {
    this.page = page
    this.fileDropzone = page.locator('[data-testid="file-dropzone"]')
    this.fileInput = page.locator('[data-testid="file-input"]')
    this.jobDescriptionInput = page.locator('[data-testid="job-description"]')
    this.roleSelect = page.locator('[data-testid="role-select"]')
    this.analyzeBtn = page.locator('[data-testid="analyze-btn"]')
    this.uploadError = page.locator('[data-testid="upload-error"]')
  }

  async goto() {
    await this.page.goto('/')
    await this.page.waitForLoadState('networkidle')
    await expect(this.page.locator('[data-testid="upload-page"]')).toBeVisible()
  }

  async uploadFile(fixturePath: string) {
    await this.fileInput.setInputFiles(fixturePath)
  }

  async setJobDescription(text: string) {
    await this.jobDescriptionInput.fill(text)
  }

  async selectRole(roleId: string) {
    await this.roleSelect.selectOption(roleId)
  }

  async clickAnalyze() {
    await this.analyzeBtn.click()
  }

  async uploadAndAnalyze(fixturePath: string, jobDescription?: string) {
    await this.uploadFile(fixturePath)
    if (jobDescription) await this.setJobDescription(jobDescription)
    await this.clickAnalyze()
  }

  async waitForResults() {
    await this.page.waitForURL('/results', { timeout: 90_000 })
    await expect(this.page.locator('[data-testid="results-page"]')).toBeVisible()
  }

  async isAnalyzeBtnEnabled() {
    return !(await this.analyzeBtn.isDisabled())
  }
}
