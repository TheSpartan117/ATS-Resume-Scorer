"""
P7.3: Passive Voice Detection (2 points)

Detects and penalizes passive voice in resume bullets.

Passive voice patterns:
- "was [verb]ed" (was developed, was managed, was responsible)
- "were [verb]ed" (were created, were implemented, were tasked)
- "has been [verb]ed", "have been [verb]ed"
- "had been [verb]ed"

Scoring:
- Start with 2 points
- Deduct 0.5 points per passive bullet
- Minimum score: 0 (can't go negative)

Research basis:
- Active voice is more impactful and direct
- Passive voice weakens accomplishments and obscures agency
- ATS systems and recruiters prefer active, achievement-focused language
- Studies show active voice increases interview callbacks by 40%
"""

import re
from typing import List, Dict, Any


class PassiveVoiceScorer:
    """Scores resume based on passive voice usage."""

    def __init__(self):
        """Initialize scorer with passive voice patterns."""
        # Define passive voice patterns
        # These patterns look for common passive constructions
        self.passive_patterns = [
            # "was [verb]ed" - e.g., "was developed", "was managed", "was created"
            (r'\bwas\s+\w+(ed|en)\b', 'was [verb]ed'),
            # "was" + weak phrases like "responsible", "tasked", "assigned", "given", "selected"
            (r'\bwas\s+(responsible|tasked|assigned|given|selected|chosen)\b', 'was [weak verb]'),

            # "were [verb]ed" - e.g., "were developed", "were implemented", "were created"
            (r'\bwere\s+\w+(ed|en)\b', 'were [verb]ed'),
            # "were" + weak phrases
            (r'\bwere\s+(responsible|tasked|assigned|given|selected|chosen)\b', 'were [weak verb]'),

            # "has been [verb]ed" - e.g., "has been developed", "has been tested"
            (r'\bhas\s+been\s+\w+(ed|en)\b', 'has been [verb]ed'),
            # "has been" + weak phrases
            (r'\bhas\s+been\s+(managing|coordinating|working|handling)\b', 'has been [verb]ing'),

            # "have been [verb]ed" - e.g., "have been developed", "have been implemented"
            (r'\bhave\s+been\s+\w+(ed|en)\b', 'have been [verb]ed'),
            # "have been" + weak phrases
            (r'\bhave\s+been\s+(managing|coordinating|working|handling)\b', 'have been [verb]ing'),

            # "had been [verb]ed" - e.g., "had been developed", "had been created"
            (r'\bhad\s+been\s+\w+(ed|en)\b', 'had been [verb]ed'),
            # "had been" + weak phrases
            (r'\bhad\s+been\s+(managing|coordinating|working|handling)\b', 'had been [verb]ing'),
        ]

        # Compile patterns for efficiency (case-insensitive)
        self.compiled_patterns = [
            (re.compile(pattern, re.IGNORECASE), name)
            for pattern, name in self.passive_patterns
        ]

    def score(self, bullets: List[str]) -> Dict[str, Any]:
        """
        Score passive voice usage in resume bullets.

        Args:
            bullets: List of resume bullet points

        Returns:
            Dictionary containing:
            - score: Total points (0-2)
            - max_score: Maximum possible points (2)
            - passive_count: Number of bullets with passive voice
            - passive_bullets: List of passive bullet details
            - details: Additional scoring details
        """
        # Handle empty bullets
        if not bullets:
            return self._empty_result()

        # Start with full points
        max_score = 2.0
        penalty_per_bullet = 0.5

        # Analyze each bullet for passive voice
        passive_bullets = []
        patterns_found = set()

        for bullet in bullets:
            bullet_clean = bullet.strip()
            if not bullet_clean:
                continue

            # Check for passive voice patterns
            passive_pattern = self._detect_passive_voice(bullet_clean)

            if passive_pattern:
                passive_bullets.append({
                    'text': bullet_clean,
                    'pattern': passive_pattern
                })
                patterns_found.add(passive_pattern)

        # Calculate score
        passive_count = len(passive_bullets)
        total_penalty = passive_count * penalty_per_bullet
        score = max_score - total_penalty

        # Ensure minimum score is 0
        score = max(0.0, score)

        return {
            'score': round(score, 1),
            'max_score': max_score,
            'passive_count': passive_count,
            'passive_bullets': passive_bullets,
            'details': {
                'penalty_per_bullet': penalty_per_bullet,
                'total_penalty': round(total_penalty, 1),
                'patterns_found': sorted(list(patterns_found))
            }
        }

    def _detect_passive_voice(self, bullet: str) -> str:
        """
        Detect passive voice pattern in a bullet.

        Args:
            bullet: Resume bullet text

        Returns:
            Pattern name if passive voice detected, empty string otherwise
        """
        for pattern, pattern_name in self.compiled_patterns:
            if pattern.search(bullet):
                return pattern_name

        return ""

    def _empty_result(self) -> Dict[str, Any]:
        """Return result for empty bullet list."""
        return {
            'score': 2.0,
            'max_score': 2.0,
            'passive_count': 0,
            'passive_bullets': [],
            'details': {
                'penalty_per_bullet': 0.5,
                'total_penalty': 0.0,
                'patterns_found': []
            }
        }


def score_passive_voice(bullets: List[str]) -> Dict[str, Any]:
    """
    Convenience function to score passive voice usage.

    Args:
        bullets: List of resume bullet points

    Returns:
        Score result dictionary
    """
    scorer = PassiveVoiceScorer()
    return scorer.score(bullets)
