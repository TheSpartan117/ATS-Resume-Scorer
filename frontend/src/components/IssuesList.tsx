/**
 * Enhanced Issues List Component with Tabbed Panel and Smart Actions
 * Implements Approach C: Click to Edit + Smart Templates
 */
import { useState, useEffect } from 'react'

interface EnhancedSuggestionFromBackend {
  id: string
  type: string
  severity: string
  title: string
  description: string
  template?: string
  quickFix?: {
    before: string
    after: string
  }
  keywords?: string[]
}

interface IssuesListProps {
  issues: {
    critical: string[]
    warnings: string[]
    suggestions: string[]
    info: string[]
  }
  overallScore: number
  enhancedSuggestions?: EnhancedSuggestionFromBackend[] // New prop for detailed suggestions
  onApplySuggestion?: (suggestion: AppliedSuggestion) => void
}

export interface AppliedSuggestion {
  id: string
  type: SuggestionType
  category: IssueCategory
  description: string
  action: 'insert' | 'replace' | 'format'
  content?: string
  searchText?: string
  replaceText?: string
}

type SuggestionType = 'missing_content' | 'formatting' | 'keyword' | 'writing'
type IssueCategory = 'critical' | 'warnings' | 'suggestions' | 'info'

interface ProcessedSuggestion {
  id: string
  type: SuggestionType
  category: IssueCategory
  description: string
  template?: string
  quickFix?: QuickFix
}

interface QuickFix {
  before: string
  after: string
  action: 'replace' | 'insert' | 'format'
}

// Smart Templates for Missing Content
const SMART_TEMPLATES: Record<string, string> = {
  'professional_summary': `<h2>Professional Summary</h2>
<p>Results-driven professional with [X] years of experience in [Your Field]. Proven track record of [Key Achievement]. Skilled in [Core Competencies]. Seeking to leverage expertise in [Target Role] to drive [Company Goal].</p>`,

  'contact_email': 'your.email@example.com',
  'contact_phone': '(555) 123-4567',
  'contact_linkedin': 'linkedin.com/in/yourprofile',

  'skills_section': `<h2>Skills</h2>
<p><strong>Technical Skills:</strong> List your technical skills here</p>
<p><strong>Soft Skills:</strong> Communication, Leadership, Problem-solving</p>`,

  'achievements': `<p><strong>Key Achievement:</strong> Increased efficiency by 30% through implementation of automated processes</p>`,
}

// Pattern matching for suggestion types
function categorizeSuggestion(description: string, category: IssueCategory): ProcessedSuggestion {
  const id = `${category}-${Math.random().toString(36).substr(2, 9)}`
  const lowerDesc = description.toLowerCase()

  // Missing Content (Red Badge)
  if (lowerDesc.includes('missing') || lowerDesc.includes('add') || lowerDesc.includes('include')) {
    if (lowerDesc.includes('email')) {
      return {
        id,
        type: 'missing_content',
        category,
        description,
        template: SMART_TEMPLATES.contact_email,
      }
    }
    if (lowerDesc.includes('phone')) {
      return {
        id,
        type: 'missing_content',
        category,
        description,
        template: SMART_TEMPLATES.contact_phone,
      }
    }
    if (lowerDesc.includes('linkedin')) {
      return {
        id,
        type: 'missing_content',
        category,
        description,
        template: SMART_TEMPLATES.contact_linkedin,
      }
    }
    if (lowerDesc.includes('summary') || lowerDesc.includes('objective')) {
      return {
        id,
        type: 'missing_content',
        category,
        description,
        template: SMART_TEMPLATES.professional_summary,
      }
    }
    if (lowerDesc.includes('skill')) {
      return {
        id,
        type: 'missing_content',
        category,
        description,
        template: SMART_TEMPLATES.skills_section,
      }
    }
    return {
      id,
      type: 'missing_content',
      category,
      description,
    }
  }

  // Formatting Issues (Yellow Badge)
  if (lowerDesc.includes('format') || lowerDesc.includes('capital') ||
      lowerDesc.includes('bullet') || lowerDesc.includes('spacing') ||
      lowerDesc.includes('consistent') || lowerDesc.includes('style')) {
    return {
      id,
      type: 'formatting',
      category,
      description,
      quickFix: {
        before: 'Inconsistent formatting detected',
        after: 'Apply consistent formatting',
        action: 'format'
      }
    }
  }

  // Keyword Issues (Blue Badge)
  if (lowerDesc.includes('keyword') || lowerDesc.includes('term') ||
      lowerDesc.includes('include the phrase')) {
    const keywordMatch = description.match(/"([^"]+)"|'([^']+)'/)
    const keyword = keywordMatch ? (keywordMatch[1] || keywordMatch[2]) : ''

    return {
      id,
      type: 'keyword',
      category,
      description,
      quickFix: keyword ? {
        before: 'Missing keyword',
        after: `Add "${keyword}" to relevant section`,
        action: 'insert'
      } : undefined
    }
  }

  // Writing Improvements (Green Badge)
  return {
    id,
    type: 'writing',
    category,
    description,
  }
}

