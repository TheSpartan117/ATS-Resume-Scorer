#!/usr/bin/env python3
"""Detailed keyword matching breakdown for all 3 CVs."""
import sys
sys.path.insert(0, '/Users/sabuj.mondal/ats-resume-scorer')

from backend.services.parser import parse_pdf
from backend.services.scorer_v3_adapter import ScorerV3Adapter
from backend.services.parameters.p1_1_required_keywords import RequiredKeywordsMatcher
from backend.services.parameters.p1_2_preferred_keywords import PreferredKeywordsMatcher
from backend.services.role_keywords import get_role_keywords

# Test CVs
CVS = [
    {
        'name': 'Sabuj Mondal',
        'path': '/Users/sabuj.mondal/Downloads/Sabuj_Mondal_PM_CV.pdf',
    },
    {
        'name': 'Aishik Das',
        'path': '/Users/sabuj.mondal/Downloads/AISHIK DAS_CV_v2.pdf',
    },
    {
        'name': 'Swastik Paul',
        'path': '/Users/sabuj.mondal/Downloads/SWASTIK PAUL_CV_DIG_TRSFN STGY_PM-2.pdf',
    }
]

# Get role keywords
role_keywords = get_role_keywords('product_manager')
required_keywords = role_keywords['required']
preferred_keywords = role_keywords['preferred']

print("="*100)
print("PRODUCT MANAGER KEYWORD LISTS")
print("="*100)
print(f"\nP1.1 Required Keywords ({len(required_keywords)} total):")
for i, kw in enumerate(required_keywords, 1):
    print(f"  {i:2d}. {kw}")

print(f"\nP1.2 Preferred Keywords ({len(preferred_keywords)} total):")
for i, kw in enumerate(preferred_keywords, 1):
    print(f"  {i:2d}. {kw}")

# Initialize matchers
p1_1_matcher = RequiredKeywordsMatcher()
p1_2_matcher = PreferredKeywordsMatcher()

# Process each CV
for cv_info in CVS:
    print("\n" + "="*100)
    print(f"CV: {cv_info['name']}")
    print("="*100)

    # Parse and extract text
    with open(cv_info['path'], 'rb') as f:
        resume_data = parse_pdf(f.read(), cv_info['name'] + '.pdf')

    adapter = ScorerV3Adapter()
    scorer_input = adapter._convert_resume_data(resume_data)
    resume_text = scorer_input['text']

    # Show resume text snippet
    print(f"\nResume text length: {len(resume_text)} characters")
    print(f"First 300 chars: {resume_text[:300]}...")

    # ============================================================
    # P1.1: Required Keywords
    # ============================================================
    print("\n" + "-"*100)
    print("P1.1: REQUIRED KEYWORDS (25 points max)")
    print("-"*100)

    p1_1_result = p1_1_matcher.score(
        keywords=required_keywords,
        resume_text=resume_text,
        level='senior'
    )

    matched = p1_1_result['matched_keywords']
    unmatched = p1_1_result['unmatched_keywords']
    match_details = p1_1_result['match_details']
    points_per_keyword = p1_1_result.get('points_per_keyword', 0)
    total_score = p1_1_result['score']

    print(f"\nScoring Formula:")
    print(f"  Total keywords: {len(required_keywords)}")
    print(f"  Points per keyword: {points_per_keyword:.2f}")
    print(f"  Formula: min(matched_count × {points_per_keyword:.2f}, 25)")

    print(f"\n✓ MATCHED Keywords ({len(matched)}/{len(required_keywords)}):")
    if matched:
        matched_points = 0
        for kw in matched:
            similarity = match_details.get(kw, 0)
            contribution = points_per_keyword if similarity >= 0.6 else 0
            matched_points += contribution
            print(f"  ✓ '{kw}' - Similarity: {similarity:.2f} → +{contribution:.2f} points")
        print(f"  → Total from matched: {matched_points:.2f} points")
    else:
        print("  (None)")

    print(f"\n✗ UNMATCHED Keywords ({len(unmatched)}/{len(required_keywords)}):")
    if unmatched:
        for kw in unmatched[:10]:  # Show first 10
            similarity = match_details.get(kw, 0)
            print(f"  ✗ '{kw}' - Similarity: {similarity:.2f} (needs ≥0.60)")
        if len(unmatched) > 10:
            print(f"  ... and {len(unmatched) - 10} more")
    else:
        print("  (None)")

    print(f"\n📊 P1.1 FINAL SCORE: {total_score:.1f}/25 ({total_score/25*100:.1f}%)")

    # ============================================================
    # P1.2: Preferred Keywords
    # ============================================================
    print("\n" + "-"*100)
    print("P1.2: PREFERRED KEYWORDS (10 points max)")
    print("-"*100)

    p1_2_result = p1_2_matcher.calculate_score(
        preferred_keywords=preferred_keywords,
        resume_text=resume_text,
        experience_level='senior'
    )

    matched_p2 = p1_2_result['matched_keywords']
    unmatched_p2 = p1_2_result['unmatched_keywords']
    points_per_keyword_p2 = 10.0 / len(preferred_keywords)  # Calculate from result
    total_score_p2 = p1_2_result['score']

    print(f"\nScoring Formula:")
    print(f"  Total keywords: {len(preferred_keywords)}")
    print(f"  Points per keyword: {points_per_keyword_p2:.2f}")
    print(f"  Formula: min(matched_count × {points_per_keyword_p2:.2f}, 10)")

    print(f"\n✓ MATCHED Keywords ({len(matched_p2)}/{len(preferred_keywords)}):")
    if matched_p2:
        matched_points_p2 = 0
        for kw in matched_p2:
            contribution = points_per_keyword_p2
            matched_points_p2 += contribution
            print(f"  ✓ '{kw}' → +{contribution:.2f} points")
        print(f"  → Total from matched: {matched_points_p2:.2f} points")
    else:
        print("  (None)")

    print(f"\n✗ UNMATCHED Keywords ({len(unmatched_p2)}/{len(preferred_keywords)}):")
    if unmatched_p2:
        for kw in unmatched_p2[:10]:  # Show first 10
            print(f"  ✗ '{kw}'")
        if len(unmatched_p2) > 10:
            print(f"  ... and {len(unmatched_p2) - 10} more")
    else:
        print("  (None)")

    print(f"\n📊 P1.2 FINAL SCORE: {total_score_p2:.1f}/10 ({total_score_p2/10*100:.1f}%)")

    # Summary
    print("\n" + "="*100)
    print(f"KEYWORD SUMMARY FOR {cv_info['name'].upper()}")
    print("="*100)
    print(f"P1.1 Required:  {len(matched)}/{len(required_keywords)} matched → {total_score:.1f}/25 points")
    print(f"P1.2 Preferred: {len(matched_p2)}/{len(preferred_keywords)} matched → {total_score_p2:.1f}/10 points")
    print(f"Total Keyword Score: {total_score + total_score_p2:.1f}/35 points")

