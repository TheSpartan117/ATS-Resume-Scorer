"""
Unit tests for A/B Testing Framework
"""

import pytest
import numpy as np
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "backend"))

from services.ab_testing import ABTestFramework, TestResumeCorpus


class TestABTestFramework:
    """Unit tests for ABTestFramework class"""

    @pytest.fixture
    def framework(self):
        return ABTestFramework()

    def test_initialization(self, framework):
        """Test framework initializes correctly"""
        assert framework is not None
        assert framework.results_dir.exists()

    def test_extract_score_from_float(self, framework):
        """Test extracting score from float"""
        assert framework._extract_score(75.5) == 75.5
        assert framework._extract_score(100) == 100.0

    def test_extract_score_from_dict(self, framework):
        """Test extracting score from dictionary"""
        assert framework._extract_score({'overall_score': 80}) == 80.0
        assert framework._extract_score({'score': 75}) == 75.0
        assert framework._extract_score({'total_score': 85}) == 85.0

    def test_extract_score_error(self, framework):
        """Test error handling for invalid score format"""
        with pytest.raises(ValueError):
            framework._extract_score("invalid")

        with pytest.raises(ValueError):
            framework._extract_score({'no_score_key': 100})

    def test_calculate_statistics(self, framework):
        """Test statistical calculations"""
        old_scores = [70, 72, 75, 68, 71]
        new_scores = [75, 77, 80, 73, 76]
        deltas = [n - o for n, o in zip(new_scores, old_scores)]

        stats = framework._calculate_statistics(old_scores, new_scores, deltas, 0.05)

        assert 't_statistic' in stats
        assert 'p_value' in stats
        assert 'is_significant' in stats
        assert 'cohens_d' in stats
        assert 'effect_size' in stats
        assert 'confidence_interval_95' in stats

        # Mean improvement should be 5 points
        assert np.mean(deltas) == 5.0

    def test_interpret_cohens_d(self, framework):
        """Test Cohen's d interpretation"""
        assert framework._interpret_cohens_d(0.1) == "negligible"
        assert framework._interpret_cohens_d(0.3) == "small"
        assert framework._interpret_cohens_d(0.6) == "medium"
        assert framework._interpret_cohens_d(0.9) == "large"
        assert framework._interpret_cohens_d(-0.3) == "small"

    def test_analyze_distributions(self, framework):
        """Test distribution analysis"""
        old_scores = [65, 70, 75, 80, 85]
        new_scores = [70, 75, 80, 85, 90]

        dist = framework._analyze_distributions(old_scores, new_scores)

        assert 'old_distribution' in dist
        assert 'new_distribution' in dist
        assert 'improvement_rate' in dist
        assert 'regression_rate' in dist

        assert dist['old_distribution']['mean'] == 75.0
        assert dist['new_distribution']['mean'] == 80.0
        assert dist['improvement_rate'] == 100.0  # All improved

    def test_generate_recommendation_deploy(self, framework):
        """Test recommendation to deploy"""
        stats = {
            'is_significant': True,
            'p_value': 0.01,
            'cohens_d': 0.8,
            'effect_size': 'medium'
        }
        distribution = {
            'new_distribution': {'mean': 85},
            'old_distribution': {'mean': 75},
            'improvement_rate': 90,
            'regression_rate': 10
        }

        rec = framework._generate_recommendation(stats, distribution)

        assert rec['decision'] == 'DEPLOY'
        assert rec['confidence'] == 'high'
        assert rec['mean_improvement'] == 10

    def test_generate_recommendation_rollback(self, framework):
        """Test recommendation to rollback"""
        stats = {
            'is_significant': True,
            'p_value': 0.01,
            'cohens_d': -0.5,
            'effect_size': 'medium'
        }
        distribution = {
            'new_distribution': {'mean': 65},
            'old_distribution': {'mean': 75},
            'improvement_rate': 20,
            'regression_rate': 80
        }

        rec = framework._generate_recommendation(stats, distribution)

        assert rec['decision'] == 'ROLLBACK'
        assert rec['mean_improvement'] == -10

    def test_generate_recommendation_not_significant(self, framework):
        """Test recommendation when not statistically significant"""
        stats = {
            'is_significant': False,
            'p_value': 0.15,
            'cohens_d': 0.1,
            'effect_size': 'negligible'
        }
        distribution = {
            'new_distribution': {'mean': 76},
            'old_distribution': {'mean': 75},
            'improvement_rate': 55,
            'regression_rate': 45
        }

        rec = framework._generate_recommendation(stats, distribution)

        assert rec['decision'] == 'DO NOT DEPLOY'
        assert rec['confidence'] == 'low'

    def test_compare_scorers_basic(self, framework):
        """Test basic scorer comparison"""
        def old_scorer(resume_data, job_desc=None):
            return {'overall_score': 70}

        def new_scorer(resume_data, job_desc=None):
            return {'overall_score': 75}

        test_resumes = [
            {'id': 'r1', 'text': 'resume 1'},
            {'id': 'r2', 'text': 'resume 2'},
            {'id': 'r3', 'text': 'resume 3'},
        ]

        report = framework.compare_scorers(old_scorer, new_scorer, test_resumes)

        assert report is not None
        assert report['successful_comparisons'] == 3
        assert report['summary']['average_delta'] == 5.0
        assert report['summary']['old_mean'] == 70.0
        assert report['summary']['new_mean'] == 75.0

    def test_compare_metrics(self, framework):
        """Test metric comparison"""
        old_metrics = [
            {'accuracy': 0.70, 'precision': 0.75},
            {'accuracy': 0.72, 'precision': 0.77},
            {'accuracy': 0.71, 'precision': 0.76},
        ]

        new_metrics = [
            {'accuracy': 0.80, 'precision': 0.85},
            {'accuracy': 0.82, 'precision': 0.87},
            {'accuracy': 0.81, 'precision': 0.86},
        ]

        comparisons = framework.compare_metrics(old_metrics, new_metrics, ['accuracy', 'precision'])

        assert 'accuracy' in comparisons
        assert 'precision' in comparisons

        acc = comparisons['accuracy']
        assert acc['old_mean'] == pytest.approx(0.71, abs=0.01)
        assert acc['new_mean'] == pytest.approx(0.81, abs=0.01)
        assert acc['delta'] == pytest.approx(0.10, abs=0.01)

    def test_power_analysis(self, framework):
        """Test statistical power analysis"""
        old_scores = [70, 72, 71, 69, 73, 70, 71, 72, 70, 71]
        new_scores = [75, 77, 76, 74, 78, 75, 76, 77, 75, 76]

        power = framework.run_power_analysis(old_scores, new_scores, desired_power=0.8)

        assert 'achieved_power' in power
        assert 'required_sample_size_for_desired_power' in power
        assert 'is_adequately_powered' in power
        assert power['current_sample_size'] == 10


