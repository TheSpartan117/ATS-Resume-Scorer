/**
 * DocxResumeViewer — renders a DOCX file faithfully using docx-preview,
 * then overlays annotation highlights on the rendered DOM.
 *
 * This replaces the HTML-based InteractiveResumeViewer with a Word-accurate
 * representation of the uploaded resume.
 */
import { useEffect, useRef, useState, useCallback, useMemo } from 'react'
import { renderAsync } from 'docx-preview'
import type { Annotation } from '../utils/buildAnnotations'
import { CATEGORY_COLORS, CATEGORY_BG_COLORS } from '../utils/buildAnnotations'
import AnnotationTooltip from './AnnotationTooltip'

interface DocxResumeViewerProps {
  docxBlob: Blob | null
  annotations: Annotation[]
  selectedCategory: string | null
  onAnnotationsChange: (annotations: Annotation[]) => void
  onTextChange: (newText: string) => void
}

export default function DocxResumeViewer({
  docxBlob,
  annotations,
  selectedCategory,
  onAnnotationsChange,
  onTextChange,
}: DocxResumeViewerProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [hoveredAnnotation, setHoveredAnnotation] = useState<Annotation | null>(null)
  const [anchorRect, setAnchorRect] = useState<DOMRect | null>(null)
  const isTooltipHovered = useRef(false)
  const dismissTimer = useRef<ReturnType<typeof setTimeout> | null>(null)
  const [docxRendered, setDocxRendered] = useState(false)

  // ── Render the DOCX ──────────────────────────────────────────
  useEffect(() => {
    const render = async () => {
      if (!containerRef.current || !docxBlob) {
        setIsLoading(false)
        return
      }

      setIsLoading(true)
      setError(null)

      try {
        containerRef.current.innerHTML = ''

        await renderAsync(docxBlob, containerRef.current, undefined, {
          className: 'docx-viewer-wrapper',
          inWrapper: true,
          ignoreWidth: false,
          ignoreHeight: false,
          ignoreFonts: false,
          breakPages: true,
          ignoreLastRenderedPageBreak: false,
          experimental: false,
          trimXmlDeclaration: true,
          useBase64URL: false,
          useMathMLPolyfill: true,
          renderHeaders: true,
          renderFooters: true,
          renderFootnotes: true,
          renderEndnotes: true,
          renderComments: false,
          debug: false,
        })

        setDocxRendered(true)
        setIsLoading(false)
      } catch (err) {
        console.error('DOCX render error:', err)
        setError('Failed to render document. The file may be corrupted.')
        setIsLoading(false)
      }
    }

    render()
  }, [docxBlob])

  // ── Inject annotation highlights into rendered DOM ────────────
  useEffect(() => {
    if (!docxRendered || !containerRef.current || annotations.length === 0) return

    // Remove any previous highlights
    containerRef.current.querySelectorAll('mark.annotation-highlight').forEach(el => {
      const parent = el.parentNode
      if (parent) {
        parent.replaceChild(document.createTextNode(el.textContent || ''), el)
        parent.normalize()
      }
    })

    // Walk all text nodes and inject <mark> elements for matching annotations
    const walker = document.createTreeWalker(
      containerRef.current,
      NodeFilter.SHOW_TEXT,
      null,
    )

    // Collect text nodes first (can't modify while walking)
    const textNodes: Text[] = []
    let node
    while ((node = walker.nextNode())) {
      textNodes.push(node as Text)
    }

    // Sort annotations by text length (longest first) to avoid partial matches
    const sortedAnns = [...annotations].sort((a, b) => b.text.length - a.text.length)

    // Track which annotations have already been matched to avoid duplicates
    const matched = new Set<string>()

    for (const ann of sortedAnns) {
      if (matched.has(ann.id)) continue

      for (let i = 0; i < textNodes.length; i++) {
        const textNode = textNodes[i]
        if (!textNode.parentNode) continue
        const content = textNode.nodeValue || ''
        const idx = content.indexOf(ann.text)
        if (idx === -1) continue

        // Split the text node and wrap the matched portion in a <mark>
        const before = content.substring(0, idx)
        const after = content.substring(idx + ann.text.length)

        const isDimmed = selectedCategory !== null && ann.category !== selectedCategory
        const isHighlighted = selectedCategory === null || ann.category === selectedCategory
        const categoryColor = CATEGORY_COLORS[ann.category] || '#6b7280'
        const categoryBg = CATEGORY_BG_COLORS[ann.category] || 'rgba(107,114,128,0.15)'

        const mark = document.createElement('mark')
        mark.className = 'annotation-highlight annotation-mark'
        mark.setAttribute('data-ann-id', ann.id)
        mark.textContent = ann.text

        if (ann.applied) {
          mark.style.cssText = `background-color: rgba(34, 197, 94, 0.25); border-bottom: 2px solid #22c55e; border-radius: 2px; padding: 1px 2px; cursor: pointer; opacity: ${isDimmed ? 0.3 : 1}; transition: opacity 0.2s, background-color 0.3s;`
        } else {
          mark.style.cssText = `background-color: ${isHighlighted ? categoryBg : 'transparent'}; border-bottom: ${isHighlighted ? `2px solid ${categoryColor}` : '2px solid transparent'}; border-radius: 2px; padding: 1px 2px; cursor: pointer; opacity: ${isDimmed ? 0.3 : 1}; transition: opacity 0.2s, background-color 0.3s;`
        }

        const parent = textNode.parentNode
        const afterNode = document.createTextNode(after)

        textNode.nodeValue = before
        parent.insertBefore(mark, textNode.nextSibling)
        parent.insertBefore(afterNode, mark.nextSibling)

        // Update textNodes array: the afterNode might contain more matches
        textNodes.splice(i + 1, 0, afterNode)

        matched.add(ann.id)
        break // Move to next annotation
      }
    }
  }, [docxRendered, annotations, selectedCategory])

  // ── Hover handlers ───────────────────────────────────────────
  const handleMouseEnter = useCallback((annotation: Annotation, element: HTMLElement) => {
    if (dismissTimer.current) {
      clearTimeout(dismissTimer.current)
      dismissTimer.current = null
    }
    setHoveredAnnotation(annotation)
    setAnchorRect(element.getBoundingClientRect())
  }, [])

  const handleMouseLeave = useCallback(() => {
    dismissTimer.current = setTimeout(() => {
      if (!isTooltipHovered.current) {
        setHoveredAnnotation(null)
        setAnchorRect(null)
      }
    }, 250)
  }, [])

  const handleTooltipMouseEnter = useCallback(() => {
    isTooltipHovered.current = true
    if (dismissTimer.current) {
      clearTimeout(dismissTimer.current)
      dismissTimer.current = null
    }
  }, [])

  const handleTooltipMouseLeave = useCallback(() => {
    isTooltipHovered.current = false
    setHoveredAnnotation(null)
    setAnchorRect(null)
  }, [])

  // ── Apply fix ────────────────────────────────────────────────
  const handleApplyFix = useCallback((annotation: Annotation, replacement: string) => {
    if (!containerRef.current) return

    // Find the <mark> element for this annotation and replace its text
    const mark = containerRef.current.querySelector(`mark[data-ann-id="${annotation.id}"]`)
    if (mark) {
      const textNode = document.createTextNode(replacement)
      mark.parentNode?.replaceChild(textNode, mark)
      textNode.parentNode?.normalize()
    }

    // We also need to extract the full text to keep the resumeText state in sync
    const fullText = containerRef.current.textContent || ''
    onTextChange(fullText)

    const updatedAnnotations = annotations.map(ann => {
      if (ann.id === annotation.id) {
        return { ...ann, text: replacement, applied: true }
      }
      return ann
    })

    onAnnotationsChange(updatedAnnotations)
    setHoveredAnnotation(null)
    setAnchorRect(null)
  }, [annotations, onAnnotationsChange, onTextChange])

  // ── Event delegation for hover on marks ──────────────────────
  const handleContainerMouseOver = useCallback((e: React.MouseEvent) => {
    const target = (e.target as HTMLElement).closest('mark.annotation-highlight')
    if (target) {
      const annId = target.getAttribute('data-ann-id')
      const ann = annotations.find(a => a.id === annId)
      if (ann) {
        handleMouseEnter(ann, target as HTMLElement)
      }
    }
  }, [annotations, handleMouseEnter])

  const handleContainerMouseOut = useCallback((e: React.MouseEvent) => {
    const target = (e.target as HTMLElement).closest('mark.annotation-highlight')
    if (target) {
      const related = e.relatedTarget as Node | null
      if (related && target.contains(related)) {
        return // Still inside the same mark
      }
      handleMouseLeave()
    }
  }, [handleMouseLeave])

  // ── Stats ────────────────────────────────────────────────────
  const totalAnnotations = annotations.length
  const appliedCount = annotations.filter(a => a.applied).length
  const pendingCount = totalAnnotations - appliedCount

  return (
    <div className="h-full flex flex-col">
      {/* Stats bar */}
      <div className="flex items-center justify-between px-4 py-2.5 bg-gradient-to-r from-gray-50 to-gray-100 border-b border-gray-200 flex-shrink-0">
        <div className="flex items-center gap-4 text-xs">
          <span className="text-gray-600 font-medium">
            📝 {totalAnnotations} annotation{totalAnnotations !== 1 ? 's' : ''}
          </span>
          {appliedCount > 0 && (
            <span className="text-green-700 font-medium flex items-center gap-1">
              <span className="w-2 h-2 rounded-full bg-green-500" />
              {appliedCount} fixed
            </span>
          )}
          {pendingCount > 0 && (
            <span className="text-amber-700 font-medium flex items-center gap-1">
              <span className="w-2 h-2 rounded-full bg-amber-500" />
              {pendingCount} pending
            </span>
          )}
        </div>
        {selectedCategory && (
          <span className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded-full font-medium">
            Filtering: {selectedCategory}
          </span>
        )}
      </div>

      {/* DOCX content */}
      <div className="flex-1 overflow-y-auto bg-gray-100 relative">
        {/* Loading overlay */}
        {isLoading && (
          <div className="absolute inset-0 bg-white bg-opacity-95 flex items-center justify-center z-20">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-4 border-blue-500 border-t-transparent mb-4 mx-auto" />
              <p className="text-gray-700 font-semibold">Rendering document...</p>
              <p className="text-gray-500 text-sm mt-1">This may take a few seconds</p>
            </div>
          </div>
        )}

        {/* Error state */}
        {error && (
          <div className="m-4 p-4 bg-red-50 border-l-4 border-red-500 rounded-lg">
            <p className="text-red-800 font-medium">{error}</p>
          </div>
        )}

        {/* Rendered DOCX container */}
        <div
          ref={containerRef}
          className="docx-viewer-content"
          onMouseOver={handleContainerMouseOver}
          onMouseOut={handleContainerMouseOut}
        />
      </div>

      {/* Tooltip */}
      {hoveredAnnotation && anchorRect && (
        <AnnotationTooltip
          annotation={hoveredAnnotation}
          anchorRect={anchorRect}
          onApply={handleApplyFix}
          onDismiss={handleTooltipMouseLeave}
          onTooltipMouseEnter={handleTooltipMouseEnter}
          onTooltipMouseLeave={handleTooltipMouseLeave}
        />
      )}

      {/* Scoped styles for docx-preview output */}
      <style>{`
        .docx-viewer-content .docx-viewer-wrapper {
          background: white;
          margin: 24px auto;
          box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
          border-radius: 4px;
          overflow: hidden;
        }

        .docx-viewer-content .docx-viewer-wrapper section.docx {
          margin: 0 auto;
          background: white;
        }

        /* Annotation marks must sit on top and receive events */
        .docx-viewer-content mark.annotation-highlight {
          transition: all 0.2s ease;
          position: relative;
          z-index: 50 !important;
          pointer-events: auto !important;
        }

        .docx-viewer-content mark.annotation-highlight:hover {
          filter: brightness(0.92);
        }

        /* Fix LibreOffice text box overlaps: force relative positioning */
        .docx-viewer-content .docx-viewer-wrapper div {
          position: relative !important;
          top: auto !important;
          left: auto !important;
          transform: none !important;
          margin-bottom: 4px;
        }

        /* Prevent SVG overlays (like borders drawn by Word) from blocking mouse events to the text underneath */
        .docx-viewer-content svg {
          pointer-events: none !important;
        }
      `}</style>
    </div>
  )
}
