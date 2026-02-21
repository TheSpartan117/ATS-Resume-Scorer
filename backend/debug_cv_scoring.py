#!/usr/bin/env python3
"""
Debug script to analyze CV scoring and keyword matching for Sabuj and Swastik.
"""

import sys
from docx import Document
from backend.services.scorer_v2 import AdaptiveScorer
from backend.services.parser import ResumeData
from backend.services.role_taxonomy import get_role_scoring_data_enhanced
import json

def extract_docx_text(file_path):
    """Extract text from DOCX file"""
    doc = Document(file_path)
    text_parts = []
    for para in doc.paragraphs:
        if para.text.strip():
            text_parts.append(para.text)
    return '\n'.join(text_parts)

def create_resume_data_from_text(text, filename):
    """Create a basic ResumeData object from text"""
    lines = text.split('\n')

    # Extract name (first non-empty line)
    name = lines[0] if lines else "Unknown"

    # Simple email extraction
    email = ""
    phone = ""
    for line in lines[:10]:
        if '@' in line and not email:
            parts = line.split()
            for part in parts:
                if '@' in part:
                    email = part
                    break
        if '+' in line or '(' in line:
            phone = line.strip()

    # Create resume data
    resume_data = ResumeData(
        fileName=filename,
        contact={
            "name": name,
            "email": email,
            "phone": phone
        },
        experience=[],
        education=[],
        skills=[],
        certifications=[],
        metadata={"raw_text": text}
    )

    return resume_data

def analyze_cv(cv_path, cv_name):
    """Analyze a single CV"""
    print(f"\n{'='*80}")
    print(f"ANALYZING: {cv_name}")
    print(f"{'='*80}\n")

    # Extract text
    text = extract_docx_text(cv_path)
    print(f"Extracted {len(text)} characters of text")
    print(f"\nFirst 500 chars:\n{text[:500]}\n")

    # Create resume data
    resume_data = create_resume_data_from_text(text, cv_name)

    # Get role data with enhanced keywords
    role_data = get_role_scoring_data_enhanced('product_manager', 'mid')
    print(f"\nRole Data Loaded:")
    print(f"  Keywords count: {len(role_data.get('keywords', []))}")
    print(f"  First 20 keywords: {role_data.get('keywords', [])[:20]}")

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
    print(f"  Mode: {result['mode']}")

    print(f"\nBreakdown:")
    for component, data in result['breakdown'].items():
        print(f"  {component}: {data['score']}/{data['maxScore']}")

    # Keyword analysis
    if 'keyword_details' in result:
        kw_details = result['keyword_details']
        print(f"\nKEYWORD ANALYSIS:")
        print(f"  Total keywords: {kw_details.get('total_keywords', 'N/A')}")
        print(f"  Matched count: {kw_details.get('matched_count', 'N/A')}")

        matched = kw_details.get('matched_keywords', [])
        print(f"\n  First 50 matched keywords:")
        for i, kw in enumerate(matched[:50], 1):
            print(f"    {i}. {kw}")

        missing = kw_details.get('missing_keywords', [])
        print(f"\n  First 30 missing keywords:")
        for i, kw in enumerate(missing[:30], 1):
            print(f"    {i}. {kw}")

    return result, text

def main():
    """Main analysis function"""
    print("\n" + "="*80)
    print("CV SCORING ANALYSIS - SABUJ vs SWASTIK")
    print("="*80)

    # Paths to CVs
    sabuj_cv = '/Users/sabuj.mondal/Downloads/Sabuj_Mondal_PM_CV.docx'
    swastik_cv = '/Users/sabuj.mondal/ats-resume-scorer/backend/data/SWASTIK PAUL_CV_DIG_TRSFN STGY_PM-2_1771540343350.docx'

    # Analyze both CVs
    sabuj_result, sabuj_text = analyze_cv(sabuj_cv, "Sabuj Mondal")

    # Try Swastik's CV - if it fails, try another one
    try:
        swastik_result, swastik_text = analyze_cv(swastik_cv, "Swastik Paul")
    except Exception as e:
        print(f"\nError with first Swastik CV: {e}")
        print("This CV file appears to be corrupted or in PDF format.")
        print("Skipping Swastik's analysis.")
        swastik_result = None
        swastik_text = None

    # Compare results
    print(f"\n{'='*80}")
    print("COMPARISON SUMMARY")
    print(f"{'='*80}\n")

    print(f"Sabuj's Score: {sabuj_result['overallScore']}/100")
    if swastik_result:
        print(f"Swastik's Score: {swastik_result['overallScore']}/100")

    # Keyword comparison
    if swastik_result and 'keyword_details' in sabuj_result and 'keyword_details' in swastik_result:
        sabuj_kw = set(sabuj_result['keyword_details'].get('matched_keywords', []))
        swastik_kw = set(swastik_result['keyword_details'].get('matched_keywords', []))

        print(f"\nKeyword Matches:")
        print(f"  Sabuj: {len(sabuj_kw)}")
        print(f"  Swastik: {len(swastik_kw)}")

        only_sabuj = sabuj_kw - swastik_kw
        only_swastik = swastik_kw - sabuj_kw
        common = sabuj_kw & swastik_kw

        print(f"\n  Common keywords: {len(common)}")
        print(f"  Only in Sabuj: {len(only_sabuj)}")
        print(f"  Only in Swastik: {len(only_swastik)}")

        if only_sabuj:
            print(f"\n  Sabuj's unique keywords (first 20):")
            for kw in list(only_sabuj)[:20]:
                print(f"    - {kw}")

if __name__ == "__main__":
    main()
