"""
Test P3.4: ATS-Friendly Formatting (7 points)

Tests formatting elements that cause ATS parsing failures:
- Tables/columns = -2 pts (parsing issues)
- Text boxes = -2 pts (text extraction fails)
- Headers/footers = -1 pt (inconsistent parsing)
- Images/graphics = -1 pt (unparseable)
- Fancy fonts = -1 pt (character recognition issues)

Scoring:
- Start with 7 points
- Deduct penalties
- Minimum 0 points
"""

import pytest
from unittest.mock import Mock
from backend.services.parameters.p3_4_ats_formatting import ATSFormattingScorer


@pytest.fixture
def scorer():
    """Create ATSFormattingScorer instance."""
    return ATSFormattingScorer()


@pytest.fixture
def mock_resume():
    """Create mock resume data."""
    resume = Mock()
    resume.metadata = None  # Explicitly set to None to avoid Mock auto-creating attributes
    return resume


@pytest.fixture
def mock_docx_structure():
    """Create mock DOCX structure."""
    return {}


# ============================================================================
# PERFECT ATS-FRIENDLY RESUME TESTS
# ============================================================================

def test_perfect_formatting_no_issues(scorer, mock_resume, mock_docx_structure):
    """Resume with no ATS formatting issues = 7 pts"""
    # Simple structure with no problematic elements
    docx_structure = {
        'sections': [{
            'paragraphs': [
                {'text': 'John Doe', 'style': 'Heading 1', 'runs': [
                    {'text': 'John Doe', 'formatting': {'font_name': 'Calibri', 'font_size': 14}}
                ]},
                {'text': 'Software Engineer', 'style': 'Normal', 'runs': [
                    {'text': 'Software Engineer', 'formatting': {'font_name': 'Calibri', 'font_size': 11}}
                ]}
            ],
            'tables': []
        }]
    }

    result = scorer.score(mock_resume, docx_structure, file_format='docx')

    assert result['score'] == 7
    assert result['issues_found'] == []
    assert result['has_tables'] is False
    assert result['has_text_boxes'] is False
    assert result['has_headers_footers'] is False
    assert result['has_images'] is False
    assert result['has_fancy_fonts'] is False
    assert result['total_penalties'] == 0


# ============================================================================
# TABLES/COLUMNS PENALTY (-2 pts)
# ============================================================================

def test_tables_present_penalty(scorer, mock_resume):
    """Resume with tables = -2 pts"""
    docx_structure = {
        'sections': [{
            'paragraphs': [
                {'text': 'John Doe', 'style': 'Normal', 'runs': [
                    {'text': 'John Doe', 'formatting': {'font_name': 'Calibri', 'font_size': 11}}
                ]}
            ],
            'tables': [
                {'rows': 2, 'cols': 3, 'cells': [[{'text': 'A'}, {'text': 'B'}]]}
            ]
        }]
    }

    result = scorer.score(mock_resume, docx_structure, file_format='docx')

    assert result['score'] == 5  # 7 - 2
    assert result['has_tables'] is True
    assert 'Tables detected' in str(result['issues_found'])
    assert result['total_penalties'] == 2


def test_multiple_tables_still_2pt_penalty(scorer, mock_resume):
    """Multiple tables still only -2 pts (not cumulative)"""
    docx_structure = {
        'sections': [{
            'paragraphs': [],
            'tables': [
                {'rows': 2, 'cols': 2, 'cells': []},
                {'rows': 3, 'cols': 4, 'cells': []},
                {'rows': 1, 'cols': 5, 'cells': []}
            ]
        }]
    }

    result = scorer.score(mock_resume, docx_structure, file_format='docx')

    assert result['score'] == 5  # 7 - 2 (not 7 - 6)
    assert result['has_tables'] is True
    assert result['total_penalties'] == 2


# ============================================================================
# TEXT BOXES PENALTY (-2 pts)
# ============================================================================

