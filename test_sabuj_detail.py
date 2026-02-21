#!/usr/bin/env python3
"""
Detailed test of Sabuj's CV to debug Content Quality scoring.
"""
import sys
sys.path.insert(0, '/Users/sabuj.mondal/ats-resume-scorer')

from backend.services.parser import parse_pdf
from backend.services.scorer_v3_adapter import ScorerV3Adapter

CV_PATH = '/Users/sabuj.mondal/Downloads/Sabuj_Mondal_PM_CV.pdf'

def main():
    print("\n" + "="*80)
    print("DETAILED TEST: Sabuj Mondal CV")
    print("="*80)

    # Parse CV
    with open(CV_PATH, 'rb') as f:
        resume_data = parse_pdf(f.read(), 'Sabuj_Mondal_PM_CV.pdf')

    print(f"\n✓ Parsed: {resume_data.metadata.get('wordCount', 0)} words")

    # Score with adapter
    adapter = ScorerV3Adapter()
    result = adapter.score(
        resume_data=resume_data,
        job_description=None,
        level='senior',
        role='product_manager'
    )

    # Show overall
    print(f"\nOVERALL SCORE: {result['overallScore']}/100 (Target: 86)")

    # Show all categories
    print("\n" + "-"*80)
    print("CATEGORY BREAKDOWN:")
    print("-"*80)
    for category, details in result['breakdown'].items():
        score = details['score']
        max_score = details['maxScore']
        pct = (score / max_score * 100) if max_score > 0 else 0
        print(f"{category:25s} {score:6.2f}/{max_score:2d} pts ({pct:5.1f}%)")

    # Show weaknesses (low-scoring parameters)
    print("\n" + "-"*80)
    print("LOW-SCORING PARAMETERS (Weaknesses):")
    print("-"*80)

    if 'feedback' in result and 'weaknesses' in result['feedback']:
        for weakness in result['feedback']['weaknesses']:
            param = weakness['parameter']
            score = weakness['score']
            max_score = weakness.get('max_score', 0)
            pct = weakness['percentage']
            status = '✓' if pct >= 70 else '⚠' if pct >= 40 else '✗'
            print(f"{status} {param:30s} {score:6.2f}/{max_score:2d} pts ({pct:5.1f}%)")

    # Show Content Quality parameters in detail
    print("\n" + "="*80)
    print("CONTENT QUALITY BREAKDOWN (P2.X):")
    print("="*80)

    content_quality_params = ['P2.1', 'P2.2', 'P2.3', 'P2.4', 'P2.5']

    # Find Content Quality category in result
    # The scorer returns raw scoring data, we need to access it via API adapter's internal call
    # For now, let's just show what we can from weaknesses

    print("\nShowing Content Quality params from weaknesses list:")
    if 'feedback' in result and 'weaknesses' in result['feedback']:
        content_weaknesses = [w for w in result['feedback']['weaknesses']
                             if any(w['parameter'].startswith(p) for p in content_quality_params)]

        total_cq_score = 0
        total_cq_max = 0

        for weakness in content_weaknesses:
            param = weakness['parameter']
            score = weakness['score']
            max_score = weakness.get('max_score', 0)
            pct = weakness['percentage']

            total_cq_score += score
            total_cq_max += max_score

            status = '✓' if pct >= 70 else '⚠' if pct >= 40 else '✗'
            print(f"{status} {param:40s} {score:6.2f}/{max_score:2d} pts ({pct:5.1f}%)")

        if total_cq_max > 0:
            print(f"\n{'TOTAL FROM WEAKNESSES':40s} {total_cq_score:6.2f}/{total_cq_max:2d} pts ({total_cq_score/total_cq_max*100:.1f}%)")

    print("\n" + "="*80)

if __name__ == '__main__':
    main()
