import pytest
from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from io import BytesIO
from backend.services.section_detector import SectionDetector

def test_detect_sections_by_heading_style():
    """Test detecting sections using Heading styles"""
    # Create test DOCX
    doc = Document()
    doc.add_heading('Experience', level=2)
    doc.add_paragraph('Software Engineer at ABC Corp')
    doc.add_heading('Education', level=2)
    doc.add_paragraph('BS Computer Science')

    # Save to bytes
    docx_bytes = BytesIO()
    doc.save(docx_bytes)
    docx_bytes.seek(0)

    # Detect sections
    detector = SectionDetector()
    sections = detector.detect(docx_bytes.read())

    # Assertions
    assert len(sections) == 2
    assert sections[0]['title'] == 'Experience'
    assert sections[0]['content'] == 'Software Engineer at ABC Corp'
    assert sections[0]['section_id'] == 'section_0'
    assert sections[0]['start_para_idx'] >= 0
    assert sections[0]['end_para_idx'] > sections[0]['start_para_idx']
    assert sections[1]['title'] == 'Education'

def test_detect_sections_by_bold_text():
    """Test detecting sections using bold text"""
    doc = Document()

    # Add bold heading
    p1 = doc.add_paragraph()
    run1 = p1.add_run('WORK EXPERIENCE')
    run1.bold = True
    run1.font.size = Pt(14)

    doc.add_paragraph('Senior Developer at XYZ')

    # Add another bold heading
    p2 = doc.add_paragraph()
    run2 = p2.add_run('SKILLS')
    run2.bold = True
    run2.font.size = Pt(14)

    doc.add_paragraph('Python, JavaScript, React')

    docx_bytes = BytesIO()
    doc.save(docx_bytes)
    docx_bytes.seek(0)

    detector = SectionDetector()
    sections = detector.detect(docx_bytes.read())

    assert len(sections) == 2
    assert sections[0]['title'] == 'WORK EXPERIENCE'
    assert 'Senior Developer' in sections[0]['content']
    assert sections[1]['title'] == 'SKILLS'
