"""
P7.1 - Readability Score (5 pts)

Scores resume readability using Flesch Reading Ease formula.
Target: Professional clarity in the 60-70 range.

Flesch Reading Ease Formula:
206.835 - 1.015 * (total_words / total_sentences) - 84.6 * (total_syllables / total_words)

Scoring:
- 60-70 (optimal professional): 5 pts
- 50-80 (acceptable): 3 pts
- Otherwise: 1 pt

Readability Levels:
- 90-100: Very Easy
- 80-89: Easy
- 70-79: Fairly Easy
- 60-69: Standard (Professional target)
- 50-59: Fairly Difficult
- 30-49: Difficult
- 0-29: Very Confusing
"""

import re
from typing import Dict, Any


class ReadabilityScorer:
    """Scores resume readability using Flesch Reading Ease."""

    def __init__(self):
        """Initialize readability scorer."""
        self.max_score = 5

    def score(self, text: str) -> Dict[str, Any]:
        """
        Score text readability using Flesch Reading Ease.

        Args:
            text: Resume text to analyze

        Returns:
            Dictionary containing:
            - score: Points earned (1, 3, or 5)
            - max_score: Maximum possible score (5)
            - flesch_score: Flesch Reading Ease score (0-100+)
            - readability_level: Readability level name
            - details: Dictionary with word/sentence/syllable counts
        """
        # Handle empty or very short text
        if not text or len(text.strip()) < 2:
            return {
                'score': 1,
                'max_score': self.max_score,
                'flesch_score': 0,
                'readability_level': 'Unknown',
                'details': {
                    'total_words': 0,
                    'total_sentences': 0,
                    'total_syllables': 0,
                    'avg_words_per_sentence': 0,
                    'avg_syllables_per_word': 0
                }
            }

        # Count components
        total_words = self._count_words(text)
        total_sentences = self._count_sentences(text)
        total_syllables = self._count_syllables_in_text(text)

        # Prevent division by zero
        if total_words == 0 or total_sentences == 0:
            return {
                'score': 1,
                'max_score': self.max_score,
                'flesch_score': 0,
                'readability_level': 'Unknown',
                'details': {
                    'total_words': total_words,
                    'total_sentences': total_sentences,
                    'total_syllables': total_syllables,
                    'avg_words_per_sentence': 0,
                    'avg_syllables_per_word': 0
                }
            }

        # Calculate Flesch Reading Ease score
        avg_words_per_sentence = total_words / total_sentences
        avg_syllables_per_word = total_syllables / total_words

        flesch_score = (
            206.835
            - 1.015 * avg_words_per_sentence
            - 84.6 * avg_syllables_per_word
        )

        # Round to 1 decimal place
        flesch_score = round(flesch_score, 1)

        # Get readability level
        readability_level = self._get_readability_level(flesch_score)

        # Calculate score based on ranges
        if 60 <= flesch_score <= 70:
            # Optimal professional range
            score = 5
        elif 50 <= flesch_score <= 80:
            # Acceptable range (50-60 or 70-80)
            score = 3
        else:
            # Outside acceptable ranges
            score = 1

        return {
            'score': score,
            'max_score': self.max_score,
            'flesch_score': flesch_score,
            'readability_level': readability_level,
            'details': {
                'total_words': total_words,
                'total_sentences': total_sentences,
                'total_syllables': total_syllables,
                'avg_words_per_sentence': round(avg_words_per_sentence, 2),
                'avg_syllables_per_word': round(avg_syllables_per_word, 2)
            }
        }

    def _count_words(self, text: str) -> int:
        """
        Count words in text.

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

    def _count_sentences(self, text: str) -> int:
        """
        Count sentences in text.

        Counts based on:
        - Sentence-ending punctuation (. ! ?)
        - Bullet points (• - *)
        - Line breaks (for resume bullets)

        Args:
            text: Text to count sentences in

        Returns:
            Sentence count (minimum 1 if text exists)
        """
        if not text or not text.strip():
            return 0

        # Count sentence-ending punctuation
        sentence_endings = re.findall(r'[.!?]+', text)
        count = len(sentence_endings)

        # Count bullet points as sentence starts
        bullet_points = re.findall(r'[•\-\*]\s+', text)
        count += len(bullet_points)

        # If no sentence markers found but text exists, count as 1 sentence
        if count == 0 and text.strip():
            count = 1

        return count

    def _count_syllables_in_text(self, text: str) -> int:
        """
        Count total syllables in text.

        Args:
            text: Text to count syllables in

        Returns:
            Total syllable count
        """
        if not text or not text.strip():
            return 0

        # Get all words
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())

        total_syllables = 0
        for word in words:
            total_syllables += self._count_syllables(word)

        return total_syllables

    def _count_syllables(self, word: str) -> int:
        """
        Count syllables in a single word.

        Uses vowel-based heuristic:
        - Count vowel groups (consecutive vowels = 1 syllable)
        - Subtract silent 'e' at end
        - Minimum 1 syllable per word

        Args:
            word: Single word to count syllables in

        Returns:
            Syllable count
        """
        if not word:
            return 0

        word = word.lower().strip()

        if len(word) <= 1:
            return 1

        # Count vowel groups
        vowels = 'aeiouy'
        syllable_count = 0
        previous_was_vowel = False

        for char in word:
            is_vowel = char in vowels
            if is_vowel and not previous_was_vowel:
                syllable_count += 1
            previous_was_vowel = is_vowel

        # Adjust for silent 'e' at end
        if word.endswith('e') and syllable_count > 1:
            syllable_count -= 1

        # Adjust for 'le' ending
        if word.endswith('le') and len(word) > 2 and word[-3] not in vowels:
            syllable_count += 1

        # Ensure at least 1 syllable
        if syllable_count == 0:
            syllable_count = 1

        return syllable_count

    def _get_readability_level(self, flesch_score: float) -> str:
        """
        Get readability level name from Flesch score.

        Args:
            flesch_score: Flesch Reading Ease score

        Returns:
            Readability level name
        """
        if flesch_score >= 90:
            return 'Very Easy'
        elif flesch_score >= 80:
            return 'Easy'
        elif flesch_score >= 70:
            return 'Fairly Easy'
        elif flesch_score >= 60:
            return 'Standard'
        elif flesch_score >= 50:
            return 'Fairly Difficult'
        elif flesch_score >= 30:
            return 'Difficult'
        else:
            return 'Very Confusing'


def create_scorer() -> ReadabilityScorer:
    """
    Factory function to create ReadabilityScorer instance.

    Returns:
        ReadabilityScorer instance
    """
    return ReadabilityScorer()
