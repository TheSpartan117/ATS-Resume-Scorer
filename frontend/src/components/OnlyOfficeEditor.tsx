/**
 * OnlyOfficeEditor Component
 *
 * Integrates OnlyOffice Document Server for 100% Word-like editing experience.
 * This component embeds the OnlyOffice Document Editor with zero format discrepancy.
 *
 * Features:
 * - Full Microsoft Word compatibility
 * - Real-time collaborative editing
 * - Auto-save functionality
 * - JWT-based security
 *
 * Requirements:
 * - OnlyOffice Document Server running on http://localhost:8080
 * - Backend API endpoint: /api/onlyoffice/config/{session_id}
 */

import { useEffect, useRef, useState } from 'react';
import axios from 'axios';

interface OnlyOfficeEditorProps {
  sessionId: string;
  onDocumentReady?: () => void;
  onError?: (error: string) => void;
  className?: string;
}

interface OnlyOfficeConfig {
  documentType: string;
  document: {
    fileType: string;
    key: string;
    title: string;
    url: string;
    permissions: {
      comment: boolean;
      download: boolean;
      edit: boolean;
      fillForms: boolean;
      modifyFilter: boolean;
      modifyContentControl: boolean;
      review: boolean;
      print: boolean;
    };
  };
  editorConfig: {
    callbackUrl: string;
    mode: string;
    lang: string;
    user: {
      id: string;
      name: string;
    };
    customization: Record<string, any>;
  };
  token?: string;
}

// Declare global DocsAPI type
declare global {
  interface Window {
    DocsAPI?: {
      DocEditor: new (containerId: string, config: any) => any;
    };
  }
}

export const OnlyOfficeEditor: React.FC<OnlyOfficeEditorProps> = ({
  sessionId,
  onDocumentReady,
  onError,
  className = '',
}) => {
  const editorContainerRef = useRef<HTMLDivElement>(null);
  const editorInstanceRef = useRef<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isScriptLoaded, setIsScriptLoaded] = useState(false);

  // Load OnlyOffice API script
  useEffect(() => {
    // Check if script is already loaded
    if (window.DocsAPI) {
      setIsScriptLoaded(true);
      return;
    }

    const script = document.createElement('script');
    script.src = 'http://localhost:8080/web-apps/apps/api/documents/api.js';
    script.async = true;

    script.onload = () => {
      console.log('OnlyOffice API script loaded');
      setIsScriptLoaded(true);
    };

    script.onerror = () => {
      const errorMsg = 'Failed to load OnlyOffice Document Server. Is it running on port 8080?';
      console.error(errorMsg);
      setError(errorMsg);
      setIsLoading(false);
      onError?.(errorMsg);
    };

    document.body.appendChild(script);

    return () => {
      // Cleanup script on unmount
      if (script.parentNode) {
        script.parentNode.removeChild(script);
      }
    };
  }, [onError]);

  // Initialize OnlyOffice editor
  useEffect(() => {
    if (!isScriptLoaded || !window.DocsAPI) {
      return;
    }

    const initEditor = async () => {
      try {
        setIsLoading(true);
        setError(null);

        // Fetch editor configuration from backend
        const response = await axios.post(
          `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/onlyoffice/config/${sessionId}`
        );

        const config: OnlyOfficeConfig = response.data;

        console.log('OnlyOffice config received:', config);

        // Destroy existing editor instance if any
        if (editorInstanceRef.current) {
          try {
            editorInstanceRef.current.destroyEditor();
          } catch (err) {
            console.warn('Error destroying previous editor:', err);
          }
        }

        // Create editor instance
        if (editorContainerRef.current && window.DocsAPI) {
          const editor = new window.DocsAPI.DocEditor('onlyoffice-editor-container', {
            ...config,
            width: '100%',
            height: '100%',
            events: {
              onDocumentReady: () => {
                console.log('Document is ready for editing');
                setIsLoading(false);
                onDocumentReady?.();
              },
              onError: (event: any) => {
                const errorMsg = `OnlyOffice error: ${JSON.stringify(event.data)}`;
                console.error(errorMsg);
                setError(errorMsg);
                setIsLoading(false);
                onError?.(errorMsg);
              },
              onWarning: (event: any) => {
                console.warn('OnlyOffice warning:', event.data);
              },
              onInfo: (event: any) => {
                console.log('OnlyOffice info:', event.data);
              },
            },
          });

          editorInstanceRef.current = editor;
        }
      } catch (err) {
        const errorMsg = err instanceof Error ? err.message : 'Failed to initialize OnlyOffice editor';
        console.error('Error initializing editor:', err);
        setError(errorMsg);
        setIsLoading(false);
        onError?.(errorMsg);
      }
    };

    initEditor();

    // Cleanup editor on unmount
    return () => {
      if (editorInstanceRef.current) {
        try {
          editorInstanceRef.current.destroyEditor();
        } catch (err) {
          console.warn('Error destroying editor on unmount:', err);
        }
      }
    };
  }, [sessionId, isScriptLoaded, onDocumentReady, onError]);

  return (
    <div className={`relative w-full h-full ${className}`}>
      {/* Loading State */}
      {isLoading && !error && (
        <div className="absolute inset-0 flex items-center justify-center bg-white bg-opacity-90 z-10">
          <div className="text-center">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mb-4"></div>
            <p className="text-gray-600 font-medium">Loading OnlyOffice Editor...</p>
            <p className="text-gray-500 text-sm mt-2">Preparing your document</p>
          </div>
        </div>
      )}

      {/* Error State */}
      {error && (
        <div className="absolute inset-0 flex items-center justify-center bg-red-50 z-10">
          <div className="max-w-md text-center p-6">
            <div className="text-red-600 mb-4">
              <svg className="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              Failed to Load Editor
            </h3>
            <p className="text-gray-600 text-sm mb-4">{error}</p>
            <div className="bg-yellow-100 border border-yellow-300 rounded-lg p-4 text-left text-sm">
              <p className="font-semibold text-yellow-900 mb-2">Troubleshooting:</p>
              <ul className="list-disc list-inside text-yellow-800 space-y-1">
                <li>Ensure OnlyOffice is running: <code className="bg-yellow-200 px-1 rounded">docker-compose up</code></li>
                <li>Check if port 8080 is accessible</li>
                <li>Verify backend is running on port 8000</li>
                <li>Check browser console for details</li>
              </ul>
            </div>
          </div>
        </div>
      )}

      {/* Editor Container */}
      <div
        id="onlyoffice-editor-container"
        ref={editorContainerRef}
        className="w-full h-full"
        style={{ minHeight: '600px' }}
      />

      {/* Info Badge */}
      {!isLoading && !error && (
        <div className="absolute bottom-4 right-4 bg-white shadow-lg rounded-lg px-3 py-2 text-xs text-gray-600 border border-gray-200">
          <span className="flex items-center">
            <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
            OnlyOffice Document Server
          </span>
        </div>
      )}
    </div>
  );
};

export default OnlyOfficeEditor;
