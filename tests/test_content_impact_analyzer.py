"""Tests for ContentImpactAnalyzer service"""
import pytest
from backend.services.content_impact_analyzer import ContentImpactAnalyzer


class TestAchievementStrength:
    """Test achievement strength scoring"""

    @pytest.fixture
    def analyzer(self):
        """Shared analyzer instance for all tests"""
        return ContentImpactAnalyzer()

    def test_classify_verb_tier_transformational(self, analyzer):
        """Tier 4 verbs should return 4"""
        assert analyzer.classify_verb_tier("transformed") == 4
        assert analyzer.classify_verb_tier("pioneered") == 4

    def test_classify_verb_tier_leadership(self, analyzer):
        """Tier 3 verbs should return 3"""
        assert analyzer.classify_verb_tier("led") == 3
        assert analyzer.classify_verb_tier("architected") == 3

    def test_classify_verb_tier_execution(self, analyzer):
        """Tier 2 verbs should return 2"""
        assert analyzer.classify_verb_tier("developed") == 2
        assert analyzer.classify_verb_tier("implemented") == 2

    def test_classify_verb_tier_support(self, analyzer):
        """Tier 1 verbs should return 1"""
        assert analyzer.classify_verb_tier("managed") == 1
        assert analyzer.classify_verb_tier("coordinated") == 1

    def test_classify_verb_tier_weak(self, analyzer):
        """Tier 0 verbs should return 0"""
        assert analyzer.classify_verb_tier("responsible for") == 0
        assert analyzer.classify_verb_tier("worked on") == 0

    def test_classify_verb_tier_unknown(self, analyzer):
        """Unknown verbs should return 1 (neutral)"""
        assert analyzer.classify_verb_tier("xyz") == 1
