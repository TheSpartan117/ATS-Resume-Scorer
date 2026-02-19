/**
 * Split-view resume editor with live preview and issue highlighting
 */
import React, { useRef, useEffect, useState } from 'react';
import type { ScoreResult } from '../types/resume';

interface ResumeEditorProps {
  value: string;
  onChange: (html: string) => void;
  currentScore: ScoreResult | null;
  isRescoring: boolean;
  wordCount: number;
  onRescore: () => void;
}

export const ResumeEditor: React.FC<ResumeEditorProps> = ({
  value,
  onChange,
  currentScore,
  isRescoring,
  wordCount,
  onRescore
}) => {
  const editorRef = useRef<HTMLDivElement>(null);
  const [selectedIssue, setSelectedIssue] = useState<string | null>(null);

  // Set editor content whenever value changes
  useEffect(() => {
    if (editorRef.current && value) {
      // Only update if content is different to avoid cursor jumping
      const currentContent = editorRef.current.innerHTML;
      if (currentContent !== value) {
        editorRef.current.innerHTML = value;
      }
    }
  }, [value]);

  const handleInput = () => {
    if (editorRef.current) {
      onChange(editorRef.current.innerHTML);
    }
  };

  const execCommand = (command: string, value?: string) => {
    document.execCommand(command, false, value);
    editorRef.current?.focus();
    handleInput();
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreBgColor = (score: number) => {
    if (score >= 80) return 'bg-green-50 border-green-200';
    if (score >= 60) return 'bg-yellow-50 border-yellow-200';
    return 'bg-red-50 border-red-200';
  };

  const getCategoryColor = (percentage: number) => {
    if (percentage >= 80) return 'from-green-500 to-emerald-500';
    if (percentage >= 60) return 'from-yellow-500 to-amber-500';
    return 'from-red-500 to-rose-500';
  };

  return (
    <div className="flex flex-col lg:flex-row gap-6 min-h-screen">
      {/* LEFT PANEL - Score Dashboard & Issues */}
      <div className="lg:w-2/5 space-y-6">
        {/* Overall Score Card */}
        {currentScore && (
          <div className={`bg-white rounded-xl shadow-lg border-2 ${getScoreBgColor(currentScore.overallScore)} p-6`}>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-gray-900">Overall Score</h2>
              <span className="px-3 py-1 bg-white rounded-full text-sm font-semibold shadow-sm">
                {currentScore.mode === 'ats_simulation' ? '🎯 ATS Mode' : '📝 Coach Mode'}
              </span>
            </div>

            <div className="flex items-center justify-center mb-6">
              <div className="relative">
                <div className="w-40 h-40 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center shadow-xl">
                  <div className="w-36 h-36 rounded-full bg-white flex flex-col items-center justify-center">
                    <span className={`text-5xl font-bold ${getScoreColor(currentScore.overallScore)}`}>
                      {currentScore.overallScore}
                    </span>
                    <span className="text-sm text-gray-500 font-medium">/100</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Category Scores with Bars */}
            <div className="space-y-4">
              <h3 className="text-sm font-bold text-gray-700 uppercase tracking-wide">Category Scores</h3>
              {Object.entries(currentScore.breakdown).map(([category, data]) => {
                const percentage = (data.score / data.maxScore) * 100;
                return (
                  <div key={category} className="space-y-2">
                    <div className="flex justify-between items-center">
                      <span className="text-sm font-medium text-gray-700 capitalize">
                        {category.replace(/_/g, ' ')}
                      </span>
                      <span className="text-sm font-bold text-gray-900">
                        {data.score}/{data.maxScore}
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
                      <div
                        className={`bg-gradient-to-r ${getCategoryColor(percentage)} h-3 rounded-full transition-all duration-500 shadow-sm`}
                        style={{ width: `${percentage}%` }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Strengths */}
            {currentScore.strengths && currentScore.strengths.length > 0 && (
              <div className="mt-6 p-4 bg-green-50 rounded-lg border border-green-200">
                <h4 className="text-sm font-bold text-green-900 mb-2 flex items-center">
                  <span className="mr-2">✨</span>
                  Strengths
                </h4>
                <ul className="space-y-1">
                  {currentScore.strengths.slice(0, 3).map((strength, idx) => (
                    <li key={idx} className="text-xs text-green-800">
                      • {strength}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}

        {/* Issues by Severity */}
        {currentScore && (
          <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center">
              <span className="mr-2">⚠️</span>
              Issues & Recommendations
            </h2>

            {/* Summary Cards */}
            <div className="grid grid-cols-3 gap-3 mb-6">
              <div className="bg-red-50 rounded-lg p-3 border border-red-200">
                <div className="text-2xl font-bold text-red-600">
                  {currentScore.issues.critical.length}
                </div>
                <div className="text-xs font-medium text-red-700">Critical</div>
              </div>
              <div className="bg-yellow-50 rounded-lg p-3 border border-yellow-200">
                <div className="text-2xl font-bold text-yellow-600">
                  {currentScore.issues.warnings.length}
                </div>
                <div className="text-xs font-medium text-yellow-700">Warnings</div>
              </div>
              <div className="bg-blue-50 rounded-lg p-3 border border-blue-200">
                <div className="text-2xl font-bold text-blue-600">
                  {currentScore.issues.suggestions.length}
                </div>
                <div className="text-xs font-medium text-blue-700">Suggestions</div>
              </div>
            </div>

            {/* Critical Issues */}
            {currentScore.issues.critical.length > 0 && (
              <div className="mb-4">
                <h3 className="text-sm font-bold text-red-700 mb-2 flex items-center">
                  <span className="w-2 h-2 bg-red-500 rounded-full mr-2"></span>
                  CRITICAL ISSUES
                </h3>
                <div className="space-y-2">
                  {currentScore.issues.critical.map((issue, idx) => (
                    <div
                      key={idx}
                      onClick={() => setSelectedIssue(issue)}
                      className={`p-3 bg-red-50 border border-red-200 rounded-lg cursor-pointer hover:bg-red-100 transition-colors ${
                        selectedIssue === issue ? 'ring-2 ring-red-400' : ''
                      }`}
                    >
                      <p className="text-xs text-red-800 leading-relaxed">{issue}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Warnings */}
            {currentScore.issues.warnings.length > 0 && (
              <div className="mb-4">
                <h3 className="text-sm font-bold text-yellow-700 mb-2 flex items-center">
                  <span className="w-2 h-2 bg-yellow-500 rounded-full mr-2"></span>
                  WARNINGS
                </h3>
                <div className="space-y-2">
                  {currentScore.issues.warnings.map((issue, idx) => (
                    <div
                      key={idx}
                      onClick={() => setSelectedIssue(issue)}
                      className={`p-3 bg-yellow-50 border border-yellow-200 rounded-lg cursor-pointer hover:bg-yellow-100 transition-colors ${
                        selectedIssue === issue ? 'ring-2 ring-yellow-400' : ''
                      }`}
                    >
                      <p className="text-xs text-yellow-800 leading-relaxed">{issue}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Suggestions */}
            {currentScore.issues.suggestions.length > 0 && (
              <div>
                <h3 className="text-sm font-bold text-blue-700 mb-2 flex items-center">
                  <span className="w-2 h-2 bg-blue-500 rounded-full mr-2"></span>
                  SUGGESTIONS
                </h3>
                <div className="space-y-2">
                  {currentScore.issues.suggestions.slice(0, 5).map((issue, idx) => (
                    <div
                      key={idx}
                      onClick={() => setSelectedIssue(issue)}
                      className={`p-3 bg-blue-50 border border-blue-200 rounded-lg cursor-pointer hover:bg-blue-100 transition-colors ${
                        selectedIssue === issue ? 'ring-2 ring-blue-400' : ''
                      }`}
                    >
                      <p className="text-xs text-blue-800 leading-relaxed">{issue}</p>
                    </div>
                  ))}
                  {currentScore.issues.suggestions.length > 5 && (
                    <p className="text-xs text-gray-500 text-center pt-2">
                      +{currentScore.issues.suggestions.length - 5} more suggestions
                    </p>
                  )}
                </div>
              </div>
            )}

            {/* No issues message */}
            {currentScore.issues.critical.length === 0 &&
              currentScore.issues.warnings.length === 0 &&
              currentScore.issues.suggestions.length === 0 && (
                <div className="text-center py-8">
                  <div className="text-4xl mb-2">🎉</div>
                  <p className="text-green-700 font-medium">No issues found!</p>
                  <p className="text-sm text-gray-600 mt-1">Your resume looks great!</p>
                </div>
              )}
          </div>
        )}
      </div>

      {/* RIGHT PANEL - Editable Resume */}
      <div className="lg:w-3/5 space-y-4">
        <div className="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden">
          {/* Toolbar */}
          <div className="bg-gray-50 border-b border-gray-200 p-3">
            <div className="flex items-center justify-between mb-3">
              <h2 className="text-lg font-bold text-gray-900 flex items-center">
                <span className="mr-2">📄</span>
                Resume Editor
              </h2>
              <div className="flex items-center gap-3">
                <span className="text-sm text-gray-600 font-medium">
                  {wordCount} words
                </span>
                <button
                  onClick={onRescore}
                  disabled={isRescoring}
                  className="px-4 py-2 bg-blue-600 text-white text-sm font-semibold rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed shadow-sm"
                >
                  {isRescoring ? (
                    <span className="flex items-center">
                      <svg className="animate-spin h-4 w-4 mr-2" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                      </svg>
                      Re-scoring...
                    </span>
                  ) : (
                    '🔄 Re-score'
                  )}
                </button>
              </div>
            </div>

            {/* Formatting Toolbar */}
            <div className="flex flex-wrap gap-1 bg-white rounded-lg p-2 border border-gray-200">
              <button
                type="button"
                onClick={() => execCommand('bold')}
                className="px-3 py-1.5 bg-gray-50 border border-gray-300 rounded hover:bg-gray-100 transition-colors"
                title="Bold (Ctrl+B)"
              >
                <strong className="text-sm">B</strong>
              </button>
              <button
                type="button"
                onClick={() => execCommand('italic')}
                className="px-3 py-1.5 bg-gray-50 border border-gray-300 rounded hover:bg-gray-100 transition-colors"
                title="Italic (Ctrl+I)"
              >
                <em className="text-sm">I</em>
              </button>
              <button
                type="button"
                onClick={() => execCommand('underline')}
                className="px-3 py-1.5 bg-gray-50 border border-gray-300 rounded hover:bg-gray-100 transition-colors"
                title="Underline (Ctrl+U)"
              >
                <u className="text-sm">U</u>
              </button>

              <div className="w-px bg-gray-300 mx-1"></div>

              <button
                type="button"
                onClick={() => execCommand('formatBlock', '<h1>')}
                className="px-3 py-1.5 bg-gray-50 border border-gray-300 rounded hover:bg-gray-100 transition-colors text-xs font-semibold"
                title="Heading 1"
              >
                H1
              </button>
              <button
                type="button"
                onClick={() => execCommand('formatBlock', '<h2>')}
                className="px-3 py-1.5 bg-gray-50 border border-gray-300 rounded hover:bg-gray-100 transition-colors text-xs font-semibold"
                title="Heading 2"
              >
                H2
              </button>
              <button
                type="button"
                onClick={() => execCommand('formatBlock', '<p>')}
                className="px-3 py-1.5 bg-gray-50 border border-gray-300 rounded hover:bg-gray-100 transition-colors text-xs font-semibold"
                title="Paragraph"
              >
                P
              </button>

              <div className="w-px bg-gray-300 mx-1"></div>

              <button
                type="button"
                onClick={() => execCommand('insertUnorderedList')}
                className="px-3 py-1.5 bg-gray-50 border border-gray-300 rounded hover:bg-gray-100 transition-colors text-sm"
                title="Bullet List"
              >
                • List
              </button>
              <button
                type="button"
                onClick={() => execCommand('insertOrderedList')}
                className="px-3 py-1.5 bg-gray-50 border border-gray-300 rounded hover:bg-gray-100 transition-colors text-sm"
                title="Numbered List"
              >
                1. List
              </button>

              <div className="w-px bg-gray-300 mx-1"></div>

              <button
                type="button"
                onClick={() => execCommand('justifyLeft')}
                className="px-3 py-1.5 bg-gray-50 border border-gray-300 rounded hover:bg-gray-100 transition-colors"
                title="Align Left"
              >
                ⬅
              </button>
              <button
                type="button"
                onClick={() => execCommand('justifyCenter')}
                className="px-3 py-1.5 bg-gray-50 border border-gray-300 rounded hover:bg-gray-100 transition-colors"
                title="Align Center"
              >
                ↔
              </button>
              <button
                type="button"
                onClick={() => execCommand('removeFormat')}
                className="px-3 py-1.5 bg-gray-50 border border-gray-300 rounded hover:bg-gray-100 transition-colors text-sm"
                title="Clear Formatting"
              >
                ✖
              </button>
            </div>
          </div>

          {/* Editor Content Area */}
          <div className="relative">
            {selectedIssue && (
              <div className="absolute top-0 left-0 right-0 bg-yellow-100 border-b border-yellow-300 p-3 z-10">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <p className="text-sm font-medium text-yellow-900 mb-1">Selected Issue:</p>
                    <p className="text-xs text-yellow-800">{selectedIssue}</p>
                  </div>
                  <button
                    onClick={() => setSelectedIssue(null)}
                    className="text-yellow-600 hover:text-yellow-800 ml-2"
                  >
                    ✕
                  </button>
                </div>
              </div>
            )}

            <div
              ref={editorRef}
              contentEditable
              onInput={handleInput}
              className={`editor-content bg-white p-8 focus:outline-none overflow-auto prose prose-lg max-w-none ${
                selectedIssue ? 'mt-20' : ''
              }`}
              style={{
                fontFamily: 'Georgia, "Times New Roman", serif',
                fontSize: '16px',
                lineHeight: '1.8',
                minHeight: '1000px',
                maxHeight: '1000px',
              }}
              data-placeholder="Loading resume content..."
            />
          </div>
        </div>

        {/* Help Text */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h3 className="text-sm font-bold text-blue-900 mb-2">💡 Editing Tips</h3>
          <ul className="text-xs text-blue-800 space-y-1">
            <li>• Click anywhere in the resume to start editing</li>
            <li>• Use the toolbar to format text (bold, italic, headings, lists)</li>
            <li>• Changes are automatically saved and re-scored after 500ms</li>
            <li>• Click on issues in the left panel to highlight them</li>
            <li>• Keep your resume concise and focused on achievements</li>
          </ul>
        </div>
      </div>
    </div>
  );
};