def test_text_boxes_penalty(scorer, mock_resume):
    """Resume with text boxes = -2 pts"""
    # Text boxes are detected by checking for textbox elements in DOCX
    docx_structure = {
        'sections': [{
            'paragraphs': [
                {'text': 'Normal text', 'style': 'Normal', 'runs': [
                    {'text': 'Normal text', 'formatting': {'font_name': 'Calibri', 'font_size': 11}}
                ]}
            ],
            'tables': [],
            'text_boxes': [
                {'text': 'Skills: Python, Java'}
            ]
        }]
    }

    result = scorer.score(mock_resume, docx_structure, file_format='docx')

    assert result['score'] == 5  # 7 - 2
    assert result['has_text_boxes'] is True
    assert 'Text boxes detected' in str(result['issues_found'])
    assert result['total_penalties'] == 2


# ============================================================================
# HEADERS/FOOTERS PENALTY (-1 pt)
# ============================================================================

def test_headers_footers_penalty(scorer, mock_resume):
    """Resume with headers/footers = -1 pt"""
    docx_structure = {
        'sections': [{
            'paragraphs': [],
            'tables': []
        }],
        'has_header': True,
        'has_footer': True
    }

    result = scorer.score(mock_resume, docx_structure, file_format='docx')

    assert result['score'] == 6  # 7 - 1
    assert result['has_headers_footers'] is True
    assert 'Headers/footers detected' in str(result['issues_found'])
    assert result['total_penalties'] == 1


def test_header_only_still_penalty(scorer, mock_resume):
    """Header only (no footer) still gets -1 pt"""
    docx_structure = {
        'sections': [{
            'paragraphs': [],
            'tables': []
        }],
        'has_header': True,
        'has_footer': False
    }

    result = scorer.score(mock_resume, docx_structure, file_format='docx')

    assert result['score'] == 6  # 7 - 1
    assert result['has_headers_footers'] is True


# ============================================================================
# IMAGES/GRAPHICS PENALTY (-1 pt)
# ============================================================================

def test_images_penalty(scorer, mock_resume):
    """Resume with images = -1 pt"""
    # Images detected from metadata or structure
    mock_resume.metadata = {'hasPhoto': True}

    docx_structure = {
        'sections': [{
            'paragraphs': [],
            'tables': []
        }]
    }

    result = scorer.score(mock_resume, docx_structure, file_format='docx')

    assert result['score'] == 6  # 7 - 1
    assert result['has_images'] is True
    assert 'Images/graphics detected' in str(result['issues_found'])
    assert result['total_penalties'] == 1


def test_images_in_structure(scorer, mock_resume):
    """Images detected from DOCX structure"""
    mock_resume.metadata = {}

    docx_structure = {
        'sections': [{
            'paragraphs': [],
            'tables': [],
            'images': [
                {'type': 'photo', 'size': 1024}
            ]
        }]
    }

    result = scorer.score(mock_resume, docx_structure, file_format='docx')

    assert result['score'] == 6  # 7 - 1
    assert result['has_images'] is True


# ============================================================================
# FANCY FONTS PENALTY (-1 pt)
# ============================================================================

def test_fancy_fonts_penalty(scorer, mock_resume):
    """Resume with fancy fonts = -1 pt"""
    docx_structure = {
        'sections': [{
            'paragraphs': [
                {'text': 'John Doe', 'style': 'Normal', 'runs': [
                    {'text': 'John', 'formatting': {'font_name': 'Comic Sans MS', 'font_size': 12}},
                    {'text': ' Doe', 'formatting': {'font_name': 'Calibri', 'font_size': 11}}
                ]}
            ],
            'tables': []
        }]
    }

    result = scorer.score(mock_resume, docx_structure, file_format='docx')

    assert result['score'] == 6  # 7 - 1
    assert result['has_fancy_fonts'] is True
    assert 'Fancy fonts detected' in str(result['issues_found'])
    assert result['total_penalties'] == 1


