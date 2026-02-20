"""
Content Impact Analyzer - Core component for evaluating resume content quality.

This module provides sophisticated content analysis including:
- Achievement strength scoring (CAR structure detection)
- Sentence clarity analysis
- Specificity evaluation
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional


class ContentImpactAnalyzer:
    """
    Analyzes resume content quality using NLP techniques.

    Evaluates:
    - Achievement strength (Context-Action-Result structure)
    - Sentence clarity (length, weak phrases, active voice)
    - Specificity (technologies, metrics, actions)
    """

    def __init__(self):
        """Initialize analyzer with pattern data"""
        self.patterns_dir = Path(__file__).parent.parent / "data" / "patterns"
        self._load_patterns()

    def _load_patterns(self):
        """Load pattern data from JSON files"""
        # Load action verb tiers
        with open(self.patterns_dir / "action_verb_tiers.json") as f:
            verb_data = json.load(f)
            self.verb_tiers = {}
            for tier_name, verbs in verb_data.items():
                tier_num = int(tier_name.split('_')[1])  # Extract tier number
                for verb in verbs:
                    self.verb_tiers[verb.lower()] = tier_num

    def classify_verb_tier(self, verb: str) -> int:
        """
        Classify action verb strength tier (0-4).

        Args:
            verb: Action verb or phrase to classify

        Returns:
            Tier number: 4 (transformational), 3 (leadership), 2 (execution),
                        1 (support), 0 (weak)
        """
        verb_lower = verb.lower().strip()
        return self.verb_tiers.get(verb_lower, 1)  # Default to tier 1 (neutral)
