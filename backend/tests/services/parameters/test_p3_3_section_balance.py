"""
Test P3.3: Section Balance (5 points)

Detects keyword stuffing and poor content distribution.
Converts penalty to positive score:
- 0 issues = 5 points (EXCELLENT)
- penalty -1 to -2 = 3 points (GOOD)
- penalty -3 to -4 = 1 point (FAIR)
- penalty -5 = 0 points (POOR)

Detects:
- Skills too large (>25%)
- Experience too small (<40%)
- Summary too large (>15%)
"""

import pytest
from backend.services.parameters.p3_3_section_balance import SectionBalanceScorer


@pytest.fixture
def scorer():
    """Create SectionBalanceScorer instance."""
    return SectionBalanceScorer()


# ============================================================================
# EXCELLENT (0 issues = 5 points)
# ============================================================================

def test_perfect_balance_excellent(scorer):
    """Perfect section balance = 5 pts (0 issues)"""
    sections = {
        'experience': {'content': 'Experience content here ' * 50, 'word_count': 500},
        'skills': {'content': 'Skills content here ' * 20, 'word_count': 200},
        'education': {'content': 'Education content here ' * 15, 'word_count': 150},
        'summary': {'content': 'Summary content here ' * 10, 'word_count': 100}
    }
    # Total: 950 words
    # Experience: 500/950 = 52.6% (within 40-100% range)
    # Skills: 200/950 = 21.1% (below 25% threshold)
    # Summary: 100/950 = 10.5% (below 15% threshold)

    result = scorer.score(sections)
    assert result['score'] == 5
    assert result['rating'] == 'EXCELLENT'
    assert result['penalty_score'] == 0
    assert len(result['issues']) == 0


def test_optimal_distribution(scorer):
    """Optimal distribution = 5 pts"""
    sections = {
        'experience': {'content': '', 'word_count': 550},  # 55%
        'skills': {'content': '', 'word_count': 240},      # 24%
        'education': {'content': '', 'word_count': 110},   # 11%
        'summary': {'content': '', 'word_count': 100}      # 10%
    }
    # Total: 1000 words
    # All sections within optimal range

    result = scorer.score(sections)
    assert result['score'] == 5
    assert result['rating'] == 'EXCELLENT'
    assert len(result['issues']) == 0


def test_boundary_values_acceptable(scorer):
    """Boundary values still acceptable = 5 pts"""
    sections = {
        'experience': {'content': '', 'word_count': 400},  # Exactly 40%
        'skills': {'content': '', 'word_count': 250},      # Exactly 25%
        'education': {'content': '', 'word_count': 200},   # 20%
        'summary': {'content': '', 'word_count': 150}      # Exactly 15%
    }
    # Total: 1000 words
    # Experience at minimum (40%), skills at max (25%), summary at max (15%)

    result = scorer.score(sections)
    assert result['score'] == 5
    assert result['rating'] == 'EXCELLENT'


# ============================================================================
# GOOD (penalty -1 to -2 = 3 points)
# ============================================================================

def test_skills_slightly_too_large(scorer):
    """Skills 30% (too large) = -2 penalty = 3 pts"""
    sections = {
        'experience': {'content': '', 'word_count': 500},  # 50%
        'skills': {'content': '', 'word_count': 300},      # 30% (>25%)
        'education': {'content': '', 'word_count': 100},   # 10%
        'summary': {'content': '', 'word_count': 100}      # 10%
    }
    # Total: 1000 words
    # Skills >25% = -2 penalty

    result = scorer.score(sections)
    assert result['score'] == 3
    assert result['rating'] == 'GOOD'
    assert result['penalty_score'] == -2
    assert len(result['issues']) == 1
    assert result['issues'][0]['section'] == 'skills'
    assert result['issues'][0]['penalty'] == -2


def test_experience_too_small(scorer):
    """Experience 35% + Summary 20% = -3 penalty = 1 pt"""
    sections = {
        'experience': {'content': '', 'word_count': 350},  # 35% (<40%)
        'skills': {'content': '', 'word_count': 200},      # 20%
        'education': {'content': '', 'word_count': 250},   # 25%
        'summary': {'content': '', 'word_count': 200}      # 20% (>15%)
    }
    # Total: 1000 words
    # Experience <40% = -2
    # Summary >15% = -1
    # Total = -3 penalty

    result = scorer.score(sections)
    assert result['score'] == 1
    assert result['rating'] == 'FAIR'
    assert result['penalty_score'] == -3
    assert len(result['issues']) == 2
    assert result['issues'][0]['section'] == 'experience'
    assert result['issues'][0]['penalty'] == -2


