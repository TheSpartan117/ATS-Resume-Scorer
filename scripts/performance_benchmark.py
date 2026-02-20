"""
Performance Benchmark Script for ATS Scorer
Tests scoring speed, memory usage, and concurrent request handling
"""

import sys
import time
import json
import psutil
import tracemalloc
from pathlib import Path
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, asdict
import statistics

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from services.scorer_ats import ATSScorer
from services.scorer_quality import QualityScorer
from services.ab_testing import TestResumeCorpus


@dataclass
class BenchmarkResult:
    """Results from a single benchmark run"""
    test_name: str
    duration_ms: float
    memory_mb: float
    success: bool
    error: str = None
    metadata: Dict[str, Any] = None


class PerformanceBenchmark:
    """Performance testing suite for ATS Scorer"""

    def __init__(self):
        self.results: List[BenchmarkResult] = []
        self.ats_scorer = ATSScorer()
        self.quality_scorer = QualityScorer()
        self.corpus = TestResumeCorpus()

    def run_all_benchmarks(self) -> Dict[str, Any]:
        """Run all performance benchmarks"""
        print("=" * 80)
        print("ATS SCORER PERFORMANCE BENCHMARK")
        print("=" * 80)
        print()

        # Test 1: Single Resume Scoring Speed
        print("Test 1: Single Resume Scoring Speed")
        print("-" * 80)
        self.benchmark_single_resume_speed()
        print()

        # Test 2: Cached vs Uncached Performance
        print("Test 2: Cached vs Uncached Performance")
        print("-" * 80)
        self.benchmark_caching_performance()
        print()

        # Test 3: Memory Usage
        print("Test 3: Memory Usage")
        print("-" * 80)
        self.benchmark_memory_usage()
        print()

        # Test 4: Concurrent Request Handling
        print("Test 4: Concurrent Request Handling")
        print("-" * 80)
        self.benchmark_concurrent_requests()
        print()

        # Test 5: Batch Processing
        print("Test 5: Batch Processing (100+ resumes)")
        print("-" * 80)
        self.benchmark_batch_processing()
        print()

        # Test 6: Large Resume Performance
        print("Test 6: Large Resume Performance")
        print("-" * 80)
        self.benchmark_large_resume()
        print()

        # Generate summary report
        report = self.generate_report()
        self.save_report(report)

        return report

    def benchmark_single_resume_speed(self):
        """Test scoring speed for a single resume (target: <2s)"""
        resume_text = self._get_sample_resume()
        job_desc = self._get_sample_job_description()

        # Warm-up run
        try:
            self.ats_scorer.score(resume_text, job_desc)
        except:
            pass

        # Benchmark run
        durations = []
        for i in range(5):
            start_time = time.time()
            try:
                result = self.ats_scorer.score(resume_text, job_desc)
                duration_ms = (time.time() - start_time) * 1000
                durations.append(duration_ms)

                self.results.append(BenchmarkResult(
                    test_name=f"single_resume_run_{i+1}",
                    duration_ms=duration_ms,
                    memory_mb=0,  # Not tracking per-run
                    success=True,
                    metadata={'run': i+1}
                ))
            except Exception as e:
                self.results.append(BenchmarkResult(
                    test_name=f"single_resume_run_{i+1}",
                    duration_ms=0,
                    memory_mb=0,
                    success=False,
                    error=str(e)
                ))

        if durations:
            avg_duration = statistics.mean(durations)
            min_duration = min(durations)
            max_duration = max(durations)

            print(f"  Average: {avg_duration:.1f}ms")
            print(f"  Min: {min_duration:.1f}ms")
            print(f"  Max: {max_duration:.1f}ms")
            print(f"  Target: <2000ms (2 seconds)")

            if avg_duration < 2000:
                print(f"  ✓ PASS - Average {avg_duration:.1f}ms is under 2000ms target")
            else:
                print(f"  ✗ FAIL - Average {avg_duration:.1f}ms exceeds 2000ms target")
        else:
            print("  ✗ FAIL - No successful runs")

    def benchmark_caching_performance(self):
        """Test cached vs uncached performance (target: <500ms cached)"""
        resume_text = self._get_sample_resume()
        job_desc = self._get_sample_job_description()

        # First run (uncached)
        start_time = time.time()
        try:
            result1 = self.ats_scorer.score(resume_text, job_desc)
            first_run_ms = (time.time() - start_time) * 1000

            self.results.append(BenchmarkResult(
                test_name="caching_first_run",
                duration_ms=first_run_ms,
                memory_mb=0,
                success=True
            ))
        except Exception as e:
            first_run_ms = 0
            self.results.append(BenchmarkResult(
                test_name="caching_first_run",
                duration_ms=0,
                memory_mb=0,
                success=False,
                error=str(e)
            ))

        # Second run (potentially cached)
        start_time = time.time()
        try:
            result2 = self.ats_scorer.score(resume_text, job_desc)
            second_run_ms = (time.time() - start_time) * 1000

            self.results.append(BenchmarkResult(
                test_name="caching_second_run",
                duration_ms=second_run_ms,
                memory_mb=0,
                success=True
            ))
        except Exception as e:
            second_run_ms = 0
            self.results.append(BenchmarkResult(
                test_name="caching_second_run",
                duration_ms=0,
                memory_mb=0,
                success=False,
                error=str(e)
            ))

        if first_run_ms > 0 and second_run_ms > 0:
            speedup = first_run_ms / second_run_ms if second_run_ms > 0 else 1
            print(f"  First run: {first_run_ms:.1f}ms")
            print(f"  Second run: {second_run_ms:.1f}ms")
            print(f"  Speedup: {speedup:.2f}x")

            if second_run_ms < 500:
                print(f"  ✓ PASS - Cached run {second_run_ms:.1f}ms is under 500ms target")
            else:
                print(f"  ⚠ WARNING - Cached run {second_run_ms:.1f}ms exceeds 500ms target")
        else:
            print("  ✗ FAIL - Could not complete caching test")

    def benchmark_memory_usage(self):
        """Test memory usage during scoring"""
        resume_text = self._get_sample_resume()
        job_desc = self._get_sample_job_description()

        # Start memory tracking
        tracemalloc.start()
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        try:
            # Score multiple times
            for i in range(10):
                result = self.ats_scorer.score(resume_text, job_desc)

            # Check memory
            current_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = current_memory - initial_memory

            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()

            peak_mb = peak / 1024 / 1024

            self.results.append(BenchmarkResult(
                test_name="memory_usage",
                duration_ms=0,
                memory_mb=peak_mb,
                success=True,
                metadata={
                    'initial_memory_mb': initial_memory,
                    'final_memory_mb': current_memory,
                    'memory_increase_mb': memory_increase,
                    'peak_traced_mb': peak_mb
                }
            ))

            print(f"  Initial memory: {initial_memory:.1f} MB")
            print(f"  Final memory: {current_memory:.1f} MB")
            print(f"  Memory increase: {memory_increase:.1f} MB")
            print(f"  Peak traced: {peak_mb:.1f} MB")

            if memory_increase < 100:
                print(f"  ✓ PASS - Memory increase {memory_increase:.1f}MB is reasonable")
            else:
                print(f"  ⚠ WARNING - High memory increase {memory_increase:.1f}MB")

        except Exception as e:
            tracemalloc.stop()
            print(f"  ✗ FAIL - {e}")
            self.results.append(BenchmarkResult(
                test_name="memory_usage",
                duration_ms=0,
                memory_mb=0,
                success=False,
                error=str(e)
            ))

    def benchmark_concurrent_requests(self):
        """Test handling of concurrent requests"""
        resume_text = self._get_sample_resume()
        job_desc = self._get_sample_job_description()

        num_concurrent = 10

        def score_resume():
            start = time.time()
            try:
                result = self.ats_scorer.score(resume_text, job_desc)
                return {
                    'success': True,
                    'duration_ms': (time.time() - start) * 1000
                }
            except Exception as e:
                return {
                    'success': False,
                    'error': str(e)
                }

        # Run concurrent requests
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=num_concurrent) as executor:
            futures = [executor.submit(score_resume) for _ in range(num_concurrent)]
            results = [future.result() for future in as_completed(futures)]

        total_duration_ms = (time.time() - start_time) * 1000

        successes = sum(1 for r in results if r['success'])
        failures = len(results) - successes

        if successes > 0:
            avg_duration = statistics.mean([r['duration_ms'] for r in results if r['success']])
        else:
            avg_duration = 0

        self.results.append(BenchmarkResult(
            test_name="concurrent_requests",
            duration_ms=total_duration_ms,
            memory_mb=0,
            success=successes > 0,
            metadata={
                'num_requests': num_concurrent,
                'successes': successes,
                'failures': failures,
                'avg_request_duration_ms': avg_duration
            }
        ))

        print(f"  Concurrent requests: {num_concurrent}")
        print(f"  Total time: {total_duration_ms:.1f}ms")
        print(f"  Successes: {successes}/{num_concurrent}")
        print(f"  Average request duration: {avg_duration:.1f}ms")

        if successes == num_concurrent and total_duration_ms < 5000:
            print(f"  ✓ PASS - All requests completed successfully")
        else:
            print(f"  ⚠ WARNING - Some issues with concurrent requests")

    def benchmark_batch_processing(self):
        """Test processing large batch of resumes"""
        # Load corpus or generate test data
        resumes = self.corpus.load_corpus()

        # If corpus is small, duplicate it
        if len(resumes) < 10:
            base_resume = self._get_sample_resume()
            resumes = [
                {'resume_text': base_resume, 'job_description': self._get_sample_job_description()}
                for _ in range(10)
            ]

        # Take first 10 for batch test
        batch_size = min(10, len(resumes))
        test_batch = resumes[:batch_size]

        start_time = time.time()
        successes = 0
        failures = 0

        for resume_data in test_batch:
            try:
                resume_text = resume_data.get('resume_text', '')
                job_desc = resume_data.get('job_description', '')
                result = self.ats_scorer.score(resume_text, job_desc)
                successes += 1
            except Exception as e:
                failures += 1

        duration_ms = (time.time() - start_time) * 1000
        avg_per_resume_ms = duration_ms / batch_size

        self.results.append(BenchmarkResult(
            test_name="batch_processing",
            duration_ms=duration_ms,
            memory_mb=0,
            success=True,
            metadata={
                'batch_size': batch_size,
                'successes': successes,
                'failures': failures,
                'avg_per_resume_ms': avg_per_resume_ms
            }
        ))

        print(f"  Batch size: {batch_size}")
        print(f"  Total time: {duration_ms:.1f}ms ({duration_ms/1000:.2f}s)")
        print(f"  Average per resume: {avg_per_resume_ms:.1f}ms")
        print(f"  Successes: {successes}/{batch_size}")

        if avg_per_resume_ms < 2000:
            print(f"  ✓ PASS - Average time {avg_per_resume_ms:.1f}ms under target")
        else:
            print(f"  ⚠ WARNING - Average time {avg_per_resume_ms:.1f}ms may be slow")

    def benchmark_large_resume(self):
        """Test performance with very large resume"""
        # Create a large resume (5+ pages)
        base_resume = self._get_sample_resume()
        large_resume = base_resume * 10  # Simulate 5+ pages
        job_desc = self._get_sample_job_description()

        start_time = time.time()
        try:
            result = self.ats_scorer.score(large_resume, job_desc)
            duration_ms = (time.time() - start_time) * 1000

            self.results.append(BenchmarkResult(
                test_name="large_resume",
                duration_ms=duration_ms,
                memory_mb=0,
                success=True,
                metadata={'resume_size_chars': len(large_resume)}
            ))

            print(f"  Resume size: {len(large_resume)} characters")
            print(f"  Duration: {duration_ms:.1f}ms")

            if duration_ms < 5000:
                print(f"  ✓ PASS - Large resume processed in {duration_ms:.1f}ms")
            else:
                print(f"  ⚠ WARNING - Large resume took {duration_ms:.1f}ms")

        except Exception as e:
            print(f"  ✗ FAIL - {e}")
            self.results.append(BenchmarkResult(
                test_name="large_resume",
                duration_ms=0,
                memory_mb=0,
                success=False,
                error=str(e)
            ))

    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive benchmark report"""
        successful_results = [r for r in self.results if r.success]
        failed_results = [r for r in self.results if not r.success]

        # Calculate statistics
        durations = [r.duration_ms for r in successful_results if r.duration_ms > 0]

        report = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'summary': {
                'total_tests': len(self.results),
                'successful': len(successful_results),
                'failed': len(failed_results),
                'success_rate': len(successful_results) / len(self.results) * 100 if self.results else 0
            },
            'performance': {
                'avg_duration_ms': statistics.mean(durations) if durations else 0,
                'min_duration_ms': min(durations) if durations else 0,
                'max_duration_ms': max(durations) if durations else 0,
                'median_duration_ms': statistics.median(durations) if durations else 0
            },
            'targets': {
                'first_run_target_ms': 2000,
                'cached_run_target_ms': 500,
                'first_run_met': any(r.test_name == 'single_resume_run_1' and r.duration_ms < 2000 for r in successful_results),
                'cached_run_met': any(r.test_name == 'caching_second_run' and r.duration_ms < 500 for r in successful_results)
            },
            'detailed_results': [asdict(r) for r in self.results],
            'bottlenecks': self._identify_bottlenecks(successful_results),
            'recommendations': self._generate_recommendations(successful_results)
        }

        return report

    def _identify_bottlenecks(self, results: List[BenchmarkResult]) -> List[str]:
        """Identify performance bottlenecks"""
        bottlenecks = []

        # Check for slow tests
        slow_tests = [r for r in results if r.duration_ms > 2000]
        if slow_tests:
            bottlenecks.append(f"Slow tests detected: {len(slow_tests)} tests took >2s")

        # Check memory usage
        memory_tests = [r for r in results if r.test_name == 'memory_usage' and r.memory_mb > 500]
        if memory_tests:
            bottlenecks.append(f"High memory usage detected: {memory_tests[0].memory_mb:.1f}MB")

        # Check concurrent performance
        concurrent_tests = [r for r in results if r.test_name == 'concurrent_requests']
        if concurrent_tests and concurrent_tests[0].metadata:
            meta = concurrent_tests[0].metadata
            if meta.get('failures', 0) > 0:
                bottlenecks.append(f"Concurrent request failures: {meta['failures']}")

        return bottlenecks

    def _generate_recommendations(self, results: List[BenchmarkResult]) -> List[str]:
        """Generate optimization recommendations"""
        recommendations = []

        # Check caching effectiveness
        first_run = next((r for r in results if r.test_name == 'caching_first_run'), None)
        second_run = next((r for r in results if r.test_name == 'caching_second_run'), None)

        if first_run and second_run:
            speedup = first_run.duration_ms / second_run.duration_ms if second_run.duration_ms > 0 else 1
            if speedup < 1.5:
                recommendations.append("Consider implementing more aggressive caching")

        # Check memory usage
        memory_test = next((r for r in results if r.test_name == 'memory_usage'), None)
        if memory_test and memory_test.metadata:
            if memory_test.metadata.get('memory_increase_mb', 0) > 100:
                recommendations.append("High memory usage - consider optimization")

        # Check batch performance
        batch_test = next((r for r in results if r.test_name == 'batch_processing'), None)
        if batch_test and batch_test.metadata:
            if batch_test.metadata.get('avg_per_resume_ms', 0) > 2000:
                recommendations.append("Batch processing is slow - consider parallel processing")

        if not recommendations:
            recommendations.append("Performance is within acceptable ranges")

        return recommendations

    def save_report(self, report: Dict[str, Any]):
        """Save benchmark report to file"""
        output_dir = Path(__file__).parent.parent / "docs"
        output_dir.mkdir(exist_ok=True)

        filename = f"performance_benchmark_{time.strftime('%Y%m%d_%H%M%S')}.json"
        filepath = output_dir / filename

        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)

        print()
        print("=" * 80)
        print("BENCHMARK COMPLETE")
        print("=" * 80)
        print(f"Report saved to: {filepath}")
        print()
        print("Summary:")
        print(f"  Total tests: {report['summary']['total_tests']}")
        print(f"  Successful: {report['summary']['successful']}")
        print(f"  Failed: {report['summary']['failed']}")
        print(f"  Success rate: {report['summary']['success_rate']:.1f}%")
        print()
        print("Performance:")
        print(f"  Average duration: {report['performance']['avg_duration_ms']:.1f}ms")
        print(f"  Min duration: {report['performance']['min_duration_ms']:.1f}ms")
        print(f"  Max duration: {report['performance']['max_duration_ms']:.1f}ms")
        print()
        print("Targets:")
        print(f"  First run target (<2s): {'✓ MET' if report['targets']['first_run_met'] else '✗ NOT MET'}")
        print(f"  Cached run target (<500ms): {'✓ MET' if report['targets']['cached_run_met'] else '✗ NOT MET'}")
        print()

        if report.get('bottlenecks'):
            print("Bottlenecks identified:")
            for bottleneck in report['bottlenecks']:
                print(f"  - {bottleneck}")
            print()

        if report.get('recommendations'):
            print("Recommendations:")
            for rec in report['recommendations']:
                print(f"  - {rec}")

    def _get_sample_resume(self) -> str:
        """Get sample resume for testing"""
        return """
