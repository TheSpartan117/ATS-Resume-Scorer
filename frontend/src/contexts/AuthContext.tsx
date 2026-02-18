/**
 * Authentication context for managing user state
 */
import { createContext, useState, useEffect, type ReactNode } from 'react'
import { signup, login, getCurrentUser, setAuthToken, type SignupRequest, type LoginRequest, type User } from '../api/client'

interface AuthContextType {
  user: User | null
  token: string | null
  isLoading: boolean
  isAuthenticated: boolean
  signup: (data: SignupRequest) => Promise<void>
  login: (data: LoginRequest) => Promise<void>
  logout: () => void
}

export const AuthContext = createContext<AuthContextType | undefined>(undefined)

interface AuthProviderProps {
  children: ReactNode
}

const TOKEN_KEY = 'ats_auth_token'

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null)
  const [token, setToken] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  // Initialize: Check for existing token and load user
  useEffect(() => {
    const initAuth = async () => {
      const storedToken = localStorage.getItem(TOKEN_KEY)

      if (storedToken) {
        setAuthToken(storedToken)
        setToken(storedToken)

        try {
          const userData = await getCurrentUser()
          setUser(userData)
        } catch (error) {
          // Token is invalid or expired
          console.error('Failed to load user:', error)
          localStorage.removeItem(TOKEN_KEY)
          setAuthToken(null)
          setToken(null)
        }
      }

      setIsLoading(false)
    }

    initAuth()
  }, [])

  const handleSignup = async (data: SignupRequest) => {
    const response = await signup(data)

    // Store token
    localStorage.setItem(TOKEN_KEY, response.accessToken)
    setAuthToken(response.accessToken)
    setToken(response.accessToken)
    setUser(response.user)
  }

  const handleLogin = async (data: LoginRequest) => {
    const response = await login(data)

    // Store token
    localStorage.setItem(TOKEN_KEY, response.accessToken)
    setAuthToken(response.accessToken)
    setToken(response.accessToken)
    setUser(response.user)
  }

  const handleLogout = () => {
    // Clear token
    localStorage.removeItem(TOKEN_KEY)
    setAuthToken(null)
    setToken(null)
    setUser(null)
  }

  const value: AuthContextType = {
    user,
    token,
    isLoading,
    isAuthenticated: !!user,
    signup: handleSignup,
    login: handleLogin,
    logout: handleLogout
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}
