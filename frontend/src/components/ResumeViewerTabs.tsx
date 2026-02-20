/**
 * ResumeViewerTabs Component - Tabbed Interface for Resume Viewing/Editing
 *
 * Provides three viewing modes:
 * 1. Original Document - High-fidelity DOCX preview using docx-preview
 * 2. Edit Mode - TipTap rich text editor for making changes
 * 3. Office Online - 100% accurate fallback (if public URL available)
 *
 * Usage:
 *   <ResumeViewerTabs
 *     originalDocx={docxFile}
 *     htmlContent={html}
 *     onHtmlChange={handleChange}
 *     previewUrl={publicUrl}
 *   />
 */

import { useState, useEffect } from 'react';
import DocxViewer from './DocxViewer';
import TiptapEditor from './TiptapEditor';
import OfficeViewer from './OfficeViewer';
import OnlyOfficeEditor from './OnlyOfficeEditor';

interface ResumeViewerTabsProps {
  originalDocx: File | Blob | null;
  htmlContent: string;
  onHtmlChange: (html: string) => void;
  previewUrl?: string; // Public URL for Office Online fallback
  onEditorReady?: (editor: any) => void;
  className?: string;
  sessionId?: string; // Session ID for OnlyOffice
}

type TabId = 'onlyoffice' | 'original' | 'edit' | 'office';

interface Tab {
  id: TabId;
  label: string;
  icon: string;
  description: string;
  badge?: string;
}

