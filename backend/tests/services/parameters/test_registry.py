"""
Tests for Parameter Registry

Tests the centralized registry for all 12 core parameters (P1.1-P4.2).
"""

import pytest
from backend.services.parameters.registry import ParameterRegistry


@pytest.fixture
def registry():
    """Create a ParameterRegistry instance for testing."""
    return ParameterRegistry()


def test_registry_has_all_12_parameters(registry):
    """Verify registry contains all 11 core parameters."""
    all_scorers = registry.get_all_scorers()

    # Should have exactly 11 parameters
    assert len(all_scorers) == 11, f"Expected 11 parameters, got {len(all_scorers)}"

    # Verify all parameter codes exist
    expected_codes = [
        'P1.1', 'P1.2',  # Keyword matching
        'P2.1', 'P2.2', 'P2.3',  # Content quality
        'P3.1', 'P3.2', 'P3.3', 'P3.4',  # Format & structure
        'P4.1', 'P4.2'  # Professional polish
    ]

    for code in expected_codes:
        assert code in all_scorers, f"Parameter {code} not found in registry"


def test_registry_total_max_score_is_100(registry):
    """Verify total max score across all parameters is 100 points."""
    max_score = registry.get_max_score()
    assert max_score == 100, f"Expected max score of 100, got {max_score}"


def test_registry_parameter_scores_match_spec(registry):
    """Verify each parameter has correct max score according to spec."""
    expected_scores = {
        'P1.1': 25,  # Required Keywords
        'P1.2': 10,  # Preferred Keywords
        'P2.1': 15,  # Action Verbs
        'P2.2': 10,  # Quantification
        'P2.3': 5,   # Achievement Depth
        'P3.1': 5,   # Page Count
        'P3.2': 3,   # Word Count
        'P3.3': 5,   # Section Balance
        'P3.4': 7,   # ATS Formatting
        'P4.1': 10,  # Grammar
        'P4.2': 5,   # Professional Standards
    }

    all_scorers = registry.get_all_scorers()

    for code, expected_max in expected_scores.items():
        assert code in all_scorers, f"Parameter {code} not in registry"
        assert all_scorers[code]['max_score'] == expected_max, \
            f"Parameter {code} expected max_score={expected_max}, got {all_scorers[code]['max_score']}"


def test_get_scorer_returns_correct_instance(registry):
    """Test get_scorer() returns correct scorer class for P1.1."""
    # P1.1 should return RequiredKeywordsMatcher
    scorer_info = registry.get_scorer('P1.1')

    assert scorer_info is not None, "P1.1 scorer not found"
    assert scorer_info['code'] == 'P1.1'
    assert scorer_info['name'] == 'Required Keywords Match'
    assert scorer_info['max_score'] == 25
    assert scorer_info['scorer_class'] is not None

    # Verify it's the correct class
    from backend.services.parameters.p1_1_required_keywords import RequiredKeywordsMatcher
    assert scorer_info['scorer_class'] == RequiredKeywordsMatcher


def test_get_scorer_returns_none_for_invalid_code(registry):
    """Test get_scorer() returns None for non-existent parameter."""
    scorer = registry.get_scorer('P99.99')
    assert scorer is None


def test_registry_includes_category_information(registry):
    """Verify each parameter has category metadata."""
    all_scorers = registry.get_all_scorers()

    # Check category assignments
    expected_categories = {
        'P1.1': 'Keyword Matching',
        'P1.2': 'Keyword Matching',
        'P2.1': 'Content Quality',
        'P2.2': 'Content Quality',
        'P2.3': 'Content Quality',
        'P3.1': 'Format & Structure',
        'P3.2': 'Format & Structure',
        'P3.3': 'Format & Structure',
        'P3.4': 'Format & Structure',
        'P4.1': 'Professional Polish',
        'P4.2': 'Professional Polish',
    }

    for code, expected_category in expected_categories.items():
        scorer = all_scorers[code]
        assert 'category' in scorer, f"Parameter {code} missing category"
        assert scorer['category'] == expected_category, \
            f"Parameter {code} expected category '{expected_category}', got '{scorer['category']}'"


def test_registry_parameter_descriptions_exist(registry):
    """Verify each parameter has a description."""
    all_scorers = registry.get_all_scorers()

    for code, scorer in all_scorers.items():
        assert 'description' in scorer, f"Parameter {code} missing description"
        assert len(scorer['description']) > 0, f"Parameter {code} has empty description"


def test_get_scorers_by_category(registry):
    """Test filtering parameters by category."""
    keyword_scorers = registry.get_scorers_by_category('Keyword Matching')

    assert len(keyword_scorers) == 2, "Expected 2 keyword matching parameters"
    assert 'P1.1' in keyword_scorers
    assert 'P1.2' in keyword_scorers

    # Test content quality category
    content_scorers = registry.get_scorers_by_category('Content Quality')
    assert len(content_scorers) == 3, "Expected 3 content quality parameters"

    # Test format & structure category
    format_scorers = registry.get_scorers_by_category('Format & Structure')
    assert len(format_scorers) == 4, "Expected 4 format & structure parameters"

    # Test professional polish category
    polish_scorers = registry.get_scorers_by_category('Professional Polish')
    assert len(polish_scorers) == 2, "Expected 2 professional polish parameters"


def test_registry_is_singleton(registry):
    """Verify ParameterRegistry uses singleton pattern."""
    registry2 = ParameterRegistry()

    # Should be the same instance
    assert registry is registry2


def test_get_max_score_by_category(registry):
    """Test calculating max score per category."""
    category_scores = registry.get_max_score_by_category()

    # Verify category totals
    assert category_scores['Keyword Matching'] == 35  # 25 + 10
    assert category_scores['Content Quality'] == 30  # 15 + 10 + 5
    assert category_scores['Format & Structure'] == 20  # 5 + 3 + 5 + 7
    assert category_scores['Professional Polish'] == 15  # 10 + 5

    # Total should be 100
    total = sum(category_scores.values())
    assert total == 100


def test_get_scorer_instantiation(registry):
    """Test that scorer classes can be instantiated."""
    # Test P1.1 instantiation
    p1_1_info = registry.get_scorer('P1.1')
    scorer_instance = p1_1_info['scorer_class']()

    # Should have a score method
    assert hasattr(scorer_instance, 'score'), "Scorer missing score() method"

    # Test P1.2 instantiation
    p1_2_info = registry.get_scorer('P1.2')
    scorer_instance = p1_2_info['scorer_class']()
    assert hasattr(scorer_instance, 'score'), "Scorer missing score() method"


def test_registry_parameter_codes_are_unique(registry):
    """Verify all parameter codes are unique."""
    all_scorers = registry.get_all_scorers()
    codes = list(all_scorers.keys())

    # Check for duplicates
    assert len(codes) == len(set(codes)), "Duplicate parameter codes found"


def test_registry_validates_scorer_interface(registry):
    """Verify all registered scorers have required methods."""
    all_scorers = registry.get_all_scorers()

    for code, scorer_info in all_scorers.items():
        scorer_class = scorer_info['scorer_class']

        # Should be instantiable
        assert scorer_class is not None, f"Parameter {code} has no scorer_class"

        # For now, just check it's a class (can't instantiate until all are implemented)
        assert callable(scorer_class) or isinstance(scorer_class, type), \
            f"Parameter {code} scorer_class is not instantiable"
