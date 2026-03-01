import React, { useState } from 'react';

interface ModeIndicatorProps {
  mode: 'ats_simulation' | 'quality_coach';
  score: number;
  keywordDetails?: {
    required_match_pct?: number;
    preferred_match_pct?: number;
    match_percentage?: number;
    matchPercentage?: number;
    matchedKeywords?: string[];
    missingKeywords?: string[];
  };
  breakdown: {
    [key: string]: number | { score: number; maxScore: number };
  };
  autoReject?: boolean;
}

const KEYWORDS_PREVIEW = 5;

export const ModeIndicator: React.FC<ModeIndicatorProps> = ({
  mode,
  score,
  keywordDetails,
  breakdown,
  autoReject
}) => {
  const isATSMode = mode === 'ats_simulation';
  const [showAllMatched, setShowAllMatched] = useState(false);
  const [showAllMissing, setShowAllMissing] = useState(false);

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
        <p className="text-xs text-gray-500 mt-2">
          💡 Base score capped at 100 (125 with bonuses)
        </p>
      </div>

      {/* Keyword Details */}
      {keywordDetails && (
        <div className="mb-6 space-y-3">
          <h4 className="text-sm font-semibold text-gray-700">🔑 Keywords</h4>
          <div className="space-y-2">
            {/* Overall Match Percentage */}
            {(keywordDetails.matchPercentage !== undefined || keywordDetails.match_percentage !== undefined) && (
              <div className="flex justify-between text-sm">
                <span className="text-gray-700">Match Rate:</span>
                <span className={`font-semibold ${
                  (keywordDetails.matchPercentage ?? keywordDetails.match_percentage ?? 0) >= 60
                    ? 'text-green-600'
                    : (keywordDetails.matchPercentage ?? keywordDetails.match_percentage ?? 0) >= 40
                      ? 'text-yellow-600'
                      : 'text-red-600'
                }`}>
                  {(keywordDetails.matchPercentage ?? keywordDetails.match_percentage ?? 0).toFixed(0)}%
                </span>
              </div>
            )}

            {/* Matched Keywords */}
            {keywordDetails.matchedKeywords && keywordDetails.matchedKeywords.length > 0 && (
              <div className="text-sm">
                <span className="text-gray-700">✅ Matched ({keywordDetails.matchedKeywords.length}):</span>
                <div className="mt-1 flex flex-wrap gap-1">
                  {(showAllMatched
                    ? keywordDetails.matchedKeywords
                    : keywordDetails.matchedKeywords.slice(0, KEYWORDS_PREVIEW)
                  ).map((kw, idx) => (
                    <span key={idx} className="px-2 py-0.5 bg-green-100 text-green-800 rounded text-xs">
                      {kw}
                    </span>
                  ))}
                  {keywordDetails.matchedKeywords.length > KEYWORDS_PREVIEW && (
                    <button
                      onClick={() => setShowAllMatched(prev => !prev)}
                      className="px-2 py-0.5 bg-green-50 text-green-700 border border-green-300 rounded text-xs hover:bg-green-100 transition-colors cursor-pointer font-medium"
                    >
                      {showAllMatched
                        ? 'Show less ▲'
                        : `+${keywordDetails.matchedKeywords.length - KEYWORDS_PREVIEW} more ▼`}
                    </button>
                  )}
                </div>
              </div>
            )}

            {/* Missing Keywords */}
            {keywordDetails.missingKeywords && keywordDetails.missingKeywords.length > 0 && (
              <div className="text-sm">
                <span className="text-gray-700">❌ Missing ({keywordDetails.missingKeywords.length}):</span>
                <div className="mt-1 flex flex-wrap gap-1">
                  {(showAllMissing
                    ? keywordDetails.missingKeywords
                    : keywordDetails.missingKeywords.slice(0, KEYWORDS_PREVIEW)
                  ).map((kw, idx) => (
                    <span key={idx} className="px-2 py-0.5 bg-red-100 text-red-800 rounded text-xs">
                      {kw}
                    </span>
                  ))}
                  {keywordDetails.missingKeywords.length > KEYWORDS_PREVIEW && (
                    <button
                      onClick={() => setShowAllMissing(prev => !prev)}
                      className="px-2 py-0.5 bg-red-50 text-red-700 border border-red-300 rounded text-xs hover:bg-red-100 transition-colors cursor-pointer font-medium"
                    >
                      {showAllMissing
                        ? 'Show less ▲'
                        : `+${keywordDetails.missingKeywords.length - KEYWORDS_PREVIEW} more ▼`}
                    </button>
                  )}
                </div>
              </div>
            )}

            {/* Legacy format support */}
            {!keywordDetails.matchPercentage && !keywordDetails.match_percentage && (
              <>
                {keywordDetails.required_match_pct !== undefined && (
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-700">Required:</span>
                    <span className={`font-semibold ${keywordDetails.required_match_pct >= 60 ? 'text-green-600' : 'text-red-600'}`}>
                      {keywordDetails.required_match_pct.toFixed(0)}%
                    </span>
                  </div>
                )}
                {keywordDetails.preferred_match_pct !== undefined && (
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-700">Preferred:</span>
                    <span className="font-semibold text-gray-600">
                      {keywordDetails.preferred_match_pct.toFixed(0)}%
                    </span>
                  </div>
                )}
              </>
            )}
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
        {Object.entries(breakdown).map(([category, value]) => {
          // Handle both old format (number) and new format ({score, maxScore})
          let scoreVal: number;
          let maxScore: number;

          if (typeof value === 'object' && value !== null && 'score' in value) {
            // New format from Scorer V3
            scoreVal = value.score;
            maxScore = value.maxScore;
          } else {
            // Old format (fallback)
            scoreVal = value as number;
            // Use Scorer V3 max scores
            const categoryLower = category.toLowerCase();
            if (categoryLower.includes('keyword')) {
              maxScore = 35;
            } else if (categoryLower.includes('content')) {
              maxScore = 30;
            } else if (categoryLower.includes('format') || categoryLower.includes('structure')) {
              maxScore = 20;
            } else if (categoryLower.includes('polish')) {
              maxScore = 15;
            } else if (categoryLower.includes('experience') || categoryLower.includes('validation')) {
              maxScore = 15;
            } else if (categoryLower.includes('readability')) {
              maxScore = 10;
            } else if (categoryLower.includes('red flag')) {
              maxScore = 0; // Red flags are penalties
            } else {
              maxScore = 25; // Default fallback
            }
          }

          const percentage = maxScore > 0 ? (scoreVal / maxScore) * 100 : 0;

          return (
            <div key={category} className="space-y-1">
              <div className="flex justify-between text-sm">
                <span className="text-gray-700 capitalize">
                  {category.replace(/_/g, ' ')}
                </span>
                <span className="font-semibold text-gray-900">
                  {Number(scoreVal).toFixed(1)}/{maxScore}
                </span>
              </div>
              {maxScore > 0 && (
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-gradient-to-r from-teal-500 to-cyan-500 h-2 rounded-full transition-all"
                    style={{ width: `${Math.min(percentage, 100)}%` }}
                  />
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};
