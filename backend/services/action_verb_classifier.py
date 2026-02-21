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

        # Handle "Project Name: Verb..." format
        # Check text after colon first if present
        if ':' in bullet_lower:
            after_colon = bullet_lower.split(':', 1)[1].strip()
            if after_colon:
                words_after_colon = re.findall(r'\b\w+\b', after_colon)
                if words_after_colon:
                    # Check first 2 words after colon
                    for i in range(min(2, len(words_after_colon))):
                        word = words_after_colon[i]
                        if word in self.verb_to_tier:
                            return self.verb_to_tier[word]

                        # Handle hyphenated words
                        if '-' in word:
                            parts = word.split('-')
                            for part in parts:
                                if part in self.verb_to_tier:
                                    return self.verb_to_tier[part]

        # Extract words from beginning, checking first 3 words for the action verb
        # Handles bullets like "Successfully delivered", "Co-led", etc.
        words = re.findall(r'\b\w+\b', bullet_lower)
        if not words:
            return VerbTier.TIER_0

        # Check first 3 words (most verbs are within first 3 words)
        for i in range(min(3, len(words))):
            word = words[i]

            # Check exact match
            if word in self.verb_to_tier:
                return self.verb_to_tier[word]

            # Handle hyphenated words (e.g., "co-led" → check "led")
            if '-' in word:
                parts = word.split('-')
                for part in parts:
                    if part in self.verb_to_tier:
                        return self.verb_to_tier[part]

        # No recognized verb found
        return VerbTier.TIER_0
