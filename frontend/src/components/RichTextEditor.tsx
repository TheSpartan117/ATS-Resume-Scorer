/**
 * Rich text editor component using TipTap
 */
import { useEditor, EditorContent } from '@tiptap/react'
import StarterKit from '@tiptap/starter-kit'
import Placeholder from '@tiptap/extension-placeholder'
import { useEffect } from 'react'
import EditorToolbar from './EditorToolbar'

interface RichTextEditorProps {
  content: string
  onChange: (content: string) => void
  placeholder?: string
  editable?: boolean
}

export default function RichTextEditor({
  content,
  onChange,
  placeholder = 'Start editing your resume...',
  editable = true
}: RichTextEditorProps) {
  const editor = useEditor({
    extensions: [
      StarterKit,
      Placeholder.configure({
        placeholder
      })
    ],
    content,
    editable,
    onUpdate: ({ editor }) => {
      // Only call onChange if content actually changed
      const newContent = editor.getHTML()
      if (newContent !== content) {
        onChange(newContent)
      }
    },
    editorProps: {
      attributes: {
        class: 'prose prose-sm sm:prose lg:prose-lg xl:prose-xl focus:outline-none min-h-[400px] max-w-none p-4'
      }
    }
  })

  // Update editor content when prop changes
  useEffect(() => {
    if (editor && content !== editor.getHTML()) {
      editor.commands.setContent(content)
    }
  }, [content, editor])

  // Update editable state
  useEffect(() => {
    if (editor) {
      editor.setEditable(editable)
    }
  }, [editable, editor])

  // Note: useEditor automatically handles cleanup, no manual destroy needed

  if (!editor) {
    return null
  }

  return (
    <div className="border border-gray-300 rounded-lg overflow-hidden bg-white">
      {editable && <EditorToolbar editor={editor} />}
      <EditorContent editor={editor} />
    </div>
  )
}
