/**
 * Overall score display component
 */
interface ScoreCardProps {
  score: number
}

export default function ScoreCard({ score }: ScoreCardProps) {
  const getScoreGradient = (score: number): string => {
    if (score >= 80) return 'from-green-500 to-emerald-600'
    if (score >= 60) return 'from-yellow-500 to-amber-600'
    return 'from-red-500 to-rose-600'
  }

  const getScoreLabel = (score: number): string => {
    if (score >= 90) return 'Outstanding'
    if (score >= 80) return 'Excellent'
    if (score >= 70) return 'Good'
    if (score >= 60) return 'Fair'
    if (score >= 50) return 'Needs Improvement'
    return 'Needs Work'
  }

  const getScoreIcon = (score: number) => {
    if (score >= 80) {
      return (
        <svg className="w-8 h-8 text-white" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M6.267 3.455a3.066 3.066 0 001.745-.723 3.066 3.066 0 013.976 0 3.066 3.066 0 001.745.723 3.066 3.066 0 012.812 2.812c.051.643.304 1.254.723 1.745a3.066 3.066 0 010 3.976 3.066 3.066 0 00-.723 1.745 3.066 3.066 0 01-2.812 2.812 3.066 3.066 0 00-1.745.723 3.066 3.066 0 01-3.976 0 3.066 3.066 0 00-1.745-.723 3.066 3.066 0 01-2.812-2.812 3.066 3.066 0 00-.723-1.745 3.066 3.066 0 010-3.976 3.066 3.066 0 00.723-1.745 3.066 3.066 0 012.812-2.812zm7.44 5.252a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
        </svg>
      )
    }
    if (score >= 60) {
      return (
        <svg className="w-8 h-8 text-white" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
        </svg>
      )
    }
    return (
      <svg className="w-8 h-8 text-white" fill="currentColor" viewBox="0 0 20 20">
        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
      </svg>
    )
  }

  const circumference = 2 * Math.PI * 60
  const strokeDashoffset = circumference - (score / 100) * circumference

  return (
    <div className="text-center">
      <div className="flex items-center justify-center mb-2">
        <div className={`w-10 h-10 rounded-full bg-gradient-to-br ${getScoreGradient(score)} flex items-center justify-center shadow-lg`}>
          <svg className="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 20 20">
            {score >= 80 ? (
              <path fillRule="evenodd" d="M6.267 3.455a3.066 3.066 0 001.745-.723 3.066 3.066 0 013.976 0 3.066 3.066 0 001.745.723 3.066 3.066 0 012.812 2.812c.051.643.304 1.254.723 1.745a3.066 3.066 0 010 3.976 3.066 3.066 0 00-.723 1.745 3.066 3.066 0 01-2.812 2.812 3.066 3.066 0 00-1.745.723 3.066 3.066 0 01-3.976 0 3.066 3.066 0 00-1.745-.723 3.066 3.066 0 01-2.812-2.812 3.066 3.066 0 00-.723-1.745 3.066 3.066 0 010-3.976 3.066 3.066 0 00.723-1.745 3.066 3.066 0 012.812-2.812zm7.44 5.252a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
            ) : score >= 60 ? (
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            ) : (
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            )}
          </svg>
        </div>
      </div>

      <h2 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">
        ATS Compatibility Score
      </h2>

      {/* Circular Progress */}
      <div className="relative inline-flex items-center justify-center mb-3">
        <svg className="transform -rotate-90" width="150" height="150">
          <circle
            cx="75"
            cy="75"
            r="60"
            stroke="currentColor"
            strokeWidth="10"
            fill="none"
            className="text-gray-200"
          />
          <circle
            cx="75"
            cy="75"
            r="60"
            stroke="currentColor"
            strokeWidth="10"
            fill="none"
            strokeLinecap="round"
            className={`transition-all duration-1000 ease-out`}
            style={{
              strokeDasharray: circumference,
              strokeDashoffset: strokeDashoffset,
              stroke: score >= 80 ? '#10b981' : score >= 60 ? '#f59e0b' : '#ef4444'
            }}
          />
        </svg>
        <div className="absolute">
          <div className={`text-4xl font-extrabold bg-gradient-to-br ${getScoreGradient(score)} bg-clip-text text-transparent`}>
            {score}
          </div>
          <div className="text-xs text-gray-400 font-medium">/100</div>
        </div>
      </div>

      <div className={`inline-flex items-center px-3 py-1.5 rounded-full bg-gradient-to-r ${getScoreGradient(score)} shadow-lg`}>
        <p className="text-sm font-bold text-white">
          {getScoreLabel(score)}
        </p>
      </div>

      <p className="text-xs text-gray-500 mt-2">
        {score >= 80 ? 'Your resume is well-optimized for ATS systems' :
         score >= 60 ? 'Your resume has good ATS compatibility' :
         'Your resume needs optimization for ATS systems'}
      </p>
    </div>
  )
}
