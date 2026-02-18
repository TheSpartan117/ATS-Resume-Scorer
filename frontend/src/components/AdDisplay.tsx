/**
 * Ad display component with countdown timer
 */
import { useEffect, useState } from 'react'
import { trackAdView } from '../api/client'

interface AdDisplayProps {
  onAdViewed: () => void
}

export default function AdDisplay({ onAdViewed }: AdDisplayProps) {
  const [countdown, setCountdown] = useState(3)

  useEffect(() => {
    // Track ad view on mount
    trackAdView()

    // Countdown timer
    const timer = setInterval(() => {
      setCountdown((prev) => {
        if (prev <= 1) {
          clearInterval(timer)
          onAdViewed()
          return 0
        }
        return prev - 1
      })
    }, 1000)

    return () => clearInterval(timer)
  }, [onAdViewed])

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div className="bg-white rounded-lg shadow-xl p-8 max-w-md w-full mx-4">
        <div className="text-center">
          <div className="mb-6">
            <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              Advertisement
            </h2>
            <p className="text-gray-600 mb-4">
              This is a placeholder for a sponsored advertisement
            </p>
          </div>

          <div className="bg-gray-50 rounded-lg p-6 mb-6">
            <p className="text-sm text-gray-500 mb-2">
              Ad content would appear here
            </p>
            <div className="text-4xl font-bold text-blue-600">
              {countdown}
            </div>
            <p className="text-sm text-gray-600 mt-2">
              seconds remaining
            </p>
          </div>

          <p className="text-xs text-gray-500">
            Sign up for premium to remove ads and unlock additional features
          </p>
        </div>
      </div>
    </div>
  )
}
