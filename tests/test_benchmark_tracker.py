"""Tests for BenchmarkTracker service"""
import pytest
from backend.services.benchmark_tracker import BenchmarkTracker


class TestScoreTracking:
    """Test score distribution tracking"""

    def test_track_score_stores_data(self):
        """Should store score with metadata"""
        tracker = BenchmarkTracker()

        tracker.track_score(
            score=75.5,
            role="software_engineer",
            level="senior",
            metadata={'sections': 4, 'word_count': 450}
        )

        assert tracker.get_score_count() > 0

    def test_track_multiple_scores(self):
        """Should track multiple scores"""
        tracker = BenchmarkTracker()

        scores = [70, 75, 80, 85, 90]
        for score in scores:
            tracker.track_score(score, role="software_engineer", level="mid")

        assert tracker.get_score_count() == 5

    def test_get_distribution_by_role(self):
        """Should calculate distribution by role"""
        tracker = BenchmarkTracker()

        # Add scores for software engineers
        for score in [70, 75, 80, 85, 90]:
            tracker.track_score(score, role="software_engineer", level="mid")

        # Add scores for product managers
        for score in [65, 70, 75]:
            tracker.track_score(score, role="product_manager", level="mid")

        se_dist = tracker.get_distribution(role="software_engineer")
        pm_dist = tracker.get_distribution(role="product_manager")

        assert se_dist['count'] == 5
        assert pm_dist['count'] == 3
        assert se_dist['mean'] > pm_dist['mean']


class TestPercentileCalculation:
    """Test percentile calculations"""

    def test_calculate_percentile_median(self):
        """Should calculate correct percentile for median score"""
        tracker = BenchmarkTracker()

        scores = list(range(50, 101))  # 50 to 100
        for score in scores:
            tracker.track_score(score, role="software_engineer", level="mid")

        # 75 should be around 50th percentile
        percentile = tracker.calculate_percentile(
            score=75,
            role="software_engineer",
            level="mid"
        )

        assert 45 <= percentile <= 55  # Around median

    def test_calculate_percentile_high_score(self):
        """Should calculate correct percentile for high score"""
        tracker = BenchmarkTracker()

        scores = list(range(50, 101))
        for score in scores:
            tracker.track_score(score, role="software_engineer", level="mid")

        percentile = tracker.calculate_percentile(
            score=95,
            role="software_engineer",
            level="mid"
        )

        assert percentile >= 85  # High percentile

    def test_calculate_percentile_low_score(self):
        """Should calculate correct percentile for low score"""
        tracker = BenchmarkTracker()

        scores = list(range(50, 101))
        for score in scores:
            tracker.track_score(score, role="software_engineer", level="mid")

        percentile = tracker.calculate_percentile(
            score=55,
            role="software_engineer",
            level="mid"
        )

        assert percentile <= 15  # Low percentile

    def test_percentile_insufficient_data(self):
        """Should handle insufficient data gracefully"""
        tracker = BenchmarkTracker()

        # Only 2 scores
        tracker.track_score(70, role="software_engineer", level="mid")
        tracker.track_score(80, role="software_engineer", level="mid")

        result = tracker.calculate_percentile(75, role="software_engineer", level="mid")

        # Should return None or a message indicating insufficient data
        assert result is None or isinstance(result, dict)


class TestCompetitivePositioning:
    """Test competitive positioning analysis"""

    def test_get_competitive_position_top_tier(self):
        """Should identify top tier resumes"""
        tracker = BenchmarkTracker()

        # Add benchmark scores
        for score in range(60, 96):
            tracker.track_score(score, role="software_engineer", level="senior")

        position = tracker.get_competitive_position(
            score=90,
            role="software_engineer",
            level="senior"
        )

        assert position['tier'] == 'top'
        assert position['percentile'] > 80

    def test_get_competitive_position_competitive(self):
        """Should identify competitive resumes"""
        tracker = BenchmarkTracker()

        for score in range(60, 96):
            tracker.track_score(score, role="software_engineer", level="senior")

        position = tracker.get_competitive_position(
            score=75,
            role="software_engineer",
            level="senior"
        )

        assert position['tier'] in ['competitive', 'above_average']

    def test_get_competitive_position_needs_work(self):
        """Should identify resumes needing improvement"""
        tracker = BenchmarkTracker()

        for score in range(60, 96):
            tracker.track_score(score, role="software_engineer", level="senior")

        position = tracker.get_competitive_position(
            score=62,
            role="software_engineer",
            level="senior"
        )

        assert position['tier'] in ['needs_improvement', 'below_average']


