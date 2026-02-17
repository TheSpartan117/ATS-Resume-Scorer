/**
 * Overall score display component
 */
interface ScoreCardProps {
  score: number
}

export default function ScoreCard({ score }: ScoreCardProps) {
  const getScoreColor = (score: number): string => {
    if (score >= 80) return 'text-green-600'
    if (score >= 60) return 'text-yellow-600'
    return 'text-red-600'
  }

  const getScoreLabel = (score: number): string => {
    if (score >= 80) return 'Excellent'
    if (score >= 60) return 'Good'
    if (score >= 40) return 'Fair'
    return 'Needs Work'
  }

  const getScoreBgColor = (score: number): string => {
    if (score >= 80) return 'bg-green-50'
    if (score >= 60) return 'bg-yellow-50'
    return 'bg-red-50'
  }

  return (
    <div className={`rounded-lg p-8 text-center ${getScoreBgColor(score)}`}>
      <h2 className="text-lg font-semibold text-gray-700 mb-2">
        ATS Compatibility Score
      </h2>
      <div className={`text-6xl font-bold ${getScoreColor(score)} mb-2`}>
        {score}
        <span className="text-3xl">/100</span>
      </div>
      <p className={`text-xl font-semibold ${getScoreColor(score)}`}>
        {getScoreLabel(score)}
      </p>
    </div>
  )
}
