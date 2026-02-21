"""
Test P3.1: Page Count Optimization (5 points)

Tests level-aware page count scoring:
- Beginner: 1 page = 5pts, 2 pages = 3pts, 3+ pages = 0pts
- Intermediary: 1-2 pages = 5pts, 3 pages = 2pts, 4+ pages = 0pts
- Senior: 2 pages = 5pts, 3 pages = 4pts, 1 page = 2pts, 4+ pages = 0pts

Scoring based on level-appropriate page counts to prevent:
- Information overload (too many pages)
- Insufficient detail (too few pages)
"""

import pytest
from backend.services.parameters.p3_1_page_count import PageCountScorer


@pytest.fixture
def scorer():
    """Create PageCountScorer instance."""
    return PageCountScorer()


# ============================================================================
# BEGINNER LEVEL TESTS (1 page optimal)
# ============================================================================

def test_beginner_one_page_optimal(scorer):
    """Beginner with 1 page = 5 pts"""
    result = scorer.score(page_count=1, level='beginner')

    assert result['score'] == 5
    assert result['level'] == 'beginner'
    assert result['page_count'] == 1
    assert result['optimal_pages'] == 1
    assert result['meets_optimal'] is True
    assert 'recommendation' in result


def test_beginner_two_pages_acceptable(scorer):
    """Beginner with 2 pages = 3 pts (acceptable but not optimal)"""
    result = scorer.score(page_count=2, level='beginner')

    assert result['score'] == 3
    assert result['level'] == 'beginner'
    assert result['page_count'] == 2
    assert result['optimal_pages'] == 1
    assert result['meets_optimal'] is False


def test_beginner_three_pages_penalty(scorer):
    """Beginner with 3+ pages = 0 pts (too long)"""
    result = scorer.score(page_count=3, level='beginner')

    assert result['score'] == 0
    assert result['level'] == 'beginner'
    assert result['page_count'] == 3
    assert result['meets_optimal'] is False
    assert 'too long' in result['recommendation'].lower()


def test_beginner_four_pages_penalty(scorer):
    """Beginner with 4 pages = 0 pts"""
    result = scorer.score(page_count=4, level='beginner')

    assert result['score'] == 0
    assert result['page_count'] == 4


# ============================================================================
# INTERMEDIARY LEVEL TESTS (1-2 pages optimal)
# ============================================================================

def test_intermediary_one_page_optimal(scorer):
    """Intermediary with 1 page = 5 pts"""
    result = scorer.score(page_count=1, level='intermediary')

    assert result['score'] == 5
    assert result['level'] == 'intermediary'
    assert result['page_count'] == 1
    assert result['optimal_pages'] == [1, 2]
    assert result['meets_optimal'] is True


def test_intermediary_two_pages_optimal(scorer):
    """Intermediary with 2 pages = 5 pts"""
    result = scorer.score(page_count=2, level='intermediary')

    assert result['score'] == 5
    assert result['level'] == 'intermediary'
    assert result['page_count'] == 2
    assert result['optimal_pages'] == [1, 2]
    assert result['meets_optimal'] is True


def test_intermediary_three_pages_acceptable(scorer):
    """Intermediary with 3 pages = 2 pts (acceptable but not optimal)"""
    result = scorer.score(page_count=3, level='intermediary')

    assert result['score'] == 2
    assert result['level'] == 'intermediary'
    assert result['page_count'] == 3
    assert result['meets_optimal'] is False


def test_intermediary_four_pages_penalty(scorer):
    """Intermediary with 4+ pages = 0 pts"""
    result = scorer.score(page_count=4, level='intermediary')

    assert result['score'] == 0
    assert result['page_count'] == 4
    assert 'too long' in result['recommendation'].lower()


def test_intermediary_five_pages_penalty(scorer):
    """Intermediary with 5 pages = 0 pts"""
    result = scorer.score(page_count=5, level='intermediary')

    assert result['score'] == 0


# ============================================================================
# SENIOR LEVEL TESTS (2 pages optimal)
# ============================================================================

def test_senior_two_pages_optimal(scorer):
    """Senior with 2 pages = 5 pts (perfect)"""
    result = scorer.score(page_count=2, level='senior')

    assert result['score'] == 5
    assert result['level'] == 'senior'
    assert result['page_count'] == 2
    assert result['optimal_pages'] == 2
    assert result['meets_optimal'] is True


def test_senior_three_pages_good(scorer):
    """Senior with 3 pages = 4 pts (acceptable, extensive experience)"""
    result = scorer.score(page_count=3, level='senior')

    assert result['score'] == 4
    assert result['level'] == 'senior'
    assert result['page_count'] == 3
    assert result['meets_optimal'] is False


