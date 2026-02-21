#!/usr/bin/env python3
"""
Calibrate Scorer V3 weightages based on benchmark CVs.

Target scores (from ResumeWorded):
- Sabuj CV: 86 points
- Swastik CV: 65 points
- Aishik CV: 81 points

Strategy:
1. Score all 3 CVs with current system
2. Get raw parameter percentages (0-100%) for each
3. Use linear optimization to find weightages that match targets
4. Update parameter max scores in registry
"""

import sys
from pathlib import Path
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.services.parser import parse_docx, parse_pdf
from backend.services.scorer_v3 import ScorerV3
from backend.services.scorer_v3_adapter import ScorerV3Adapter

# Benchmark CVs with target scores
BENCHMARKS = [
    {
        'name': 'Sabuj',
        'file': 'data/Sabuj_Mondal_PM_CV_1771577761468.docx',
        'target_score': 86,
        'level': 'senior'
    },
    {
        'name': 'Swastik',
        'file': 'data/SWASTIK PAUL_CV_DIG_TRSFN STGY_PM-2_1771620946020.docx',
        'target_score': 65,
        'level': 'intermediary'
    },
    # Aishik CV to be added if found
]

def score_benchmark_cv(cv_info):
    """Score a benchmark CV and return detailed results."""
    print(f"\n{'='*60}")
    print(f"Scoring: {cv_info['name']} CV")
    print(f"Target Score: {cv_info['target_score']}/100")
    print(f"{'='*60}")

    # Load CV
    file_path = Path(__file__).parent / cv_info['file']
    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        return None

    # Parse based on extension
    with open(file_path, 'rb') as f:
        file_content = f.read()

    if str(file_path).endswith('.pdf'):
        resume_data = parse_pdf(file_content, file_path.name)
    else:
        resume_data = parse_docx(file_content, file_path.name)

    # Convert to Scorer V3 format
    adapter = ScorerV3Adapter()
    scorer_input = adapter._convert_resume_data(resume_data)

    # Score (no job description)
    scorer = ScorerV3()
    result = scorer.score(
        resume_data=scorer_input,
        job_requirements=None,
        experience_level=cv_info['level']
    )

    # Display results
    print(f"\n📊 Current Score: {result['total_score']:.1f}/100")
    print(f"   Target Score: {cv_info['target_score']}/100")
    print(f"   Gap: {cv_info['target_score'] - result['total_score']:.1f} points")
    print(f"   Rating: {result['rating']}")

    print(f"\n📋 Category Breakdown:")
    for category, data in result['category_scores'].items():
        pct = (data['score'] / data['max'] * 100) if data['max'] > 0 else 0
        print(f"   {category:25s}: {data['score']:4.1f}/{data['max']:2d} ({pct:5.1f}%)")

    print(f"\n🔍 Parameter Details:")
    param_scores = {}
    for code, param in result['parameter_scores'].items():
        status = param.get('status', 'unknown')
        if status == 'success':
            pct = param.get('percentage', 0)
            score = param.get('score', 0)
            max_score = param.get('max_score', 0)
            param_scores[code] = {
                'percentage': pct,
                'score': score,
                'max_score': max_score
            }
            print(f"   {code}: {score:.1f}/{max_score} ({pct:.1f}%)")
        elif status == 'skipped':
            param_scores[code] = {
                'percentage': 0,
                'score': 0,
                'max_score': param.get('max_score', 0),
                'skipped': True
            }
            print(f"   {code}: SKIPPED (no job description)")

    return {
        'name': cv_info['name'],
        'target_score': cv_info['target_score'],
        'current_score': result['total_score'],
        'gap': cv_info['target_score'] - result['total_score'],
        'parameter_scores': param_scores,
        'category_scores': result['category_scores']
    }

