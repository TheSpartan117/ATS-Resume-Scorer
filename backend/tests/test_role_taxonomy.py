"""Tests for role taxonomy"""
from services.role_taxonomy import (
    get_role_scoring_data,
    get_all_roles,
    ExperienceLevel,
    ROLE_DEFINITIONS
)


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


def test_all_roles_have_complete_data():
    """Test that all 19 roles have complete data"""
    all_roles = get_all_roles()

    assert len(all_roles) == 19

    for role_id, role_name in all_roles:
        role_def = ROLE_DEFINITIONS[role_id]

        # Check required fields
        assert "action_verbs" in role_def
        assert "typical_keywords" in role_def
        assert "scoring_weights" in role_def
        assert "metrics_expected" in role_def

        # Check all experience levels present
        for level in ExperienceLevel:
            assert level in role_def["action_verbs"]
            assert level in role_def["typical_keywords"]
