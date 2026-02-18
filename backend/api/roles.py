"""Roles endpoint for fetching available roles and their details"""
from fastapi import APIRouter
from typing import Dict, List
from backend.services.role_taxonomy import (
    get_all_roles,
    get_roles_by_category,
    get_role_scoring_data,
    RoleCategory,
    ExperienceLevel,
    ROLE_DEFINITIONS
)

router = APIRouter(prefix="/api", tags=["roles"])


@router.get("/roles")
async def get_roles():
    """
    Get all available roles grouped by category.

    Returns roles organized by category (TECH, PRODUCT, DESIGN, etc.)
    for easy display in frontend dropdowns.
    """
    roles_by_category = {}

    for category in RoleCategory:
        category_roles = get_roles_by_category(category)
        if category_roles:
            roles_by_category[category.value] = [
                {"id": role_id, "name": name}
                for role_id, name in category_roles
            ]

    return {
        "categories": roles_by_category,
        "levels": [
            {"id": level.value, "name": level.value.capitalize(), "description": _get_level_description(level.value)}
            for level in ExperienceLevel
        ]
    }


@router.get("/roles/{role_id}")
async def get_role_details(role_id: str):
    """
    Get details for a specific role.

    Returns role information including name, category, required skills,
    and preferred sections.
    """
    if role_id not in ROLE_DEFINITIONS:
        return {"error": "Role not found"}

    role_data = ROLE_DEFINITIONS[role_id]

    # Get sample keywords and action verbs for each level
    sample_data = {}
    for level in ExperienceLevel:
        scoring_data = get_role_scoring_data(role_id, level)
        if scoring_data:
            sample_data[level.value] = {
                "keywords": scoring_data.get("typical_keywords", [])[:5],  # First 5
                "action_verbs": scoring_data.get("action_verbs", [])[:5]  # First 5
            }

    return {
        "id": role_id,
        "name": role_data["name"],
        "category": role_data["category"].value,
        "required_skills": role_data.get("required_skills", []),
        "preferred_sections": role_data.get("preferred_sections", []),
        "sample_data": sample_data
    }


def _get_level_description(level: str) -> str:
    """Get human-readable description for experience level"""
    descriptions = {
        "entry": "0-2 years experience",
        "mid": "3-5 years experience",
        "senior": "6-10 years experience",
        "lead": "10+ years, Lead/Principal roles",
        "executive": "C-level, VP, Director roles"
    }
    return descriptions.get(level, "")
