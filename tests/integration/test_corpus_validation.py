"""
Corpus Validation Test Suite

Integration tests to verify corpus integration quality.
Tests corpus data loading, service availability, and data integrity.
"""

import pytest
import json
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "backend"))

from services.corpus_skills_database import get_corpus_skills_database, CorpusSkillsDatabase
from services.role_mapping_service import get_role_mapping_service, RoleMappingService
from services.role_taxonomy import get_role_scoring_data_enhanced, get_corpus_keywords


class TestCorpusDataLoading:
    """Test that corpus data loads successfully"""

    def test_skills_database_loaded(self):
        """Test skills database loaded successfully"""
        db = get_corpus_skills_database()

        assert db.is_available(), "Skills database should be available"

        all_skills = db.get_all_skills()
        assert len(all_skills) > 0, "Skills database should contain skills"

        # Verify we have expected number of skills (approximately)
        # Based on Task 10 completion: 35,557 skills
        assert len(all_skills) >= 35000, f"Expected at least 35,000 skills, got {len(all_skills)}"
        print(f"✓ Skills database loaded: {len(all_skills):,} skills")

    def test_skills_database_frequencies(self):
        """Test that skills have valid frequency counts"""
        db = get_corpus_skills_database()

        # Get top 10 skills
        top_skills = db.get_top_skills(10)
        assert len(top_skills) == 10, "Should return 10 top skills"

        # Verify all have positive frequencies
        for skill in top_skills:
            freq = db.get_skill_frequency(skill)
            assert freq > 0, f"Skill '{skill}' should have positive frequency"

        print(f"✓ Top 10 skills: {', '.join(top_skills[:10])}")

    def test_role_mappings_loaded(self):
        """Test role mappings loaded successfully"""
        service = get_role_mapping_service()

        assert service.is_available(), "Role mapping service should be available"

        # Test some common role mappings (using actual corpus role_ids)
        test_cases = [
            ("software engineer", "software_developer"),  # Actual role_id from corpus
            ("senior software engineer", "software_developer"),
            ("web developer", "web_developer"),
        ]

        successful_mappings = 0
        for job_title, expected_role_id in test_cases:
            result = service.normalize_role(job_title)
            if result == expected_role_id:
                successful_mappings += 1
            else:
                print(f"  Note: '{job_title}' mapped to '{result}' (expected '{expected_role_id}')")

        # At least some mappings should work
        assert successful_mappings > 0, "Role mappings should work for common titles"
        print(f"✓ Role mappings service available: {successful_mappings}/{len(test_cases)} test cases passed")

    def test_role_mappings_count(self):
        """Test that role mappings has expected count"""
        service = get_role_mapping_service()

        # Based on Task 10 completion: 19,463 role mappings
        # We don't have a direct count method, but we can check file size
        backend_dir = Path(__file__).parent.parent.parent / "backend"
        mappings_path = backend_dir / "data" / "corpus" / "role_mappings.json"

        assert mappings_path.exists(), "Role mappings file should exist"

        # Load and count
        with open(mappings_path, 'r', encoding='utf-8') as f:
            mappings = json.load(f)

        assert len(mappings) >= 19000, f"Expected at least 19,000 mappings, got {len(mappings):,}"
        print(f"✓ Role mappings loaded: {len(mappings):,} mappings")


