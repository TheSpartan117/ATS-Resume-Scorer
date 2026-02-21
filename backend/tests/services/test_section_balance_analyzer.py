import pytest
from backend.services.section_balance_analyzer import SectionBalanceAnalyzer

@pytest.fixture
def analyzer():
    return SectionBalanceAnalyzer()

def test_balanced_resume_no_penalty(analyzer):
    """Well-balanced resume should have no penalties"""
    sections = {
        'experience': 500,  # 50% (ideal: 50-60%)
        'skills': 200,      # 20% (ideal: <25%)
        'education': 150,   # 15%
        'summary': 150      # 15% (ideal: <15%)
    }

    result = analyzer.analyze(sections)

    assert result['penalty_score'] == 0
    assert result['is_balanced'] is True
    assert len(result['violations']) == 0

def test_skills_section_too_large(analyzer):
    """Skills section >25% should trigger -2 pt penalty"""
    sections = {
        'experience': 400,  # 40%
        'skills': 400,      # 40% (exceeds 25% threshold)
        'education': 100,   # 10%
        'summary': 100      # 10%
    }

    result = analyzer.analyze(sections)

    assert result['penalty_score'] == -2
    assert result['is_balanced'] is False
    assert any(v['section'] == 'skills' for v in result['violations'])

def test_experience_section_too_small(analyzer):
    """Experience section <40% should trigger -2 pt penalty"""
    sections = {
        'experience': 200,  # 20% (below 40% threshold)
        'skills': 200,      # 20%
        'education': 450,   # 45%
        'summary': 150      # 15%
    }

    result = analyzer.analyze(sections)

    assert result['penalty_score'] == -2
    assert any(v['section'] == 'experience' for v in result['violations'])

def test_summary_section_too_large(analyzer):
    """Summary >15% should trigger -1 pt penalty"""
    sections = {
        'experience': 500,  # 50%
        'skills': 150,      # 15%
        'education': 150,   # 15%
        'summary': 200      # 20% (exceeds 15% threshold)
    }

    result = analyzer.analyze(sections)

    assert result['penalty_score'] == -1
    assert any(v['section'] == 'summary' for v in result['violations'])

def test_multiple_violations(analyzer):
    """Multiple violations should accumulate penalties"""
    sections = {
        'experience': 200,  # 20% (too small: -2)
        'skills': 400,      # 40% (too large: -2)
        'education': 200,   # 20%
        'summary': 200      # 20% (too large: -1)
    }

    result = analyzer.analyze(sections)

    # -2 (exp) + -2 (skills) + -1 (summary) = -5
    assert result['penalty_score'] == -5
    assert len(result['violations']) == 3

def test_penalty_cap_at_5_points(analyzer):
    """Penalty should not exceed -5 points"""
    sections = {
        'experience': 100,  # 10% (way too small)
        'skills': 600,      # 60% (way too large)
        'education': 100,   # 10%
        'summary': 200      # 20% (too large)
    }

    result = analyzer.analyze(sections)

    # Even with multiple violations, cap at -5
    assert result['penalty_score'] >= -5

def test_calculate_percentages(analyzer):
    """Should calculate section percentages correctly"""
    sections = {
        'experience': 500,
        'skills': 300,
        'education': 100,
        'summary': 100
    }

    result = analyzer.analyze(sections)

    assert result['section_percentages']['experience'] == 50.0
    assert result['section_percentages']['skills'] == 30.0
    assert result['section_percentages']['education'] == 10.0
    assert result['section_percentages']['summary'] == 10.0

def test_empty_sections_handled(analyzer):
    """Should handle missing/empty sections gracefully"""
    sections = {
        'experience': 800,
        'skills': 200
        # No education or summary
    }

    result = analyzer.analyze(sections)

    assert 'experience' in result['section_percentages']
    assert 'skills' in result['section_percentages']
    assert isinstance(result['penalty_score'], int)

def test_violation_details(analyzer):
    """Violation details should include section, threshold, actual"""
    sections = {
        'experience': 300,  # 30% (below 40%)
        'skills': 400,      # 40% (above 25%)
        'education': 200,
        'summary': 100
    }

    result = analyzer.analyze(sections)

    # Check violation structure
    for violation in result['violations']:
        assert 'section' in violation
        assert 'actual_percentage' in violation
        assert 'threshold' in violation
        assert 'penalty' in violation
        assert 'message' in violation

def test_word_count_vs_character_count(analyzer):
    """Should work with both word counts and character counts"""
    # Test with word counts
    sections_words = {
        'experience': 250,  # words
        'skills': 100,
        'education': 50,
        'summary': 50
    }

    result = analyzer.analyze(sections_words)
    assert isinstance(result['penalty_score'], int)
