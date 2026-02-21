"""
Structural validation test for P1.1 Required Keywords Matcher
Tests that don't require downloading semantic model from HuggingFace
"""

import pytest
from backend.services.parameters.p1_1_required_keywords import RequiredKeywordsMatcher


def test_class_instantiation():
    """Test that RequiredKeywordsMatcher can be instantiated"""
    matcher = RequiredKeywordsMatcher()
    assert matcher is not None
    assert hasattr(matcher, 'hybrid_matcher')


def test_scoring_tiers_configuration():
    """Test that scoring tiers are correctly configured"""
    matcher = RequiredKeywordsMatcher()
    tiers = matcher.get_scoring_tiers()

    assert len(tiers) == 4
    assert tiers[0] == (60, 25)  # ≥60% = 25 pts
    assert tiers[1] == (40, 15)  # ≥40% = 15 pts
    assert tiers[2] == (25, 5)   # ≥25% = 5 pts
    assert tiers[3] == (0, 0)    # <25% = 0 pts


def test_match_threshold_configuration():
    """Test that match threshold is correctly set"""
    matcher = RequiredKeywordsMatcher()
    threshold = matcher.get_match_threshold()

    assert threshold == 0.6  # 60% semantic similarity


def test_empty_keywords_returns_full_score():
    """Test edge case: empty keywords list should return full score"""
    matcher = RequiredKeywordsMatcher()
    result = matcher.score([], "Any resume text", 'intermediary')

    assert result['score'] == 25
    assert result['max_score'] == 25
    assert result['match_percentage'] == 100.0
    assert result['matched_keywords'] == []
    assert result['unmatched_keywords'] == []
    assert result['match_details'] == {}
    assert 'tier_applied' in result


def test_result_structure():
    """Test that score() returns all required fields"""
    matcher = RequiredKeywordsMatcher()
    result = matcher.score([], "Test", 'intermediary')

    # Check all required keys exist
    required_keys = [
        'score', 'max_score', 'match_percentage',
        'matched_keywords', 'unmatched_keywords',
        'match_details', 'tier_applied'
    ]

    for key in required_keys:
        assert key in result, f"Missing required key: {key}"


def test_max_score_is_always_25():
    """Test that max_score is always 25"""
    matcher = RequiredKeywordsMatcher()
    result = matcher.score([], "Test", 'intermediary')

    assert result['max_score'] == 25


def test_match_percentage_bounds():
    """Test that match_percentage for empty keywords is 100"""
    matcher = RequiredKeywordsMatcher()
    result = matcher.score([], "Test", 'intermediary')

    assert result['match_percentage'] == 100.0
    assert 0 <= result['match_percentage'] <= 100


def test_score_bounds():
    """Test that score is within valid range"""
    matcher = RequiredKeywordsMatcher()
    result = matcher.score([], "Test", 'intermediary')

    assert result['score'] >= 0
    assert result['score'] <= 25
