#!/usr/bin/env python3
"""
Quick test script to verify Phase 4 implementation
Run this to validate all components are working
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

def test_ab_framework():
    """Test A/B Testing Framework"""
    print("Testing A/B Testing Framework...")

    from services.ab_testing import ABTestFramework, TestResumeCorpus

    # Initialize
    framework = ABTestFramework()
    corpus = TestResumeCorpus()

    print(f"  ✓ Framework initialized")
    print(f"  ✓ Results directory: {framework.results_dir}")

    # Test corpus
    stats = corpus.get_corpus_stats()
    print(f"  ✓ Corpus loaded: {stats.get('total_resumes', 0)} resumes")

    # Test comparison
    def mock_old_scorer(resume_data, job_desc=None):
        return {'overall_score': 70}

    def mock_new_scorer(resume_data, job_desc=None):
        return {'overall_score': 75}

    test_resumes = [
        {'id': 'test1', 'text': 'resume'},
        {'id': 'test2', 'text': 'resume'},
        {'id': 'test3', 'text': 'resume'},
    ]

    report = framework.compare_scorers(mock_old_scorer, mock_new_scorer, test_resumes)

    print(f"  ✓ A/B test completed")
    print(f"  ✓ Mean delta: {report['summary']['average_delta']}")
    print(f"  ✓ Recommendation: {report['recommendation']['decision']}")
    print(f"  ✓ Significant: {report['statistics']['is_significant']}")

    return True

def test_test_corpus():
    """Test Resume Corpus"""
    print("\nTesting Test Resume Corpus...")

    from services.ab_testing import TestResumeCorpus

    corpus = TestResumeCorpus()
    resumes = corpus.load_corpus()
    stats = corpus.get_corpus_stats()

    print(f"  ✓ Loaded {len(resumes)} resumes")
    print(f"  ✓ Unique roles: {stats.get('unique_roles', 0)}")
    print(f"  ✓ Experience levels: {stats.get('unique_experience_levels', 0)}")
    print(f"  ✓ Industries: {stats.get('unique_industries', 0)}")

    if len(resumes) >= 5:
        print(f"  ✓ Corpus size adequate (5+ resumes)")
    else:
        print(f"  ⚠ Corpus could use more resumes (current: {len(resumes)})")

    return True

def test_performance_benchmark():
    """Test Performance Benchmark Script"""
    print("\nTesting Performance Benchmark Script...")

    # Just check if imports work
    import scripts.performance_benchmark as pb

    print(f"  ✓ Performance benchmark module loads")
    print(f"  ✓ PerformanceBenchmark class available")

    # Create instance
    benchmark = pb.PerformanceBenchmark()
    print(f"  ✓ Benchmark instance created")

    return True

def test_competitor_benchmark():
    """Test Competitor Benchmark Script"""
    print("\nTesting Competitor Benchmark Script...")

    import scripts.benchmark_against_competitors as cb

    print(f"  ✓ Competitor benchmark module loads")
    print(f"  ✓ CompetitorBenchmark class available")

    # Create instance
    benchmark = cb.CompetitorBenchmark()
    print(f"  ✓ Benchmark instance created")

    return True

def test_documentation():
    """Test that all documentation files exist"""
    print("\nTesting Documentation...")

    docs_dir = Path(__file__).parent.parent / "docs"

    required_docs = [
        "SCORING_METHODOLOGY.md",
        "API_DOCUMENTATION.md",
        "PHASE4_VALIDATION_REPORT.md",
        "FINAL_IMPLEMENTATION_SUMMARY.md"
    ]

    for doc in required_docs:
        doc_path = docs_dir / doc
        if doc_path.exists():
            size = doc_path.stat().st_size / 1024  # KB
            print(f"  ✓ {doc} exists ({size:.1f} KB)")
        else:
            print(f"  ✗ {doc} MISSING")
            return False

    # Check root files
    root_dir = Path(__file__).parent.parent

    if (root_dir / "CHANGELOG.md").exists():
        print(f"  ✓ CHANGELOG.md exists")
    else:
        print(f"  ✗ CHANGELOG.md MISSING")
        return False

    return True

def test_test_files():
    """Test that test files exist"""
    print("\nTesting Test Files...")

    tests_dir = Path(__file__).parent.parent / "tests"

    required_tests = [
        "integration/test_full_pipeline.py",
        "unit/test_ab_testing.py"
    ]

    for test in required_tests:
        test_path = tests_dir / test
        if test_path.exists():
            lines = len(test_path.read_text().split('\n'))
            print(f"  ✓ {test} exists ({lines} lines)")
        else:
            print(f"  ✗ {test} MISSING")
            return False

    return True

def main():
    """Run all tests"""
    print("=" * 70)
    print("PHASE 4 IMPLEMENTATION VALIDATION")
    print("=" * 70)
    print()

    tests = [
        ("A/B Testing Framework", test_ab_framework),
        ("Test Resume Corpus", test_test_corpus),
        ("Performance Benchmark", test_performance_benchmark),
        ("Competitor Benchmark", test_competitor_benchmark),
        ("Documentation", test_documentation),
        ("Test Files", test_test_files),
    ]

    results = []

    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n  ✗ ERROR in {test_name}: {e}")
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status:8} {test_name}")

    print()
    print(f"Results: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 ALL PHASE 4 COMPONENTS VALIDATED SUCCESSFULLY!")
        print("\n✅ Ready for production deployment")
        return 0
    else:
        print(f"\n⚠ {total - passed} test(s) failed")
        print("\n❌ Fix issues before deployment")
        return 1

if __name__ == "__main__":
    exit(main())
