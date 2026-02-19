/**
 * Tiptap Editor Component for Resume Editing
 * Professional CV-style editor with Word/PDF-like appearance
 */
import { useEditor, EditorContent } from '@tiptap/react'
import StarterKit from '@tiptap/starter-kit'
import { Underline } from '@tiptap/extension-underline'
import { TextAlign } from '@tiptap/extension-text-align'
import { TextStyle } from '@tiptap/extension-text-style'
import { Color } from '@tiptap/extension-color'
import { useEffect, useRef } from 'react'

interface TiptapEditorProps {
  content: string
  onChange: (html: string) => void
  onReady?: (editor: any) => void
}

export const TiptapEditor: React.FC<TiptapEditorProps> = ({ content, onChange, onReady }) => {
  const isInitializedRef = useRef(false)

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
    ],
    content: content,
    editorProps: {
      attributes: {
        class: 'tiptap-editor-content',
      },
    },
    onUpdate: ({ editor }) => {
      onChange(editor.getHTML())
    },
  })

  // Initialize content once
  useEffect(() => {
    if (editor && content && !isInitializedRef.current) {
      editor.commands.setContent(content)
      isInitializedRef.current = true

      // Notify parent that editor is ready
      if (onReady) {
        onReady(editor)
      }
    }
  }, [editor, content, onReady])

  if (!editor) {
    return null
  }

  return (
    <div className="tiptap-editor-wrapper bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden">
      {/* Toolbar */}
      <div className="toolbar bg-gray-50 border-b border-gray-200 p-3 flex flex-wrap gap-2 items-center">
        {/* Text Formatting */}
        <div className="flex gap-1">
          <button
            onClick={() => editor.chain().focus().toggleBold().run()}
            className={`toolbar-button ${editor.isActive('bold') ? 'is-active' : ''}`}
            title="Bold"
          >
            <strong>B</strong>
          </button>
          <button
            onClick={() => editor.chain().focus().toggleItalic().run()}
            className={`toolbar-button ${editor.isActive('italic') ? 'is-active' : ''}`}
            title="Italic"
          >
            <em>I</em>
          </button>
          <button
            onClick={() => editor.chain().focus().toggleUnderline().run()}
            className={`toolbar-button ${editor.isActive('underline') ? 'is-active' : ''}`}
            title="Underline"
          >
            <u>U</u>
          </button>
        </div>

        <div className="w-px h-6 bg-gray-300" />

        {/* Headings */}
        <div className="flex gap-1">
          <button
            onClick={() => editor.chain().focus().toggleHeading({ level: 1 }).run()}
            className={`toolbar-button ${editor.isActive('heading', { level: 1 }) ? 'is-active' : ''}`}
            title="Heading 1"
          >
            H1
          </button>
          <button
            onClick={() => editor.chain().focus().toggleHeading({ level: 2 }).run()}
            className={`toolbar-button ${editor.isActive('heading', { level: 2 }) ? 'is-active' : ''}`}
            title="Heading 2"
          >
            H2
          </button>
          <button
            onClick={() => editor.chain().focus().toggleHeading({ level: 3 }).run()}
            className={`toolbar-button ${editor.isActive('heading', { level: 3 }) ? 'is-active' : ''}`}
            title="Heading 3"
          >
            H3
          </button>
          <button
            onClick={() => editor.chain().focus().setParagraph().run()}
            className={`toolbar-button ${editor.isActive('paragraph') ? 'is-active' : ''}`}
            title="Paragraph"
          >
            P
          </button>
        </div>

        <div className="w-px h-6 bg-gray-300" />

        {/* Lists */}
        <div className="flex gap-1">
          <button
            onClick={() => editor.chain().focus().toggleBulletList().run()}
            className={`toolbar-button ${editor.isActive('bulletList') ? 'is-active' : ''}`}
            title="Bullet List"
          >
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clipRule="evenodd" />
            </svg>
          </button>
          <button
            onClick={() => editor.chain().focus().toggleOrderedList().run()}
            className={`toolbar-button ${editor.isActive('orderedList') ? 'is-active' : ''}`}
            title="Numbered List"
          >
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clipRule="evenodd" />
            </svg>
          </button>
        </div>

        <div className="w-px h-6 bg-gray-300" />

        {/* Text Alignment */}
        <div className="flex gap-1">
          <button
            onClick={() => editor.chain().focus().setTextAlign('left').run()}
            className={`toolbar-button ${editor.isActive({ textAlign: 'left' }) ? 'is-active' : ''}`}
            title="Align Left"
          >
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h8a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h8a1 1 0 110 2H4a1 1 0 01-1-1z" clipRule="evenodd" />
            </svg>
          </button>
          <button
            onClick={() => editor.chain().focus().setTextAlign('center').run()}
            className={`toolbar-button ${editor.isActive({ textAlign: 'center' }) ? 'is-active' : ''}`}
            title="Align Center"
          >
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm2 4a1 1 0 011-1h8a1 1 0 110 2H6a1 1 0 01-1-1zm-2 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm2 4a1 1 0 011-1h8a1 1 0 110 2H6a1 1 0 01-1-1z" clipRule="evenodd" />
            </svg>
          </button>
          <button
            onClick={() => editor.chain().focus().setTextAlign('right').run()}
            className={`toolbar-button ${editor.isActive({ textAlign: 'right' }) ? 'is-active' : ''}`}
            title="Align Right"
          >
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm4 4a1 1 0 011-1h8a1 1 0 110 2H8a1 1 0 01-1-1zm-4 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm4 4a1 1 0 011-1h8a1 1 0 110 2H8a1 1 0 01-1-1z" clipRule="evenodd" />
            </svg>
          </button>
        </div>

        <div className="w-px h-6 bg-gray-300" />

        {/* Undo/Redo */}
        <div className="flex gap-1">
          <button
            onClick={() => editor.chain().focus().undo().run()}
            disabled={!editor.can().undo()}
            className="toolbar-button"
            title="Undo"
          >
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M9.707 16.707a1 1 0 01-1.414 0l-6-6a1 1 0 010-1.414l6-6a1 1 0 011.414 1.414L5.414 9H17a1 1 0 110 2H5.414l4.293 4.293a1 1 0 010 1.414z" clipRule="evenodd" />
            </svg>
          </button>
          <button
            onClick={() => editor.chain().focus().redo().run()}
            disabled={!editor.can().redo()}
            className="toolbar-button"
            title="Redo"
          >
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10.293 16.707a1 1 0 001.414 0l6-6a1 1 0 000-1.414l-6-6a1 1 0 00-1.414 1.414L14.586 9H3a1 1 0 100 2h11.586l-4.293 4.293a1 1 0 000 1.414z" clipRule="evenodd" />
            </svg>
          </button>
        </div>
      </div>

      {/* Editor Content Area */}
      <div className="editor-container">
        <EditorContent editor={editor} />
      </div>

      {/* Styles */}
      <style>{`
        /* Toolbar Button Styles */
        .toolbar-button {
          padding: 0.375rem 0.75rem;
          background-color: white;
          border: 1px solid #d1d5db;
          border-radius: 0.375rem;
          font-size: 0.875rem;
          font-weight: 500;
          color: #374151;
          cursor: pointer;
          transition: all 0.15s ease;
          display: flex;
          align-items: center;
          justify-content: center;
          min-width: 2rem;
        }

        .toolbar-button:hover:not(:disabled) {
          background-color: #f3f4f6;
          border-color: #9ca3af;
        }

        .toolbar-button:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }

        .toolbar-button.is-active {
          background-color: #3b82f6;
          color: white;
          border-color: #2563eb;
        }

        /* Editor Container - Paper-like appearance */
        .editor-container {
          background-color: #f9fafb;
          padding: 2rem;
          overflow-y: auto;
          max-height: 800px;
          min-height: 800px;
        }

        /* Editor Content - Document styling */
        .tiptap-editor-content {
          background-color: white;
          padding: 1in;
          min-height: 11in;
          max-width: 8.5in;
          margin: 0 auto;
          box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
          font-family: 'Georgia', 'Times New Roman', serif;
          font-size: 12pt;
          line-height: 1.6;
          color: #1f2937;
        }

        .tiptap-editor-content:focus {
          outline: none;
        }

        /* Heading Styles - CV Format */
        .tiptap-editor-content h1 {
          font-size: 24pt;
          font-weight: bold;
          color: #1e3a8a;
          margin-top: 1.5rem;
          margin-bottom: 1rem;
          border-bottom: 2px solid #bfdbfe;
          padding-bottom: 0.5rem;
          text-align: center;
        }

        .tiptap-editor-content h2 {
          font-size: 14pt;
          font-weight: bold;
          color: #3730a3;
          margin-top: 1.25rem;
          margin-bottom: 0.75rem;
          border-bottom: 1px solid #c7d2fe;
          padding-bottom: 0.25rem;
        }

        .tiptap-editor-content h3 {
          font-size: 12pt;
          font-weight: bold;
          color: #4338ca;
          margin-top: 1rem;
          margin-bottom: 0.5rem;
        }

        /* Paragraph Styles */
        .tiptap-editor-content p {
          margin-bottom: 0.75rem;
          color: #1f2937;
        }

        /* Strong and Emphasis */
        .tiptap-editor-content strong {
          font-weight: bold;
          color: #111827;
        }

        .tiptap-editor-content em {
          font-style: italic;
          color: #374151;
        }

        .tiptap-editor-content u {
          text-decoration: underline;
        }

        /* List Styles */
        .tiptap-editor-content ul,
        .tiptap-editor-content ol {
          margin-left: 1.5rem;
          margin-bottom: 0.75rem;
        }

        .tiptap-editor-content ul {
          list-style-type: disc;
        }

        .tiptap-editor-content ol {
          list-style-type: decimal;
        }

        .tiptap-editor-content li {
          margin-bottom: 0.5rem;
          color: #1f2937;
        }

        .tiptap-editor-content li p {
          margin-bottom: 0;
        }

        /* Nested Lists */
        .tiptap-editor-content ul ul,
        .tiptap-editor-content ol ol,
        .tiptap-editor-content ul ol,
        .tiptap-editor-content ol ul {
          margin-top: 0.25rem;
          margin-bottom: 0.25rem;
        }

        /* Code and Preformatted Text */
        .tiptap-editor-content code {
          background-color: #f3f4f6;
          padding: 0.125rem 0.375rem;
          border-radius: 0.25rem;
          font-family: 'Courier New', monospace;
          font-size: 0.9em;
        }

        .tiptap-editor-content pre {
          background-color: #f3f4f6;
          padding: 1rem;
          border-radius: 0.5rem;
          overflow-x: auto;
          margin-bottom: 0.75rem;
        }

        .tiptap-editor-content pre code {
          background-color: transparent;
          padding: 0;
        }

        /* Blockquote */
        .tiptap-editor-content blockquote {
          border-left: 4px solid #3b82f6;
          padding-left: 1rem;
          margin-left: 0;
          margin-bottom: 0.75rem;
          color: #4b5563;
          font-style: italic;
        }

        /* Horizontal Rule */
        .tiptap-editor-content hr {
          border: none;
          border-top: 2px solid #e5e7eb;
          margin: 1.5rem 0;
        }

        /* Selection */
        .tiptap-editor-content ::selection {
          background-color: #bfdbfe;
        }

        /* Placeholder */
        .tiptap-editor-content p.is-editor-empty:first-child::before {
          color: #9ca3af;
          content: attr(data-placeholder);
          float: left;
          height: 0;
          pointer-events: none;
        }

        /* Print-friendly */
        @media print {
          .toolbar,
          .editor-container {
            padding: 0;
            background: white;
          }

          .tiptap-editor-content {
            box-shadow: none;
            padding: 0;
          }
        }
      `}</style>
    </div>
  )
}

export default TiptapEditor
