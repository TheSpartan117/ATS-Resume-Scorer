import { type Page, type Locator, expect } from '@playwright/test'

export class AuthModal {
  readonly page: Page
  readonly modal: Locator
  readonly emailInput: Locator
  readonly passwordInput: Locator
  readonly confirmPasswordInput: Locator
  readonly submitBtn: Locator
  readonly errorMsg: Locator
  readonly closeBtn: Locator
  readonly loginBtn: Locator

  constructor(page: Page) {
    this.page = page
    this.modal = page.locator('[data-testid="auth-modal"]')
    this.emailInput = page.locator('[data-testid="auth-email"]')
    this.passwordInput = page.locator('[data-testid="auth-password"]')
    this.confirmPasswordInput = page.locator('[data-testid="auth-confirm-password"]')
    this.submitBtn = page.locator('[data-testid="auth-submit"]')
    this.errorMsg = page.locator('[data-testid="auth-error"]')
    this.closeBtn = page.locator('[data-testid="auth-modal-close"]')
    this.loginBtn = page.locator('[data-testid="login-btn"]')
  }

  async open() {
    await this.loginBtn.click()
    await expect(this.modal).toBeVisible()
  }

  async switchToSignup() {
    await this.page.locator('button', { hasText: "Don't have an account? Sign up" }).click()
    await expect(this.confirmPasswordInput).toBeVisible()
  }

  async switchToLogin() {
    await this.page.locator('button', { hasText: 'Already have an account? Login' }).click()
    await expect(this.confirmPasswordInput).not.toBeVisible()
  }

  async fillLogin(email: string, password: string) {
    await this.emailInput.fill(email)
    await this.passwordInput.fill(password)
  }

  async fillSignup(email: string, password: string) {
    await this.switchToSignup()
    await this.emailInput.fill(email)
    await this.passwordInput.fill(password)
    await this.confirmPasswordInput.fill(password)
  }

  async submit() {
    await this.submitBtn.click()
  }

  async login(email: string, password: string) {
    await this.fillLogin(email, password)
    await this.submit()
    // Wait for modal to close on success
    await expect(this.modal).not.toBeVisible({ timeout: 15_000 })
  }

  async signup(email: string, password: string) {
    await this.switchToSignup()
    await this.emailInput.fill(email)
    await this.passwordInput.fill(password)
    await this.confirmPasswordInput.fill(password)
    await this.submit()
    await expect(this.modal).not.toBeVisible({ timeout: 15_000 })
  }

  async assertError(text: string) {
    await expect(this.errorMsg).toBeVisible()
    await expect(this.errorMsg).toContainText(text)
  }

  async close() {
    await this.closeBtn.click()
    await expect(this.modal).not.toBeVisible()
  }
}
