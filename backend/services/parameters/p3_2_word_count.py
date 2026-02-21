"""
P3.2: Word Count Optimization (3 points)

Optimal word count varies by level - too sparse lacks detail, too verbose loses focus.

Level-Specific Ranges:
- Beginner: 300-400 words = 3pts, 250-500 = 2pts, else = 0pts
- Intermediary: 400-600 words = 3pts, 300-700 = 2pts, else = 0pts
- Senior: 500-700 words = 3pts, 400-800 = 2pts, else = 0pts

Based on ATS research:
- Too short: Lacks sufficient detail and context
- Too long: Loses focus and increases screening time
- Level matters: Senior roles expect more comprehensive content
"""

import re
from typing import Dict, Any, Union


class WordCountScorer:
    """Scores resume word count based on experience level."""

    # Level-specific ranges (more lenient to avoid penalizing good CVs)
    LEVEL_RANGES = {
        'beginner': {
            'optimal': (250, 450),
            'acceptable': (200, 550)
        },
        'intermediary': {
            'optimal': (350, 650),
            'acceptable': (250, 750)
        },
        'senior': {
            'optimal': (400, 750),  # Lowered from 500 to accommodate compact professional CVs
            'acceptable': (350, 850)
        }
    }

    def __init__(self):
        """Initialize word count scorer."""
        pass

    def score(self, content: str, level: str) -> Dict[str, Any]:
        """
        Score word count for resume content.

        Args:
            content: Full resume text content (all sections combined)
            level: Experience level ('beginner', 'intermediary', 'senior')

        Returns:
            Dictionary containing:
            - score: Points earned (0, 2, or 3)
            - level: Experience level used
            - word_count: Total word count
            - optimal_range: Optimal word count range for this level
            - acceptable_range: Acceptable word count range for this level
            - in_optimal_range: Whether word count is in optimal range
            - in_acceptable_range: Whether word count is in acceptable range
            - too_short: Whether word count is below acceptable
            - too_long: Whether word count is above acceptable
            - feedback: Human-readable feedback message
        """
        # Normalize level
        level_lower = str(level).lower().strip()
        if level_lower not in self.LEVEL_RANGES:
            level_lower = 'intermediary'  # Default to intermediary

        # Count words
        word_count = self._count_words(content)

        # Get ranges for this level
        ranges = self.LEVEL_RANGES[level_lower]
        optimal_min, optimal_max = ranges['optimal']
        acceptable_min, acceptable_max = ranges['acceptable']

        # Check which range we're in
        in_optimal_range = optimal_min <= word_count <= optimal_max
        in_acceptable_range = acceptable_min <= word_count <= acceptable_max
        too_short = word_count < acceptable_min
        too_long = word_count > acceptable_max

        # Calculate score
        if in_optimal_range:
            score = 3
        elif in_acceptable_range:
            score = 2
        else:
            score = 0

        # Generate feedback
        feedback = self._generate_feedback(
            word_count, level_lower, in_optimal_range,
            in_acceptable_range, too_short, too_long,
            optimal_min, optimal_max, acceptable_min, acceptable_max
        )

        return {
            'score': score,
            'level': level_lower,
            'word_count': word_count,
            'optimal_range': (optimal_min, optimal_max),
            'acceptable_range': (acceptable_min, acceptable_max),
            'in_optimal_range': in_optimal_range,
            'in_acceptable_range': in_acceptable_range,
            'too_short': too_short,
            'too_long': too_long,
            'feedback': feedback
        }

    def score_from_sections(self, sections: Dict[str, str], level: str) -> Dict[str, Any]:
        """
        Score word count from multiple resume sections.

        Args:
            sections: Dictionary of section_name -> content
            level: Experience level

        Returns:
            Score result dictionary (same as score())
        """
        # Combine all sections into one text
        combined_text = " ".join(
            str(content) for content in sections.values() if content
        )

        return self.score(combined_text, level)

    def _count_words(self, text: str) -> int:
        """
        Count words in text.

        Uses whitespace splitting after removing extra spaces.
        Punctuation is not counted as separate words.

        Args:
            text: Text to count words in

        Returns:
            Word count
        """
        if not text or not text.strip():
            return 0

        # Remove extra whitespace and normalize
        cleaned = re.sub(r'\s+', ' ', text.strip())

        # Split on whitespace
        words = cleaned.split()

        return len(words)

    def _generate_feedback(
        self,
        word_count: int,
        level: str,
        in_optimal: bool,
        in_acceptable: bool,
        too_short: bool,
        too_long: bool,
        optimal_min: int,
        optimal_max: int,
        acceptable_min: int,
        acceptable_max: int
    ) -> str:
        """
        Generate human-readable feedback message.

        Args:
            word_count: Current word count
            level: Experience level
            in_optimal: Whether in optimal range
            in_acceptable: Whether in acceptable range
            too_short: Whether below acceptable
            too_long: Whether above acceptable
            optimal_min: Minimum of optimal range
            optimal_max: Maximum of optimal range
            acceptable_min: Minimum of acceptable range
            acceptable_max: Maximum of acceptable range

        Returns:
            Feedback message string
        """
        if in_optimal:
            return (
                f"Excellent! Your resume has {word_count} words, which is in the "
                f"optimal range ({optimal_min}-{optimal_max}) for {level} level."
            )
        elif in_acceptable:
            if word_count < optimal_min:
                words_needed = optimal_min - word_count
                return (
                    f"Your resume has {word_count} words. Consider adding {words_needed} "
                    f"more words to reach the optimal range ({optimal_min}-{optimal_max}) "
                    f"for {level} level."
                )
            else:  # word_count > optimal_max
                words_to_remove = word_count - optimal_max
                return (
                    f"Your resume has {word_count} words. Consider removing {words_to_remove} "
                    f"words to reach the optimal range ({optimal_min}-{optimal_max}) "
                    f"for {level} level."
                )
        elif too_short:
            words_needed = acceptable_min - word_count
            return (
                f"Your resume is too short at {word_count} words. Add at least "
                f"{words_needed} more words to provide sufficient detail. Target: "
                f"{optimal_min}-{optimal_max} words for {level} level."
            )
        else:  # too_long
            words_to_remove = word_count - acceptable_max
            return (
                f"Your resume is too long at {word_count} words. Remove at least "
                f"{words_to_remove} words to improve focus and readability. Target: "
                f"{optimal_min}-{optimal_max} words for {level} level."
            )


def score_word_count(content: Union[str, Dict[str, str]], level: str) -> Dict[str, Any]:
    """
    Convenience function to score word count.

    Args:
        content: Either a string (full resume text) or a dict (sections)
        level: Experience level ('beginner', 'intermediary', 'senior')

    Returns:
        Score result dictionary
    """
    scorer = WordCountScorer()

    if isinstance(content, dict):
        return scorer.score_from_sections(content, level)
    else:
        return scorer.score(content, level)
