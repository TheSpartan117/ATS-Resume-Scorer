/**
 * Issues list component with severity badges
 */
import type { JSX } from 'react'

interface IssuesListProps {
  issues: {
    critical: string[]
    warnings: string[]
    suggestions: string[]
    info: string[]
  }
}

interface IssueCategory {
  key: keyof IssuesListProps['issues']
  label: string
  icon: JSX.Element
  bgGradient: string
  iconBg: string
  iconColor: string
  badgeColor: string
}

const issueCategories: IssueCategory[] = [
  {
    key: 'critical',
    label: 'Critical Issues',
    icon: (
      <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
        <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
      </svg>
    ),
    bgGradient: 'from-red-50 to-rose-50',
    iconBg: 'bg-red-100',
    iconColor: 'text-red-600',
    badgeColor: 'bg-red-500 text-white'
  },
  {
    key: 'warnings',
    label: 'Warnings',
    icon: (
      <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
        <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
      </svg>
    ),
    bgGradient: 'from-yellow-50 to-amber-50',
    iconBg: 'bg-yellow-100',
    iconColor: 'text-yellow-600',
    badgeColor: 'bg-yellow-500 text-white'
  },
  {
    key: 'suggestions',
    label: 'Suggestions',
    icon: (
      <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
        <path d="M11 3a1 1 0 10-2 0v1a1 1 0 102 0V3zM15.657 5.757a1 1 0 00-1.414-1.414l-.707.707a1 1 0 001.414 1.414l.707-.707zM18 10a1 1 0 01-1 1h-1a1 1 0 110-2h1a1 1 0 011 1zM5.05 6.464A1 1 0 106.464 5.05l-.707-.707a1 1 0 00-1.414 1.414l.707.707zM5 10a1 1 0 01-1 1H3a1 1 0 110-2h1a1 1 0 011 1zM8 16v-1h4v1a2 2 0 11-4 0zM12 14c.015-.34.208-.646.477-.859a4 4 0 10-4.954 0c.27.213.462.519.476.859h4.002z" />
      </svg>
    ),
    bgGradient: 'from-blue-50 to-indigo-50',
    iconBg: 'bg-blue-100',
    iconColor: 'text-blue-600',
    badgeColor: 'bg-blue-500 text-white'
  },
  {
    key: 'info',
    label: 'Info',
    icon: (
      <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
        <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
      </svg>
    ),
    bgGradient: 'from-gray-50 to-slate-50',
    iconBg: 'bg-gray-100',
    iconColor: 'text-gray-600',
    badgeColor: 'bg-gray-500 text-white'
  }
]

export default function IssuesList({ issues }: IssuesListProps) {
  const totalIssues = Object.values(issues).reduce((sum, arr) => sum + arr.length, 0)

  if (totalIssues === 0) {
    return (
      <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-2xl border-2 border-green-200 p-8 text-center">
        <div className="w-16 h-16 bg-gradient-to-br from-green-500 to-emerald-600 rounded-full flex items-center justify-center mx-auto mb-4 shadow-lg">
          <svg className="w-8 h-8 text-white" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
          </svg>
        </div>
        <h3 className="text-2xl font-bold text-green-900 mb-2">Perfect Score!</h3>
        <p className="text-green-700">No issues found. Your resume looks excellent!</p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-gradient-to-br from-amber-500 to-orange-600 rounded-lg flex items-center justify-center">
            <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
          <h3 className="text-2xl font-bold text-gray-900">
            Issues & Recommendations
          </h3>
        </div>
        <span className="px-4 py-2 bg-gray-100 rounded-full text-sm font-bold text-gray-700">
          {totalIssues} {totalIssues === 1 ? 'Item' : 'Items'}
        </span>
      </div>

      {issueCategories.map((category) => {
        const categoryIssues = issues[category.key]

        if (categoryIssues.length === 0) {
          return null
        }

        return (
          <div key={category.key} className={`bg-gradient-to-r ${category.bgGradient} rounded-xl border-2 border-gray-200 overflow-hidden`}>
            <div className="p-6">
              <div className="flex items-center mb-4">
                <div className={`w-10 h-10 rounded-lg ${category.iconBg} ${category.iconColor} flex items-center justify-center flex-shrink-0 mr-3`}>
                  {category.icon}
                </div>
                <h4 className="font-bold text-gray-900 text-lg flex-1">
                  {category.label}
                </h4>
                <span className={`px-3 py-1 text-sm font-bold rounded-full ${category.badgeColor} shadow-sm`}>
                  {categoryIssues.length}
                </span>
              </div>

              <div className="space-y-3">
                {categoryIssues.map((issue, idx) => (
                  <div key={idx} className="flex items-start space-x-3 bg-white p-4 rounded-lg border border-gray-200 shadow-sm">
                    <div className="flex-shrink-0 mt-0.5">
                      <div className="w-6 h-6 rounded-full bg-gray-100 flex items-center justify-center">
                        <span className="text-xs font-bold text-gray-600">{idx + 1}</span>
                      </div>
                    </div>
                    <p className="text-sm text-gray-700 leading-relaxed flex-1">{issue}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )
      })}
    </div>
  )
}
