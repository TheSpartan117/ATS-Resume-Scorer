#!/usr/bin/env python3
"""
Final comparison of Sabuj and Swastik CVs.
"""

from backend.services.parser import parse_docx, parse_pdf
from backend.services.scorer_v2 import AdaptiveScorer
from backend.services.role_taxonomy import get_role_scoring_data_enhanced

def test_cv(cv_path, cv_name, is_pdf=False):
    """Test a single CV"""
    print(f"\n{'='*80}")
    print(f"TESTING: {cv_name}")
    print(f"{'='*80}\n")

    # Read and parse CV
    with open(cv_path, 'rb') as f:
        file_content = f.read()

    if is_pdf:
        resume_data = parse_pdf(file_content, cv_name)
    else:
        resume_data = parse_docx(file_content, cv_name)

    print(f"Parsed Resume Data:")
    print(f"  Name: {resume_data.contact.get('name', 'N/A')}")
    print(f"  Email: {resume_data.contact.get('email', 'N/A')}")
    print(f"  Experience items: {len(resume_data.experience)}")
    print(f"  Skills: {len(resume_data.skills)}")

    # Show first experience
    if resume_data.experience:
        exp = resume_data.experience[0]
        print(f"\nFirst Experience:")
        print(f"  Title: {exp.get('title', 'N/A')[:60]}")
        print(f"  Company: {exp.get('company', 'N/A')}")
        desc = exp.get('description', '')
        if isinstance(desc, str):
            print(f"  Description (first 200 chars): {desc[:200]}")

    # Score the resume
    scorer = AdaptiveScorer()
    result = scorer.score(
        resume_data=resume_data,
        role_id='product_manager',
        level='mid',
        job_description=None,
        mode='quality_coach'
    )

    print(f"\nSCORING RESULTS:")
    print(f"  Overall Score: {result['overallScore']}/100")

    print(f"\nBreakdown:")
    for component, data in result['breakdown'].items():
        print(f"  {component}: {data['score']}/{data['maxScore']}")

    # Keyword details
    if 'keyword_details' in result:
        kw_details = result['keyword_details']
        print(f"\nKEYWORD ANALYSIS:")
        print(f"  Keywords Matched: {kw_details.get('keywords_matched', 0)}/{kw_details.get('keywords_total', 0)}")
        print(f"  Verbs Matched: {kw_details.get('verbs_matched', 0)}/{kw_details.get('verbs_total', 0)}")

        total_matched = kw_details.get('keywords_matched', 0) + kw_details.get('verbs_matched', 0)
        total_keywords = kw_details.get('keywords_total', 0) + kw_details.get('verbs_total', 0)
        print(f"  Total Matched: {total_matched}/{total_keywords}")
        print(f"  Match %: {kw_details.get('overall_match_pct', 0):.1f}%")

        matched_kw = kw_details.get('matched_keywords', [])
        matched_verbs = kw_details.get('matched_verbs', [])

        print(f"\nMatched Keywords (first 40):")
        for i, kw in enumerate(matched_kw[:40], 1):
            print(f"    {i}. {kw}")

        print(f"\nMatched Verbs:")
        for i, verb in enumerate(matched_verbs, 1):
            print(f"    {i}. {verb}")

    return result

