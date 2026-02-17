/**
 * Toolbar for TipTap editor with formatting buttons
 */
import { Editor } from '@tiptap/react'
import { useCallback } from 'react'

interface EditorToolbarProps {
  editor: Editor | null
}

export default function EditorToolbar({ editor }: EditorToolbarProps) {
  if (!editor) {
    return null
  }

  const ButtonClass = useCallback((isActive: boolean, isDisabled: boolean = false) =>
    `px-3 py-1 rounded text-sm font-medium transition-colors ${
      isDisabled
        ? 'bg-gray-100 text-gray-700 opacity-50 cursor-not-allowed'
        : isActive
        ? 'bg-blue-600 text-white'
        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
    }`, [])

  return (
    <div className="border-b border-gray-300 p-2 bg-gray-50 flex flex-wrap gap-2">
      {/* Text Formatting */}
      <div className="flex gap-1">
        <button
          type="button"
          onClick={() => editor.chain().focus().toggleBold().run()}
          className={ButtonClass(editor.isActive('bold'))}
          title="Bold (Ctrl+B)"
          aria-label="Bold"
          aria-keyshortcuts="Control+B"
          aria-pressed={editor.isActive('bold')}
        >
          <strong>B</strong>
        </button>
        <button
          type="button"
          onClick={() => editor.chain().focus().toggleItalic().run()}
          className={ButtonClass(editor.isActive('italic'))}
          title="Italic (Ctrl+I)"
          aria-label="Italic"
          aria-keyshortcuts="Control+I"
          aria-pressed={editor.isActive('italic')}
        >
          <em>I</em>
        </button>
        <button
          type="button"
          onClick={() => editor.chain().focus().toggleStrike().run()}
          className={ButtonClass(editor.isActive('strike'))}
          title="Strikethrough"
          aria-label="Strikethrough"
          aria-pressed={editor.isActive('strike')}
        >
          <s>S</s>
        </button>
      </div>

      {/* Divider */}
      <div className="border-l border-gray-300" aria-hidden="true"></div>

      {/* Headings */}
      <div className="flex gap-1">
        <button
          type="button"
          onClick={() => editor.chain().focus().toggleHeading({ level: 1 }).run()}
          className={ButtonClass(editor.isActive('heading', { level: 1 }))}
          title="Heading 1"
          aria-label="Heading 1"
          aria-pressed={editor.isActive('heading', { level: 1 })}
        >
          H1
        </button>
        <button
          type="button"
          onClick={() => editor.chain().focus().toggleHeading({ level: 2 }).run()}
          className={ButtonClass(editor.isActive('heading', { level: 2 }))}
          title="Heading 2"
          aria-label="Heading 2"
          aria-pressed={editor.isActive('heading', { level: 2 })}
        >
          H2
        </button>
        <button
          type="button"
          onClick={() => editor.chain().focus().toggleHeading({ level: 3 }).run()}
          className={ButtonClass(editor.isActive('heading', { level: 3 }))}
          title="Heading 3"
          aria-label="Heading 3"
          aria-pressed={editor.isActive('heading', { level: 3 })}
        >
          H3
        </button>
      </div>

      {/* Divider */}
      <div className="border-l border-gray-300" aria-hidden="true"></div>

      {/* Lists */}
      <div className="flex gap-1">
        <button
          type="button"
          onClick={() => editor.chain().focus().toggleBulletList().run()}
          className={ButtonClass(editor.isActive('bulletList'))}
          title="Bullet List"
          aria-label="Bullet List"
          aria-pressed={editor.isActive('bulletList')}
        >
          • List
        </button>
        <button
          type="button"
          onClick={() => editor.chain().focus().toggleOrderedList().run()}
          className={ButtonClass(editor.isActive('orderedList'))}
          title="Numbered List"
          aria-label="Numbered List"
          aria-pressed={editor.isActive('orderedList')}
        >
          1. List
        </button>
      </div>

      {/* Divider */}
      <div className="border-l border-gray-300" aria-hidden="true"></div>

      {/* Misc */}
      <div className="flex gap-1">
        <button
          type="button"
          onClick={() => editor.chain().focus().setHorizontalRule().run()}
          className={ButtonClass(false)}
          title="Horizontal Rule"
          aria-label="Insert Horizontal Rule"
        >
          ―
        </button>
        <button
          type="button"
          onClick={() => editor.chain().focus().undo().run()}
          disabled={!editor.can().undo()}
          className={ButtonClass(false, !editor.can().undo())}
          title="Undo (Ctrl+Z)"
          aria-label="Undo"
          aria-keyshortcuts="Control+Z"
        >
          ↶ Undo
        </button>
        <button
          type="button"
          onClick={() => editor.chain().focus().redo().run()}
          disabled={!editor.can().redo()}
          className={ButtonClass(false, !editor.can().redo())}
          title="Redo (Ctrl+Y)"
          aria-label="Redo"
          aria-keyshortcuts="Control+Y"
        >
          ↷ Redo
        </button>
      </div>
    </div>
  )
}
