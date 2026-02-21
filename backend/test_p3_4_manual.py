"""
Manual test for P3.4 ATS Formatting Scorer
Run this to validate the implementation works
"""

from unittest.mock import Mock
from services.parameters.p3_4_ats_formatting import ATSFormattingScorer


def test_basic_functionality():
    """Test basic functionality of the scorer"""
    scorer = ATSFormattingScorer()
    mock_resume = Mock()
    mock_resume.metadata = {}

    # Test 1: Perfect resume
    print("Test 1: Perfect resume (no issues)")
    docx_structure = {
        'sections': [{
            'paragraphs': [
                {'text': 'John Doe', 'runs': [
                    {'text': 'John Doe', 'formatting': {'font_name': 'Calibri', 'font_size': 11}}
                ]}
            ],
            'tables': []
        }]
    }
    result = scorer.score(mock_resume, docx_structure, file_format='docx')
    print(f"  Score: {result['score']} (expected: 7)")
    print(f"  Issues: {result['issues_found']}")
    assert result['score'] == 7, f"Expected 7, got {result['score']}"
    print("  ✓ PASSED\n")

    # Test 2: Resume with tables
    print("Test 2: Resume with tables")
    docx_structure = {
        'sections': [{
            'paragraphs': [],
            'tables': [{'rows': 2, 'cols': 2, 'cells': []}]
        }]
    }
    result = scorer.score(mock_resume, docx_structure, file_format='docx')
    print(f"  Score: {result['score']} (expected: 5)")
    print(f"  Has tables: {result['has_tables']} (expected: True)")
    print(f"  Penalties: {result['total_penalties']} (expected: 2)")
    assert result['score'] == 5, f"Expected 5, got {result['score']}"
    assert result['has_tables'] is True
    print("  ✓ PASSED\n")

    # Test 3: Resume with fancy fonts
    print("Test 3: Resume with fancy fonts")
    docx_structure = {
        'sections': [{
            'paragraphs': [
                {'text': 'Title', 'runs': [
                    {'text': 'Title', 'formatting': {'font_name': 'Comic Sans MS', 'font_size': 12}}
                ]}
            ],
            'tables': []
        }]
    }
    result = scorer.score(mock_resume, docx_structure, file_format='docx')
    print(f"  Score: {result['score']} (expected: 6)")
    print(f"  Has fancy fonts: {result['has_fancy_fonts']} (expected: True)")
    assert result['score'] == 6, f"Expected 6, got {result['score']}"
    assert result['has_fancy_fonts'] is True
    print("  ✓ PASSED\n")

    # Test 4: Multiple issues
    print("Test 4: Multiple issues (tables + text boxes + header)")
    docx_structure = {
        'sections': [{
            'paragraphs': [],
            'tables': [{'rows': 1, 'cols': 1, 'cells': []}],
            'text_boxes': [{'text': 'Skills'}]
        }],
        'has_header': True
    }
    result = scorer.score(mock_resume, docx_structure, file_format='docx')
    print(f"  Score: {result['score']} (expected: 2)")
    print(f"  Penalties: {result['total_penalties']} (expected: 5)")
    print(f"  Issues: {result['issues_found']}")
    assert result['score'] == 2, f"Expected 2, got {result['score']}"
    assert result['total_penalties'] == 5
    print("  ✓ PASSED\n")

    # Test 5: Standard fonts (no penalty)
    print("Test 5: Standard fonts (Arial, Calibri)")
    for font in ['Arial', 'Calibri', 'Times New Roman']:
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
        assert result['has_fancy_fonts'] is False, f"{font} should not be fancy"
        assert result['score'] == 7, f"{font} should get full score"
        print(f"  {font}: ✓")
    print("  ✓ ALL PASSED\n")

    print("=" * 50)
    print("All manual tests PASSED! ✓")
    print("=" * 50)


if __name__ == '__main__':
    test_basic_functionality()
