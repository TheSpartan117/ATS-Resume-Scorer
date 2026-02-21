"""
Tests for P3.2: Word Count Optimization (3 points)

Optimal word count varies by level - too sparse lacks detail, too verbose loses focus.

Level-Specific Ranges:
- Beginner: 300-400 words = 3pts, 250-500 = 2pts, else = 0pts
- Intermediary: 400-600 words = 3pts, 300-700 = 2pts, else = 0pts
- Senior: 500-700 words = 3pts, 400-800 = 2pts, else = 0pts
"""

import pytest
from backend.services.parameters.p3_2_word_count import WordCountScorer, score_word_count


class TestWordCountScorer:
    """Test suite for word count scoring."""

    def setup_method(self):
        """Setup test instance."""
        self.scorer = WordCountScorer()

    # ========================================================================
    # BEGINNER LEVEL TESTS
    # ========================================================================

    def test_beginner_optimal_range_300_words(self):
        """Beginner: 300 words (low end of optimal) = 3 points."""
        content = " ".join(["word"] * 300)
        result = self.scorer.score(content, "beginner")

        assert result['score'] == 3
        assert result['level'] == 'beginner'
        assert result['word_count'] == 300
        assert result['optimal_range'] == (300, 400)
        assert result['in_optimal_range'] is True

    def test_beginner_optimal_range_350_words(self):
        """Beginner: 350 words (middle of optimal) = 3 points."""
        content = " ".join(["word"] * 350)
        result = self.scorer.score(content, "beginner")

        assert result['score'] == 3
        assert result['word_count'] == 350
        assert result['in_optimal_range'] is True

    def test_beginner_optimal_range_400_words(self):
        """Beginner: 400 words (high end of optimal) = 3 points."""
        content = " ".join(["word"] * 400)
        result = self.scorer.score(content, "beginner")

        assert result['score'] == 3
        assert result['word_count'] == 400
        assert result['in_optimal_range'] is True

    def test_beginner_acceptable_range_250_words(self):
        """Beginner: 250 words (low end of acceptable) = 2 points."""
        content = " ".join(["word"] * 250)
        result = self.scorer.score(content, "beginner")

        assert result['score'] == 2
        assert result['word_count'] == 250
        assert result['acceptable_range'] == (250, 500)
        assert result['in_optimal_range'] is False
        assert result['in_acceptable_range'] is True

    def test_beginner_acceptable_range_500_words(self):
        """Beginner: 500 words (high end of acceptable) = 2 points."""
        content = " ".join(["word"] * 500)
        result = self.scorer.score(content, "beginner")

        assert result['score'] == 2
        assert result['word_count'] == 500
        assert result['in_acceptable_range'] is True

    def test_beginner_too_short(self):
        """Beginner: 200 words (below acceptable) = 0 points."""
        content = " ".join(["word"] * 200)
        result = self.scorer.score(content, "beginner")

        assert result['score'] == 0
        assert result['word_count'] == 200
        assert result['in_optimal_range'] is False
        assert result['in_acceptable_range'] is False
        assert result['too_short'] is True

    def test_beginner_too_long(self):
        """Beginner: 600 words (above acceptable) = 0 points."""
        content = " ".join(["word"] * 600)
        result = self.scorer.score(content, "beginner")

        assert result['score'] == 0
        assert result['word_count'] == 600
        assert result['in_optimal_range'] is False
        assert result['in_acceptable_range'] is False
        assert result['too_long'] is True

    # ========================================================================
    # INTERMEDIARY LEVEL TESTS
    # ========================================================================

    def test_intermediary_optimal_range_400_words(self):
        """Intermediary: 400 words (low end of optimal) = 3 points."""
        content = " ".join(["word"] * 400)
        result = self.scorer.score(content, "intermediary")

        assert result['score'] == 3
        assert result['level'] == 'intermediary'
        assert result['word_count'] == 400
        assert result['optimal_range'] == (400, 600)
        assert result['in_optimal_range'] is True

    def test_intermediary_optimal_range_500_words(self):
        """Intermediary: 500 words (middle of optimal) = 3 points."""
        content = " ".join(["word"] * 500)
        result = self.scorer.score(content, "intermediary")

        assert result['score'] == 3
        assert result['word_count'] == 500
        assert result['in_optimal_range'] is True

    def test_intermediary_optimal_range_600_words(self):
        """Intermediary: 600 words (high end of optimal) = 3 points."""
        content = " ".join(["word"] * 600)
        result = self.scorer.score(content, "intermediary")

        assert result['score'] == 3
        assert result['word_count'] == 600
        assert result['in_optimal_range'] is True

    def test_intermediary_acceptable_range_300_words(self):
        """Intermediary: 300 words (low end of acceptable) = 2 points."""
        content = " ".join(["word"] * 300)
        result = self.scorer.score(content, "intermediary")

        assert result['score'] == 2
        assert result['word_count'] == 300
        assert result['acceptable_range'] == (300, 700)
        assert result['in_optimal_range'] is False
        assert result['in_acceptable_range'] is True

    def test_intermediary_acceptable_range_700_words(self):
        """Intermediary: 700 words (high end of acceptable) = 2 points."""
        content = " ".join(["word"] * 700)
        result = self.scorer.score(content, "intermediary")

        assert result['score'] == 2
        assert result['word_count'] == 700
        assert result['in_acceptable_range'] is True

    def test_intermediary_too_short(self):
        """Intermediary: 250 words (below acceptable) = 0 points."""
        content = " ".join(["word"] * 250)
        result = self.scorer.score(content, "intermediary")

        assert result['score'] == 0
        assert result['word_count'] == 250
        assert result['too_short'] is True

    def test_intermediary_too_long(self):
        """Intermediary: 800 words (above acceptable) = 0 points."""
        content = " ".join(["word"] * 800)
        result = self.scorer.score(content, "intermediary")

        assert result['score'] == 0
        assert result['word_count'] == 800
        assert result['too_long'] is True

    # ========================================================================
    # SENIOR LEVEL TESTS
    # ========================================================================

    def test_senior_optimal_range_500_words(self):
        """Senior: 500 words (low end of optimal) = 3 points."""
        content = " ".join(["word"] * 500)
        result = self.scorer.score(content, "senior")

        assert result['score'] == 3
        assert result['level'] == 'senior'
        assert result['word_count'] == 500
        assert result['optimal_range'] == (500, 700)
        assert result['in_optimal_range'] is True

    def test_senior_optimal_range_600_words(self):
        """Senior: 600 words (middle of optimal) = 3 points."""
        content = " ".join(["word"] * 600)
        result = self.scorer.score(content, "senior")

        assert result['score'] == 3
        assert result['word_count'] == 600
        assert result['in_optimal_range'] is True

    def test_senior_optimal_range_700_words(self):
        """Senior: 700 words (high end of optimal) = 3 points."""
        content = " ".join(["word"] * 700)
        result = self.scorer.score(content, "senior")

        assert result['score'] == 3
        assert result['word_count'] == 700
        assert result['in_optimal_range'] is True

    def test_senior_acceptable_range_400_words(self):
        """Senior: 400 words (low end of acceptable) = 2 points."""
        content = " ".join(["word"] * 400)
        result = self.scorer.score(content, "senior")

        assert result['score'] == 2
        assert result['word_count'] == 400
        assert result['acceptable_range'] == (400, 800)
        assert result['in_optimal_range'] is False
        assert result['in_acceptable_range'] is True

    def test_senior_acceptable_range_800_words(self):
        """Senior: 800 words (high end of acceptable) = 2 points."""
        content = " ".join(["word"] * 800)
        result = self.scorer.score(content, "senior")

        assert result['score'] == 2
        assert result['word_count'] == 800
        assert result['in_acceptable_range'] is True

    def test_senior_too_short(self):
        """Senior: 350 words (below acceptable) = 0 points."""
        content = " ".join(["word"] * 350)
        result = self.scorer.score(content, "senior")

        assert result['score'] == 0
        assert result['word_count'] == 350
        assert result['too_short'] is True

    def test_senior_too_long(self):
        """Senior: 900 words (above acceptable) = 0 points."""
        content = " ".join(["word"] * 900)
        result = self.scorer.score(content, "senior")

        assert result['score'] == 0
        assert result['word_count'] == 900
        assert result['too_long'] is True

    # ========================================================================
    # EDGE CASES
    # ========================================================================

    def test_empty_content(self):
        """Empty content = 0 points."""
        result = self.scorer.score("", "intermediary")

        assert result['score'] == 0
        assert result['word_count'] == 0
        assert result['too_short'] is True

    def test_whitespace_only(self):
        """Whitespace-only content = 0 points."""
        result = self.scorer.score("   \n\t   ", "intermediary")

        assert result['score'] == 0
        assert result['word_count'] == 0

    def test_single_word(self):
        """Single word = 0 points."""
        result = self.scorer.score("Hello", "intermediary")

        assert result['score'] == 0
        assert result['word_count'] == 1

    def test_multiple_sections_combined(self):
        """Multiple sections should combine word counts."""
        sections = {
            'summary': "This is a summary with ten words in it for testing.",
            'experience': " ".join(["experience"] * 250),
            'skills': " ".join(["skills"] * 50),
            'education': " ".join(["education"] * 40)
        }

        result = self.scorer.score_from_sections(sections, "intermediary")

        # 11 + 250 + 50 + 40 = 351 words (summary has 11 words)
        assert result['word_count'] == 351
        assert result['score'] == 2  # Acceptable range for intermediary

    def test_punctuation_and_formatting(self):
        """Punctuation should not inflate word count."""
        content = "Hello, world! This is a test... Yes, it is."
        result = self.scorer.score(content, "beginner")

        # Should count 9 words, not including punctuation marks
        assert result['word_count'] == 9

    def test_case_insensitive_level(self):
        """Level parameter should be case-insensitive."""
        content = " ".join(["word"] * 350)

        result1 = self.scorer.score(content, "BEGINNER")
        result2 = self.scorer.score(content, "Beginner")
        result3 = self.scorer.score(content, "beginner")

        assert result1['level'] == 'beginner'
        assert result2['level'] == 'beginner'
        assert result3['level'] == 'beginner'
        assert result1['score'] == result2['score'] == result3['score'] == 3

    def test_invalid_level_defaults_to_intermediary(self):
        """Invalid level should default to intermediary."""
        content = " ".join(["word"] * 500)
        result = self.scorer.score(content, "invalid_level")

        assert result['level'] == 'intermediary'
        assert result['optimal_range'] == (400, 600)

    # ========================================================================
    # CONVENIENCE FUNCTION TESTS
    # ========================================================================

    def test_convenience_function(self):
        """Test the convenience function."""
        content = " ".join(["word"] * 350)
        result = score_word_count(content, "beginner")

        assert result['score'] == 3
        assert result['word_count'] == 350

    # ========================================================================
    # DETAILED ANALYSIS TESTS
    # ========================================================================

    def test_detailed_analysis_includes_all_fields(self):
        """Result should include all expected fields."""
        content = " ".join(["word"] * 450)
        result = self.scorer.score(content, "intermediary")

        # Required fields
        assert 'score' in result
        assert 'level' in result
        assert 'word_count' in result
        assert 'optimal_range' in result
        assert 'acceptable_range' in result
        assert 'in_optimal_range' in result
        assert 'in_acceptable_range' in result
        assert 'too_short' in result
        assert 'too_long' in result

    def test_feedback_message_optimal(self):
        """Should provide helpful feedback for optimal range."""
        content = " ".join(["word"] * 500)
        result = self.scorer.score(content, "intermediary")

        assert 'feedback' in result
        assert 'optimal' in result['feedback'].lower()

    def test_feedback_message_too_short(self):
        """Should provide helpful feedback when too short."""
        content = " ".join(["word"] * 200)
        result = self.scorer.score(content, "intermediary")

        assert 'feedback' in result
        assert 'short' in result['feedback'].lower() or 'more' in result['feedback'].lower()

    def test_feedback_message_too_long(self):
        """Should provide helpful feedback when too long."""
        content = " ".join(["word"] * 900)
        result = self.scorer.score(content, "intermediary")

        assert 'feedback' in result
        assert 'long' in result['feedback'].lower() or 'concise' in result['feedback'].lower()
