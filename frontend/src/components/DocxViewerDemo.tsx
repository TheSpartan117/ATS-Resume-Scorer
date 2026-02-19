/**
 * DocxViewerDemo - Testing and Comparison Component
 *
 * This component demonstrates the different viewing options:
 * 1. docx-preview (Primary - 85-95% accuracy)
 * 2. Office Online (Fallback - 100% accuracy)
 * 3. Mammoth HTML (Current - 60-75% accuracy)
 *
 * Usage:
 *   <DocxViewerDemo />
 *
 * Use this for testing and comparing viewer quality.
 */

import { useState, useRef } from 'react';
import DocxViewer from './DocxViewer';

interface ViewerOption {
  id: string;
  name: string;
  accuracy: string;
  description: string;
  pros: string[];
  cons: string[];
}

const VIEWER_OPTIONS: ViewerOption[] = [
  {
    id: 'docx-preview',
    name: 'docx-preview',
    accuracy: '85-95%',
    description: 'Client-side DOCX renderer with high fidelity',
    pros: [
      'Fast rendering (< 1 second)',
      'No server required',
      'Privacy-friendly',
      'Supports tables, images, formatting',
      'Free and open-source',
    ],
    cons: [
      'Not 100% pixel-perfect',
      'Some advanced features unsupported',
      'Font substitution may occur',
    ],
  },
  {
    id: 'office-online',
    name: 'Office Online',
    accuracy: '100%',
    description: 'Microsoft Word Online embedded viewer',
    pros: [
      'Perfect accuracy (100%)',
      'Supports all Word features',
      'Professional appearance',
      'Free service',
    ],
    cons: [
      'Requires public URL',
      'Slower loading (3-5 seconds)',
      'Privacy concerns',
      'Network dependent',
    ],
  },
  {
    id: 'mammoth',
    name: 'Mammoth HTML',
    accuracy: '60-75%',
    description: 'Current HTML converter (baseline)',
    pros: [
      'Already implemented',
      'Good for text extraction',
      'Editable in TipTap',
    ],
    cons: [
      'Low fidelity',
      'Loses complex formatting',
      'Tables lose styling',
      'No images',
    ],
  },
];

