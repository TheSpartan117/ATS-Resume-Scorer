#!/usr/bin/env python3
"""
Direct keyword matching test to understand the scoring issue.
"""

from docx import Document
from backend.services.role_taxonomy import get_role_scoring_data_enhanced
from backend.services.keyword_extractor import match_with_synonyms
import json

def extract_docx_text(file_path):
    """Extract text from DOCX file"""
    doc = Document(file_path)
    text_parts = []
    for para in doc.paragraphs:
        if para.text.strip():
            text_parts.append(para.text)
    return '\n'.join(text_parts)

def main():
    """Test keyword matching directly"""
    print("="*80)
    print("DIRECT KEYWORD MATCHING TEST")
    print("="*80)

    # Load Sabuj's CV
    sabuj_cv = '/Users/sabuj.mondal/Downloads/Sabuj_Mondal_PM_CV.docx'
    sabuj_text = extract_docx_text(sabuj_cv).lower()

    print(f"\nCV Text Length: {len(sabuj_text)} characters")
    print(f"\nFirst 800 characters:\n{sabuj_text[:800]}")

    # Get role data
    role_data = get_role_scoring_data_enhanced('product_manager', 'mid')

    # Check both keyword fields
    print(f"\n{'='*80}")
    print("ROLE DATA INSPECTION")
    print(f"{'='*80}\n")

    keywords = role_data.get("keywords", [])
    typical_keywords = role_data.get("typical_keywords", [])
    action_verbs = role_data.get("action_verbs", [])

    print(f"Keywords field: {len(keywords)} keywords")
    print(f"Typical_keywords field: {len(typical_keywords)} keywords")
    print(f"Action_verbs field: {len(action_verbs)} verbs")

    print(f"\nFirst 20 keywords:")
    for i, kw in enumerate(keywords[:20], 1):
        print(f"  {i}. {kw}")

    print(f"\nFirst 20 typical_keywords:")
    for i, kw in enumerate(typical_keywords[:20], 1):
        print(f"  {i}. {kw}")

    # Now manually match keywords
    print(f"\n{'='*80}")
    print("MANUAL KEYWORD MATCHING")
    print(f"{'='*80}\n")

    matched_keywords = []
    missing_keywords = []

    # Use typical_keywords (which should be the same as keywords)
    for keyword in typical_keywords:
        # Use the same matching function as the scorer
        if match_with_synonyms(keyword, sabuj_text):
            matched_keywords.append(keyword)
        else:
            missing_keywords.append(keyword)

    print(f"Matched: {len(matched_keywords)}/{len(typical_keywords)} keywords")
    print(f"Match percentage: {len(matched_keywords)/len(typical_keywords)*100:.1f}%")

    print(f"\nFirst 50 MATCHED keywords:")
    for i, kw in enumerate(matched_keywords[:50], 1):
        print(f"  {i}. {kw}")

    print(f"\nFirst 30 MISSING keywords:")
    for i, kw in enumerate(missing_keywords[:30], 1):
        print(f"  {i}. {kw}")

    # Also check action verbs
    print(f"\n{'='*80}")
    print("ACTION VERB MATCHING")
    print(f"{'='*80}\n")

    matched_verbs = []
    missing_verbs = []

    for verb in action_verbs:
        if match_with_synonyms(verb, sabuj_text):
            matched_verbs.append(verb)
        else:
            missing_verbs.append(verb)

    print(f"Matched: {len(matched_verbs)}/{len(action_verbs)} verbs")

    print(f"\nFirst 30 MATCHED verbs:")
    for i, verb in enumerate(matched_verbs[:30], 1):
        print(f"  {i}. {verb}")

    # Total
    total_matched = len(matched_keywords) + len(matched_verbs)
    total_keywords = len(typical_keywords) + len(action_verbs)

    print(f"\n{'='*80}")
    print("TOTAL SCORING")
    print(f"{'='*80}\n")

    print(f"Total matched: {total_matched}/{total_keywords}")
    print(f"Total match percentage: {total_matched/total_keywords*100:.1f}%")

    # Calculate expected score based on the thresholds in the code
    if total_keywords > 100:
        if total_matched >= 40:
            expected_score = 25
        elif total_matched >= 30:
            expected_score = 23
        elif total_matched >= 20:
            expected_score = 20
        elif total_matched >= 15:
            expected_score = 17
        elif total_matched >= 10:
            expected_score = 14
        elif total_matched >= 5:
            expected_score = 10
        else:
            expected_score = (total_matched / 5) * 10
    else:
        match_pct = total_matched/total_keywords*100
        if match_pct >= 60:
            expected_score = 25
        elif match_pct >= 50:
            expected_score = 22
        elif match_pct >= 40:
            expected_score = 18
        elif match_pct >= 30:
            expected_score = 15
        elif match_pct >= 20:
            expected_score = 12
        else:
            expected_score = (match_pct / 20) * 12

    print(f"Expected score: {expected_score}/25")

if __name__ == "__main__":
    main()
