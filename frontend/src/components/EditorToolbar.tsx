/**
 * Toolbar for TipTap editor with formatting buttons
 */
import { Editor } from '@tiptap/react'

interface EditorToolbarProps {
  editor: Editor | null
}

export default function EditorToolbar({ editor }: EditorToolbarProps) {
  if (!editor) {
    return null
  }

  const ButtonClass = (isActive: boolean) =>
    `px-3 py-1 rounded text-sm font-medium transition-colors ${
      isActive
        ? 'bg-blue-600 text-white'
        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
    }`

  return (
    <div className="border-b border-gray-300 p-2 bg-gray-50 flex flex-wrap gap-2">
      {/* Text Formatting */}
      <div className="flex gap-1">
        <button
          type="button"
          onClick={() => editor.chain().focus().toggleBold().run()}
          className={ButtonClass(editor.isActive('bold'))}
          title="Bold (Ctrl+B)"
        >
          <strong>B</strong>
        </button>
        <button
          type="button"
          onClick={() => editor.chain().focus().toggleItalic().run()}
          className={ButtonClass(editor.isActive('italic'))}
          title="Italic (Ctrl+I)"
        >
          <em>I</em>
        </button>
        <button
          type="button"
          onClick={() => editor.chain().focus().toggleStrike().run()}
          className={ButtonClass(editor.isActive('strike'))}
          title="Strikethrough"
        >
          <s>S</s>
        </button>
      </div>

      {/* Divider */}
      <div className="border-l border-gray-300"></div>

      {/* Headings */}
      <div className="flex gap-1">
        <button
          type="button"
          onClick={() => editor.chain().focus().toggleHeading({ level: 1 }).run()}
          className={ButtonClass(editor.isActive('heading', { level: 1 }))}
          title="Heading 1"
        >
          H1
        </button>
        <button
          type="button"
          onClick={() => editor.chain().focus().toggleHeading({ level: 2 }).run()}
          className={ButtonClass(editor.isActive('heading', { level: 2 }))}
          title="Heading 2"
        >
          H2
        </button>
        <button
          type="button"
          onClick={() => editor.chain().focus().toggleHeading({ level: 3 }).run()}
          className={ButtonClass(editor.isActive('heading', { level: 3 }))}
          title="Heading 3"
        >
          H3
        </button>
      </div>

      {/* Divider */}
      <div className="border-l border-gray-300"></div>

      {/* Lists */}
      <div className="flex gap-1">
        <button
          type="button"
          onClick={() => editor.chain().focus().toggleBulletList().run()}
          className={ButtonClass(editor.isActive('bulletList'))}
          title="Bullet List"
        >
          • List
        </button>
        <button
          type="button"
          onClick={() => editor.chain().focus().toggleOrderedList().run()}
          className={ButtonClass(editor.isActive('orderedList'))}
          title="Numbered List"
        >
          1. List
        </button>
      </div>

      {/* Divider */}
      <div className="border-l border-gray-300"></div>

      {/* Misc */}
      <div className="flex gap-1">
        <button
          type="button"
          onClick={() => editor.chain().focus().setHorizontalRule().run()}
          className={ButtonClass(false)}
          title="Horizontal Rule"
        >
          ―
        </button>
        <button
          type="button"
          onClick={() => editor.chain().focus().undo().run()}
          disabled={!editor.can().undo()}
          className="px-3 py-1 rounded text-sm font-medium bg-gray-100 text-gray-700 hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed"
          title="Undo (Ctrl+Z)"
        >
          ↶ Undo
        </button>
        <button
          type="button"
          onClick={() => editor.chain().focus().redo().run()}
          disabled={!editor.can().redo()}
          className="px-3 py-1 rounded text-sm font-medium bg-gray-100 text-gray-700 hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed"
          title="Redo (Ctrl+Y)"
        >
          ↷ Redo
        </button>
      </div>
    </div>
  )
}