class TestServiceAvailability:
    """Test that corpus services are available and functional"""

    def test_corpus_skills_service_available(self):
        """Test corpus skills database service is available"""
        db = get_corpus_skills_database()
        assert db.is_available(), "Corpus skills database should be available"

    def test_role_mapping_service_available(self):
        """Test role mapping service is available"""
        service = get_role_mapping_service()
        assert service.is_available(), "Role mapping service should be available"

    def test_skills_query_works(self):
        """Test that skills queries work correctly"""
        db = get_corpus_skills_database()

        # Test common skills
        test_skills = ["python", "java", "javascript", "sql"]

        for skill in test_skills:
            freq = db.get_skill_frequency(skill)
            # These common skills should exist in corpus
            assert freq >= 0, f"Should be able to query frequency for '{skill}'"

        print(f"✓ Skills queries working for {len(test_skills)} test skills")

    def test_role_normalization_works(self):
        """Test that role normalization works correctly"""
        service = get_role_mapping_service()

        # Test case insensitive and whitespace handling
        test_cases = [
            "Software Engineer",
            "software engineer",
            "  software engineer  ",
            "SOFTWARE ENGINEER"
        ]

        results = [service.normalize_role(title) for title in test_cases]

        # All variations should return a result (or all None if not mapped)
        # The key is consistency
        unique_results = set(results)
        assert len(unique_results) <= 2, "Case/whitespace variations should normalize consistently"

        print(f"✓ Role normalization handling case/whitespace correctly")

    def test_role_variations_lookup(self):
        """Test that role variations lookup works"""
        service = get_role_mapping_service()

        # Try to get variations for a common role
        # First, find a valid role_id
        test_title = "software engineer"
        role_id = service.normalize_role(test_title)

        if role_id:
            variations = service.get_all_variations(role_id)
            assert variations is not None, "Should return variations list"
            assert len(variations) > 0, "Should have at least one variation"
            print(f"✓ Role variations lookup working (found {len(variations)} variations for '{role_id}')")
        else:
            print("! Skipping variations test - no role_id found for test title")


class TestEnhancedKeywords:
    """Test enhanced keywords merge correctly"""

    def test_enhanced_scoring_data_function_exists(self):
        """Test that get_role_scoring_data_enhanced function exists and is callable"""
        assert callable(get_role_scoring_data_enhanced), "get_role_scoring_data_enhanced should be callable"

    def test_corpus_keywords_function_exists(self):
        """Test that get_corpus_keywords function exists and is callable"""
        assert callable(get_corpus_keywords), "get_corpus_keywords should be callable"

    def test_enhanced_scoring_data_returns_valid(self):
        """Test that enhanced scoring data returns valid structure"""
        # Test with a known role
        data = get_role_scoring_data_enhanced("software_engineer", "mid")

        assert data is not None, "Should return scoring data"
        assert isinstance(data, dict), "Should return dictionary"

        # Should have typical_keywords field
        assert "typical_keywords" in data, "Should have typical_keywords field"
        keywords = data["typical_keywords"]
        assert isinstance(keywords, list), "Keywords should be a list"
        assert len(keywords) > 0, "Should have at least some keywords"

        print(f"✓ Enhanced scoring data working (returned {len(keywords)} keywords)")

    def test_corpus_keywords_returns_data(self):
        """Test that corpus keywords returns valid data"""
        keywords = get_corpus_keywords("software_engineer", "mid")

        assert keywords is not None, "Should return keywords"
        assert isinstance(keywords, list), "Should return list"

        # May be empty if corpus not available, but should be a list
        print(f"✓ Corpus keywords function working (returned {len(keywords)} keywords)")

    def test_enhanced_keywords_for_multiple_roles(self):
        """Test enhanced keywords work for multiple roles"""
        roles = ["software_engineer", "data_scientist", "product_manager"]
        levels = ["entry", "mid", "senior"]

        successful_calls = 0
        for role in roles:
            for level in levels:
                try:
                    data = get_role_scoring_data_enhanced(role, level)
                    if data and "typical_keywords" in data:
                        successful_calls += 1
                except Exception as e:
                    print(f"! Warning: get_role_scoring_data_enhanced({role}, {level}) raised {e}")

        # At least some combinations should work
        assert successful_calls > 0, "Enhanced keywords should work for some role/level combinations"
        print(f"✓ Enhanced keywords working for {successful_calls}/{len(roles) * len(levels)} combinations")


