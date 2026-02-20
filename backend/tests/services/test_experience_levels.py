"""
Tests for 3-tier experience level system.

Based on comprehensive ATS research indicating 3 tiers (beginner, intermediary, senior)
are more effective than 5-tier systems for scoring accuracy.
"""
import pytest
from backend.services.role_taxonomy import ExperienceLevel, get_level_expectations


def test_experience_level_enum_has_three_tiers():
    """Verify 3-tier system: Beginner, Intermediary, Senior"""
    levels = list(ExperienceLevel)
    assert len(levels) == 3, f"Expected 3 levels, got {len(levels)}: {levels}"
    assert ExperienceLevel.BEGINNER in levels
    assert ExperienceLevel.INTERMEDIARY in levels
    assert ExperienceLevel.SENIOR in levels


def test_beginner_expectations():
    """Beginner: 0-3 years, 1 page, Tier 1.5+ verbs, 30% quantification"""
    expectations = get_level_expectations('beginner')
    assert expectations['years_range'] == (0, 3)
    assert expectations['page_count'] == 1
    assert expectations['min_verb_tier'] == 1.5
    assert expectations['quantification_threshold'] == 30


def test_intermediary_expectations():
    """Intermediary: 3-7 years, 1-2 pages, Tier 2+ verbs, 50% quantification"""
    expectations = get_level_expectations('intermediary')
    assert expectations['years_range'] == (3, 7)
    assert expectations['page_count'] in [1, 2] or expectations['page_count'] == [1, 2]
    assert expectations['min_verb_tier'] == 2.0
    assert expectations['quantification_threshold'] == 50


def test_senior_expectations():
    """Senior: 7+ years, 2 pages, Tier 2.5+ verbs, 60% quantification"""
    expectations = get_level_expectations('senior')
    assert expectations['years_range'] == (7, 100)
    assert expectations['page_count'] == 2
    assert expectations['min_verb_tier'] == 2.5
    assert expectations['quantification_threshold'] == 60


def test_experience_level_display_names():
    """Test display names are properly formatted"""
    assert ExperienceLevel.BEGINNER.display_name == 'Beginner (0-3 years)'
    assert ExperienceLevel.INTERMEDIARY.display_name == 'Intermediary (3-7 years)'
    assert ExperienceLevel.SENIOR.display_name == 'Senior Professional (7+ years)'


def test_experience_level_years_range():
    """Test years_range property on enum"""
    assert ExperienceLevel.BEGINNER.years_range == (0, 3)
    assert ExperienceLevel.INTERMEDIARY.years_range == (3, 7)
    assert ExperienceLevel.SENIOR.years_range == (7, 100)


def test_get_level_expectations_default():
    """Test that unknown levels default to intermediary"""
    expectations = get_level_expectations('unknown_level')
    intermediary = get_level_expectations('intermediary')
    assert expectations == intermediary


def test_level_expectations_structure():
    """Test that all required expectation fields are present"""
    required_fields = [
        'years_range', 'page_count', 'page_count_penalty',
        'word_count_optimal', 'word_count_acceptable',
        'min_verb_tier', 'verb_coverage_threshold',
        'quantification_threshold', 'experience_depth_minimum'
    ]

    for level in ['beginner', 'intermediary', 'senior']:
        expectations = get_level_expectations(level)
        for field in required_fields:
            assert field in expectations, f"Missing field '{field}' for {level}"
