"""Tests for roles API endpoint"""
import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_get_all_roles():
    """Test getting all roles grouped by category"""
    response = client.get("/api/roles")

    assert response.status_code == 200
    data = response.json()

    # Check structure
    assert "categories" in data
    assert "levels" in data

    # Check categories exist
    categories = data["categories"]
    assert "tech" in categories
    assert "product" in categories
    assert "design" in categories

    # Check tech roles
    tech_roles = categories["tech"]
    assert len(tech_roles) > 0
    assert any(role["id"] == "software_engineer" for role in tech_roles)
    assert any(role["name"] == "Software Engineer" for role in tech_roles)

    # Check levels - 3-tier system
    levels = data["levels"]
    assert len(levels) == 3
    level_ids = [level["id"] for level in levels]
    assert "beginner" in level_ids
    assert "intermediary" in level_ids
    assert "senior" in level_ids

    # Check level descriptions
    beginner_level = next(l for l in levels if l["id"] == "beginner")
    assert "0-3 years" in beginner_level["description"]


def test_get_role_details_software_engineer():
    """Test getting details for software engineer role"""
    response = client.get("/api/roles/software_engineer")

    assert response.status_code == 200
    data = response.json()

    # Check basic fields
    assert data["id"] == "software_engineer"
    assert data["name"] == "Software Engineer"
    assert data["category"] == "tech"

    # Check required skills
    assert "required_skills" in data
    assert len(data["required_skills"]) > 0

    # Check sample data for each level - 3-tier system
    assert "sample_data" in data
    sample_data = data["sample_data"]
    assert "beginner" in sample_data
    assert "intermediary" in sample_data
    assert "senior" in sample_data

    # Check beginner level sample data
    beginner_data = sample_data["beginner"]
    assert "keywords" in beginner_data
    assert "action_verbs" in beginner_data
    assert len(beginner_data["keywords"]) > 0
    assert len(beginner_data["action_verbs"]) > 0


def test_get_role_details_product_manager():
    """Test getting details for product manager role"""
    response = client.get("/api/roles/product_manager")

    assert response.status_code == 200
    data = response.json()

    assert data["id"] == "product_manager"
    assert data["name"] == "Product Manager"
    assert data["category"] == "product"
    assert "sample_data" in data


def test_get_nonexistent_role():
    """Test getting details for nonexistent role"""
    response = client.get("/api/roles/nonexistent_role")

    assert response.status_code == 200
    data = response.json()

    assert "error" in data
    assert data["error"] == "Role not found"


def test_all_categories_have_roles():
    """Test that all categories in the response have at least one role"""
    response = client.get("/api/roles")

    assert response.status_code == 200
    data = response.json()

    categories = data["categories"]
    for category_name, roles in categories.items():
        assert len(roles) > 0, f"Category {category_name} should have at least one role"

        # Check each role has required fields
        for role in roles:
            assert "id" in role
            assert "name" in role
            assert role["id"]  # Not empty
            assert role["name"]  # Not empty
