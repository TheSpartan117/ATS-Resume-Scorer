import React from 'react';

interface ModeIndicatorProps {
  mode: 'ats_simulation' | 'quality_coach';
  score: number;
  keywordDetails?: {
    required_match_pct?: number;
    preferred_match_pct?: number;
    match_percentage?: number;
  };
  breakdown: {
    [key: string]: number;
  };
  autoReject?: boolean;
}

export const ModeIndicator: React.FC<ModeIndicatorProps> = ({
  mode,
  score,
  keywordDetails,
  breakdown,
  autoReject
}) => {
  const isATSMode = mode === 'ats_simulation';

  const getScoreColor = () => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreStatus = () => {
    if (isATSMode) {
      if (autoReject) return '⚠️ Warning';
      if (score >= 60) return '✅ Likely to Pass';
      return '❌ May Not Pass';
    } else {
      if (score >= 80) return '✅ Strong';
      if (score >= 60) return '👍 Good';
      return '📝 Needs Work';
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      {/* Header */}
      <div className="mb-4">
        <div className="flex items-center gap-2 mb-1">
          <span className="text-2xl">{isATSMode ? '🎯' : '📝'}</span>
          <h3 className="text-lg font-semibold text-gray-900">
            {isATSMode ? 'ATS SIMULATION MODE' : 'QUALITY COACH MODE'}
          </h3>
        </div>
        <p className="text-sm text-gray-600">
          {isATSMode ? 'Scoring against job description' : 'General resume quality scoring'}
        </p>
      </div>

      {/* Score Circle */}
      <div className="flex items-center justify-center mb-6">
        <div className="relative">
          <div className="w-32 h-32 rounded-full bg-gradient-to-br from-teal-500 to-cyan-500 flex items-center justify-center shadow-lg">
            <div className="w-28 h-28 rounded-full bg-white flex flex-col items-center justify-center">
              <span className={`text-4xl font-bold ${getScoreColor()}`}>
                {score}
              </span>
              <span className="text-sm text-gray-500">/100</span>
            </div>
          </div>
        </div>
      </div>

      <div className="text-center mb-6">
        <span className="text-lg font-medium">{getScoreStatus()}</span>
        {isATSMode && (
          <p className="text-sm text-gray-600 mt-1">
            60% match needed to pass ATS
          </p>
        )}
      </div>

      {/* Keyword Details */}
      {isATSMode && keywordDetails && (
        <div className="mb-6 space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-gray-700">Required Keywords:</span>
            <span className={`font-semibold ${keywordDetails.required_match_pct >= 60 ? 'text-green-600' : 'text-red-600'}`}>
              {keywordDetails.required_match_pct?.toFixed(0)}% ✅
            </span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-gray-700">Preferred Keywords:</span>
            <span className="font-semibold text-gray-600">
              {keywordDetails.preferred_match_pct?.toFixed(0)}%
            </span>
          </div>
        </div>
      )}

      {!isATSMode && (
        <div className="mb-6 p-3 bg-blue-50 border border-blue-200 rounded-md">
          <p className="text-sm text-blue-800">
            💡 Want ATS simulation? Paste a job description when rescoring.
          </p>
        </div>
      )}

      {/* Breakdown */}
      <div className="space-y-3">
        <h4 className="text-sm font-semibold text-gray-700 mb-2">📊 BREAKDOWN</h4>
        {Object.entries(breakdown).map(([category, scoreVal]) => {
          const maxScore = isATSMode
            ? (category === 'keyword_match' ? 70 : category === 'ats_format' ? 20 : 10)
            : 25;
          const percentage = (scoreVal / maxScore) * 100;

          return (
            <div key={category} className="space-y-1">
              <div className="flex justify-between text-sm">
                <span className="text-gray-700 capitalize">
                  {category.replace(/_/g, ' ')}
                </span>
                <span className="font-semibold text-gray-900">
                  {scoreVal}/{maxScore}
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-gradient-to-r from-teal-500 to-cyan-500 h-2 rounded-full transition-all"
                  style={{ width: `${percentage}%` }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
