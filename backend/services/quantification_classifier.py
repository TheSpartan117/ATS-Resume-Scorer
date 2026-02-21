"""
Quantification Quality Classification

Classifies metrics in bullets by impact value (high/medium/low)
Based on ResumeWorded and Jobscan research on metric effectiveness.
"""

import re
from enum import Enum
from typing import Optional, List, Dict


class MetricQuality(Enum):
    """3-tier metric quality system"""
    HIGH = (1.0, "High-value")     # Percentages, money, multipliers
    MEDIUM = (0.7, "Medium-value") # Team sizes, durations, scale
    LOW = (0.3, "Low-value")       # Bare numbers without context

    def __init__(self, weight: float, description: str):
        self._weight = weight
        self._description = description

    @property
    def weight(self) -> float:
        return self._weight

    @property
    def description(self) -> str:
        return self._description


class QuantificationClassifier:
    """
    Classify quantifiable achievements by metric quality.

    Research findings:
    - High-value: Business impact (%, $, multipliers, before/after)
    - Medium-value: Scope indicators (team sizes, time, scale)
    - Low-value: Activity counts without business context
    """

    def __init__(self):
        # High-value patterns (business impact)
        self.high_value_patterns = {
            'percentage': re.compile(r'\b\d+(?:\.\d+)?%'),
            # Support both $ and ₹ (Indian Rupee), with K/M/B/Cr/L suffixes
            'money': re.compile(r'(?:\$|₹|INR|Rs\.?)\s*\d+(?:[.,]\d+)?(?:\+)?\s*(?:[KMB]|Cr|Lakh|L)?(?:/(?:year|month|day))?', re.IGNORECASE),
            # Also catch "Cr" (Crore) without currency symbol
            'money_crore': re.compile(r'\d+(?:[.,]\d+)?(?:\+)?\s*Cr\b', re.IGNORECASE),
            'multiplier': re.compile(r'\b\d+x\b', re.IGNORECASE),
            'comparison': re.compile(
                r'(?:increased|reduced|improved|boosted|decreased|enhanced|grew|cut|delivered|generated|saved)'
                r'.*?(?:from|by|to)\s+\d+',
                re.IGNORECASE
            ),
            'time_improvement': re.compile(
                r'(?:from|reduced|saving|saved)\s+\d+[,\s]*\d*\s*(?:ms|seconds?|minutes?|hours?|hrs?|days?|man-?hrs?|man-?hours?)',
                re.IGNORECASE
            )
        }

        # Medium-value patterns (scope/scale)
        self.medium_value_patterns = {
            'team_size': re.compile(
                r'(?:team|group|engineers|developers|people|members|stakeholders?|departments?)\s+(?:of\s+)?\d+',
                re.IGNORECASE
            ),
            'duration': re.compile(
                r'\d+[+]?\s+(?:days?|weeks?|months?|years?)',
                re.IGNORECASE
            ),
            # More flexible user scale - matches "14K+ users", "across 14K+ users", etc.
            'user_scale': re.compile(
                r'\d+[,\s]*\d*[KMB]?\+?\s*(?:users?|customers?|clients?|accounts?|employees?|pilots?|crew members?)',
                re.IGNORECASE
            ),
            'traffic_scale': re.compile(
                r'(?:serving|handling|managing|supporting|across|over)\s+\d+[,\s]*\d*[KMB]?\+?',
                re.IGNORECASE
            ),
            'project_count': re.compile(
                r'(?:managed|handled|led|completed|delivered|automated?|initiatives?)\s+\d+[+]?\s+(?:concurrent\s+)?(?:projects?|tasks?|initiatives?|features?|automations?|workshops?|SKUs?|stores?)',
                re.IGNORECASE
            ),
            # Large scale numbers (like "180+ SKUs", "21 stores")
            'scale_indicator': re.compile(
                r'\d+[+]?\s+(?:SKUs?|stores?|locations?|branches?|facilities?|systems?|applications?|APIs?|endpoints?|integrations?)',
                re.IGNORECASE
            )
        }

        # Low-value patterns (bare numbers)
        self.low_value_patterns = {
            'bare_number': re.compile(r'(?<![.\d])\d+(?![.\d])')
        }

    def classify_bullet(self, bullet: str) -> Optional[MetricQuality]:
        """
        Classify a single bullet by its metric quality.

        Priority order: high > medium > low
        """
        if not bullet or len(bullet.strip()) < 5:
            return None

        # Check high-value patterns first
        for pattern_name, pattern in self.high_value_patterns.items():
            if pattern.search(bullet):
                return MetricQuality.HIGH

        # Check medium-value patterns
        for pattern_name, pattern in self.medium_value_patterns.items():
            if pattern.search(bullet):
                return MetricQuality.MEDIUM

        # Check low-value patterns
        for pattern_name, pattern in self.low_value_patterns.items():
            if pattern.search(bullet):
                return MetricQuality.LOW

        return None  # No metrics found

    def classify_bullets(self, bullets: List[str]) -> Dict:
        """
        Classify multiple bullets and return weighted statistics.

        Returns:
            {
                'total_bullets': int,
                'quantified_count': int,
                'high_count': int,
                'medium_count': int,
                'low_count': int,
                'weighted_quantification_rate': float (%)
            }
        """
        if not bullets:
            return {
                'total_bullets': 0,
                'quantified_count': 0,
                'high_count': 0,
                'medium_count': 0,
                'low_count': 0,
                'weighted_quantification_rate': 0.0
            }

        quality_counts = {'high': 0, 'medium': 0, 'low': 0}
        total_weighted = 0.0

        for bullet in bullets:
            quality = self.classify_bullet(bullet)
            if quality is not None:
                if quality == MetricQuality.HIGH:
                    quality_counts['high'] += 1
                    total_weighted += 1.0
                elif quality == MetricQuality.MEDIUM:
                    quality_counts['medium'] += 1
                    total_weighted += 0.7
                else:  # LOW
                    quality_counts['low'] += 1
                    total_weighted += 0.3

        total_bullets = len(bullets)
        quantified_count = sum(quality_counts.values())
        weighted_rate = (total_weighted / total_bullets * 100) if total_bullets > 0 else 0.0

        return {
            'total_bullets': total_bullets,
            'quantified_count': quantified_count,
            'high_count': quality_counts['high'],
            'medium_count': quality_counts['medium'],
            'low_count': quality_counts['low'],
            'weighted_quantification_rate': weighted_rate
        }
