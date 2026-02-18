"""
Tests for keyword matching engine with synonym support.
"""

import pytest
from backend.services.keyword_matcher import KeywordMatcher


def test_keyword_matcher_initialization():
    """Test that keyword matcher loads data correctly"""
    matcher = KeywordMatcher()

    # Should have loaded role keywords
    assert len(matcher.role_keywords) > 0
    assert "software_engineer_mid" in matcher.role_keywords

    # Should have loaded synonyms
    assert len(matcher.synonyms) > 0
    assert "python" in matcher.synonyms


def test_exact_keyword_match():
    """Test exact keyword matching"""
    matcher = KeywordMatcher()

    resume_text = "Experienced with Python, React, and AWS cloud services"
    keywords = ["python", "react", "aws", "docker"]

    result = matcher.match_keywords(resume_text, keywords)

    assert result['percentage'] == 75  # 3 out of 4
    assert "python" in result['matched']
    assert "react" in result['matched']
    assert "aws" in result['matched']
    assert "docker" in result['missing']


def test_synonym_keyword_match():
    """Test that synonyms are matched correctly"""
    matcher = KeywordMatcher()

    resume_text = "Python3 and ReactJS experience"
    keywords = ["python", "react"]

    result = matcher.match_keywords(resume_text, keywords)

    assert result['percentage'] == 100  # Both matched via synonyms
    assert "python" in result['matched']
    assert "react" in result['matched']


def test_case_insensitive_match():
    """Test case-insensitive matching"""
    matcher = KeywordMatcher()

    resume_text = "javascript and PYTHON skills"
    keywords = ["javascript", "python"]

    result = matcher.match_keywords(resume_text, keywords)

    assert result['percentage'] == 100


def test_role_based_matching():
    """Test matching against role-specific keywords"""
    matcher = KeywordMatcher()

    resume_text = "Python Django REST API development with PostgreSQL"

    result = matcher.match_role_keywords(resume_text, "software_engineer", "mid")

    assert result['percentage'] > 0
    assert 'matched' in result
    assert 'missing' in result


def test_bigram_matching():
    """Test that compound terms (bigrams) are matched correctly"""
    matcher = KeywordMatcher()

    resume_text = "Expert in machine learning and deep learning algorithms"
    keywords = ["machine learning", "deep learning", "computer vision"]

    result = matcher.match_keywords(resume_text, keywords)

    assert result['percentage'] == pytest.approx(66.66, rel=1)
    assert "machine learning" in result['matched']
    assert "deep learning" in result['matched']
    assert "computer vision" in result['missing']


def test_fuzzy_matching():
    """Test fuzzy matching with 80% threshold"""
    matcher = KeywordMatcher()

    # Slight typos that should still match
    resume_text = "Experience with kubernetes and postgresql database"
    keywords = ["kubernetes", "postgresql"]

    result = matcher.match_keywords(resume_text, keywords)

    assert result['percentage'] == 100
    assert "kubernetes" in result['matched']
    assert "postgresql" in result['matched']


def test_empty_keywords():
    """Test behavior with empty keyword list"""
    matcher = KeywordMatcher()

    resume_text = "Python Django experience"
    keywords = []

    result = matcher.match_keywords(resume_text, keywords)

    assert result['percentage'] == 0
    assert result['matched'] == []
    assert result['missing'] == []


def test_invalid_role():
    """Test handling of invalid role/level combination"""
    matcher = KeywordMatcher()

    resume_text = "Python Django experience"

    result = matcher.match_role_keywords(resume_text, "invalid_role", "invalid_level")

    assert result['percentage'] == 0
    assert 'error' in result


def test_match_job_description():
    """Test matching resume against job description"""
    matcher = KeywordMatcher()

    resume_text = "Python Django REST API development with PostgreSQL and Docker"
    job_description = """
    We are looking for a Python developer with Django experience.
    Must have knowledge of REST APIs, PostgreSQL, and Docker containers.
    Experience with AWS and CI/CD pipelines is a plus.
    """

    result = matcher.match_job_description(resume_text, job_description)

    assert result['percentage'] > 0
    assert 'matched' in result
    assert 'missing' in result
    # Should match python, django, postgresql, docker
    assert len(result['matched']) >= 4
