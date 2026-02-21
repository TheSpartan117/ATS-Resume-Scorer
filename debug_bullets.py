#!/usr/bin/env python3
"""Debug script to see what bullets are extracted and how they're classified."""
import sys
sys.path.insert(0, '/Users/sabuj.mondal/ats-resume-scorer')

from backend.services.parser import parse_pdf
from backend.services.scorer_v3_adapter import ScorerV3Adapter
from backend.services.action_verb_classifier import ActionVerbClassifier

CV_PATH = '/Users/sabuj.mondal/Downloads/Sabuj_Mondal_PM_CV.pdf'

def main():
    print("\n" + "="*80)
    print("BULLET DEBUG: Sabuj Mondal CV")
    print("="*80)

    # Parse CV
    with open(CV_PATH, 'rb') as f:
        resume_data = parse_pdf(f.read(), 'Sabuj_Mondal_PM_CV.pdf')

    # Get bullets via adapter
    adapter = ScorerV3Adapter()
    scorer_input = adapter._convert_resume_data(resume_data)

    bullets = scorer_input.get('bullets', [])
    print(f"\nTotal bullets extracted: {len(bullets)}")

    # Classify each bullet
    classifier = ActionVerbClassifier()

    print("\n" + "-"*80)
    print("BULLET CLASSIFICATION:")
    print("-"*80)

    for i, bullet in enumerate(bullets, 1):
        tier = classifier.classify_bullet(bullet)
        tier_points = tier.points
        has_verb = tier_points > 0

        status = '✓' if has_verb else '✗'
        print(f"\n{status} #{i} (Tier {tier_points}):")
        print(f"   {bullet[:100]}...")  # First 100 chars

    # Summary
    verbs_found = sum(1 for b in bullets if classifier.classify_bullet(b).points > 0)
    coverage = (verbs_found / len(bullets) * 100) if bullets else 0

    print("\n" + "="*80)
    print(f"SUMMARY: {verbs_found}/{len(bullets)} bullets with action verbs ({coverage:.1f}%)")
    print("="*80)

if __name__ == '__main__':
    main()
