/**
 * User menu component with login/logout
 */
import { useState } from 'react'
import { useAuth } from '../hooks/useAuth'
import AuthModal from './AuthModal'

export default function UserMenu() {
  const { user, logout, isAuthenticated, isLoading } = useAuth()
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [isDropdownOpen, setIsDropdownOpen] = useState(false)

  if (isLoading) {
    return (
      <div className="text-sm text-gray-500">
        Loading...
      </div>
    )
  }

  if (!isAuthenticated) {
    return (
      <>
        <button
          onClick={() => setIsModalOpen(true)}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors font-semibold text-sm"
        >
          Login / Sign Up
        </button>
        <AuthModal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} />
      </>
    )
  }

  return (
    <div className="relative">
      {/* User Button */}
      <button
        onClick={() => setIsDropdownOpen(!isDropdownOpen)}
        className="flex items-center space-x-2 px-3 py-2 rounded-md hover:bg-gray-100 transition-colors"
      >
        <div className="w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center font-semibold">
          {user?.email.charAt(0).toUpperCase()}
        </div>
        <span className="text-sm font-medium text-gray-700">{user?.email}</span>
        <svg className="w-4 h-4 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {/* Dropdown Menu */}
      {isDropdownOpen && (
        <>
          {/* Backdrop */}
          <div
            className="fixed inset-0 z-10"
            onClick={() => setIsDropdownOpen(false)}
          />

          {/* Menu */}
          <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg z-20 border border-gray-200">
            <button
              onClick={() => {
                logout()
                setIsDropdownOpen(false)
              }}
              className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-md"
            >
              Logout
            </button>
          </div>
        </>
      )}
    </div>
  )
}
