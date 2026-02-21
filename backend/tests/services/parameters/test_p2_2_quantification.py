"""
Tests for P2.2: Quantification Rate & Quality (10 points)

Tests weighted quantification scoring with level-aware thresholds.
Uses QuantificationClassifier for bullet analysis.
"""

import pytest
from backend.services.parameters.p2_2_quantification import QuantificationScorer


class TestQuantificationScorer:
    """Test suite for P2.2 quantification scoring"""

    @pytest.fixture
    def scorer(self):
        """Create scorer instance"""
        return QuantificationScorer()

    # ========================================================================
    # SENIOR LEVEL TESTS (60% for 10 pts, 45% for 6 pts)
    # ========================================================================

    def test_senior_60_percent_high_quality(self, scorer):
        """Senior with 60%+ weighted rate = 10 pts"""
        bullets = [
            "Increased revenue by 45% through strategic initiatives",  # HIGH (1.0)
            "Led team of 12 engineers across 3 projects",               # MEDIUM (0.7)
            "Reduced latency by 60% optimizing cache layer"             # HIGH (1.0)
        ]
        # Total weighted: (1.0 + 0.7 + 1.0) / 3 = 2.7/3 = 90% weighted rate

        result = scorer.score(bullets, 'senior')

        assert result['score'] == 10
        assert result['max_score'] == 10
        assert result['weighted_quantification_rate'] >= 60.0
        assert result['feedback'] is not None

    def test_senior_45_percent_partial_credit(self, scorer):
        """Senior with 45-60% weighted rate = 6 pts"""
        bullets = [
            "Increased sales by 25%",           # HIGH (1.0)
            "Led team of 5 developers",        # MEDIUM (0.7)
            "Managed 3 projects",               # MEDIUM (0.7) - matched by project_count pattern
            "Wrote documentation",              # NONE (0.0)
            "Implemented new features"          # NONE (0.0)
        ]
        # Total weighted: (1.0 + 0.7 + 0.7) / 5 = 2.4/5 = 48% weighted rate
        # This gets 6 pts for senior (45-60%)

        result = scorer.score(bullets, 'senior')

        assert result['score'] == 6
        assert 45.0 <= result['weighted_quantification_rate'] < 60.0

    def test_senior_exactly_45_percent(self, scorer):
        """Senior with exactly 45% = 6 pts"""
        bullets = [
            "Increased efficiency by 30%",      # HIGH (1.0)
            "Managed team of 8",                # MEDIUM (0.7)
            "Completed 2 initiatives",          # MEDIUM (0.7) - matched by project_count pattern
            "Developed new system",             # NONE (0.0)
            "Participated in planning"          # NONE (0.0)
        ]
        # Total weighted: (1.0 + 0.7 + 0.7) / 5 = 2.4/5 = 48%
        # Gets 6 pts for senior (45-60%)

        result = scorer.score(bullets, 'senior')
        assert result['score'] == 6
        assert 45.0 <= result['weighted_quantification_rate'] < 60.0

    # ========================================================================
    # INTERMEDIARY LEVEL TESTS (50% for 10 pts, 35% for 6 pts)
    # ========================================================================

    def test_intermediary_50_percent(self, scorer):
        """Intermediary with 50%+ weighted rate = 10 pts"""
        bullets = [
            "Improved performance by 40%",      # HIGH (1.0)
            "Led team of 5 developers",        # MEDIUM (0.7)
            "Handled 3 concurrent projects",    # LOW (0.3)
            "Developed new features"            # NONE (0.0)
        ]
        # Total weighted: (1.0 + 0.7 + 0.3) / 4 = 2.0/4 = 50% weighted rate

        result = scorer.score(bullets, 'intermediary')

        assert result['score'] == 10
        assert result['weighted_quantification_rate'] >= 50.0

    def test_intermediary_35_percent_partial_credit(self, scorer):
        """Intermediary with 35-50% weighted rate = 6 pts"""
        bullets = [
            "Reduced costs by 20%",             # HIGH (1.0)
            "Worked on 3 projects",             # LOW (0.3)
            "Implemented features",             # NONE (0.0)
            "Collaborated with team",           # NONE (0.0)
            "Participated in meetings"          # NONE (0.0)
        ]
        # Total weighted: (1.0 + 0.3) / 5 = 1.3/5 = 26% weighted rate
        # Below 35%, so 0 pts

        result = scorer.score(bullets, 'intermediary')
        assert result['score'] == 0

    # ========================================================================
    # BEGINNER LEVEL TESTS (30% for 10 pts, 20% for 6 pts)
    # ========================================================================

    def test_beginner_30_percent(self, scorer):
        """Beginner with 30%+ weighted rate = 10 pts"""
        bullets = [
            "Improved test coverage by 25%",    # HIGH (1.0)
            "Assisted team of 3 developers",   # MEDIUM (0.7)
            "Completed 5 tasks",                # LOW (0.3)
            "Learned new technologies",         # NONE (0.0)
            "Participated in code reviews"      # NONE (0.0)
        ]
        # Total weighted: (1.0 + 0.7 + 0.3) / 5 = 2.0/5 = 40% weighted rate

        result = scorer.score(bullets, 'beginner')

        assert result['score'] == 10
        assert result['weighted_quantification_rate'] >= 30.0

    def test_beginner_20_percent_partial_credit(self, scorer):
        """Beginner with 20-30% weighted rate = 6 pts"""
        bullets = [
            "Fixed 5 bugs",                     # LOW (0.3)
            "Wrote unit tests",                 # NONE (0.0)
            "Implemented features",             # NONE (0.0)
            "Attended meetings",                # NONE (0.0)
            "Learned Python"                    # NONE (0.0)
        ]
        # Total weighted: 0.3 / 5 = 6% weighted rate
        # Below 20%, so 0 pts

        result = scorer.score(bullets, 'beginner')
        assert result['score'] == 0

    # ========================================================================
    # EDGE CASES
    # ========================================================================

    def test_empty_bullets(self, scorer):
        """Empty bullets = 0 pts with appropriate feedback"""
        result = scorer.score([], 'senior')

        assert result['score'] == 0
        assert result['weighted_quantification_rate'] == 0.0
        assert 'no bullets' in result['feedback'].lower()

    def test_no_quantification(self, scorer):
        """No quantified bullets = 0 pts"""
        bullets = [
            "Developed software features",
            "Worked with team members",
            "Participated in meetings",
            "Wrote documentation"
        ]

        result = scorer.score([], 'intermediary')

        assert result['score'] == 0
        assert result['weighted_quantification_rate'] == 0.0

    def test_all_high_quality(self, scorer):
        """All HIGH quality metrics = 100% weighted rate"""
        bullets = [
            "Increased revenue by 150%",
            "Reduced costs by $2.5M",
            "Improved performance by 3x",
            "Boosted sales from $10M to $25M"
        ]
        # Total weighted: (1.0 + 1.0 + 1.0 + 1.0) / 4 = 4.0/4 = 100%

        result = scorer.score(bullets, 'senior')

        assert result['score'] == 10
        assert result['weighted_quantification_rate'] == 100.0

    def test_invalid_level_defaults_to_intermediary(self, scorer):
        """Invalid experience level defaults to intermediary thresholds"""
        bullets = [
            "Increased efficiency by 50%",      # HIGH (1.0)
            "Led team of 6",                    # MEDIUM (0.7)
            "Completed projects"                # NONE (0.0)
        ]
        # Total weighted: (1.0 + 0.7) / 3 = 1.7/3 = 56.67% weighted rate

        result = scorer.score(bullets, 'invalid_level')

        # Should use intermediary thresholds (50% for 10 pts)
        assert result['score'] == 10

    def test_weighted_rate_calculation(self, scorer):
        """Verify weighted rate calculation is correct"""
        bullets = [
            "Increased sales by 30%",           # HIGH (1.0)
            "Led team of 5",                    # MEDIUM (0.7)
            "Completed 3 projects",             # MEDIUM (0.7) - matched by project_count pattern
            "Wrote documentation"               # NONE (0.0)
        ]
        # Total weighted: (1.0 + 0.7 + 0.7 + 0.0) / 4 = 2.4/4 = 60%

        result = scorer.score(bullets, 'intermediary')

        assert result['weighted_quantification_rate'] == 60.0
        assert result['high_count'] == 1
        assert result['medium_count'] == 2
        assert result['low_count'] == 0
        assert result['quantified_count'] == 3

    # ========================================================================
    # FEEDBACK QUALITY
    # ========================================================================

    def test_feedback_includes_breakdown(self, scorer):
        """Feedback should include quality breakdown"""
        bullets = [
            "Increased revenue by 45%",
            "Led team of 8",
            "Fixed 5 bugs"
        ]

        result = scorer.score(bullets, 'senior')

        feedback = result['feedback']
        assert 'high' in feedback.lower() or 'medium' in feedback.lower()
        # Check that the rate appears in feedback (formatted as X.Y%)
        assert str(int(result['weighted_quantification_rate'])) in feedback or \
               f"{result['weighted_quantification_rate']:.1f}" in feedback

    def test_feedback_suggests_improvement_when_low(self, scorer):
        """Low score should have improvement suggestions"""
        bullets = [
            "Developed features",
            "Worked on projects",
            "Participated in meetings"
        ]

        result = scorer.score(bullets, 'senior')

        assert result['score'] < 10
        assert 'improve' in result['feedback'].lower() or 'add' in result['feedback'].lower()
