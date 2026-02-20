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


class TestMetricDetection:
    """Test metric pattern detection"""

    @pytest.fixture
    def analyzer(self):
        """Shared analyzer instance for all tests"""
        return ContentImpactAnalyzer()

    def test_extract_metrics_percentage(self, analyzer):
        """Should extract percentage metrics"""
        text = "Increased revenue by 45% and reduced costs by 30%"
        metrics = analyzer.extract_metrics(text)
        assert len(metrics) >= 2
        assert any(m['value'] == '45%' and m['type'] == 'percentage' for m in metrics)
        assert any(m['value'] == '30%' and m['type'] == 'percentage' for m in metrics)

    def test_extract_metrics_money(self, analyzer):
        """Should extract money metrics"""
        text = "Generated $2M in revenue and saved $500K in costs"
        metrics = analyzer.extract_metrics(text)
        assert len(metrics) == 2
        assert any(m['value'] == '$2M' and m['type'] == 'money' for m in metrics)
        assert any(m['value'] == '$500K' and m['type'] == 'money' for m in metrics)

    def test_extract_metrics_multiplier(self, analyzer):
        """Should extract multiplier metrics"""
        text = "Improved performance by 3x"
        metrics = analyzer.extract_metrics(text)
        assert len(metrics) >= 1
        assert any(m['value'] == '3x' and m['type'] == 'multiplier' for m in metrics)

    def test_extract_metrics_count(self, analyzer):
        """Should extract count metrics"""
        text = "Managed 12 teams and 150 users"
        metrics = analyzer.extract_metrics(text)
        assert len(metrics) >= 2
        # Should find "12 teams" and "150 users"

    def test_evaluate_metric_quality_high(self, analyzer):
        """Money and percentage should be high quality (1.0)"""
        assert analyzer.evaluate_metric_quality('money') == 1.0
        assert analyzer.evaluate_metric_quality('percentage') == 1.0

    def test_evaluate_metric_quality_medium(self, analyzer):
        """Counts and time should be medium quality (0.7)"""
        assert analyzer.evaluate_metric_quality('count') == 0.7
        assert analyzer.evaluate_metric_quality('time') == 0.7
