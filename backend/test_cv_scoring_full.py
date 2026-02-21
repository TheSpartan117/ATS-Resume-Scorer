#!/usr/bin/env python3
"""
Full CV scoring test with proper parsing.
"""

from backend.services.parser import parse_docx
from backend.services.scorer_v2 import AdaptiveScorer
from backend.services.role_taxonomy import get_role_scoring_data_enhanced
import json

def test_cv(cv_path, cv_name):
    """Test a single CV with full scoring"""
    print(f"\n{'='*80}")
    print(f"TESTING: {cv_name}")
    print(f"{'='*80}\n")

    # Read and parse CV
    with open(cv_path, 'rb') as f:
        file_content = f.read()

    resume_data = parse_docx(file_content, cv_name)

    print(f"Parsed Resume Data:")
    print(f"  Name: {resume_data.contact.get('name', 'N/A')}")
    print(f"  Email: {resume_data.contact.get('email', 'N/A')}")
    print(f"  Experience items: {len(resume_data.experience)}")
    print(f"  Education items: {len(resume_data.education)}")
    print(f"  Skills: {len(resume_data.skills)}")

    # Get role data
    role_data = get_role_scoring_data_enhanced('product_manager', 'mid')
    print(f"\nRole Data:")
    print(f"  Keywords: {len(role_data.get('keywords', []))}")
    print(f"  Typical Keywords: {len(role_data.get('typical_keywords', []))}")
    print(f"  Action Verbs: {len(role_data.get('action_verbs', []))}")

    # Score the resume
    scorer = AdaptiveScorer()
    result = scorer.score(
        resume_data=resume_data,
        role_id='product_manager',
        level='mid',
        job_description=None,
        mode='quality_coach'
    )

    print(f"\n{'='*80}")
    print("SCORING RESULTS")
    print(f"{'='*80}\n")

    print(f"Overall Score: {result['overallScore']}/100")
    print(f"Mode: {result['mode']}")

    print(f"\nBreakdown:")
    for component, data in result['breakdown'].items():
        print(f"  {component}: {data['score']}/{data['maxScore']}")

    # Detailed keyword analysis
    if 'keyword_details' in result:
        kw_details = result['keyword_details']
        print(f"\n{'='*80}")
        print("KEYWORD ANALYSIS")
        print(f"{'='*80}\n")

        print(f"Keywords Matched: {kw_details.get('keywords_matched', 0)}/{kw_details.get('keywords_total', 0)}")
        print(f"Verbs Matched: {kw_details.get('verbs_matched', 0)}/{kw_details.get('verbs_total', 0)}")
        print(f"Overall Match: {kw_details.get('overall_match_pct', 0):.1f}%")

        matched_kw = kw_details.get('matched_keywords', [])
        missing_kw = kw_details.get('missing_keywords', [])
        matched_verbs = kw_details.get('matched_verbs', [])

        print(f"\nFirst 50 Matched Keywords:")
        for i, kw in enumerate(matched_kw[:50], 1):
            print(f"  {i}. {kw}")

        print(f"\nMatched Verbs:")
        for i, verb in enumerate(matched_verbs, 1):
            print(f"  {i}. {verb}")

        print(f"\nFirst 30 Missing Keywords:")
        for i, kw in enumerate(missing_kw[:30], 1):
            print(f"  {i}. {kw}")

    return result

def main():
    """Main test function"""
    print("\n" + "="*80)
    print("FULL CV SCORING TEST - SABUJ vs SWASTIK")
    print("="*80)

    # Test Sabuj's CV
    sabuj_cv = '/Users/sabuj.mondal/Downloads/Sabuj_Mondal_PM_CV.docx'
    sabuj_result = test_cv(sabuj_cv, "Sabuj Mondal")

    # Summary
    print(f"\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}\n")

    print(f"Sabuj's Overall Score: {sabuj_result['overallScore']}/100")

    if 'keyword_details' in sabuj_result:
        kw_details = sabuj_result['keyword_details']
        total_matched = kw_details.get('keywords_matched', 0) + kw_details.get('verbs_matched', 0)
        total_keywords = kw_details.get('keywords_total', 0) + kw_details.get('verbs_total', 0)

        print(f"\nKeyword Analysis:")
        print(f"  Total matched: {total_matched}/{total_keywords}")
        print(f"  Match percentage: {total_matched/total_keywords*100:.1f}%")
        print(f"  Role keywords score: {sabuj_result['breakdown']['role_keywords']['score']}/25")

if __name__ == "__main__":
    main()
