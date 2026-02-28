/**
 * Enhanced Results Display - Shows clear positive/negative areas with actionable feedback
 * Provides best UX for users to easily understand and upgrade their CV
 */
import { useState } from 'react'

// Fallback mapping for cryptic parameter codes returned by the backend.
// If the backend is later fixed to return human-readable strings the display
// function below will pass them through unchanged.
const PARAMETER_NAMES: Record<string, { name: string; tip: string }> = {
  'P1.1': { name: 'Required Keywords', tip: 'Add keywords from the job description to your resume' },
  'P1.2': { name: 'Preferred Keywords', tip: 'Include preferred skills mentioned in the job posting' },
  'P2.1': { name: 'Action Verbs', tip: 'Start bullet points with strong verbs like Led, Built, Drove, Increased' },
  'P2.2': { name: 'Quantification', tip: 'Add numbers to achievements (e.g., "increased sales by 30%")' },
  'P2.3': { name: 'Achievement Depth', tip: 'Replace vague phrases with specific accomplishments' },
  'P3.1': { name: 'Page Count', tip: 'Keep resume to 1 page (junior) or 2 pages (senior)' },
  'P3.2': { name: 'Word Count', tip: 'Aim for 400–800 words for optimal ATS scanning' },
  'P3.3': { name: 'Section Balance', tip: 'Distribute content evenly — avoid cramming all detail in one section' },
  'P3.4': { name: 'ATS Formatting', tip: 'Remove tables, graphics, and text boxes — use plain text' },
  'P4.1': { name: 'Grammar & Spelling', tip: 'Fix grammar and spelling errors — use Grammarly or similar' },
  'P4.2': { name: 'Professional Tone', tip: 'Use formal, professional language throughout' },
  'P5.1': { name: 'Years of Experience', tip: 'Ensure listed experience matches your declared seniority level' },
  'P5.2': { name: 'Career Recency', tip: 'Highlight recent roles — older experience matters less' },
  'P5.3': { name: 'Experience Depth', tip: 'Add 3–5 detailed bullet points per role with context and impact' },
  'P6.1': { name: 'Employment Gaps', tip: 'Add dates for all positions or briefly explain career breaks' },
  'P6.2': { name: 'Job Hopping', tip: 'Group short stints or explain contract/freelance work' },
  'P6.3': { name: 'Repetition', tip: 'Vary your language — avoid repeating the same verbs or phrases' },
  'P6.4': { name: 'Date Formatting', tip: 'Use consistent date format throughout (e.g., "Jan 2022 – Mar 2023")' },
  'P7.1': { name: 'Readability', tip: 'Use shorter sentences and simpler words for easier scanning' },
  'P7.2': { name: 'Bullet Structure', tip: 'Format experience as bullet points, not paragraphs' },
  'P7.3': { name: 'Passive Voice', tip: 'Replace "was responsible for" with active verbs like "managed", "led"' },
}

// Pattern that matches backend codes like "P6.1: Score 0%"
const CRYPTIC_CODE_PATTERN = /^(P\d+\.\d+):\s*Score\s*(\d+)%$/

interface ParsedIssue {
  code: string | null
  name: string
  score: string | null
  tip: string | null
  raw: string
}

/**
 * Parses a single issue string from the backend.
 * - If it matches the old "P6.1: Score 0%" format, look up a human-readable name
 *   and tip from PARAMETER_NAMES and extract the score value.
 * - Otherwise treat the whole string as a human-readable message with no extra tip.
 */
function parseIssue(issue: string): ParsedIssue {
  const match = issue.match(CRYPTIC_CODE_PATTERN)
  if (match) {
    const code = match[1]
    const score = match[2] + '%'
    const info = PARAMETER_NAMES[code]
    return {
      code,
      name: info ? info.name : code,
      score,
      tip: info ? info.tip : null,
      raw: issue,
    }
  }
  // Human-readable string from a fixed backend — display as-is
  return { code: null, name: issue, score: null, tip: null, raw: issue }
}

/**
 * Resolves a strength string — if it looks like a raw code ("P2.1: Score 80%")
 * return the human-readable name, otherwise return the string unchanged.
 */
function resolveStrengthLabel(strength: string): { name: string; tip: string | null } {
  const match = strength.match(CRYPTIC_CODE_PATTERN)
  if (match) {
    const code = match[1]
    const info = PARAMETER_NAMES[code]
    return { name: info ? info.name : code, tip: info ? info.tip : null }
  }
  return { name: strength, tip: null }
}

interface CategoryScore {
  score: number
  maxScore: number
  issues?: string[]
}

