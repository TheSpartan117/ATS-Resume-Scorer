import React from 'react';

interface SuggestionLocation {
  section: string;
  line?: number | null;
  para_idx?: number;
}

interface Suggestion {
  id: string;
  type: 'missing_content' | 'content_change' | 'missing_section' | 'formatting';
  severity: 'critical' | 'warning' | 'suggestion' | 'info';
  title: string;
  description: string;
  location: SuggestionLocation;
  action: string;
  example?: string;
  current_text?: string;
  suggested_text?: string;
  state?: 'pending' | 'fixed' | 'dismissed';
}

interface SuggestionCardProps {
  suggestion: Suggestion;
  onAction: (suggestion: Suggestion, action: string) => void;
  onDismiss: (suggestionId: string) => void;
}

const SuggestionCard: React.FC<SuggestionCardProps> = ({
  suggestion,
  onAction,
  onDismiss,
}) => {
  // Severity icons
  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'critical':
        return '❌';
      case 'warning':
        return '⚠️';
      case 'suggestion':
        return '💡';
      case 'info':
        return 'ℹ️';
      default:
        return '📝';
    }
  };

  // Get action button label
  const getActionButtonLabel = (action: string, type: string) => {
    if (action === 'add_phone') return 'Add Phone';
    if (action === 'add_section') {
      // Extract section name from title
      const match = suggestion.title.match(/Missing (\w+) section/i);
      if (match) return `Add ${match[1]} Section`;
      return 'Add Section';
    }
    if (action === 'replace_text') return 'Replace Text';
    if (action === 'show_location') return 'Show Location';
    return 'Apply';
  };

  // Render location info
  const renderLocation = () => {
    const { section, line } = suggestion.location;
    if (line !== null && line !== undefined) {
      return `${section}, Line ${line}`;
    }
    return section;
  };

  // Handle action button click
  const handleActionClick = (action: string) => {
    onAction(suggestion, action);
  };

  const isFixed = suggestion.state === 'fixed';
  const isDismissed = suggestion.state === 'dismissed';

  return (
    <div
      className={`suggestion-card severity-${suggestion.severity} ${
        isFixed ? 'state-fixed' : ''
      } ${isDismissed ? 'state-dismissed' : ''} bg-white border rounded-lg p-4 mb-3 shadow-sm`}
    >
      {/* Header with title and dismiss button */}
      <div className="flex justify-between items-start mb-2">
        <div className="flex-1">
          <h4 className="font-semibold text-gray-800 flex items-center gap-2">
            <span className="text-xl">{getSeverityIcon(suggestion.severity)}</span>
            <span className="uppercase text-xs text-gray-500">
              {suggestion.severity}:
            </span>
            <span>{suggestion.title}</span>
          </h4>
        </div>
        <button
          onClick={() => onDismiss(suggestion.id)}
          className="text-gray-400 hover:text-gray-600 ml-2"
          aria-label="Dismiss suggestion"
          title="Dismiss"
        >
          ✕
        </button>
      </div>

      {/* Location */}
      <div className="flex items-center gap-2 mb-2 text-sm text-gray-600">
        <span>📍</span>
        <span>Location: {renderLocation()}</span>
      </div>

      {/* Description */}
      <div className="flex items-start gap-2 mb-2 text-sm text-gray-700">
        <span>💡</span>
        <span>Why: {suggestion.description}</span>
      </div>

      {/* Example (if provided) */}
      {suggestion.example && (
        <div className="flex items-start gap-2 mb-3 text-sm text-gray-600">
          <span>📝</span>
          <span>Example: {suggestion.example}</span>
        </div>
      )}

      {/* Current and Suggested Text (for content_change type) */}
      {suggestion.type === 'content_change' &&
        suggestion.current_text &&
        suggestion.suggested_text && (
          <div className="mb-3 text-sm">
            <div className="flex items-start gap-2 mb-1">
              <span>❌</span>
              <span className="text-red-600">
                Current: {suggestion.current_text}
              </span>
            </div>
            <div className="flex items-start gap-2">
              <span>✅</span>
              <span className="text-green-600">
                Suggest: {suggestion.suggested_text}
              </span>
            </div>
          </div>
        )}

      {/* Fixed Badge */}
      {isFixed && (
        <div className="mb-3 inline-block px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm font-medium">
          ✅ Fixed
        </div>
      )}

      {/* Action Buttons */}
      {!isFixed && !isDismissed && (
        <div className="flex gap-2 flex-wrap">
          {/* Primary action button */}
          {suggestion.action && (
            <button
              onClick={() => handleActionClick(suggestion.action)}
              className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 text-sm font-medium transition-colors"
              disabled={isFixed}
            >
              {getActionButtonLabel(suggestion.action, suggestion.type)}
            </button>
          )}

          {/* Show Location button for content_change type */}
          {suggestion.type === 'content_change' && (
            <button
              onClick={() => handleActionClick('show_location')}
              className="px-4 py-2 bg-gray-200 text-gray-700 rounded hover:bg-gray-300 text-sm font-medium transition-colors"
              disabled={isFixed}
            >
              Show Location
            </button>
          )}
        </div>
      )}
    </div>
  );
};

export default SuggestionCard;
