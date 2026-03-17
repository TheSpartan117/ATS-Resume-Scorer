/**
 * PdfResumeViewer — renders a PDF file faithfully using react-pdf,
 * and overlays annotation highlights on the rendered text layer.
 */
import { useEffect, useRef, useState, useCallback } from 'react'
import { Document, Page, pdfjs } from 'react-pdf'
import 'react-pdf/dist/Page/AnnotationLayer.css'
import 'react-pdf/dist/Page/TextLayer.css'
import type { Annotation } from '../utils/buildAnnotations'
import { CATEGORY_COLORS, CATEGORY_BG_COLORS } from '../utils/buildAnnotations'
import AnnotationTooltip from './AnnotationTooltip'

// Configure pdfjs worker
pdfjs.GlobalWorkerOptions.workerSrc = new URL(
  'pdfjs-dist/build/pdf.worker.min.mjs',
  import.meta.url,
).toString()

interface PdfResumeViewerProps {
  pdfUrl: string
  annotations: Annotation[]
  selectedCategory: string | null
  onAnnotationsChange: (annotations: Annotation[]) => void
  onTextChange?: (newText: string) => void
}

export default function PdfResumeViewer({
  pdfUrl,
  annotations,
  selectedCategory,
  onAnnotationsChange,
}: PdfResumeViewerProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const [numPages, setNumPages] = useState<number>(0)
  const [scale, setScale] = useState(1.2)
  const [hoveredAnnotation, setHoveredAnnotation] = useState<Annotation | null>(null)
  const [anchorRect, setAnchorRect] = useState<DOMRect | null>(null)
  const isTooltipHovered = useRef(false)
  const dismissTimer = useRef<ReturnType<typeof setTimeout> | null>(null)
  
  // Track text layer renders to trigger annotation injection
  const [textLayerRenderedPages, setTextLayerRenderedPages] = useState<Set<number>>(new Set())

  // Resize observer to auto-fit width
  useEffect(() => {
    if (!containerRef.current) return
    const resizeObserver = new ResizeObserver((entries) => {
      for (let entry of entries) {
        // Calculate scale to fit container width, leaving some padding
        const newScale = Math.max(0.5, (entry.contentRect.width - 40) / 600) // 600 is approx base width of US Letter
        setScale(newScale)
      }
    })
    resizeObserver.observe(containerRef.current)
    return () => resizeObserver.disconnect()
  }, [])

  function onDocumentLoadSuccess({ numPages }: { numPages: number }) {
    setNumPages(numPages)
    setTextLayerRenderedPages(new Set())
  }

  function onTextLayerRendered(pageNumber: number) {
    setTextLayerRenderedPages(prev => {
      const next = new Set(prev)
      next.add(pageNumber)
      return next
    })
  }

  // ── Inject annotation highlights into rendered TextLayer ────────────
  useEffect(() => {
    if (!containerRef.current || annotations.length === 0 || textLayerRenderedPages.size === 0) return

    // Remove any previous highlights
    containerRef.current.querySelectorAll('mark.annotation-highlight').forEach(el => {
      const parent = el.parentNode
      if (parent) {
        parent.replaceChild(document.createTextNode(el.textContent || ''), el)
        parent.normalize()
      }
    })

    // Walk all React-PDF text layer nodes
    const textLayers = containerRef.current.querySelectorAll('.react-pdf__Page__textContent')
    
    textLayers.forEach(layer => {
      const walker = document.createTreeWalker(
        layer,
        NodeFilter.SHOW_TEXT,
        null,
      )

      // Collect text nodes
      const textNodes: Text[] = []
      let node
      while ((node = walker.nextNode())) {
        textNodes.push(node as Text)
      }

      // Sort annotations by length
      const sortedAnns = [...annotations].sort((a, b) => b.text.length - a.text.length)
      const matched = new Set<string>()

      for (const ann of sortedAnns) {
        if (matched.has(ann.id)) continue

        for (let i = 0; i < textNodes.length; i++) {
          const textNode = textNodes[i]
          if (!textNode.parentNode) continue
          const content = textNode.nodeValue || ''
          const idx = content.indexOf(ann.text)
          if (idx === -1) continue

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
            // Use an opaque background to hide the underlying PDF text
            mark.style.cssText = `background-color: #dcfce7; color: #166534; border-bottom: 2px solid #22c55e; border-radius: 4px; padding: 0 4px; box-shadow: 0 1px 2px rgba(0,0,0,0.1); cursor: pointer; opacity: ${isDimmed ? 0.3 : 1}; transition: opacity 0.2s, background-color 0.3s; pointer-events: auto !important; position: relative; z-index: 100; display: inline-block; line-height: 1.2;`
          } else {
            // Unapplied annotations: transparent text, so only the original PDF text is visible,
            // with a background color and bottom border for the highlight effect.
            mark.style.cssText = `color: transparent; background-color: ${isHighlighted ? categoryBg : 'transparent'}; border-bottom: ${isHighlighted ? `2px solid ${categoryColor}` : '2px solid transparent'}; border-radius: 2px; cursor: pointer; opacity: ${isDimmed ? 0.3 : 1}; transition: opacity 0.2s, background-color 0.3s; pointer-events: auto !important;`
          }
          
          const parent = textNode.parentNode
          // Fix react-pdf overlap behavior by making parent pointer-events auto
          if (parent instanceof HTMLElement) {
            parent.style.pointerEvents = 'auto'
          }

          const afterNode = document.createTextNode(after)

          textNode.nodeValue = before
          parent.insertBefore(mark, textNode.nextSibling)
          parent.insertBefore(afterNode, mark.nextSibling)

          textNodes.splice(i + 1, 0, afterNode)
          matched.add(ann.id)
          break
        }
      }
    })
  }, [textLayerRenderedPages, annotations, selectedCategory])

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

    const mark = containerRef.current.querySelector(`mark[data-ann-id="${annotation.id}"]`)
    if (mark) {
      const textNode = document.createTextNode(replacement)
      mark.parentNode?.replaceChild(textNode, mark)
      textNode.parentNode?.normalize()
    }

    // Since it's a PDF, we don't strictly "edit" the underlying document, 
    // but we can update the plain text state for exports if needed
    
    // We update annotations
    const updatedAnnotations = annotations.map(ann => {
      if (ann.id === annotation.id) {
        return { ...ann, text: replacement, applied: true }
      }
      return ann
    })

    onAnnotationsChange(updatedAnnotations)
    setHoveredAnnotation(null)
    setAnchorRect(null)
  }, [annotations, onAnnotationsChange])

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

      {/* PDF content */}
      <div 
        ref={containerRef}
        className="flex-1 overflow-y-auto bg-gray-200 relative p-4 flex flex-col items-center"
        onMouseOver={handleContainerMouseOver}
        onMouseOut={handleContainerMouseOut}
      >
        <Document
          file={pdfUrl}
          onLoadSuccess={onDocumentLoadSuccess}
          className="flex flex-col gap-4 items-center"
          loading={
            <div className="flex items-center justify-center p-12">
              <div className="animate-spin rounded-full h-12 w-12 border-4 border-blue-500 border-t-transparent" />
            </div>
          }
        >
          {Array.from(new Array(numPages), (_, index) => (
            <div key={`page_${index + 1}`} className="shadow-lg bg-white">
              <Page
                pageNumber={index + 1}
                scale={scale}
                renderTextLayer={true}
                renderAnnotationLayer={false}
                onGetTextSuccess={() => onTextLayerRendered(index + 1)}
              />
            </div>
          ))}
        </Document>
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
      
      <style>{`
        /* react-pdf text layer interaction setup */
        .react-pdf__Page__textContent {
          pointer-events: none; /* Let clicks pass through empty space */
        }
        
        .react-pdf__Page__textContent > span {
          pointer-events: auto; /* Allow hovering text nodes */
          /* Ensure text spans don't clip our opaque highlight boxes */
          overflow: visible !important;
        }
        
        mark.annotation-highlight {
          position: relative;
          z-index: 100;
          display: inline-block;
          line-height: 1.2;
        }
        
        mark.annotation-highlight:hover {
          filter: brightness(0.92);
        }
      `}</style>
    </div>
  )
}
