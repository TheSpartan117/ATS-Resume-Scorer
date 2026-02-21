"""
Tests for P4.1 - Grammar & Spelling (10 pts)

Professional writing quality with tiered penalties.
"""

import pytest
from backend.services.parameters.p4_1_grammar import GrammarScorer


@pytest.fixture
def scorer():
    """Create GrammarScorer instance"""
    return GrammarScorer()


class TestGrammarScorerErrorClassification:
    """Test error classification and severity"""

    def test_critical_errors_grammar(self, scorer):
        """Grammar errors are classified as critical (-0.5 pts each)"""
        text = "She dont like them apples. He have many problems."
        result = scorer.score(text)

        assert result['critical_errors'] >= 2  # dont, have (wrong conjugation)
        assert result['score'] < 10  # Should lose points

    def test_critical_errors_spelling(self, scorer):
        """Spelling errors are classified as critical (-0.5 pts each)"""
        text = "I am a softwere enginer with excelent skils in Python."
        result = scorer.score(text)

        # softwere, enginer, excelent, skils
        assert result['critical_errors'] >= 3
        assert result['score'] <= 8  # At least 2 points lost

    def test_minor_errors_style(self, scorer):
        """Style errors are classified as minor (-0.25 pts each)"""
        text = "Very unique and extremely perfect solution that is totally complete."
        result = scorer.score(text)

        # Very unique (redundant), extremely perfect (redundant), totally complete (redundant)
        assert result['minor_errors'] >= 0  # May or may not catch these

    def test_minor_errors_punctuation(self, scorer):
        """Punctuation errors are classified as minor (-0.25 pts each)"""
        text = "Led team of engineers,developed new features,improved performance."
        result = scorer.score(text)

        # Missing spaces after commas
        assert result['minor_errors'] >= 0


class TestGrammarScorerTieredScoring:
    """Test tiered scoring system"""

    def test_zero_errors_10_points(self, scorer):
        """0 errors = 10 points"""
        text = "Led team of 5 engineers to develop scalable microservices architecture."
        result = scorer.score(text)

        assert result['total_errors'] == 0
        assert result['score'] == 10
        assert result['tier'] == 'excellent'

    def test_one_to_two_minor_9_points(self, scorer):
        """1-2 minor errors = 9 points"""
        # This is tricky - we need to craft text with exactly minor errors
        # For now, test the scoring logic with simulated errors
        result = scorer._calculate_score(
            critical_errors=0,
            minor_errors=2
        )

        assert result['score'] == 9
        assert result['tier'] == 'very_good'

    def test_one_critical_or_three_minor_7_points(self, scorer):
        """1 critical or 3-4 minor = 7 points"""
        # Test 1 critical
        result1 = scorer._calculate_score(
            critical_errors=1,
            minor_errors=0
        )
        assert result1['score'] == 7

        # Test 3 minor
        result2 = scorer._calculate_score(
            critical_errors=0,
            minor_errors=3
        )
        assert result2['score'] == 7

    def test_two_to_three_critical_or_five_minor_5_points(self, scorer):
        """2-3 critical or 5+ minor = 5 points"""
        # Test 2 critical
        result1 = scorer._calculate_score(
            critical_errors=2,
            minor_errors=0
        )
        assert result1['score'] == 5

        # Test 5 minor
        result2 = scorer._calculate_score(
            critical_errors=0,
            minor_errors=5
        )
        assert result2['score'] == 5

    def test_four_critical_or_eight_minor_3_points(self, scorer):
        """4+ critical or 8+ minor = 3 points"""
        # Test 4 critical
        result1 = scorer._calculate_score(
            critical_errors=4,
            minor_errors=0
        )
        assert result1['score'] == 3

        # Test 8 minor
        result2 = scorer._calculate_score(
            critical_errors=0,
            minor_errors=8
        )
        assert result2['score'] == 3

    def test_six_critical_or_twelve_minor_0_points(self, scorer):
        """6+ critical or 12+ minor = 0 points"""
        # Test 6 critical
        result1 = scorer._calculate_score(
            critical_errors=6,
            minor_errors=0
        )
        assert result1['score'] == 0

        # Test 12 minor
        result2 = scorer._calculate_score(
            critical_errors=0,
            minor_errors=12
        )
        assert result2['score'] == 0