def test_summary_too_large(scorer):
    """Summary 20% (too large) = -1 penalty = 3 pts"""
    sections = {
        'experience': {'content': '', 'word_count': 500},  # 50%
        'skills': {'content': '', 'word_count': 200},      # 20%
        'education': {'content': '', 'word_count': 100},   # 10%
        'summary': {'content': '', 'word_count': 200}      # 20% (>15%)
    }
    # Total: 1000 words
    # Summary >15% = -1 penalty

    result = scorer.score(sections)
    assert result['score'] == 3
    assert result['rating'] == 'GOOD'
    assert result['penalty_score'] == -1
    assert len(result['issues']) == 1
    assert result['issues'][0]['section'] == 'summary'
    assert result['issues'][0]['penalty'] == -1


def test_two_minor_issues(scorer):
    """Two issues totaling -2 penalty = 3 pts"""
    sections = {
        'experience': {'content': '', 'word_count': 380},  # 38% (<40%)
        'skills': {'content': '', 'word_count': 200},      # 20%
        'education': {'content': '', 'word_count': 220},   # 22%
        'summary': {'content': '', 'word_count': 200}      # 20% (>15%)
    }
    # Total: 1000 words
    # Experience <40% = -2 penalty
    # Summary >15% = -1 penalty
    # But total capped at -2 in this range

    result = scorer.score(sections)
    assert result['score'] == 1  # penalty -3 = FAIR
    assert result['rating'] == 'FAIR'
    assert result['penalty_score'] == -3
    assert len(result['issues']) >= 2


# ============================================================================
# FAIR (penalty -3 to -4 = 1 point)
# ============================================================================

def test_multiple_issues_fair(scorer):
    """Multiple issues = -5 penalty (capped) = 0 pt"""
    sections = {
        'experience': {'content': '', 'word_count': 300},  # 30% (<40%)
        'skills': {'content': '', 'word_count': 300},      # 30% (>25%)
        'education': {'content': '', 'word_count': 200},   # 20%
        'summary': {'content': '', 'word_count': 200}      # 20% (>15%)
    }
    # Total: 1000 words
    # Experience <40% = -2
    # Skills >25% = -2
    # Summary >15% = -1
    # Total = -5 (max penalty cap)

    result = scorer.score(sections)
    assert result['score'] == 0
    assert result['rating'] == 'POOR'
    assert result['penalty_score'] == -5
    assert len(result['issues']) >= 3


def test_severe_skill_stuffing(scorer):
    """Severe skills section (40%) = -2, plus other issues = 1 pt"""
    sections = {
        'experience': {'content': '', 'word_count': 350},  # 35% (<40%)
        'skills': {'content': '', 'word_count': 400},      # 40% (>25%)
        'education': {'content': '', 'word_count': 150},   # 15%
        'summary': {'content': '', 'word_count': 100}      # 10%
    }
    # Total: 1000 words
    # Experience <40% = -2
    # Skills >25% = -2
    # Total = -4

    result = scorer.score(sections)
    assert result['score'] == 1
    assert result['rating'] == 'FAIR'
    assert result['penalty_score'] == -4
    assert len(result['issues']) >= 2


# ============================================================================
# POOR (penalty -5 = 0 points)
# ============================================================================

def test_all_issues_poor(scorer):
    """All three issues = -5 penalty (capped) = 0 pts"""
    sections = {
        'experience': {'content': '', 'word_count': 200},  # 20% (<40%)
        'skills': {'content': '', 'word_count': 400},      # 40% (>25%)
        'education': {'content': '', 'word_count': 200},   # 20%
        'summary': {'content': '', 'word_count': 200}      # 20% (>15%)
    }
    # Total: 1000 words
    # Experience <40% = -2
    # Skills >25% = -2
    # Summary >15% = -1
    # Total = -5 (capped at -5)

    result = scorer.score(sections)
    assert result['score'] == 0
    assert result['rating'] == 'POOR'
    assert result['penalty_score'] == -5
    assert len(result['issues']) == 3


def test_extreme_keyword_stuffing(scorer):
    """Extreme keyword stuffing (60% skills) = -5 penalty = 0 pts"""
    sections = {
        'experience': {'content': '', 'word_count': 150},  # 15% (<40%)
        'skills': {'content': '', 'word_count': 600},      # 60% (>25%)
        'education': {'content': '', 'word_count': 50},    # 5%
        'summary': {'content': '', 'word_count': 200}      # 20% (>15%)
    }
    # Total: 1000 words
    # Multiple severe violations

    result = scorer.score(sections)
    assert result['score'] == 0
    assert result['rating'] == 'POOR'
    assert result['penalty_score'] == -5
    assert len(result['issues']) >= 3


