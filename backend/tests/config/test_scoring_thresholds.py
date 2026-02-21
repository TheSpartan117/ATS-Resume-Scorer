import pytest
from backend.config.scoring_thresholds import (
    get_thresholds_for_level,
    BEGINNER_THRESHOLDS,
    INTERMEDIARY_THRESHOLDS,
    SENIOR_THRESHOLDS
)

def test_beginner_thresholds_structure():
    """Beginner thresholds should have all required keys"""
    thresholds = BEGINNER_THRESHOLDS

    # Page count
    assert 'page_count' in thresholds
    assert thresholds['page_count'] == 1

    # Action verbs
    assert 'action_verb_coverage_min' in thresholds
    assert 'action_verb_tier_avg_min' in thresholds

    # Quantification
    assert 'quantification_rate_min' in thresholds

    # Keywords
    assert 'required_keywords_threshold' in thresholds

    # Word count
    assert 'word_count_optimal_range' in thresholds

def test_intermediary_thresholds_structure():
    """Intermediary thresholds should have all required keys"""
    thresholds = INTERMEDIARY_THRESHOLDS

    assert 'page_count' in thresholds
    assert 'action_verb_coverage_min' in thresholds
    assert 'quantification_rate_min' in thresholds

def test_senior_thresholds_structure():
    """Senior thresholds should have all required keys"""
    thresholds = SENIOR_THRESHOLDS

    assert 'page_count' in thresholds
    assert 'action_verb_coverage_min' in thresholds
    assert 'quantification_rate_min' in thresholds

def test_get_thresholds_for_beginner():
    """Should return beginner thresholds"""
    thresholds = get_thresholds_for_level('beginner')

    assert thresholds == BEGINNER_THRESHOLDS
    assert thresholds['page_count'] == 1

def test_get_thresholds_for_intermediary():
    """Should return intermediary thresholds"""
    thresholds = get_thresholds_for_level('intermediary')

    assert thresholds == INTERMEDIARY_THRESHOLDS
    assert thresholds['page_count'] == [1, 2]

def test_get_thresholds_for_senior():
    """Should return senior thresholds"""
    thresholds = get_thresholds_for_level('senior')

    assert thresholds == SENIOR_THRESHOLDS
    assert thresholds['page_count'] == 2

def test_case_insensitive_level_lookup():
    """Should handle case-insensitive level names"""
    assert get_thresholds_for_level('BEGINNER') == BEGINNER_THRESHOLDS
    assert get_thresholds_for_level('Intermediary') == INTERMEDIARY_THRESHOLDS
    assert get_thresholds_for_level('SENIOR') == SENIOR_THRESHOLDS

def test_default_to_intermediary():
    """Invalid level should default to intermediary"""
    thresholds = get_thresholds_for_level('invalid_level')

    assert thresholds == INTERMEDIARY_THRESHOLDS

def test_thresholds_progression():
    """Thresholds should increase with seniority"""
    # Action verb coverage should increase
    assert BEGINNER_THRESHOLDS['action_verb_coverage_min'] < \
           INTERMEDIARY_THRESHOLDS['action_verb_coverage_min'] < \
           SENIOR_THRESHOLDS['action_verb_coverage_min']

    # Quantification rate should increase
    assert BEGINNER_THRESHOLDS['quantification_rate_min'] < \
           INTERMEDIARY_THRESHOLDS['quantification_rate_min'] < \
           SENIOR_THRESHOLDS['quantification_rate_min']

    # Action verb tier average should increase
    assert BEGINNER_THRESHOLDS['action_verb_tier_avg_min'] < \
           INTERMEDIARY_THRESHOLDS['action_verb_tier_avg_min'] < \
           SENIOR_THRESHOLDS['action_verb_tier_avg_min']

def test_keyword_thresholds_realistic():
    """Keyword thresholds should be realistic (not >100%)"""
    for thresholds in [BEGINNER_THRESHOLDS, INTERMEDIARY_THRESHOLDS, SENIOR_THRESHOLDS]:
        assert 0 <= thresholds['required_keywords_threshold'] <= 100
        assert 0 <= thresholds['preferred_keywords_threshold'] <= 100
