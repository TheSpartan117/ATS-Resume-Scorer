/**
 * Interactive Resume Viewer — renders resume text with inline annotations.
 *
 * Occupies the left 70% of the results page. Supported features:
 * - Highlighted phrases (colour-coded by category)
 * - Hover tooltips with suggestions
 * - Inline apply-fix (turns highlights green)
 * - Category filtering (dim/show highlights per category)
 * - Undo / redo history
 */
import { useState, useCallback, useMemo, useRef } from 'react'
import type { Annotation } from '../utils/buildAnnotations'
import { CATEGORY_COLORS, CATEGORY_BG_COLORS } from '../utils/buildAnnotations'
import AnnotationTooltip from './AnnotationTooltip'

interface InteractiveResumeViewerProps {
  resumeHtml: string
  annotations: Annotation[]
  selectedCategory: string | null
  onAnnotationsChange: (annotations: Annotation[]) => void
  onHtmlChange: (newHtml: string) => void
  undoStack: string[]
  redoStack: string[]
}

export default function InteractiveResumeViewer({
  resumeHtml,
  annotations,
  selectedCategory,
  onAnnotationsChange,
  onHtmlChange,
}: InteractiveResumeViewerProps) {
  const [hoveredAnnotation, setHoveredAnnotation] = useState<Annotation | null>(null)
  const [anchorRect, setAnchorRect] = useState<DOMRect | null>(null)
  const isTooltipHovered = useRef(false)
  const dismissTimer = useRef<ReturnType<typeof setTimeout> | null>(null)

  // Handle hover on a mark element
  const handleMouseEnter = useCallback((annotation: Annotation, element: HTMLElement) => {
    // Cancel any pending dismiss
    if (dismissTimer.current) {
      clearTimeout(dismissTimer.current)
      dismissTimer.current = null
    }
    setHoveredAnnotation(annotation)
    setAnchorRect(element.getBoundingClientRect())
  }, [])

  const handleMouseLeave = useCallback(() => {
    // Delay dismiss to let user move mouse to the tooltip
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

  // Apply a fix: replace text inside the HTML and update annotation
  const handleApplyFix = useCallback((annotation: Annotation, replacement: string) => {
    // We need to replace the text inside the HTML. Since we're injecting markers using replace,
    // the safest way to replace the text in the source HTML is to find it via its exact match if possible.
    // However, since annotations keep track of plain-text indices, we'll try a regex replace on the HTML.
    // For a robust WYSIWYG, we'd use a DOM parser, but here we can do a targeted replace.
    // Create a temporary element to manipulate the DOM
    const tempDiv = document.createElement('div')
    tempDiv.innerHTML = resumeHtml

    // Find the text node containing the annotation text and replace it
    // A simplified approach is just replacing the text content of the whole document, but that risks
    // replacing unintended occurrences. Instead, we'll replace the *first* matching text node whose
    // content matches, or just do a global replace of the phrase if it's unique enough (which it often is).
    // For ATS-Resume-Scorer, a simple replace on the innerHTML text nodes is best:
    const walker = document.createTreeWalker(tempDiv, NodeFilter.SHOW_TEXT, null)
    let node
    let matched = false
    while ((node = walker.nextNode()) && !matched) {
      if (node.nodeValue?.includes(annotation.text)) {
        node.nodeValue = node.nodeValue.replace(annotation.text, replacement)
        matched = true
      }
    }

    const newHtml = tempDiv.innerHTML

    // Update the annotation
    const updatedAnnotations = annotations.map(ann => {
      if (ann.id === annotation.id) {
        return { ...ann, text: replacement, applied: true }
      }
      return ann
    })

    onHtmlChange(newHtml)
    onAnnotationsChange(updatedAnnotations)
    setHoveredAnnotation(null)
    setAnchorRect(null)
  }, [resumeHtml, annotations, onHtmlChange, onAnnotationsChange])

  // Process the HTML to inject <mark> tags around annotation matches
  const processedHtml = useMemo(() => {
    if (annotations.length === 0 || !resumeHtml) return resumeHtml || ''

    // Sort annotations by length (longest first) to prevent inner matches replacing outer matches
    const sorted = [...annotations].sort((a, b) => b.text.length - a.text.length)
    
    let html = resumeHtml
    const placeholders: Record<string, string> = {}
    
    sorted.forEach((ann, idx) => {
      // Determine visibility & style
      const isDimmed = selectedCategory !== null && ann.category !== selectedCategory
      const isHighlighted = selectedCategory === null || ann.category === selectedCategory
      const categoryColor = CATEGORY_COLORS[ann.category] || '#6b7280'
      const categoryBg = CATEGORY_BG_COLORS[ann.category] || 'rgba(107,114,128,0.15)'

      const markStyle = ann.applied
        ? `background-color: rgba(34, 197, 94, 0.25); border-bottom: 2px solid #22c55e; border-radius: 2px; padding: 1px 2px; cursor: pointer; opacity: ${isDimmed ? 0.3 : 1}; transition: opacity 0.2s, background-color 0.3s;`
        : `background-color: ${isHighlighted ? categoryBg : 'transparent'}; border-bottom: ${isHighlighted ? `2px solid ${categoryColor}` : '2px solid transparent'}; border-radius: 2px; padding: 1px 2px; cursor: pointer; opacity: ${isDimmed ? 0.3 : 1}; transition: opacity 0.2s, background-color 0.3s;`

      // We use a placeholder to avoid replacing inside already-replaced tags
      const placeholderId = `__MARK_PLACEHOLDER_${idx}__`
      const markHtml = `<mark id="mark-${ann.id}" class="annotation-mark" style="${markStyle}" data-ann-id="${ann.id}">${ann.text}</mark>`
      placeholders[placeholderId] = markHtml

      // Replace text outside of HTML tags using a regex
      // Note: This regex is a simple heuristic. A robust HTML parser is ideal, but this works well for standard resumes.
      const escapedText = ann.text.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&')
      const regex = new RegExp(`(?![^<]*>)${escapedText}`, 'i')
      
      // Only replace the first occurrence to roughly match the indexing logic
      html = html.replace(regex, placeholderId)
    })

    // Restore placeholders
    Object.keys(placeholders).forEach(ph => {
      html = html.replace(ph, placeholders[ph])
    })

    return html
  }, [resumeHtml, annotations, selectedCategory])

  // Attach hover events to injected marks
  const containerRef = useRef<HTMLDivElement>(null)
  
  // Use a layout effect or effect to attach listeners to raw injected HTML
  useMemo(() => {
    // This is handled via event delegation on the container
  }, [processedHtml])

  const handleContainerMouseOver = useCallback((e: React.MouseEvent) => {
    const target = e.target as HTMLElement
    if (target.tagName.toLowerCase() === 'mark' && target.classList.contains('annotation-mark')) {
      const annId = target.getAttribute('data-ann-id')
      const ann = annotations.find(a => a.id === annId)
      if (ann) {
        handleMouseEnter(ann, target)
      }
    }
  }, [annotations, handleMouseEnter])

  // Count stats
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

      {/* Resume content */}
      <div className="flex-1 overflow-y-auto p-4 md:p-8 bg-white relative">
        <div
          ref={containerRef}
          className="max-w-full md:max-w-4xl mx-auto font-serif text-gray-900 leading-relaxed resume-document editor-content docx-wrapper overflow-x-auto"
          onMouseOver={handleContainerMouseOver}
          onMouseOut={(e) => {
            const target = e.target as HTMLElement
            if (target.tagName.toLowerCase() === 'mark') {
              handleMouseLeave()
            }
          }}
          style={{
            minHeight: '100%',
          }}
          dangerouslySetInnerHTML={{ __html: processedHtml }}
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
    </div>
  )
}
