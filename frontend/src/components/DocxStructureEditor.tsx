/**
 * DOCX Structure Editor
 * Binary-level DOCX editing that preserves 100% formatting
 * Shows editable text fields with formatting indicators
 */
import { useState, useEffect } from 'react';
import axios from 'axios';

interface Run {
  id: number;
  text: string;
  formatting: {
    bold: boolean;
    italic: boolean;
    underline: boolean;
    font_name: string;
    font_size: number;
    font_color: string;
  };
}

interface Paragraph {
  id: number;
  text: string;
  style: string | null;
  runs: Run[];
}

interface Section {
  paragraphs: Paragraph[];
  tables: any[];
}

interface DocxStructure {
  sections: Section[];
  metadata: any;
}

interface DocxStructureEditorProps {
  sessionId: string;
  onSave?: () => void;
}

export const DocxStructureEditor: React.FC<DocxStructureEditorProps> = ({
  sessionId,
  onSave,
}) => {
  const [structure, setStructure] = useState<DocxStructure | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [editedRuns, setEditedRuns] = useState<Map<number, string>>(new Map());

  useEffect(() => {
    loadStructure();
  }, [sessionId]);

  const loadStructure = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await axios.get(`/api/docx-editor/structure/${sessionId}`);
      setStructure(response.data.structure);
    } catch (err) {
      console.error('Failed to load structure:', err);
      setError('Failed to load document structure');
    } finally {
      setLoading(false);
    }
  };

  const handleRunTextChange = (runId: number, newText: string) => {
    setEditedRuns(prev => {
      const newMap = new Map(prev);
      newMap.set(runId, newText);
      return newMap;
    });
  };

  const saveChanges = async () => {
    if (editedRuns.size === 0) {
      alert('No changes to save');
      return;
    }

    try {
      setSaving(true);
      setError(null);

      // Build edits structure
      const paragraphEdits = new Map<number, any[]>();

      structure?.sections.forEach(section => {
        section.paragraphs.forEach(para => {
          const runEdits: any[] = [];

          para.runs.forEach(run => {
            if (editedRuns.has(run.id)) {
              runEdits.push({
                run_id: run.id,
                text: editedRuns.get(run.id)
              });
            }
          });

          if (runEdits.length > 0) {
            paragraphEdits.set(para.id, runEdits);
          }
        });
      });

      const edits = Array.from(paragraphEdits.entries()).map(([paraId, runEdits]) => ({
        paragraph_id: paraId,
        run_edits: runEdits
      }));

      await axios.post(`/api/docx-editor/update/${sessionId}`, { edits });

      alert('Changes saved successfully!');
      setEditedRuns(new Map());
      onSave?.();

    } catch (err) {
      console.error('Failed to save changes:', err);
      setError('Failed to save changes');
    } finally {
      setSaving(false);
    }
  };

  const downloadEdited = async () => {
    try {
      window.open(`/api/docx-editor/download/${sessionId}`, '_blank');
    } catch (err) {
      console.error('Failed to download:', err);
      alert('Failed to download document');
    }
  };

  const getRunDisplay = (run: Run): React.CSSProperties => {
    return {
      fontWeight: run.formatting.bold ? 'bold' : 'normal',
      fontStyle: run.formatting.italic ? 'italic' : 'normal',
      textDecoration: run.formatting.underline ? 'underline' : 'none',
      fontFamily: run.formatting.font_name,
      fontSize: `${run.formatting.font_size}pt`,
      color: run.formatting.font_color,
    };
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading document structure...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <p className="text-red-600">{error}</p>
        <button
          onClick={loadStructure}
          className="mt-2 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
        >
          Retry
        </button>
      </div>
    );
  }

  if (!structure) {
    return (
      <div className="text-center text-gray-600 p-8">
        No document loaded
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full">
      {/* Toolbar */}
      <div className="bg-white border-b border-gray-300 px-4 py-3 flex items-center justify-between shadow-sm">
        <div>
          <h2 className="text-lg font-semibold text-gray-800">Structure Editor</h2>
          <p className="text-sm text-gray-500">Edit text while preserving 100% formatting</p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={saveChanges}
            disabled={saving || editedRuns.size === 0}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          >
            {saving ? (
              <>
                <span className="animate-spin">⏳</span> Saving...
              </>
            ) : (
              <>
                💾 Save Changes {editedRuns.size > 0 && `(${editedRuns.size})`}
              </>
            )}
          </button>
          <button
            onClick={downloadEdited}
            className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 flex items-center gap-2"
          >
            📥 Download DOCX
          </button>
        </div>
      </div>

      {/* Editor Content */}
      <div className="flex-1 overflow-auto p-6 bg-gray-50">
        <div className="max-w-4xl mx-auto bg-white shadow-lg rounded-lg p-8">
          {structure.sections.map((section, sectionIdx) => (
            <div key={sectionIdx} className="space-y-4">
              {section.paragraphs.map((para, paraIdx) => (
                <div
                  key={para.id}
                  className="border-l-4 border-blue-200 pl-4 py-2 hover:bg-blue-50 transition"
                >
                  {/* Paragraph Style Indicator */}
                  {para.style && (
                    <div className="text-xs text-gray-500 mb-1 font-mono">
                      Style: {para.style}
                    </div>
                  )}

                  {/* Runs (editable text fragments) */}
                  <div className="space-y-2">
                    {para.runs.map((run, runIdx) => {
                      const currentText = editedRuns.get(run.id) ?? run.text;
                      const hasChanges = editedRuns.has(run.id);

                      return (
                        <div key={run.id} className="flex items-start gap-3">
                          {/* Formatting Indicator */}
                          <div className="text-xs text-gray-500 font-mono whitespace-nowrap flex-shrink-0 w-32">
                            {run.formatting.bold && <span className="font-bold">B</span>}
                            {run.formatting.italic && <span className="italic">I</span>}
                            {run.formatting.underline && <span className="underline">U</span>}
                            {' '}
                            {run.formatting.font_size}pt
                          </div>

                          {/* Editable Text */}
                          <div className="flex-1">
                            <textarea
                              value={currentText}
                              onChange={(e) => handleRunTextChange(run.id, e.target.value)}
                              className={`w-full border rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                                hasChanges ? 'border-yellow-400 bg-yellow-50' : 'border-gray-300'
                              }`}
                              style={getRunDisplay(run)}
                              rows={Math.max(1, Math.ceil(currentText.length / 60))}
                            />
                            {hasChanges && (
                              <div className="text-xs text-yellow-600 mt-1">
                                ✏️ Modified
                              </div>
                            )}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              ))}

              {/* Tables (if any) */}
              {section.tables.map((table, tableIdx) => (
                <div
                  key={tableIdx}
                  className="border border-gray-300 rounded-lg p-4 bg-gray-50"
                >
                  <div className="text-sm text-gray-600">
                    📊 Table: {table.rows} rows × {table.cols} columns
                  </div>
                  <div className="text-xs text-gray-500 mt-1">
                    Table editing coming soon
                  </div>
                </div>
              ))}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default DocxStructureEditor;
