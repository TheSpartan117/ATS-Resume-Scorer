"""
Tests for LinkedIn skills scraper (mock data generator).
"""

import pytest
import json
from pathlib import Path
import sys

# Add backend to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.scrape_linkedin_skills import generate_mock_linkedin_skills, ROLES


def test_generate_mock_skills():
    """Test that mock skills are generated correctly"""
    skills_data = generate_mock_linkedin_skills()

    # Should have all 7 roles
    assert len(skills_data) == 7

    # Check each role has required structure
    for role_name in ROLES:
        assert role_name in skills_data
        assert isinstance(skills_data[role_name], list)

        # Should have 50-100 skills per role
        skills_count = len(skills_data[role_name])
        assert 50 <= skills_count <= 100, f"{role_name} has {skills_count} skills, expected 50-100"

        # All skills should be lowercase strings
        for skill in skills_data[role_name]:
            assert isinstance(skill, str)
            assert skill == skill.lower()


def test_software_engineer_has_modern_tech():
    """Test that Software Engineer includes modern tech terms"""
    skills_data = generate_mock_linkedin_skills()
    se_skills = skills_data["Software Engineer"]

    # Check for modern tech that O*NET might not have
    modern_tech = ["kubernetes", "docker", "react", "typescript", "graphql"]

    for tech in modern_tech:
        assert tech in se_skills, f"Software Engineer should include {tech}"


def test_data_scientist_has_ml_skills():
    """Test that Data Scientist includes ML/AI skills"""
    skills_data = generate_mock_linkedin_skills()
    ds_skills = skills_data["Data Scientist"]

    # Check for ML/AI terms
    ml_skills = ["machine learning", "python", "sql", "tensorflow", "pytorch"]

    for skill in ml_skills:
        assert skill in ds_skills, f"Data Scientist should include {skill}"


def test_devops_has_infrastructure_tools():
    """Test that DevOps Engineer includes infrastructure tools"""
    skills_data = generate_mock_linkedin_skills()
    devops_skills = skills_data["DevOps Engineer"]

    # Check for DevOps tools
    devops_tools = ["kubernetes", "terraform", "docker", "jenkins", "aws"]

    for tool in devops_tools:
        assert tool in devops_skills, f"DevOps Engineer should include {tool}"


def test_no_duplicate_skills_per_role():
    """Test that each role has no duplicate skills"""
    skills_data = generate_mock_linkedin_skills()

    for role_name, skills in skills_data.items():
        assert len(skills) == len(set(skills)), f"{role_name} has duplicate skills"


def test_skills_are_realistic():
    """Test that skills don't contain obvious test data or placeholders"""
    skills_data = generate_mock_linkedin_skills()

    invalid_terms = ["placeholder", "xxx", "todo", "fixme"]

    for role_name, skills in skills_data.items():
        for skill in skills:
            for invalid_term in invalid_terms:
                assert invalid_term not in skill.lower(), \
                    f"{role_name} has invalid term '{invalid_term}' in skill: {skill}"


def test_output_file_structure():
    """Test that output file has correct JSON structure"""
    from scripts.scrape_linkedin_skills import main

    # Generate and save to temp location
    output_path = Path(__file__).parent.parent / "data" / "keywords" / "linkedin_skills.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Run the script
    result_path = main()

    # Verify file exists
    assert result_path.exists()

    # Load and verify structure
    with open(result_path, 'r') as f:
        data = json.load(f)

    # Should be dict with role names as keys
    assert isinstance(data, dict)
    assert len(data) == 7

    for role_name, skills in data.items():
        assert isinstance(role_name, str)
        assert isinstance(skills, list)
        assert all(isinstance(s, str) for s in skills)
