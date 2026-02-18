"""
Convert documents (PDF/DOCX) to rich HTML with formatting preserved.

This module converts resume files to editable HTML that preserves:
- Text formatting (bold, italic, underline)
- Document structure (headings, paragraphs, lists)
- Tables and layout
- Fonts and styling
"""
import io
from typing import Dict
from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
import fitz  # PyMuPDF


def docx_to_html(docx_bytes: bytes) -> str:
    """
    Convert DOCX to rich HTML with formatting preserved.

    Args:
        docx_bytes: DOCX file content as bytes

    Returns:
        HTML string with formatting preserved
    """
    doc = Document(io.BytesIO(docx_bytes))
    html_parts = []

    # Add basic styling
    html_parts.append("""
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto; }
        h1 { font-size: 24px; font-weight: bold; margin: 20px 0 10px 0; }
        h2 { font-size: 18px; font-weight: bold; margin: 15px 0 8px 0; }
        h3 { font-size: 16px; font-weight: bold; margin: 12px 0 6px 0; }
        p { margin: 8px 0; }
        ul, ol { margin: 8px 0; padding-left: 30px; }
        table { border-collapse: collapse; width: 100%; margin: 10px 0; }
        td { padding: 8px; vertical-align: top; }
        .center { text-align: center; }
        .right { text-align: right; }
    </style>
    """)

    # Process paragraphs
    for para in doc.paragraphs:
        if not para.text.strip():
            html_parts.append("<p>&nbsp;</p>")
            continue

        # Determine if paragraph is a heading
        if para.style.name.startswith('Heading'):
            level = para.style.name.replace('Heading ', '').strip()
            if level.isdigit():
                tag = f"h{min(int(level), 6)}"
            else:
                tag = "h2"
        else:
            tag = "p"

        # Get alignment
        align_class = ""
        if para.alignment == WD_ALIGN_PARAGRAPH.CENTER:
            align_class = ' class="center"'
        elif para.alignment == WD_ALIGN_PARAGRAPH.RIGHT:
            align_class = ' class="right"'

        # Build paragraph with inline formatting
        text_html = ""
        for run in para.runs:
            text = run.text
            if not text:
                continue

            # Apply formatting
            if run.bold:
                text = f"<strong>{text}</strong>"
            if run.italic:
                text = f"<em>{text}</em>"
            if run.underline:
                text = f"<u>{text}</u>"

            # Apply font size if different
            if run.font.size:
                size = run.font.size.pt
                if size > 14:
                    text = f'<span style="font-size: {size}px;">{text}</span>'

            text_html += text

        html_parts.append(f"<{tag}{align_class}>{text_html}</{tag}>")

    # Process tables
    for table in doc.tables:
        html_parts.append("<table>")
        for row in table.rows:
            html_parts.append("<tr>")
            for cell in row.cells:
                cell_html = ""
                for para in cell.paragraphs:
                    if para.text.strip():
                        # Build cell content with formatting
                        text_html = ""
                        for run in para.runs:
                            text = run.text
                            if run.bold:
                                text = f"<strong>{text}</strong>"
                            if run.italic:
                                text = f"<em>{text}</em>"
                            text_html += text
                        cell_html += text_html + "<br>"
                html_parts.append(f"<td>{cell_html}</td>")
            html_parts.append("</tr>")
        html_parts.append("</table>")

    return "".join(html_parts)


def pdf_to_html(pdf_bytes: bytes) -> str:
    """
    Convert PDF to rich HTML (simplified - extracts text with basic formatting).

    Args:
        pdf_bytes: PDF file content as bytes

    Returns:
        HTML string with basic formatting
    """
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    html_parts = []

    # Add basic styling
    html_parts.append("""
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto; }
        h1 { font-size: 24px; font-weight: bold; margin: 20px 0 10px 0; }
        h2 { font-size: 18px; font-weight: bold; margin: 15px 0 8px 0; }
        p { margin: 8px 0; }
    </style>
    """)

    for page in doc:
        # Extract text blocks with basic formatting detection
        blocks = page.get_text("dict")["blocks"]

        for block in blocks:
            if block.get("type") == 0:  # Text block
                for line in block.get("lines", []):
                    line_text = ""
                    for span in line.get("spans", []):
                        text = span.get("text", "")
                        size = span.get("size", 12)
                        flags = span.get("flags", 0)

                        # Check for bold (flag 16) and italic (flag 2)
                        is_bold = flags & 16
                        is_italic = flags & 2

                        if is_bold:
                            text = f"<strong>{text}</strong>"
                        if is_italic:
                            text = f"<em>{text}</em>"

                        line_text += text

                    if line_text.strip():
                        # Detect headings by font size
                        avg_size = sum(s.get("size", 12) for s in line.get("spans", [])) / max(len(line.get("spans", [])), 1)
                        if avg_size > 16:
                            html_parts.append(f"<h1>{line_text}</h1>")
                        elif avg_size > 14:
                            html_parts.append(f"<h2>{line_text}</h2>")
                        else:
                            html_parts.append(f"<p>{line_text}</p>")

    doc.close()
    return "".join(html_parts)