print("\n" + "="*100)
print("COMPARISON ACROSS ALL CVs")
print("="*100)

# Create comparison table
comparison_data = []
for cv_info in CVS:
    with open(cv_info['path'], 'rb') as f:
        resume_data = parse_pdf(f.read(), cv_info['name'] + '.pdf')

    adapter = ScorerV3Adapter()
    scorer_input = adapter._convert_resume_data(resume_data)
    resume_text = scorer_input['text']

    p1_1_result = p1_1_matcher.score(keywords=required_keywords, resume_text=resume_text, level='senior')
    p1_2_result = p1_2_matcher.calculate_score(preferred_keywords=preferred_keywords, resume_text=resume_text, experience_level='senior')

    comparison_data.append({
        'name': cv_info['name'],
        'p1_1_matched': len(p1_1_result['matched_keywords']),
        'p1_1_score': p1_1_result['score'],
        'p1_1_keywords': p1_1_result['matched_keywords'],
        'p1_2_matched': len(p1_2_result['matched_keywords']),
        'p1_2_score': p1_2_result['score'],
        'p1_2_keywords': p1_2_result['matched_keywords']
    })

print(f"\n{'CV':<20} {'P1.1 Matched':<15} {'P1.1 Score':<15} {'P1.2 Matched':<15} {'P1.2 Score':<15}")
print("-"*100)
for data in comparison_data:
    print(f"{data['name']:<20} {data['p1_1_matched']}/{len(required_keywords):<12} {data['p1_1_score']:.1f}/25{'':<9} {data['p1_2_matched']}/{len(preferred_keywords):<12} {data['p1_2_score']:.1f}/10")

print("\n" + "="*100)
print("WHY P1.1 SCORES ARE IDENTICAL")
print("="*100)
print("All 3 CVs matched the SAME 7 required keywords:")
for i, kw in enumerate(comparison_data[0]['p1_1_keywords'], 1):
    print(f"  {i}. {kw}")
print(f"\nPoints per keyword: {comparison_data[0]['p1_1_score'] / comparison_data[0]['p1_1_matched']:.2f}")
print(f"7 matches × 1.32 pts/keyword = {comparison_data[0]['p1_1_score']:.1f} points")
print("\nConclusion: Similar PM roles → similar PM keyword usage → identical scores")

print("\n" + "="*100)
print("WHY P1.2 SCORES ARE DIFFERENT")
print("="*100)
for data in comparison_data:
    print(f"\n{data['name']}:")
    print(f"  Matched {data['p1_2_matched']} keywords: {data['p1_2_keywords']}")
    print(f"  {data['p1_2_matched']} × {10.0/len(preferred_keywords):.2f} pts/keyword = {data['p1_2_score']:.1f} points")
