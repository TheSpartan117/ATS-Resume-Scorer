import React, { useState } from 'react';
import SuggestionCard from './SuggestionCard';
import PassProbabilityCard from './PassProbabilityCard';

interface SuggestionLocation {
  section: string;
  line?: number | null;
  para_idx?: number;
  after_section?: string;
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
  template?: string;
  state?: 'pending' | 'fixed' | 'dismissed';
  // Phase 3 additions
  impact_score?: number;
  priority?: 'critical' | 'important' | 'optional';
  action_cta?: string;
}

interface PlatformProbability {
  probability: number;
  status: string;
}

interface PassProbability {
  overall_probability: number;
  platform_breakdown: {
    [platform: string]: PlatformProbability;
  };
  confidence_level: string;
  interpretation: string;
  color_code: string;
  based_on_score: number;
}

interface PrioritizedSuggestions {
  top_issues: Suggestion[];
  remaining_by_priority: {
    critical: Suggestion[];
    important: Suggestion[];
    optional: Suggestion[];
  };
  total_count: number;
}

interface CurrentScore {
  overallScore: number;
  breakdown?: Record<string, number>;
}

interface SuggestionsPanelProps {
  suggestions: Suggestion[];
  currentScore: CurrentScore;
  onSuggestionClick: (suggestion: Suggestion) => void;
  onRescore: () => void;
  lastScored?: Date;
  isRescoring?: boolean;
  // Phase 3 additions
  prioritizedSuggestions?: PrioritizedSuggestions;
  passProbability?: PassProbability;
  mode?: string; // ats_simulation or quality_coach
}

