/**
 * Simple Resume Editor with 70/30 split (no external dependencies)
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

export const ResumeEditorSimple: React.FC<ResumeEditorProps> = ({
  value,
  onChange,
  currentScore,
  isRescoring,
  wordCount,
  onRescore
}) => {
  const editorRef = useRef<HTMLDivElement>(null);
  const [selectedIssue, setSelectedIssue] = useState<string | null>(null);
  const isInitializedRef = useRef(false);

  // Initialize editor content once
  useEffect(() => {
    if (editorRef.current && value && !isInitializedRef.current) {
      editorRef.current.innerHTML = value;
      isInitializedRef.current = true;
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

  const getCategoryColor = (percentage: number) => {
    if (percentage >= 80) return 'from-green-500 to-emerald-500';
    if (percentage >= 60) return 'from-yellow-500 to-amber-500';
    return 'from-red-500 to-rose-500';
  };

  return (
    <div className="flex h-full w-full overflow-hidden">
      {/* LEFT PANEL - 70% - Resume Editor */}
      <div className="w-[70%] flex flex-col border-r border-gray-300 bg-white">
        {/* Editor Header */}
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-6 py-3 flex items-center justify-between flex-none">
          <div>
            <h2 className="text-lg font-bold">Resume Editor</h2>
            <p className="text-xs text-blue-100">Edit your resume with formatting preserved</p>
          </div>
          <div className="text-right">
            <div className="text-xl font-bold">{wordCount}</div>
            <div className="text-xs text-blue-100">words</div>
          </div>
        </div>

        {/* Toolbar */}
        <div className="bg-gray-50 border-b border-gray-200 p-2 flex flex-wrap gap-2 flex-none">
          <button onClick={() => execCommand('bold')} className="px-3 py-1.5 bg-white border border-gray-300 rounded hover:bg-gray-100 font-bold text-sm" title="Bold">B</button>
          <button onClick={() => execCommand('italic')} className="px-3 py-1.5 bg-white border border-gray-300 rounded hover:bg-gray-100 italic text-sm" title="Italic">I</button>
          <button onClick={() => execCommand('underline')} className="px-3 py-1.5 bg-white border border-gray-300 rounded hover:bg-gray-100 underline text-sm" title="Underline">U</button>
          <div className="w-px bg-gray-300" />
          <button onClick={() => execCommand('formatBlock', '<h1>')} className="px-3 py-1.5 bg-white border border-gray-300 rounded hover:bg-gray-100 text-sm" title="Heading 1">H1</button>
          <button onClick={() => execCommand('formatBlock', '<h2>')} className="px-3 py-1.5 bg-white border border-gray-300 rounded hover:bg-gray-100 text-sm" title="Heading 2">H2</button>
          <button onClick={() => execCommand('formatBlock', '<h3>')} className="px-3 py-1.5 bg-white border border-gray-300 rounded hover:bg-gray-100 text-sm" title="Heading 3">H3</button>
          <button onClick={() => execCommand('formatBlock', '<p>')} className="px-3 py-1.5 bg-white border border-gray-300 rounded hover:bg-gray-100 text-sm" title="Paragraph">P</button>
          <div className="w-px bg-gray-300" />
          <button onClick={() => execCommand('insertUnorderedList')} className="px-3 py-1.5 bg-white border border-gray-300 rounded hover:bg-gray-100 text-sm" title="Bullet List">• List</button>
          <button onClick={() => execCommand('insertOrderedList')} className="px-3 py-1.5 bg-white border border-gray-300 rounded hover:bg-gray-100 text-sm" title="Numbered List">1. List</button>
          <div className="w-px bg-gray-300" />
          <button onClick={() => execCommand('justifyLeft')} className="px-3 py-1.5 bg-white border border-gray-300 rounded hover:bg-gray-100 text-sm" title="Align Left">⟵</button>
          <button onClick={() => execCommand('justifyCenter')} className="px-3 py-1.5 bg-white border border-gray-300 rounded hover:bg-gray-100 text-sm" title="Align Center">⟷</button>
          <button onClick={() => execCommand('justifyRight')} className="px-3 py-1.5 bg-white border border-gray-300 rounded hover:bg-gray-100 text-sm" title="Align Right">⟶</button>
        </div>

        {/* Editor Content Area */}
        <div className="flex-1 overflow-auto p-8 bg-white">
          <style>{`
            .resume-content {
              max-width: 850px;
              margin: 0 auto;
              font-family: 'Calibri', 'Arial', sans-serif;
              font-size: 11pt;
              line-height: 1.4;
              color: #000;
            }
            .resume-content h1 {
              font-size: 24pt;
              font-weight: bold;
              color: #008080;
              margin: 0 0 8px 0;
              letter-spacing: 0.5px;
            }
            .resume-content h2 {
              font-size: 13pt;
              font-weight: bold;
              color: #1f4788;
              margin: 16px 0 8px 0;
              text-transform: uppercase;
              border-bottom: 2px solid #1f4788;
              padding-bottom: 2px;
              letter-spacing: 0.5px;
            }
            .resume-content h3 {
              font-size: 11pt;
              font-weight: bold;
              margin: 8px 0 4px 0;
              color: #000;
            }
            .resume-content p {
              margin: 4px 0;
              line-height: 1.4;
            }
            .resume-content strong {
              font-weight: bold;
            }
            .resume-content ul, .resume-content ol {
              margin: 4px 0;
              padding-left: 25px;
            }
            .resume-content li {
              margin: 3px 0;
              line-height: 1.4;
            }
            .resume-content a {
              color: #0563c1;
              text-decoration: none;
            }
            .resume-content a:hover {
              text-decoration: underline;
            }
            /* Table styling for two-column layouts */
            .resume-content table {
              width: 100%;
              border-collapse: collapse;
              margin: 0;
            }
            .resume-content table td {
              padding: 12px;
              vertical-align: top;
            }
            /* Preserve background colors from DOCX */
            .resume-content [style*="background-color"] {
              padding: 12px;
            }
            /* Images (photos) */
            .resume-content img {
              max-width: 150px;
              border-radius: 50%;
              display: block;
              margin: 10px auto;
            }
            /* Colored spans */
            .resume-content span[style*="color"] {
              /* Preserve inline colors */
            }
            /* Contact info */
            .resume-content h1 + p {
              font-size: 10pt;
              margin-bottom: 12px;
              color: #333;
            }
          `}</style>
          <div
            ref={editorRef}
            contentEditable
            onInput={handleInput}
            className="resume-content min-h-full focus:outline-none"
            suppressContentEditableWarning
          >
            {!value && <p className="text-gray-400">Loading resume content...</p>}
          </div>
        </div>
      </div>

      {/* RIGHT PANEL - 30% - Scores & Suggestions */}
      <div className="w-[30%] flex flex-col bg-gray-50 overflow-y-auto">
        {currentScore && (
          <>
            {/* Score Summary */}
            <div className="p-6 border-b-4 border-blue-300 bg-gradient-to-br from-blue-50 to-purple-50 flex-none">
              <div className="flex items-center justify-between mb-4">
                <span className="text-xs font-semibold text-gray-600">
                  {currentScore.mode === 'ats_simulation' ? '🎯 ATS Mode' : '📝 Coach Mode'}
                </span>
                {isRescoring && (
                  <span className="text-xs text-blue-600 animate-pulse">Updating...</span>
                )}
              </div>

              {/* Big Score Circle */}
              <div className="flex items-center justify-center mb-4">
                <div className="relative">
                  <svg className="w-28 h-28" viewBox="0 0 120 120">
                    <circle
                      cx="60"
                      cy="60"
                      r="54"
                      fill="none"
                      stroke="#e5e7eb"
                      strokeWidth="8"
                    />
                    <circle
                      cx="60"
                      cy="60"
                      r="54"
                      fill="none"
                      stroke={currentScore.overallScore >= 80 ? '#10b981' : currentScore.overallScore >= 60 ? '#f59e0b' : '#ef4444'}
                      strokeWidth="8"
                      strokeDasharray={`${(currentScore.overallScore / 100) * 339.292} 339.292`}
                      transform="rotate(-90 60 60)"
                      strokeLinecap="round"
                    />
                  </svg>
                  <div className="absolute inset-0 flex flex-col items-center justify-center">
                    <span className={`text-3xl font-bold ${getScoreColor(currentScore.overallScore)}`}>
                      {currentScore.overallScore}
                    </span>
                    <span className="text-xs text-gray-500">/100</span>
                  </div>
                </div>
              </div>

              {/* Category Mini Bars */}
              <div className="space-y-2">
                {Object.entries(currentScore.breakdown).map(([category, data]) => {
                  const percentage = (data.score / data.maxScore) * 100;
                  return (
                    <div key={category}>
                      <div className="flex justify-between items-center text-xs mb-1">
                        <span className="font-medium text-gray-700 capitalize">
                          {category.replace(/_/g, ' ')}
                        </span>
                        <span className="font-bold text-gray-900">
                          {data.score}/{data.maxScore}
                        </span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                          className={`h-full bg-gradient-to-r ${getCategoryColor(percentage)} rounded-full transition-all duration-500`}
                          style={{ width: `${percentage}%` }}
                        />
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Issues & Suggestions */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {/* Critical Issues */}
              {currentScore.issues.critical && currentScore.issues.critical.length > 0 && (
                <div>
                  <div className="flex items-center mb-2">
                    <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-red-100 text-red-800">
                      🚨 Critical ({currentScore.issues.critical.length})
                    </span>
                  </div>
                  <div className="space-y-2">
                    {currentScore.issues.critical.map((issue, idx) => (
                      <div
                        key={idx}
                        className="text-xs p-3 rounded-lg border-l-4 border-red-500 bg-red-50 shadow-sm hover:bg-red-100 cursor-pointer transition-colors"
                        onClick={() => setSelectedIssue(issue)}
                      >
                        {issue}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Warnings */}
              {currentScore.issues.warnings && currentScore.issues.warnings.length > 0 && (
                <div>
                  <div className="flex items-center mb-2">
                    <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-yellow-100 text-yellow-800">
                      ⚠️ Warnings ({currentScore.issues.warnings.length})
                    </span>
                  </div>
                  <div className="space-y-2">
                    {currentScore.issues.warnings.map((issue, idx) => (
                      <div
                        key={idx}
                        className="text-xs p-3 rounded-lg border-l-4 border-yellow-500 bg-yellow-50 shadow-sm hover:bg-yellow-100 cursor-pointer transition-colors"
                        onClick={() => setSelectedIssue(issue)}
                      >
                        {issue}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Suggestions */}
              {currentScore.issues.suggestions && currentScore.issues.suggestions.length > 0 && (
                <div>
                  <div className="flex items-center mb-2">
                    <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-blue-100 text-blue-800">
                      💡 Suggestions ({currentScore.issues.suggestions.length})
                    </span>
                  </div>
                  <div className="space-y-2">
                    {currentScore.issues.suggestions.map((issue, idx) => (
                      <div
                        key={idx}
                        className="text-xs p-3 rounded-lg border-l-4 border-blue-500 bg-blue-50 shadow-sm hover:bg-blue-100 cursor-pointer transition-colors"
                        onClick={() => setSelectedIssue(issue)}
                      >
                        {issue}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Keyword Details */}
              {currentScore.keywordDetails && (
                <div>
                  <div className="flex items-center mb-2">
                    <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-purple-100 text-purple-800">
                      🔑 Keywords
                    </span>
                  </div>
                  <div className="bg-white rounded-lg p-3 shadow-sm border border-purple-200 text-xs">
                    {currentScore.keywordDetails.required_matched !== undefined && (
                      <div className="mb-2">
                        <div className="font-semibold text-gray-700 mb-1">Required Keywords:</div>
                        <div className="flex items-center justify-between">
                          <span className="text-gray-600">Matched:</span>
                          <span className="font-bold text-green-600">
                            {currentScore.keywordDetails.required_matched}/{currentScore.keywordDetails.required_total}
                          </span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2 mt-1">
                          <div
                            className="h-full bg-gradient-to-r from-green-500 to-emerald-500 rounded-full"
                            style={{ width: `${currentScore.keywordDetails.required_match_pct || 0}%` }}
                          />
                        </div>
                      </div>
                    )}
                    {currentScore.keywordDetails.preferred_matched !== undefined && (
                      <div>
                        <div className="font-semibold text-gray-700 mb-1">Preferred Keywords:</div>
                        <div className="flex items-center justify-between">
                          <span className="text-gray-600">Matched:</span>
                          <span className="font-bold text-blue-600">
                            {currentScore.keywordDetails.preferred_matched}/{currentScore.keywordDetails.preferred_total}
                          </span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2 mt-1">
                          <div
                            className="h-full bg-gradient-to-r from-blue-500 to-indigo-500 rounded-full"
                            style={{ width: `${currentScore.keywordDetails.preferred_match_pct || 0}%` }}
                          />
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Strengths */}
              {currentScore.strengths && currentScore.strengths.length > 0 && (
                <div>
                  <div className="flex items-center mb-2">
                    <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-green-100 text-green-800">
                      ✅ Strengths ({currentScore.strengths.length})
                    </span>
                  </div>
                  <div className="space-y-2">
                    {currentScore.strengths.map((strength, idx) => (
                      <div
                        key={idx}
                        className="text-xs p-3 rounded-lg border-l-4 border-green-500 bg-green-50 shadow-sm"
                      >
                        {strength}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  );
};
