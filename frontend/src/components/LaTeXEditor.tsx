/**
 * LaTeX Editor Component with Live Preview
 *
 * Split-pane editor with Monaco (left) and HTML preview (right)
 * Parses basic LaTeX commands for resume formatting
 */
import { useState, useEffect, useRef } from 'react';
import Editor from '@monaco-editor/react';

interface LaTeXEditorProps {
  initialContent?: string;
  onContentChange?: (latex: string) => void;
  onExportPDF?: () => void;
}

const DEFAULT_TEMPLATE = `\\documentclass[11pt,a4paper]{article}
\\usepackage[utf8]{inputenc}
\\usepackage[margin=1in]{geometry}
\\usepackage{enumitem}
\\usepackage{hyperref}

\\begin{document}

\\section*{John Doe}
\\noindent
Email: john.doe@email.com \\quad Phone: (555) 123-4567 \\\\
LinkedIn: linkedin.com/in/johndoe \\quad Location: San Francisco, CA

\\section*{Professional Summary}
Experienced software engineer with 5+ years in full-stack development.
Skilled in React, Node.js, and cloud technologies. Proven track record
of delivering scalable solutions.

\\section*{Experience}

\\textbf{Senior Software Engineer} \\hfill \\textit{Jan 2020 - Present} \\\\
\\textit{TechCorp Inc., San Francisco, CA}
\\begin{itemize}[leftmargin=*]
  \\item Led development of microservices architecture serving 1M+ users
  \\item Improved system performance by 40\\% through optimization
  \\item Mentored team of 5 junior developers
\\end{itemize}

\\textbf{Software Engineer} \\hfill \\textit{Jun 2018 - Dec 2019} \\\\
\\textit{StartupXYZ, Mountain View, CA}
\\begin{itemize}[leftmargin=*]
  \\item Built RESTful APIs using Node.js and Express
  \\item Implemented React frontend with modern best practices
  \\item Reduced page load time by 60\\% through code splitting
\\end{itemize}

\\section*{Education}

\\textbf{Bachelor of Science in Computer Science} \\hfill \\textit{2014 - 2018} \\\\
University of California, Berkeley \\\\
GPA: 3.8/4.0

\\section*{Skills}

\\textbf{Programming Languages:} JavaScript, TypeScript, Python, Java \\\\
\\textbf{Frontend:} React, Vue.js, HTML5, CSS3, Tailwind CSS \\\\
\\textbf{Backend:} Node.js, Express, Django, FastAPI \\\\
\\textbf{Databases:} PostgreSQL, MongoDB, Redis \\\\
\\textbf{DevOps:} Docker, Kubernetes, AWS, CI/CD

\\end{document}`;

