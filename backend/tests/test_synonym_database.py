"""
Test suite for synonym database module.
"""

import pytest
from services.synonym_database import get_all_synonyms, expand_keywords


def test_get_synonyms_programming_language():
    """Test that 'python' returns its synonyms."""
    synonyms = get_all_synonyms("python")
    assert "py" in synonyms
    assert "python3" in synonyms
    assert "python" in synonyms  # Should include the keyword itself


def test_get_synonyms_reverse_lookup():
    """Test that 'k8s' returns 'kubernetes' (reverse lookup)."""
    synonyms = get_all_synonyms("k8s")
    assert "kubernetes" in synonyms
    assert "k8s" in synonyms


def test_expand_keywords():
    """Test that keyword list expands to include all synonyms."""
    keywords = ["python", "aws"]
    expanded = expand_keywords(keywords)

    # Should include original keywords
    assert "python" in expanded
    assert "aws" in expanded

    # Should include synonyms
    assert "py" in expanded
    assert "python3" in expanded
    assert "amazon web services" in expanded

    # Should not have duplicates
    assert len(expanded) == len(set(expanded))
