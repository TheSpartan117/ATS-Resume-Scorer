#!/usr/bin/env python3
"""
Phase 1 Implementation Validator
Checks that all Phase 1 components are properly installed and functional.
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def check_file_exists(filepath, description):
    """Check if a file exists"""
    if os.path.exists(filepath):
        print(f"✅ {description}")
        return True
    else:
        print(f"❌ {description} - NOT FOUND: {filepath}")
        return False

def check_import(module_name, description):
    """Check if a module can be imported"""
    try:
        __import__(module_name)
        print(f"✅ {description}")
        return True
    except ImportError as e:
        print(f"⚠️  {description} - {str(e)}")
        return False

def check_dependency(package_name, description):
    """Check if a dependency is installed"""
    try:
        __import__(package_name.replace('-', '_'))
        print(f"✅ {description}")
        return True
    except ImportError:
        print(f"⚠️  {description} - Install: pip install {package_name}")
        return False

def main():
    print("=" * 60)
    print("Phase 1 Implementation Validation")
    print("=" * 60)
    print()

    all_checks = []

    # Check modified files
    print("📝 Checking Modified Files:")
    print("-" * 60)
    all_checks.append(check_file_exists(
        "backend/services/scorer_ats.py",
        "Modified: scorer_ats.py"
    ))
    all_checks.append(check_file_exists(
        "backend/services/scorer_quality.py",
        "Modified: scorer_quality.py"
    ))
    all_checks.append(check_file_exists(
        "backend/requirements.txt",
        "Modified: requirements.txt"
    ))
    print()

    # Check new files
    print("📦 Checking New Files:")
    print("-" * 60)
    all_checks.append(check_file_exists(
        "backend/services/semantic_matcher.py",
        "Created: semantic_matcher.py"
    ))
    all_checks.append(check_file_exists(
        "backend/services/grammar_checker.py",
        "Created: grammar_checker.py"
    ))
    all_checks.append(check_file_exists(
        "backend/services/cache_utils.py",
        "Created: cache_utils.py"
    ))
    all_checks.append(check_file_exists(
        "tests/test_phase1_improvements.py",
        "Created: test_phase1_improvements.py"
    ))
    all_checks.append(check_file_exists(
        "docs/PHASE1_IMPLEMENTATION_REPORT.md",
        "Created: PHASE1_IMPLEMENTATION_REPORT.md"
    ))
    print()

    # Check imports
    print("🔧 Checking Core Modules:")
    print("-" * 60)
    all_checks.append(check_import(
        "backend.services.scorer_ats",
        "Import: scorer_ats"
    ))
    all_checks.append(check_import(
        "backend.services.scorer_quality",
        "Import: scorer_quality"
    ))
    all_checks.append(check_import(
        "backend.services.semantic_matcher",
        "Import: semantic_matcher"
    ))
    all_checks.append(check_import(
        "backend.services.grammar_checker",
        "Import: grammar_checker"
    ))
    all_checks.append(check_import(
        "backend.services.cache_utils",
        "Import: cache_utils"
    ))
    print()

    # Check dependencies
    print("📚 Checking Dependencies:")
    print("-" * 60)
    dep_checks = []
    dep_checks.append(check_dependency(
        "sentence_transformers",
        "Dependency: sentence-transformers"
    ))
    dep_checks.append(check_dependency(
        "keybert",
        "Dependency: keybert"
    ))
    dep_checks.append(check_dependency(
        "language_tool_python",
        "Dependency: language-tool-python"
    ))
    dep_checks.append(check_dependency(
        "diskcache",
        "Dependency: diskcache"
    ))
    print()

    # Test basic functionality
    print("🧪 Testing Basic Functionality:")
    print("-" * 60)

    try:
        from backend.services.semantic_matcher import SemanticKeywordMatcher
        matcher = SemanticKeywordMatcher()
        print("✅ SemanticKeywordMatcher initialized")
        all_checks.append(True)
    except Exception as e:
        print(f"⚠️  SemanticKeywordMatcher failed: {e}")
        all_checks.append(False)

    try:
        from backend.services.grammar_checker import GrammarChecker
        checker = GrammarChecker()
        print("✅ GrammarChecker initialized")
        all_checks.append(True)
    except Exception as e:
        print(f"⚠️  GrammarChecker failed: {e}")
        all_checks.append(False)

    try:
        from backend.services.cache_utils import get_cache
        cache = get_cache()
        if cache is not None:
            print("✅ Cache system available")
            all_checks.append(True)
        else:
            print("⚠️  Cache system not available (diskcache not installed)")
            all_checks.append(False)
    except Exception as e:
        print(f"⚠️  Cache system failed: {e}")
        all_checks.append(False)

    try:
        from backend.services.scorer_ats import ATSScorer
        scorer = ATSScorer()
        print("✅ ATSScorer with Phase 1 improvements")
        all_checks.append(True)
    except Exception as e:
        print(f"❌ ATSScorer failed: {e}")
        all_checks.append(False)

    print()

    # Summary
    print("=" * 60)
    print("Summary:")
    print("=" * 60)

    passed = sum(all_checks)
    total = len(all_checks)
    deps_passed = sum(dep_checks)
    deps_total = len(dep_checks)

    print(f"Core checks: {passed}/{total} passed")
    print(f"Dependencies: {deps_passed}/{deps_total} installed")
    print()

    if passed == total and deps_passed == deps_total:
        print("🎉 Phase 1 implementation is complete and functional!")
        print()
        print("Next steps:")
        print("1. Run tests: python -m pytest tests/test_phase1_improvements.py -v")
        print("2. Test with sample resumes")
        print("3. Compare scores before/after")
        return 0
    elif passed == total:
        print("✅ Core implementation complete!")
        print("⚠️  Some dependencies not installed. Install with:")
        print("   pip install -r backend/requirements.txt")
        print()
        print("The system will work with fallbacks, but for full functionality:")
        print("- Install sentence-transformers for semantic matching")
        print("- Install keybert for keyword extraction")
        print("- Install language-tool-python for grammar checking")
        print("- Install diskcache for caching")
        return 1
    else:
        print("❌ Some core components are missing or not functional.")
        print("   Review the errors above and fix issues.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
