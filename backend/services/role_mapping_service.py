"""Role mapping service for normalizing job titles to standard roles."""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class RoleMappingService:
    """Service for mapping job title variations to standard role IDs.

    Provides functionality to:
    - Normalize any job title to a standard role_id
    - Get all variations of a given role
    - Handle case-insensitive lookups with whitespace normalization
    """

    def __init__(self, data_path: Optional[str] = None):
        """Initialize the role mapping service.

        Args:
            data_path: Optional path to role_mappings.json file.
                      If not provided, uses default location.
        """
        self._title_to_role: Dict[str, str] = {}
        self._role_to_titles: Dict[str, List[str]] = {}
        self._available = False

        # Determine data path
        if data_path is None:
            # Default path relative to this file
            backend_dir = Path(__file__).parent.parent
            data_path = backend_dir / "data" / "corpus" / "role_mappings.json"
        else:
            data_path = Path(data_path)

        # Load mappings
        self._load_mappings(data_path)

    def _load_mappings(self, data_path: Path) -> None:
        """Load role mappings from JSON file.

        Args:
            data_path: Path to the role_mappings.json file.
        """
        try:
            if not data_path.exists():
                logger.warning(f"Role mappings file not found: {data_path}")
                return

            with open(data_path, "r", encoding="utf-8") as f:
                mappings = json.load(f)

            # Build title -> role mapping (with normalized keys)
            for job_title, role_id in mappings.items():
                normalized_title = self._normalize_string(job_title)
                self._title_to_role[normalized_title] = role_id

            # Build reverse mapping: role -> list of titles
            for job_title, role_id in mappings.items():
                if role_id not in self._role_to_titles:
                    self._role_to_titles[role_id] = []
                self._role_to_titles[role_id].append(job_title)

            self._available = True
            logger.info(
                f"Loaded {len(self._title_to_role)} job title mappings "
                f"for {len(self._role_to_titles)} roles"
            )

        except Exception as e:
            logger.error(f"Error loading role mappings: {e}")
            self._available = False

    @staticmethod
    def _normalize_string(text: str) -> str:
        """Normalize a string for comparison.

        Args:
            text: The string to normalize.

        Returns:
            Normalized string (lowercase, trimmed, single spaces).
        """
        if not text:
            return ""
        # Convert to lowercase, strip whitespace, normalize internal spaces
        return " ".join(text.lower().strip().split())

    def normalize_role(self, job_title: Optional[str]) -> Optional[str]:
        """Map a job title to its standard role ID.

        Args:
            job_title: The job title to normalize.

        Returns:
            The standard role_id if found, None otherwise.
        """
        if not job_title or not isinstance(job_title, str):
            return None

        if not self._available:
            logger.debug("Role mapping service not available")
            return None

        normalized_title = self._normalize_string(job_title)
        if not normalized_title:
            return None

        return self._title_to_role.get(normalized_title)

    def get_all_variations(self, role_id: Optional[str]) -> Optional[List[str]]:
        """Get all job title variations for a given role.

        Args:
            role_id: The standard role ID.

        Returns:
            List of job title variations if found, None otherwise.
        """
        if not role_id or not isinstance(role_id, str):
            return None

        if not self._available:
            logger.debug("Role mapping service not available")
            return None

        if not role_id:
            return None

        return self._role_to_titles.get(role_id)

    def is_available(self) -> bool:
        """Check if the role mapping service is available.

        Returns:
            True if mappings are loaded, False otherwise.
        """
        return self._available


# Singleton instance
_role_mapping_service_instance: Optional[RoleMappingService] = None


def get_role_mapping_service() -> RoleMappingService:
    """Get the singleton role mapping service instance.

    Returns:
        The RoleMappingService singleton instance.
    """
    global _role_mapping_service_instance
    if _role_mapping_service_instance is None:
        _role_mapping_service_instance = RoleMappingService()
    return _role_mapping_service_instance
