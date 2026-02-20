"""
A/B Testing Framework for ATS Scorer
Validates improvements through statistical comparison
"""

import numpy as np
from scipy import stats
from typing import Dict, List, Tuple, Any, Callable
import json
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class ABTestFramework:
    """Framework for comparing old vs new scoring algorithms"""

    def __init__(self, results_dir: str = "/tmp/ab_test_results"):
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(parents=True, exist_ok=True)

    def compare_scorers(
        self,
        old_scorer: Callable,
        new_scorer: Callable,
        test_resumes: List[Dict[str, Any]],
        job_descriptions: List[str] = None,
        alpha: float = 0.05
    ) -> Dict[str, Any]:
        """
        Compare two scoring algorithms using statistical tests

        Args:
            old_scorer: Original scoring function
            new_scorer: Improved scoring function
            test_resumes: List of test resume data
            job_descriptions: Optional list of job descriptions for each resume
            alpha: Significance level (default 0.05)

        Returns:
            Comprehensive comparison report with statistical analysis
        """
        logger.info(f"Starting A/B test with {len(test_resumes)} resumes")

        old_scores = []
        new_scores = []
        deltas = []
        detailed_results = []

        for idx, resume_data in enumerate(test_resumes):
            try:
                # Get job description if provided
                job_desc = job_descriptions[idx] if job_descriptions and idx < len(job_descriptions) else None

                # Score with both algorithms
                if job_desc:
                    old_result = old_scorer(resume_data, job_desc)
                    new_result = new_scorer(resume_data, job_desc)
                else:
                    old_result = old_scorer(resume_data)
                    new_result = new_scorer(resume_data)

                # Extract numeric scores
                old_score = self._extract_score(old_result)
                new_score = self._extract_score(new_result)

                old_scores.append(old_score)
                new_scores.append(new_score)
                delta = new_score - old_score
                deltas.append(delta)

                detailed_results.append({
                    'resume_id': resume_data.get('id', f'resume_{idx}'),
                    'old_score': old_score,
                    'new_score': new_score,
                    'delta': delta,
                    'improvement_pct': (delta / old_score * 100) if old_score > 0 else 0
                })

            except Exception as e:
                logger.error(f"Error scoring resume {idx}: {e}")
                continue

        # Statistical Analysis
        stats_analysis = self._calculate_statistics(old_scores, new_scores, deltas, alpha)

        # Distribution Analysis
        distribution_analysis = self._analyze_distributions(old_scores, new_scores)

        # Recommendation
        recommendation = self._generate_recommendation(stats_analysis, distribution_analysis)

        # Compile full report
        report = {
            'timestamp': datetime.now().isoformat(),
            'sample_size': len(test_resumes),
            'successful_comparisons': len(old_scores),
            'summary': {
                'old_mean': np.mean(old_scores),
                'new_mean': np.mean(new_scores),
                'average_delta': np.mean(deltas),
                'median_delta': np.median(deltas),
                'std_delta': np.std(deltas),
            },
            'statistics': stats_analysis,
            'distribution': distribution_analysis,
            'detailed_results': detailed_results,
            'recommendation': recommendation
        }

        # Save report
        self._save_report(report)

        return report

    def _extract_score(self, result: Any) -> float:
        """Extract numeric score from various result formats"""
        if isinstance(result, (int, float)):
            return float(result)
        elif isinstance(result, dict):
            # Try common score keys
            for key in ['overall_score', 'score', 'total_score', 'final_score']:
                if key in result:
                    return float(result[key])
            # Try to find any numeric value
            for value in result.values():
                if isinstance(value, (int, float)):
                    return float(value)
        raise ValueError(f"Cannot extract score from result: {type(result)}")

    def _calculate_statistics(
        self,
        old_scores: List[float],
        new_scores: List[float],
        deltas: List[float],
        alpha: float
    ) -> Dict[str, Any]:
        """Perform statistical significance tests"""

        # Paired t-test (most appropriate for A/B testing)
        t_statistic, p_value = stats.ttest_rel(new_scores, old_scores)

        # Effect size (Cohen's d)
        cohens_d = (np.mean(new_scores) - np.mean(old_scores)) / np.std(deltas)

        # Confidence interval for mean difference
        n = len(deltas)
        se = stats.sem(deltas)
        ci_95 = stats.t.interval(1 - alpha, n - 1, loc=np.mean(deltas), scale=se)

        # Wilcoxon signed-rank test (non-parametric alternative)
        wilcoxon_stat, wilcoxon_p = stats.wilcoxon(new_scores, old_scores)

        # Determine statistical significance
        is_significant = p_value < alpha

        return {
            't_statistic': float(t_statistic),
            'p_value': float(p_value),
            'is_significant': is_significant,
            'significance_level': alpha,
            'cohens_d': float(cohens_d),
            'effect_size': self._interpret_cohens_d(cohens_d),
            'confidence_interval_95': [float(ci_95[0]), float(ci_95[1])],
            'wilcoxon_statistic': float(wilcoxon_stat),
            'wilcoxon_p_value': float(wilcoxon_p),
        }

    def _interpret_cohens_d(self, d: float) -> str:
        """Interpret Cohen's d effect size"""
        abs_d = abs(d)
        if abs_d < 0.2:
            return "negligible"
        elif abs_d < 0.5:
            return "small"
        elif abs_d < 0.8:
            return "medium"
        else:
            return "large"

    def _analyze_distributions(
        self,
        old_scores: List[float],
        new_scores: List[float]
    ) -> Dict[str, Any]:
        """Analyze score distributions"""

        return {
            'old_distribution': {
                'mean': float(np.mean(old_scores)),
                'median': float(np.median(old_scores)),
                'std': float(np.std(old_scores)),
                'min': float(np.min(old_scores)),
                'max': float(np.max(old_scores)),
                'q25': float(np.percentile(old_scores, 25)),
                'q75': float(np.percentile(old_scores, 75)),
            },
            'new_distribution': {
                'mean': float(np.mean(new_scores)),
                'median': float(np.median(new_scores)),
                'std': float(np.std(new_scores)),
                'min': float(np.min(new_scores)),
                'max': float(np.max(new_scores)),
                'q25': float(np.percentile(new_scores, 25)),
                'q75': float(np.percentile(new_scores, 75)),
            },
            'improvement_rate': float(np.mean([1 if n > o else 0 for n, o in zip(new_scores, old_scores)]) * 100),
            'regression_rate': float(np.mean([1 if n < o else 0 for n, o in zip(new_scores, old_scores)]) * 100),
        }

    def _generate_recommendation(
        self,
        stats: Dict[str, Any],
        distribution: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate deployment recommendation based on test results"""

        # Decision criteria
        is_significant = stats['is_significant']
        mean_improvement = distribution['new_distribution']['mean'] - distribution['old_distribution']['mean']
        improvement_rate = distribution['improvement_rate']
        effect_size = stats['effect_size']

        # Decision logic
        if not is_significant:
            decision = "DO NOT DEPLOY"
            reason = f"Changes are not statistically significant (p={stats['p_value']:.4f})"
            confidence = "low"
        elif mean_improvement < 0:
            decision = "ROLLBACK"
            reason = f"New scorer performs worse on average (delta={mean_improvement:.2f})"
            confidence = "high"
        elif mean_improvement < 3:
            decision = "CAUTION"
            reason = f"Improvement is minimal ({mean_improvement:.2f} points). Consider more testing."
            confidence = "medium"
        elif effect_size in ["small", "negligible"]:
            decision = "CAUTION"
            reason = f"Effect size is {effect_size}. Changes may not be meaningful in practice."
            confidence = "medium"
        elif improvement_rate < 60:
            decision = "CAUTION"
            reason = f"Only {improvement_rate:.1f}% of resumes improved. Consider edge cases."
            confidence = "medium"
        else:
            decision = "DEPLOY"
            reason = (
                f"Statistically significant improvement "
                f"(p={stats['p_value']:.4f}, d={stats['cohens_d']:.2f}). "
                f"{improvement_rate:.1f}% of resumes improved."
            )
            confidence = "high"

        return {
            'decision': decision,
            'reason': reason,
            'confidence': confidence,
            'mean_improvement': float(mean_improvement),
            'improvement_rate': float(improvement_rate),
            'metrics': {
                'p_value': stats['p_value'],
                'cohens_d': stats['cohens_d'],
                'effect_size': effect_size,
            }
        }

    def _save_report(self, report: Dict[str, Any]) -> Path:
        """Save test report to disk"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ab_test_report_{timestamp}.json"
        filepath = self.results_dir / filename

        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)

        logger.info(f"Report saved to {filepath}")
        return filepath

    def compare_metrics(
        self,
        old_metrics: List[Dict[str, float]],
        new_metrics: List[Dict[str, float]],
        metric_names: List[str] = None
    ) -> Dict[str, Dict[str, Any]]:
        """
        Compare multiple metrics between old and new scorers

        Args:
            old_metrics: List of metric dictionaries from old scorer
            new_metrics: List of metric dictionaries from new scorer
            metric_names: Optional list of specific metrics to compare

        Returns:
            Dictionary with comparison for each metric
        """
        if metric_names is None:
            # Get all common metric names
            metric_names = list(set(old_metrics[0].keys()) & set(new_metrics[0].keys()))

        comparisons = {}

        for metric_name in metric_names:
            old_values = [m[metric_name] for m in old_metrics if metric_name in m]
            new_values = [m[metric_name] for m in new_metrics if metric_name in m]

            if not old_values or not new_values:
                continue

            # Statistical test
            t_stat, p_value = stats.ttest_rel(new_values, old_values)
            mean_delta = np.mean(new_values) - np.mean(old_values)

            comparisons[metric_name] = {
                'old_mean': float(np.mean(old_values)),
                'new_mean': float(np.mean(new_values)),
                'delta': float(mean_delta),
                'pct_change': float((mean_delta / np.mean(old_values)) * 100) if np.mean(old_values) != 0 else 0,
                'p_value': float(p_value),
                'is_significant': p_value < 0.05,
                't_statistic': float(t_stat)
            }

        return comparisons

    def run_power_analysis(
        self,
        old_scores: List[float],
        new_scores: List[float],
        desired_power: float = 0.8,
        alpha: float = 0.05
    ) -> Dict[str, Any]:
        """
        Perform post-hoc power analysis

        Args:
            old_scores: Scores from old algorithm
            new_scores: Scores from new algorithm
            desired_power: Desired statistical power (default 0.8)
            alpha: Significance level

        Returns:
            Power analysis results
        """
        from scipy.stats import norm

        # Calculate effect size
        deltas = [n - o for n, o in zip(new_scores, old_scores)]
        cohens_d = np.mean(deltas) / np.std(deltas)

        # Calculate achieved power
        n = len(old_scores)
        ncp = cohens_d * np.sqrt(n)  # Non-centrality parameter

        # Critical value for two-tailed test
        t_crit = stats.t.ppf(1 - alpha / 2, n - 1)

        # Calculate power (simplified approximation)
        power = 1 - stats.nct.cdf(t_crit, n - 1, ncp) + stats.nct.cdf(-t_crit, n - 1, ncp)

        # Estimate required sample size for desired power
        if cohens_d != 0:
            # Simplified formula for required n
            z_alpha = norm.ppf(1 - alpha / 2)
            z_beta = norm.ppf(desired_power)
            required_n = int(np.ceil(2 * ((z_alpha + z_beta) / cohens_d) ** 2))
        else:
            required_n = float('inf')

        return {
            'current_sample_size': n,
            'achieved_power': float(power),
            'desired_power': desired_power,
            'is_adequately_powered': power >= desired_power,
            'cohens_d': float(cohens_d),
            'required_sample_size_for_desired_power': required_n,
            'recommendation': (
                f"Sample size of {n} achieves {power:.2f} power. "
                f"{'Adequate' if power >= desired_power else f'Need {required_n} samples for {desired_power} power'}."
            )
        }


