import React, { useRef, useEffect } from 'react';

interface WYSIWYGEditorProps {
  value: string;
  onChange: (html: string) => void;
}

export const WYSIWYGEditor: React.FC<WYSIWYGEditorProps> = ({ value, onChange }) => {
  const editorRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (editorRef.current && editorRef.current.innerHTML !== value) {
      editorRef.current.innerHTML = value;
    }
  }, [value]);

  const handleInput = () => {
    if (editorRef.current) {
      onChange(editorRef.current.innerHTML);
    }
  };

  const execCommand = (command: string, value?: string) => {
    document.execCommand(command, false, value);
    editorRef.current?.focus();
    handleInput();
  };

  const insertHeading = (level: number) => {
    const selection = window.getSelection();
    if (selection && selection.rangeCount > 0) {
      const range = selection.getRangeAt(0);
      const heading = document.createElement(`h${level}`);
      heading.textContent = selection.toString() || `Heading ${level}`;
      range.deleteContents();
      range.insertNode(heading);
      handleInput();
    }
  };

  return (
    <div className="wysiwyg-editor">
      {/* Toolbar */}
      <div className="toolbar bg-gray-100 border border-gray-300 rounded-t-lg p-2 flex flex-wrap gap-1">
        {/* Text Formatting */}
        <button
          type="button"
          onClick={() => execCommand('bold')}
          className="px-3 py-1 bg-white border border-gray-300 rounded hover:bg-gray-50"
          title="Bold (Ctrl+B)"
        >
          <strong>B</strong>
        </button>
        <button
          type="button"
          onClick={() => execCommand('italic')}
          className="px-3 py-1 bg-white border border-gray-300 rounded hover:bg-gray-50"
          title="Italic (Ctrl+I)"
        >
          <em>I</em>
        </button>
        <button
          type="button"
          onClick={() => execCommand('underline')}
          className="px-3 py-1 bg-white border border-gray-300 rounded hover:bg-gray-50"
          title="Underline (Ctrl+U)"
        >
          <u>U</u>
        </button>

        <div className="w-px bg-gray-300 mx-1"></div>

        {/* Headings */}
        <button
          type="button"
          onClick={() => execCommand('formatBlock', '<h1>')}
          className="px-3 py-1 bg-white border border-gray-300 rounded hover:bg-gray-50 text-sm"
          title="Heading 1"
        >
          H1
        </button>
        <button
          type="button"
          onClick={() => execCommand('formatBlock', '<h2>')}
          className="px-3 py-1 bg-white border border-gray-300 rounded hover:bg-gray-50 text-sm"
          title="Heading 2"
        >
          H2
        </button>
        <button
          type="button"
          onClick={() => execCommand('formatBlock', '<h3>')}
          className="px-3 py-1 bg-white border border-gray-300 rounded hover:bg-gray-50 text-sm"
          title="Heading 3"
        >
          H3
        </button>
        <button
          type="button"
          onClick={() => execCommand('formatBlock', '<p>')}
          className="px-3 py-1 bg-white border border-gray-300 rounded hover:bg-gray-50 text-sm"
          title="Normal"
        >
          P
        </button>

        <div className="w-px bg-gray-300 mx-1"></div>

        {/* Lists */}
        <button
          type="button"
          onClick={() => execCommand('insertUnorderedList')}
          className="px-3 py-1 bg-white border border-gray-300 rounded hover:bg-gray-50"
          title="Bullet List"
        >
          • List
        </button>
        <button
          type="button"
          onClick={() => execCommand('insertOrderedList')}
          className="px-3 py-1 bg-white border border-gray-300 rounded hover:bg-gray-50"
          title="Numbered List"
        >
          1. List
        </button>

        <div className="w-px bg-gray-300 mx-1"></div>

        {/* Alignment */}
        <button
          type="button"
          onClick={() => execCommand('justifyLeft')}
          className="px-3 py-1 bg-white border border-gray-300 rounded hover:bg-gray-50"
          title="Align Left"
        >
          ⬅
        </button>
        <button
          type="button"
          onClick={() => execCommand('justifyCenter')}
          className="px-3 py-1 bg-white border border-gray-300 rounded hover:bg-gray-50"
          title="Align Center"
        >
          ↔
        </button>
        <button
          type="button"
          onClick={() => execCommand('justifyRight')}
          className="px-3 py-1 bg-white border border-gray-300 rounded hover:bg-gray-50"
          title="Align Right"
        >
          ➡
        </button>

        <div className="w-px bg-gray-300 mx-1"></div>

        {/* Indent */}
        <button
          type="button"
          onClick={() => execCommand('indent')}
          className="px-3 py-1 bg-white border border-gray-300 rounded hover:bg-gray-50"
          title="Indent"
        >
          →
        </button>
        <button
          type="button"
          onClick={() => execCommand('outdent')}
          className="px-3 py-1 bg-white border border-gray-300 rounded hover:bg-gray-50"
          title="Outdent"
        >
          ←
        </button>

        <div className="w-px bg-gray-300 mx-1"></div>

        {/* Other */}
        <button
          type="button"
          onClick={() => execCommand('createLink', prompt('Enter URL:') || '')}
          className="px-3 py-1 bg-white border border-gray-300 rounded hover:bg-gray-50"
          title="Insert Link"
        >
          🔗
        </button>
        <button
          type="button"
          onClick={() => execCommand('removeFormat')}
          className="px-3 py-1 bg-white border border-gray-300 rounded hover:bg-gray-50"
          title="Clear Formatting"
        >
          ✖
        </button>
      </div>

      {/* Editor */}
      <div
        ref={editorRef}
        contentEditable
        onInput={handleInput}
        className="editor-content bg-white border border-gray-300 border-t-0 rounded-b-lg p-6 min-h-[600px] focus:outline-none focus:ring-2 focus:ring-blue-500 overflow-auto"
        style={{
          fontFamily: 'Arial, sans-serif',
          fontSize: '14px',
          lineHeight: '1.6',
          maxWidth: '100%',
        }}
      />
    </div>
  );
};
