import { useState, useEffect } from 'react';

interface OfficePreviewProps {
  officeOnlineUrl: string;
  docxDownloadUrl?: string;
  pdfDownloadUrl?: string;
  isLoading?: boolean;
  onRefresh?: () => void;
}

export default function OfficePreview({
  officeOnlineUrl,
  docxDownloadUrl,
  pdfDownloadUrl,
  isLoading = false,
  onRefresh,
}: OfficePreviewProps) {
  const [iframeKey, setIframeKey] = useState(0);
  const [zoomLevel, setZoomLevel] = useState(100);

  // Force iframe refresh when URL changes
  useEffect(() => {
    if (officeOnlineUrl) {
      setIframeKey((prev) => prev + 1);
    }
  }, [officeOnlineUrl]);

  const handleZoomIn = () => {
    setZoomLevel((prev) => Math.min(prev + 10, 200));
  };

  const handleZoomOut = () => {
    setZoomLevel((prev) => Math.max(prev - 10, 50));
  };

  const handleRefresh = () => {
    setIframeKey((prev) => prev + 1);
    if (onRefresh) {
      onRefresh();
    }
  };

  // Error state - no URL provided
  if (!officeOnlineUrl) {
    return (
      <div className="w-full h-full flex items-center justify-center bg-gray-50">
        <div className="text-center max-w-md p-8">
          <div className="text-6xl mb-4">⚠️</div>
          <h3 className="text-xl font-semibold text-gray-800 mb-2">
            Preview Unavailable
          </h3>
          <p className="text-gray-600 mb-4">
            Unable to generate preview URL. Please try again or download the file.
          </p>
          {docxDownloadUrl && (
            <a
              href={docxDownloadUrl}
              download
              className="inline-block px-6 py-3 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
            >
              Download DOCX
            </a>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="w-full h-full relative bg-white flex flex-col">
      {/* Minimal Controls Bar */}
      <div className="flex items-center justify-between px-4 py-2 bg-gray-50 border-b border-gray-200">
        {/* Zoom Controls */}
        <div className="flex items-center gap-2">
          <button
            onClick={handleZoomOut}
            aria-label="Zoom out"
            className="p-2 hover:bg-gray-200 rounded transition-colors"
            title="Zoom out"
          >
            <svg
              className="w-5 h-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM13 10H7"
              />
            </svg>
          </button>
          <span className="text-sm text-gray-600 min-w-[4rem] text-center">
            {zoomLevel}%
          </span>
          <button
            onClick={handleZoomIn}
            aria-label="Zoom in"
            className="p-2 hover:bg-gray-200 rounded transition-colors"
            title="Zoom in"
          >
            <svg
              className="w-5 h-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v6m3-3H7"
              />
            </svg>
          </button>
        </div>

        {/* Refresh and Download */}
        <div className="flex items-center gap-2">
          <button
            onClick={handleRefresh}
            aria-label="Refresh preview"
            className="p-2 hover:bg-gray-200 rounded transition-colors"
            title="Refresh preview"
          >
            <svg
              className="w-5 h-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
              />
            </svg>
          </button>

          {docxDownloadUrl && (
            <a
              href={docxDownloadUrl}
              download
              className="px-3 py-1.5 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
            >
              Download DOCX
            </a>
          )}

          {pdfDownloadUrl && (
            <a
              href={pdfDownloadUrl}
              download
              className="px-3 py-1.5 text-sm bg-gray-600 text-white rounded hover:bg-gray-700 transition-colors"
            >
              Download PDF
            </a>
          )}
        </div>
      </div>

      {/* Loading Overlay */}
      {isLoading && (
        <div className="absolute inset-0 bg-white bg-opacity-90 flex flex-col items-center justify-center z-10">
          <div className="animate-spin rounded-full h-12 w-12 border-4 border-blue-500 border-t-transparent mb-4"></div>
          <p className="text-gray-700 font-semibold">Loading preview...</p>
        </div>
      )}

      {/* Office Online Iframe */}
      <div className="flex-1 overflow-hidden" style={{ zoom: `${zoomLevel}%` }}>
        <iframe
          key={iframeKey}
          data-key={iframeKey}
          src={officeOnlineUrl}
          className="w-full h-full border-none"
          title="DOCX Preview"
          sandbox="allow-same-origin allow-scripts allow-popups allow-forms"
        />
      </div>
    </div>
  );
}
