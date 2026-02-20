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
        try:
            # Load action verb tiers
            with open(self.patterns_dir / "action_verb_tiers.json") as f:
                verb_data = json.load(f)
                self.verb_tiers = {}
                for tier_name, verbs in verb_data.items():
                    # Robust tier number parsing with fallback
                    try:
                        tier_num = int(tier_name.split('_')[1])
                    except (IndexError, ValueError):
                        # Fallback: extract first digit found
                        match = re.search(r'\d+', tier_name)
                        if match:
                            tier_num = int(match.group())
                        else:
                            raise ValueError(f"Cannot extract tier number from: {tier_name}")

                    for verb in verbs:
                        self.verb_tiers[verb.lower()] = tier_num

            # Load metric patterns
            with open(self.patterns_dir / "metric_patterns.json") as f:
                metric_data = json.load(f)
                self.metric_patterns = metric_data['patterns']
                self.metric_quality_weights = metric_data['quality_weights']

        except FileNotFoundError as e:
            raise RuntimeError(f"Pattern file not found: {e}")
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Invalid JSON in pattern file: {e}")
        except (KeyError, ValueError) as e:
            raise RuntimeError(f"Invalid pattern file format: {e}")

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

    def extract_metrics(self, text: str) -> List[Dict]:
        """
        Extract quantifiable metrics from text.

        Args:
            text: Text to analyze

        Returns:
            List of metric dictionaries with 'value', 'type', and 'quality'
        """
        metrics = []

        for metric_type, pattern in self.metric_patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                # Handle tuple matches (from capturing groups)
                if isinstance(match, tuple):
                    value = match[0] if match[0] else match[1]
                else:
                    value = match

                metrics.append({
                    'value': value,
                    'type': metric_type,
                    'quality': self.evaluate_metric_quality(metric_type)
                })

        return metrics

    def evaluate_metric_quality(self, metric_type: str) -> float:
        """
        Rate metric quality/impact (0-1 scale).

        Args:
            metric_type: Type of metric (percentage, money, etc.)

        Returns:
            Quality score (1.0 = excellent, 0.5 = basic)
        """
        return self.metric_quality_weights.get(metric_type, 0.5)
