#!/usr/bin/env python3
"""Detailed RCA - What's actually in the CV vs what parser extracts"""

import sys
sys.path.insert(0, '/Users/sabuj.mondal/ats-resume-scorer')

from backend.services.parser import parse_pdf, extract_resume_sections, is_likely_section_header
from pathlib import Path
import fitz
import json

CV_PATH = "/Users/sabuj.mondal/Downloads/SWASTIK PAUL_CV_DIG_TRSFN STGY_PM-2.pdf"

def analyze_cv():
    print("="*80)
    print("ROOT CAUSE ANALYSIS - Swastik's CV")
    print("="*80)
    print()

    # 1. Extract raw text
    doc = fitz.open(CV_PATH)
    full_text = ""
    for page in doc:
        full_text += page.get_text()
    doc.close()

    print("1. RAW TEXT ANALYSIS")
    print("-" * 80)
    print(f"Total length: {len(full_text)} chars")
    print(f"Total lines: {len(full_text.split(chr(10)))} lines")
    print()

    # 2. Check for key content
    print("2. CONTENT VERIFICATION")
    print("-" * 80)

    # Check contact info
    has_email = '@' in full_text
    has_phone = '+91' in full_text or '91-' in full_text
    print(f"✓ Email present: {has_email}")
    print(f"✓ Phone present: {has_phone}")
    print()

    # Check sections
    keywords = {
        'Profile/Summary': ['PROFILE BRIEF', 'PROFILE', 'BRIEF'],
        'Experience': ['EXPERIENCE SUMMARY', 'EXPERIENCE', 'AIR INDIA', 'DIGITAL TRANSFORMATION'],
        'Education': ['EDUCATION', 'IIT', 'INDIAN INSTITUTE', 'MBA', 'BACHELOR'],
        'Skills': ['SKILLS', 'JIRA', 'POWERBI', 'PYTHON', 'JAVA'],
    }

    for section, terms in keywords.items():
        found = [term for term in terms if term in full_text.upper()]
        print(f"✓ {section}: {len(found)} keywords found - {found[:3]}")
    print()

    # 3. Show actual section headers in the CV
    print("3. ACTUAL SECTION HEADERS IN CV")
    print("-" * 80)
    lines = full_text.split('\n')
    for i, line in enumerate(lines[:100]):  # First 100 lines
        line_stripped = line.strip()
        if line_stripped and (
            line_stripped.isupper() or
            any(kw in line_stripped.upper() for kw in ['EXPERIENCE', 'EDUCATION', 'PROFILE', 'BRIEF', 'SKILLS', 'SUMMARY'])
        ):
            if len(line_stripped) < 80:
                is_header = is_likely_section_header(line)
                print(f"Line {i:3d} [{'' if is_header else 'X'}]: {line_stripped[:70]}")
    print()

    # 4. Test parser
    print("4. PARSER OUTPUT")
    print("-" * 80)
    sections = extract_resume_sections(full_text)

    for section_name, content in sections.items():
        print(f"\n{section_name.upper()}: {len(content)} items")
        if isinstance(content, list):
            for i, item in enumerate(content[:2]):  # First 2 items
                if isinstance(item, str):
                    preview = item[:150].replace('\n', ' ')
                    print(f"  [{i+1}] {preview}...")
                elif isinstance(item, dict):
                    print(f"  [{i+1}] {item}")
    print()

    # 5. Test full parser
    print("5. FULL PARSER (parse_pdf) OUTPUT")
    print("-" * 80)
    with open(CV_PATH, 'rb') as f:
        file_content = f.read()
    resume_data = parse_pdf(file_content, "SWASTIK_CV.pdf")

    print(f"Name: {resume_data.contact.get('name', 'NOT FOUND')}")
    print(f"Email: {resume_data.contact.get('email', 'NOT FOUND')}")
    print(f"Phone: {resume_data.contact.get('phone', 'NOT FOUND')}")
    print(f"Summary: {'YES' if resume_data.summary else 'NO'} ({len(resume_data.summary or '')} chars)")
    print(f"Experience: {len(resume_data.experience)} entries")
    print(f"Education: {len(resume_data.education)} entries")
    print(f"Skills: {len(resume_data.skills)} items")
    print()

    if resume_data.experience:
        print("Experience entries:")
        for i, exp in enumerate(resume_data.experience):
            print(f"  {i+1}. {exp}")
    else:
        print("❌ NO EXPERIENCE ENTRIES FOUND!")
    print()

    # 6. Score breakdown
    print("6. ISSUES IDENTIFIED")
    print("-" * 80)
    issues = []

    if not resume_data.contact.get('email'):
        issues.append("❌ Email not extracted (but IS in CV)")
    if not resume_data.contact.get('phone'):
        issues.append("❌ Phone not extracted (but IS in CV)")
    if len(resume_data.experience) == 0:
        issues.append("❌ Experience not extracted (but IS in CV)")
    if not resume_data.summary:
        issues.append("❌ Summary not extracted (but IS in CV)")

    if issues:
        for issue in issues:
            print(issue)
    else:
        print("✅ All content extracted correctly")

if __name__ == "__main__":
    analyze_cv()
