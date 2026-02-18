"""
Tests for LinkedIn skills scraper (mock data generator).
"""

import pytest
import json
from pathlib import Path
import sys

# Add backend to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.scrape_linkedin_skills import generate_mock_linkedin_skills, ROLES, role_name_to_id


def test_generate_mock_skills():
    """Test that mock skills are generated correctly"""
    skills_data = generate_mock_linkedin_skills()

    # Should have all 7 roles
    assert len(skills_data) == 7

    # Check each role has required structure
    for role_name in ROLES:
        role_id = role_name_to_id(role_name)

        # Check role_id exists
        assert role_id in skills_data, f"Missing role_id: {role_id}"

        # Check nested structure
        assert isinstance(skills_data[role_id], dict), f"{role_id} should be a dict"
        assert "role_name" in skills_data[role_id], f"{role_id} missing 'role_name'"
        assert "trending_skills" in skills_data[role_id], f"{role_id} missing 'trending_skills'"

        # Verify role_name matches
        assert skills_data[role_id]["role_name"] == role_name

        # Verify trending_skills is a list
        assert isinstance(skills_data[role_id]["trending_skills"], list)

        # Should have 50-100 skills per role
        skills_count = len(skills_data[role_id]["trending_skills"])
        assert 50 <= skills_count <= 100, f"{role_name} has {skills_count} skills, expected 50-100"

        # All skills should be lowercase strings
        for skill in skills_data[role_id]["trending_skills"]:
            assert isinstance(skill, str)
            assert skill == skill.lower()


def test_software_engineer_has_modern_tech():
    """Test that Software Engineer includes modern tech terms"""
    skills_data = generate_mock_linkedin_skills()
    se_skills = skills_data["software_engineer"]["trending_skills"]

    # Check for modern tech that O*NET might not have
    modern_tech = ["kubernetes", "docker", "react", "typescript", "graphql"]

    for tech in modern_tech:
        assert tech in se_skills, f"Software Engineer should include {tech}"


def test_data_scientist_has_ml_skills():
    """Test that Data Scientist includes ML/AI skills"""
    skills_data = generate_mock_linkedin_skills()
    ds_skills = skills_data["data_scientist"]["trending_skills"]

    # Check for ML/AI terms
    ml_skills = ["machine learning", "python", "sql", "tensorflow", "pytorch"]

    for skill in ml_skills:
        assert skill in ds_skills, f"Data Scientist should include {skill}"


def test_devops_has_infrastructure_tools():
    """Test that DevOps Engineer includes infrastructure tools"""
    skills_data = generate_mock_linkedin_skills()
    devops_skills = skills_data["devops_engineer"]["trending_skills"]

    # Check for DevOps tools
    devops_tools = ["kubernetes", "terraform", "docker", "jenkins", "aws"]

    for tool in devops_tools:
        assert tool in devops_skills, f"DevOps Engineer should include {tool}"


def test_no_duplicate_skills_per_role():
    """Test that each role has no duplicate skills"""
    skills_data = generate_mock_linkedin_skills()

    for role_id, role_data in skills_data.items():
        skills = role_data["trending_skills"]
        role_name = role_data["role_name"]
        assert len(skills) == len(set(skills)), f"{role_name} (id: {role_id}) has duplicate skills"


def test_skills_are_realistic():
    """Test that skills don't contain obvious test data or placeholders"""
    skills_data = generate_mock_linkedin_skills()

    invalid_terms = ["placeholder", "xxx", "todo", "fixme"]

    for role_id, role_data in skills_data.items():
        role_name = role_data["role_name"]
        skills = role_data["trending_skills"]
        for skill in skills:
            for invalid_term in invalid_terms:
                assert invalid_term not in skill.lower(), \
                    f"{role_name} has invalid term '{invalid_term}' in skill: {skill}"


def test_role_name_to_id_conversion():
    """Test that role names are correctly converted to role_ids"""
    test_cases = {
        "Software Engineer": "software_engineer",
        "Data Scientist": "data_scientist",
        "DevOps Engineer": "devops_engineer",
        "Product Manager": "product_manager",
        "UX Designer": "ux_designer",
        "Data Engineer": "data_engineer",
        "QA Engineer": "qa_engineer"
    }

    for role_name, expected_id in test_cases.items():
        actual_id = role_name_to_id(role_name)
        assert actual_id == expected_id, f"Expected {expected_id}, got {actual_id}"


def test_structure_matches_plan_spec():
    """Test that the structure matches the plan specification exactly"""
    skills_data = generate_mock_linkedin_skills()

    # Verify we can access data as specified in Task 6
    # linkedin_data[role_id].get('trending_skills', [])
    for role_name in ROLES:
        role_id = role_name_to_id(role_name)

        # This is how Task 6 will access the data
        trending_skills = skills_data[role_id].get('trending_skills', [])

        # Should return a list of skills
        assert isinstance(trending_skills, list)
        assert len(trending_skills) > 0

        # Should also have role_name
        role_name_from_data = skills_data[role_id].get('role_name', '')
        assert role_name_from_data == role_name


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

    # Should be dict with role_ids as keys
    assert isinstance(data, dict)
    assert len(data) == 7

    # Verify nested structure: role_id -> {role_name, trending_skills}
    for role_id, role_data in data.items():
        # role_id should be lowercase with underscores
        assert isinstance(role_id, str)
        assert role_id == role_id.lower()
        assert "_" in role_id or role_id in ["qa"]  # All roles have underscores except potential edge cases

        # role_data should be a dict with specific keys
        assert isinstance(role_data, dict)
        assert "role_name" in role_data
        assert "trending_skills" in role_data

        # role_name should be a string
        assert isinstance(role_data["role_name"], str)

        # trending_skills should be a list of strings
        assert isinstance(role_data["trending_skills"], list)
        assert all(isinstance(s, str) for s in role_data["trending_skills"])