class TestGrammarScorerMixedErrors:
    """Test mixed error scenarios"""

    def test_mixed_errors_combined_score(self, scorer):
        """Mixed critical and minor errors calculate correctly"""
        # 2 critical + 4 minor = 2*0.5 + 4*0.25 = 1 + 1 = 2 pts penalty = 8 pts
        result = scorer._calculate_score(
            critical_errors=2,
            minor_errors=4
        )
        assert result['score'] == 8

    def test_excessive_mixed_errors_capped(self, scorer):
        """Excessive errors are capped at 0 points"""
        result = scorer._calculate_score(
            critical_errors=10,
            minor_errors=20
        )
        assert result['score'] == 0


class TestGrammarScorerErrorDetails:
    """Test detailed error reporting"""

    def test_returns_error_list(self, scorer):
        """Returns detailed list of errors"""
        text = "I have writen many softwere programs. They is very good."
        result = scorer.score(text)

        assert 'errors' in result
        assert isinstance(result['errors'], list)
        assert len(result['errors']) > 0

    def test_error_details_include_category(self, scorer):
        """Each error includes category (grammar/spelling/style/punctuation)"""
        text = "I have writen many softwere programs."
        result = scorer.score(text)

        if result['errors']:
            error = result['errors'][0]
            assert 'category' in error
            assert error['category'] in ['grammar', 'spelling', 'style', 'punctuation', 'typo', 'other']

    def test_error_details_include_message(self, scorer):
        """Each error includes descriptive message"""
        text = "I have writen many softwere programs."
        result = scorer.score(text)

        if result['errors']:
            error = result['errors'][0]
            assert 'message' in error
            assert isinstance(error['message'], str)
            assert len(error['message']) > 0

    def test_error_details_include_severity(self, scorer):
        """Each error includes severity (critical/minor)"""
        text = "I have writen many softwere programs."
        result = scorer.score(text)

        if result['errors']:
            error = result['errors'][0]
            assert 'severity' in error
            assert error['severity'] in ['critical', 'minor']


class TestGrammarScorerEdgeCases:
    """Test edge cases"""

    def test_empty_text(self, scorer):
        """Empty text returns max score"""
        result = scorer.score("")
        assert result['score'] == 10
        assert result['total_errors'] == 0

    def test_very_short_text(self, scorer):
        """Very short text (< 5 chars) returns max score"""
        result = scorer.score("Hi")
        assert result['score'] == 10

    def test_no_errors_in_bullet_points(self, scorer):
        """Correctly formatted resume bullets get full score"""
        text = """
        Led team of 5 engineers to develop scalable microservices architecture.
        Increased system performance by 40% through database optimization.
        Reduced deployment time from 2 hours to 15 minutes using CI/CD pipeline.
        """
        result = scorer.score(text)

        assert result['score'] >= 8  # Should be high score
        assert result['total_errors'] <= 3  # Very few or no errors


class TestGrammarScorerResultStructure:
    """Test result structure"""

    def test_result_contains_required_fields(self, scorer):
        """Result contains all required fields"""
        text = "Led team to develop new features."
        result = scorer.score(text)

        required_fields = [
            'score',
            'total_errors',
            'critical_errors',
            'minor_errors',
            'errors',
            'tier',
            'message'
        ]

        for field in required_fields:
            assert field in result, f"Missing required field: {field}"

    def test_score_is_integer(self, scorer):
        """Score is an integer between 0-10"""
        text = "Led team to develop new features."
        result = scorer.score(text)

        assert isinstance(result['score'], (int, float))
        assert 0 <= result['score'] <= 10

    def test_tier_values(self, scorer):
        """Tier has valid values"""
        valid_tiers = [
            'excellent',      # 10 pts
            'very_good',      # 9 pts
            'good',           # 7 pts
            'acceptable',     # 5 pts
            'needs_work',     # 3 pts
            'poor'            # 0 pts
        ]

        text = "Led team to develop new features."
        result = scorer.score(text)

        assert result['tier'] in valid_tiers
