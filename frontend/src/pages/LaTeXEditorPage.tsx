/**
 * LaTeX Editor Page
 *
 * Upload DOCX → Convert to LaTeX → Edit → Export PDF
 */
import { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import LaTeXEditor from '../components/LaTeXEditor';

const LaTeXEditorPage = () => {
  const [latexCode, setLatexCode] = useState('');
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [fileName, setFileName] = useState('');
  const fileInputRef = useRef<HTMLInputElement>(null);
  const navigate = useNavigate();

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    if (!file.name.endsWith('.docx')) {
      setError('Please upload a DOCX file');
      return;
    }

    setIsUploading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch('/api/latex/convert', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        let errorMessage = 'Conversion failed';
        try {
          const errorData = await response.json();
          errorMessage = errorData.detail || errorMessage;
        } catch {
          errorMessage = `Server error (${response.status}): ${response.statusText}`;
        }
        throw new Error(errorMessage);
      }

      const data = await response.json();
      setLatexCode(data.latex_code);
      setFileName(data.filename || file.name);

    } catch (err) {
      console.error('Upload error:', err);
      setError(err instanceof Error ? err.message : 'Failed to convert file');
    } finally {
      setIsUploading(false);
      // Reset file input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const handleStartFromTemplate = () => {
    // User can start with the default template (already in LaTeXEditor)
    setLatexCode(''); // This will use the default template
    setFileName('new-resume');
  };

  return (
    <div className="h-screen flex flex-col bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between shadow-sm">
        <div className="flex items-center gap-4">
          <button
            onClick={() => navigate('/')}
            className="text-gray-600 hover:text-gray-900 transition"
          >
            ← Back
          </button>
          <h1 className="text-2xl font-bold text-gray-900">LaTeX Resume Editor</h1>
          {fileName && (
            <span className="text-sm text-gray-500">({fileName}.tex)</span>
          )}
        </div>

        <div className="flex items-center gap-3">
          {!latexCode && (
            <>
              <button
                onClick={handleStartFromTemplate}
                className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition flex items-center gap-2"
              >
                📝 Start from Template
              </button>

              <div className="relative">
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".docx"
                  onChange={handleFileUpload}
                  className="hidden"
                  id="file-upload"
                />
                <label
                  htmlFor="file-upload"
                  className={`px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition cursor-pointer flex items-center gap-2 ${
                    isUploading ? 'opacity-50 cursor-not-allowed' : ''
                  }`}
                >
                  {isUploading ? (
                    <>
                      <span className="animate-spin">⏳</span> Converting...
                    </>
                  ) : (
                    <>
                      📤 Upload DOCX
                    </>
                  )}
                </label>
              </div>
            </>
          )}

          {latexCode && (
            <button
              onClick={() => {
                setLatexCode('');
                setFileName('');
                setError(null);
              }}
              className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition flex items-center gap-2"
            >
              🔄 New Document
            </button>
          )}
        </div>
      </header>

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 border-l-4 border-red-500 px-6 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-red-600 text-xl">⚠</span>
            <span className="text-red-800">{error}</span>
          </div>
          <button
            onClick={() => setError(null)}
            className="text-red-600 hover:text-red-800 font-bold"
          >
            ✕
          </button>
        </div>
      )}

      {/* Welcome Screen or Editor */}
      {!latexCode ? (
        <div className="flex-1 flex items-center justify-center">
          <div className="max-w-2xl text-center px-6">
            <div className="text-6xl mb-6">📄</div>
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Professional Resume Editor
            </h2>
            <p className="text-lg text-gray-600 mb-8">
              Convert your DOCX resume to LaTeX for professional typesetting and formatting.
              Edit with live preview and export to PDF.
            </p>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
              <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
                <div className="text-3xl mb-3">📤</div>
                <h3 className="font-semibold text-lg mb-2">Upload DOCX</h3>
                <p className="text-sm text-gray-600">
                  Convert your existing resume to LaTeX format automatically
                </p>
              </div>

              <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
                <div className="text-3xl mb-3">📝</div>
                <h3 className="font-semibold text-lg mb-2">Start from Template</h3>
                <p className="text-sm text-gray-600">
                  Begin with a professional LaTeX template and customize it
                </p>
              </div>
            </div>

            <div className="flex flex-col gap-4">
              <input
                ref={fileInputRef}
                type="file"
                accept=".docx"
                onChange={handleFileUpload}
                className="hidden"
                id="welcome-file-upload"
              />
              <label
                htmlFor="welcome-file-upload"
                className={`inline-block px-8 py-4 bg-blue-600 text-white text-lg rounded-lg hover:bg-blue-700 transition cursor-pointer ${
                  isUploading ? 'opacity-50 cursor-not-allowed' : ''
                }`}
              >
                {isUploading ? 'Converting...' : 'Upload DOCX Resume'}
              </label>

              <button
                onClick={handleStartFromTemplate}
                className="inline-block px-8 py-4 bg-gray-600 text-white text-lg rounded-lg hover:bg-gray-700 transition"
              >
                Start from Template
              </button>
            </div>

            <div className="mt-8 text-sm text-gray-500">
              <p>✨ Features:</p>
              <ul className="mt-2 space-y-1">
                <li>✓ Split-pane editor with live preview</li>
                <li>✓ Professional LaTeX typesetting</li>
                <li>✓ Export to PDF</li>
                <li>✓ Download LaTeX source</li>
              </ul>
            </div>
          </div>
        </div>
      ) : (
        <div className="flex-1 overflow-hidden">
          <LaTeXEditor
            initialContent={latexCode}
            onContentChange={setLatexCode}
            onExportPDF={() => {
              console.log('PDF exported');
            }}
          />
        </div>
      )}
    </div>
  );
};

export default LaTeXEditorPage;
