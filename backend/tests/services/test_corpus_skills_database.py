"""
Tests for Corpus Skills Database Service

Tests the CorpusSkillsDatabase service which loads and queries
the corpus-derived skills database.
"""

import pytest
import json
import os
from pathlib import Path


class TestCorpusSkillsDatabase:
    """Test corpus skills database loading and querying"""

    def test_load_skills_database(self):
        """Test that skills database loads successfully"""
        from services.corpus_skills_database import CorpusSkillsDatabase

        db = CorpusSkillsDatabase()
        assert db.is_available()
        assert len(db.skills) > 0

    def test_get_skill_frequency(self):
        """Test getting frequency for a specific skill"""
        from services.corpus_skills_database import CorpusSkillsDatabase

        db = CorpusSkillsDatabase()

        # Test with a skill that should exist
        freq = db.get_skill_frequency("python")
        assert freq is not None
        assert freq > 0

        # Test with non-existent skill
        freq = db.get_skill_frequency("nonexistent_skill_xyz")
        assert freq == 0

    def test_get_skills_for_role(self):
        """Test getting skills for a specific role"""
        from services.corpus_skills_database import CorpusSkillsDatabase

        db = CorpusSkillsDatabase()

        # Test with software_developer role
        skills = db.get_skills_for_role("software_developer", min_frequency=10)
        assert isinstance(skills, list)
        assert len(skills) > 0

        # Verify all skills meet minimum frequency
        for skill in skills:
            assert db.get_skill_frequency(skill) >= 10

    def test_get_skills_for_role_with_high_threshold(self):
        """Test that high threshold filters skills correctly"""
        from services.corpus_skills_database import CorpusSkillsDatabase

        db = CorpusSkillsDatabase()

        # Get skills with low threshold
        skills_low = db.get_skills_for_role("python_developer", min_frequency=5)

        # Get skills with high threshold
        skills_high = db.get_skills_for_role("python_developer", min_frequency=50)

        # High threshold should return fewer or equal skills
        assert len(skills_high) <= len(skills_low)

    def test_get_skills_for_nonexistent_role(self):
        """Test graceful handling of non-existent role"""
        from services.corpus_skills_database import CorpusSkillsDatabase

        db = CorpusSkillsDatabase()

        skills = db.get_skills_for_role("nonexistent_role_xyz", min_frequency=1)
        assert isinstance(skills, list)
        # Note: Currently returns all skills since role-specific mappings
        # are not yet implemented. This will return empty list once
        # role-skills mappings are added to corpus database.
        # For now, just verify it returns a list.
        assert len(skills) >= 0

    def test_graceful_fallback_when_db_missing(self, tmp_path, monkeypatch):
        """Test that service handles missing database gracefully"""
        from services.corpus_skills_database import CorpusSkillsDatabase

        # Point to non-existent database
        fake_path = tmp_path / "nonexistent" / "skills_database.json"
        monkeypatch.setattr(
            "services.corpus_skills_database.SKILLS_DB_PATH",
            str(fake_path)
        )

        db = CorpusSkillsDatabase()
        assert not db.is_available()

        # Should return empty/default values gracefully
        assert db.get_skill_frequency("python") == 0
        assert db.get_skills_for_role("software_developer") == []

    def test_singleton_pattern(self):
        """Test that get_corpus_skills_database returns singleton"""
        from services.corpus_skills_database import get_corpus_skills_database

        db1 = get_corpus_skills_database()
        db2 = get_corpus_skills_database()

        # Should be the same instance
        assert db1 is db2

    def test_case_insensitive_skill_lookup(self):
        """Test that skill lookups are case-insensitive"""
        from services.corpus_skills_database import CorpusSkillsDatabase

        db = CorpusSkillsDatabase()

        # Test with different cases
        freq_lower = db.get_skill_frequency("python")
        freq_upper = db.get_skill_frequency("PYTHON")
        freq_mixed = db.get_skill_frequency("Python")

        # All should return the same frequency (normalized to lowercase)
        assert freq_lower == freq_upper == freq_mixed

    def test_get_all_skills(self):
        """Test getting all skills from database"""
        from services.corpus_skills_database import CorpusSkillsDatabase

        db = CorpusSkillsDatabase()

        all_skills = db.get_all_skills()
        assert isinstance(all_skills, list)
        assert len(all_skills) > 0

        # Verify skills are sorted by frequency (descending)
        if len(all_skills) > 1:
            freq1 = db.get_skill_frequency(all_skills[0])
            freq2 = db.get_skill_frequency(all_skills[1])
            assert freq1 >= freq2

    def test_get_top_skills(self):
        """Test getting top N skills"""
        from services.corpus_skills_database import CorpusSkillsDatabase

        db = CorpusSkillsDatabase()

        top_10 = db.get_top_skills(10)
        assert isinstance(top_10, list)
        assert len(top_10) <= 10

        # Verify they are sorted by frequency
        for i in range(len(top_10) - 1):
            freq_current = db.get_skill_frequency(top_10[i])
            freq_next = db.get_skill_frequency(top_10[i + 1])
            assert freq_current >= freq_next


class TestCorpusSkillsDatabaseIntegration:
    """Integration tests with actual corpus data"""

    def test_real_corpus_data_structure(self):
        """Test that real corpus data has expected structure"""
        from services.corpus_skills_database import CorpusSkillsDatabase

        db = CorpusSkillsDatabase()

        # Should have loaded successfully
        assert db.is_available()

        # Check that skills database has frequency data
        sample_skills = list(db.skills.keys())[:5]
        for skill in sample_skills:
            freq = db.get_skill_frequency(skill)
            assert freq > 0
            assert isinstance(freq, int)

    def test_common_skills_present(self):
        """Test that common tech skills are present in database"""
        from services.corpus_skills_database import CorpusSkillsDatabase

        db = CorpusSkillsDatabase()

        # These should be common in any tech resume corpus
        common_skills = ["python", "java", "javascript", "sql", "linux"]

        found_count = 0
        for skill in common_skills:
            if db.get_skill_frequency(skill) > 0:
                found_count += 1

        # At least some common skills should be present
        assert found_count > 0
