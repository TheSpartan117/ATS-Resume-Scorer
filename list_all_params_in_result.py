#!/usr/bin/env python3
"""List all parameters found in a result."""
import sys
sys.path.insert(0, '/Users/sabuj.mondal/ats-resume-scorer')

from backend.services.parser import parse_pdf
from backend.services.scorer_v3_adapter import ScorerV3Adapter

cv_path = '/Users/sabuj.mondal/Downloads/Sabuj_Mondal_PM_CV.pdf'

with open(cv_path, 'rb') as f:
    resume_data = parse_pdf(f.read(), 'Sabuj_Mondal_PM_CV.pdf')

adapter = ScorerV3Adapter()
result = adapter.score(
    resume_data=resume_data,
    job_description=None,
    level='senior',
    role='product_manager'
)

print("="*80)
print("ALL PARAMETERS IN WEAKNESSES:")
print("="*80)
for weak in result['feedback']['weaknesses']:
    print(f"  {weak['code']:6s} {weak['parameter']:30s} {weak['score']:5.1f}")

print("\n" + "="*80)
print("ALL PARAMETERS IN STRENGTHS:")
print("="*80)
for strength in result['feedback']['strengths']:
    print(f"  {strength['code']:6s} {strength['parameter']:30s} {strength['score']:5.1f}")

print(f"\nTotal: {len(result['feedback']['weaknesses'])} weaknesses + {len(result['feedback']['strengths'])} strengths")
