"""
Tests for enhanced role taxonomy with hybrid keywords.
Tests the merging of manual and corpus-derived keywords.
"""

import pytest
from unittest.mock import patch, MagicMock
from backend.services.role_taxonomy import (
    get_role_scoring_data_enhanced,
    get_corpus_keywords,
)


class TestCorpusKeywords:
    """Test corpus keyword retrieval."""

    @patch('backend.services.corpus_skills_database.get_corpus_skills_database')
    def test_get_corpus_keywords_success(self, mock_get_db):
        """Test successful corpus keyword retrieval."""
        # Mock corpus service response
        mock_db = MagicMock()
        mock_db.is_available.return_value = True
        mock_db.get_top_skills.return_value = [
            'machine learning', 'python', 'tensorflow'
        ]
        mock_get_db.return_value = mock_db

        keywords = get_corpus_keywords('ml_engineer', 'mid')

        assert keywords == ['machine learning', 'python', 'tensorflow']
        mock_db.get_top_skills.assert_called_once_with(n=20)

    @patch('backend.services.corpus_skills_database.get_corpus_skills_database')
    def test_get_corpus_keywords_failure_returns_empty(self, mock_get_db):
        """Test corpus keyword retrieval failure returns empty list."""
        # Mock corpus service to raise exception
        mock_get_db.side_effect = Exception("Corpus unavailable")

        keywords = get_corpus_keywords('ml_engineer', 'mid')

        assert keywords == []

    @patch('backend.services.corpus_skills_database.get_corpus_skills_database')
    def test_get_corpus_keywords_no_service_returns_empty(self, mock_get_db):
        """Test corpus keyword retrieval with no service returns empty list."""
        # Mock corpus service as unavailable
        mock_db = MagicMock()
        mock_db.is_available.return_value = False
        mock_get_db.return_value = mock_db

        keywords = get_corpus_keywords('ml_engineer', 'mid')

        assert keywords == []


class TestEnhancedRoleScoringData:
    """Test enhanced role scoring data with hybrid keywords."""

    @patch('backend.config.ENABLE_CORPUS_KEYWORDS', True)
    @patch('backend.services.role_taxonomy.get_corpus_keywords')
    def test_enhanced_data_with_corpus_enabled(self, mock_get_corpus):
        """Test enhanced data returns merged keywords when corpus is enabled."""
        # Setup
        mock_get_corpus.return_value = ['python', 'tensorflow', 'deep learning']

        # Execute
        result = get_role_scoring_data_enhanced('data_scientist', 'mid')

        # Verify
        assert result is not None
        assert 'keywords' in result

        # Should contain both manual and corpus keywords
        keywords = result['keywords']
        assert 'python' in keywords
        assert 'tensorflow' in keywords
        assert 'deep learning' in keywords

        # Should also have manual keywords from base taxonomy
        assert len(keywords) > 3  # More than just corpus keywords

        mock_get_corpus.assert_called_once_with('data_scientist', 'mid')

    @patch('backend.config.ENABLE_CORPUS_KEYWORDS', False)
    @patch('backend.services.role_taxonomy.get_corpus_keywords')
    def test_enhanced_data_with_corpus_disabled(self, mock_get_corpus):
        """Test enhanced data returns only manual keywords when corpus is disabled."""
        # Execute
        result = get_role_scoring_data_enhanced('data_scientist', 'mid')

        # Verify
        assert result is not None
        assert 'keywords' in result

        # Should only have manual keywords
        keywords = result['keywords']
        assert len(keywords) > 0

        # Corpus service should not be called
        mock_get_corpus.assert_not_called()

    @patch('backend.config.ENABLE_CORPUS_KEYWORDS', True)
    @patch('backend.services.role_taxonomy.get_corpus_keywords')
    def test_enhanced_data_deduplicates_keywords(self, mock_get_corpus):
        """Test that duplicate keywords are removed when merging."""
        # Setup - return some keywords that overlap with manual keywords
        mock_get_corpus.return_value = ['python', 'machine learning', 'pytorch']

        # Execute
        result = get_role_scoring_data_enhanced('data_scientist', 'mid')

        # Verify
        keywords = result['keywords']

        # Check no duplicates (convert to lowercase set and compare lengths)
        keywords_lower = [k.lower() for k in keywords]
        assert len(keywords_lower) == len(set(keywords_lower)), "Keywords should be deduplicated"

    @patch('backend.config.ENABLE_CORPUS_KEYWORDS', True)
    @patch('backend.services.role_taxonomy.get_corpus_keywords')
    def test_enhanced_data_corpus_failure_fallback(self, mock_get_corpus):
        """Test graceful fallback when corpus service fails."""
        # Setup
        mock_get_corpus.return_value = []  # Corpus failed, returns empty

        # Execute
        result = get_role_scoring_data_enhanced('data_scientist', 'mid')

        # Verify - should still return manual keywords
        assert result is not None
        assert 'keywords' in result
        assert len(result['keywords']) > 0

    @patch('backend.config.ENABLE_CORPUS_KEYWORDS', True)
    @patch('backend.services.role_taxonomy.get_corpus_keywords')
    def test_enhanced_data_invalid_role(self, mock_get_corpus):
        """Test enhanced data with invalid role returns None."""
        # Execute
        result = get_role_scoring_data_enhanced('invalid_role', 'mid')

        # Verify
        assert result is None
        # Corpus should not be called for invalid role
        mock_get_corpus.assert_not_called()

    @patch('backend.config.ENABLE_CORPUS_KEYWORDS', True)
    @patch('backend.services.role_taxonomy.get_corpus_keywords')
    def test_enhanced_data_preserves_other_fields(self, mock_get_corpus):
        """Test that enhanced data preserves all other taxonomy fields."""
        # Setup
        mock_get_corpus.return_value = ['extra_keyword']

        # Execute
        result = get_role_scoring_data_enhanced('data_scientist', 'mid')

        # Verify all expected fields are present
        assert 'role_id' in result
        assert 'level' in result
        assert 'keywords' in result
        assert 'required_skills' in result
        # Note: preferred_skills is actually preferred_sections in the implementation
        assert 'preferred_sections' in result
        assert 'education' in result
        assert 'certifications' in result
        assert 'experience_years' in result

        # Verify field values are correct
        assert result['role_id'] == 'data_scientist'
        # Level can be either string or enum
        level_val = result['level']
        if hasattr(level_val, 'value'):
            assert level_val.value == 'mid'
        else:
            assert level_val == 'mid'

    @patch('backend.config.ENABLE_CORPUS_KEYWORDS', True)
    @patch('backend.services.role_taxonomy.get_corpus_keywords')
    def test_enhanced_data_case_insensitive_deduplication(self, mock_get_corpus):
        """Test that deduplication is case-insensitive."""
        # Setup - return keywords with different cases
        mock_get_corpus.return_value = ['Python', 'SQL', 'Machine Learning']

        # Execute
        result = get_role_scoring_data_enhanced('data_scientist', 'mid')

        # Verify - should deduplicate case-insensitively
        keywords = result['keywords']
        keywords_lower = [k.lower() for k in keywords]
        assert len(keywords_lower) == len(set(keywords_lower)), \
            "Keywords should be deduplicated case-insensitively"