class TestResumeCorpus:
    """Unit tests for TestResumeCorpus class"""

    @pytest.fixture
    def corpus(self):
        return TestResumeCorpus()

    def test_initialization(self, corpus):
        """Test corpus initializes correctly"""
        assert corpus is not None
        assert corpus.corpus_dir.exists()

    def test_load_corpus(self, corpus):
        """Test loading corpus"""
        resumes = corpus.load_corpus()
        assert isinstance(resumes, list)

    def test_get_corpus_stats(self, corpus):
        """Test getting corpus statistics"""
        stats = corpus.get_corpus_stats()
        assert 'total_resumes' in stats

        if stats['total_resumes'] > 0:
            assert 'unique_roles' in stats
            assert 'unique_experience_levels' in stats
            assert 'roles_distribution' in stats


class TestStatisticalFunctions:
    """Test statistical calculation accuracy"""

    @pytest.fixture
    def framework(self):
        return ABTestFramework()

    def test_paired_ttest(self, framework):
        """Test that t-test is calculated correctly"""
        # Known values
        old_scores = [10, 20, 30, 40, 50]
        new_scores = [15, 25, 35, 45, 55]  # All +5

        deltas = [n - o for n, o in zip(new_scores, old_scores)]

        stats = framework._calculate_statistics(old_scores, new_scores, deltas, 0.05)

        # All values increased by exactly 5
        assert np.mean(deltas) == 5.0

        # Should be statistically significant
        assert stats['is_significant'] == True
        assert stats['p_value'] < 0.05

    def test_confidence_intervals(self, framework):
        """Test confidence interval calculation"""
        old_scores = [70] * 10
        new_scores = [75] * 10  # Perfect +5 increase

        deltas = [n - o for n, o in zip(new_scores, old_scores)]

        stats = framework._calculate_statistics(old_scores, new_scores, deltas, 0.05)

        ci = stats['confidence_interval_95']

        # Mean difference is exactly 5
        assert np.mean(deltas) == 5.0

        # CI should be tight around 5 (no variance)
        assert ci[0] == pytest.approx(5.0, abs=0.1)
        assert ci[1] == pytest.approx(5.0, abs=0.1)

    def test_effect_size_calculation(self, framework):
        """Test Cohen's d calculation"""
        # Large effect
        old_scores = [60, 62, 61, 63, 62]
        new_scores = [80, 82, 81, 83, 82]  # +20 points

        deltas = [n - o for n, o in zip(new_scores, old_scores)]

        stats = framework._calculate_statistics(old_scores, new_scores, deltas, 0.05)

        # Large improvement should have large effect size
        assert stats['effect_size'] in ['large', 'medium']
        assert abs(stats['cohens_d']) > 0.5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
