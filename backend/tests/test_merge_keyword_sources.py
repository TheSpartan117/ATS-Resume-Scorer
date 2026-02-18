"""Tests for keyword sources merger"""
import pytest
import json
from pathlib import Path
from backend.scripts.merge_keyword_sources import (
    load_existing_taxonomy,
    merge_keyword_sources,
    EXPERIENCE_LEVELS,
    ALL_ROLES
)


def test_experience_levels():
    """Test that all 5 experience levels are defined"""
    assert len(EXPERIENCE_LEVELS) == 5
    assert EXPERIENCE_LEVELS == ["entry", "mid", "senior", "lead", "executive"]


def test_all_roles_defined():
    """Test that all 22 roles are defined"""
    assert len(ALL_ROLES) == 22
    expected_roles = [
        "software_engineer", "data_scientist", "devops_engineer",
        "product_manager", "technical_product_manager",
        "ux_designer", "ui_designer", "product_designer",
        "marketing_manager", "sales_manager", "business_analyst",
        "operations_manager", "financial_analyst", "accountant",
        "hr_manager", "recruiter", "customer_success_manager",
        "corporate_lawyer", "content_writer",
        "qa_engineer", "data_engineer", "project_manager"
    ]
    assert set(ALL_ROLES) == set(expected_roles)


def test_load_existing_taxonomy():
    """Test extraction of keywords from role_taxonomy.py"""
    keywords_by_role_level = load_existing_taxonomy()

    # Should have extracted keywords for all roles
    assert len(keywords_by_role_level) > 0

    # Check software_engineer has keywords for all levels
    assert "software_engineer" in keywords_by_role_level
    se_keywords = keywords_by_role_level["software_engineer"]

    # Should have all 5 levels
    for level in EXPERIENCE_LEVELS:
        assert level in se_keywords
        assert len(se_keywords[level]) > 0

    # Check specific keywords exist
    assert "python" in se_keywords["entry"]
    assert "architecture" in se_keywords["mid"]


def test_merged_keywords_exist():
    """Test that merged keywords file is created"""
    data_dir = Path(__file__).parent.parent / "data" / "keywords"
    output_path = data_dir / "role_keywords.json"

    # Run merger
    merge_keyword_sources()

    # Check file exists
    assert output_path.exists()

    # Load and verify structure
    with open(output_path, 'r') as f:
        merged = json.load(f)

    # Should have 110 combinations (22 roles × 5 levels)
    assert len(merged) == 110

    # Check specific role/level combinations exist
    assert "software_engineer_entry" in merged
    assert "data_scientist_senior" in merged
    assert "product_manager_executive" in merged


def test_keyword_counts_per_role_level():
    """Test that each role/level has 50-200 keywords"""
    data_dir = Path(__file__).parent.parent / "data" / "keywords"
    output_path = data_dir / "role_keywords.json"

    with open(output_path, 'r') as f:
        merged = json.load(f)

    # Check keyword counts
    for role_level, keywords in merged.items():
        assert isinstance(keywords, list)
        assert len(keywords) >= 50, f"{role_level} has only {len(keywords)} keywords (expected 50-200)"
        assert len(keywords) <= 200, f"{role_level} has {len(keywords)} keywords (expected 50-200 max)"


def test_keywords_are_lowercase():
    """Test that all keywords are lowercase"""
    data_dir = Path(__file__).parent.parent / "data" / "keywords"
    output_path = data_dir / "role_keywords.json"

    with open(output_path, 'r') as f:
        merged = json.load(f)

    for role_level, keywords in merged.items():
        for keyword in keywords:
            assert keyword == keyword.lower(), f"Keyword '{keyword}' in {role_level} is not lowercase"


def test_keywords_are_deduplicated():
    """Test that keywords within each role/level are unique"""
    data_dir = Path(__file__).parent.parent / "data" / "keywords"
    output_path = data_dir / "role_keywords.json"

    with open(output_path, 'r') as f:
        merged = json.load(f)

    for role_level, keywords in merged.items():
        assert len(keywords) == len(set(keywords)), f"{role_level} has duplicate keywords"


def test_keywords_are_sorted():
    """Test that keywords are sorted alphabetically"""
    data_dir = Path(__file__).parent.parent / "data" / "keywords"
    output_path = data_dir / "role_keywords.json"

    with open(output_path, 'r') as f:
        merged = json.load(f)

    for role_level, keywords in merged.items():
        assert keywords == sorted(keywords), f"{role_level} keywords are not sorted"


def test_level_specific_keywords():
    """Test that level-specific keywords are added"""
    data_dir = Path(__file__).parent.parent / "data" / "keywords"
    output_path = data_dir / "role_keywords.json"

    with open(output_path, 'r') as f:
        merged = json.load(f)

    # Entry level should have learning-related keywords
    entry_keywords = merged["software_engineer_entry"]
    assert "learning" in entry_keywords or "training" in entry_keywords

    # Senior+ levels should have leadership keywords
    senior_keywords = merged["software_engineer_senior"]
    assert "leadership" in senior_keywords or "strategy" in senior_keywords or "mentoring" in senior_keywords


def test_merges_all_three_sources():
    """Test that merger combines O*NET, LinkedIn, and taxonomy keywords"""
    data_dir = Path(__file__).parent.parent / "data" / "keywords"
    output_path = data_dir / "role_keywords.json"

    # Load source files
    with open(data_dir / "onet_skills.json", 'r') as f:
        onet_data = json.load(f)

    with open(data_dir / "linkedin_skills.json", 'r') as f:
        linkedin_data = json.load(f)

    with open(output_path, 'r') as f:
        merged = json.load(f)

    # Check software_engineer_mid has keywords from all sources
    se_mid_keywords = set(merged["software_engineer_mid"])

    # Should include O*NET skills
    if "software_engineer" in onet_data:
        onet_skills = set(onet_data["software_engineer"].get("core_skills", []))
        # At least some O*NET skills should be present
        assert len(se_mid_keywords & onet_skills) > 0, "No O*NET skills found in merged data"

    # Should include LinkedIn skills
    if "software_engineer" in linkedin_data:
        linkedin_skills = set(linkedin_data["software_engineer"].get("trending_skills", []))
        # At least some LinkedIn skills should be present
        assert len(se_mid_keywords & linkedin_skills) > 0, "No LinkedIn skills found in merged data"


def test_all_role_level_combinations():
    """Test that all 110 role/level combinations are present"""
    data_dir = Path(__file__).parent.parent / "data" / "keywords"
    output_path = data_dir / "role_keywords.json"

    with open(output_path, 'r') as f:
        merged = json.load(f)

    # Generate expected combinations
    expected_keys = [
        f"{role}_{level}"
        for role in ALL_ROLES
        for level in EXPERIENCE_LEVELS
    ]

    assert len(expected_keys) == 110
    assert set(merged.keys()) == set(expected_keys)