def main():
    """Main comparison function"""
    print("\n" + "="*80)
    print("FINAL CV COMPARISON - SABUJ vs SWASTIK")
    print("="*80)

    # Get role data to show keywords being used
    role_data = get_role_scoring_data_enhanced('product_manager', 'mid')
    print(f"\nRole Data (product_manager, mid):")
    print(f"  Keywords: {len(role_data.get('keywords', []))}")
    print(f"  Typical Keywords: {len(role_data.get('typical_keywords', []))}")
    print(f"  Action Verbs: {len(role_data.get('action_verbs', []))}")
    print(f"  First 20 keywords: {role_data.get('keywords', [])[:20]}")

    # Test both CVs
    sabuj_cv = '/Users/sabuj.mondal/Downloads/Sabuj_Mondal_PM_CV.docx'
    sabuj_result = test_cv(sabuj_cv, "Sabuj Mondal", is_pdf=False)

    swastik_cv = '/Users/sabuj.mondal/ats-resume-scorer/backend/data/SWASTIK PAUL_CV_DIG_TRSFN STGY_PM-2_1771540343350.docx'
    swastik_result = test_cv(swastik_cv, "Swastik Paul", is_pdf=True)

    # Comparison
    print(f"\n{'='*80}")
    print("COMPARISON SUMMARY")
    print(f"{'='*80}\n")

    print(f"SABUJ MONDAL:")
    print(f"  Overall Score: {sabuj_result['overallScore']}/100")
    print(f"  Role Keywords Score: {sabuj_result['breakdown']['role_keywords']['score']}/25")
    if 'keyword_details' in sabuj_result:
        kw = sabuj_result['keyword_details']
        total = kw.get('keywords_matched', 0) + kw.get('verbs_matched', 0)
        print(f"  Total Keyword Matches: {total}")

    print(f"\nSWASTIK PAUL:")
    print(f"  Overall Score: {swastik_result['overallScore']}/100")
    print(f"  Role Keywords Score: {swastik_result['breakdown']['role_keywords']['score']}/25")
    if 'keyword_details' in swastik_result:
        kw = swastik_result['keyword_details']
        total = kw.get('keywords_matched', 0) + kw.get('verbs_matched', 0)
        print(f"  Total Keyword Matches: {total}")

    # Detailed comparison
    if 'keyword_details' in sabuj_result and 'keyword_details' in swastik_result:
        sabuj_kw_set = set(sabuj_result['keyword_details'].get('matched_keywords', []))
        swastik_kw_set = set(swastik_result['keyword_details'].get('matched_keywords', []))

        sabuj_verbs_set = set(sabuj_result['keyword_details'].get('matched_verbs', []))
        swastik_verbs_set = set(swastik_result['keyword_details'].get('matched_verbs', []))

        common_kw = sabuj_kw_set & swastik_kw_set
        only_sabuj_kw = sabuj_kw_set - swastik_kw_set
        only_swastik_kw = swastik_kw_set - sabuj_kw_set

        print(f"\n{'='*80}")
        print("KEYWORD DIFFERENCES")
        print(f"{'='*80}\n")

        print(f"Common keywords: {len(common_kw)}")
        print(f"Only in Sabuj: {len(only_sabuj_kw)}")
        print(f"Only in Swastik: {len(only_swastik_kw)}")

        if only_sabuj_kw:
            print(f"\nKeywords only in Sabuj's CV:")
            for kw in sorted(only_sabuj_kw):
                print(f"  - {kw}")

        if only_swastik_kw:
            print(f"\nKeywords only in Swastik's CV:")
            for kw in sorted(only_swastik_kw):
                print(f"  - {kw}")

        # Verb comparison
        common_verbs = sabuj_verbs_set & swastik_verbs_set
        only_sabuj_verbs = sabuj_verbs_set - swastik_verbs_set
        only_swastik_verbs = swastik_verbs_set - sabuj_verbs_set

        print(f"\n{'='*80}")
        print("VERB DIFFERENCES")
        print(f"{'='*80}\n")

        print(f"Common verbs: {len(common_verbs)}")
        print(f"Only in Sabuj: {len(only_sabuj_verbs)}")
        print(f"Only in Swastik: {len(only_swastik_verbs)}")

        if only_sabuj_verbs:
            print(f"\nVerbs only in Sabuj's CV: {sorted(only_sabuj_verbs)}")

        if only_swastik_verbs:
            print(f"\nVerbs only in Swastik's CV: {sorted(only_swastik_verbs)}")

if __name__ == "__main__":
    main()
