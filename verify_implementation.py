#!/usr/bin/env python3
"""
Verification script for Quality Coach recalibration implementation.
Checks that all files exist and can be imported.
"""

import sys
from pathlib import Path

def check_file_exists(filepath: str) -> bool:
    """Check if a file exists"""
    path = Path(filepath)
    exists = path.exists()
    status = "✓" if exists else "✗"
    print(f"{status} {filepath}")
    return exists

def check_import(module_path: str, class_name: str) -> bool:
    """Check if a module can be imported"""
    try:
        module = __import__(module_path, fromlist=[class_name])
        cls = getattr(module, class_name)
        status = "✓"
        print(f"{status} Import: {module_path}.{class_name}")
        return True
    except Exception as e:
        status = "✗"
        print(f"{status} Import: {module_path}.{class_name} - Error: {e}")
        return False

def main():
    print("=" * 70)
    print("Quality Coach Recalibration - Implementation Verification")
    print("=" * 70)

    all_passed = True

    # Check service files
    print("\n📁 Service Files:")
    service_files = [
        "backend/services/writing_quality_analyzer.py",
        "backend/services/context_aware_scorer.py",
        "backend/services/feedback_generator.py",
        "backend/services/benchmark_tracker.py",
        "backend/services/content_impact_analyzer.py",
        "backend/services/scorer_v2.py"
    ]

    for filepath in service_files:
        if not check_file_exists(filepath):
            all_passed = False

    # Check test files
    print("\n📁 Test Files:")
    test_files = [
        "tests/test_writing_quality_analyzer.py",
        "tests/test_context_aware_scorer.py",
        "tests/test_feedback_generator.py",
        "tests/test_benchmark_tracker.py",
        "tests/test_integration_quality_coach.py"
    ]

    for filepath in test_files:
        if not check_file_exists(filepath):
            all_passed = False

    # Check documentation files
    print("\n📁 Documentation Files:")
    doc_files = [
        "docs/QUALITY_COACH_RECALIBRATION_SUMMARY.md",
        "docs/COMMIT_TASKS_9-15.md"
    ]

    for filepath in doc_files:
        if not check_file_exists(filepath):
            all_passed = False

    # Check pattern files
    print("\n📁 Pattern Files:")
    pattern_files = [
        "backend/data/patterns/action_verb_tiers.json",
        "backend/data/patterns/metric_patterns.json",
        "backend/data/patterns/weak_phrases.json",
        "backend/data/patterns/generic_to_specific.json"
    ]

    for filepath in pattern_files:
        if not check_file_exists(filepath):
            all_passed = False

    # Check imports
    print("\n📦 Module Imports:")
    imports = [
        ("backend.services.writing_quality_analyzer", "WritingQualityAnalyzer"),
        ("backend.services.context_aware_scorer", "ContextAwareScorer"),
        ("backend.services.feedback_generator", "FeedbackGenerator"),
        ("backend.services.benchmark_tracker", "BenchmarkTracker"),
        ("backend.services.content_impact_analyzer", "ContentImpactAnalyzer"),
        ("backend.services.scorer_v2", "AdaptiveScorer")
    ]

    for module_path, class_name in imports:
        if not check_import(module_path, class_name):
            all_passed = False

    # Quick functionality test
    print("\n🧪 Quick Functionality Test:")
    try:
        from backend.services.writing_quality_analyzer import WritingQualityAnalyzer
        from backend.services.context_aware_scorer import ContextAwareScorer
        from backend.services.feedback_generator import FeedbackGenerator
        from backend.services.benchmark_tracker import BenchmarkTracker

        # Test WritingQualityAnalyzer
        wqa = WritingQualityAnalyzer()
        result = wqa.score_grammar_with_severity([])
        assert result['score'] == 10.0, "WritingQualityAnalyzer test failed"
        print("✓ WritingQualityAnalyzer: Basic test passed")

        # Test ContextAwareScorer
        cas = ContextAwareScorer()
        adjusted = cas.apply_level_multiplier(10.0, "entry", "gap_penalty")
        assert adjusted == 6.0, "ContextAwareScorer test failed"
        print("✓ ContextAwareScorer: Basic test passed")

        # Test FeedbackGenerator
        fg = FeedbackGenerator()
        interp = fg.interpret_overall_score(85, "senior")
        assert interp['rating'] == 'excellent', "FeedbackGenerator test failed"
        print("✓ FeedbackGenerator: Basic test passed")

        # Test BenchmarkTracker
        bt = BenchmarkTracker()
        bt.track_score(75, "software_engineer", "senior")
        assert bt.get_score_count() == 1, "BenchmarkTracker test failed"
        print("✓ BenchmarkTracker: Basic test passed")

        print("✓ All functionality tests passed")

    except Exception as e:
        print(f"✗ Functionality test failed: {e}")
        all_passed = False

    # Summary
    print("\n" + "=" * 70)
    if all_passed:
        print("✅ ALL CHECKS PASSED - Implementation is complete and ready!")
        print("\nNext steps:")
        print("1. Run: pytest tests/ -v")
        print("2. Make commits following docs/COMMIT_TASKS_9-15.md")
        print("3. Test with real resume data")
        return 0
    else:
        print("❌ SOME CHECKS FAILED - Please review errors above")
        return 1

if __name__ == "__main__":
    sys.exit(main())
