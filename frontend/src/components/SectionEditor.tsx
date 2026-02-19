import { useState, useCallback } from 'react';
import { useDebounce } from '../hooks/useDebounce';
import { DEBOUNCE_DELAY_MS } from '../config/timeouts';

interface Section {
  title: string;
  content: string;
  section_id: string;
  start_para_idx: number;
  end_para_idx: number;
}

interface SectionEditorProps {
  sections: Section[];
  onSectionUpdate: (sectionId: string, content: string, startIdx: number, endIdx: number) => void;
  highlightedSection?: string;
}

export default function SectionEditor({
  sections,
  onSectionUpdate,
  highlightedSection
}: SectionEditorProps) {
  const [editedContent, setEditedContent] = useState<Record<string, string>>({});
  const [collapsedSections, setCollapsedSections] = useState<Set<string>>(new Set());

  const toggleSection = (sectionId: string) => {
    const newCollapsed = new Set(collapsedSections);
    if (newCollapsed.has(sectionId)) {
      newCollapsed.delete(sectionId);
    } else {
      newCollapsed.add(sectionId);
    }
    setCollapsedSections(newCollapsed);
  };

  const handleContentChange = (section: Section, newContent: string) => {
    setEditedContent(prev => ({ ...prev, [section.section_id]: newContent }));

    // Debounced update to backend
    debouncedUpdate(section.section_id, newContent, section.start_para_idx, section.end_para_idx);
  };

  const debouncedUpdate = useDebounce(
    (sectionId: string, content: string, startIdx: number, endIdx: number) => {
      onSectionUpdate(sectionId, content, startIdx, endIdx);
    },
    DEBOUNCE_DELAY_MS
  );

  const getIcon = (title: string) => {
    const lower = title.toLowerCase();
    if (lower.includes('experience') || lower.includes('work')) return '💼';
    if (lower.includes('education')) return '🎓';
    if (lower.includes('skill')) return '🛠️';
    if (lower.includes('contact') || lower.includes('info')) return '📧';
    if (lower.includes('summary') || lower.includes('profile')) return '📝';
    if (lower.includes('project')) return '🚀';
    if (lower.includes('certification') || lower.includes('award')) return '🏆';
    return '📄';
  };

  return (
    <div className="w-1/2 overflow-y-auto p-6 bg-gray-50 border-r border-gray-300">
      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-xl font-bold text-gray-800">Resume Sections</h2>
        <button
          onClick={() => setCollapsedSections(collapsedSections.size > 0 ? new Set() : new Set(sections.map(s => s.section_id)))}
          className="text-sm text-blue-600 hover:text-blue-800"
        >
          {collapsedSections.size > 0 ? '📂 Expand All' : '📁 Collapse All'}
        </button>
      </div>

      <div className="space-y-4">
        {sections.map((section) => {
          const isCollapsed = collapsedSections.has(section.section_id);
          const isHighlighted = highlightedSection === section.section_id;
          const content = editedContent[section.section_id] ?? section.content;

          return (
            <div
              key={section.section_id}
              className={`bg-white rounded-lg border-2 transition-all ${
                isHighlighted ? 'border-blue-500 shadow-lg' : 'border-gray-200'
              }`}
            >
              {/* Section Header */}
              <div
                onClick={() => toggleSection(section.section_id)}
                className="flex items-center justify-between p-4 cursor-pointer hover:bg-gray-50"
              >
                <div className="flex items-center space-x-3">
                  <span className="text-2xl">{getIcon(section.title)}</span>
                  <span className="font-semibold text-gray-800">{section.title}</span>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="text-xs text-gray-500">{content.length} chars</span>
                  <span className="text-gray-400">{isCollapsed ? '▼' : '▲'}</span>
                </div>
              </div>

              {/* Section Content */}
              {!isCollapsed && (
                <div className="p-4 pt-0">
                  <textarea
                    value={content}
                    onChange={(e) => handleContentChange(section, e.target.value)}
                    className="w-full min-h-32 p-3 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono text-sm"
                    placeholder={`Edit ${section.title}...`}
                  />
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
