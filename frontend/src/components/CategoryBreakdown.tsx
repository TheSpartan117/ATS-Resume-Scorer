/**
 * Category-by-category score breakdown
 */
import type { ScoreBreakdown } from '../types/resume'

interface CategoryBreakdownProps {
  breakdown: ScoreBreakdown
}

interface CategoryDisplay {
  key: keyof ScoreBreakdown
  label: string
  description: string
}

const categories: CategoryDisplay[] = [
  {
    key: 'contactInfo',
    label: 'Contact Information',
    description: 'Name, email, phone, location, links'
  },
  {
    key: 'formatting',
    label: 'Formatting & Structure',
    description: 'Page count, sections, consistency'
  },
  {
    key: 'keywords',
    label: 'Keyword Optimization',
    description: 'Match with job description'
  },
  {
    key: 'content',
    label: 'Content Quality',
    description: 'Action verbs, achievements, buzzwords'
  },
  {
    key: 'lengthDensity',
    label: 'Length & Density',
    description: 'Word count, white space'
  },
  {
    key: 'roleSpecific',
    label: 'Role-Specific',
    description: 'Role and experience level requirements'
  }
]

export default function CategoryBreakdown({ breakdown }: CategoryBreakdownProps) {
  const getPercentage = (score: number, maxScore: number): number => {
    return Math.round((score / maxScore) * 100)
  }

  const getBarColor = (percentage: number): string => {
    if (percentage >= 80) return 'bg-green-500'
    if (percentage >= 60) return 'bg-yellow-500'
    return 'bg-red-500'
  }

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">
        Category Breakdown
      </h3>

      {categories.map((category) => {
        const categoryData = breakdown[category.key]
        const percentage = getPercentage(categoryData.score, categoryData.maxScore)

        return (
          <div key={category.key} className="border-b border-gray-200 pb-4 last:border-0">
            <div className="flex justify-between items-start mb-2">
              <div className="flex-1">
                <h4 className="font-semibold text-gray-900">{category.label}</h4>
                <p className="text-sm text-gray-600">{category.description}</p>
              </div>
              <div className="text-right ml-4">
                <span className="text-lg font-bold text-gray-900">
                  {categoryData.score}/{categoryData.maxScore}
                </span>
              </div>
            </div>

            {/* Progress Bar */}
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className={`h-2 rounded-full transition-all duration-500 ${getBarColor(percentage)}`}
                style={{ width: `${percentage}%` }}
              />
            </div>

            {/* Category-specific issues */}
            {categoryData.issues.length > 0 && (
              <ul className="mt-2 space-y-1">
                {categoryData.issues.map((issue, idx) => (
                  <li key={idx} className="text-sm text-gray-700 flex items-start">
                    <span className="text-red-500 mr-2">•</span>
                    <span>{issue}</span>
                  </li>
                ))}
              </ul>
            )}
          </div>
        )
      })}
    </div>
  )
}
