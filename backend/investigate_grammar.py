#!/usr/bin/env python3
"""
Investigation script for grammar checker issues.
Tests with actual CV: SWASTIK PAUL_CV_DIG_TRSFN STGY_PM-2.pdf
"""

import sys
import os
import json

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.parser import parse_resume
from services.scorer_quality import QualityScorer
from services.red_flags_validator import RedFlagsValidator
from services.grammar_checker import get_grammar_checker

# Test file path
CV_PATH = "/Users/sabuj.mondal/Downloads/SWASTIK PAUL_CV_DIG_TRSFN STGY_PM-2.pdf"


def test_grammar_checker_directly():
    """Test LanguageTool grammar checker directly"""
    print("=" * 80)
    print("TEST 1: Testing Grammar Checker Directly (LanguageTool)")
    print("=" * 80)

    try:
        checker = get_grammar_checker()

        # Test with some problematic text
        test_texts = [
            "I has many experiance in managment.",  # Multiple errors
            "Their is alot of things to do.",  # Common mistakes
            "Develped and implimented new strategys.",  # Typos
            "Managed cross-functional team.",  # Good text
        ]

        for text in test_texts:
            print(f"\nChecking: '{text}'")
            result = checker.check(text)
            print(f"  Issues: {result['total_issues']}")
            print(f"  Score: {result['score']}/100")
            print(f"  Severity: {result['severity_breakdown']}")
            if result['issues']:
                for issue in result['issues'][:3]:
                    print(f"    - {issue['message']}")

        print("\n✓ Grammar checker is working")
        return True

    except Exception as e:
        print(f"\n✗ Grammar checker error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_cv_parsing():
    """Test CV parsing and text extraction"""
    print("\n" + "=" * 80)
    print("TEST 2: Testing CV Parsing and Text Extraction")
    print("=" * 80)

    try:
        print(f"\nParsing CV: {CV_PATH}")
        resume_data = parse_resume(CV_PATH)

        print(f"\n✓ CV parsed successfully")
        print(f"  Name: {resume_data.contact.get('name', 'N/A')}")
        print(f"  Experience entries: {len(resume_data.experience) if resume_data.experience else 0}")
        print(f"  Education entries: {len(resume_data.education) if resume_data.education else 0}")
        print(f"  Skills: {len(resume_data.skills) if resume_data.skills else 0}")

        # Extract some text samples
        if resume_data.experience:
            print("\n  Sample experience text:")
            for i, exp in enumerate(resume_data.experience[:2]):
                print(f"    [{i+1}] {exp.get('title', 'N/A')} at {exp.get('company', 'N/A')}")
                desc = exp.get('description', '')
                if desc:
                    lines = desc.split('\n')[:2]
                    for line in lines:
                        print(f"        {line[:100]}")

        return resume_data

    except Exception as e:
        print(f"\n✗ CV parsing error: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_red_flags_validator(resume_data):
    """Test red flags validator grammar checking"""
    print("\n" + "=" * 80)
    print("TEST 3: Testing Red Flags Validator Grammar Checking")
    print("=" * 80)

    try:
        validator = RedFlagsValidator()

        # Test grammar validation directly
        print("\nRunning grammar validation...")
        grammar_issues = validator.validate_grammar(resume_data)

        print(f"\n✓ Grammar validation completed")
        print(f"  Total grammar issues found: {len(grammar_issues)}")

        # Categorize issues
        by_category = {}
        for issue in grammar_issues:
            cat = issue.get('category', 'unknown')
            by_category[cat] = by_category.get(cat, 0) + 1

        print(f"  Breakdown by category:")
        for cat, count in sorted(by_category.items()):
            print(f"    - {cat}: {count}")

        # Show first few issues
        if grammar_issues:
            print(f"\n  Sample issues:")
            for i, issue in enumerate(grammar_issues[:5]):
                print(f"    [{i+1}] [{issue['category']}] {issue['message']}")
        else:
            print("\n  ⚠ WARNING: No grammar issues detected!")

        return grammar_issues

    except Exception as e:
        print(f"\n✗ Grammar validation error: {e}")
        import traceback
        traceback.print_exc()
        return []


def test_full_validation(resume_data):
    """Test full validation flow"""
    print("\n" + "=" * 80)
    print("TEST 4: Testing Full Validation Flow")
    print("=" * 80)

    try:
        validator = RedFlagsValidator()

        print("\nRunning full validation (all 44 parameters)...")
        validation_result = validator.validate_resume(resume_data, "product_manager", "mid")

        print(f"\n✓ Full validation completed")
        print(f"  Critical issues: {len(validation_result['critical'])}")
        print(f"  Warning issues: {len(validation_result['warnings'])}")
        print(f"  Suggestions: {len(validation_result['suggestions'])}")

        # Check for grammar-related issues
        grammar_related = ['typo', 'grammar', 'capitalization', 'spelling']
        grammar_warnings = [
            w for w in validation_result['warnings']
            if w.get('category') in grammar_related
        ]

        print(f"\n  Grammar-related warnings: {len(grammar_warnings)}")
        if grammar_warnings:
            for i, issue in enumerate(grammar_warnings[:5]):
                print(f"    [{i+1}] [{issue['category']}] {issue['message']}")
        else:
            print("    ⚠ WARNING: No grammar warnings in validation result!")

        return validation_result

    except Exception as e:
        print(f"\n✗ Full validation error: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_quality_scorer(resume_data):
    """Test quality scorer with CV"""
    print("\n" + "=" * 80)
    print("TEST 5: Testing Quality Scorer")
    print("=" * 80)

    try:
        scorer = QualityScorer()

        print("\nScoring resume in Quality Mode...")
        score_result = scorer.score(
            resume_data,
            role_id="product_manager",
            level="mid"
        )

        print(f"\n✓ Scoring completed")
        print(f"  Overall Score: {score_result['score']}/100")
        print(f"\n  Breakdown:")

        breakdown = score_result['breakdown']
        for category, data in breakdown.items():
            score = data['score']
            max_score = data['max_score']
            print(f"    {category}: {score}/{max_score}")

        # Check polish score (includes grammar)
        polish = breakdown['polish']
        print(f"\n  Polish Details:")
        print(f"    Score: {polish['score']}/{polish['max_score']}")
        if 'details' in polish:
            details = polish['details']
            print(f"    Grammar Score: {details.get('grammar_score', 'N/A')}/10")
            print(f"    Grammar Errors: {details.get('grammar_errors', 'N/A')}")
            print(f"    Grammar Feedback: {details.get('grammar_feedback', 'N/A')}")

            if details.get('grammar_errors', 0) == 0:
                print(f"\n    ⚠ WARNING: Grammar errors = 0! This is likely wrong!")

        return score_result

    except Exception as e:
        print(f"\n✗ Scoring error: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    print("=" * 80)
    print("GRAMMAR CHECKER INVESTIGATION")
    print("Investigating why grammar checking is not reducing scores")
    print("=" * 80)

    results = {}

    # Test 1: Grammar checker directly
    results['grammar_checker'] = test_grammar_checker_directly()

    # Test 2: Parse CV
    resume_data = test_cv_parsing()
    if not resume_data:
        print("\n✗ FATAL: Cannot proceed without parsed CV data")
        return

    # Test 3: Red flags grammar validation
    grammar_issues = test_red_flags_validator(resume_data)
    results['grammar_validation'] = len(grammar_issues) > 0

    # Test 4: Full validation
    validation_result = test_full_validation(resume_data)
    results['full_validation'] = validation_result is not None

    # Test 5: Quality scorer
    score_result = test_quality_scorer(resume_data)
    results['quality_scorer'] = score_result is not None

    # Summary
    print("\n" + "=" * 80)
    print("INVESTIGATION SUMMARY")
    print("=" * 80)

    print("\nTest Results:")
    for test_name, passed in results.items():
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"  {test_name}: {status}")

    print("\n" + "=" * 80)
    print("ROOT CAUSE ANALYSIS")
    print("=" * 80)

    # Analyze the findings
    if not results.get('grammar_checker'):
        print("\n⚠ ISSUE FOUND: Grammar checker (LanguageTool) is not working!")
        print("   - LanguageTool may not be installed")
        print("   - Check: pip install language-tool-python")

    if not results.get('grammar_validation'):
        print("\n⚠ ISSUE FOUND: Grammar validation returning no issues!")
        print("   - Red flags validator may not be using LanguageTool")
        print("   - Check validate_grammar() implementation")

    if results.get('quality_scorer') and score_result:
        polish_score = score_result['breakdown']['polish']['score']
        if polish_score >= 14:  # Out of 15
            print(f"\n⚠ ISSUE FOUND: Polish score too high ({polish_score}/15)")
            print("   - Grammar errors not being detected or penalized")
            print("   - Check _score_polish() in scorer_quality.py")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
