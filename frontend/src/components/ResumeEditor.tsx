/**
 * Enhanced ResumeEditor with Word Viewer and IssuesList
 */
import React, { useRef, useCallback } from 'react';
import type { ScoreResult } from '../types/resume';
import IssuesList, { type AppliedSuggestion } from './IssuesList';
import ResumeViewerTabs from './ResumeViewerTabs';

interface ResumeEditorProps {
  value: string;
  onChange: (html: string) => void;
  currentScore: ScoreResult | null;
  isRescoring: boolean;
  wordCount: number;
  onRescore: () => void;
  originalDocxFile?: File | null;
}

export const ResumeEditor: React.FC<ResumeEditorProps> = ({
  value,
  onChange,
  currentScore,
  isRescoring: _isRescoring,
  wordCount: _wordCount,
  onRescore: _onRescore,
  originalDocxFile
}) => {
  const editorRef = useRef<any>(null);

  // Store editor instance when ready
  const handleEditorReady = useCallback((editor: any) => {
    editorRef.current = editor;
    if (import.meta.env.DEV) {
      console.log('Editor ready');
    }
  }, []);

  // Handle applying suggestions from IssuesList
  const handleApplySuggestion = useCallback((suggestion: AppliedSuggestion) => {
    const editor = editorRef.current;
    if (!editor) {
      console.warn('Editor not ready yet');
      return;
    }

    try {
      if (suggestion.action === 'insert' && suggestion.content) {
        // Insert template content at the end of the document
        editor.chain().focus().setContent(
          editor.getHTML() + suggestion.content
        ).run();

        if (import.meta.env.DEV) {
          console.log('Applied suggestion:', suggestion.description);
        }
      } else if (suggestion.action === 'replace' && suggestion.searchText && suggestion.replaceText) {
        // Replace text content
        const currentHtml = editor.getHTML();
        const newHtml = currentHtml.replace(suggestion.searchText, suggestion.replaceText);

        if (newHtml !== currentHtml) {
          editor.chain().focus().setContent(newHtml).run();
          if (import.meta.env.DEV) {
            console.log('Replaced text:', suggestion.searchText, '->', suggestion.replaceText);
          }
        }
      } else if (suggestion.action === 'format') {
        // Apply formatting improvements (simplified for now)
        if (import.meta.env.DEV) {
          console.log('Formatting applied:', suggestion.description);
        }
      }
    } catch (error) {
      if (import.meta.env.DEV) {
        console.error('Error applying suggestion:', error);
      }
    }
  }, []);

  return (
    <div className="flex flex-col lg:flex-row gap-4 min-h-screen w-full">
      {/* LEFT PANEL - Resume Viewer with Tabs (70%) */}
      <div className="lg:w-[70%] w-full">
        <ResumeViewerTabs
          originalDocx={originalDocxFile}
          htmlContent={value}
          onHtmlChange={onChange}
          onEditorReady={handleEditorReady}
        />
      </div>

      {/* RIGHT PANEL - Enhanced Suggestions Panel (30%) */}
      <div className="lg:w-[30%] w-full flex flex-col bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden">
        {/* Mode Indicator */}
        {currentScore && (
          <div className="bg-gradient-to-r from-blue-600 to-indigo-600 px-4 py-2">
            <div className="flex items-center justify-between">
              <span className="text-white text-sm font-semibold">
                {currentScore.mode === 'ats_simulation' ? '🎯 ATS Mode' : '📝 Coach Mode'}
              </span>
              <span className="text-white text-xs opacity-90">Smart Suggestions</span>
            </div>
          </div>
        )}

        {/* Enhanced IssuesList with Tabs and Apply Actions */}
        <div className="flex-1 overflow-hidden p-4">
          {currentScore && (
            <IssuesList
              issues={currentScore.issues}
              overallScore={currentScore.overallScore}
              enhancedSuggestions={currentScore.enhancedSuggestions}
              onApplySuggestion={handleApplySuggestion}
            />
          )}
        </div>
      </div>
    </div>
  );
};
