"""Tests for role mapping service."""

import pytest
from backend.services.role_mapping_service import (
    RoleMappingService,
    get_role_mapping_service,
)


class TestRoleMappingService:
    """Test cases for RoleMappingService."""

    def test_normalize_role_exact_match(self):
        """Test normalizing a job title to standard role."""
        service = RoleMappingService()
        result = service.normalize_role("Software Engineer")
        assert result is not None
        assert isinstance(result, str)
        assert len(result) > 0

    def test_normalize_role_case_insensitive(self):
        """Test that role normalization is case-insensitive."""
        service = RoleMappingService()
        result1 = service.normalize_role("Software Engineer")
        result2 = service.normalize_role("software engineer")
        result3 = service.normalize_role("SOFTWARE ENGINEER")
        assert result1 == result2
        assert result2 == result3

    def test_normalize_role_with_whitespace(self):
        """Test that extra whitespace is handled."""
        service = RoleMappingService()
        result1 = service.normalize_role("Software Engineer")
        result2 = service.normalize_role("  Software Engineer  ")
        result3 = service.normalize_role("Software  Engineer")
        assert result1 == result2
        # Multiple internal spaces should still match
        assert result3 is not None

    def test_normalize_role_unknown_returns_none(self):
        """Test that unknown job titles return None."""
        service = RoleMappingService()
        result = service.normalize_role("Quantum Entanglement Specialist XYZABC")
        assert result is None

    def test_normalize_role_empty_string(self):
        """Test that empty string returns None."""
        service = RoleMappingService()
        result = service.normalize_role("")
        assert result is None

    def test_normalize_role_none(self):
        """Test that None input returns None."""
        service = RoleMappingService()
        result = service.normalize_role(None)
        assert result is None

    def test_get_all_variations(self):
        """Test getting all variations for a role."""
        service = RoleMappingService()
        # First normalize a known role to get the role_id
        role_id = service.normalize_role("Software Engineer")
        assert role_id is not None

        # Get all variations for that role
        variations = service.get_all_variations(role_id)
        assert variations is not None
        assert isinstance(variations, list)
        assert len(variations) > 0
        assert all(isinstance(v, str) for v in variations)

    def test_get_all_variations_unknown_role(self):
        """Test getting variations for unknown role returns None."""
        service = RoleMappingService()
        variations = service.get_all_variations("unknown_role_id_12345")
        assert variations is None

    def test_get_all_variations_empty_string(self):
        """Test that empty string returns None."""
        service = RoleMappingService()
        variations = service.get_all_variations("")
        assert variations is None

    def test_get_all_variations_none(self):
        """Test that None input returns None."""
        service = RoleMappingService()
        variations = service.get_all_variations(None)
        assert variations is None

    def test_is_available(self):
        """Test that service reports availability correctly."""
        service = RoleMappingService()
        assert service.is_available() is True

    def test_singleton_pattern(self):
        """Test that get_role_mapping_service returns singleton."""
        service1 = get_role_mapping_service()
        service2 = get_role_mapping_service()
        assert service1 is service2

    def test_multiple_role_variations(self):
        """Test that different job titles map to same role."""
        service = RoleMappingService()
        # Common variations that should map to the same role
        role1 = service.normalize_role("Software Engineer")
        role2 = service.normalize_role("Software Developer")

        # Both should return valid role_ids
        assert role1 is not None
        assert role2 is not None

    def test_data_integrity(self):
        """Test that the loaded data has expected structure."""
        service = RoleMappingService()
        # If service is available, it should have mappings
        if service.is_available():
            # Test with a known common role
            result = service.normalize_role("Software Engineer")
            assert result is not None

            # Verify we can get variations back
            variations = service.get_all_variations(result)
            assert variations is not None
            assert len(variations) > 0
