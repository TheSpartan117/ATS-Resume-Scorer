/**
 * Category-by-category score breakdown
 */
import type { JSX } from 'react'
import type { ScoreBreakdown } from '../types/resume'

interface CategoryBreakdownProps {
  breakdown: ScoreBreakdown
}

interface CategoryDisplay {
  key: keyof ScoreBreakdown
  label: string
  description: string
}

interface CategoryConfig extends CategoryDisplay {
  icon: JSX.Element
  color: string
}

const categories: CategoryConfig[] = [
  {
    key: 'contactInfo',
    label: 'Contact Information',
    description: 'Name, email, phone, location, links',
    color: 'blue',
    icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
      </svg>
    )
  },
  {
    key: 'formatting',
    label: 'Formatting & Structure',
    description: 'Page count, sections, consistency',
    color: 'purple',
    icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 10h16M4 14h16M4 18h16" />
      </svg>
    )
  },
  {
    key: 'keywords',
    label: 'Keyword Optimization',
    description: 'Match with job description',
    color: 'indigo',
    icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 20l4-16m2 16l4-16M6 9h14M4 15h14" />
      </svg>
    )
  },
  {
    key: 'content',
    label: 'Content Quality',
    description: 'Action verbs, achievements, buzzwords',
    color: 'green',
    icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
      </svg>
    )
  },
  {
    key: 'lengthDensity',
    label: 'Length & Density',
    description: 'Word count, white space',
    color: 'yellow',
    icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
      </svg>
    )
  },
  {
    key: 'roleSpecific',
    label: 'Role-Specific',
    description: 'Role and experience level requirements',
    color: 'pink',
    icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
      </svg>
    )
  }
]

export default function CategoryBreakdown({ breakdown }: CategoryBreakdownProps) {
  const getPercentage = (score: number, maxScore: number): number => {
    return Math.round((score / maxScore) * 100)
  }

  const getBarGradient = (percentage: number): string => {
    if (percentage >= 80) return 'from-green-500 to-emerald-600'
    if (percentage >= 60) return 'from-yellow-500 to-amber-600'
    return 'from-red-500 to-rose-600'
  }

  const getIconBgColor = (color: string): string => {
    const colors: Record<string, string> = {
      blue: 'bg-blue-100 text-blue-600',
      purple: 'bg-purple-100 text-purple-600',
      indigo: 'bg-indigo-100 text-indigo-600',
      green: 'bg-green-100 text-green-600',
      yellow: 'bg-yellow-100 text-yellow-600',
      pink: 'bg-pink-100 text-pink-600'
    }
    return colors[color] || 'bg-gray-100 text-gray-600'
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center space-x-3 mb-6">
        <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-lg flex items-center justify-center">
          <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
        </div>
        <h3 className="text-2xl font-bold text-gray-900">
          Category Breakdown
        </h3>
      </div>

      {categories.map((category) => {
        const categoryData = breakdown[category.key]
        const percentage = getPercentage(categoryData.score, categoryData.maxScore)

        return (
          <div key={category.key} className="bg-white rounded-xl p-6 border border-gray-200 hover:shadow-lg transition-shadow duration-200">
            <div className="flex justify-between items-start mb-4">
              <div className="flex items-start space-x-3 flex-1">
                <div className={`w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0 ${getIconBgColor(category.color)}`}>
                  {category.icon}
                </div>
                <div className="flex-1">
                  <h4 className="font-bold text-gray-900 text-lg">{category.label}</h4>
                  <p className="text-sm text-gray-500 mt-0.5">{category.description}</p>
                </div>
              </div>
              <div className="text-right ml-4">
                <div className="text-2xl font-bold text-gray-900">
                  {Number(categoryData.score).toFixed(1)}
                  <span className="text-sm text-gray-400 font-medium">/{categoryData.maxScore}</span>
                </div>
                <div className="text-xs text-gray-500 mt-0.5">{percentage}%</div>
              </div>
            </div>

            {/* Progress Bar */}
            <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden shadow-inner">
              <div
                className={`h-3 rounded-full bg-gradient-to-r ${getBarGradient(percentage)} transition-all duration-700 ease-out shadow-sm`}
                style={{ width: `${percentage}%` }}
              />
            </div>

            {/* Category-specific issues */}
            {categoryData.issues.length > 0 && (
              <div className="mt-4 space-y-2">
                {categoryData.issues.map((issue, idx) => (
                  <div key={idx} className="flex items-start space-x-2 text-sm bg-gray-50 p-3 rounded-lg border border-gray-200">
                    <svg className="w-4 h-4 text-amber-500 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                    </svg>
                    <span className="text-gray-700">{issue}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        )
      })}
    </div>
  )
}
