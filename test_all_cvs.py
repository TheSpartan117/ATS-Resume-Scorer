#!/usr/bin/env python3
"""
Comprehensive test of all 3 benchmark CVs to identify scoring issues.
"""
import sys
sys.path.insert(0, '/Users/sabuj.mondal/ats-resume-scorer')

from backend.services.parser import parse_pdf
from backend.services.scorer_v3_adapter import ScorerV3Adapter

# Test CVs with ResumeWorded target scores
TEST_CVS = [
    {
        'name': 'Sabuj Mondal',
        'path': '/Users/sabuj.mondal/Downloads/Sabuj_Mondal_PM_CV.pdf',
        'role': 'product_manager',
        'level': 'senior',
        'target_score': 86
    },
    {
        'name': 'Aishik Das',
        'path': '/Users/sabuj.mondal/Downloads/AISHIK DAS_CV_v2.pdf',
        'role': 'product_manager',
        'level': 'mid',
        'target_score': 81
    },
    {
        'name': 'Swastik Paul',
        'path': '/Users/sabuj.mondal/Downloads/SWASTIK PAUL_CV_DIG_TRSFN STGY_PM-2.pdf',
        'role': 'product_manager',
        'level': 'mid',
        'target_score': 65
    }
]

def test_cv(cv_info):
    """Test a single CV and show detailed results."""
    print(f"\n{'='*80}")
    print(f"TESTING: {cv_info['name']}")
    print(f"Target Score: {cv_info['target_score']}/100")
    print(f"Role: {cv_info['role']}, Level: {cv_info['level']}")
    print('='*80)

    # Parse CV
    try:
        with open(cv_info['path'], 'rb') as f:
            resume_data = parse_pdf(f.read(), cv_info['name'] + '.pdf')

        print(f"✓ Parsed: {resume_data.metadata.get('wordCount', 0)} words")

        # Score with adapter
        adapter = ScorerV3Adapter()
        result = adapter.score(
            resume_data=resume_data,
            job_description=None,  # No JD - should use default keywords
            level=cv_info['level'],
            role=cv_info['role']
        )

        overall = result['overallScore']
        target = cv_info['target_score']
        diff = overall - target

        print(f"\n{'─'*80}")
        print(f"OVERALL SCORE: {overall}/100 (Target: {target}) [Diff: {diff:+d}]")
        print(f"{'─'*80}")

        # Show category breakdown
        print("\nCATEGORY BREAKDOWN:")
        for category, details in result['breakdown'].items():
            score = details['score']
            max_score = details['maxScore']
            pct = (score / max_score * 100) if max_score > 0 else 0

            status = '✓' if pct >= 70 else '⚠' if pct >= 40 else '✗'
            print(f"  {status} {category:25s} {score:5.1f}/{max_score:2d} pts ({pct:5.1f}%)")

        # Show low-scoring parameters
        print("\nLOW-SCORING PARAMETERS (< 60%):")
        if 'feedback' in result and 'weaknesses' in result['feedback']:
            for weakness in result['feedback']['weaknesses'][:10]:
                param = weakness['parameter']
                pct = weakness['percentage']
                score = weakness['score']
                max_score = weakness.get('max_score', 0)
                print(f"  ✗ {param:20s} {score:5.1f}/{max_score:2d} pts ({pct:5.1f}%)")

        # Check for critical issues
        print("\nCRITICAL ISSUES:")
        critical_found = False

        # Check if keyword matching is working
        keyword_score = result['breakdown'].get('Keyword Matching', {}).get('score', 0)
        keyword_max = result['breakdown'].get('Keyword Matching', {}).get('maxScore', 25)
        if keyword_score == 0:
            print(f"  ✗✗✗ KEYWORD MATCHING: 0/{keyword_max} - NOT WORKING!")
            critical_found = True

        # Check if content quality is too low
        content_score = result['breakdown'].get('Content Quality', {}).get('score', 0)
        content_max = result['breakdown'].get('Content Quality', {}).get('maxScore', 35)
        content_pct = (content_score / content_max * 100) if content_max > 0 else 0
        if content_pct < 50:
            print(f"  ✗✗ CONTENT QUALITY TOO LOW: {content_score}/{content_max} ({content_pct:.1f}%)")
            critical_found = True

        if not critical_found:
            print("  ✓ No critical issues detected")

        return {
            'name': cv_info['name'],
            'actual': overall,
            'target': target,
            'diff': diff,
            'breakdown': result['breakdown']
        }

    except Exception as e:
        print(f"\n✗✗✗ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """Run all CV tests and show summary."""
    print("\n" + "="*80)
    print("ATS SCORER BENCHMARK TEST")
    print("Testing 3 CVs against ResumeWorded scores")
    print("="*80)

    results = []
    for cv_info in TEST_CVS:
        result = test_cv(cv_info)
        if result:
            results.append(result)

    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"{'Name':<20} {'Actual':>8} {'Target':>8} {'Diff':>8} {'Status':>10}")
    print("-"*80)

    for result in results:
        status = '✓ GOOD' if abs(result['diff']) <= 10 else '⚠ OFF' if abs(result['diff']) <= 20 else '✗ BAD'
        print(f"{result['name']:<20} {result['actual']:>8}/100 {result['target']:>8}/100 {result['diff']:>+8} {status:>10}")

    avg_diff = sum(abs(r['diff']) for r in results) / len(results) if results else 0
    print("-"*80)
    print(f"Average difference: {avg_diff:.1f} points")

    if avg_diff <= 10:
        print("\n✓✓✓ EXCELLENT: Scorer matches ResumeWorded within 10 points!")
    elif avg_diff <= 20:
        print("\n⚠⚠ NEEDS TUNING: Scorer is off by 10-20 points on average")
    else:
        print("\n✗✗✗ MAJOR ISSUES: Scorer is off by 20+ points - needs significant fixes")

    print("\n" + "="*80)


if __name__ == '__main__':
    main()
