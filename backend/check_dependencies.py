#!/usr/bin/env python3
"""
Dependency Checker for ATS Resume Scorer
Checks which critical dependencies are available
"""

import sys

dependencies_status = {}

# Critical Phase 1 dependencies
critical_deps = {
    'sentence_transformers': 'Semantic keyword matching',
    'keybert': 'Keyword extraction',
    'language_tool_python': 'Grammar checking',
    'diskcache': 'Performance caching',
}

# Core API dependencies
api_deps = {
    'fastapi': 'API framework',
    'uvicorn': 'ASGI server',
    'pydantic': 'Data validation',
    'httpx': 'HTTP client',
    'jwt': 'JWT authentication',
    'dotenv': 'Environment variables',
}

# Document processing
doc_deps = {
    'docx': 'DOCX parsing',
    'PyMuPDF': 'PDF parsing (alternative)',
    'pdfplumber': 'PDF parsing',
}

# Optional
optional_deps = {
    'spacy': 'Advanced NLP (optional)',
}

def check_dependency(module_name, display_name):
    try:
        __import__(module_name)
        print(f"✅ {display_name:30} - Available")
        return True
    except ImportError:
        print(f"❌ {display_name:30} - Missing")
        return False

print("=" * 60)
print("ATS Resume Scorer - Dependency Check")
print("=" * 60)

print("\n🔥 CRITICAL DEPENDENCIES (Phase 1):")
critical_available = 0
for module, desc in critical_deps.items():
    if check_dependency(module, desc):
        critical_available += 1

print(f"\nCritical: {critical_available}/{len(critical_deps)} available")

print("\n📦 CORE API DEPENDENCIES:")
api_available = 0
for module, desc in api_deps.items():
    if check_dependency(module, desc):
        api_available += 1

print(f"\nAPI: {api_available}/{len(api_deps)} available")

print("\n📄 DOCUMENT PROCESSING:")
doc_available = 0
for module, desc in doc_deps.items():
    if check_dependency(module, desc):
        doc_available += 1

print(f"\nDocument: {doc_available}/{len(doc_deps)} available")

print("\n⭐ OPTIONAL DEPENDENCIES:")
for module, desc in optional_deps.items():
    check_dependency(module, desc)

print("\n" + "=" * 60)
total = critical_available + api_available + doc_available
required = len(critical_deps) + len(api_deps) + len(doc_deps)

if critical_available == len(critical_deps) and api_available == len(api_deps):
    print("✅ SYSTEM READY - All critical dependencies available!")
    print(f"   Total: {total}/{required} dependencies")
    sys.exit(0)
elif critical_available == len(critical_deps):
    print("⚠️  PARTIALLY READY - Critical AI features available")
    print(f"   Missing some optional dependencies: {required - total}")
    sys.exit(0)
else:
    print("❌ NOT READY - Missing critical dependencies")
    print(f"   Available: {total}/{required}")
    sys.exit(1)
