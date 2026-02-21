#!/usr/bin/env python3
"""
Calibrate Scorer V3 weightages via API (handles file type detection automatically).
"""

import requests
import json
from pathlib import Path

API_URL = "http://localhost:8000/api/upload"

# Benchmark CVs with target scores (from ResumeWorded)
BENCHMARKS = [
    {
        'name': 'Sabuj',
        'file': 'data/Sabuj_Mondal_PM_CV_1771577761468.docx',  # Actually PDF
        'target_score': 86,
        'level': 'senior'
    },
    {
        'name': 'Swastik',
        'file': 'data/SWASTIK PAUL_CV_DIG_TRSFN STGY_PM-2_1771620946020.docx',
        'target_score': 65,
        'level': 'intermediary'
    },
    # Aishik - User to provide file path
]

def score_via_api(cv_info):
    """Score a CV via API and return results."""
    print(f"\n{'='*70}")
    print(f"Scoring: {cv_info['name']} CV (Target: {cv_info['target_score']}/100)")
    print(f"{'='*70}")

    file_path = Path(__file__).parent / cv_info['file']
    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        return None

    # Upload via API
    with open(file_path, 'rb') as f:
        files = {'file': (file_path.name, f)}
        data = {
            'level': cv_info['level'],
            'mode': 'quality_coach'
        }

        response = requests.post(API_URL, files=files, data=data)

    if response.status_code != 200:
        print(f"❌ API Error: {response.text}")
        return None

    result = response.json()
    score_data = result['score']

    current_score = score_data['overallScore']
    breakdown = score_data['breakdown']

    print(f"\n📊 SCORE: {current_score}/100 (Target: {cv_info['target_score']})")
    print(f"   Gap: {cv_info['target_score'] - current_score:+.0f} points")
    print(f"   Rating: {score_data.get('rating', 'N/A')}")

    print(f"\n📋 Category Breakdown:")
    for category, data in breakdown.items():
        score = data['score']
        max_score = data['maxScore']
        pct = (score / max_score * 100) if max_score > 0 else 0
        print(f"   {category:30s}: {score:5.1f}/{max_score:3d} ({pct:5.1f}%)")

    return {
        'name': cv_info['name'],
        'target_score': cv_info['target_score'],
        'current_score': current_score,
        'gap': cv_info['target_score'] - current_score,
        'breakdown': breakdown
    }

def calculate_weightage_adjustments(benchmark_results):
    """Calculate how to adjust weightages to match targets."""
    print(f"\n{'='*70}")
    print("CALCULATING WEIGHTAGE ADJUSTMENTS")
    print(f"{'='*70}")

    # Calculate scaling factors for each CV
    print(f"\n🎯 Required Scaling Factors:")
    scaling_factors = []
    for result in benchmark_results:
        target = result['target_score']
        current = result['current_score']
        if current > 0:
            factor = target / current
        else:
            factor = 1.0
        scaling_factors.append(factor)
        print(f"   {result['name']:10s}: {current:5.1f} → {target:3d} (×{factor:.3f})")

    avg_factor = sum(scaling_factors) / len(scaling_factors)
    print(f"\n   Average scaling: ×{avg_factor:.3f}")

    # Show category performance
    print(f"\n📊 Category Performance Across CVs:")
    all_categories = set()
    for result in benchmark_results:
        all_categories.update(result['breakdown'].keys())

    print(f"\n{'Category':<30s} | {'Current Max':<12s} | {'Suggested New':<12s}")
    print(f"{'-'*70}")

    category_adjustments = {}
    for category in sorted(all_categories):
        # Get average max score across CVs
        max_scores = []
        for result in benchmark_results:
            if category in result['breakdown']:
                max_scores.append(result['breakdown'][category]['maxScore'])

        if max_scores:
            current_max = max(max_scores)  # Use the actual max
            new_max = round(current_max * avg_factor, 1)
            # Cap between 5 and 50
            new_max = max(5, min(50, new_max))
            category_adjustments[category] = {
                'current': current_max,
                'new': new_max,
                'change': new_max - current_max
            }

            print(f"{category:<30s} | {current_max:12.1f} | {new_max:12.1f} ({new_max - current_max:+.1f})")

    total_current = sum(adj['current'] for adj in category_adjustments.values())
    total_new = sum(adj['new'] for adj in category_adjustments.values())

    print(f"\n{'TOTAL (without job description)':<30s} | {total_current:12.1f} | {total_new:12.1f} ({total_new - total_current:+.1f})")

    return category_adjustments, avg_factor

def main():
    """Main calibration process."""
    print("🎯 Scorer V3 Weightage Calibration")
    print("=" * 70)
    print("\nBenchmark CVs (from ResumeWorded):")
    for cv in BENCHMARKS:
        print(f"   • {cv['name']}: Target {cv['target_score']}/100")

    # Score all benchmark CVs
    benchmark_results = []
    for cv_info in BENCHMARKS:
        result = score_via_api(cv_info)
        if result:
            benchmark_results.append(result)

    if len(benchmark_results) < 2:
        print("\n❌ Need at least 2 CVs scored successfully")
        return

    # Calculate adjustments
    category_adjustments, avg_factor = calculate_weightage_adjustments(benchmark_results)

    # Save results
    output = {
        'benchmarks': benchmark_results,
        'scaling_factor': avg_factor,
        'category_adjustments': category_adjustments
    }

    output_file = Path(__file__).parent / 'calibration_results.json'
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\n✅ Calibration complete!")
    print(f"   Results saved to: {output_file}")
    print(f"\n💡 Recommendation: Scale all parameter weights by {avg_factor:.3f}×")
    print(f"   This will bring scores to match ResumeWorded benchmarks.")

if __name__ == '__main__':
    main()
