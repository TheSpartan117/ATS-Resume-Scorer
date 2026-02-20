"""Tests for WritingQualityAnalyzer service"""
import pytest
from backend.services.writing_quality_analyzer import WritingQualityAnalyzer


class TestGrammarSeverityScoring:
    """Test severity-weighted grammar scoring"""

    def test_score_grammar_no_errors(self):
        """No errors should score 10/10"""
        analyzer = WritingQualityAnalyzer()
        result = analyzer.score_grammar_with_severity([])

        assert result['score'] == 10.0
        assert result['total_errors'] == 0
        assert result['deduction'] == 0.0

    def test_score_grammar_spelling_errors(self):
        """Spelling errors should deduct 2 pts each"""
        analyzer = WritingQualityAnalyzer()
        errors = [
            {'category': 'spelling', 'message': 'Typo: managment'},
            {'category': 'spelling', 'message': 'Typo: recieve'}
        ]
        result = analyzer.score_grammar_with_severity(errors)

        assert result['score'] == 6.0  # 10 - 4
        assert result['deduction'] == 4.0

    def test_score_grammar_mixed_severity(self):
        """Mixed errors should apply weighted deductions"""
        analyzer = WritingQualityAnalyzer()
        errors = [
            {'category': 'spelling', 'message': 'Spelling error'},      # -2
            {'category': 'grammar', 'message': 'Grammar error'},        # -1.5
            {'category': 'punctuation', 'message': 'Missing comma'},    # -1
            {'category': 'style', 'message': 'Style suggestion'}        # -0.5
        ]
        result = analyzer.score_grammar_with_severity(errors)

        assert result['score'] == 5.0  # 10 - 5
        assert result['deduction'] == 5.0

    def test_score_grammar_capped_at_zero(self):
        """Deductions should cap at 10 (score = 0)"""
        analyzer = WritingQualityAnalyzer()
        errors = [{'category': 'spelling', 'message': 'Error'} for _ in range(10)]
        result = analyzer.score_grammar_with_severity(errors)

        assert result['score'] == 0.0
        assert result['deduction'] == 10.0  # Capped