def test_senior_one_page_too_brief(scorer):
    """Senior with 1 page = 2 pts (too brief for senior level)"""
    result = scorer.score(page_count=1, level='senior')

    assert result['score'] == 2
    assert result['level'] == 'senior'
    assert result['page_count'] == 1
    assert result['meets_optimal'] is False
    assert 'brief' in result['recommendation'].lower() or 'short' in result['recommendation'].lower()


def test_senior_four_pages_penalty(scorer):
    """Senior with 4+ pages = 0 pts (too long, loses focus)"""
    result = scorer.score(page_count=4, level='senior')

    assert result['score'] == 0
    assert result['page_count'] == 4
    assert 'too long' in result['recommendation'].lower()


def test_senior_five_pages_penalty(scorer):
    """Senior with 5 pages = 0 pts"""
    result = scorer.score(page_count=5, level='senior')

    assert result['score'] == 0


# ============================================================================
# EDGE CASES
# ============================================================================

def test_zero_pages(scorer):
    """Zero pages = 0 pts"""
    result = scorer.score(page_count=0, level='intermediary')

    assert result['score'] == 0
    assert result['page_count'] == 0
    assert 'error' in result['recommendation'].lower() or 'invalid' in result['recommendation'].lower()


def test_negative_pages(scorer):
    """Negative pages = 0 pts"""
    result = scorer.score(page_count=-1, level='senior')

    assert result['score'] == 0
    assert result['page_count'] == -1


def test_invalid_level_defaults_to_intermediary(scorer):
    """Invalid level defaults to intermediary thresholds"""
    result = scorer.score(page_count=2, level='invalid_level')

    # Should default to intermediary behavior
    assert result['score'] == 5  # 2 pages is optimal for intermediary
    assert result['level'] == 'invalid_level'


def test_case_insensitive_level(scorer):
    """Level parameter is case-insensitive"""
    result1 = scorer.score(page_count=2, level='SENIOR')
    result2 = scorer.score(page_count=2, level='Senior')
    result3 = scorer.score(page_count=2, level='senior')

    assert result1['score'] == result2['score'] == result3['score'] == 5


# ============================================================================
# RESULT STRUCTURE VALIDATION
# ============================================================================

def test_result_structure_complete(scorer):
    """Result dictionary contains all required fields"""
    result = scorer.score(page_count=2, level='intermediary')

    required_fields = [
        'score',
        'level',
        'page_count',
        'optimal_pages',
        'meets_optimal',
        'recommendation'
    ]

    for field in required_fields:
        assert field in result, f"Missing required field: {field}"


def test_score_always_non_negative(scorer):
    """Score should never be negative"""
    test_cases = [
        (0, 'beginner'),
        (-1, 'intermediary'),
        (100, 'senior'),
        (10, 'beginner')
    ]

    for pages, level in test_cases:
        result = scorer.score(page_count=pages, level=level)
        assert result['score'] >= 0, f"Score is negative for {pages} pages, {level} level"


def test_score_max_is_five(scorer):
    """Score should never exceed 5 points"""
    test_cases = [
        (1, 'beginner'),
        (1, 'intermediary'),
        (2, 'intermediary'),
        (2, 'senior')
    ]

    for pages, level in test_cases:
        result = scorer.score(page_count=pages, level=level)
        assert result['score'] <= 5, f"Score exceeds max for {pages} pages, {level} level"


# ============================================================================
# RECOMMENDATION QUALITY TESTS
# ============================================================================

def test_recommendation_is_actionable(scorer):
    """Recommendation should provide clear guidance"""
    result = scorer.score(page_count=3, level='beginner')

    recommendation = result['recommendation']
    assert len(recommendation) > 0
    assert isinstance(recommendation, str)
    # Should mention reducing page count or being concise
    assert any(word in recommendation.lower() for word in ['reduce', 'condense', 'shorten', 'brief', 'concise', 'long'])


def test_recommendation_for_optimal_is_positive(scorer):
    """Recommendation for optimal page count should be positive"""
    result = scorer.score(page_count=2, level='senior')

    recommendation = result['recommendation']
    # Should indicate it's good/optimal/perfect
    assert any(word in recommendation.lower() for word in ['optimal', 'perfect', 'good', 'ideal', 'appropriate'])


# ============================================================================
# CONVENIENCE FUNCTION TEST
# ============================================================================

def test_convenience_function_exists():
    """Convenience function score_page_count should exist and work"""
    from backend.services.parameters.p3_1_page_count import score_page_count

    result = score_page_count(page_count=2, level='senior')
    assert result['score'] == 5
    assert result['page_count'] == 2
    assert result['level'] == 'senior'
