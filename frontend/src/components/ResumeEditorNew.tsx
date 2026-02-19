/**
 * Redesigned Resume Editor with 70/30 split and Quill editor
 */
import React, { useRef, useEffect, useState } from 'react';
import ReactQuill from 'react-quill';
import 'react-quill/dist/quill.snow.css';
import type { ScoreResult } from '../types/resume';

interface ResumeEditorProps {
  value: string;
  onChange: (html: string) => void;
  currentScore: ScoreResult | null;
  isRescoring: boolean;
  wordCount: number;
  onRescore: () => void;
}

// Quill toolbar configuration
const modules = {
  toolbar: [
    [{ 'header': [1, 2, 3, false] }],
    ['bold', 'italic', 'underline', 'strike'],
    [{ 'list': 'ordered'}, { 'list': 'bullet' }],
    [{ 'align': [] }],
    [{ 'color': [] }, { 'background': [] }],
    [{ 'font': [] }],
    [{ 'size': ['small', false, 'large', 'huge'] }],
    ['link'],
    ['clean']
  ]
};

const formats = [
  'header',
  'bold', 'italic', 'underline', 'strike',
  'list', 'bullet',
  'align',
  'color', 'background',
  'font', 'size',
  'link'
];

export const ResumeEditorNew: React.FC<ResumeEditorProps> = ({
  value,
  onChange,
  currentScore,
  isRescoring,
  wordCount,
  onRescore
}) => {
  const [editorContent, setEditorContent] = useState<string>(value || '');

  useEffect(() => {
    if (value) {
      setEditorContent(value);
    }
  }, [value]);

  const handleChange = (content: string) => {
    setEditorContent(content);
    onChange(content);
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

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'border-red-500 bg-red-50';
      case 'warning': return 'border-yellow-500 bg-yellow-50';
      case 'suggestion': return 'border-blue-500 bg-blue-50';
      case 'info': return 'border-gray-500 bg-gray-50';
      default: return 'border-gray-500 bg-gray-50';
    }
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'critical': return '🚨';
      case 'warning': return '⚠️';
      case 'suggestion': return '💡';
      case 'info': return 'ℹ️';
      default: return '•';
    }
  };

  return (
    <div className="flex h-screen w-full overflow-hidden">
      {/* LEFT PANEL - 70% - Resume Editor */}
      <div className="w-[70%] flex flex-col border-r border-gray-300">
        {/* Editor Header */}
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-6 py-4 flex items-center justify-between">
          <div>
            <h2 className="text-xl font-bold">Resume Editor</h2>
            <p className="text-sm text-blue-100">Edit your resume with formatting preserved</p>
          </div>
          <div className="text-right">
            <div className="text-2xl font-bold">{wordCount}</div>
            <div className="text-xs text-blue-100">words</div>
          </div>
        </div>

        {/* Quill Editor */}
        <div className="flex-1 overflow-hidden flex flex-col bg-white">
          <ReactQuill
            theme="snow"
            value={editorContent}
            onChange={handleChange}
            modules={modules}
            formats={formats}
            className="h-full flex flex-col"
            style={{ height: '100%' }}
          />
        </div>
      </div>

      {/* RIGHT PANEL - 30% - Scores & Suggestions */}
      <div className="w-[30%] flex flex-col bg-gray-50 overflow-y-auto">
        {currentScore && (
          <>
            {/* Score Summary */}
            <div className={`p-6 border-b-4 ${getScoreBgColor(currentScore.overallScore).replace('bg-', 'border-')}`}>
              <div className="flex items-center justify-between mb-4">
                <span className="text-sm font-semibold text-gray-600">
                  {currentScore.mode === 'ats_simulation' ? '🎯 ATS Mode' : '📝 Coach Mode'}
                </span>
                {isRescoring && (
                  <span className="text-xs text-blue-600 animate-pulse">Updating...</span>
                )}
              </div>

              {/* Big Score Circle */}
              <div className="flex items-center justify-center mb-4">
                <div className="relative">
                  <svg className="w-32 h-32" viewBox="0 0 120 120">
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
                    <span className={`text-4xl font-bold ${getScoreColor(currentScore.overallScore)}`}>
                      {currentScore.overallScore}
                    </span>
                    <span className="text-sm text-gray-500">/100</span>
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
                        className="text-xs p-3 rounded-lg border-l-4 border-red-500 bg-red-50 shadow-sm"
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
                        className="text-xs p-3 rounded-lg border-l-4 border-yellow-500 bg-yellow-50 shadow-sm"
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
                        className="text-xs p-3 rounded-lg border-l-4 border-blue-500 bg-blue-50 shadow-sm"
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
