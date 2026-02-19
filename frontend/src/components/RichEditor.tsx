/**
 * RichEditor Component
 * A focused TipTap-based rich text editor for section-based resume editing
 * Designed for use in the 70-30 split editor layout
 */
import { useEditor, EditorContent } from '@tiptap/react';
import StarterKit from '@tiptap/starter-kit';
import { Underline } from '@tiptap/extension-underline';
import { TextAlign } from '@tiptap/extension-text-align';
import { TextStyle } from '@tiptap/extension-text-style';
import { Color } from '@tiptap/extension-color';
import { Placeholder } from '@tiptap/extension-placeholder';
import { useEffect, useRef } from 'react';

interface RichEditorProps {
  content: string;
  onChange: (html: string) => void;
  onReady?: (editor: any) => void;
  sectionId?: string;
  compact?: boolean;
  editable?: boolean;
  placeholder?: string;
}

const RichEditor: React.FC<RichEditorProps> = ({
  content,
  onChange,
  onReady,
  sectionId,
  compact = false,
  editable = true,
  placeholder = 'Start typing...',
}) => {
  const isInitializedRef = useRef(false);

  const editor = useEditor({
    extensions: [
      StarterKit.configure({
        heading: {
          levels: [1, 2, 3],
        },
      }),
      Underline,
      TextAlign.configure({
        types: ['heading', 'paragraph'],
      }),
      TextStyle,
      Color,
      Placeholder.configure({
        placeholder,
      }),
    ],
    content: content,
    editable: editable,
    editorProps: {
      attributes: {
        class: `rich-editor-content ${compact ? 'compact' : ''}`,
        role: 'textbox',
        'data-section-id': sectionId || '',
      },
    },
    onUpdate: ({ editor }) => {
      if (editable) {
        onChange(editor.getHTML());
      }
    },
  });

  // Initialize content once
  useEffect(() => {
    if (editor && content && !isInitializedRef.current) {
      editor.commands.setContent(content);
      isInitializedRef.current = true;

      // Notify parent that editor is ready
      if (onReady) {
        onReady(editor);
      }
    }
  }, [editor, content, onReady]);

  // Update editable state
  useEffect(() => {
    if (editor) {
      editor.setEditable(editable);
    }
  }, [editor, editable]);

  if (!editor) {
    return null;
  }

  return (
    <div className={`rich-editor-wrapper ${compact ? 'compact' : ''}`}>
      {/* Toolbar */}
      {editable && (
        <div className={`rich-editor-toolbar ${compact ? 'compact' : ''}`}>
          {/* Text Formatting */}
          <div className="toolbar-group">
            <button
              type="button"
              onClick={() => editor.chain().focus().toggleBold().run()}
              className={`toolbar-btn ${editor.isActive('bold') ? 'is-active' : ''}`}
              title="Bold"
              disabled={!editable}
            >
              <strong>B</strong>
            </button>
            <button
              type="button"
              onClick={() => editor.chain().focus().toggleItalic().run()}
              className={`toolbar-btn ${editor.isActive('italic') ? 'is-active' : ''}`}
              title="Italic"
              disabled={!editable}
            >
              <em>I</em>
            </button>
            <button
              type="button"
              onClick={() => editor.chain().focus().toggleUnderline().run()}
              className={`toolbar-btn ${editor.isActive('underline') ? 'is-active' : ''}`}
              title="Underline"
              disabled={!editable}
            >
              <u>U</u>
            </button>
          </div>

          <div className="toolbar-divider" />

          {/* Headings */}
          {!compact && (
            <>
              <div className="toolbar-group">
                <button
                  type="button"
                  onClick={() => editor.chain().focus().toggleHeading({ level: 2 }).run()}
                  className={`toolbar-btn ${editor.isActive('heading', { level: 2 }) ? 'is-active' : ''}`}
                  title="Heading 2"
                  disabled={!editable}
                >
                  H2
                </button>
                <button
                  type="button"
                  onClick={() => editor.chain().focus().toggleHeading({ level: 3 }).run()}
                  className={`toolbar-btn ${editor.isActive('heading', { level: 3 }) ? 'is-active' : ''}`}
                  title="Heading 3"
                  disabled={!editable}
                >
                  H3
                </button>
              </div>

              <div className="toolbar-divider" />
            </>
          )}

          {/* Lists */}
          <div className="toolbar-group">
            <button
              type="button"
              onClick={() => editor.chain().focus().toggleBulletList().run()}
              className={`toolbar-btn ${editor.isActive('bulletList') ? 'is-active' : ''}`}
              title="Bullet List"
              disabled={!editable}
            >
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path
                  fillRule="evenodd"
                  d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z"
                  clipRule="evenodd"
                />
              </svg>
            </button>
            <button
              type="button"
              onClick={() => editor.chain().focus().toggleOrderedList().run()}
              className={`toolbar-btn ${editor.isActive('orderedList') ? 'is-active' : ''}`}
              title="Numbered List"
              disabled={!editable}
            >
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path
                  fillRule="evenodd"
                  d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z"
                  clipRule="evenodd"
                />
              </svg>
            </button>
          </div>

          {!compact && (
            <>
              <div className="toolbar-divider" />

              {/* Text Alignment */}
              <div className="toolbar-group">
                <button
                  type="button"
                  onClick={() => editor.chain().focus().setTextAlign('left').run()}
                  className={`toolbar-btn ${editor.isActive({ textAlign: 'left' }) ? 'is-active' : ''}`}
                  title="Align Left"
                  disabled={!editable}
                >
                  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                    <path
                      fillRule="evenodd"
                      d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h8a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h8a1 1 0 110 2H4a1 1 0 01-1-1z"
                      clipRule="evenodd"
                    />
                  </svg>
                </button>
                <button
                  type="button"
                  onClick={() => editor.chain().focus().setTextAlign('center').run()}
                  className={`toolbar-btn ${editor.isActive({ textAlign: 'center' }) ? 'is-active' : ''}`}
                  title="Align Center"
                  disabled={!editable}
                >
                  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                    <path
                      fillRule="evenodd"
                      d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm2 4a1 1 0 011-1h8a1 1 0 110 2H6a1 1 0 01-1-1zm-2 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm2 4a1 1 0 011-1h8a1 1 0 110 2H6a1 1 0 01-1-1z"
                      clipRule="evenodd"
                    />
                  </svg>
                </button>
              </div>

              <div className="toolbar-divider" />

              {/* Undo/Redo */}
              <div className="toolbar-group">
                <button
                  type="button"
                  onClick={() => editor.chain().focus().undo().run()}
                  disabled={!editor.can().undo() || !editable}
                  className="toolbar-btn"
                  title="Undo"
                >
                  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                    <path
                      fillRule="evenodd"
                      d="M9.707 16.707a1 1 0 01-1.414 0l-6-6a1 1 0 010-1.414l6-6a1 1 0 011.414 1.414L5.414 9H17a1 1 0 110 2H5.414l4.293 4.293a1 1 0 010 1.414z"
                      clipRule="evenodd"
                    />
                  </svg>
                </button>
                <button
                  type="button"
                  onClick={() => editor.chain().focus().redo().run()}
                  disabled={!editor.can().redo() || !editable}
                  className="toolbar-btn"
                  title="Redo"
                >
                  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                    <path
                      fillRule="evenodd"
                      d="M10.293 16.707a1 1 0 001.414 0l6-6a1 1 0 000-1.414l-6-6a1 1 0 00-1.414 1.414L14.586 9H3a1 1 0 100 2h11.586l-4.293 4.293a1 1 0 000 1.414z"
                      clipRule="evenodd"
                    />
                  </svg>
                </button>
              </div>
            </>
          )}
        </div>
      )}

      {/* Editor Content Area */}
      <div className="rich-editor-container">
        <EditorContent editor={editor} />
      </div>

      {/* Styles */}
      <style>{`
        /* Rich Editor Wrapper */
        .rich-editor-wrapper {
          display: flex;
          flex-direction: column;
          height: 100%;
          background-color: white;
          border-radius: 0.5rem;
          border: 1px solid #e5e7eb;
          overflow: hidden;
        }

        .rich-editor-wrapper.compact {
          border-radius: 0.375rem;
        }

        /* Toolbar Styles */
        .rich-editor-toolbar {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          padding: 0.75rem;
          background-color: #f9fafb;
          border-bottom: 1px solid #e5e7eb;
          flex-wrap: wrap;
        }

        .rich-editor-toolbar.compact {
          padding: 0.5rem;
          gap: 0.25rem;
        }

        .toolbar-group {
          display: flex;
          gap: 0.25rem;
        }

        .toolbar-divider {
          width: 1px;
          height: 1.5rem;
          background-color: #d1d5db;
        }

        /* Toolbar Button Styles */
        .toolbar-btn {
          display: flex;
          align-items: center;
          justify-content: center;
          min-width: 2rem;
          min-height: 2rem;
          padding: 0.375rem 0.5rem;
          background-color: white;
          border: 1px solid #d1d5db;
          border-radius: 0.375rem;
          font-size: 0.875rem;
          font-weight: 500;
          color: #374151;
          cursor: pointer;
          transition: all 0.15s ease;
        }

        .toolbar-btn:hover:not(:disabled) {
          background-color: #f3f4f6;
          border-color: #9ca3af;
        }

        .toolbar-btn:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }

        .toolbar-btn.is-active {
          background-color: #3b82f6;
          color: white;
          border-color: #2563eb;
        }

        .toolbar-btn svg {
          width: 1rem;
          height: 1rem;
        }

        /* Editor Container */
        .rich-editor-container {
          flex: 1;
          overflow-y: auto;
          padding: 1rem;
          background-color: white;
        }

        /* Editor Content */
        .rich-editor-content {
          outline: none;
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica', 'Arial', sans-serif;
          font-size: 0.875rem;
          line-height: 1.6;
          color: #1f2937;
        }

        .rich-editor-content.compact {
          font-size: 0.8125rem;
        }

        .rich-editor-content:focus {
          outline: none;
        }

        /* Heading Styles */
        .rich-editor-content h1 {
          font-size: 1.5rem;
          font-weight: 700;
          color: #111827;
          margin-top: 1rem;
          margin-bottom: 0.75rem;
        }

        .rich-editor-content h2 {
          font-size: 1.25rem;
          font-weight: 600;
          color: #1f2937;
          margin-top: 0.875rem;
          margin-bottom: 0.625rem;
        }

        .rich-editor-content h3 {
          font-size: 1.125rem;
          font-weight: 600;
          color: #374151;
          margin-top: 0.75rem;
          margin-bottom: 0.5rem;
        }

        /* Paragraph Styles */
        .rich-editor-content p {
          margin-bottom: 0.75rem;
          color: #1f2937;
        }

        .rich-editor-content p:last-child {
          margin-bottom: 0;
        }

        /* Strong and Emphasis */
        .rich-editor-content strong {
          font-weight: 700;
          color: #111827;
        }

        .rich-editor-content em {
          font-style: italic;
        }

        .rich-editor-content u {
          text-decoration: underline;
        }

        /* List Styles */
        .rich-editor-content ul,
        .rich-editor-content ol {
          margin-left: 1.5rem;
          margin-bottom: 0.75rem;
        }

        .rich-editor-content ul {
          list-style-type: disc;
        }

        .rich-editor-content ol {
          list-style-type: decimal;
        }

        .rich-editor-content li {
          margin-bottom: 0.375rem;
          color: #1f2937;
        }

        .rich-editor-content li p {
          margin-bottom: 0;
        }

        /* Nested Lists */
        .rich-editor-content ul ul,
        .rich-editor-content ol ol,
        .rich-editor-content ul ol,
        .rich-editor-content ol ul {
          margin-top: 0.25rem;
          margin-bottom: 0.25rem;
        }

        /* Code */
        .rich-editor-content code {
          background-color: #f3f4f6;
          padding: 0.125rem 0.375rem;
          border-radius: 0.25rem;
          font-family: 'Courier New', monospace;
          font-size: 0.875em;
        }

        .rich-editor-content pre {
          background-color: #f3f4f6;
          padding: 1rem;
          border-radius: 0.375rem;
          overflow-x: auto;
          margin-bottom: 0.75rem;
        }

        .rich-editor-content pre code {
          background-color: transparent;
          padding: 0;
        }

        /* Blockquote */
        .rich-editor-content blockquote {
          border-left: 3px solid #3b82f6;
          padding-left: 1rem;
          margin-left: 0;
          margin-bottom: 0.75rem;
          color: #4b5563;
          font-style: italic;
        }

        /* Horizontal Rule */
        .rich-editor-content hr {
          border: none;
          border-top: 1px solid #e5e7eb;
          margin: 1rem 0;
        }

        /* Selection */
        .rich-editor-content ::selection {
          background-color: #bfdbfe;
        }

        /* Placeholder */
        .rich-editor-content p.is-editor-empty:first-child::before {
          color: #9ca3af;
          content: attr(data-placeholder);
          float: left;
          height: 0;
          pointer-events: none;
        }

        /* Read-only State */
        .rich-editor-content[contenteditable='false'] {
          cursor: default;
          background-color: #f9fafb;
        }
      `}</style>
    </div>
  );
};

export default RichEditor;