def calculate_optimal_weightages(benchmark_results):
    """Calculate optimal parameter weightages to match target scores."""
    print(f"\n{'='*60}")
    print("CALCULATING OPTIMAL WEIGHTAGES")
    print(f"{'='*60}")

    # Collect parameter percentages for each benchmark
    # percentages[param_code] = [sabuj_pct, swastik_pct, aishik_pct]
    all_params = set()
    for result in benchmark_results:
        all_params.update(result['parameter_scores'].keys())

    # Build data matrix: each row is a CV, each column is a parameter
    print(f"\n📊 Parameter Performance Matrix:")
    print(f"{'Parameter':<8} | {'Sabuj':<8} | {'Swastik':<8} | {'Aishik':<8}")
    print(f"{'-'*50}")

    param_data = {}
    for param in sorted(all_params):
        percentages = []
        for result in benchmark_results:
            param_info = result['parameter_scores'].get(param, {})
            if param_info.get('skipped'):
                pct = None  # Skip this parameter for this CV
            else:
                pct = param_info.get('percentage', 0)
            percentages.append(pct)

        param_data[param] = percentages

        # Display
        pct_strs = []
        for pct in percentages:
            if pct is None:
                pct_strs.append('SKIP')
            else:
                pct_strs.append(f"{pct:.1f}%")

        print(f"{param:<8} | {pct_strs[0]:<8} | {pct_strs[1]:<8} | {pct_strs[2] if len(pct_strs) > 2 else 'N/A':<8}")

    # Simple heuristic: Scale weightages proportionally to close the gap
    print(f"\n🎯 Calculating Weightage Adjustments:")

    # Current total available points (without P1.1, P1.2)
    # 100 - 35 (keyword matching) = 65 available
    current_available = 90  # As per normalization

    # For each CV, calculate scaling factor needed
    scaling_factors = []
    for result in benchmark_results:
        target = result['target_score']
        current = result['current_score']
        # Factor to scale current score to target
        if current > 0:
            factor = target / current
        else:
            factor = 1.0
        scaling_factors.append(factor)
        print(f"   {result['name']}: {current:.1f} → {target} (factor: {factor:.2f}x)")

    # Average scaling factor
    avg_factor = sum(scaling_factors) / len(scaling_factors)
    print(f"\n   Average scaling factor: {avg_factor:.2f}x")

    # Calculate new weightages
    from backend.services.parameters.registry import get_parameter_registry
    registry = get_parameter_registry()
    all_params_info = registry.get_all_scorers()

    print(f"\n📝 Recommended Weightage Changes:")
    print(f"{'Parameter':<8} | {'Current':<8} | {'New':<8} | {'Change':<8}")
    print(f"{'-'*50}")

    new_weightages = {}
    for code, param_info in sorted(all_params_info.items()):
        current_max = param_info['max_score']

        # Skip keyword matching parameters (P1.1, P1.2) - they're conditional
        if code in ['P1.1', 'P1.2']:
            new_max = current_max
        else:
            # Scale by average factor
            new_max = round(current_max * avg_factor, 1)
            # Don't go below 1 or above 50
            new_max = max(1, min(50, new_max))

        new_weightages[code] = new_max
        change = new_max - current_max
        print(f"{code:<8} | {current_max:<8.1f} | {new_max:<8.1f} | {change:+.1f}")

    # Calculate new category totals
    print(f"\n📊 New Category Totals:")
    category_totals = {}
    for code, new_max in new_weightages.items():
        category = all_params_info[code]['category']
        category_totals[category] = category_totals.get(category, 0) + new_max

    for category, total in sorted(category_totals.items()):
        print(f"   {category:30s}: {total:.1f} pts")

    total_points = sum(category_totals.values())
    print(f"\n   {'TOTAL POINTS':<30s}: {total_points:.1f} pts")

    return new_weightages, category_totals

def main():
    """Main calibration process."""
    print("🎯 Scorer V3 Weightage Calibration")
    print("=" * 60)

    # Score all benchmark CVs
    benchmark_results = []
    for cv_info in BENCHMARKS:
        result = score_benchmark_cv(cv_info)
        if result:
            benchmark_results.append(result)

    if len(benchmark_results) < 2:
        print("\n❌ Need at least 2 benchmark CVs scored successfully")
        return

    # Calculate optimal weightages
    new_weightages, category_totals = calculate_optimal_weightages(benchmark_results)

    # Save recommendations
    output_file = Path(__file__).parent / 'calibration_results.json'
    output = {
        'benchmark_results': [
            {
                'name': r['name'],
                'target_score': r['target_score'],
                'current_score': r['current_score'],
                'gap': r['gap']
            }
            for r in benchmark_results
        ],
        'new_weightages': new_weightages,
        'category_totals': category_totals
    }

    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\n✅ Calibration complete!")
    print(f"   Results saved to: {output_file}")
    print(f"\n📝 Next steps:")
    print(f"   1. Review the recommended weightages above")
    print(f"   2. Apply changes to parameter registry")
    print(f"   3. Test with all 3 CVs to verify target scores")

if __name__ == '__main__':
    main()
