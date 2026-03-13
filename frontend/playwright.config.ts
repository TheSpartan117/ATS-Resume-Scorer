import { defineConfig, devices } from '@playwright/test'

const BASE_URL = process.env.BASE_URL || 'http://localhost:5173'
const IS_CI = !!process.env.CI

export default defineConfig({
  testDir: './e2e',
  fullyParallel: !IS_CI,
  forbidOnly: IS_CI,
  retries: IS_CI ? 2 : 0,
  workers: IS_CI ? 1 : undefined,
  reporter: [
    ['html', { outputFolder: 'playwright-report', open: 'never' }],
    ['json', { outputFile: 'playwright-results.json' }],
    ['list'],
  ],
  use: {
    baseURL: BASE_URL,
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    actionTimeout: 15_000,
    navigationTimeout: 30_000,
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
    {
      name: 'mobile-chrome',
      use: { ...devices['Pixel 5'] },
    },
  ],
  // Only start dev server when running locally (not in CI against deployed URL)
  ...(process.env.BASE_URL
    ? {}
    : {
        webServer: {
          command: 'npm run dev',
          url: 'http://localhost:5173',
          reuseExistingServer: !IS_CI,
          timeout: 120_000,
          env: {
            VITE_API_URL: process.env.VITE_API_URL || 'http://localhost:8000',
          },
        },
      }),
})
