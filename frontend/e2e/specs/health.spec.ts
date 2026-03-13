/**
 * E2E smoke tests: Run against live deployed URL
 * These tests verify the app is alive and the backend API is reachable.
 * Designed to run post-deployment (BASE_URL=https://your-app.vercel.app).
 */
import { test, expect } from '@playwright/test'

test.describe('Smoke Tests — Post-Deployment', () => {
  test('home page loads', async ({ page }) => {
    await page.goto('/')
    await expect(page).toHaveTitle(/ATS|Resume/i)
    await expect(page.locator('[data-testid="upload-page"]')).toBeVisible({ timeout: 30_000 })
  })

  test('file upload zone is visible', async ({ page }) => {
    await page.goto('/')
    await page.waitForLoadState('networkidle')
    await expect(page.locator('[data-testid="file-dropzone"]')).toBeVisible()
  })

  test('analyze button is initially disabled (no file selected)', async ({ page }) => {
    await page.goto('/')
    await page.waitForLoadState('networkidle')
    await expect(page.locator('[data-testid="analyze-btn"]')).toBeDisabled()
  })

  test('login button is visible for unauthenticated user', async ({ page }) => {
    await page.goto('/')
    await page.waitForLoadState('networkidle')
    await expect(page.locator('[data-testid="login-btn"]')).toBeVisible()
  })

  test('auth modal opens on login button click', async ({ page }) => {
    await page.goto('/')
    await page.waitForLoadState('networkidle')
    await page.locator('[data-testid="login-btn"]').click()
    await expect(page.locator('[data-testid="auth-modal"]')).toBeVisible()
    await page.locator('[data-testid="auth-modal-close"]').click()
    await expect(page.locator('[data-testid="auth-modal"]')).not.toBeVisible()
  })

  test('backend health endpoint responds', async ({ request }) => {
    const apiUrl = process.env.VITE_API_URL || process.env.API_URL || ''
    // Only run this test when a live API URL is explicitly configured
    test.skip(!apiUrl, 'Skipped: set VITE_API_URL or API_URL to test a live backend')

    const resp = await request.get(`${apiUrl}/health`)
    expect(resp.status()).toBe(200)
    const body = await resp.json()
    expect(body).toMatchObject({ status: 'healthy' })
  })

  test('roles API endpoint responds', async ({ request }) => {
    const apiUrl = process.env.VITE_API_URL || process.env.API_URL || ''
    test.skip(!apiUrl, 'Skipped: set VITE_API_URL or API_URL to test a live backend')

    const resp = await request.get(`${apiUrl}/api/roles`)
    expect(resp.status()).toBe(200)
    const body = await resp.json()
    expect(body).toHaveProperty('categories')
    expect(body).toHaveProperty('levels')
  })
})
