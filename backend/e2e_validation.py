#!/usr/bin/env python3
"""
End-to-End Validation Script
Tests critical user workflows to ensure the system is ready for launch
"""
import requests
import json
import time
from pathlib import Path

BASE_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:5173"

def print_result(test_name, passed, message=""):
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} - {test_name}")
    if message:
        print(f"   {message}")

def test_1_backend_health():
    """Test 1: Backend API is healthy"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        passed = response.status_code == 200 and response.json().get("status") == "healthy"
        print_result("Backend Health Check", passed, f"Status: {response.status_code}")
        return passed
    except Exception as e:
        print_result("Backend Health Check", False, f"Error: {str(e)}")
        return False

def test_2_frontend_accessible():
    """Test 2: Frontend is accessible"""
    try:
        response = requests.get(FRONTEND_URL, timeout=5)
        passed = response.status_code == 200 and "ATS Resume Scorer" in response.text
        print_result("Frontend Accessibility", passed, f"Status: {response.status_code}")
        return passed
    except Exception as e:
        print_result("Frontend Accessibility", False, f"Error: {str(e)}")
        return False

def test_3_roles_endpoint():
    """Test 3: Roles API endpoint works"""
    try:
        response = requests.get(f"{BASE_URL}/api/roles", timeout=5)
        passed = response.status_code == 200
        if passed:
            roles = response.json()
            passed = len(roles) > 0
            print_result("Roles API", passed, f"Found {len(roles)} role categories")
        else:
            print_result("Roles API", passed, f"Status: {response.status_code}")
        return passed
    except Exception as e:
        print_result("Roles API", False, f"Error: {str(e)}")
        return False

def test_4_upload_workflow():
    """Test 4: Resume upload workflow (without actual file)"""
    try:
        # Test upload endpoint availability
        response = requests.options(f"{BASE_URL}/api/upload", timeout=5)
        passed = response.status_code in [200, 204]
        print_result("Upload Endpoint Availability", passed, f"Status: {response.status_code}")
        return passed
    except Exception as e:
        print_result("Upload Endpoint Availability", False, f"Error: {str(e)}")
        return False

def test_5_scorer_imports():
    """Test 5: Scorer services can be imported"""
    try:
        from services.scorer_ats import score_resume_ats
        from services.scorer_quality import score_resume_quality
        from services.semantic_matcher import SemanticKeywordMatcher
        print_result("Scorer Imports", True, "All scorer services importable")
        return True
    except ImportError as e:
        print_result("Scorer Imports", False, f"Import error: {str(e)}")
        return False

def test_6_phase1_dependencies():
    """Test 6: Phase 1 critical dependencies available"""
    try:
        import sentence_transformers
        import keybert
        import language_tool_python
        import diskcache
        print_result("Phase 1 Dependencies", True, "All Phase 1 AI dependencies available")
        return True
    except ImportError as e:
        print_result("Phase 1 Dependencies", False, f"Missing: {str(e)}")
        return False

def test_7_grammar_checker():
    """Test 7: Grammar checker functionality"""
    try:
        from services.grammar_checker import check_grammar
        # Test with sample text (mock mode if LanguageTool unavailable)
        result = check_grammar("This is a test sentance with a typo.")
        passed = isinstance(result, list)
        print_result("Grammar Checker", passed, f"Returned {len(result)} issues")
        return passed
    except Exception as e:
        print_result("Grammar Checker", False, f"Error: {str(e)}")
        return False

def test_8_semantic_matching():
    """Test 8: Semantic keyword matching"""
    try:
        from services.semantic_matcher import SemanticKeywordMatcher
        matcher = SemanticKeywordMatcher()

        # Test keyword extraction
        text = "Python developer with ML experience"
        keywords = matcher.extract_keywords(text, top_n=5)
        passed = len(keywords) > 0
        print_result("Semantic Matching", passed, f"Extracted {len(keywords)} keywords")
        return passed
    except Exception as e:
        print_result("Semantic Matching", False, f"Error: {str(e)}")
        return False

def test_9_cache_utils():
    """Test 9: Cache utilities work"""
    try:
        from services.cache_utils import cache_embeddings, clear_all_caches
        print_result("Cache Utilities", True, "Cache decorators available")
        return True
    except Exception as e:
        print_result("Cache Utilities", False, f"Error: {str(e)}")
        return False

def test_10_template_manager():
    """Test 10: DOCX template manager works"""
    try:
        from services.docx_template_manager import DocxTemplateManager
        print_result("Template Manager", True, "DocxTemplateManager available")
        return True
    except Exception as e:
        print_result("Template Manager", False, f"Error: {str(e)}")
        return False

def run_all_tests():
    """Run all validation tests"""
    print("=" * 60)
    print("ATS RESUME SCORER - END-TO-END VALIDATION")
    print("=" * 60)
    print()

    tests = [
        test_1_backend_health,
        test_2_frontend_accessible,
        test_3_roles_endpoint,
        test_4_upload_workflow,
        test_5_scorer_imports,
        test_6_phase1_dependencies,
        test_7_grammar_checker,
        test_8_semantic_matching,
        test_9_cache_utils,
        test_10_template_manager,
    ]

    results = []
    for test in tests:
        passed = test()
        results.append(passed)
        print()
        time.sleep(0.5)  # Small delay for readability

    print("=" * 60)
    passed_count = sum(results)
    total_count = len(results)

    if passed_count == total_count:
        print(f"✅ ALL TESTS PASSED ({passed_count}/{total_count})")
        print("🚀 SYSTEM READY FOR LAUNCH")
        return 0
    else:
        print(f"⚠️  SOME TESTS FAILED ({passed_count}/{total_count})")
        print(f"   {total_count - passed_count} test(s) need attention")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(run_all_tests())