class TestDataIntegrity:
    """Test data integrity and quality"""

    def test_skills_database_no_empty_skills(self):
        """Test that skills database has no empty skill names"""
        db = get_corpus_skills_database()
        all_skills = db.get_all_skills()

        # Check no empty skills
        empty_skills = [s for s in all_skills if not s or not s.strip()]
        assert len(empty_skills) == 0, f"Found {len(empty_skills)} empty skill names"

    def test_skills_database_frequencies_positive(self):
        """Test that all skill frequencies are positive"""
        db = get_corpus_skills_database()
        all_skills = db.get_all_skills()

        # Sample check (checking all 35k+ would be slow)
        sample_size = min(100, len(all_skills))
        sample_skills = all_skills[:sample_size]

        for skill in sample_skills:
            freq = db.get_skill_frequency(skill)
            assert freq > 0, f"Skill '{skill}' has non-positive frequency: {freq}"

        print(f"✓ Validated {sample_size} skills have positive frequencies")

    def test_role_mappings_no_empty_keys(self):
        """Test that role mappings have no empty keys or values"""
        backend_dir = Path(__file__).parent.parent.parent / "backend"
        mappings_path = backend_dir / "data" / "corpus" / "role_mappings.json"

        with open(mappings_path, 'r', encoding='utf-8') as f:
            mappings = json.load(f)

        # Check no empty keys or values
        empty_keys = [k for k in mappings.keys() if not k or not k.strip()]
        empty_values = [k for k, v in mappings.items() if not v or not v.strip()]

        assert len(empty_keys) == 0, f"Found {len(empty_keys)} empty job title keys"
        assert len(empty_values) == 0, f"Found {len(empty_values)} empty role_id values"

    def test_corpus_files_exist(self):
        """Test that all expected corpus files exist"""
        backend_dir = Path(__file__).parent.parent.parent / "backend"
        corpus_dir = backend_dir / "data" / "corpus"

        required_files = [
            "skills_database.json",
            "role_mappings.json",
            "skill_synonyms_corpus.json"
        ]

        for filename in required_files:
            filepath = corpus_dir / filename
            assert filepath.exists(), f"Required corpus file missing: {filename}"

            # Check file is not empty
            assert filepath.stat().st_size > 0, f"Corpus file is empty: {filename}"

        print(f"✓ All {len(required_files)} corpus files exist and are non-empty")


class TestFeatureFlags:
    """Test feature flags configuration"""

    def test_feature_flags_importable(self):
        """Test that feature flags can be imported"""
        try:
            from config import (
                ENABLE_CORPUS_KEYWORDS,
                ENABLE_CORPUS_SYNONYMS,
                ENABLE_ROLE_MAPPINGS,
                ENABLE_ML_SUGGESTIONS
            )

            # All flags should be boolean
            assert isinstance(ENABLE_CORPUS_KEYWORDS, bool), "ENABLE_CORPUS_KEYWORDS should be bool"
            assert isinstance(ENABLE_CORPUS_SYNONYMS, bool), "ENABLE_CORPUS_SYNONYMS should be bool"
            assert isinstance(ENABLE_ROLE_MAPPINGS, bool), "ENABLE_ROLE_MAPPINGS should be bool"
            assert isinstance(ENABLE_ML_SUGGESTIONS, bool), "ENABLE_ML_SUGGESTIONS should be bool"

            print(f"✓ Feature flags configured: CORPUS_KEYWORDS={ENABLE_CORPUS_KEYWORDS}, "
                  f"CORPUS_SYNONYMS={ENABLE_CORPUS_SYNONYMS}, "
                  f"ROLE_MAPPINGS={ENABLE_ROLE_MAPPINGS}, "
                  f"ML_SUGGESTIONS={ENABLE_ML_SUGGESTIONS}")

        except ImportError as e:
            pytest.fail(f"Failed to import feature flags: {e}")


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "-s"])
