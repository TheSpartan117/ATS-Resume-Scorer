// frontend/src/components/SuggestionCarousel.tsx
import { useState } from 'react';
import type { SuggestionCarouselProps } from '../types/suggestion';

export default function SuggestionCarousel({
  score,
  suggestions,
  issueCounts,
  onRescore,
  onSuggestionClick,
  isRescoring = false
}: SuggestionCarouselProps) {
  const [currentIndex, setCurrentIndex] = useState(0);

  const currentSuggestion = suggestions[currentIndex];

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'bg-red-100 text-red-800 border-red-500';
      case 'warning': return 'bg-yellow-100 text-yellow-800 border-yellow-500';
      case 'suggestion': return 'bg-blue-100 text-blue-800 border-blue-500';
      default: return 'bg-gray-100 text-gray-800 border-gray-500';
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600 bg-green-50';
    if (score >= 60) return 'text-yellow-600 bg-yellow-50';
    return 'text-red-600 bg-red-50';
  };

  const handlePrev = () => {
    setCurrentIndex((prev) => (prev > 0 ? prev - 1 : suggestions.length - 1));
  };

  const handleNext = () => {
    setCurrentIndex((prev) => (prev < suggestions.length - 1 ? prev + 1 : 0));
  };

  if (!currentSuggestion) {
    return (
      <div className="bg-gradient-to-r from-green-50 to-blue-50 border-b border-gray-200 px-6 py-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className={`px-4 py-2 rounded-full font-bold text-lg ${getScoreColor(score)}`}>
              Score: {score}/100
            </div>
            <span className="text-green-600 font-semibold">✅ No issues found!</span>
          </div>
          <button
            onClick={onRescore}
            disabled={isRescoring}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors disabled:opacity-50"
          >
            {isRescoring ? 'Re-scoring...' : '🔄 Re-score'}
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white border-b border-gray-200 shadow-sm">
      {/* Row 1: Score, Counters, Navigation */}
      <div className="px-6 py-2 flex items-center justify-between bg-gradient-to-r from-gray-50 to-blue-50">
        {/* Left: Score */}
        <div className={`px-4 py-1.5 rounded-full font-bold ${getScoreColor(score)}`}>
          {score}/100
        </div>

        {/* Center: Issue Counters */}
        <div className="flex items-center space-x-3 text-sm">
          {issueCounts.critical > 0 && (
            <span className="px-3 py-1 bg-red-100 text-red-800 rounded-full font-semibold">
              🚨 {issueCounts.critical}
            </span>
          )}
          {issueCounts.warnings > 0 && (
            <span className="px-3 py-1 bg-yellow-100 text-yellow-800 rounded-full font-semibold">
              ⚠️ {issueCounts.warnings}
            </span>
          )}
          {issueCounts.suggestions > 0 && (
            <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full font-semibold">
              💡 {issueCounts.suggestions}
            </span>
          )}
        </div>

        {/* Right: Navigation */}
        <div className="flex items-center space-x-2">
          <span className="text-sm text-gray-600 mr-2">
            {currentIndex + 1} / {suggestions.length}
          </span>
          <button
            onClick={handlePrev}
            className="px-3 py-1 bg-white border border-gray-300 rounded hover:bg-gray-50 transition-colors"
            title="Previous suggestion"
          >
            ←
          </button>
          <button
            onClick={handleNext}
            className="px-3 py-1 bg-white border border-gray-300 rounded hover:bg-gray-50 transition-colors"
            title="Next suggestion"
          >
            →
          </button>
          <button
            onClick={onRescore}
            disabled={isRescoring}
            className="ml-2 px-4 py-1 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors disabled:opacity-50 text-sm"
          >
            {isRescoring ? 'Re-scoring...' : '🔄 Re-score'}
          </button>
        </div>
      </div>

      {/* Row 2: Current Suggestion Detail */}
      <div
        className={`px-6 py-3 border-l-4 ${getSeverityColor(currentSuggestion.severity)} cursor-pointer hover:bg-opacity-80 transition-colors`}
        onClick={() => onSuggestionClick(currentSuggestion.affectedSection)}
      >
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="font-semibold text-sm mb-1">{currentSuggestion.title}</div>
            <div className="text-sm text-gray-700 mb-2">{currentSuggestion.description}</div>

            {currentSuggestion.actionable && (
              <div className="text-xs bg-white bg-opacity-60 rounded p-2 mt-2">
                <div className="font-semibold mb-1">Action Items:</div>
                <ul className="list-disc list-inside space-y-1">
                  {currentSuggestion.actionable.items.map((item, idx) => (
                    <li key={idx}>{item}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