def test_multiple_fancy_fonts_same_penalty(scorer, mock_resume):
    """Multiple fancy fonts still only -1 pt"""
    docx_structure = {
        'sections': [{
            'paragraphs': [
                {'text': 'Title', 'runs': [
                    {'text': 'Title', 'formatting': {'font_name': 'Papyrus', 'font_size': 14}}
                ]},
                {'text': 'Body', 'runs': [
                    {'text': 'Body', 'formatting': {'font_name': 'Comic Sans MS', 'font_size': 11}}
                ]}
            ],
            'tables': []
        }]
    }

    result = scorer.score(mock_resume, docx_structure, file_format='docx')

    assert result['score'] == 6  # 7 - 1
    assert result['has_fancy_fonts'] is True


def test_standard_fonts_no_penalty(scorer, mock_resume):
    """Standard fonts (Calibri, Arial, Times) = no penalty"""
    standard_fonts = ['Calibri', 'Arial', 'Times New Roman', 'Helvetica', 'Georgia']

    for font in standard_fonts:
        docx_structure = {
            'sections': [{
                'paragraphs': [
                    {'text': 'Test', 'runs': [
                        {'text': 'Test', 'formatting': {'font_name': font, 'font_size': 11}}
                    ]}
                ],
                'tables': []
            }]
        }

        result = scorer.score(mock_resume, docx_structure, file_format='docx')

        assert result['has_fancy_fonts'] is False, f"{font} should not be considered fancy"


# ============================================================================
# MULTIPLE ISSUES (CUMULATIVE PENALTIES)
# ============================================================================

def test_multiple_issues_cumulative(scorer, mock_resume):
    """Multiple formatting issues = cumulative penalties"""
    mock_resume.metadata = {'hasPhoto': True}

    docx_structure = {
        'sections': [{
            'paragraphs': [
                {'text': 'Title', 'runs': [
                    {'text': 'Title', 'formatting': {'font_name': 'Comic Sans MS', 'font_size': 14}}
                ]}
            ],
            'tables': [
                {'rows': 2, 'cols': 2, 'cells': []}
            ],
            'text_boxes': [
                {'text': 'Skills'}
            ]
        }],
        'has_header': True
    }

    result = scorer.score(mock_resume, docx_structure, file_format='docx')

    # Tables: -2, Text boxes: -2, Headers: -1, Images: -1, Fancy fonts: -1 = -7
    assert result['score'] == 0  # 7 - 7 = 0 (minimum)
    assert result['has_tables'] is True
    assert result['has_text_boxes'] is True
    assert result['has_headers_footers'] is True
    assert result['has_images'] is True
    assert result['has_fancy_fonts'] is True
    assert result['total_penalties'] == 7


def test_penalties_dont_go_negative(scorer, mock_resume):
    """Score cannot go below 0"""
    # This shouldn't happen in practice, but ensure minimum is 0
    mock_resume.metadata = {}

    docx_structure = {
        'sections': [{
            'paragraphs': [],
            'tables': [{'rows': 1, 'cols': 1, 'cells': []}],
            'text_boxes': [{'text': 'Box'}]
        }],
        'has_header': True
    }

    result = scorer.score(mock_resume, docx_structure, file_format='docx')

    assert result['score'] >= 0


# ============================================================================
# PDF HANDLING TESTS
# ============================================================================

def test_pdf_format_limited_checks(scorer, mock_resume):
    """PDF resumes have limited format checks"""
    # PDFs can't check structure as easily, so we mostly check metadata
    mock_resume.metadata = {'hasPhoto': False}

    result = scorer.score(mock_resume, None, file_format='pdf')

    # For PDFs, we can only check images from metadata
    # Without structure, we give benefit of doubt and assume no tables/boxes/etc
    assert result['score'] >= 5  # Partial credit for PDF format
    assert result['file_format'] == 'pdf'


def test_pdf_with_photo_penalty(scorer, mock_resume):
    """PDF with photo gets image penalty"""
    mock_resume.metadata = {'hasPhoto': True}

    result = scorer.score(mock_resume, None, file_format='pdf')

    assert result['has_images'] is True
    assert result['score'] <= 6  # At least image penalty


