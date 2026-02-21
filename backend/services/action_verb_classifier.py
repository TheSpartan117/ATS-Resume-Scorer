"""Action verb classification for resume scoring."""
import json
import re
from enum import Enum
from pathlib import Path
from typing import Dict, List

class VerbTier(Enum):
    """5-tier action verb classification."""
    TIER_4 = "tier_4"  # Transformational
    TIER_3 = "tier_3"  # Leadership
    TIER_2 = "tier_2"  # Execution
    TIER_1 = "tier_1"  # Support
    TIER_0 = "tier_0"  # Weak

    @property
    def points(self) -> int:
        """Get point value for this tier."""
        points_map = {
            "tier_4": 4,
            "tier_3": 3,
            "tier_2": 2,
            "tier_1": 1,
            "tier_0": 0
        }
        return points_map[self.value]

class ActionVerbClassifier:
    """Classifies action verbs in resume bullet points by tier."""

    def __init__(self, data_path: str = None):
        """Initialize classifier with verb tier data."""
        if data_path is None:
            data_path = Path(__file__).parent.parent / "data" / "action_verb_tiers.json"

        with open(data_path, 'r') as f:
            self.tier_data = json.load(f)

        # Build verb-to-tier lookup
        self.verb_to_tier: Dict[str, VerbTier] = {}
        for tier_name, tier_info in self.tier_data.items():
            tier_enum = VerbTier(tier_name)
            for verb in tier_info["verbs"]:
                self.verb_to_tier[verb.lower()] = tier_enum

    def classify_bullet(self, bullet: str) -> VerbTier:
        """Classify a bullet point by its action verb tier.

        Args:
            bullet: Resume bullet point text

        Returns:
            VerbTier enum indicating the tier of the action verb
        """
        bullet_lower = bullet.lower().strip()

        # Check multi-word phrases first (tier 0 mostly)
        for verb, tier in self.verb_to_tier.items():
            if ' ' in verb:  # Multi-word phrase
                if verb in bullet_lower:
                    return tier

        # Check single-word verbs (first word typically)
        words = re.findall(r'\b\w+\b', bullet_lower)
        if words:
            first_word = words[0]
            if first_word in self.verb_to_tier:
                return self.verb_to_tier[first_word]

        # No recognized verb found
        return VerbTier.TIER_0