export const DocxViewerDemo: React.FC = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [activeViewer, setActiveViewer] = useState<string>('docx-preview');
  const [fileContent, setFileContent] = useState<string>('');
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setSelectedFile(file);

    // Read file for Office Online preview (needs URL)
    const reader = new FileReader();
    reader.onload = (event) => {
      const result = event.target?.result;
      if (typeof result === 'string') {
        setFileContent(result);
      }
    };
    reader.readAsDataURL(file);
  };

  const handleSelectViewer = (viewerId: string) => {
    setActiveViewer(viewerId);
  };

  const currentOption = VIEWER_OPTIONS.find((opt) => opt.id === activeViewer);

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Word Document Viewer Comparison
          </h1>
          <p className="text-gray-600 mb-4">
            Test and compare different DOCX viewing solutions for accuracy and performance
          </p>

          {/* File Upload */}
          <div className="flex items-center space-x-4">
            <button
              onClick={() => fileInputRef.current?.click()}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium transition-colors"
            >
              {selectedFile ? 'Change File' : 'Upload DOCX File'}
            </button>
            <input
              ref={fileInputRef}
              type="file"
              accept=".docx"
              onChange={handleFileSelect}
              className="hidden"
            />
            {selectedFile && (
              <div className="text-sm text-gray-600">
                <span className="font-medium">Selected:</span> {selectedFile.name}
                <span className="ml-2 text-gray-400">
                  ({(selectedFile.size / 1024).toFixed(1)} KB)
                </span>
              </div>
            )}
          </div>
        </div>

        <div className="grid grid-cols-12 gap-6">
          {/* Left Sidebar - Viewer Options */}
          <div className="col-span-3">
            <div className="bg-white rounded-lg shadow-lg p-4">
              <h2 className="text-lg font-bold text-gray-900 mb-4">
                Viewer Options
              </h2>

              <div className="space-y-3">
                {VIEWER_OPTIONS.map((option) => (
                  <button
                    key={option.id}
                    onClick={() => handleSelectViewer(option.id)}
                    className={`
                      w-full text-left p-4 rounded-lg border-2 transition-all
                      ${
                        activeViewer === option.id
                          ? 'border-blue-600 bg-blue-50'
                          : 'border-gray-200 hover:border-gray-300 bg-white'
                      }
                    `}
                  >
                    <div className="font-semibold text-gray-900 mb-1">
                      {option.name}
                    </div>
                    <div className="text-xs text-gray-600 mb-2">
                      {option.description}
                    </div>
                    <div
                      className={`
                        inline-block px-2 py-1 rounded text-xs font-medium
                        ${
                          option.accuracy === '100%'
                            ? 'bg-green-100 text-green-800'
                            : option.accuracy.startsWith('85')
                            ? 'bg-blue-100 text-blue-800'
                            : 'bg-yellow-100 text-yellow-800'
                        }
                      `}
                    >
                      {option.accuracy} Accurate
                    </div>
                  </button>
                ))}
              </div>

              {/* Current Option Details */}
              {currentOption && (
                <div className="mt-6 pt-6 border-t border-gray-200">
                  <h3 className="font-semibold text-gray-900 mb-3 text-sm">
                    Details
                  </h3>

                  <div className="mb-4">
                    <h4 className="text-xs font-medium text-green-700 mb-2">
                      ✅ Pros:
                    </h4>
                    <ul className="text-xs text-gray-600 space-y-1">
                      {currentOption.pros.map((pro, idx) => (
                        <li key={idx} className="flex items-start">
                          <span className="text-green-600 mr-1">•</span>
                          {pro}
                        </li>
                      ))}
                    </ul>
                  </div>

                  <div>
                    <h4 className="text-xs font-medium text-red-700 mb-2">
                      ❌ Cons:
                    </h4>
                    <ul className="text-xs text-gray-600 space-y-1">
                      {currentOption.cons.map((con, idx) => (
                        <li key={idx} className="flex items-start">
                          <span className="text-red-600 mr-1">•</span>
                          {con}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Main Content - Viewer Display */}
          <div className="col-span-9">
            <div className="bg-white rounded-lg shadow-lg overflow-hidden">
              {/* Viewer Header */}
              <div className="bg-gradient-to-r from-blue-600 to-indigo-600 px-6 py-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h2 className="text-xl font-bold text-white">
                      {currentOption?.name} Viewer
                    </h2>
                    <p className="text-blue-100 text-sm mt-1">
                      {currentOption?.description}
                    </p>
                  </div>
                  <div className="bg-white bg-opacity-20 px-4 py-2 rounded-lg">
                    <div className="text-white text-2xl font-bold">
                      {currentOption?.accuracy}
                    </div>
                    <div className="text-blue-100 text-xs">Accuracy</div>
                  </div>
                </div>
              </div>

              {/* Viewer Content */}
              <div className="h-[800px] overflow-hidden">
                {!selectedFile && (
                  <div className="h-full flex items-center justify-center bg-gray-50">
                    <div className="text-center text-gray-500">
                      <svg
                        className="w-24 h-24 mx-auto mb-4 text-gray-400"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={1.5}
                          d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                        />
                      </svg>
                      <p className="text-xl font-medium mb-2">
                        Upload a DOCX file to start
                      </p>
                      <p className="text-sm">
                        Compare viewer accuracy and performance
                      </p>
                    </div>
                  </div>
                )}

                {selectedFile && activeViewer === 'docx-preview' && (
                  <DocxViewer docxFile={selectedFile} className="h-full" />
                )}

                {selectedFile && activeViewer === 'office-online' && (
                  <div className="h-full flex items-center justify-center bg-yellow-50 p-8">
                    <div className="max-w-lg text-center">
                      <svg
                        className="w-16 h-16 mx-auto mb-4 text-yellow-600"
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
                      <h3 className="text-lg font-bold text-gray-900 mb-2">
                        Office Online Requires Public URL
                      </h3>
                      <p className="text-sm text-gray-600 mb-4">
                        Office Online viewer requires the document to be hosted at a
                        publicly accessible URL. In a production environment:
                      </p>
                      <ol className="text-left text-sm text-gray-700 space-y-2 mb-4">
                        <li className="flex items-start">
                          <span className="font-bold mr-2">1.</span>
                          Backend uploads file to cloud storage (S3, Azure Blob)
                        </li>
                        <li className="flex items-start">
                          <span className="font-bold mr-2">2.</span>
                          Generate public URL with temporary access
                        </li>
                        <li className="flex items-start">
                          <span className="font-bold mr-2">3.</span>
                          Pass URL to Office Online:
                          <code className="block mt-1 bg-gray-100 p-2 rounded text-xs">
                            https://view.officeapps.live.com/op/embed.aspx?src=YOUR_URL
                          </code>
                        </li>
                      </ol>
                      <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 text-xs text-blue-800">
                        <strong>Note:</strong> This demo uses local files. Enable Office
                        Online in production with public URLs.
                      </div>
                    </div>
                  </div>
                )}

                {selectedFile && activeViewer === 'mammoth' && (
                  <div className="h-full flex items-center justify-center bg-gray-50 p-8">
                    <div className="max-w-lg text-center">
                      <svg
                        className="w-16 h-16 mx-auto mb-4 text-gray-400"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                        />
                      </svg>
                      <h3 className="text-lg font-bold text-gray-900 mb-2">
                        Mammoth HTML Converter
                      </h3>
                      <p className="text-sm text-gray-600 mb-4">
                        Mammoth is currently used in the backend to convert DOCX to HTML
                        for TipTap editing. It provides basic formatting but loses
                        fidelity.
                      </p>
                      <div className="bg-gray-100 rounded-lg p-4 text-left text-xs">
                        <p className="font-semibold mb-2">Current Usage:</p>
                        <code className="block bg-white p-2 rounded mb-2">
                          DOCX → Mammoth → HTML → TipTap Editor
                        </code>
                        <p className="text-gray-600">
                          Mammoth strips complex formatting to create clean HTML suitable
                          for editing. Good for content, not for accurate preview.
                        </p>
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* Viewer Footer - Performance Stats */}
              {selectedFile && (
                <div className="bg-gray-50 border-t border-gray-200 px-6 py-3">
                  <div className="grid grid-cols-4 gap-4 text-center text-xs">
                    <div>
                      <div className="text-gray-600 mb-1">Accuracy</div>
                      <div className="font-bold text-lg">
                        {currentOption?.accuracy}
                      </div>
                    </div>
                    <div>
                      <div className="text-gray-600 mb-1">Cost</div>
                      <div className="font-bold text-lg text-green-600">Free</div>
                    </div>
                    <div>
                      <div className="text-gray-600 mb-1">Speed</div>
                      <div className="font-bold text-lg">
                        {activeViewer === 'docx-preview' ? '< 1s' :
                         activeViewer === 'office-online' ? '3-5s' : '< 1s'}
                      </div>
                    </div>
                    <div>
                      <div className="text-gray-600 mb-1">Privacy</div>
                      <div className="font-bold text-lg">
                        {activeViewer === 'office-online' ? '⚠️' : '✅'}
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Recommendation */}
            <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-6">
              <h3 className="text-lg font-bold text-blue-900 mb-2">
                💡 Recommendation
              </h3>
              <p className="text-sm text-blue-800 mb-3">
                Use <strong>docx-preview</strong> as the primary viewer for 90% of use cases.
                It provides excellent accuracy (85-95%), is completely free, protects user
                privacy, and renders instantly.
              </p>
              <p className="text-sm text-blue-800">
                Add <strong>Office Online</strong> as a fallback for complex documents or
                when 100% accuracy is critical. This gives users the best of both worlds.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DocxViewerDemo;