# ============================================================================
# EDGE CASES
# ============================================================================

def test_empty_docx_structure(scorer, mock_resume):
    """Empty DOCX structure = 7 pts (no issues detected)"""
    docx_structure = {
        'sections': []
    }

    result = scorer.score(mock_resume, docx_structure, file_format='docx')

    assert result['score'] == 7
    assert result['issues_found'] == []


def test_none_docx_structure_with_docx_format(scorer, mock_resume):
    """None structure with DOCX format = assume no issues"""
    result = scorer.score(mock_resume, None, file_format='docx')

    # Can't check structure, so give benefit of doubt
    assert result['score'] == 7


def test_missing_metadata(scorer):
    """Missing metadata doesn't crash"""
    mock_resume = Mock()
    mock_resume.metadata = None

    docx_structure = {
        'sections': [{
            'paragraphs': [],
            'tables': []
        }]
    }

    result = scorer.score(mock_resume, docx_structure, file_format='docx')

    assert result['score'] >= 0


# ============================================================================
# DETAILED ANALYSIS TESTS
# ============================================================================

def test_detailed_issue_descriptions(scorer, mock_resume):
    """Issues list contains detailed descriptions"""
    mock_resume.metadata = {}

    docx_structure = {
        'sections': [{
            'paragraphs': [],
            'tables': [{'rows': 2, 'cols': 2, 'cells': []}]
        }]
    }

    result = scorer.score(mock_resume, docx_structure, file_format='docx')

    assert len(result['issues_found']) > 0
    # Check that issues contain meaningful descriptions
    issue_text = ' '.join(result['issues_found'])
    assert 'table' in issue_text.lower()


def test_result_structure_completeness(scorer, mock_resume):
    """Result dictionary contains all required fields"""
    docx_structure = {
        'sections': [{
            'paragraphs': [],
            'tables': []
        }]
    }

    result = scorer.score(mock_resume, docx_structure, file_format='docx')

    # Check all required fields present
    required_fields = [
        'score', 'file_format', 'has_tables', 'has_text_boxes',
        'has_headers_footers', 'has_images', 'has_fancy_fonts',
        'total_penalties', 'issues_found'
    ]

    for field in required_fields:
        assert field in result, f"Missing required field: {field}"


# ============================================================================
# FONT CLASSIFICATION TESTS
# ============================================================================

def test_font_classification_comprehensive(scorer, mock_resume):
    """Test comprehensive font classification"""
    # Standard fonts (no penalty)
    standard_fonts = [
        'Calibri', 'Arial', 'Times New Roman', 'Helvetica',
        'Georgia', 'Verdana', 'Tahoma', 'Trebuchet MS',
        'Garamond', 'Cambria', 'Book Antiqua'
    ]

    # Fancy fonts (penalty)
    fancy_fonts = [
        'Comic Sans MS', 'Papyrus', 'Curlz MT', 'Brush Script MT',
        'Lucida Handwriting', 'Chiller', 'Jokerman'
    ]

    for font in standard_fonts:
        docx_structure = {
            'sections': [{
                'paragraphs': [
                    {'text': 'Test', 'runs': [
                        {'text': 'Test', 'formatting': {'font_name': font, 'font_size': 11}}
                    ]}
                ],
                'tables': []
            }]
        }
        result = scorer.score(mock_resume, docx_structure, file_format='docx')
        assert result['has_fancy_fonts'] is False, f"{font} should be standard"
        assert result['score'] == 7

    for font in fancy_fonts:
        docx_structure = {
            'sections': [{
                'paragraphs': [
                    {'text': 'Test', 'runs': [
                        {'text': 'Test', 'formatting': {'font_name': font, 'font_size': 11}}
                    ]}
                ],
                'tables': []
            }]
        }
        result = scorer.score(mock_resume, docx_structure, file_format='docx')
        assert result['has_fancy_fonts'] is True, f"{font} should be fancy"
        assert result['score'] == 6  # 7 - 1
