"""
Corpus Skills Database Service

Loads and provides access to the corpus-derived skills database.
This service enables querying skill frequencies and getting skills by role.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

# Path to skills database
BACKEND_DIR = Path(__file__).parent.parent
SKILLS_DB_PATH = BACKEND_DIR / "data" / "corpus" / "skills_database.json"


class CorpusSkillsDatabase:
    """
    Service for accessing corpus-derived skills data.

    Provides methods to:
    - Query skill frequencies from corpus
    - Get skills for specific roles
    - List top skills by frequency
    """

    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize the corpus skills database.

        Args:
            db_path: Optional custom path to skills database JSON
        """
        self.db_path = db_path or SKILLS_DB_PATH
        self.skills: Dict[str, int] = {}
        self._available = False
        self._load_database()

    def _load_database(self) -> None:
        """Load skills database from JSON file."""
        try:
            if not self.db_path.exists():
                logger.warning(f"Skills database not found at {self.db_path}")
                return

            with open(self.db_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Convert {"skill": {"frequency": N}} to {"skill": N}
            self.skills = {
                skill.lower(): info.get('frequency', 0)
                for skill, info in data.items()
            }

            self._available = True
            logger.info(f"Loaded {len(self.skills):,} skills from corpus database")

        except Exception as e:
            logger.error(f"Failed to load skills database: {e}")
            self.skills = {}
            self._available = False

    def is_available(self) -> bool:
        """
        Check if the skills database is available.

        Returns:
            True if database loaded successfully, False otherwise
        """
        return self._available

    def get_skill_frequency(self, skill: str) -> int:
        """
        Get the frequency count for a specific skill.

        Args:
            skill: Skill name (case-insensitive)

        Returns:
            Frequency count, or 0 if skill not found
        """
        if not self._available:
            return 0

        return self.skills.get(skill.lower(), 0)

    def get_skills_for_role(
        self,
        role: str,
        min_frequency: int = 1
    ) -> List[str]:
        """
        Get skills associated with a specific role.

        Note: Currently returns all skills meeting the minimum frequency
        threshold. Will be enhanced when role-specific skill mappings
        are added to the corpus database.

        Args:
            role: Role identifier (e.g., "software_developer")
            min_frequency: Minimum frequency threshold for skills

        Returns:
            List of skill names meeting the criteria
        """
        if not self._available:
            return []

        # Filter skills by frequency threshold
        filtered_skills = [
            skill for skill, freq in self.skills.items()
            if freq >= min_frequency
        ]

        # Sort by frequency (descending)
        filtered_skills.sort(key=lambda s: self.skills[s], reverse=True)

        return filtered_skills

    def get_all_skills(self) -> List[str]:
        """
        Get all skills from the database.

        Returns:
            List of all skill names, sorted by frequency (descending)
        """
        if not self._available:
            return []

        # Sort by frequency descending
        sorted_skills = sorted(
            self.skills.keys(),
            key=lambda s: self.skills[s],
            reverse=True
        )

        return sorted_skills

    def get_top_skills(self, n: int = 10) -> List[str]:
        """
        Get the top N most frequent skills.

        Args:
            n: Number of top skills to return

        Returns:
            List of top N skill names
        """
        if not self._available:
            return []

        all_skills = self.get_all_skills()
        return all_skills[:n]


# Singleton instance
_corpus_skills_db_instance: Optional[CorpusSkillsDatabase] = None


def get_corpus_skills_database() -> CorpusSkillsDatabase:
    """
    Get singleton instance of CorpusSkillsDatabase.

    Returns:
        CorpusSkillsDatabase instance
    """
    global _corpus_skills_db_instance

    if _corpus_skills_db_instance is None:
        _corpus_skills_db_instance = CorpusSkillsDatabase()

    return _corpus_skills_db_instance
