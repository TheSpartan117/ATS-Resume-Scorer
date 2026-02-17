/**
 * Issues list component with severity badges
 */
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
  icon: string
  bgColor: string
  textColor: string
  badgeColor: string
}

const issueCategories: IssueCategory[] = [
  {
    key: 'critical',
    label: 'Critical Issues',
    icon: '⚠️',
    bgColor: 'bg-red-50',
    textColor: 'text-red-900',
    badgeColor: 'bg-red-100 text-red-800'
  },
  {
    key: 'warnings',
    label: 'Warnings',
    icon: '⚡',
    bgColor: 'bg-yellow-50',
    textColor: 'text-yellow-900',
    badgeColor: 'bg-yellow-100 text-yellow-800'
  },
  {
    key: 'suggestions',
    label: 'Suggestions',
    icon: '💡',
    bgColor: 'bg-blue-50',
    textColor: 'text-blue-900',
    badgeColor: 'bg-blue-100 text-blue-800'
  },
  {
    key: 'info',
    label: 'Info',
    icon: 'ℹ️',
    bgColor: 'bg-gray-50',
    textColor: 'text-gray-900',
    badgeColor: 'bg-gray-100 text-gray-800'
  }
]

export default function IssuesList({ issues }: IssuesListProps) {
  const totalIssues = Object.values(issues).reduce((sum, arr) => sum + arr.length, 0)

  if (totalIssues === 0) {
    return (
      <div className="text-center py-8 text-gray-600">
        <p className="text-lg">✨ No issues found! Your resume looks great!</p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">
        Issues & Recommendations ({totalIssues})
      </h3>

      {issueCategories.map((category) => {
        const categoryIssues = issues[category.key]

        if (categoryIssues.length === 0) {
          return null
        }

        return (
          <div key={category.key} className={`rounded-lg p-4 ${category.bgColor}`}>
            <div className="flex items-center mb-3">
              <span className="text-2xl mr-2">{category.icon}</span>
              <h4 className={`font-semibold ${category.textColor}`}>
                {category.label}
              </h4>
              <span className={`ml-auto px-2 py-1 text-xs font-semibold rounded-full ${category.badgeColor}`}>
                {categoryIssues.length}
              </span>
            </div>

            <ul className="space-y-2">
              {categoryIssues.map((issue, idx) => (
                <li key={idx} className={`text-sm ${category.textColor} flex items-start`}>
                  <span className="mr-2 mt-0.5">•</span>
                  <span>{issue}</span>
                </li>
              ))}
            </ul>
          </div>
        )
      })}
    </div>
  )
}
