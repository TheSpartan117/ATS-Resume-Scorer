#!/usr/bin/env python3
"""
Direct test of scorer_v3 to see raw parameter scores.
"""
import sys
sys.path.insert(0, '/Users/sabuj.mondal/ats-resume-scorer')

from backend.services.parser import parse_pdf
from backend.services.scorer_v3_adapter import ScorerV3Adapter

CV_PATH = '/Users/sabuj.mondal/Downloads/Sabuj_Mondal_PM_CV.pdf'

def main():
    print("\n" + "="*80)
    print("DIRECT SCORER V3 TEST: Sabuj Mondal CV")
    print("="*80)

    # Parse CV
    with open(CV_PATH, 'rb') as f:
        resume_data = parse_pdf(f.read(), 'Sabuj_Mondal_PM_CV.pdf')

    print(f"\n✓ Parsed: {resume_data.metadata.get('wordCount', 0)} words")

    # Score with adapter and access internal result
    adapter = ScorerV3Adapter()

    # Get scorer input
    scorer_input = adapter._convert_resume_data(resume_data)

    # Score directly
    result = adapter.scorer.score(
        resume_data=scorer_input,
        job_requirements=None,
        experience_level='senior',
        role='product_manager'
    )

    # Show overall
    print(f"\nRAW SCORE: {result['raw_score']}/100")
    print(f"NORMALIZED SCORE: {result['total_score']}/100")

    # Show category scores
    print("\n" + "-"*80)
    print("CATEGORY SCORES:")
    print("-"*80)
    for category_name, category_data in result['category_scores'].items():
        score = category_data['score']
        max_score = category_data['max']
        pct = (score / max_score * 100) if max_score > 0 else 0
        print(f"{category_name:25s} {score:6.2f}/{max_score:2d} pts ({pct:5.1f}%)")

    # Show ALL parameter scores
    print("\n" + "="*80)
    print("ALL PARAMETER SCORES:")
    print("="*80)

    for category_name, category_data in result['category_scores'].items():
        print(f"\n{category_name.upper()}:")
        for param_code, param_result in category_data['parameters'].items():
            if param_result.get('status') == 'success':
                score = param_result['score']
                max_score = param_result['max_score']
                pct = param_result['percentage']
                status = '✓' if pct >= 70 else '⚠' if pct >= 40 else '✗'
                print(f"  {status} {param_code:8s} {score:6.2f}/{max_score:2d} pts ({pct:5.1f}%)")

                # Show details for Content Quality params
                if param_code.startswith('P2.'):
                    details = param_result.get('details', {})
                    if param_code == 'P2.1':
                        coverage = details.get('coverage_percentage', 0)
                        avg_tier = details.get('average_tier', 0)
                        total = details.get('total_bullets', 0)
                        verbs = details.get('bullets_with_verbs', 0)
                        print(f"       Coverage: {coverage:.1f}% ({verbs}/{total} bullets) | Avg Tier: {avg_tier:.2f}")
                    elif param_code == 'P2.2':
                        wqr = details.get('weighted_quantification_rate', 0)
                        quant_count = details.get('quantified_count', 0)
                        total = details.get('total_bullets', 0)
                        high = details.get('high_count', 0)
                        med = details.get('medium_count', 0)
                        low = details.get('low_count', 0)
                        print(f"       Weighted Rate: {wqr:.1f}% | Quantified: {quant_count}/{total} (H:{high}, M:{med}, L:{low})")
                    elif param_code == 'P2.4':
                        car_pct = details.get('car_percentage', 0)
                        car_count = details.get('car_count', 0)
                        total = details.get('total_bullets', 0)
                        print(f"       CAR %: {car_pct:.1f}% | CAR Count: {car_count}/{total}")
            elif param_result.get('status') == 'error':
                print(f"  ✗ {param_code:8s} ERROR: {param_result.get('error', 'Unknown error')}")

    print("\n" + "="*80)

if __name__ == '__main__':
    main()
