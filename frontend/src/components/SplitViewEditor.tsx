import { useState, useCallback, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import SuggestionCarousel from './SuggestionCarousel';
import SectionEditor from './SectionEditor';
import OfficeViewer from './OfficeViewer';
import UserMenu from './UserMenu';
import { updateSection } from '../api/client';
import type { UploadResponse, ScoreResult } from '../types/resume';
import type { DetailedSuggestion } from '../types/suggestion';

export default function SplitViewEditor() {
  const location = useLocation();
  const navigate = useNavigate();
  const result = location.state?.result as UploadResponse | undefined;

  const [sections, setSections] = useState(result?.sections || []);
  const [previewUrl, setPreviewUrl] = useState(result?.previewUrl || '');
  const [currentScore, setCurrentScore] = useState<ScoreResult | null>(result?.score || null);
  const [isUpdating, setIsUpdating] = useState(false);
  const [highlightedSection, setHighlightedSection] = useState<string | undefined>();

  // Redirect if no result
  useEffect(() => {
    if (!result || !result.sessionId) {
      navigate('/');
    }
  }, [result, navigate]);

  // Convert score issues to detailed suggestions
  const suggestions: DetailedSuggestion[] = [];
  if (currentScore) {
    // Critical issues
    currentScore.issues.critical?.forEach((issue, idx) => {
      suggestions.push({
        id: `critical-${idx}`,
        severity: 'critical',
        title: 'Critical Issue',
        description: issue,
        affectedSection: undefined
      });
    });

    // Warnings
    currentScore.issues.warnings?.forEach((issue, idx) => {
      suggestions.push({
        id: `warning-${idx}`,
        severity: 'warning',
        title: 'Warning',
        description: issue,
        affectedSection: undefined
      });
    });

    // Suggestions
    currentScore.issues.suggestions?.forEach((issue, idx) => {
      suggestions.push({
        id: `suggestion-${idx}`,
        severity: 'suggestion',
        title: 'Improvement',
        description: issue,
        affectedSection: undefined
      });
    });
  }

  const handleSectionUpdate = useCallback(async (
    sectionId: string,
    content: string,
    startIdx: number,
    endIdx: number
  ) => {
    if (!result?.sessionId) return;

    setIsUpdating(true);
    try {
      const response = await updateSection({
        session_id: result.sessionId,
        start_para_idx: startIdx,
        end_para_idx: endIdx,
        new_content: content
      });

      if (response.success) {
        setPreviewUrl(response.preview_url);
      }
    } catch (err) {
      console.error('Failed to update section:', err);
    } finally {
      setIsUpdating(false);
    }
  }, [result]);

  const handleRescore = useCallback(() => {
    // TODO: Implement re-scoring logic
    console.log('Re-score triggered');
  }, []);

  const handleSuggestionClick = useCallback((sectionId?: string) => {
    setHighlightedSection(sectionId);

    // Clear highlight after 3 seconds
    if (sectionId) {
      setTimeout(() => setHighlightedSection(undefined), 3000);
    }
  }, []);

  if (!result || !currentScore) {
    return null;
  }

  const issueCounts = {
    critical: currentScore.issues.critical?.length || 0,
    warnings: currentScore.issues.warnings?.length || 0,
    suggestions: currentScore.issues.suggestions?.length || 0
  };

  return (
    <div className="h-screen w-screen flex flex-col overflow-hidden bg-white">
      {/* Top Bar - Compact Header */}
      <div className="flex-none">
        <div className="bg-white border-b border-gray-200 px-4 py-2 flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <button
              onClick={() => navigate('/results', { state: { result } })}
              className="text-blue-600 hover:text-blue-800 font-semibold flex items-center text-sm"
            >
              <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              Back
            </button>
            <span className="text-sm text-gray-600">{result.fileName}</span>
          </div>
          <UserMenu />
        </div>

        {/* Suggestion Carousel */}
        <SuggestionCarousel
          score={currentScore.overallScore}
          suggestions={suggestions}
          issueCounts={issueCounts}
          onRescore={handleRescore}
          onSuggestionClick={handleSuggestionClick}
          isRescoring={false}
        />
      </div>

      {/* Split View: Section Editor + Office Viewer */}
      <div className="flex-1 flex overflow-hidden">
        <SectionEditor
          sections={sections}
          onSectionUpdate={handleSectionUpdate}
          highlightedSection={highlightedSection}
        />
        <OfficeViewer
          previewUrl={previewUrl}
          isUpdating={isUpdating}
        />
      </div>
    </div>
  );
}