// Enhanced LaTeX to HTML parser for resume formatting
function parseLaTeXToHTML(latex: string): string {
  try {
    // Extract content between \begin{document} and \end{document}
    const docMatch = latex.match(/\\begin\{document\}([\s\S]*?)\\end\{document\}/);
    let content = docMatch ? docMatch[1].trim() : latex;

    // Remove preamble commands
    content = content.replace(/\\documentclass.*?\n/g, '');
    content = content.replace(/\\usepackage.*?\n/g, '');
    content = content.replace(/\\noindent\s*/g, '');

    // Parse sections (case-insensitive, handle nested braces better)
    content = content.replace(/\\section\*\{([^}]+)\}/gi, '<h2 class="text-xl font-bold mt-6 mb-3 text-gray-900 border-b-2 border-gray-300 pb-1 uppercase tracking-wide">$1</h2>');
    content = content.replace(/\\subsection\*\{([^}]+)\}/gi, '<h3 class="text-lg font-semibold mt-4 mb-2 text-gray-800">$1</h3>');

    // Parse text formatting (handle nested and multiple instances)
    content = content.replace(/\\textbf\{([^}]*(?:\{[^}]*\}[^}]*)*)\}/g, '<strong class="font-bold text-gray-900">$1</strong>');
    content = content.replace(/\\textit\{([^}]*(?:\{[^}]*\}[^}]*)*)\}/g, '<em class="italic text-gray-700">$1</em>');
    content = content.replace(/\\emph\{([^}]+)\}/g, '<em class="italic text-gray-700">$1</em>');
    content = content.replace(/\\underline\{([^}]+)\}/g, '<u class="underline">$1</u>');

    // Parse special LaTeX characters
    content = content.replace(/\\textbackslash\{\}/g, '\\');
    content = content.replace(/\\%/g, '%');
    content = content.replace(/\\&/g, '&');
    content = content.replace(/\\$/g, '$');
    content = content.replace(/\\#/g, '#');
    content = content.replace(/\\_/g, '_');
    content = content.replace(/\\\{/g, '{');
    content = content.replace(/\\\}/g, '}');

    // Parse hfill (right-aligned dates) - wrap in flex container
    content = content.replace(/([^\n]+)\\hfill([^\n]+)/g, '<div class="flex justify-between items-baseline mb-1"><span>$1</span><span class="text-gray-600 italic">$2</span></div>');

    // Parse line breaks (handle multiple backslashes)
    content = content.replace(/\\\\\\\\/g, '<br/>');
    content = content.replace(/\\\\/g, '<br/>');

    // Parse lists with better spacing
    content = content.replace(/\\begin\{itemize\}(\[.*?\])?/g, '<ul class="list-disc ml-6 my-2 space-y-1.5">');
    content = content.replace(/\\end\{itemize\}/g, '</ul>');
    content = content.replace(/\\begin\{enumerate\}/g, '<ol class="list-decimal ml-6 my-2 space-y-1.5">');
    content = content.replace(/\\end\{enumerate\}/g, '</ol>');
    content = content.replace(/\\item\s*/g, '<li class="text-gray-800 leading-relaxed">');

    // Parse spacing commands
    content = content.replace(/\\quad/g, '<span class="inline-block w-8"></span>');
    content = content.replace(/\\qquad/g, '<span class="inline-block w-16"></span>');
    content = content.replace(/\\,/g, '<span class="inline-block w-1"></span>');
    content = content.replace(/~/g, '&nbsp;');

    // Parse URLs and links (if any)
    content = content.replace(/\\href\{([^}]+)\}\{([^}]+)\}/g, '<a href="$1" class="text-blue-600 underline">$2</a>');
    content = content.replace(/\\url\{([^}]+)\}/g, '<a href="$1" class="text-blue-600 underline">$1</a>');

    // Handle remaining LaTeX commands by removing them
    content = content.replace(/\\[a-zA-Z]+\*?\s*/g, '');

    // Convert paragraph breaks
    const lines = content.split('\n');
    let inList = false;
    let html = '';

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i].trim();

      if (!line) {
        if (!inList) {
          html += '</p><p class="mb-2">';
        }
        continue;
      }

      if (line.includes('<ul') || line.includes('<ol')) {
        inList = true;
      } else if (line.includes('</ul>') || line.includes('</ol>')) {
        inList = false;
      }

      html += line + '\n';
    }

    // Wrap in paragraph tags
    html = '<p class="mb-2">' + html + '</p>';

    // Clean up
    html = html.replace(/<p class="mb-2">\s*<\/p>/g, '');
    html = html.replace(/<p class="mb-2">(<[h|u|o])/g, '$1');
    html = html.replace(/(<\/[h|u|o][^>]*>)<\/p>/g, '$1');
    html = html.replace(/<br\/>\s*<\/p>/g, '</p>');
    html = html.replace(/<p class="mb-2">\s*<br\/>/g, '<p class="mb-2">');

    return html;
  } catch (err) {
    console.error('Parse error:', err);
    return `<div class="text-red-600 p-4 bg-red-50 rounded-lg">
      <strong>Parse Error:</strong><br/>
      ${err instanceof Error ? err.message : 'Failed to parse LaTeX'}
    </div>`;
  }
}

