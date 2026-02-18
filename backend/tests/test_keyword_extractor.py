"""
Tests for keyword extraction and classification from job descriptions.
"""

import pytest
from services.keyword_extractor import (
    extract_keywords_from_jd,
    match_with_synonyms,
)


class TestExtractRequiredKeywords:
    """Tests for extracting required keywords from job descriptions."""

    def test_extract_required_keywords(self):
        """Test extraction of required keywords from job description."""
        job_description = """
        We are seeking a talented engineer with the following skills:

        Required: Python, Docker, Kubernetes, AWS

        You will work on building scalable systems.
        """

        result = extract_keywords_from_jd(job_description)

        # Check that all required keywords are extracted
        assert "python" in result["required"]
        assert "docker" in result["required"]
        assert "kubernetes" in result["required"]
        assert "aws" in result["required"]

        # Check that they're also in the "all" list
        assert "python" in result["all"]
        assert "docker" in result["all"]
        assert "kubernetes" in result["all"]
        assert "aws" in result["all"]


class TestExtractPreferredKeywords:
    """Tests for extracting preferred keywords from job descriptions."""

    def test_extract_preferred_keywords(self):
        """Test extraction of preferred keywords from job description."""
        job_description = """
        We are seeking a talented engineer with the following skills:

        Required: Python, Docker

        Preferred: Terraform is a plus, Nice to have: PostgreSQL

        You will work on building scalable systems.
        """

        result = extract_keywords_from_jd(job_description)

        # Check that preferred keywords are extracted
        assert "terraform" in result["preferred"]
        assert "postgresql" in result["preferred"]

        # Check that required keywords are not in preferred
        assert "python" not in result["preferred"]
        assert "docker" not in result["preferred"]

        # Check that required keywords are in required
        assert "python" in result["required"]
        assert "docker" in result["required"]


class TestMatchWithSynonymsDirect:
    """Tests for direct keyword matching."""

    def test_match_with_synonyms_direct(self):
        """Test that direct keyword match works."""
        keyword = "python"
        text = "I am experienced with python and have built many applications"

        result = match_with_synonyms(keyword, text)

        assert result is True


class TestMatchWithSynonymsSynonym:
    """Tests for synonym-based keyword matching."""

    def test_match_with_synonyms_synonym(self):
        """Test that synonym matching works (kubernetes -> k8s)."""
        keyword = "kubernetes"
        text = "I have built distributed systems using k8s and docker"

        result = match_with_synonyms(keyword, text)

        assert result is True

    def test_match_with_synonyms_no_match(self):
        """Test that non-matching keywords return False."""
        keyword = "python"
        text = "I am experienced with Java and C++"

        result = match_with_synonyms(keyword, text)

        assert result is False