// Tab configuration
const TABS = [
  {
    id: 'missing_content' as SuggestionType,
    label: 'Missing Content',
    icon: '🔴',
    color: 'red'
  },
  {
    id: 'formatting' as SuggestionType,
    label: 'Formatting',
    icon: '🟡',
    color: 'yellow'
  },
  {
    id: 'keyword' as SuggestionType,
    label: 'Keywords',
    icon: '🔵',
    color: 'blue'
  },
  {
    id: 'writing' as SuggestionType,
    label: 'Writing',
    icon: '🟢',
    color: 'green'
  }
]

export default function IssuesList({ issues, overallScore, enhancedSuggestions, onApplySuggestion }: IssuesListProps) {
  const [activeTab, setActiveTab] = useState<SuggestionType>('missing_content')
  const [processedSuggestions, setProcessedSuggestions] = useState<ProcessedSuggestion[]>([])
  const [appliedSuggestions, setAppliedSuggestions] = useState<Set<string>>(new Set())

  // Process all issues into categorized suggestions
  useEffect(() => {
    const all: ProcessedSuggestion[] = []

    // Use enhanced suggestions from backend if available
    if (enhancedSuggestions && enhancedSuggestions.length > 0) {
      if (import.meta.env.DEV) {
        console.log('Using enhanced suggestions from backend:', enhancedSuggestions.length)
      }
      enhancedSuggestions.forEach(enhanced => {
        all.push({
          id: enhanced.id,
          type: enhanced.type as SuggestionType,
          category: (enhanced.severity === 'high' ? 'critical' : enhanced.severity === 'medium' ? 'warnings' : 'suggestions') as IssueCategory,
          description: enhanced.title + (enhanced.description ? ': ' + enhanced.description : ''),
          template: enhanced.template,
          quickFix: enhanced.quickFix
        })
      })
    } else {
      // Fallback to old issue processing
      if (import.meta.env.DEV) {
        console.log('Using old issue format (no enhanced suggestions)')
      }
      Object.entries(issues).forEach(([category, items]) => {
        items.forEach(description => {
          all.push(categorizeSuggestion(description, category as IssueCategory))
        })
      })
    }

    setProcessedSuggestions(all)
  }, [issues, enhancedSuggestions])

  const totalIssues = processedSuggestions.length
  const appliedCount = appliedSuggestions.size
  const pendingCount = totalIssues - appliedCount
  const progressPercent = totalIssues > 0 ? Math.round((appliedCount / totalIssues) * 100) : 100

  // Filter suggestions by active tab
  const filteredSuggestions = processedSuggestions.filter(s => s.type === activeTab)

  // Get count for each tab
  const getTabCount = (type: SuggestionType) => {
    return processedSuggestions.filter(s => s.type === type && !appliedSuggestions.has(s.id)).length
  }

  const handleApply = (suggestion: ProcessedSuggestion) => {
    if (appliedSuggestions.has(suggestion.id)) return

    // Determine the action to take
    let action: 'insert' | 'replace' | 'format' = 'insert'
    let content = ''
    let searchText = ''
    let replaceText = ''

    if (suggestion.template) {
      action = 'insert'
      content = suggestion.template
    } else if (suggestion.quickFix) {
      action = suggestion.quickFix.action as 'insert' | 'replace' | 'format'
      searchText = suggestion.quickFix.before
      replaceText = suggestion.quickFix.after
    }

    const appliedSuggestion: AppliedSuggestion = {
      id: suggestion.id,
      type: suggestion.type,
      category: suggestion.category,
      description: suggestion.description,
      action,
      content,
      searchText,
      replaceText,
    }

    // Mark as applied
    setAppliedSuggestions(prev => new Set([...prev, suggestion.id]))

    // Notify parent component
    if (onApplySuggestion) {
      onApplySuggestion(appliedSuggestion)
    }
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
    <div className="flex flex-col h-full space-y-4">
      {/* Component 1: Top Section with Score & Progress */}
      <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl border-2 border-blue-200 p-4 shadow-sm">
        <div className="flex items-center justify-center mb-3">
          <div className="relative">
            <svg className="w-20 h-20 transform -rotate-90">
              <circle
                cx="40"
                cy="40"
                r="36"
                stroke="#e5e7eb"
                strokeWidth="8"
                fill="none"
              />
              <circle
                cx="40"
                cy="40"
                r="36"
                stroke={overallScore >= 80 ? '#10b981' : overallScore >= 60 ? '#f59e0b' : '#ef4444'}
                strokeWidth="8"
                fill="none"
                strokeDasharray={`${(overallScore / 100) * 226} 226`}
                strokeLinecap="round"
              />
            </svg>
            <div className="absolute inset-0 flex items-center justify-center">
              <span className="text-2xl font-bold text-gray-900">{overallScore}</span>
            </div>
          </div>
        </div>

        <div className="space-y-2 mb-3">
          <div className="flex justify-between text-xs text-gray-600 mb-1">
            <span>Progress</span>
            <span className="font-semibold">{progressPercent}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-blue-500 to-indigo-600 transition-all duration-500"
              style={{ width: `${progressPercent}%` }}
            />
          </div>
        </div>

        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-700 font-medium">
            {totalIssues} suggestion{totalIssues !== 1 ? 's' : ''} remaining
          </span>
        </div>

        <div className="flex items-center justify-between text-xs text-gray-600 mt-2">
          <div className="flex items-center space-x-1">
            <span className="text-green-600 font-semibold">✓</span>
            <span>{appliedCount} applied</span>
          </div>
          <div className="flex items-center space-x-1">
            <span className="text-orange-500 font-semibold">⏳</span>
            <span>{pendingCount} pending</span>
          </div>
        </div>
      </div>

      {/* Component 2: Tab Navigation */}
      <div className="flex border-b border-gray-200">
        {TABS.map(tab => {
          const count = getTabCount(tab.id)
          const isActive = activeTab === tab.id

          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex-1 py-2 px-3 text-xs font-medium transition-colors relative ${
                isActive
                  ? 'text-blue-700 border-b-2 border-blue-600'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <div className="flex items-center justify-center space-x-1">
                <span>{tab.icon}</span>
                <span className="hidden sm:inline">{tab.label}</span>
              </div>
              {count > 0 && (
                <span className={`absolute -top-1 -right-1 w-5 h-5 rounded-full text-xs flex items-center justify-center text-white font-bold ${
                  tab.color === 'red' ? 'bg-red-500' :
                  tab.color === 'yellow' ? 'bg-yellow-500' :
                  tab.color === 'blue' ? 'bg-blue-500' :
                  'bg-green-500'
                }`}>
                  {count}
                </span>
              )}
            </button>
          )
        })}
      </div>

      {/* Component 3 & 4: Suggestion Cards with Apply Actions */}
      <div className="flex-1 overflow-y-auto space-y-3 px-1 suggestions-scroll">
        {filteredSuggestions.length === 0 ? (
          <div className="text-center py-8 text-gray-500 text-sm">
            <svg className="w-12 h-12 mx-auto mb-2 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <p>All suggestions in this category have been applied!</p>
          </div>
        ) : (
          filteredSuggestions.map(suggestion => {
            const isApplied = appliedSuggestions.has(suggestion.id)

            return (
              <div
                key={suggestion.id}
                className={`bg-white rounded-lg border-2 p-3 shadow-sm transition-all ${
                  isApplied
                    ? 'border-green-300 bg-green-50 opacity-60'
                    : 'border-gray-200 hover:border-blue-300 hover:shadow-md'
                }`}
              >
                {/* Issue Description */}
                <div className="flex items-start space-x-2 mb-3">
                  <div className="flex-shrink-0 mt-0.5">
                    {isApplied ? (
                      <span className="text-green-600 font-bold text-lg">✓</span>
                    ) : (
                      <div className={`w-2 h-2 rounded-full ${
                        suggestion.category === 'critical' ? 'bg-red-500' :
                        suggestion.category === 'warnings' ? 'bg-yellow-500' :
                        suggestion.category === 'suggestions' ? 'bg-blue-500' :
                        'bg-gray-400'
                      }`} />
                    )}
                  </div>
                  <p className="text-xs text-gray-700 leading-relaxed flex-1">
                    {suggestion.description}
                  </p>
                </div>

                {/* Before/After Preview */}
                {(suggestion.template || suggestion.quickFix) && !isApplied && (
                  <div className="mb-3 space-y-2">
                    {suggestion.quickFix && (
                      <>
                        <div className="bg-red-50 border border-red-200 rounded p-2">
                          <div className="text-xs text-red-700 font-semibold mb-1">Before:</div>
                          <div className="text-xs text-red-900">{suggestion.quickFix.before}</div>
                        </div>
                        <div className="bg-green-50 border border-green-200 rounded p-2">
                          <div className="text-xs text-green-700 font-semibold mb-1">After:</div>
                          <div className="text-xs text-green-900">{suggestion.quickFix.after}</div>
                        </div>
                      </>
                    )}
                    {suggestion.template && (
                      <div className="bg-blue-50 border border-blue-200 rounded p-2">
                        <div className="text-xs text-blue-700 font-semibold mb-1">Template Preview:</div>
                        <div className="text-xs text-blue-900 line-clamp-3"
                             dangerouslySetInnerHTML={{ __html: suggestion.template.replace(/<[^>]+>/g, ' ').trim() }} />
                      </div>
                    )}
                  </div>
                )}

                {/* Apply Change Button - Disabled for manual editing */}
                {!isApplied && (
                  <button
                    disabled
                    className="w-full py-2 px-3 bg-gray-300 text-gray-600 rounded-lg font-medium text-xs cursor-not-allowed"
                    title="Please edit manually in the editor - automatic application temporarily disabled"
                  >
                    Manual Edit Recommended
                  </button>
                )}

                {isApplied && (
                  <div className="text-center text-xs text-green-700 font-medium">
                    ✓ Applied successfully
                  </div>
                )}
              </div>
            )
          })
        )}
      </div>
    </div>
  )
}
