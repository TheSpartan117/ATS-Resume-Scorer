// frontend/src/components/OfficeViewer.tsx
import { useState, useEffect } from 'react';

interface OfficeViewerProps {
  previewUrl: string;
  isUpdating?: boolean;
}

export default function OfficeViewer({ previewUrl, isUpdating = false }: OfficeViewerProps) {
  const [iframeKey, setIframeKey] = useState(0);
  const [hasError, setHasError] = useState(false);

  // Force iframe refresh when preview URL changes
  useEffect(() => {
    if (previewUrl) {
      setIframeKey(prev => prev + 1);
      setHasError(false);
    }
  }, [previewUrl]);

  // Build Office Online viewer URL
  const getViewerUrl = () => {
    const baseUrl = window.location.origin;
    const fullDocUrl = `${baseUrl}${previewUrl}`;
    return `https://view.officeapps.live.com/op/embed.aspx?src=${encodeURIComponent(fullDocUrl)}`;
  };

  const handleIframeError = () => {
    setHasError(true);
  };

  if (hasError) {
    return (
      <div className="w-1/2 bg-gray-100 flex items-center justify-center p-8">
        <div className="text-center max-w-md">
          <div className="text-6xl mb-4">⚠️</div>
          <h3 className="text-xl font-bold text-gray-800 mb-2">Preview Unavailable</h3>
          <p className="text-gray-600 mb-4">
            Unable to load Office Online viewer. This may happen if:
          </p>
          <ul className="text-sm text-gray-600 text-left list-disc list-inside mb-6">
            <li>Document is too large</li>
            <li>Network connectivity issues</li>
            <li>Microsoft Office Online service is temporarily unavailable</li>
          </ul>
          <a
            href={previewUrl}
            download
            className="inline-block px-6 py-3 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
          >
            📥 Download DOCX to view locally
          </a>
        </div>
      </div>
    );
  }

  return (
    <div className="w-1/2 relative bg-white">
      {/* Loading Overlay */}
      {isUpdating && (
        <div className="absolute inset-0 bg-white bg-opacity-90 flex flex-col items-center justify-center z-10">
          <div className="animate-spin rounded-full h-12 w-12 border-4 border-blue-500 border-t-transparent mb-4"></div>
          <p className="text-gray-700 font-semibold">Updating preview...</p>
        </div>
      )}

      {/* Office Online Viewer */}
      <iframe
        key={iframeKey}
        src={getViewerUrl()}
        className="w-full h-full border-none"
        title="Resume Preview"
        onError={handleIframeError}
        sandbox="allow-same-origin allow-scripts allow-popups allow-forms"
      />

      {/* Info Badge */}
      <div className="absolute top-4 right-4 bg-blue-100 text-blue-800 text-xs px-3 py-1 rounded-full shadow">
        📄 Live Preview
      </div>
    </div>
  );
}
