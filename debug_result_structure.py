#!/usr/bin/env python3
"""Debug to see the result structure."""
import sys
sys.path.insert(0, '/Users/sabuj.mondal/ats-resume-scorer')
import json

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

print("Result keys:", result.keys())

print("\n" + "="*80)
print("feedback.category_breakdown structure:")
print("="*80)

if 'feedback' in result and 'category_breakdown' in result['feedback']:
    cat_breakdown = result['feedback']['category_breakdown']
    print("Category breakdown keys:", cat_breakdown.keys() if hasattr(cat_breakdown, 'keys') else type(cat_breakdown))

    if isinstance(cat_breakdown, dict):
        first_cat = list(cat_breakdown.keys())[0]
        print(f"\nFirst category: {first_cat}")
        cat_data = cat_breakdown[first_cat]
        print(f"  Type: {type(cat_data)}")
        if isinstance(cat_data, dict):
            print(f"  Keys: {cat_data.keys()}")
            if 'parameters' in cat_data:
                print(f"  First parameter:")
                param = cat_data['parameters'][0]
                print(f"    {json.dumps(param, indent=6)}")

print("\n" + "="*80)
print("Full result.feedback.weaknesses[0]:")
print("="*80)
if 'feedback' in result and 'weaknesses' in result['feedback']:
    print(json.dumps(result['feedback']['weaknesses'][0], indent=2))