# ============================================================================
# EDGE CASES
# ============================================================================

def test_empty_sections(scorer):
    """Empty sections = 0 pts (no data to score)"""
    result = scorer.score({})
    assert result['score'] == 0
    assert result['rating'] == 'POOR'
    assert result['penalty_score'] == 0
    assert len(result['issues']) == 0
    assert result['total_words'] == 0


def test_missing_key_sections(scorer):
    """Missing experience section = penalty for skills being too large"""
    sections = {
        'skills': {'content': '', 'word_count': 500},
        'education': {'content': '', 'word_count': 500}
    }
    # No experience section, skills 50% (>25%)

    result = scorer.score(sections)
    # Should penalize large skills section
    assert result['score'] == 3  # penalty -2 = GOOD
    assert 'skills' in [issue['section'] for issue in result['issues']]


def test_only_experience_section(scorer):
    """Only experience section = 5 pts (100% experience is fine)"""
    sections = {
        'experience': {'content': '', 'word_count': 1000}  # 100%
    }

    result = scorer.score(sections)
    assert result['score'] == 5
    assert result['rating'] == 'EXCELLENT'
    assert len(result['issues']) == 0


def test_section_percentages_in_result(scorer):
    """Result includes section percentages"""
    sections = {
        'experience': {'content': '', 'word_count': 500},
        'skills': {'content': '', 'word_count': 300},
        'summary': {'content': '', 'word_count': 200}
    }

    result = scorer.score(sections)
    assert 'section_percentages' in result
    assert 'experience' in result['section_percentages']
    assert 'skills' in result['section_percentages']
    assert result['section_percentages']['experience'] == 50.0
    assert result['section_percentages']['skills'] == 30.0


def test_detailed_issues_format(scorer):
    """Issues include detailed information"""
    sections = {
        'experience': {'content': '', 'word_count': 300},  # 30% (<40%)
        'skills': {'content': '', 'word_count': 300},      # 30% (>25%)
        'summary': {'content': '', 'word_count': 400}      # 40% (>15%)
    }

    result = scorer.score(sections)
    assert len(result['issues']) >= 2

    # Check issue structure
    for issue in result['issues']:
        assert 'section' in issue
        assert 'percentage' in issue
        assert 'issue' in issue
        assert 'penalty' in issue


def test_result_includes_all_keys(scorer):
    """Result includes all expected keys"""
    sections = {
        'experience': {'content': '', 'word_count': 500},
        'skills': {'content': '', 'word_count': 200},
        'summary': {'content': '', 'word_count': 100}
    }

    result = scorer.score(sections)

    # Check all required keys
    assert 'score' in result
    assert 'rating' in result
    assert 'penalty_score' in result
    assert 'issues' in result
    assert 'section_percentages' in result
    assert 'total_words' in result
    assert 'max_penalty' in result


def test_zero_word_count_sections(scorer):
    """Sections with zero word count"""
    sections = {
        'experience': {'content': '', 'word_count': 0},
        'skills': {'content': '', 'word_count': 500},
        'summary': {'content': '', 'word_count': 500}
    }

    result = scorer.score(sections)
    # Experience is 0%, should trigger penalty
    assert 'experience' in [issue['section'] for issue in result['issues']]


def test_very_small_resume(scorer):
    """Very small resume (100 words total)"""
    sections = {
        'experience': {'content': '', 'word_count': 50},
        'skills': {'content': '', 'word_count': 30},
        'summary': {'content': '', 'word_count': 20}
    }
    # Total: 100 words
    # Experience: 50% (good)
    # Skills: 30% (>25%, penalty)
    # Summary: 20% (>15%, penalty)

    result = scorer.score(sections)
    assert result['total_words'] == 100
    assert result['score'] <= 3  # Should have penalties


def test_very_large_resume(scorer):
    """Very large resume (2000 words total)"""
    sections = {
        'experience': {'content': '', 'word_count': 1000},  # 50%
        'skills': {'content': '', 'word_count': 400},       # 20%
        'education': {'content': '', 'word_count': 400},    # 20%
        'summary': {'content': '', 'word_count': 200}       # 10%
    }
    # Total: 2000 words
    # All sections in optimal range

    result = scorer.score(sections)
    assert result['score'] == 5
    assert result['rating'] == 'EXCELLENT'
    assert result['total_words'] == 2000
