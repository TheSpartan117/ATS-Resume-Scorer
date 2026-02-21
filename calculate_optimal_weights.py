#!/usr/bin/env python3
"""
Calculate optimal parameter weightages to match ResumeWorded target scores.

Strategy:
1. Score all 3 CVs with current system
2. Get raw percentage scores for each parameter
3. Use optimization to find weights that minimize error vs targets
4. Update registry with new weights
"""
import sys
sys.path.insert(0, '/Users/sabuj.mondal/ats-resume-scorer')

from backend.services.parser import parse_pdf
from backend.services.scorer_v3_adapter import ScorerV3Adapter
from backend.services.parameters.registry import get_parameter_registry
import numpy as np
from scipy.optimize import minimize

# Test CVs with target scores
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

def get_cv_parameter_scores(cv_info):
    """Get raw parameter percentage scores for a CV."""
    print(f"\nScoring: {cv_info['name']}...")

    # Parse CV
    with open(cv_info['path'], 'rb') as f:
        resume_data = parse_pdf(f.read(), cv_info['name'] + '.pdf')

    # Score with adapter
    adapter = ScorerV3Adapter()
    scorer_input = adapter._convert_resume_data(resume_data)

    # Score directly with scorer to get raw results
    result = adapter.scorer.score(
        resume_data=scorer_input,
        job_requirements=None,
        experience_level=cv_info['level'],
        role=cv_info['role']
    )

    # Extract parameter percentages
    param_percentages = {}
    for category_name, category_data in result['category_scores'].items():
        for param_code, param_result in category_data['parameters'].items():
            if param_result.get('status') == 'success':
                param_percentages[param_code] = param_result['percentage'] / 100.0  # 0-1

    return param_percentages, result['raw_score']

def calculate_optimal_weights(cv_scores, targets):
    """
    Calculate optimal parameter weights to match target scores.

    Args:
        cv_scores: List of {param_code: percentage} dicts for each CV
        targets: List of target scores (86, 81, 65)

    Returns:
        Dict of {param_code: optimal_weight}
    """
    # Get all parameter codes
    param_codes = sorted(cv_scores[0].keys())
    n_params = len(param_codes)
    n_cvs = len(cv_scores)

    print(f"\nOptimizing {n_params} parameter weights across {n_cvs} CVs...")
    print(f"Target scores: {targets}")

    # Build percentage matrix (n_cvs x n_params)
    percentage_matrix = np.zeros((n_cvs, n_params))
    for i, scores in enumerate(cv_scores):
        for j, param_code in enumerate(param_codes):
            percentage_matrix[i, j] = scores.get(param_code, 0.0)

    # Objective: minimize sum of squared errors
    def objective(weights):
        predicted = percentage_matrix @ weights
        errors = predicted - np.array(targets)
        return np.sum(errors ** 2)

    # Constraints:
    # 1. All weights positive
    # 2. Total weight = 100
    # 3. Weights reasonable (each between 1-30 pts)
    bounds = [(1, 30) for _ in range(n_params)]
    constraints = [
        {'type': 'eq', 'fun': lambda w: np.sum(w) - 100}
    ]

    # Initial guess: current registry weights
    registry = get_parameter_registry()
    current_weights = []
    for param_code in param_codes:
        param = registry.get_scorer(param_code)
        current_weights.append(param['max_score'])

    x0 = np.array(current_weights)

    # Optimize
    result = minimize(
        objective,
        x0,
        method='SLSQP',
        bounds=bounds,
        constraints=constraints,
        options={'maxiter': 1000}
    )

    if not result.success:
        print(f"Warning: Optimization did not converge: {result.message}")

    # Return optimal weights
    optimal_weights = {}
    for i, param_code in enumerate(param_codes):
        optimal_weights[param_code] = round(result.x[i], 1)

    # Calculate predicted scores with optimal weights
    predicted_scores = percentage_matrix @ result.x
    print(f"\nOptimized scores: {[round(s, 1) for s in predicted_scores]}")
    print(f"Target scores:    {targets}")
    print(f"Errors:           {[round(s - t, 1) for s, t in zip(predicted_scores, targets)]}")

    return optimal_weights

def main():
    print("="*80)
    print("OPTIMAL WEIGHT CALCULATION")
    print("="*80)

    # Get parameter scores for all 3 CVs
    cv_scores = []
    current_scores = []
    targets = []

    for cv_info in TEST_CVS:
        param_percentages, current_score = get_cv_parameter_scores(cv_info)
        cv_scores.append(param_percentages)
        current_scores.append(current_score)
        targets.append(cv_info['target_score'])

    print(f"\nCurrent scores: {[round(s, 1) for s in current_scores]}")
    print(f"Target scores:  {targets}")
    print(f"Gaps:           {[round(c - t, 1) for c, t in zip(current_scores, targets)]}")

    # Calculate optimal weights
    optimal_weights = calculate_optimal_weights(cv_scores, targets)

    # Compare current vs optimal weights
    print("\n" + "="*80)
    print("WEIGHT COMPARISON (Current → Optimal)")
    print("="*80)

    registry = get_parameter_registry()
    total_change = 0
    for param_code in sorted(optimal_weights.keys()):
        param = registry.get_scorer(param_code)
        current = param['max_score']
        optimal = optimal_weights[param_code]
        change = optimal - current
        total_change += abs(change)

        if abs(change) >= 1:
            print(f"{param_code:8s}  {current:5.1f} → {optimal:5.1f}  ({change:+5.1f})")

    print(f"\nTotal weight redistribution: {total_change:.1f} points")

    # Save optimal weights to file
    output_file = '/Users/sabuj.mondal/ats-resume-scorer/optimal_weights.json'
    import json
    with open(output_file, 'w') as f:
        json.dump(optimal_weights, f, indent=2)

    print(f"\n✓ Optimal weights saved to: {output_file}")
    print("\nNext: Update registry.py with these weights and restart backend")

if __name__ == '__main__':
    main()