class TestResumeCorpus:
    """Manages benchmark resume test corpus"""

    def __init__(self, corpus_dir: str = "/Users/sabuj.mondal/ats-resume-scorer/backend/data/test_resumes"):
        self.corpus_dir = Path(corpus_dir)
        self.corpus_dir.mkdir(parents=True, exist_ok=True)

    def load_corpus(self) -> List[Dict[str, Any]]:
        """Load all test resumes from corpus"""
        resumes = []

        for file_path in self.corpus_dir.glob("*.json"):
            try:
                with open(file_path, 'r') as f:
                    resume_data = json.load(f)
                    resumes.append(resume_data)
            except Exception as e:
                logger.error(f"Error loading {file_path}: {e}")

        logger.info(f"Loaded {len(resumes)} test resumes from corpus")
        return resumes

    def add_resume(self, resume_data: Dict[str, Any], filename: str = None) -> Path:
        """Add a resume to the test corpus"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"test_resume_{timestamp}.json"

        filepath = self.corpus_dir / filename

        with open(filepath, 'w') as f:
            json.dump(resume_data, f, indent=2)

        logger.info(f"Added resume to corpus: {filepath}")
        return filepath

    def get_corpus_stats(self) -> Dict[str, Any]:
        """Get statistics about the test corpus"""
        resumes = self.load_corpus()

        if not resumes:
            return {'count': 0, 'note': 'No resumes in corpus'}

        # Analyze corpus diversity
        roles = [r.get('role', 'Unknown') for r in resumes]
        experience_levels = [r.get('experience_level', 'Unknown') for r in resumes]
        industries = [r.get('industry', 'Unknown') for r in resumes]

        return {
            'total_resumes': len(resumes),
            'unique_roles': len(set(roles)),
            'unique_experience_levels': len(set(experience_levels)),
            'unique_industries': len(set(industries)),
            'roles_distribution': {role: roles.count(role) for role in set(roles)},
            'experience_distribution': {level: experience_levels.count(level) for level in set(experience_levels)},
            'industry_distribution': {ind: industries.count(ind) for ind in set(industries)},
        }


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)

    # Initialize framework
    ab_test = ABTestFramework()

    print("A/B Testing Framework initialized successfully")
    print(f"Results will be saved to: {ab_test.results_dir}")
