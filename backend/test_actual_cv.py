#!/usr/bin/env python3
"""
Test script to analyze Swastik Paul's CV and identify why score is too high.
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.parser import parse_resume
from services.scorer_quality import QualityScorer
from services.red_flags_validator import RedFlagsValidator
from services.grammar_checker import get_grammar_checker

# CV path
CV_PATH = "/Users/sabuj.mondal/Downloads/SWASTIK PAUL_CV_DIG_TRSFN STGY_PM-2.pdf"


def test_current_system():
    """Test current scoring system"""
    print("=" * 80)
    print("CURRENT SCORING SYSTEM - Swastik Paul CV")
    print("=" * 80)

    # Parse resume
    resume_data = parse_resume(CV_PATH)
    print(f"\n✓ Parsed CV: {resume_data.contact.get('name', 'N/A')}")

    # Score with QualityScorer
    scorer = QualityScorer()
    result = scorer.score(resume_data, "product_manager", "mid")

    print(f"\nOVERALL SCORE: {result['score']}/100")
    print("\nBREAKDOWN:")
    for category, data in result['breakdown'].items():
        print(f"  {category}: {data['score']}/{data['max_score']}")

    # Focus on polish (grammar)
    polish = result['breakdown']['polish']
    print(f"\nPOLISH DETAILS (Grammar Component):")
    print(f"  Total: {polish['score']}/{polish['max_score']}")
    if 'details' in polish:
        details = polish['details']
        print(f"  Grammar Score: {details.get('grammar_score', 'N/A')}/10")
        print(f"  Grammar Errors: {details.get('grammar_errors', 'N/A')}")
        print(f"  Grammar Feedback: {details.get('grammar_feedback', 'N/A')}")

    return result


def test_grammar_validation():
    """Test grammar validation directly"""
    print("\n" + "=" * 80)
    print("GRAMMAR VALIDATION TEST (pyspellchecker)")
    print("=" * 80)

    resume_data = parse_resume(CV_PATH)
    validator = RedFlagsValidator()

    # Get grammar issues
    grammar_issues = validator.validate_grammar(resume_data)

    print(f"\nGrammar Issues Found: {len(grammar_issues)}")

    # Group by category
    by_category = {}
    for issue in grammar_issues:
        cat = issue.get('category', 'unknown')
        by_category[cat] = by_category.get(cat, 0) + 1

    print("\nBy Category:")
    for cat, count in sorted(by_category.items()):
        print(f"  {cat}: {count}")

    # Show first 10 issues
    if grammar_issues:
        print("\nFirst 10 Issues:")
        for i, issue in enumerate(grammar_issues[:10], 1):
            print(f"  {i}. [{issue['category']}] {issue['message']}")

    return grammar_issues


def test_languagetool():
    """Test LanguageTool grammar checker"""
    print("\n" + "=" * 80)
    print("LANGUAGETOOL GRAMMAR CHECKER TEST")
    print("=" * 80)

    # Parse resume
    resume_data = parse_resume(CV_PATH)

    # Get text from experience
    all_text = []
    if resume_data.experience:
        for exp in resume_data.experience:
            desc = exp.get('description', '')
            if desc:
                all_text.append(desc)

    combined_text = " ".join(all_text)
    print(f"\nExtracted Text Length: {len(combined_text)} characters")
    print(f"First 200 chars: {combined_text[:200]}...")

    # Test with LanguageTool
    try:
        checker = get_grammar_checker()
        print("\n✓ LanguageTool initialized successfully")

        # Check the text
        result = checker.check(combined_text, max_issues=100)

        print(f"\nLanguageTool Results:")
        print(f"  Total Issues: {result['total_issues']}")
        print(f"  Grammar Score: {result['score']}/100")
        print(f"  Message: {result['message']}")
        print(f"\nSeverity Breakdown:")
        for severity, count in result['severity_breakdown'].items():
            print(f"  {severity}: {count}")

        # Show first 15 issues
        if result['issues']:
            print(f"\nFirst 15 Issues:")
            for i, issue in enumerate(result['issues'][:15], 1):
                print(f"  {i}. [{issue['severity']}] {issue['category']}: {issue['message'][:80]}")

        return result

    except Exception as e:
        print(f"\n✗ LanguageTool Error: {e}")
        import traceback
        traceback.print_exc()
        return None


def analyze_discrepancy():
    """Analyze the discrepancy between systems"""
    print("\n" + "=" * 80)
    print("ROOT CAUSE ANALYSIS")
    print("=" * 80)

    # Get results from both systems
    resume_data = parse_resume(CV_PATH)

    # Current system
    scorer = QualityScorer()
    score_result = scorer.score(resume_data, "product_manager", "mid")
    current_score = score_result['score']
    grammar_errors_detected = score_result['breakdown']['polish']['details'].get('grammar_errors', 0)

    # LanguageTool
    all_text = []
    if resume_data.experience:
        for exp in resume_data.experience:
            desc = exp.get('description', '')
            if desc:
                all_text.append(desc)
    combined_text = " ".join(all_text)

    try:
        checker = get_grammar_checker()
        lt_result = checker.check(combined_text, max_issues=100)
        lt_issues = lt_result['total_issues']
        lt_critical = lt_result['severity_breakdown'].get('critical', 0)
    except:
        lt_issues = None
        lt_critical = None

    print(f"\nCURRENT SYSTEM:")
    print(f"  Overall Score: {current_score}/100")
    print(f"  Grammar Errors Detected: {grammar_errors_detected}")
    print(f"  Grammar Checker: pyspellchecker (basic)")

    print(f"\nLANGUAGETOOL (NOT USED):")
    if lt_issues is not None:
        print(f"  Total Issues: {lt_issues}")
        print(f"  Critical Issues: {lt_critical}")
        print(f"  Status: Available but NOT integrated")
    else:
        print(f"  Status: Failed to initialize")

    print(f"\n{'='*80}")
    print("CONCLUSION:")
    print("="*80)

    if lt_issues and lt_issues > grammar_errors_detected:
        print(f"\n⚠️  ISSUE IDENTIFIED:")
        print(f"  - LanguageTool finds {lt_issues} issues")
        print(f"  - Current system finds {grammar_errors_detected} issues")
        print(f"  - Difference: {lt_issues - grammar_errors_detected} issues missed!")
        print(f"\n  ROOT CAUSE:")
        print(f"  - RedFlagsValidator.validate_grammar() uses pyspellchecker")
        print(f"  - LanguageTool is implemented but NOT integrated")
        print(f"  - Need to update validate_grammar() to use LanguageTool")
        print(f"\n  SOLUTION:")
        print(f"  - Integrate grammar_checker.py into red_flags_validator.py")
        print(f"  - Replace basic spelling checks with LanguageTool")
        print(f"  - Expected score reduction: ~5-15 points")
    else:
        print(f"\n✓ Systems match or LanguageTool unavailable")


def main():
    print("=" * 80)
    print("SWASTIK PAUL CV - GRAMMAR CHECKER INVESTIGATION")
    print("=" * 80)
    print(f"\nCV Path: {CV_PATH}")
    print(f"Issue: Score is 64.1/100 - TOO HIGH")
    print(f"Expected: Grammar mistakes should lower the score")

    # Run tests
    test_current_system()
    test_grammar_validation()
    test_languagetool()
    analyze_discrepancy()

    print("\n" + "=" * 80)
    print("INVESTIGATION COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
