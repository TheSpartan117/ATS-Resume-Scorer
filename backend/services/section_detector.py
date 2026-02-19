"""
Dynamically detect sections from DOCX resumes.
Supports various formats: heading styles, bold text, ALL CAPS, tables.
"""
from docx import Document
from docx.oxml.shared import qn
from io import BytesIO
import logging

logger = logging.getLogger(__name__)

class SectionDetector:
    """Detect resume sections dynamically without hardcoded section names"""

    def detect(self, docx_bytes: bytes) -> list[dict]:
        """
        Detect sections from DOCX bytes.

        Returns:
            List of section dictionaries with title, content, indices
        """
        doc = Document(BytesIO(docx_bytes))
        sections = []
        current_section = None
        section_counter = 0

        for idx, para in enumerate(doc.paragraphs):
            text = para.text.strip()
            if not text:
                continue

            # Check if this is a section heading
            is_heading = self._is_section_heading(para)

            if is_heading:
                # Save previous section
                if current_section:
                    current_section['end_para_idx'] = idx
                    sections.append(current_section)

                # Start new section
                current_section = {
                    'title': text,
                    'content': '',
                    'section_id': f'section_{section_counter}',
                    'start_para_idx': idx + 1,
                    'end_para_idx': idx + 1,
                    'is_in_table': False,
                    'table_cell_ref': None
                }
                section_counter += 1
            elif current_section:
                # Add content to current section
                if current_section['content']:
                    current_section['content'] += '\n'
                current_section['content'] += text
                current_section['end_para_idx'] = idx + 1

        # Save last section
        if current_section:
            sections.append(current_section)

        return sections

    def _is_section_heading(self, paragraph) -> bool:
        """Determine if paragraph is a section heading"""
        # Check style name
        if 'Heading' in paragraph.style.name:
            return True

        # Check if text is bold and larger font
        if paragraph.runs:
            first_run = paragraph.runs[0]
            if first_run.bold and first_run.font.size:
                if first_run.font.size.pt >= 12:
                    return True

        # Check for ALL CAPS (likely a heading)
        text = paragraph.text.strip()
        if text and text.isupper() and len(text) > 2:
            return True

        return False
