"""Tests for role taxonomy system"""
import pytest
from backend.services.role_taxonomy import (
    get_role_scoring_data,
    get_all_roles,
    get_roles_by_category,
    ExperienceLevel,
    RoleCategory,
    ROLE_DEFINITIONS
)


def test_experience_levels():
    """Test that all 5 experience levels are defined"""
    assert ExperienceLevel.ENTRY.value == "entry"
    assert ExperienceLevel.MID.value == "mid"
    assert ExperienceLevel.SENIOR.value == "senior"
    assert ExperienceLevel.LEAD.value == "lead"
    assert ExperienceLevel.EXECUTIVE.value == "executive"
    assert len(ExperienceLevel) == 5


def test_role_categories():
    """Test that all 11 role categories are defined"""
    expected_categories = [
        "tech", "product", "design", "business", "data",
        "operations", "finance", "hr", "legal", "customer", "creative"
    ]
    actual_categories = [cat.value for cat in RoleCategory]
    assert set(actual_categories) == set(expected_categories)
    assert len(RoleCategory) == 11


def test_minimum_role_count():
    """Test that at least 20 roles are defined"""
    all_roles = get_all_roles()
    assert len(all_roles) >= 20
    assert len(ROLE_DEFINITIONS) >= 20


def test_required_roles_present():
    """Test that all required roles are defined"""
    required_roles = [
        "software_engineer", "data_scientist", "devops_engineer",
        "product_manager", "technical_product_manager",
        "ux_designer", "ui_designer", "product_designer",
        "marketing_manager", "sales_manager", "business_analyst",
        "operations_manager", "financial_analyst", "accountant",
        "hr_manager", "recruiter", "customer_success_manager",
        "corporate_lawyer", "content_writer"
    ]
    for role_id in required_roles:
        assert role_id in ROLE_DEFINITIONS, f"Required role '{role_id}' not found"


def test_role_has_action_verbs():
    """Test that roles include level-specific action verbs"""
    role_data = get_role_scoring_data("software_engineer", ExperienceLevel.MID)

    assert "action_verbs" in role_data
    assert len(role_data["action_verbs"]) > 0
    assert any(verb in ["developed", "architected", "designed", "built"] for verb in role_data["action_verbs"])


def test_role_has_typical_keywords():
    """Test that roles include typical keywords"""
    role_data = get_role_scoring_data("software_engineer", ExperienceLevel.SENIOR)

    assert "typical_keywords" in role_data
    assert len(role_data["typical_keywords"]) > 0


def test_role_has_scoring_weights():
    """Test that roles include scoring weights"""
    role_data = get_role_scoring_data("product_manager", ExperienceLevel.MID)

    assert "scoring_weights" in role_data
    assert "keywords" in role_data["scoring_weights"]
    assert "action_verbs" in role_data["scoring_weights"]
    assert "metrics" in role_data["scoring_weights"]
    assert "format" in role_data["scoring_weights"]
    assert "content_quality" in role_data["scoring_weights"]


def test_all_roles_have_complete_data():
    """Test that all roles have complete data structure"""
    all_roles = get_all_roles()

    assert len(all_roles) >= 20

    for role_id, role_name in all_roles:
        role_def = ROLE_DEFINITIONS[role_id]

        # Check required fields
        assert "name" in role_def, f"Role {role_id} missing 'name'"
        assert "category" in role_def, f"Role {role_id} missing 'category'"
        assert "action_verbs" in role_def, f"Role {role_id} missing 'action_verbs'"
        assert "typical_keywords" in role_def, f"Role {role_id} missing 'typical_keywords'"
        assert "scoring_weights" in role_def, f"Role {role_id} missing 'scoring_weights'"
        assert "metrics_expected" in role_def, f"Role {role_id} missing 'metrics_expected'"
        assert "required_skills" in role_def, f"Role {role_id} missing 'required_skills'"
        assert "preferred_sections" in role_def, f"Role {role_id} missing 'preferred_sections'"

        # Check all experience levels present
        for level in ExperienceLevel:
            assert level in role_def["action_verbs"], \
                f"Role {role_id} missing action_verbs for {level.value}"
            assert level in role_def["typical_keywords"], \
                f"Role {role_id} missing typical_keywords for {level.value}"
            assert level in role_def["metrics_expected"], \
                f"Role {role_id} missing metrics_expected for {level.value}"

        # Check scoring weights sum to 1.0
        weights = role_def["scoring_weights"]
        total_weight = sum(weights.values())
        assert abs(total_weight - 1.0) < 0.01, \
            f"Role {role_id} weights sum to {total_weight}, expected 1.0"


def test_get_all_roles():
    """Test get_all_roles helper function"""
    roles = get_all_roles()

    assert isinstance(roles, list)
    assert len(roles) >= 20

    for item in roles:
        assert isinstance(item, tuple)
        assert len(item) == 2
        role_id, name = item
        assert isinstance(role_id, str)
        assert isinstance(name, str)
        assert role_id in ROLE_DEFINITIONS


def test_get_roles_by_category():
    """Test get_roles_by_category helper function"""
    tech_roles = get_roles_by_category(RoleCategory.TECH)

    assert isinstance(tech_roles, list)
    assert len(tech_roles) >= 2

    tech_role_ids = [role_id for role_id, _ in tech_roles]
    assert "software_engineer" in tech_role_ids
    assert "devops_engineer" in tech_role_ids

    # Verify all returned roles belong to TECH category
    for role_id, _ in tech_roles:
        assert ROLE_DEFINITIONS[role_id]["category"] == RoleCategory.TECH


def test_get_role_scoring_data_valid():
    """Test get_role_scoring_data with valid input"""
    data = get_role_scoring_data("software_engineer", ExperienceLevel.MID)

    assert data is not None
    assert "name" in data
    assert "category" in data
    assert "typical_keywords" in data
    assert "action_verbs" in data
    assert "scoring_weights" in data
    assert "metrics_expected" in data
    assert "required_skills" in data
    assert "preferred_sections" in data

    assert isinstance(data["typical_keywords"], list)
    assert isinstance(data["action_verbs"], list)
    assert len(data["typical_keywords"]) > 0
    assert len(data["action_verbs"]) > 0


def test_get_role_scoring_data_invalid():
    """Test get_role_scoring_data with invalid role"""
    data = get_role_scoring_data("invalid_role", ExperienceLevel.MID)
    assert data is None


def test_all_categories_have_roles():
    """Test that all categories have at least one role"""
    for category in RoleCategory:
        roles = get_roles_by_category(category)
        assert len(roles) > 0, f"Category '{category.value}' has no roles"


def test_new_roles_added():
    """Test that new roles (QA Engineer, Data Engineer, Project Manager) are present"""
    assert "qa_engineer" in ROLE_DEFINITIONS
    assert "data_engineer" in ROLE_DEFINITIONS
    assert "project_manager" in ROLE_DEFINITIONS

    # Test QA Engineer
    qa_data = get_role_scoring_data("qa_engineer", ExperienceLevel.MID)
    assert qa_data is not None
    assert qa_data["name"] == "QA Engineer"
    assert qa_data["category"] == RoleCategory.TECH

    # Test Data Engineer
    de_data = get_role_scoring_data("data_engineer", ExperienceLevel.MID)
    assert de_data is not None
    assert de_data["name"] == "Data Engineer"
    assert de_data["category"] == RoleCategory.DATA

    # Test Project Manager
    pm_data = get_role_scoring_data("project_manager", ExperienceLevel.MID)
    assert pm_data is not None
    assert pm_data["name"] == "Project Manager"
    assert pm_data["category"] == RoleCategory.OPERATIONS
