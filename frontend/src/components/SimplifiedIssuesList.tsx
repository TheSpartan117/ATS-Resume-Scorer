/**
 * Simplified Issues List - Groups by Severity (not by type)
 * Shows all suggestions in clear categories without fragmentation
 */
import { useState } from 'react'

interface IssuesListProps {
  issues: {
    critical: string[]
    warnings: string[]
    suggestions: string[]
    info?: string[]
  }
  overallScore: number
  breakdown?: {
    [key: string]: { score: number; maxScore: number; issues?: string[] }
  }
}

type SeverityLevel = 'critical' | 'warnings' | 'suggestions'

const SEVERITY_CONFIG = {
  critical: {
    label: 'Critical Issues',
    icon: '🔴',
    color: 'red',
    bgColor: 'bg-red-50',
    borderColor: 'border-red-200',
    textColor: 'text-red-900',
    badgeColor: 'bg-red-500'
  },
  warnings: {
    label: 'Warnings',
    icon: '🟡',
    color: 'yellow',
    bgColor: 'bg-yellow-50',
    borderColor: 'border-yellow-200',
    textColor: 'text-yellow-900',
    badgeColor: 'bg-yellow-500'
  },
  suggestions: {
    label: 'Suggestions',
    icon: '🔵',
    color: 'blue',
    bgColor: 'bg-blue-50',
    borderColor: 'border-blue-200',
    textColor: 'text-blue-900',
    badgeColor: 'bg-blue-500'
  }
}

export default function SimplifiedIssuesList({ issues, overallScore, breakdown }: IssuesListProps) {
  const [expandedSections, setExpandedSections] = useState<Set<SeverityLevel>>(
    new Set(['critical', 'warnings', 'suggestions'])
  )

  // Calculate total issues
  const totalIssues = (issues.critical?.length || 0) + (issues.warnings?.length || 0) + (issues.suggestions?.length || 0)

  const toggleSection = (severity: SeverityLevel) => {
    const newExpanded = new Set(expandedSections)
    if (newExpanded.has(severity)) {
      newExpanded.delete(severity)
    } else {
      newExpanded.add(severity)
    }
    setExpandedSections(newExpanded)
  }

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
      {/* Score Summary */}
      <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl border-2 border-blue-200 p-6 shadow-sm">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-bold text-gray-900 mb-1">Resume Analysis</h3>
            <p className="text-sm text-gray-600">
              {totalIssues} issue{totalIssues !== 1 ? 's' : ''} found across {Object.keys(breakdown || {}).length} categories
            </p>
          </div>
          <div className="flex items-center justify-center w-20 h-20 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 shadow-lg">
            <div className="flex flex-col items-center text-white">
              <span className="text-3xl font-bold">{overallScore}</span>
              <span className="text-xs">/100</span>
            </div>
          </div>
        </div>
      </div>

      {/* Issues by Severity */}
      {(['critical', 'warnings', 'suggestions'] as SeverityLevel[]).map((severity) => {
        const config = SEVERITY_CONFIG[severity]
        const issueList = issues[severity] || []

        if (issueList.length === 0) return null

        const isExpanded = expandedSections.has(severity)

        return (
          <div key={severity} className={`rounded-xl border-2 ${config.borderColor} ${config.bgColor} overflow-hidden`}>
            {/* Section Header */}
            <button
              onClick={() => toggleSection(severity)}
              className="w-full flex items-center justify-between p-4 hover:bg-opacity-80 transition-colors"
            >
              <div className="flex items-center space-x-3">
                <span className="text-2xl">{config.icon}</span>
                <div className="text-left">
                  <h4 className={`font-bold ${config.textColor}`}>
                    {config.label}
                  </h4>
                  <p className="text-xs text-gray-600">
                    {issueList.length} issue{issueList.length !== 1 ? 's' : ''}
                  </p>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <span className={`${config.badgeColor} text-white text-xs font-bold px-2 py-1 rounded-full`}>
                  {issueList.length}
                </span>
                <svg
                  className={`w-5 h-5 text-gray-600 transition-transform ${isExpanded ? 'rotate-180' : ''}`}
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </div>
            </button>

            {/* Issues List */}
            {isExpanded && (
              <div className="px-4 pb-4 space-y-2">
                {issueList.map((issue, idx) => (
                  <div
                    key={idx}
                    className="bg-white rounded-lg p-3 border border-gray-200 shadow-sm"
                  >
                    <div className="flex items-start space-x-2">
                      <span className="text-lg mt-0.5">
                        {severity === 'critical' ? '❌' : severity === 'warnings' ? '⚠️' : '💡'}
                      </span>
                      <p className="text-sm text-gray-700 flex-1">{issue}</p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )
      })}

      {/* Category Breakdown Summary */}
      {breakdown && Object.keys(breakdown).length > 0 && (
        <div className="bg-white rounded-xl border-2 border-gray-200 p-4">
          <h4 className="font-bold text-gray-900 mb-3">📊 Category Performance</h4>
          <div className="space-y-2">
            {Object.entries(breakdown).map(([category, data]) => {
              const percentage = data.maxScore > 0 ? (data.score / data.maxScore) * 100 : 0
              const color = percentage >= 80 ? 'bg-green-500' : percentage >= 60 ? 'bg-yellow-500' : 'bg-red-500'

              return (
                <div key={category} className="space-y-1">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-700">{category}</span>
                    <span className="font-semibold text-gray-900">
                      {data.score}/{data.maxScore}
                    </span>
                  </div>
                  {data.maxScore > 0 && (
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className={`${color} h-2 rounded-full transition-all`}
                        style={{ width: `${Math.min(percentage, 100)}%` }}
                      />
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        </div>
      )}
    </div>
  )
}
