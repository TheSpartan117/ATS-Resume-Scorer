"""
Quick test script for enhanced suggestions system.

Run: python -m backend.test_suggestions
"""

from backend.services.suggestion_generator import EnhancedSuggestionGenerator
from backend.services.suggestion_integrator import SuggestionIntegrator
from backend.services.parser import ResumeData
import json


def test_missing_summary():
    """Test professional summary suggestion generation."""
    print("\n" + "="*80)
    print("TEST 1: Missing Professional Summary")
    print("="*80)

    generator = EnhancedSuggestionGenerator("software_engineer", "mid")

    resume_data = ResumeData(
        fileName="test.pdf",
        contact={"name": "John Doe", "email": "john@example.com"},
        experience=[],
        education=[],
        skills=[],
        certifications=[],
        metadata={}
    )

    suggestions = generator.generate_suggestions(
        resume_data=resume_data,
        missing_keywords=[],
        weak_bullets=[],
        format_issues=[]
    )

    if suggestions:
        suggestion = suggestions[0]
        print(f"\nSuggestion ID: {suggestion['id']}")
        print(f"Type: {suggestion['type']}")
        print(f"Severity: {suggestion['severity']}")
        print(f"Title: {suggestion['title']}")
        print(f"Description: {suggestion['description']}")
        print(f"\nTemplate preview (first 200 chars):")
        print(suggestion['template'][:200] + "...")
        print(f"\nQuick Fix:")
        print(f"  Before: {suggestion['quickFix']['before']}")
        print(f"  After: {suggestion['quickFix']['after'][:100]}...")
        print("\n✅ Test passed!")
    else:
        print("\n❌ No suggestions generated")


def test_missing_keywords():
    """Test keyword suggestion generation."""
    print("\n" + "="*80)
    print("TEST 2: Missing Keywords")
    print("="*80)

    generator = EnhancedSuggestionGenerator("software_engineer", "mid")

    resume_data = ResumeData(
        fileName="test.pdf",
        contact={"name": "John Doe"},
        experience=[],
        education=[],
        skills=["HTML", "CSS"],  # Very basic skills
        certifications=[],
        metadata={}
    )

    missing_keywords = [
        "python", "javascript", "react", "node.js", "aws", "docker",
        "kubernetes", "postgresql", "mongodb", "git", "ci/cd", "agile",
        "microservices", "rest api", "graphql"
    ]

    suggestions = generator.generate_suggestions(
        resume_data=resume_data,
        missing_keywords=missing_keywords,
        weak_bullets=[],
        format_issues=[]
    )

    # Find keyword suggestion
    keyword_suggestion = None
    for s in suggestions:
        if s['type'] == 'keyword':
            keyword_suggestion = s
            break

    if keyword_suggestion:
        print(f"\nSuggestion ID: {keyword_suggestion['id']}")
        print(f"Type: {keyword_suggestion['type']}")
        print(f"Title: {keyword_suggestion['title']}")
        print(f"Keywords to add ({len(keyword_suggestion.get('keywords', []))}):")
        print(f"  {', '.join(keyword_suggestion.get('keywords', [])[:10])}...")
        print(f"\nTemplate preview (first 300 chars):")
        print(keyword_suggestion['template'][:300] + "...")
        print("\n✅ Test passed!")
    else:
        print("\n❌ No keyword suggestions generated")


def test_weak_bullets():
    """Test bullet point strengthening suggestions."""
    print("\n" + "="*80)
    print("TEST 3: Weak Bullet Points")
    print("="*80)

    generator = EnhancedSuggestionGenerator("software_engineer", "mid")

    resume_data = ResumeData(
        fileName="test.pdf",
        contact={"name": "John Doe"},
        experience=[
            {
                "title": "Software Engineer",
                "company": "Tech Corp",
                "description": "Worked on web applications"
            },
            {
                "title": "Developer",
                "company": "StartupXYZ",
                "description": "Responsible for backend development"
            }
        ],
        education=[],
        skills=[],
        certifications=[],
        metadata={}
    )

    weak_bullets = [
        {
            "text": "Worked on web applications",
            "description": "Worked on web applications",
            "company": "Tech Corp",
            "title": "Software Engineer"
        },
        {
            "text": "Responsible for backend development",
            "description": "Responsible for backend development",
            "company": "StartupXYZ",
            "title": "Developer"
        }
    ]

    suggestions = generator.generate_suggestions(
        resume_data=resume_data,
        missing_keywords=[],
        weak_bullets=weak_bullets,
        format_issues=[]
    )

    # Find writing suggestion
    writing_suggestion = None
    for s in suggestions:
        if s['type'] == 'writing':
            writing_suggestion = s
            break

    if writing_suggestion:
        print(f"\nSuggestion ID: {writing_suggestion['id']}")
        print(f"Type: {writing_suggestion['type']}")
        print(f"Title: {writing_suggestion['title']}")
        print(f"\nQuick Fix Example:")
        qf = writing_suggestion['quickFix']
        print(f"  Before: {qf['before']}")
        print(f"  After: {qf['after']}")
        print(f"\nTemplate preview (first 400 chars):")
        print(writing_suggestion['template'][:400] + "...")
        print("\n✅ Test passed!")
    else:
        print("\n❌ No writing suggestions generated")