export const ResumeViewerTabs: React.FC<ResumeViewerTabsProps> = ({
  originalDocx,
  htmlContent,
  onHtmlChange,
  previewUrl,
  onEditorReady,
  className = '',
  sessionId,
}) => {
  const [activeTab, setActiveTab] = useState<TabId>('onlyoffice');
  const [docxViewerError, setDocxViewerError] = useState(false);
  const [showOfficeTab, setShowOfficeTab] = useState(false);
  const [onlyOfficeEnabled, setOnlyOfficeEnabled] = useState(true);

  // Show Office Online tab if docx-preview fails and public URL available
  useEffect(() => {
    if (docxViewerError && previewUrl) {
      setShowOfficeTab(true);
      // Auto-switch to Office Online on error
      setActiveTab('office');
    }
  }, [docxViewerError, previewUrl]);

  // Define available tabs
  const baseTabs: Tab[] = [
    ...(onlyOfficeEnabled && sessionId ? [{
      id: 'onlyoffice' as TabId,
      label: 'OnlyOffice Editor',
      icon: '📝',
      description: '100% Word-like editing with zero format discrepancy - powered by OnlyOffice',
      badge: '100% Accurate',
    }] : []),
    {
      id: 'original',
      label: 'Preview',
      icon: '📄',
      description: 'View your document exactly as uploaded with preserved formatting',
      badge: '85-95% Accurate',
    },
    {
      id: 'edit',
      label: 'Structure Editor',
      icon: '✏️',
      description: 'Make changes to your resume content with rich text editing',
    },
  ];

  // Add Office Online tab conditionally
  const tabs: Tab[] = showOfficeTab
    ? [
        ...baseTabs,
        {
          id: 'office',
          label: 'Office Online',
          icon: '🌐',
          description: '100% accurate Microsoft Word Online viewer (requires internet)',
          badge: '100% Accurate',
        },
      ]
    : baseTabs;

  const handleTabChange = (tabId: TabId) => {
    setActiveTab(tabId);
  };

  const handleDocxViewerError = (error: string) => {
    console.warn('DocxViewer error:', error);
    setDocxViewerError(true);
  };

  const handleDocxViewerSuccess = () => {
    setDocxViewerError(false);
  };

  return (
    <div className={`flex flex-col h-full bg-white rounded-lg shadow-lg overflow-hidden ${className}`}>
      {/* Tab Navigation Header */}
      <div className="bg-gradient-to-r from-gray-50 to-white border-b border-gray-200">
        <div className="flex items-center space-x-1 px-4 pt-3">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => handleTabChange(tab.id)}
              className={`
                relative px-6 py-3 font-medium text-sm rounded-t-lg transition-all
                ${
                  activeTab === tab.id
                    ? 'bg-white text-blue-600 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                }
              `}
            >
              <div className="flex items-center space-x-2">
                <span className="text-lg">{tab.icon}</span>
                <span>{tab.label}</span>
                {tab.badge && activeTab === tab.id && (
                  <span className="ml-2 px-2 py-0.5 text-xs bg-blue-100 text-blue-700 rounded-full">
                    {tab.badge}
                  </span>
                )}
              </div>

              {/* Active tab indicator */}
              {activeTab === tab.id && (
                <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-blue-600"></div>
              )}
            </button>
          ))}
        </div>
      </div>

      {/* Tab Description Bar */}
      <div className="bg-blue-50 border-b border-blue-100 px-6 py-3">
        <div className="flex items-center justify-between">
          <p className="text-sm text-blue-800">
            {tabs.find((t) => t.id === activeTab)?.description}
          </p>

          {/* Additional controls */}
          {activeTab === 'original' && docxViewerError && previewUrl && (
            <button
              onClick={() => setActiveTab('office')}
              className="text-sm text-blue-700 hover:text-blue-900 font-medium underline"
            >
              Try 100% accurate viewer →
            </button>
          )}
        </div>
      </div>

      {/* Tab Content Area */}
      <div className="flex-1 overflow-hidden relative">
        {/* OnlyOffice Editor Tab */}
        {activeTab === 'onlyoffice' && sessionId && (
          <div className="h-full">
            <OnlyOfficeEditor
              sessionId={sessionId}
              onDocumentReady={() => console.log('OnlyOffice document ready')}
              onError={(error) => {
                console.error('OnlyOffice error:', error);
                setOnlyOfficeEnabled(false);
                setActiveTab('original');
              }}
              className="h-full"
            />
          </div>
        )}

        {/* Original Document Tab */}
        {activeTab === 'original' && (
          <div className="h-full">
            <DocxViewer
              docxFile={originalDocx}
              className="h-full"
              onError={handleDocxViewerError}
              onSuccess={handleDocxViewerSuccess}
            />
          </div>
        )}

        {/* Edit Mode Tab */}
        {activeTab === 'edit' && (
          <div className="h-full overflow-auto">
            <TiptapEditor
              content={htmlContent}
              onChange={onHtmlChange}
              onReady={onEditorReady}
            />
          </div>
        )}

        {/* Office Online Tab */}
        {activeTab === 'office' && previewUrl && (
          <div className="h-full">
            <OfficeViewer previewUrl={previewUrl} />
          </div>
        )}

        {/* Fallback - No document */}
        {!originalDocx && activeTab === 'original' && (
          <div className="h-full flex items-center justify-center bg-gray-50">
            <div className="text-center text-gray-500">
              <svg
                className="w-20 h-20 mx-auto mb-4 text-gray-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={1.5}
                  d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                />
              </svg>
              <p className="text-lg font-medium mb-2">No document loaded</p>
              <p className="text-sm">Upload a resume to view and edit</p>
            </div>
          </div>
        )}
      </div>

      {/* Footer Status Bar */}
      <div className="bg-gray-50 border-t border-gray-200 px-6 py-2.5">
        <div className="flex items-center justify-between text-xs">
          {/* Left side - viewer info */}
          <div className="flex items-center space-x-4 text-gray-600">
            {activeTab === 'onlyoffice' && (
              <span className="flex items-center">
                <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                OnlyOffice Document Server - 100% Word Compatible
              </span>
            )}

            {activeTab === 'original' && (
              <>
                <span className="flex items-center">
                  <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                  Powered by docx-preview
                </span>
                {docxViewerError && (
                  <span className="text-yellow-700 font-medium">
                    ⚠️ Rendering issue detected
                  </span>
                )}
              </>
            )}

            {activeTab === 'edit' && (
              <span className="flex items-center">
                <span className="w-2 h-2 bg-blue-500 rounded-full mr-2"></span>
                Rich text editor active
              </span>
            )}

            {activeTab === 'office' && (
              <span className="flex items-center">
                <span className="w-2 h-2 bg-purple-500 rounded-full mr-2"></span>
                Microsoft Office Online
              </span>
            )}
          </div>

          {/* Right side - actions */}
          <div className="flex items-center space-x-3">
            {activeTab === 'original' && showOfficeTab && (
              <button
                onClick={() => setActiveTab('office')}
                className="text-blue-600 hover:text-blue-800 font-medium"
              >
                Switch to 100% accurate viewer
              </button>
            )}

            {activeTab === 'edit' && (
              <span className="text-gray-500">
                Changes auto-saved
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Help tooltip (optional) */}
      {docxViewerError && activeTab === 'original' && !previewUrl && (
        <div className="absolute bottom-16 right-6 bg-yellow-100 border border-yellow-300 rounded-lg p-4 shadow-lg max-w-sm z-20">
          <div className="flex items-start">
            <svg
              className="w-5 h-5 text-yellow-700 mt-0.5 mr-3 flex-shrink-0"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            <div className="flex-1">
              <h4 className="text-sm font-semibold text-yellow-900 mb-1">
                Complex Document Detected
              </h4>
              <p className="text-xs text-yellow-800 mb-2">
                Your document uses advanced features that may not render perfectly.
                You can still edit in Edit Mode.
              </p>
              <button
                onClick={() => setActiveTab('edit')}
                className="text-xs bg-yellow-200 hover:bg-yellow-300 text-yellow-900 px-3 py-1.5 rounded font-medium transition-colors"
              >
                Go to Edit Mode
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ResumeViewerTabs;
