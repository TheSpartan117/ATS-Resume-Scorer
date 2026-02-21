"""
Word/Verb Repetition Detector

Detects excessive repetition of action verbs across resume bullets.
Penalizes poor writing diversity.

Research basis:
- Career coaches recommend max 2 uses of same verb per resume
- Excessive repetition indicates limited vocabulary/lazy writing
- ATS systems flag keyword stuffing when same term repeated 3+ times

Penalty structure:
- Each verb used 3+ times: -1 point
- Maximum penalty: -3 points total
- Threshold chosen to allow some repetition (2 uses OK) but penalize excessive (3+)
"""

import re
from collections import Counter
from typing import Dict, List


class RepetitionDetector:
    """
    Detect repetitive use of action verbs across resume bullets.

    Penalty structure:
    - Each verb repeated 3+ times: -1 point
    - Maximum cumulative penalty: -3 points
    """

    # Common words to ignore (articles, prepositions, conjunctions)
    IGNORE_WORDS = {
        'the', 'a', 'an', 'and', 'or', 'but', 'to', 'of', 'in', 'on', 'at',
        'for', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be',
        'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
        'would', 'should', 'could', 'may', 'might', 'must', 'can'
    }

    def __init__(self, repetition_threshold: int = 3, max_penalty: int = 3):
        """
        Initialize detector with thresholds.

        Args:
            repetition_threshold: Number of uses to trigger penalty (default: 3)
            max_penalty: Maximum cumulative penalty points (default: 3)
        """
        self.repetition_threshold = repetition_threshold
        self.max_penalty = max_penalty

    def _extract_action_verb(self, bullet: str) -> str:
        """
        Extract the action verb (first meaningful word) from a bullet.

        Args:
            bullet: Resume bullet point

        Returns:
            Lowercase action verb, or empty string if none found
        """
        if not bullet:
            return ""

        # Remove leading bullet markers and whitespace
        bullet = bullet.strip()
        bullet = re.sub(r'^[-•*]\s*', '', bullet)

        # Extract first word
        words = re.findall(r'\b[a-zA-Z]+\b', bullet)

        if not words:
            return ""

        first_word = words[0].lower()

        # Skip if it's a common word
        if first_word in self.IGNORE_WORDS:
            # Try next word
            if len(words) > 1:
                return words[1].lower()
            return ""

        return first_word

    def detect(self, bullets: List[str]) -> Dict:
        """
        Detect repetitive action verbs in bullet list.

        Args:
            bullets: List of resume bullet points

        Returns:
            {
                'penalty_score': int (0 to -3),
                'repeated_words': [
                    {
                        'word': str,
                        'count': int,
                        'penalty': int (-1)
                    }
                ],
                'verb_counts': Dict[str, int] (all verbs with counts)
            }
        """
        if not bullets:
            return {
                'penalty_score': 0,
                'repeated_words': [],
                'verb_counts': {}
            }

        # Extract action verbs from all bullets
        action_verbs = [self._extract_action_verb(bullet) for bullet in bullets]
        action_verbs = [verb for verb in action_verbs if verb]  # Remove empty strings

        # Count occurrences
        verb_counts = Counter(action_verbs)

        # Find verbs that exceed threshold
        repeated_words = []
        total_penalty = 0

        for verb, count in verb_counts.items():
            if count >= self.repetition_threshold:
                repeated_words.append({
                    'word': verb,
                    'count': count,
                    'penalty': -1
                })
                total_penalty -= 1

        # Sort by count (most repeated first)
        repeated_words.sort(key=lambda x: x['count'], reverse=True)

        # Apply penalty cap
        penalty_score = max(total_penalty, -self.max_penalty)

        return {
            'penalty_score': penalty_score,
            'repeated_words': repeated_words,
            'verb_counts': dict(verb_counts)
        }

    def analyze(self, bullets: List[str]) -> Dict:
        """
        Complete analysis with full details.

        Args:
            bullets: List of resume bullet points

        Returns:
            {
                'total_bullets': int,
                'penalty_score': int (0 to -3),
                'max_penalty': int (-3),
                'repeated_words': List[Dict],
                'verb_counts': Dict[str, int]
            }
        """
        detection_result = self.detect(bullets)

        return {
            'total_bullets': len(bullets),
            'penalty_score': detection_result['penalty_score'],
            'max_penalty': -self.max_penalty,
            'repeated_words': detection_result['repeated_words'],
            'verb_counts': detection_result['verb_counts']
        }


# Singleton instance
_detector_instance = None

def get_repetition_detector() -> RepetitionDetector:
    """Get singleton instance of RepetitionDetector."""
    global _detector_instance
    if _detector_instance is None:
        _detector_instance = RepetitionDetector()
    return _detector_instance