interface EnhancedResultsProps {
  overallScore: number
  breakdown: { [key: string]: CategoryScore }
  issues: {
    critical: string[]
    warnings: string[]
    suggestions: string[]
  }
  strengths?: string[]
}

export default function EnhancedResultsDisplay({ overallScore, breakdown, issues, strengths }: EnhancedResultsProps) {
  const [expandedCategory, setExpandedCategory] = useState<string | null>(null)

  // Calculate category percentages
  const getCategoryPercentage = (category: CategoryScore) => {
    if (category.maxScore === 0) return 0
    return Math.round((category.score / category.maxScore) * 100)
  }

  // Get category status and color (using full Tailwind class names for proper compilation)
  const getCategoryStatus = (percentage: number) => {
    if (percentage >= 80) return {
      label: 'Excellent',
      emoji: '✅',
      bgColor: 'bg-green-50',
      hoverBg: 'hover:bg-green-100',
      borderColor: 'border-green-200',
      barColor: 'bg-green-500',
      badgeBg: 'bg-green-200',
      badgeText: 'text-green-800'
    }
    if (percentage >= 60) return {
      label: 'Good',
      emoji: '👍',
      bgColor: 'bg-blue-50',
      hoverBg: 'hover:bg-blue-100',
      borderColor: 'border-blue-200',
      barColor: 'bg-blue-500',
      badgeBg: 'bg-blue-200',
      badgeText: 'text-blue-800'
    }
    if (percentage >= 40) return {
      label: 'Needs Work',
      emoji: '⚠️',
      bgColor: 'bg-yellow-50',
      hoverBg: 'hover:bg-yellow-100',
      borderColor: 'border-yellow-200',
      barColor: 'bg-yellow-500',
      badgeBg: 'bg-yellow-200',
      badgeText: 'text-yellow-800'
    }
    return {
      label: 'Critical',
      emoji: '❌',
      bgColor: 'bg-red-50',
      hoverBg: 'hover:bg-red-100',
      borderColor: 'border-red-200',
      barColor: 'bg-red-500',
      badgeBg: 'bg-red-200',
      badgeText: 'text-red-800'
    }
  }

  // Sort categories by performance (worst first for attention)
  const sortedCategories = Object.entries(breakdown).sort((a, b) => {
    const percentA = getCategoryPercentage(a[1])
    const percentB = getCategoryPercentage(b[1])
    return percentA - percentB
  })

  // Get overall rating (using full Tailwind class names for proper compilation)
  const getOverallRating = () => {
    if (overallScore >= 85) return {
      label: 'Excellent',
      emoji: '🎉',
      description: 'Top-tier resume! Ready for most roles.',
      bgGradient: 'bg-gradient-to-br from-green-50 to-green-100',
      border: 'border-green-300',
      circleColor: 'bg-green-500'
    }
    if (overallScore >= 70) return {
      label: 'Good',
      emoji: '👍',
      description: 'Strong resume with minor improvements needed.',
      bgGradient: 'bg-gradient-to-br from-blue-50 to-blue-100',
      border: 'border-blue-300',
      circleColor: 'bg-blue-500'
    }
    if (overallScore >= 55) return {
      label: 'Fair',
      emoji: '⚠️',
      description: 'Decent base but needs significant improvements.',
      bgGradient: 'bg-gradient-to-br from-yellow-50 to-yellow-100',
      border: 'border-yellow-300',
      circleColor: 'bg-yellow-500'
    }
    return {
      label: 'Needs Improvement',
      emoji: '❌',
      description: 'Major improvements required for ATS success.',
      bgGradient: 'bg-gradient-to-br from-red-50 to-red-100',
      border: 'border-red-300',
      circleColor: 'bg-red-500'
    }
  }

  const rating = getOverallRating()

  // Calculate strengths and weaknesses
  const categoryStrengths = sortedCategories.filter(([_, cat]) => getCategoryPercentage(cat) >= 70)
  const categoryWeaknesses = sortedCategories.filter(([_, cat]) => getCategoryPercentage(cat) < 60)

  return (
    <div className="space-y-6">
      {/* Overall Score Card */}
      <div className={`${rating.bgGradient} rounded-2xl border-2 ${rating.border} p-6 shadow-lg`}>
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <span className="text-4xl">{rating.emoji}</span>
              <div>
                <h2 className="text-2xl font-bold text-gray-900">{rating.label}</h2>
                <p className="text-sm text-gray-700">{rating.description}</p>
              </div>
            </div>
          </div>
          <div className="flex flex-col items-center">
            <div className={`w-24 h-24 rounded-full ${rating.circleColor} flex items-center justify-center shadow-xl`}>
              <div className="flex flex-col items-center text-white">
                <span className="text-4xl font-bold">{overallScore}</span>
                <span className="text-xs font-semibold">/100</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-3 gap-4">
        <div className="bg-green-50 border-2 border-green-200 rounded-xl p-4 text-center">
          <div className="text-3xl font-bold text-green-700">{categoryStrengths.length}</div>
          <div className="text-sm text-green-600 font-medium">Strong Areas</div>
        </div>
        <div className="bg-red-50 border-2 border-red-200 rounded-xl p-4 text-center">
          <div className="text-3xl font-bold text-red-700">{categoryWeaknesses.length}</div>
          <div className="text-sm text-red-600 font-medium">Need Attention</div>
        </div>
        <div className="bg-blue-50 border-2 border-blue-200 rounded-xl p-4 text-center">
          <div className="text-3xl font-bold text-blue-700">{issues.critical.length + issues.warnings.length}</div>
          <div className="text-sm text-blue-600 font-medium">Action Items</div>
        </div>
      </div>

      {/* Category Performance */}
      <div>
        <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
          📊 Category Performance
          <span className="text-sm font-normal text-gray-500">Click to see details</span>
        </h3>

        <div className="space-y-3">
          {sortedCategories.map(([categoryName, category]) => {
            const percentage = getCategoryPercentage(category)
            const status = getCategoryStatus(percentage)
            const isExpanded = expandedCategory === categoryName

            return (
              <div key={categoryName} className={`border-2 ${status.borderColor} rounded-xl overflow-hidden transition-all`}>
                {/* Category Header */}
                <button
                  onClick={() => setExpandedCategory(isExpanded ? null : categoryName)}
                  className={`w-full ${status.bgColor} ${status.hoverBg} p-4 flex items-center justify-between transition-colors`}
                >
                  <div className="flex items-center gap-3 flex-1">
                    <span className="text-2xl">{status.emoji}</span>
                    <div className="text-left flex-1">
                      <div className="font-bold text-gray-900">{categoryName}</div>
                      <div className="text-sm text-gray-600">
                        {category.score.toFixed(1)}/{category.maxScore} pts ({percentage}%)
                      </div>
                    </div>
                  </div>

                  {/* Progress Bar */}
                  <div className="flex items-center gap-4">
                    <div className="w-32 h-3 bg-gray-200 rounded-full overflow-hidden">
                      <div
                        className={`h-full ${status.barColor} transition-all`}
                        style={{ width: `${percentage}%` }}
                      />
                    </div>
                    <span className={`px-3 py-1 rounded-full text-xs font-bold ${status.badgeBg} ${status.badgeText}`}>
                      {status.label}
                    </span>
                    <svg
                      className={`w-5 h-5 text-gray-500 transition-transform ${isExpanded ? 'rotate-180' : ''}`}
                      fill="currentColor"
                      viewBox="0 0 20 20"
                    >
                      <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" />
                    </svg>
                  </div>
                </button>

                {/* Expanded Details */}
                {isExpanded && category.issues && category.issues.length > 0 && (
                  <div className={`bg-white border-t-2 ${status.borderColor} p-4`}>
                    <h4 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
                      <span>🔍</span> What to improve:
                    </h4>
                    <div className="space-y-3">
                      {category.issues.map((issue, idx) => {
                        const parsed = parseIssue(issue)
                        return (
                          <div
                            key={idx}
                            className="flex items-start gap-3 bg-amber-50 border border-amber-200 rounded-lg p-3"
                          >
                            <span className="text-amber-500 mt-0.5 flex-shrink-0 text-base">⚠️</span>
                            <div className="flex-1 min-w-0">
                              <div className="flex flex-wrap items-center gap-2 mb-1">
                                <span className="font-semibold text-gray-900 text-sm">{parsed.name}</span>
                                {parsed.score !== null && (
                                  <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-700 border border-red-200">
                                    Score: {parsed.score}
                                  </span>
                                )}
                              </div>
                              {parsed.tip && (
                                <p className="text-xs text-gray-500 leading-relaxed">{parsed.tip}</p>
                              )}
                            </div>
                          </div>
                        )
                      })}
                    </div>
                  </div>
                )}

                {isExpanded && (!category.issues || category.issues.length === 0) && (
                  <div className="bg-white border-t-2 border-green-200 p-4">
                    <p className="text-sm text-green-700 flex items-center gap-2">
                      <span>✨</span> This category looks great! No issues found.
                    </p>
                  </div>
                )}
              </div>
            )
          })}
        </div>
      </div>

      {/* Top Strengths */}
      {categoryStrengths.length > 0 && (
        <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl border-2 border-green-200 p-6">
          <h3 className="text-lg font-bold text-gray-900 mb-3 flex items-center gap-2">
            <span>💪</span> Your Strengths
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {categoryStrengths.map(([categoryName, category]) => {
              const resolved = resolveStrengthLabel(categoryName)
              return (
                <div key={categoryName} className="flex items-start gap-3 bg-white rounded-lg border border-green-200 p-3 shadow-sm">
                  <span className="text-green-500 text-xl flex-shrink-0">✓</span>
                  <div className="flex-1 min-w-0">
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="font-semibold text-gray-900 text-sm">{resolved.name}</span>
                      <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-700 border border-green-200">
                        {getCategoryPercentage(category)}%
                      </span>
                    </div>
                    {resolved.tip && (
                      <p className="text-xs text-gray-500 mt-0.5 leading-relaxed">{resolved.tip}</p>
                    )}
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      )}

      {/* Priority Improvements */}
      {issues.critical.length + issues.warnings.length > 0 && (
        <div className="bg-gradient-to-br from-orange-50 to-red-50 rounded-xl border-2 border-orange-300 p-6">
          <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
            <span>🎯</span> Priority Improvements
          </h3>

          {issues.critical.length > 0 && (
            <div className="mb-4">
              <div className="flex items-center gap-2 mb-3">
                <span className="text-red-500 text-xl">🔴</span>
                <h4 className="font-semibold text-red-800">Critical ({issues.critical.length})</h4>
              </div>
              <div className="space-y-2">
                {issues.critical.slice(0, 5).map((issue, idx) => {
                  const parsed = parseIssue(issue)
                  return (
                    <div key={idx} className="flex items-start gap-3 bg-red-50 border border-red-200 rounded-lg p-3">
                      <span className="text-red-500 flex-shrink-0 mt-0.5">⚠️</span>
                      <div className="flex-1 min-w-0">
                        <div className="flex flex-wrap items-center gap-2 mb-0.5">
                          <span className="font-semibold text-gray-900 text-sm">{parsed.name}</span>
                          {parsed.score !== null && (
                            <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-700 border border-red-200">
                              Score: {parsed.score}
                            </span>
                          )}
                        </div>
                        {parsed.tip && (
                          <p className="text-xs text-gray-500 leading-relaxed">{parsed.tip}</p>
                        )}
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>
          )}

          {issues.warnings.length > 0 && (
            <div>
              <div className="flex items-center gap-2 mb-3">
                <span className="text-yellow-500 text-xl">🟡</span>
                <h4 className="font-semibold text-yellow-800">Warnings ({issues.warnings.length})</h4>
              </div>
              <div className="space-y-2">
                {issues.warnings.slice(0, 5).map((issue, idx) => {
                  const parsed = parseIssue(issue)
                  return (
                    <div key={idx} className="flex items-start gap-3 bg-yellow-50 border border-yellow-200 rounded-lg p-3">
                      <span className="text-yellow-500 flex-shrink-0 mt-0.5">⚠️</span>
                      <div className="flex-1 min-w-0">
                        <div className="flex flex-wrap items-center gap-2 mb-0.5">
                          <span className="font-semibold text-gray-900 text-sm">{parsed.name}</span>
                          {parsed.score !== null && (
                            <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-700 border border-yellow-200">
                              Score: {parsed.score}
                            </span>
                          )}
                        </div>
                        {parsed.tip && (
                          <p className="text-xs text-gray-500 leading-relaxed">{parsed.tip}</p>
                        )}
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Quick Tips */}
      <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl border-2 border-blue-200 p-6">
        <h3 className="text-lg font-bold text-gray-900 mb-3 flex items-center gap-2">
          <span>💡</span> Quick Improvement Tips
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="flex items-start gap-3">
            <span className="text-2xl">📝</span>
            <div>
              <div className="font-semibold text-gray-800 text-sm">Use CAR Framework</div>
              <div className="text-xs text-gray-600">Context → Action → Result with metrics</div>
            </div>
          </div>
          <div className="flex items-start gap-3">
            <span className="text-2xl">📊</span>
            <div>
              <div className="font-semibold text-gray-800 text-sm">Add Numbers</div>
              <div className="text-xs text-gray-600">Quantify your achievements with %,  $, time saved</div>
            </div>
          </div>
          <div className="flex items-start gap-3">
            <span className="text-2xl">🎯</span>
            <div>
              <div className="font-semibold text-gray-800 text-sm">Strong Action Verbs</div>
              <div className="text-xs text-gray-600">Led, Architected, Delivered vs Responsible for</div>
            </div>
          </div>
          <div className="flex items-start gap-3">
            <span className="text-2xl">📏</span>
            <div>
              <div className="font-semibold text-gray-800 text-sm">Show Scope</div>
              <div className="text-xs text-gray-600">Team size, budget, users impacted, reach</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