export const LaTeXEditor: React.FC<LaTeXEditorProps> = ({
  initialContent = DEFAULT_TEMPLATE,
  onContentChange,
  onExportPDF,
}) => {
  const [latexCode, setLatexCode] = useState(initialContent);
  const [renderedHTML, setRenderedHTML] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isRendering, setIsRendering] = useState(false);
  const previewRef = useRef<HTMLDivElement>(null);

  // Render LaTeX to HTML
  useEffect(() => {
    const renderLaTeX = () => {
      if (!latexCode.trim()) {
        setRenderedHTML('<p class="text-gray-500">Enter LaTeX code to see preview...</p>');
        return;
      }

      setIsRendering(true);
      setError(null);

      try {
        const html = parseLaTeXToHTML(latexCode);
        setRenderedHTML(html);
      } catch (err) {
        console.error('LaTeX rendering error:', err);
        setError(err instanceof Error ? err.message : 'Failed to render LaTeX');
        setRenderedHTML(`<div class="text-red-600 p-4 bg-red-50 rounded">
          <strong>LaTeX Error:</strong><br/>
          ${err instanceof Error ? err.message : 'Unknown error'}
        </div>`);
      } finally {
        setIsRendering(false);
      }
    };

    // Debounce rendering
    const timer = setTimeout(renderLaTeX, 300);
    return () => clearTimeout(timer);
  }, [latexCode]);

  const handleEditorChange = (value: string | undefined) => {
    const newValue = value || '';
    setLatexCode(newValue);
    onContentChange?.(newValue);
  };

  const handleExportPDF = async () => {
    if (previewRef.current) {
      try {
        // Use html2pdf.js to convert preview to PDF
        const html2pdf = (await import('html2pdf.js')).default;

        const opt = {
          margin: [0.5, 0.5],
          filename: 'resume.pdf',
          image: { type: 'jpeg', quality: 0.98 },
          html2canvas: { scale: 2 },
          jsPDF: { unit: 'in', format: 'letter', orientation: 'portrait' }
        };

        html2pdf().set(opt).from(previewRef.current).save();
        onExportPDF?.();
      } catch (err) {
        console.error('PDF export error:', err);
        alert('Failed to export PDF. Please try again.');
      }
    }
  };

  const handleDownloadLaTeX = () => {
    const blob = new Blob([latexCode], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'resume.tex';
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="h-full flex flex-col bg-gray-50">
      {/* Toolbar */}
      <div className="bg-white border-b border-gray-300 px-4 py-2.5 flex items-center justify-between shadow-sm">
        <div className="flex items-center gap-4">
          <h2 className="text-lg font-semibold text-gray-800">LaTeX Editor</h2>
          {isRendering && (
            <span className="text-sm text-blue-600 animate-pulse">● Rendering...</span>
          )}
          {error && (
            <span className="text-sm text-red-600">⚠ Syntax Error</span>
          )}
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={handleDownloadLaTeX}
            className="px-4 py-2 bg-gray-600 text-white text-sm rounded-lg hover:bg-gray-700 transition flex items-center gap-2"
          >
            📄 Download .tex
          </button>
          <button
            onClick={handleExportPDF}
            className="px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 transition flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
            disabled={!!error}
          >
            📥 Export PDF
          </button>
        </div>
      </div>

      {/* Split Pane */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left: Monaco Editor */}
        <div className="w-1/2 border-r border-gray-300 bg-white">
          <Editor
            height="100%"
            defaultLanguage="latex"
            value={latexCode}
            onChange={handleEditorChange}
            theme="vs-light"
            options={{
              fontSize: 14,
              lineNumbers: 'on',
              minimap: { enabled: false },
              scrollBeyondLastLine: false,
              wordWrap: 'on',
              automaticLayout: true,
              tabSize: 2,
              padding: { top: 16, bottom: 16 },
            }}
          />
        </div>

        {/* Right: Live Preview */}
        <div className="w-1/2 bg-gray-100 overflow-auto">
          <div className="p-8">
            <div
              ref={previewRef}
              className="bg-white shadow-lg p-12 max-w-[8.5in] mx-auto leading-relaxed"
              style={{
                minHeight: '11in',
                fontFamily: '"Times New Roman", Times, serif',
                fontSize: '11pt',
                lineHeight: '1.4'
              }}
              dangerouslySetInnerHTML={{ __html: renderedHTML }}
            />
          </div>
        </div>
      </div>

      {/* Status Bar */}
      <div className="bg-white border-t border-gray-300 px-4 py-2 text-xs text-gray-600 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <span>Lines: {latexCode.split('\n').length}</span>
          <span>Characters: {latexCode.length}</span>
        </div>
        <div className="flex items-center gap-4">
          <span className="text-gray-500">💡 Edit LaTeX on the left, see preview on the right</span>
        </div>
      </div>
    </div>
  );
};

export default LaTeXEditor;
