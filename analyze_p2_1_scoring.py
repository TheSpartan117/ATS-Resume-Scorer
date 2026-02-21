#!/usr/bin/env python3
"""Analyze P2.1 Action Verbs scoring breakdown."""
import sys
sys.path.insert(0, '/Users/sabuj.mondal/ats-resume-scorer')

from backend.services.parser import parse_pdf
from backend.services.scorer_v3 import ScorerV3
from backend.services.scorer_v3_adapter import ScorerV3Adapter

# Test CVs
TEST_CVS = [
    {
        'name': 'Sabuj Mondal',
        'path': '/Users/sabuj.mondal/Downloads/Sabuj_Mondal_PM_CV.pdf',
        'role': 'product_manager',
        'level': 'senior',
    },
    {
        'name': 'Aishik Das',
        'path': '/Users/sabuj.mondal/Downloads/AISHIK DAS_CV_v2.pdf',
        'role': 'product_manager',
        'level': 'mid',
    },
    {
        'name': 'Swastik Paul',
        'path': '/Users/sabuj.mondal/Downloads/SWASTIK PAUL_CV_DIG_TRSFN STGY_PM-2.pdf',
        'role': 'product_manager',
        'level': 'mid',
    }
]

def analyze_cv_p2_1(cv_info):
    """Analyze P2.1 scoring for a CV."""
    with open(cv_info['path'], 'rb') as f:
        resume_data = parse_pdf(f.read(), cv_info['name'] + '.pdf')

    # Use adapter to convert and score
    adapter = ScorerV3Adapter()
    scorer_input = adapter._convert_resume_data(resume_data)

    # Create scorer and score directly
    scorer = ScorerV3()
    result = scorer.score(
        resume_data=scorer_input,
        job_requirements=None,
        experience_level=cv_info['level'],
        role=cv_info['role']
    )

    # Get P2.1 details
    p2_1 = result['parameter_scores'].get('P2.1', {})

    print(f"\n{'='*70}")
    print(f"{cv_info['name']} - P2.1 Analysis")
    print(f"{'='*70}")
    print(f"Score: {p2_1.get('score', 0):.1f}/15 ({p2_1.get('score', 0)/15*100:.0f}%)")

    details = p2_1.get('details', {})
    print(f"\nTotal Bullets: {details.get('total_bullets', 0)}")
    print(f"Coverage: {details.get('coverage_percentage', 0):.1f}%")
    print(f"Average Tier: {details.get('average_tier', 0):.2f}")

    # Count bullets by tier
    bullet_details = details.get('bullet_details', [])
    tier_counts = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0}
    for bullet in bullet_details:
        tier_counts[bullet['tier']] += 1

    print(f"\nTier Distribution:")
    tier_points = {4: 1.0, 3: 0.8, 2: 0.6, 1: 0.4, 0: 0.0}
    for tier in [4, 3, 2, 1, 0]:
        count = tier_counts[tier]
        points_per = tier_points[tier]
        total_pts = count * points_per
        print(f"  Tier {tier}: {count:2d} bullets × {points_per} = {total_pts:5.1f} points")

    # Show some example bullets per tier
    print(f"\nSample Bullets by Tier:")
    for tier in [4, 3, 2, 1, 0]:
        examples = [b for b in bullet_details if b['tier'] == tier][:2]
        if examples:
            print(f"\n  Tier {tier} ({tier_points[tier]} pts each):")
            for ex in examples:
                text = ex['text'][:80] + '...' if len(ex['text']) > 80 else ex['text']
                print(f"    - {text}")

# Analyze all CVs
for cv_info in TEST_CVS:
    try:
        analyze_cv_p2_1(cv_info)
    except Exception as e:
        print(f"\n✗ {cv_info['name']}: {e}")
        import traceback
        traceback.print_exc()
