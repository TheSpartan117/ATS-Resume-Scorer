#!/usr/bin/env python3
"""Debug specific scoring issues."""
import sys
sys.path.insert(0, '/Users/sabuj.mondal/ats-resume-scorer')
import json

from backend.services.parser import parse_pdf
from backend.services.scorer_v3 import ScorerV3
from backend.services.scorer_v3_adapter import ScorerV3Adapter

# Test Sabuj's CV
cv_path = '/Users/sabuj.mondal/Downloads/Sabuj_Mondal_PM_CV.pdf'

with open(cv_path, 'rb') as f:
    resume_data = parse_pdf(f.read(), 'Sabuj_Mondal_PM_CV.pdf')

adapter = ScorerV3Adapter()
scorer_input = adapter._convert_resume_data(resume_data)
scorer = ScorerV3()

result = scorer.score(
    resume_data=scorer_input,
    job_requirements=None,
    experience_level='senior',
    role='product_manager'
)

print("="*80)
print("ISSUE 1: Required Keywords (P1.1) - Why all same?")
print("="*80)
p1_1 = result['parameter_scores'].get('P1.1', {})
print(f"Status: {p1_1.get('status')}")
print(f"Score: {p1_1.get('score')}/{p1_1.get('max')}")
if 'details' in p1_1:
    details = p1_1['details']
    print(f"Matched: {len(details.get('matched', []))} keywords")
    print(f"  {details.get('matched', [])}")
    print(f"Missing: {len(details.get('missing', []))} keywords")
    print(f"  {details.get('missing', [])[:10]}")  # Show first 10
    print(f"Total keywords checked: {len(details.get('matched', [])) + len(details.get('missing', []))}")

print("\n" + "="*80)
print("ISSUE 2: Quantification (P2.2) - Why only 4/10 for Sabuj?")
print("="*80)
p2_2 = result['parameter_scores'].get('P2.2', {})
print(f"Status: {p2_2.get('status')}")
print(f"Score: {p2_2.get('score')}/{p2_2.get('max')}")
if 'details' in p2_2:
    details = p2_2['details']
    print(f"Details: {json.dumps(details, indent=2)}")

print("\n" + "="*80)
print("ISSUE 3: Page Count (P3.1) - Current scoring")
print("="*80)
p3_1 = result['parameter_scores'].get('P3.1', {})
print(f"Status: {p3_1.get('status')}")
print(f"Score: {p3_1.get('score')}/{p3_1.get('max')}")
print(f"Page count: {scorer_input.get('page_count')}")
if 'details' in p3_1:
    print(f"Details: {json.dumps(p3_1['details'], indent=2)}")

print("\n" + "="*80)
print("ISSUE 4: Grammar (P4.1) - Is it checking?")
print("="*80)
p4_1 = result['parameter_scores'].get('P4.1', {})
print(f"Status: {p4_1.get('status')}")
print(f"Score: {p4_1.get('score')}/{p4_1.get('max')}")
if 'details' in p4_1:
    details = p4_1['details']
    print(f"Error count: {details.get('error_count', 0)}")
    print(f"Details: {json.dumps(details, indent=2)}")

print("\n" + "="*80)
print("ISSUE 5: Readability (P7.1) - Why only 1/5?")
print("="*80)
p7_1 = result['parameter_scores'].get('P7.1', {})
print(f"Status: {p7_1.get('status')}")
print(f"Score: {p7_1.get('score')}/{p7_1.get('max')}")
if 'details' in p7_1:
    print(f"Details: {json.dumps(p7_1['details'], indent=2)}")

print("\n" + "="*80)
print("ISSUE 6: Bullet Structure (P7.2) - Why 0/3?")
print("="*80)
p7_2 = result['parameter_scores'].get('P7.2', {})
print(f"Status: {p7_2.get('status')}")
print(f"Score: {p7_2.get('score')}/{p7_2.get('max')}")
if 'details' in p7_2:
    print(f"Details: {json.dumps(p7_2['details'], indent=2)}")
print(f"Bullets in resume: {len(scorer_input.get('bullets', []))}")
if scorer_input.get('bullets'):
    print(f"First 3 bullets:")
    for bullet in scorer_input['bullets'][:3]:
        print(f"  - {bullet[:80]}...")
