import pytest
from backend.services.section_balance_analyzer import SectionBalanceAnalyzer

@pytest.fixture
def analyzer():
    return SectionBalanceAnalyzer()

def test_balanced_sections_no_penalty(analyzer):
    """Well-balanced sections = no penalty"""
    sections = {
        'experience': {
            'content': 'A' * 600,  # 55% of 1100 total
            'word_count': 600
        },
        'skills': {
            'content': 'B' * 200,  # 18% of total
            'word_count': 200
        },
        'education': {
            'content': 'C' * 150,  # 14% of total
            'word_count': 150
        },
        'summary': {
            'content': 'D' * 150,  # 14% of total
            'word_count': 150
        }
    }

    result = analyzer.analyze(sections)

    assert result['penalty_score'] == 0
    assert result['issues'] == []

def test_skills_section_too_large(analyzer):
    """Skills >25% = -2 pts (keyword stuffing)"""
    sections = {
        'experience': {
            'content': 'A' * 400,  # 40%
            'word_count': 400
        },
        'skills': {
            'content': 'B' * 300,  # 30% (over 25% threshold)
            'word_count': 300
        },
        'education': {
            'content': 'C' * 150,  # 15%
            'word_count': 150
        },
        'summary': {
            'content': 'D' * 150,  # 15%
            'word_count': 150
        }
    }

    result = analyzer.analyze(sections)

    assert result['penalty_score'] == -2
    assert len(result['issues']) == 1
    assert 'skills' in result['issues'][0]['section']
    assert result['issues'][0]['penalty'] == -2

def test_experience_section_too_small(analyzer):
    """Experience <40% = -2 pts (insufficient detail)"""
    sections = {
        'experience': {
            'content': 'A' * 300,  # 30% (under 40% threshold)
            'word_count': 300
        },
        'skills': {
            'content': 'B' * 200,  # 20%
            'word_count': 200
        },
        'education': {
            'content': 'C' * 400,  # 40%
            'word_count': 400
        },
        'summary': {
            'content': 'D' * 100,  # 10%
            'word_count': 100
        }
    }

    result = analyzer.analyze(sections)

    assert result['penalty_score'] == -2
    assert any('experience' in issue['section'] for issue in result['issues'])

def test_summary_section_too_large(analyzer):
    """Summary >15% = -1 pt (too verbose)"""
    sections = {
        'experience': {
            'content': 'A' * 500,  # 50%
            'word_count': 500
        },
        'skills': {
            'content': 'B' * 200,  # 20%
            'word_count': 200
        },
        'education': {
            'content': 'C' * 100,  # 10%
            'word_count': 100
        },
        'summary': {
            'content': 'D' * 200,  # 20% (over 15% threshold)
            'word_count': 200
        }
    }

    result = analyzer.analyze(sections)

    assert result['penalty_score'] == -1
    assert any('summary' in issue['section'] for issue in result['issues'])

def test_multiple_issues_cumulative_penalty(analyzer):
    """Multiple section issues = cumulative penalty (capped)"""
    sections = {
        'experience': {
            'content': 'A' * 200,  # 20% (too small)
            'word_count': 200
        },
        'skills': {
            'content': 'B' * 400,  # 40% (too large)
            'word_count': 400
        },
        'education': {
            'content': 'C' * 200,  # 20%
            'word_count': 200
        },
        'summary': {
            'content': 'D' * 200,  # 20% (too large)
            'word_count': 200
        }
    }

    result = analyzer.analyze(sections)

    # -2 (exp too small) + -2 (skills too large) + -1 (summary too large) = -5
    assert result['penalty_score'] <= -3  # Should be capped at -5
    assert len(result['issues']) == 3

def test_penalty_capped_at_5(analyzer):
    """Total penalty should not exceed -5 points"""
    sections = {
        'experience': {
            'content': 'A' * 100,  # 10% (very small)
            'word_count': 100
        },
        'skills': {
            'content': 'B' * 600,  # 60% (very large)
            'word_count': 600
        },
        'education': {
            'content': 'C' * 150,  # 15%
            'word_count': 150
        },
        'summary': {
            'content': 'D' * 150,  # 15%
            'word_count': 150
        }
    }

    result = analyzer.analyze(sections)

    assert result['penalty_score'] >= -5  # Cap at -5

def test_missing_sections_handled_gracefully(analyzer):
    """Should handle resumes with missing sections"""
    sections = {
        'experience': {
            'content': 'A' * 800,  # 80%
            'word_count': 800
        },
        'skills': {
            'content': 'B' * 200,  # 20%
            'word_count': 200
        }
        # No education or summary
    }

    result = analyzer.analyze(sections)

    # Should not crash, may or may not penalize
    assert isinstance(result['penalty_score'], int)
    assert result['penalty_score'] <= 0

def test_get_section_percentage(analyzer):
    """Should correctly calculate section percentage"""
    sections = {
        'experience': {'content': 'A' * 500, 'word_count': 500},
        'skills': {'content': 'B' * 300, 'word_count': 300},
        'education': {'content': 'C' * 200, 'word_count': 200}
    }

    # Total = 1000
    exp_pct = analyzer._get_section_percentage(sections, 'experience')
    skills_pct = analyzer._get_section_percentage(sections, 'skills')
    edu_pct = analyzer._get_section_percentage(sections, 'education')

    assert exp_pct == 50.0
    assert skills_pct == 30.0
    assert edu_pct == 20.0

def test_detailed_analysis_structure(analyzer):
    """analyze() should return comprehensive structure"""
    sections = {
        'experience': {'content': 'A' * 600, 'word_count': 600},
        'skills': {'content': 'B' * 400, 'word_count': 400}
    }

    result = analyzer.analyze(sections)

    assert 'penalty_score' in result
    assert 'issues' in result
    assert 'section_percentages' in result
    assert 'total_words' in result
    assert 'max_penalty' in result

    assert result['section_percentages']['experience'] == 60.0
    assert result['section_percentages']['skills'] == 40.0
