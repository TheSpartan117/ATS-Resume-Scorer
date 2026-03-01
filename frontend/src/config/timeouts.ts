/**
 * Centralized timeout configuration
 */

/** API request timeout in milliseconds (90 seconds — accounts for Render cold start) */
export const API_TIMEOUT = 90000;

/** Auto-dismiss duration for error messages (5 seconds) */
export const ERROR_AUTO_DISMISS_MS = 5000;

/** Default debounce delay for user input (500ms) */
export const DEBOUNCE_DELAY_MS = 500;

/** Debounce delay for search/filter inputs (300ms) */
export const SEARCH_DEBOUNCE_MS = 300;

/** Polling interval for status updates (2 seconds) */
export const POLLING_INTERVAL_MS = 2000;
