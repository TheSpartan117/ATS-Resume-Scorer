import { type Page, type Locator, expect } from '@playwright/test'

export class ResultsPage {
  readonly page: Page
  readonly resultsDisplay: Locator
  readonly scoreCard: Locator
  readonly overallScore: Locator
  readonly backToUpload: Locator
  readonly editResumeBtn: Locator

  constructor(page: Page) {
    this.page = page
    this.resultsDisplay = page.locator('[data-testid="results-display"]')
    this.scoreCard = page.locator('[data-testid="score-card"]')
    this.overallScore = page.locator('[data-testid="overall-score"]')
    this.backToUpload = page.locator('[data-testid="back-to-upload"]')
    this.editResumeBtn = page.locator('[data-testid="edit-resume-btn"]')
  }

  async assertLoaded() {
    await expect(this.page.locator('[data-testid="results-page"]')).toBeVisible({ timeout: 10_000 })
    await expect(this.resultsDisplay).toBeVisible()
    await expect(this.scoreCard).toBeVisible()
  }

  async getOverallScore(): Promise<number> {
    const text = await this.overallScore.textContent()
    return parseInt(text ?? '0', 10)
  }

  async assertScoreInRange(min: number, max: number) {
    const score = await this.getOverallScore()
    expect(score).toBeGreaterThanOrEqual(min)
    expect(score).toBeLessThanOrEqual(max)
  }

  async goBack() {
    await this.backToUpload.click()
    await this.page.waitForURL('/')
  }

  async clickEditResume() {
    await this.editResumeBtn.click()
  }
}