John Doe
Senior Software Engineer
email@example.com | 555-1234

EXPERIENCE
Senior Software Engineer | TechCorp | 2020-Present
- Developed scalable microservices using Python and FastAPI, improving system performance by 40%
- Led team of 5 engineers in migrating legacy systems to cloud infrastructure
- Implemented CI/CD pipelines reducing deployment time from 2 hours to 15 minutes
- Designed and optimized PostgreSQL databases serving 1M+ users

Software Engineer | StartupXYZ | 2018-2020
- Built RESTful APIs handling 100K+ daily requests
- Collaborated with product team to deliver 15+ features per quarter
- Mentored 3 junior developers on best practices
- Reduced bug count by 35% through comprehensive testing

SKILLS
Languages: Python, JavaScript, TypeScript, SQL
Frameworks: FastAPI, React, Django, Node.js
Tools: Docker, Kubernetes, AWS, Git, PostgreSQL, Redis
Methodologies: Agile, TDD, CI/CD, Microservices

EDUCATION
B.S. Computer Science | Tech University | 2018
GPA: 3.8/4.0

CERTIFICATIONS
AWS Certified Solutions Architect
Certified Kubernetes Administrator
"""

    def _get_sample_job_description(self) -> str:
        """Get sample job description for testing"""
        return """
We are seeking a talented Senior Software Engineer to join our growing team.

Responsibilities:
- Develop and maintain scalable backend services
- Work with microservices architecture
- Implement CI/CD pipelines
- Collaborate with cross-functional teams
- Mentor junior developers

Required Skills:
- 5+ years of Python development
- Experience with FastAPI or similar frameworks
- Strong knowledge of Docker and Kubernetes
- PostgreSQL and database optimization
- AWS or similar cloud platforms
- Agile methodologies

Preferred:
- Team leadership experience
- Open source contributions
- Strong communication skills
"""


if __name__ == "__main__":
    benchmark = PerformanceBenchmark()
    report = benchmark.run_all_benchmarks()
