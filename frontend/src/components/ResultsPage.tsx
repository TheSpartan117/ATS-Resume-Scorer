/**
 * Results page — split-screen layout.
 *
 * Left 70 %: DOCX resume viewer with annotated highlights.
 * Right 30 %: Scoring sidebar (score card + category breakdown).
 */
import { useLocation, useNavigate } from 'react-router-dom'
import { useEffect, useState, useCallback } from 'react'
import type { UploadResponse } from '../types/resume'
import { ModeIndicator } from './ModeIndicator'
import { DownloadMenu } from './DownloadMenu'
import EnhancedResultsDisplay from './EnhancedResultsDisplay'
import DocxResumeViewer from './DocxResumeViewer'
import UserMenu from './UserMenu'
import { buildAnnotations } from '../utils/buildAnnotations'
import type { Annotation } from '../utils/buildAnnotations'
import PdfResumeViewer from './PdfResumeViewer'

export default function ResultsPage() {
  const location = useLocation()
  const navigate = useNavigate()
  const result = location.state?.result as UploadResponse | undefined

  // File states for viewer
  const [docxBlob, setDocxBlob] = useState<Blob | null>(null)
  const [pdfUrl, setPdfUrl] = useState<string | null>(null)
  const [fileType, setFileType] = useState<'pdf' | 'docx' | null>(null)

  // Resume plain text (for download / annotation matching)
  const [resumeText, setResumeText] = useState('')
  const [annotations, setAnnotations] = useState<Annotation[]>([])
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null)

  // Undo / redo stacks
  const [undoStack, setUndoStack] = useState<string[]>([])
  const [redoStack, setRedoStack] = useState<string[]>([])
  const [undoAnnotationStack, setUndoAnnotationStack] = useState<Annotation[][]>([])
  const [redoAnnotationStack, setRedoAnnotationStack] = useState<Annotation[][]>([])

  useEffect(() => {
    if (!result) {
      navigate('/', { replace: true })
      return
    }

    // Build plain text for annotations
    const text = buildResumeContent(result)
    setResumeText(text)

    // Build initial annotations from plain text
    const anns = buildAnnotations(text, result.score.breakdown, result.score.issues)
    setAnnotations(anns)

    // Fetch the DOCX blob or PDF URL for the viewer
    const originalUrl = result.originalFileUrl
    const docxUrl = result.docxFileUrl
    
    // We prefer PDF if it was originally a PDF for exact layout matches
    const isOriginalPdf = result.fileName?.toLowerCase().endsWith('.pdf') || originalUrl?.toLowerCase().endsWith('.pdf')
    
    if (isOriginalPdf && originalUrl) {
      // It's a PDF - use PDF viewer
      setFileType('pdf')
      setPdfUrl(originalUrl)
    } else if (docxUrl || originalUrl) {
      // It's a DOCX - fetch blob for docx-preview
      const fetchUrl = docxUrl || originalUrl
      setFileType('docx')
      fetch(fetchUrl!)
        .then(res => {
          if (!res.ok) throw new Error(`HTTP ${res.status}`)
          return res.blob()
        })
        .then(blob => {
          setDocxBlob(blob)
        })
        .catch(err => {
          console.error('Failed to fetch docx file:', err)
        })
    }    
  }, [result, navigate])

  // ── Build resume text from parsed data ──────────────────────────
  const buildResumeContent = (r: UploadResponse): string => {
    const parts: string[] = []

    if (r.contact) {
      if (r.contact.name) parts.push(r.contact.name)
      const contactLine = [r.contact.email, r.contact.phone, r.contact.location, r.contact.linkedin]
        .filter(Boolean)
        .join(' • ')
      if (contactLine) parts.push(contactLine)
      parts.push('')
    }

    if ((r as any).summary) {
      parts.push('SUMMARY')
      parts.push((r as any).summary)
      parts.push('')
    }

    if (r.experience && r.experience.length > 0) {
      parts.push('PROFESSIONAL EXPERIENCE')
      parts.push('')
      r.experience.forEach((exp: any) => {
        const titleLine = [exp.title, exp.company].filter(Boolean).join(' — ')
        if (titleLine) parts.push(titleLine)
        const dateLine = [exp.startDate, exp.endDate].filter(Boolean).join(' – ')
        const metaLine = [dateLine, exp.location].filter(Boolean).join(' | ')
        if (metaLine) parts.push(metaLine)
        if (exp.description) {
          parts.push(exp.description)
        }
        parts.push('')
      })
    }

    if (r.education && r.education.length > 0) {
      parts.push('EDUCATION')
      parts.push('')
      r.education.forEach((edu: any) => {
        if (edu.degree) parts.push(edu.degree)
        const instLine = [edu.institution, edu.location].filter(Boolean).join(', ')
        if (instLine) parts.push(instLine)
        if (edu.graduationDate) parts.push(edu.graduationDate)
        if (edu.gpa) parts.push(`GPA: ${edu.gpa}`)
        parts.push('')
      })
    }

    if (r.skills && r.skills.length > 0) {
      parts.push('SKILLS')
      parts.push(r.skills.join(', '))
      parts.push('')
    }

    if (r.certifications && r.certifications.length > 0) {
      parts.push('CERTIFICATIONS')
      r.certifications.forEach((cert: any) => {
        const cLine = [cert.name, cert.issuer].filter(Boolean).join(' — ')
        if (cLine) parts.push(cLine)
        if (cert.date) parts.push(cert.date)
      })
      parts.push('')
    }

    return parts.join('\n')
  }

  // ── Text change handler (with undo tracking) ───────────────────
  const handleTextChange = useCallback((newText: string) => {
    setUndoStack(prev => [...prev, resumeText])
    setUndoAnnotationStack(prev => [...prev, annotations])
    setRedoStack([])
    setRedoAnnotationStack([])
    setResumeText(newText)
  }, [resumeText, annotations])

  const handleAnnotationsChange = useCallback((newAnnotations: Annotation[]) => {
    setAnnotations(newAnnotations)
  }, [])

  // ── Undo / Redo ────────────────────────────────────────────────
  const handleUndo = useCallback(() => {
    if (undoStack.length === 0) return
    const prevText = undoStack[undoStack.length - 1]
    const prevAnnotations = undoAnnotationStack[undoAnnotationStack.length - 1]

    setRedoStack(prev => [...prev, resumeText])
    setRedoAnnotationStack(prev => [...prev, annotations])
    setUndoStack(prev => prev.slice(0, -1))
    setUndoAnnotationStack(prev => prev.slice(0, -1))
    setResumeText(prevText)
    if (prevAnnotations) setAnnotations(prevAnnotations)
  }, [undoStack, undoAnnotationStack, resumeText, annotations])

  const handleRedo = useCallback(() => {
    if (redoStack.length === 0) return
    const nextText = redoStack[redoStack.length - 1]
    const nextAnnotations = redoAnnotationStack[redoAnnotationStack.length - 1]

    setUndoStack(prev => [...prev, resumeText])
    setUndoAnnotationStack(prev => [...prev, annotations])
    setRedoStack(prev => prev.slice(0, -1))
    setRedoAnnotationStack(prev => prev.slice(0, -1))
    setResumeText(nextText)
    if (nextAnnotations) setAnnotations(nextAnnotations)
  }, [redoStack, redoAnnotationStack, resumeText, annotations])

  // ── Category selection handler ─────────────────────────────────
  const handleCategorySelect = useCallback((categoryName: string | null) => {
    setSelectedCategory(prev => prev === categoryName ? null : categoryName)
  }, [])

  if (!result) return null

  return (
    <div className="h-screen w-screen flex flex-col bg-gray-100 overflow-hidden">
      {/* ── Top Header Bar ─────────────────────────────────────── */}
      <header className="flex items-center justify-between px-4 py-2.5 bg-white border-b border-gray-200 shadow-sm flex-shrink-0 z-10">
        <div className="flex items-center gap-4">
          <button
            onClick={() => navigate('/')}
            className="text-blue-600 hover:text-blue-800 font-medium flex items-center gap-1 text-sm"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            Back
          </button>
          <div className="h-5 w-px bg-gray-300" />
          <h1 className="text-sm font-semibold text-gray-800 truncate max-w-xs">
            {result.fileName}
          </h1>
        </div>

        <div className="flex items-center gap-2">
          {/* Undo / Redo */}
          <div className="flex items-center border border-gray-200 rounded-lg overflow-hidden">
            <button
              onClick={handleUndo}
              disabled={undoStack.length === 0}
              className="px-3 py-1.5 text-sm text-gray-700 hover:bg-gray-100 disabled:opacity-30 disabled:cursor-not-allowed transition-colors flex items-center gap-1"
              title="Undo (Ctrl+Z)"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h10a5 5 0 015 5v2M3 10l4-4M3 10l4 4" />
              </svg>
              Undo
            </button>
            <div className="w-px h-6 bg-gray-200" />
            <button
              onClick={handleRedo}
              disabled={redoStack.length === 0}
              className="px-3 py-1.5 text-sm text-gray-700 hover:bg-gray-100 disabled:opacity-30 disabled:cursor-not-allowed transition-colors flex items-center gap-1"
              title="Redo (Ctrl+Y)"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 10H11a5 5 0 00-5 5v2M21 10l-4-4M21 10l-4 4" />
              </svg>
              Redo
            </button>
          </div>

          <div className="h-5 w-px bg-gray-300" />

          <DownloadMenu
            resumeContent={resumeText}
            resumeName={result.contact?.name || 'Resume'}
            resumeData={result}
            scoreData={result.score}
            mode={result.scoringMode || 'quality_coach'}
            role={result.role || 'software_engineer'}
            level={result.level || 'mid'}
          />

          <UserMenu />
        </div>
      </header>

      {/* ── Main Split Layout ─────────────────────────────────── */}
      <div className="flex-1 flex overflow-hidden">
        {/* LEFT: Resume Viewer (70%) */}
        <div className="w-[70%] min-w-[70%] max-w-[70%] border-r border-gray-200 bg-gray-100 flex flex-col overflow-hidden">
          {fileType === 'pdf' && pdfUrl ? (
            <PdfResumeViewer
              pdfUrl={pdfUrl}
              annotations={annotations}
              selectedCategory={selectedCategory}
              onAnnotationsChange={setAnnotations}
              onTextChange={handleTextChange}
            />
          ) : fileType === 'docx' && docxBlob ? (
            <DocxResumeViewer
              docxBlob={docxBlob}
              annotations={annotations}
              selectedCategory={selectedCategory}
              onAnnotationsChange={setAnnotations}
              onTextChange={handleTextChange}
            />
          ) : (
             <div className="flex h-full items-center justify-center">
               <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
             </div>
          )}
        </div>

        {/* RIGHT: Scoring Sidebar (30%) */}
        <div className="w-[30%] min-w-[30%] max-w-[30%] flex flex-col overflow-hidden bg-white">
          <div className="flex-1 overflow-y-auto sidebar-scroll">
            <div className="p-4 space-y-4">
              {/* Score Circle */}
              <ModeIndicator
                mode={(result.scoringMode || result.score.mode || 'quality_coach') as any}
                score={result.score.overallScore}
                keywordDetails={result.score.keywordDetails}
                breakdown={result.score.breakdown}
                autoReject={result.score.autoReject}
              />

              {/* Category Breakdown */}
              <div className="bg-white rounded-lg">
                <EnhancedResultsDisplay
                  overallScore={result.score.overallScore}
                  breakdown={result.score.breakdown}
                  issues={result.score.issues}
                  strengths={result.score.strengths}
                  selectedCategory={selectedCategory}
                  onCategorySelect={handleCategorySelect}
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
