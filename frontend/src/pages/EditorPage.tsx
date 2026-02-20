import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import SuggestionsPanel from '../components/SuggestionsPanel';
import RichEditor from '../components/RichEditor';
import OfficePreview from '../components/OfficePreview';
import DocxStructureEditor from '../components/DocxStructureEditor';

interface Section {
  name: string;
  start_para: number;
  end_para: number;
}

interface Score {
  overallScore: number;
  breakdown: Record<string, number>;
}

interface SuggestionLocation {
  section: string;
  line?: number | null;
  para_idx?: number;
  after_section?: string;
}

interface Suggestion {
  id: string;
  type: 'missing_content' | 'content_change' | 'missing_section' | 'formatting';
  severity: 'critical' | 'warning' | 'suggestion' | 'info';
  title: string;
  description: string;
  location: SuggestionLocation;
  action: string;
  example?: string;
  current_text?: string;
  suggested_text?: string;
  template?: string;
  state?: 'pending' | 'fixed' | 'dismissed';
}

const EditorPage: React.FC = () => {
  const { sessionId } = useParams<{ sessionId: string }>();
  const navigate = useNavigate();

  const [activeTab, setActiveTab] = useState<'editor' | 'structure' | 'preview'>('structure');
  const [sections, setSections] = useState<Section[]>([]);
  const [currentScore, setCurrentScore] = useState<Score | null>(null);
  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);
  const [workingDocxUrl, setWorkingDocxUrl] = useState<string>('');
  const [lastScored, setLastScored] = useState<Date | undefined>(undefined);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Load session data
  useEffect(() => {
    if (!sessionId) {
      setError('No session ID provided');
      setLoading(false);
      return;
    }

    const loadSession = async () => {
      try {
        const response = await fetch(`/api/editor/session/${sessionId}`);
        if (!response.ok) {
          throw new Error('Failed to load session');
        }

        const data = await response.json();
        setSections(data.sections);
        setCurrentScore(data.current_score);
        setSuggestions(data.suggestions);
        setWorkingDocxUrl(data.working_docx_url);
        setLastScored(new Date());
        setLoading(false);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error');
        setLoading(false);
      }
    };

    loadSession();
  }, [sessionId]);

  const handleSuggestionClick = (suggestion: Suggestion) => {
    // Switch to editor tab and highlight location
    setActiveTab('editor');
    // TODO: Implement highlight logic
  };

  const handleRescore = async () => {
    if (!sessionId) return;

    try {
      const response = await fetch('/api/editor/rescore', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId })
      });

      if (!response.ok) {
        throw new Error('Rescore failed');
      }

      const data = await response.json();
      setCurrentScore(data.score);
      setSuggestions(data.suggestions);
      setLastScored(new Date());
    } catch (err) {
      console.error('Rescore error:', err);
    }
  };

  const handleDownload = () => {
    if (workingDocxUrl) {
      window.location.href = workingDocxUrl;
    }
  };

  if (loading) {
    return <div className="p-8">Loading...</div>;
  }

  if (error) {
    return <div className="p-8 text-red-600">Error: {error}</div>;
  }

  return (
    <div className="h-screen flex flex-col">
      {/* Header */}
      <header className="bg-white border-b px-6 py-4 flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold">Resume Editor</h1>
          <p className="text-sm text-gray-600">Session: {sessionId}</p>
        </div>
        <div className="flex gap-4">
          <button
            onClick={handleRescore}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            Re-score Resume
          </button>
          <button
            onClick={handleDownload}
            className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
          >
            Download DOCX
          </button>
        </div>
      </header>

      {/* Main content: 70-30 split */}
      <div className="flex-1 flex overflow-hidden">
        {/* Suggestions Panel (30%) */}
        <aside className="w-[30%] border-r bg-gray-50">
          <SuggestionsPanel
            suggestions={suggestions}
            currentScore={currentScore!}
            onSuggestionClick={handleSuggestionClick}
            onRescore={handleRescore}
            lastScored={lastScored}
          />
        </aside>

        {/* Main Panel (70%) */}
        <main className="w-[70%] flex flex-col">
          {/* Tabs */}
          <div className="border-b bg-white" role="tablist">
            <button
              role="tab"
              aria-selected={activeTab === 'structure'}
              onClick={() => setActiveTab('structure')}
              className={`px-6 py-3 font-medium ${
                activeTab === 'structure'
                  ? 'border-b-2 border-blue-600 text-blue-600'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              ⚡ Structure Editor (100% Format Preserving)
            </button>
            <button
              role="tab"
              aria-selected={activeTab === 'editor'}
              onClick={() => setActiveTab('editor')}
              className={`px-6 py-3 font-medium ${
                activeTab === 'editor'
                  ? 'border-b-2 border-blue-600 text-blue-600'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              Rich Editor
            </button>
            <button
              role="tab"
              aria-selected={activeTab === 'preview'}
              onClick={() => setActiveTab('preview')}
              className={`px-6 py-3 font-medium ${
                activeTab === 'preview'
                  ? 'border-b-2 border-blue-600 text-blue-600'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              Preview
            </button>
          </div>

          {/* Tab content */}
          <div className="flex-1 overflow-hidden">
            {activeTab === 'structure' && sessionId && (
              <DocxStructureEditor
                sessionId={sessionId}
                onSave={() => {
                  handleRescore();
                }}
              />
            )}

            {activeTab === 'editor' && (
              <div className="p-6 h-full overflow-auto">
                <RichEditor
                  content="<p>Resume content here...</p>"
                  onChange={(html) => {
                    // TODO: Implement auto-save
                  }}
                />
              </div>
            )}

            {activeTab === 'preview' && (
              <div className="p-6 h-full overflow-auto">
                <OfficePreview
                  officeOnlineUrl={workingDocxUrl}
                  docxDownloadUrl={workingDocxUrl}
                />
              </div>
            )}
          </div>
        </main>
      </div>
    </div>
  );
};

export default EditorPage;
