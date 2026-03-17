/**
 * Floating tooltip shown when hovering an annotated phrase in the resume viewer.
 *
 * Positioned near the highlighted element using a portal + getBoundingClientRect.
 */
import { useEffect, useRef, useState } from 'react'
import { createPortal } from 'react-dom'
import type { Annotation } from '../utils/buildAnnotations'
import { CATEGORY_COLORS } from '../utils/buildAnnotations'

interface AnnotationTooltipProps {
  annotation: Annotation
  anchorRect: DOMRect
  onApply?: (annotation: Annotation, replacement: string) => void
  onDismiss: () => void
  onTooltipMouseEnter?: () => void
  onTooltipMouseLeave?: () => void
}

export default function AnnotationTooltip({
  annotation,
  anchorRect,
  onApply,
  onDismiss,
  onTooltipMouseEnter,
  onTooltipMouseLeave,
}: AnnotationTooltipProps) {
  const tooltipRef = useRef<HTMLDivElement>(null)
  const [position, setPosition] = useState({ top: 0, left: 0 })

  useEffect(() => {
    if (!tooltipRef.current) return

    const tooltipRect = tooltipRef.current.getBoundingClientRect()
    const viewportWidth = window.innerWidth
    const viewportHeight = window.innerHeight

    let top = anchorRect.bottom + 8
    let left = anchorRect.left + anchorRect.width / 2 - tooltipRect.width / 2

    // Keep within viewport horizontally
    if (left < 12) left = 12
    if (left + tooltipRect.width > viewportWidth - 12) {
      left = viewportWidth - tooltipRect.width - 12
    }

    // If tooltip would go below viewport, show above
    if (top + tooltipRect.height > viewportHeight - 12) {
      top = anchorRect.top - tooltipRect.height - 8
    }

    setPosition({ top, left })
  }, [anchorRect])

  // Dismiss on Escape
  useEffect(() => {
    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onDismiss()
    }
    window.addEventListener('keydown', handleEsc)
    return () => window.removeEventListener('keydown', handleEsc)
  }, [onDismiss])

  const categoryColor = CATEGORY_COLORS[annotation.category] || '#6b7280'

  const severityBadge = {
    critical: { bg: 'bg-red-100', text: 'text-red-700', label: 'Critical' },
    warning: { bg: 'bg-amber-100', text: 'text-amber-700', label: 'Warning' },
    suggestion: { bg: 'bg-blue-100', text: 'text-blue-700', label: 'Suggestion' },
  }[annotation.severity]

  return createPortal(
    <div
      ref={tooltipRef}
      className="annotation-tooltip"
      style={{
        position: 'fixed',
        top: position.top,
        left: position.left,
        zIndex: 9999,
      }}
      onMouseEnter={onTooltipMouseEnter}
      onMouseLeave={onTooltipMouseLeave}
    >
      <div className="bg-white rounded-xl shadow-2xl border border-gray-200 p-4 max-w-sm w-80 animate-tooltip-in">
        {/* Category bar */}
        <div className="flex items-center gap-2 mb-2">
          <div
            className="w-3 h-3 rounded-full flex-shrink-0"
            style={{ backgroundColor: categoryColor }}
          />
          <span className="text-xs font-semibold text-gray-500 uppercase tracking-wide">
            {annotation.category}
          </span>
          <span className={`ml-auto px-2 py-0.5 rounded-full text-xs font-bold ${severityBadge.bg} ${severityBadge.text}`}>
            {severityBadge.label}
          </span>
        </div>

        {/* Issue description */}
        <p className="text-sm text-gray-800 leading-relaxed mb-3">
          {annotation.issue}
        </p>

        {/* Highlighted phrase */}
        <div className="bg-gray-50 rounded-lg p-2 mb-3 border border-gray-100">
          <div className="text-xs text-gray-500 font-medium mb-1">Found in resume:</div>
          <div className="text-sm font-mono text-gray-900 break-words">
            "{annotation.text}"
          </div>
        </div>

        {/* Suggestion */}
        {annotation.suggestion && !annotation.applied && (
          <div className="space-y-2">
            <div className="bg-green-50 rounded-lg p-2 border border-green-200">
              <div className="text-xs text-green-600 font-medium mb-1">💡 Suggestion:</div>
              <div className="text-sm text-green-800">{annotation.suggestion}</div>
            </div>

            {onApply && annotation.replacement && (
              <button
                onClick={() => onApply(annotation, annotation.replacement!)}
                className="w-full py-2 px-3 bg-gradient-to-r from-green-500 to-emerald-600 text-white rounded-lg font-medium text-sm hover:from-green-600 hover:to-emerald-700 transition-all shadow-sm hover:shadow-md active:scale-[0.98]"
              >
                ✓ Apply Fix
              </button>
            )}
          </div>
        )}

        {/* Applied state */}
        {annotation.applied && (
          <div className="flex items-center gap-2 text-green-700 bg-green-50 rounded-lg p-2 border border-green-200">
            <span className="text-lg">✓</span>
            <span className="text-sm font-medium">Fix applied</span>
          </div>
        )}
      </div>
    </div>,
    document.body
  )
}
