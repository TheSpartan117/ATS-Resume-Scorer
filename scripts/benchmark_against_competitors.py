"""
Benchmark ATS Scorer against Competitors
Compare scores with Resume Worded and other ATS tools
Calculate correlation and identify systematic biases
"""

import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass, asdict
import statistics

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from services.scorer_ats import ATSScorer
from services.ab_testing import TestResumeCorpus


@dataclass
class CompetitorScore:
    """Score from a competitor tool"""
    tool_name: str
    overall_score: float
    keyword_score: float = None
    format_score: float = None
    notes: str = ""


@dataclass
class ComparisonResult:
    """Comparison between our tool and competitors"""
    resume_id: str
    our_score: float
    competitor_scores: Dict[str, float]
    delta: Dict[str, float]  # Difference from competitors
    metadata: Dict[str, Any] = None


class CompetitorBenchmark:
    """Benchmark against competitor ATS tools"""

    def __init__(self):
        self.our_scorer = ATSScorer()
        self.corpus = TestResumeCorpus()
        self.results: List[ComparisonResult] = []

    def run_benchmark(self, competitor_data: Dict[str, List[CompetitorScore]]) -> Dict[str, Any]:
        """
        Run benchmark against competitor scores

        Args:
            competitor_data: Dictionary mapping resume_id to list of CompetitorScore objects

        Returns:
            Comprehensive comparison report
        """
        print("=" * 80)
        print("COMPETITOR BENCHMARK - ATS SCORER")
        print("=" * 80)
        print()

        # Load test resumes
        resumes = self.corpus.load_corpus()

        if not resumes:
            print("⚠ Warning: No resumes in corpus. Creating sample data...")
            resumes = self._create_sample_resumes()

        print(f"Loaded {len(resumes)} test resumes")
        print()

        # Score with our tool
        print("Scoring resumes with our ATS Scorer...")
        our_scores = {}
        for resume_data in resumes:
            resume_id = resume_data.get('id', 'unknown')
            resume_text = resume_data.get('resume_text', '')
            job_desc = resume_data.get('job_description', '')

            try:
                result = self.our_scorer.score(resume_text, job_desc)
                score = self._extract_score(result)
                our_scores[resume_id] = score
                print(f"  {resume_id}: {score:.1f}")
            except Exception as e:
                print(f"  {resume_id}: ERROR - {e}")
                our_scores[resume_id] = 0

        print()

        # Compare with competitor data
        print("Comparing with competitor scores...")
        print()

        for resume_id, our_score in our_scores.items():
            if resume_id in competitor_data:
                competitor_scores = {}
                deltas = {}

                for comp_score in competitor_data[resume_id]:
                    competitor_scores[comp_score.tool_name] = comp_score.overall_score
                    deltas[comp_score.tool_name] = our_score - comp_score.overall_score

                self.results.append(ComparisonResult(
                    resume_id=resume_id,
                    our_score=our_score,
                    competitor_scores=competitor_scores,
                    delta=deltas
                ))

        # Generate analysis
        report = self._generate_report()
        self._save_report(report)

        return report

    def _extract_score(self, result: Any) -> float:
        """Extract score from result"""
        if isinstance(result, (int, float)):
            return float(result)
        elif isinstance(result, dict):
            for key in ['overall_score', 'score', 'total_score']:
                if key in result:
                    return float(result[key])
        return 0.0

    def _generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive comparison report"""
        if not self.results:
            return {
                'error': 'No comparison results available',
                'note': 'Need competitor data to run comparison'
            }

        # Get all competitor tools
        competitor_tools = set()
        for result in self.results:
            competitor_tools.update(result.competitor_scores.keys())

        # Calculate statistics for each competitor
        competitor_stats = {}
        for tool in competitor_tools:
            our_scores = []
            their_scores = []
            deltas = []

            for result in self.results:
                if tool in result.competitor_scores:
                    our_scores.append(result.our_score)
                    their_scores.append(result.competitor_scores[tool])
                    deltas.append(result.delta[tool])

            if len(our_scores) >= 2:
                correlation = self._calculate_correlation(our_scores, their_scores)

                competitor_stats[tool] = {
                    'num_comparisons': len(our_scores),
                    'our_mean': statistics.mean(our_scores),
                    'their_mean': statistics.mean(their_scores),
                    'mean_delta': statistics.mean(deltas),
                    'std_delta': statistics.stdev(deltas) if len(deltas) > 1 else 0,
                    'correlation': correlation,
                    'max_delta': max(deltas),
                    'min_delta': min(deltas),
                    'deltas': deltas
                }

        # Overall assessment
        assessment = self._assess_performance(competitor_stats)

        report = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'total_comparisons': len(self.results),
            'competitors_tested': list(competitor_tools),
            'competitor_statistics': competitor_stats,
            'assessment': assessment,
            'detailed_results': [asdict(r) for r in self.results],
            'recommendations': self._generate_recommendations(competitor_stats)
        }

        return report

    def _calculate_correlation(self, x: List[float], y: List[float]) -> float:
        """Calculate Pearson correlation coefficient"""
        if len(x) != len(y) or len(x) < 2:
            return 0.0

        n = len(x)
        mean_x = statistics.mean(x)
        mean_y = statistics.mean(y)

        # Calculate covariance and standard deviations
        cov = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(n)) / n
        std_x = statistics.stdev(x)
        std_y = statistics.stdev(y)

        if std_x == 0 or std_y == 0:
            return 0.0

        correlation = cov / (std_x * std_y)
        return correlation

    def _assess_performance(self, competitor_stats: Dict[str, Dict]) -> Dict[str, Any]:
        """Assess overall performance vs competitors"""
        assessment = {
            'overall_status': 'unknown',
            'strengths': [],
            'weaknesses': [],
            'notes': []
        }

        for tool, stats in competitor_stats.items():
            mean_delta = stats['mean_delta']
            correlation = stats['correlation']

            # Check correlation (target: r > 0.75)
            if correlation >= 0.75:
                assessment['strengths'].append(
                    f"Strong correlation with {tool} (r={correlation:.3f})"
                )
            elif correlation >= 0.5:
                assessment['notes'].append(
                    f"Moderate correlation with {tool} (r={correlation:.3f})"
                )
            else:
                assessment['weaknesses'].append(
                    f"Weak correlation with {tool} (r={correlation:.3f})"
                )

            # Check systematic bias
            if abs(mean_delta) <= 5:
                assessment['strengths'].append(
                    f"Well-calibrated vs {tool} (Δ={mean_delta:+.1f})"
                )
            elif mean_delta < -10:
                assessment['weaknesses'].append(
                    f"Scoring {abs(mean_delta):.1f} points lower than {tool}"
                )
            elif mean_delta > 10:
                assessment['notes'].append(
                    f"Scoring {mean_delta:.1f} points higher than {tool}"
                )

        # Overall status
        if len(assessment['weaknesses']) == 0:
            assessment['overall_status'] = 'EXCELLENT'
        elif len(assessment['weaknesses']) <= len(assessment['strengths']):
            assessment['overall_status'] = 'GOOD'
        else:
            assessment['overall_status'] = 'NEEDS IMPROVEMENT'

        return assessment

    def _generate_recommendations(self, competitor_stats: Dict[str, Dict]) -> List[str]:
        """Generate recommendations based on comparison"""
        recommendations = []

        for tool, stats in competitor_stats.items():
            mean_delta = stats['mean_delta']
            correlation = stats['correlation']

            # Correlation recommendations
            if correlation < 0.75:
                recommendations.append(
                    f"Improve correlation with {tool} (current: {correlation:.3f}, target: >0.75). "
                    "Consider adjusting scoring weights."
                )

            # Systematic bias recommendations
            if mean_delta < -15:
                recommendations.append(
                    f"Scores are {abs(mean_delta):.1f} points lower than {tool} on average. "
                    "Consider recalibrating thresholds to be less strict."
                )
            elif mean_delta > 15:
                recommendations.append(
                    f"Scores are {mean_delta:.1f} points higher than {tool} on average. "
                    "Consider tightening scoring criteria."
                )

            # Consistency recommendations
            if stats['std_delta'] > 15:
                recommendations.append(
                    f"High variance in differences vs {tool} (σ={stats['std_delta']:.1f}). "
                    "Consider improving consistency."
                )

        if not recommendations:
            recommendations.append(
                "Performance is well-aligned with competitors. No major adjustments needed."
            )

        return recommendations

    def _save_report(self, report: Dict[str, Any]):
        """Save report to file"""
        output_dir = Path(__file__).parent.parent / "docs"
        output_dir.mkdir(exist_ok=True)

        filename = f"competitor_benchmark_{time.strftime('%Y%m%d_%H%M%S')}.json"
        filepath = output_dir / filename

        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)

        # Print summary
        print()
        print("=" * 80)
        print("BENCHMARK COMPLETE")
        print("=" * 80)
        print(f"Report saved to: {filepath}")
        print()

        if 'error' in report:
            print(f"Error: {report['error']}")
            print(f"Note: {report.get('note', '')}")
            return

        print(f"Total comparisons: {report['total_comparisons']}")
        print(f"Competitors tested: {', '.join(report['competitors_tested'])}")
        print()

        print("Results by competitor:")
        print("-" * 80)
        for tool, stats in report['competitor_statistics'].items():
            print(f"\n{tool}:")
            print(f"  Comparisons: {stats['num_comparisons']}")
            print(f"  Our mean score: {stats['our_mean']:.1f}")
            print(f"  Their mean score: {stats['their_mean']:.1f}")
            print(f"  Mean difference: {stats['mean_delta']:+.1f}")
            print(f"  Correlation: {stats['correlation']:.3f} {'✓' if stats['correlation'] >= 0.75 else '✗'}")
            print(f"  Std deviation: {stats['std_delta']:.1f}")

        print()
        print(f"Overall Assessment: {report['assessment']['overall_status']}")
        print()

        if report['assessment']['strengths']:
            print("Strengths:")
            for strength in report['assessment']['strengths']:
                print(f"  ✓ {strength}")
            print()

        if report['assessment']['weaknesses']:
            print("Weaknesses:")
            for weakness in report['assessment']['weaknesses']:
                print(f"  ✗ {weakness}")
            print()

        if report['recommendations']:
            print("Recommendations:")
            for rec in report['recommendations']:
                print(f"  • {rec}")

    def _create_sample_resumes(self) -> List[Dict[str, Any]]:
        """Create sample resumes for testing"""
        return [
            {
                'id': 'sample_001',
                'resume_text': """