class TestOutlierDetection:
    """Test outlier identification"""

    def test_identify_outliers_high(self):
        """Should identify high-scoring outliers"""
        tracker = BenchmarkTracker()

        # Normal distribution around 75
        for score in [70, 72, 74, 75, 76, 78, 80]:
            tracker.track_score(score, role="software_engineer", level="mid")

        # Outlier
        tracker.track_score(95, role="software_engineer", level="mid")

        outliers = tracker.identify_outliers(role="software_engineer", level="mid")

        assert len(outliers) > 0
        assert any(o['score'] == 95 for o in outliers)

    def test_identify_outliers_low(self):
        """Should identify low-scoring outliers"""
        tracker = BenchmarkTracker()

        # Normal distribution around 75
        for score in [70, 72, 74, 75, 76, 78, 80]:
            tracker.track_score(score, role="software_engineer", level="mid")

        # Outlier
        tracker.track_score(45, role="software_engineer", level="mid")

        outliers = tracker.identify_outliers(role="software_engineer", level="mid")

        assert len(outliers) > 0
        assert any(o['score'] == 45 for o in outliers)

    def test_no_outliers_uniform_distribution(self):
        """Should find no outliers in uniform distribution"""
        tracker = BenchmarkTracker()

        # Uniform distribution
        for score in range(70, 81):
            tracker.track_score(score, role="software_engineer", level="mid")

        outliers = tracker.identify_outliers(role="software_engineer", level="mid")

        assert len(outliers) == 0


class TestStatistics:
    """Test statistical calculations"""

    def test_get_statistics_complete(self):
        """Should calculate complete statistics"""
        tracker = BenchmarkTracker()

        scores = [70, 75, 80, 85, 90]
        for score in scores:
            tracker.track_score(score, role="software_engineer", level="mid")

        stats = tracker.get_statistics(role="software_engineer", level="mid")

        assert 'mean' in stats
        assert 'median' in stats
        assert 'std_dev' in stats
        assert 'min' in stats
        assert 'max' in stats
        assert stats['count'] == 5

    def test_statistics_by_level(self):
        """Should differentiate statistics by level"""
        tracker = BenchmarkTracker()

        # Entry level scores (generally lower)
        for score in [60, 65, 70]:
            tracker.track_score(score, role="software_engineer", level="entry")

        # Senior level scores (generally higher)
        for score in [80, 85, 90]:
            tracker.track_score(score, role="software_engineer", level="senior")

        entry_stats = tracker.get_statistics(role="software_engineer", level="entry")
        senior_stats = tracker.get_statistics(role="software_engineer", level="senior")

        assert entry_stats['mean'] < senior_stats['mean']


class TestBenchmarkComparison:
    """Test benchmark comparison functionality"""

    def test_compare_to_benchmark(self):
        """Should provide meaningful comparison"""
        tracker = BenchmarkTracker()

        # Add benchmark data
        for score in range(65, 91):
            tracker.track_score(score, role="software_engineer", level="senior")

        comparison = tracker.compare_to_benchmark(
            score=82,
            role="software_engineer",
            level="senior"
        )

        assert 'percentile' in comparison
        assert 'vs_average' in comparison
        assert 'tier' in comparison
        assert 'message' in comparison

    def test_comparison_message_above_average(self):
        """Should provide encouraging message for above-average scores"""
        tracker = BenchmarkTracker()

        for score in range(60, 91):
            tracker.track_score(score, role="software_engineer", level="mid")

        comparison = tracker.compare_to_benchmark(85, role="software_engineer", level="mid")

        assert 'above' in comparison['message'].lower() or 'strong' in comparison['message'].lower()

    def test_comparison_message_below_average(self):
        """Should provide constructive message for below-average scores"""
        tracker = BenchmarkTracker()

        for score in range(60, 91):
            tracker.track_score(score, role="software_engineer", level="mid")

        comparison = tracker.compare_to_benchmark(65, role="software_engineer", level="mid")

        assert 'below' in comparison['message'].lower() or 'improve' in comparison['message'].lower()
