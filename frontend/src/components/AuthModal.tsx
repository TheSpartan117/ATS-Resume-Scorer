/**
 * Authentication modal component
 */
import { useState, type FormEvent } from 'react'
import { useAuth } from '../hooks/useAuth'

interface AuthModalProps {
  isOpen: boolean
  onClose: () => void
}

export default function AuthModal({ isOpen, onClose }: AuthModalProps) {
  const { signup, login } = useAuth()
  const [mode, setMode] = useState<'login' | 'signup'>('login')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  if (!isOpen) return null

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setError(null)

    // Validation
    if (!email || !password) {
      setError('Please fill in all fields')
      return
    }

    if (mode === 'signup' && password !== confirmPassword) {
      setError('Passwords do not match')
      return
    }

    if (password.length < 8) {
      setError('Password must be at least 8 characters')
      return
    }

    setIsSubmitting(true)

    try {
      if (mode === 'signup') {
        await signup({ email, password })
      } else {
        await login({ email, password })
      }

      // Success - close modal
      onClose()
      setEmail('')
      setPassword('')
      setConfirmPassword('')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Authentication failed')
    } finally {
      setIsSubmitting(false)
    }
  }

  const toggleMode = () => {
    setMode(mode === 'login' ? 'signup' : 'login')
    setError(null)
    setPassword('')
    setConfirmPassword('')
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6 relative">
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-gray-400 hover:text-gray-600"
          type="button"
        >
          <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>

        {/* Header */}
        <h2 className="text-2xl font-bold text-gray-900 mb-6">
          {mode === 'login' ? 'Login' : 'Sign Up'}
        </h2>

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Email */}
          <div>
            <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
              Email
            </label>
            <input
              type="email"
              id="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="you@example.com"
              disabled={isSubmitting}
            />
          </div>

          {/* Password */}
          <div>
            <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">
              Password
            </label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="At least 8 characters"
              disabled={isSubmitting}
            />
          </div>

          {/* Confirm Password (Signup only) */}
          {mode === 'signup' && (
            <div>
              <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700 mb-1">
                Confirm Password
              </label>
              <input
                type="password"
                id="confirmPassword"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Repeat your password"
                disabled={isSubmitting}
              />
            </div>
          )}

          {/* Error Message */}
          {error && (
            <div className="p-3 bg-red-50 border border-red-200 rounded-md">
              <p className="text-sm text-red-800">{error}</p>
            </div>
          )}

          {/* Submit Button */}
          <button
            type="submit"
            disabled={isSubmitting}
            className={`
              w-full py-2 px-4 rounded-md font-semibold text-white
              transition-colors duration-200
              ${isSubmitting
                ? 'bg-gray-300 cursor-not-allowed'
                : 'bg-blue-600 hover:bg-blue-700'
              }
            `}
          >
            {isSubmitting ? 'Please wait...' : mode === 'login' ? 'Login' : 'Sign Up'}
          </button>
        </form>

        {/* Toggle Mode */}
        <div className="mt-4 text-center">
          <button
            type="button"
            onClick={toggleMode}
            className="text-sm text-blue-600 hover:text-blue-800"
            disabled={isSubmitting}
          >
            {mode === 'login'
              ? "Don't have an account? Sign up"
              : 'Already have an account? Login'
            }
          </button>
        </div>
      </div>
    </div>
  )
}
