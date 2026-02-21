#!/usr/bin/env python3
"""Test role keyword loading."""
import sys
sys.path.insert(0, '/Users/sabuj.mondal/ats-resume-scorer')

from backend.services.role_keywords import get_role_keywords

# Test getting product_manager keywords
keywords = get_role_keywords('product_manager')

print("="*80)
print("Role: product_manager")
print("="*80)
print(f"Required keywords ({len(keywords['required'])}): {keywords['required']}")
print(f"\nPreferred keywords ({len(keywords['preferred'])}): {keywords['preferred']}")

# Now test if scorer is actually using them
from backend.services.scorer_v3 import ScorerV3
from backend.services.parser import parse_pdf
from backend.services.scorer_v3_adapter import ScorerV3Adapter

cv_path = '/Users/sabuj.mondal/Downloads/Sabuj_Mondal_PM_CV.pdf'

with open(cv_path, 'rb') as f:
    resume_data = parse_pdf(f.read(), 'Sabuj_Mondal_PM_CV.pdf')

adapter = ScorerV3Adapter()
scorer_input = adapter._convert_resume_data(resume_data)

# Add debug to scorer_v3
print("\n" + "="*80)
print("Testing ScorerV3 with role='product_manager'")
print("="*80)

scorer = ScorerV3()

# Patch the score method to see what's being passed
original_score_param = scorer._score_parameter

def debug_score_parameter(code, param_info, resume_data, job_requirements, experience_level, role):
    print(f"\n_score_parameter called for {code}")
    print(f"  role={role}")
    print(f"  job_requirements={job_requirements}")

    if code == 'P1.1':
        # Check if keywords are loaded
        if not job_requirements or 'required_keywords' not in job_requirements:
            from backend.services.role_keywords import get_role_keywords
            role_keywords = get_role_keywords(role)
            print(f"  Loaded {len(role_keywords['required'])} required keywords for role={role}")
            print(f"  Keywords: {role_keywords['required'][:5]}...")
        else:
            print(f"  Using JD keywords: {len(job_requirements['required_keywords'])}")

    return original_score_param(code, param_info, resume_data, job_requirements, experience_level, role)

scorer._score_parameter = debug_score_parameter

result = scorer.score(
    resume_data=scorer_input,
    job_requirements=None,
    experience_level='senior',
    role='product_manager'
)

print(f"\nP1.1 Result:")
p1_1 = result['parameter_scores']['P1.1']
print(f"  Score: {p1_1['score']}")
print(f"  Details: {p1_1.get('details', {})}")