const SuggestionsPanel: React.FC<SuggestionsPanelProps> = ({
  suggestions,
  currentScore,
  onSuggestionClick,
  onRescore,
  lastScored,
  isRescoring = false,
  prioritizedSuggestions,
  passProbability,
  mode = 'quality_coach',
}) => {
  // Group suggestions by severity
  const criticalSuggestions = suggestions.filter(
    (s) => s.severity === 'critical'
  );
  const warningSuggestions = suggestions.filter((s) => s.severity === 'warning');
  const suggestionItems = suggestions.filter(
    (s) => s.severity === 'suggestion'
  );
  const infoSuggestions = suggestions.filter((s) => s.severity === 'info');

  // State for collapsible groups
  const [expandedGroups, setExpandedGroups] = useState<Record<string, boolean>>(
    {
      critical: true,
      warning: true,
      suggestion: false,
      info: false,
      remaining: false,
    }
  );

  const toggleGroup = (group: string) => {
    setExpandedGroups((prev) => ({
      ...prev,
      [group]: !prev[group],
    }));
  };

  // Calculate progress
  const fixedCount = suggestions.filter((s) => s.state === 'fixed').length;
  const totalCount = suggestions.length;
  const progressPercentage =
    totalCount > 0 ? Math.round((fixedCount / totalCount) * 100) : 0;

  // Format last scored time
  const formatLastScored = (date: Date) => {
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);

    if (diffMins < 1) return 'just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours}h ago`;
    const diffDays = Math.floor(diffHours / 24);
    return `${diffDays}d ago`;
  };

  // Get priority label color
  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'critical':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'important':
        return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'optional':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  // Render severity group
  const renderSeverityGroup = (
    title: string,
    groupKey: string,
    items: Suggestion[],
    bgColor: string
  ) => {
    if (items.length === 0) return null;

    const isExpanded = expandedGroups[groupKey];

    return (
      <div className="mb-4">
        <button
          onClick={() => toggleGroup(groupKey)}
          className={`w-full flex items-center justify-between p-3 rounded-lg ${bgColor} hover:opacity-90 transition-opacity`}
        >
          <div className="flex items-center gap-2">
            <span className="font-semibold text-sm uppercase">{title}</span>
            <span className="px-2 py-0.5 bg-white rounded-full text-sm font-medium">
              {items.length}
            </span>
          </div>
          <span className="text-lg">{isExpanded ? '▼' : '▶'}</span>
        </button>

        {isExpanded && (
          <div className="mt-2 space-y-2">
            {items.map((suggestion) => (
              <div
                key={suggestion.id}
                onClick={() => onSuggestionClick(suggestion)}
                className="cursor-pointer"
              >
                <SuggestionCard
                  suggestion={suggestion}
                  onAction={(sug, action) => {
                    // Pass through to parent handler
                    onSuggestionClick(sug);
                  }}
                  onDismiss={(id) => {
                    // Mark as dismissed
                    const dismissedSuggestion = suggestions.find(
                      (s) => s.id === id
                    );
                    if (dismissedSuggestion) {
                      dismissedSuggestion.state = 'dismissed';
                      onSuggestionClick(dismissedSuggestion);
                    }
                  }}
                />
              </div>
            ))}
          </div>
        )}
      </div>
    );
  };

  return (
    <div
      data-testid="suggestions-panel"
      className="suggestions-panel h-full flex flex-col bg-gray-50 border-r overflow-y-auto"
    >
      {/* Score Display */}
      <div className="sticky top-0 bg-white border-b p-4 z-10">
        <div className="text-center mb-3">
          <div className="text-4xl font-bold text-blue-600">
            {currentScore.overallScore}
            <span className="text-2xl text-gray-400">/100</span>
          </div>
          {lastScored && (
            <div className="text-xs text-gray-500 mt-1">
              Last scored: {formatLastScored(lastScored)}
            </div>
          )}
        </div>

        {/* Re-score Button */}
        <button
          onClick={onRescore}
          disabled={isRescoring}
          className="w-full py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
        >
          {isRescoring ? (
            <span className="flex items-center justify-center gap-2">
              <span className="animate-spin">🔄</span>
              Re-scoring...
            </span>
          ) : (
            'Re-score Resume'
          )}
        </button>

        {/* Progress Indicator */}
        {totalCount > 0 && (
          <div className="mt-3">
            <div className="flex justify-between text-sm text-gray-600 mb-1">
              <span>Progress</span>
              <span>
                {fixedCount} of {totalCount} fixed
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-green-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${progressPercentage}%` }}
              />
            </div>
          </div>
        )}
      </div>

      {/* Suggestions Groups */}
      <div className="flex-1 p-4 overflow-y-auto">
        {/* Pass Probability Card (ATS mode only) */}
        {passProbability && mode === 'ats_simulation' && (
          <div className="mb-6">
            <PassProbabilityCard passProbability={passProbability} />
          </div>
        )}

        {totalCount === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <div className="text-4xl mb-2">🎉</div>
            <p className="font-medium">No suggestions</p>
            <p className="text-sm mt-1">Your resume looks great!</p>
          </div>
        ) : prioritizedSuggestions && prioritizedSuggestions.top_issues.length > 0 ? (
          <>
            {/* Top 3 Issues - Prominently Displayed */}
            <div className="mb-6">
              <div className="flex items-center gap-2 mb-3">
                <h3 className="text-lg font-bold text-gray-900">
                  Top {prioritizedSuggestions.top_issues.length} Critical Issues
                </h3>
                <span className="px-2 py-1 bg-red-100 text-red-800 rounded-full text-xs font-bold">
                  FIX THESE FIRST
                </span>
              </div>

              <div className="space-y-3">
                {prioritizedSuggestions.top_issues.map((suggestion, index) => (
                  <div
                    key={suggestion.id}
                    className="relative border-2 border-red-300 rounded-lg bg-white shadow-sm hover:shadow-md transition-shadow"
                  >
                    {/* Priority Badge */}
                    <div className="absolute -top-2 -right-2">
                      <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-bold border ${getPriorityColor(suggestion.priority || 'important')}`}>
                        #{index + 1} {suggestion.priority?.toUpperCase()}
                      </span>
                    </div>

                    <div
                      onClick={() => onSuggestionClick(suggestion)}
                      className="cursor-pointer p-4"
                    >
                      <div className="flex items-start gap-3">
                        <div className="flex-shrink-0 text-2xl">
                          {suggestion.severity === 'critical' ? '❌' : '⚠️'}
                        </div>
                        <div className="flex-1 min-w-0">
                          <h4 className="font-semibold text-gray-900 mb-1">
                            {suggestion.title}
                          </h4>
                          <p className="text-sm text-gray-600 mb-2">
                            {suggestion.description}
                          </p>
                          {suggestion.action_cta && (
                            <button className="px-3 py-1.5 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors">
                              {suggestion.action_cta} →
                            </button>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Remaining Suggestions - Collapsible */}
            {prioritizedSuggestions.total_count > prioritizedSuggestions.top_issues.length && (
              <div className="mb-4">
                <button
                  onClick={() => setExpandedGroups(prev => ({
                    ...prev,
                    remaining: !prev.remaining
                  }))}
                  className="w-full flex items-center justify-between p-3 rounded-lg bg-gray-100 hover:bg-gray-200 transition-colors"
                >
                  <span className="font-medium text-gray-900">
                    See {prioritizedSuggestions.total_count - prioritizedSuggestions.top_issues.length} more suggestions
                  </span>
                  <span className="text-gray-600">
                    {expandedGroups.remaining ? '▼' : '▶'}
                  </span>
                </button>

                {expandedGroups.remaining && (
                  <div className="mt-4 space-y-4">
                    {/* Render remaining by priority */}
                    {Object.entries(prioritizedSuggestions.remaining_by_priority).map(([priority, items]) => {
                      if (items.length === 0) return null;

                      return (
                        <div key={priority} className="space-y-2">
                          <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-bold border ${getPriorityColor(priority)}`}>
                            {priority.toUpperCase()} ({items.length})
                          </div>
                          <div className="space-y-2">
                            {items.map((suggestion) => (
                              <div
                                key={suggestion.id}
                                onClick={() => onSuggestionClick(suggestion)}
                                className="cursor-pointer"
                              >
                                <SuggestionCard
                                  suggestion={suggestion}
                                  onAction={(sug, action) => {
                                    onSuggestionClick(sug);
                                  }}
                                  onDismiss={(id) => {
                                    const dismissedSuggestion = suggestions.find(
                                      (s) => s.id === id
                                    );
                                    if (dismissedSuggestion) {
                                      dismissedSuggestion.state = 'dismissed';
                                      onSuggestionClick(dismissedSuggestion);
                                    }
                                  }}
                                />
                              </div>
                            ))}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            )}
          </>
        ) : (
          <>
            {/* Fallback to old display if no prioritized suggestions */}
            {renderSeverityGroup(
              'CRITICAL',
              'critical',
              criticalSuggestions,
              'bg-red-100 text-red-800'
            )}
            {renderSeverityGroup(
              'WARNINGS',
              'warning',
              warningSuggestions,
              'bg-yellow-100 text-yellow-800'
            )}
            {renderSeverityGroup(
              'SUGGESTIONS',
              'suggestion',
              suggestionItems,
              'bg-blue-100 text-blue-800'
            )}
            {renderSeverityGroup(
              'INFO',
              'info',
              infoSuggestions,
              'bg-gray-100 text-gray-800'
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default SuggestionsPanel;