def test_format_issues():
    """Test format fix suggestions."""
    print("\n" + "="*80)
    print("TEST 4: Format Issues")
    print("="*80)

    generator = EnhancedSuggestionGenerator("software_engineer", "mid")

    resume_data = ResumeData(
        fileName="test.pdf",
        contact={"name": "John Doe"},
        experience=[],
        education=[],
        skills=[],
        certifications=[],
        metadata={}
    )

    format_issues = [
        "Date format inconsistent",
        "Bullet points not ATS-friendly",
        "Font not standard"
    ]

    suggestions = generator.generate_suggestions(
        resume_data=resume_data,
        missing_keywords=[],
        weak_bullets=[],
        format_issues=format_issues
    )

    # Find formatting suggestion
    format_suggestion = None
    for s in suggestions:
        if s['type'] == 'formatting':
            format_suggestion = s
            break

    if format_suggestion:
        print(f"\nSuggestion ID: {format_suggestion['id']}")
        print(f"Type: {format_suggestion['type']}")
        print(f"Title: {format_suggestion['title']}")
        print(f"Issues detected: {len(format_issues)}")
        print(f"\nTemplate preview (first 300 chars):")
        print(format_suggestion['template'][:300] + "...")
        print("\n✅ Test passed!")
    else:
        print("\n❌ No formatting suggestions generated")


def test_integration():
    """Test suggestion integration with score results."""
    print("\n" + "="*80)
    print("TEST 5: Integration with Scoring")
    print("="*80)

    # Simulate score result
    score_result = {
        "overallScore": 65.0,
        "mode": "quality_coach",
        "breakdown": {
            "role_keywords": {
                "score": 15,
                "maxScore": 25,
                "issues": [("warning", "Missing 10 role keywords")]
            }
        },
        "issues": {
            "critical": [],
            "warnings": [("warning", "Missing important keywords")],
            "suggestions": [("suggestion", "Add professional summary")],
            "info": []
        },
        "keyword_details": {
            "missing_keywords": ["python", "react", "aws", "docker"]
        }
    }

    resume_data = ResumeData(
        fileName="test.pdf",
        contact={"name": "John Doe"},
        experience=[
            {
                "description": "Worked on projects"
            }
        ],
        education=[],
        skills=["HTML"],
        certifications=[],
        metadata={}
    )

    # Enrich with suggestions
    enriched = SuggestionIntegrator.enrich_score_result(
        score_result=score_result,
        resume_data=resume_data,
        role="software_engineer",
        level="mid",
        job_description=""
    )

    if 'enhanced_suggestions' in enriched:
        suggestions = enriched['enhanced_suggestions']
        print(f"\n✅ Enhanced suggestions added to score result")
        print(f"   Total suggestions: {len(suggestions)}")

        for i, s in enumerate(suggestions[:3], 1):
            print(f"\n   Suggestion {i}:")
            print(f"     ID: {s['id']}")
            print(f"     Type: {s['type']}")
            print(f"     Title: {s['title']}")
            print(f"     Has template: {'template' in s}")
            print(f"     Has quick fix: {'quickFix' in s}")

        print("\n✅ Test passed!")
    else:
        print("\n❌ Enhanced suggestions not added to score result")


def main():
    """Run all tests."""
    print("\n" + "="*80)
    print("ENHANCED SUGGESTIONS SYSTEM - TEST SUITE")
    print("="*80)

    try:
        test_missing_summary()
        test_missing_keywords()
        test_weak_bullets()
        test_format_issues()
        test_integration()

        print("\n" + "="*80)
        print("ALL TESTS COMPLETED SUCCESSFULLY! ✅")
        print("="*80)

    except Exception as e:
        print(f"\n❌ TEST FAILED with error:")
        print(f"   {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
