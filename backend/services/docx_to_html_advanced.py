"""
Advanced DOCX to HTML conversion that preserves images, colors, and layout.
"""
import io
import base64
import logging
from docx import Document
from docx.oxml import parse_xml
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from PIL import Image

logger = logging.getLogger(__name__)


def docx_to_html_advanced(docx_bytes: bytes) -> str:
    """
    Convert DOCX to HTML preserving images, colors, tables, and layout.

    Args:
        docx_bytes: DOCX file content as bytes

    Returns:
        HTML string with full formatting preserved
    """
    try:
        doc = Document(io.BytesIO(docx_bytes))
        html_parts = []

        # Add wrapper and styles
        html_parts.append("""
        <div class="resume-document" style="
            font-family: Calibri, Arial, sans-serif;
            font-size: 11pt;
            line-height: 1.4;
            color: #000;
            max-width: 850px;
            margin: 0 auto;
        ">
        """)

        # Process document elements
        for element in doc.element.body:
            if element.tag.endswith('p'):  # Paragraph
                html_parts.append(_process_paragraph(element))
            elif element.tag.endswith('tbl'):  # Table
                html_parts.append(_process_table(element, doc))

        # Extract and embed images
        for rel in doc.part.rels.values():
            if "image" in rel.target_ref:
                try:
                    image_data = rel.target_part.blob
                    # Convert to base64
                    img_b64 = base64.b64encode(image_data).decode('utf-8')

                    # Determine image type
                    img_format = 'jpeg'
                    if image_data[:4] == b'\x89PNG':
                        img_format = 'png'

                    html_parts.append(f'''
                    <div style="text-align: center; margin: 10px 0;">
                        <img src="data:image/{img_format};base64,{img_b64}"
                             style="max-width: 150px; border-radius: 50%;" />
                    </div>
                    ''')
                except Exception as e:
                    logger.warning(f"Failed to extract image: {e}")

        html_parts.append("</div>")

        return "".join(html_parts)

    except Exception as e:
        logger.error(f"Advanced DOCX conversion failed: {e}")
        raise


def _process_paragraph(p_element) -> str:
    """Process a paragraph element with full formatting."""
    from docx.text.paragraph import Paragraph
    from docx.oxml.shared import qn

    # Get paragraph properties
    p_style = ""
    if p_element.pPr is not None:
        # Check alignment
        jc = p_element.pPr.find(qn('w:jc'))
        if jc is not None:
            align = jc.get(qn('w:val'))
            if align == 'center':
                p_style += "text-align: center;"
            elif align == 'right':
                p_style += "text-align: right;"

        # Check shading (background color)
        shd = p_element.pPr.find(qn('w:shd'))
        if shd is not None:
            fill = shd.get(qn('w:fill'))
            if fill and fill != 'auto':
                p_style += f"background-color: #{fill}; padding: 8px;"

    # Process runs (text with formatting)
    text_parts = []
    for run in p_element.findall(qn('w:r')):
        text_parts.append(_process_run(run))

    text_content = "".join(text_parts)

    # Determine tag based on style
    tag = "p"
    style_attr = f' style="{p_style}"' if p_style else ""

    if not text_content.strip():
        return "<br>"

    return f"<{tag}{style_attr}>{text_content}</{tag}>"


def _process_run(r_element) -> str:
    """Process a run (text with formatting)."""
    from docx.oxml.shared import qn

    # Get text
    text_parts = []
    for t in r_element.findall(qn('w:t')):
        text_parts.append(t.text if t.text else "")

    text = "".join(text_parts)
    if not text:
        return ""

    # Escape HTML
    text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

    # Get run properties
    rPr = r_element.find(qn('w:rPr'))
    if rPr is None:
        return text

    # Check for bold
    if rPr.find(qn('w:b')) is not None:
        text = f"<strong>{text}</strong>"

    # Check for italic
    if rPr.find(qn('w:i')) is not None:
        text = f"<em>{text}</em>"

    # Check for underline
    if rPr.find(qn('w:u')) is not None:
        text = f"<u>{text}</u>"

    # Check for color
    color = rPr.find(qn('w:color'))
    if color is not None:
        color_val = color.get(qn('w:val'))
        if color_val and color_val != 'auto':
            text = f'<span style="color: #{color_val};">{text}</span>'

    # Check for font size
    sz = rPr.find(qn('w:sz'))
    if sz is not None:
        size_val = sz.get(qn('w:val'))
        if size_val:
            # Size is in half-points
            size_pt = int(size_val) / 2
            if size_pt > 14 or size_pt < 10:
                text = f'<span style="font-size: {size_pt}pt;">{text}</span>'

    # Check for highlighting
    highlight = rPr.find(qn('w:highlight'))
    if highlight is not None:
        hl_val = highlight.get(qn('w:val'))
        if hl_val:
            text = f'<mark style="background-color: {hl_val};">{text}</mark>'

    return text


def _process_table(tbl_element, doc) -> str:
    """Process a table element."""
    from docx.oxml.shared import qn

    html = '<table style="width: 100%; border-collapse: collapse; margin: 10px 0;">'

    for tr in tbl_element.findall(qn('w:tr')):
        html += '<tr>'
        for tc in tr.findall(qn('w:tc')):
            # Get cell shading (background)
            cell_style = "padding: 8px; vertical-align: top;"
            tcPr = tc.find(qn('w:tcPr'))
            if tcPr is not None:
                shd = tcPr.find(qn('w:shd'))
                if shd is not None:
                    fill = shd.get(qn('w:fill'))
                    if fill and fill != 'auto':
                        cell_style += f"background-color: #{fill};"

            html += f'<td style="{cell_style}">'

            # Process paragraphs in cell
            for p in tc.findall(qn('w:p')):
                html += _process_paragraph(p)

            html += '</td>'
        html += '</tr>'

    html += '</table>'
    return html
