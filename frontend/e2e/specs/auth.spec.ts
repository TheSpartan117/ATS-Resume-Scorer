/**
 * E2E tests: Authentication flows (signup, login, logout)
 */
import { test, expect } from '@playwright/test'
import { AuthModal } from '../pages/AuthModal'

const MOCK_USER = {
  id: 'test-user-id',
  email: 'test@example.com',
  isPremium: false,
  createdAt: new Date().toISOString(),
}

const MOCK_AUTH_RESPONSE = {
  accessToken: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0LXVzZXItaWQiLCJleHAiOjk5OTk5OTk5OTl9.mock',
  user: MOCK_USER,
}

test.describe('Authentication', () => {
  let authModal: AuthModal

  test.beforeEach(async ({ page }) => {
    // Mock roles so upload page loads fast
    await page.route('**/api/roles', (route) =>
      route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ categories: {}, levels: [] }) })
    )

    authModal = new AuthModal(page)
    await page.goto('/')
    await page.waitForLoadState('networkidle')
  })

  test.describe('Login', () => {
    test('should open auth modal when clicking Login / Sign Up', async () => {
      await authModal.open()
      await expect(authModal.modal).toBeVisible()
      await expect(authModal.emailInput).toBeVisible()
      await expect(authModal.passwordInput).toBeVisible()
    })

    test('should close modal on X button click', async () => {
      await authModal.open()
      await authModal.close()
      await expect(authModal.modal).not.toBeVisible()
    })

    test('should show validation error for invalid email', async ({ page }) => {
      await authModal.open()

      // Add novalidate to bypass browser's native HTML5 email validation
      // so React's JS-level validation runs and shows the error div
      await page.evaluate(() => {
        const form = document.querySelector('[data-testid="auth-modal"] form')
        form?.setAttribute('novalidate', 'true')
      })

      await authModal.emailInput.fill('not-an-email')
      await authModal.passwordInput.fill('password123')
      await authModal.submit()

      await authModal.assertError('valid email')
    })

    test('should show validation error for short password', async () => {
      await authModal.open()
      await authModal.emailInput.fill('test@example.com')
      await authModal.passwordInput.fill('short')
      await authModal.submit()

      await authModal.assertError('8 characters')
    })

    test('should show validation error for password without number', async () => {
      await authModal.open()
      await authModal.emailInput.fill('test@example.com')
      await authModal.passwordInput.fill('passwordonly')
      await authModal.submit()

      await authModal.assertError('number')
    })

    test('should show API error on invalid credentials', async ({ page }) => {
      await page.route('**/api/login', (route) =>
        route.fulfill({ status: 401, contentType: 'application/json', body: JSON.stringify({ detail: 'Invalid credentials' }) })
      )

      await authModal.open()
      await authModal.fillLogin('test@example.com', 'wrongpass1')
      await authModal.submit()

      await authModal.assertError(/credentials|Invalid/i)
    })

    test('should login successfully and show user menu', async ({ page }) => {
      await page.route('**/api/login', (route) =>
        route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(MOCK_AUTH_RESPONSE) })
      )
      await page.route('**/api/me', (route) =>
        route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(MOCK_USER) })
      )

      await authModal.open()
      await authModal.login('test@example.com', 'validpass1')

      // Modal should be gone, user menu should show
      await expect(page.locator('[data-testid="user-menu"]')).toBeVisible()
      await expect(page.locator('[data-testid="user-menu-btn"]')).toContainText('test@example.com')
    })
  })

  test.describe('Signup', () => {
    test('should switch to signup mode', async () => {
      await authModal.open()
      await authModal.switchToSignup()

      await expect(authModal.confirmPasswordInput).toBeVisible()
      await expect(authModal.page.locator('h2', { hasText: 'Sign Up' })).toBeVisible()
    })

    test('should show error when passwords do not match', async () => {
      await authModal.open()
      await authModal.switchToSignup()
      await authModal.emailInput.fill('new@example.com')
      await authModal.passwordInput.fill('securepass1')
      await authModal.confirmPasswordInput.fill('different1')
      await authModal.submit()

      await authModal.assertError('do not match')
    })

    test('should sign up successfully', async ({ page }) => {
      await page.route('**/api/signup', (route) =>
        route.fulfill({ status: 201, contentType: 'application/json', body: JSON.stringify(MOCK_AUTH_RESPONSE) })
      )
      await page.route('**/api/me', (route) =>
        route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(MOCK_USER) })
      )

      await authModal.open()
      await authModal.signup('new@example.com', 'securepass1')

      await expect(page.locator('[data-testid="user-menu"]')).toBeVisible()
    })

    test('should show error when email already exists', async ({ page }) => {
      await page.route('**/api/signup', (route) =>
        route.fulfill({ status: 400, contentType: 'application/json', body: JSON.stringify({ detail: 'Email already exists' }) })
      )

      await authModal.open()
      await authModal.switchToSignup()
      await authModal.emailInput.fill('existing@example.com')
      await authModal.passwordInput.fill('password123')
      await authModal.confirmPasswordInput.fill('password123')
      await authModal.submit()

      await authModal.assertError(/Email already exists/i)
    })
  })

  test.describe('Logout', () => {
    test.beforeEach(async ({ page }) => {
      // Mock login to get authenticated state
      await page.route('**/api/login', (route) =>
        route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(MOCK_AUTH_RESPONSE) })
      )
      await page.route('**/api/me', (route) =>
        route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(MOCK_USER) })
      )

      // Log in
      await authModal.open()
      await authModal.login('test@example.com', 'validpass1')
      await expect(page.locator('[data-testid="user-menu"]')).toBeVisible()
    })

    test('should logout and show login button', async ({ page }) => {
      await page.locator('[data-testid="user-menu-btn"]').click()
      await page.locator('[data-testid="logout-btn"]').click()

      await expect(page.locator('[data-testid="login-btn"]')).toBeVisible({ timeout: 5_000 })
      await expect(page.locator('[data-testid="user-menu"]')).not.toBeVisible()
    })
  })
})