John Doe
Senior Software Engineer
- 5 years Python development
- Built scalable web applications
- Led team of developers
Skills: Python, FastAPI, Docker, AWS
""",
                'job_description': 'Python developer with cloud experience'
            }
        ]

    def load_competitor_data_from_file(self, filepath: str) -> Dict[str, List[CompetitorScore]]:
        """Load competitor scores from JSON file"""
        with open(filepath, 'r') as f:
            data = json.load(f)

        competitor_data = {}
        for resume_id, scores in data.items():
            competitor_data[resume_id] = [
                CompetitorScore(**score) if isinstance(score, dict) else score
                for score in scores
            ]

        return competitor_data


def create_sample_competitor_data() -> Dict[str, List[CompetitorScore]]:
    """
    Create sample competitor data for testing

    In real usage, you would manually test resumes on competitor sites
    and record their scores here
    """
    return {
        'test_resume_001': [
            CompetitorScore(
                tool_name='Resume Worded',
                overall_score=86,
                keyword_score=88,
                format_score=84,
                notes='Good keyword match, strong format'
            ),
            CompetitorScore(
                tool_name='Jobscan',
                overall_score=82,
                keyword_score=85,
                format_score=80,
                notes='Missing some keywords'
            )
        ],
        'test_resume_002': [
            CompetitorScore(
                tool_name='Resume Worded',
                overall_score=78,
                keyword_score=75,
                format_score=82,
                notes='Needs more quantification'
            ),
            CompetitorScore(
                tool_name='Jobscan',
                overall_score=75,
                keyword_score=73,
                format_score=78,
                notes='Format could be improved'
            )
        ],
        'test_resume_003': [
            CompetitorScore(
                tool_name='Resume Worded',
                overall_score=91,
                keyword_score=92,
                format_score=90,
                notes='Excellent resume'
            ),
            CompetitorScore(
                tool_name='Jobscan',
                overall_score=89,
                keyword_score=90,
                format_score=88,
                notes='Very strong candidate'
            )
        ]
    }


if __name__ == "__main__":
    print("""
Competitor Benchmark Tool
==========================

To use this tool effectively:

1. Manually test 10+ resumes on competitor tools (Resume Worded, Jobscan, etc.)
2. Record their scores in a JSON file with the format:
   {
     "resume_id": [
       {
         "tool_name": "Resume Worded",
         "overall_score": 86,
         "keyword_score": 88,
         "format_score": 84,
         "notes": "Good match"
       }
     ]
   }
3. Run this script with that data

For now, running with sample data...
""")

    benchmark = CompetitorBenchmark()

    # Use sample data
    competitor_data = create_sample_competitor_data()

    report = benchmark.run_benchmark(competitor_data)

    print()
    print("Note: This was run with sample data.")
    print("For real benchmarking, test actual resumes on competitor sites.")
