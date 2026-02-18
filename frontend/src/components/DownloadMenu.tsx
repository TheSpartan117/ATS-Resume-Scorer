import React, { useState } from 'react';
import apiClient from '../api/client';

interface DownloadMenuProps {
  resumeContent: string;
  resumeName: string;
  resumeData: any;
  scoreData: any;
  mode: string;
  role: string;
  level: string;
}

export const DownloadMenu: React.FC<DownloadMenuProps> = ({
  resumeContent,
  resumeName,
  resumeData,
  scoreData,
  mode,
  role,
  level
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [downloading, setDownloading] = useState<string | null>(null);

  const handleDownloadResume = async (format: 'pdf' | 'docx') => {
    setDownloading(format);

    try {
      const response = await apiClient.post('/api/export/resume', {
        content: resumeContent,
        name: resumeName,
        format
      }, {
        responseType: 'blob'
      });

      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${resumeName}_Resume.${format}`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error(`Failed to download ${format}:`, error);
      alert(`Failed to download resume as ${format.toUpperCase()}`);
    } finally {
      setDownloading(null);
      setIsOpen(false);
    }
  };

  const handleDownloadReport = async () => {
    setDownloading('report');

    try {
      const response = await apiClient.post('/api/export/report', {
        resumeData,
        scoreData,
        mode,
        role,
        level
      }, {
        responseType: 'blob'
      });

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${resumeName}_ATS_Report.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Failed to download report:', error);
      alert('Failed to download report');
    } finally {
      setDownloading(null);
      setIsOpen(false);
    }
  };

  const handleCopySuggestions = () => {
    const suggestions = scoreData.issues?.map((issue: any) =>
      `• ${issue.message}`
    ).join('\n') || 'No suggestions available';

    navigator.clipboard.writeText(suggestions);
    alert('Suggestions copied to clipboard!');
    setIsOpen(false);
  };

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-4 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700 transition-colors"
      >
        Download ▼
      </button>

      {isOpen && (
        <>
          <div
            className="fixed inset-0 z-10"
            onClick={() => setIsOpen(false)}
          />
          <div className="absolute right-0 mt-2 w-56 bg-white rounded-lg shadow-lg border border-gray-200 z-20">
            <button
              onClick={() => handleDownloadResume('pdf')}
              disabled={downloading === 'pdf'}
              className="w-full px-4 py-3 text-left hover:bg-gray-50 flex items-center gap-2 border-b border-gray-100"
            >
              <span>📄</span>
              <span>{downloading === 'pdf' ? 'Downloading...' : 'Download as PDF'}</span>
            </button>

            <button
              onClick={() => handleDownloadResume('docx')}
              disabled={downloading === 'docx'}
              className="w-full px-4 py-3 text-left hover:bg-gray-50 flex items-center gap-2 border-b border-gray-100"
            >
              <span>📝</span>
              <span>{downloading === 'docx' ? 'Downloading...' : 'Download as DOCX'}</span>
            </button>

            <button
              onClick={handleDownloadReport}
              disabled={downloading === 'report'}
              className="w-full px-4 py-3 text-left hover:bg-gray-50 flex items-center gap-2 border-b border-gray-100"
            >
              <span>📊</span>
              <span>{downloading === 'report' ? 'Downloading...' : 'Download Report'}</span>
            </button>

            <button
              onClick={handleCopySuggestions}
              className="w-full px-4 py-3 text-left hover:bg-gray-50 flex items-center gap-2"
            >
              <span>📋</span>
              <span>Copy Suggestions</span>
            </button>
          </div>
        </>
      )}
    </div>
  );
};
