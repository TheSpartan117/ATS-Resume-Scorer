"""
P7.1 - Readability Score (5 pts)

Scores resume readability using CV-appropriate metrics.
Technical/professional resumes naturally have complex language, so we focus on structure.

Scoring (out of 5):
- Has bullet points (structured format): +2 pts
- Avg sentence length 15-30 words (appropriate complexity): +2 pts
- Not too many long sentences (>40 words, max 20%): +1 pt

Why not Flesch Reading Ease?
- Flesch penalizes technical terminology and professional language
- Technical resumes naturally score low (10-30) despite being well-written
- CV structure matters more than general readability scores
"""

import re
from typing import Dict, Any


class ReadabilityScorer:
    """Scores resume readability using CV-appropriate metrics."""

    def __init__(self):
        """Initialize readability scorer."""
        self.max_score = 5
        self.optimal_sentence_length_min = 5  # Lower threshold to account for bullet parsing
        self.optimal_sentence_length_max = 25
        self.long_sentence_threshold = 35  # Slightly lower threshold
        self.max_long_sentence_percentage = 20.0  # Max 20% of sentences can be >35 words

    def score(self, text: str) -> Dict[str, Any]:
        """
        Score text readability using CV-appropriate metrics.

        Args:
            text: Resume text to analyze

        Returns:
            Dictionary containing:
            - score: Points earned (0-5)
            - max_score: Maximum possible score (5)
            - has_bullets: Whether text has bullet points
            - avg_sentence_length: Average words per sentence
            - long_sentence_percentage: Percentage of sentences >40 words
            - details: Dictionary with breakdown of checks
        """
        # Handle empty or very short text
        if not text or len(text.strip()) < 2:
            return {
                'score': 0,
                'max_score': self.max_score,
                'has_bullets': False,
                'avg_sentence_length': 0,
                'long_sentence_percentage': 0,
                'details': {
                    'bullet_points_check': {'passed': False, 'points': 0},
                    'sentence_length_check': {'passed': False, 'points': 0},
                    'long_sentence_check': {'passed': False, 'points': 0},
                    'total_sentences': 0
                }
            }

        # Check for bullet points
        has_bullets = self._has_bullet_points(text)

        # Analyze sentence lengths
        sentence_lengths = self._get_sentence_lengths(text)

        if not sentence_lengths:
            return {
                'score': 2 if has_bullets else 0,
                'max_score': self.max_score,
                'has_bullets': has_bullets,
                'avg_sentence_length': 0,
                'long_sentence_percentage': 0,
                'details': {
                    'bullet_points_check': {'passed': has_bullets, 'points': 2 if has_bullets else 0},
                    'sentence_length_check': {'passed': False, 'points': 0},
                    'long_sentence_check': {'passed': False, 'points': 0},
                    'total_sentences': 0
                }
            }

        # Calculate average sentence length
        avg_sentence_length = sum(sentence_lengths) / len(sentence_lengths)

        # Calculate percentage of long sentences (>40 words)
        long_sentences = [l for l in sentence_lengths if l > self.long_sentence_threshold]
        long_sentence_percentage = (len(long_sentences) / len(sentence_lengths)) * 100

        # Scoring
        score = 0

        # Check 1: Has bullet points (+2 pts)
        bullet_check_passed = has_bullets
        bullet_points = 2 if bullet_check_passed else 0
        score += bullet_points

        # Check 2: Average sentence length is appropriate (+2 pts)
        sentence_length_check_passed = (
            self.optimal_sentence_length_min <= avg_sentence_length <= self.optimal_sentence_length_max
        )
        sentence_length_points = 2 if sentence_length_check_passed else 0
        score += sentence_length_points

        # Check 3: Not too many long sentences (+1 pt)
        long_sentence_check_passed = long_sentence_percentage <= self.max_long_sentence_percentage
        long_sentence_points = 1 if long_sentence_check_passed else 0
        score += long_sentence_points

        return {
            'score': score,
            'max_score': self.max_score,
            'has_bullets': has_bullets,
            'avg_sentence_length': round(avg_sentence_length, 2),
            'long_sentence_percentage': round(long_sentence_percentage, 2),
            'details': {
                'bullet_points_check': {
                    'passed': bullet_check_passed,
                    'points': bullet_points,
                    'description': 'Structured format with bullet points'
                },
                'sentence_length_check': {
                    'passed': sentence_length_check_passed,
                    'points': sentence_length_points,
                    'avg_length': round(avg_sentence_length, 2),
                    'optimal_range': f'{self.optimal_sentence_length_min}-{self.optimal_sentence_length_max} words',
                    'description': 'Appropriate sentence complexity'
                },
                'long_sentence_check': {
                    'passed': long_sentence_check_passed,
                    'points': long_sentence_points,
                    'percentage': round(long_sentence_percentage, 2),
                    'threshold': f'Max {self.max_long_sentence_percentage}%',
                    'description': 'Not too many overly long sentences'
                },
                'total_sentences': len(sentence_lengths),
                'long_sentences_count': len(long_sentences)
            }
        }

    def _has_bullet_points(self, text: str) -> bool:
        """
        Check if text has bullet points (indicating structured format).

        Args:
            text: Text to check

        Returns:
            True if bullet points found, False otherwise
        """
        # Common bullet point markers
        bullet_patterns = [
            r'[•\-\*]\s+',  # Bullet markers
            r'^\s*[\-\*•]',  # Line starting with bullet
            r'\n\s*[\-\*•]',  # Bullet after newline
        ]

        for pattern in bullet_patterns:
            if re.search(pattern, text, re.MULTILINE):
                return True

        return False

    def _get_sentence_lengths(self, text: str) -> list:
        """
        Get word count for each sentence/bullet point.

        Args:
            text: Text to analyze

        Returns:
            List of word counts per sentence
        """
        if not text or not text.strip():
            return []

        # Split by common sentence/bullet delimiters
        # Split on: periods, question marks, exclamation marks, bullet points, newlines
        sentences = re.split(r'[.!?]+|\n+|[•\-\*]\s+', text)

        sentence_lengths = []
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence:
                # Count words (split by whitespace, filter non-empty)
                words = re.findall(r'\b\w+\b', sentence)
                word_count = len(words)
                if word_count > 0:
                    sentence_lengths.append(word_count)

        return sentence_lengths



def create_scorer() -> ReadabilityScorer:
    """
    Factory function to create ReadabilityScorer instance.

    Returns:
        ReadabilityScorer instance
    """
    return ReadabilityScorer()
