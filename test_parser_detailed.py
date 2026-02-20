#!/usr/bin/env python3
"""Detailed debug script to test section extraction"""

import sys
sys.path.insert(0, '/Users/sabuj.mondal/ats-resume-scorer')

from backend.services.parser import extract_resume_sections
from pathlib import Path
import fitz  # PyMuPDF

CV_PATH = "/Users/sabuj.mondal/Downloads/SWASTIK PAUL_CV_DIG_TRSFN STGY_PM-2.pdf"

def test_section_extraction():
    cv_file = Path(CV_PATH)

    if not cv_file.exists():
        print(f"❌ File not found: {CV_PATH}")
        return

    print(f"📄 Testing section extraction with: {cv_file.name}")
    print()

    # Extract text using PyMuPDF
    doc = fitz.open(cv_file)
    full_text = ""
    for page in doc:
        full_text += page.get_text()
    doc.close()

    print("="*60)
    print("FULL TEXT (first 2000 chars)")
    print("="*60)
    print(full_text[:2000])
    print()

    # Check for "PROFILE BRIEF" in the text
    if "PROFILE BRIEF" in full_text:
        print("✅ 'PROFILE BRIEF' found in extracted text")
        # Find where it is
        idx = full_text.find("PROFILE BRIEF")
        print(f"   Position: {idx}")
        print(f"   Context: ...{full_text[max(0, idx-50):idx+100]}...")
    else:
        print("❌ 'PROFILE BRIEF' NOT found in extracted text")
        if "profile brief" in full_text.lower():
            print("   (but found in lowercase)")
    print()

    # Extract sections
    sections = extract_resume_sections(full_text)

    print("="*60)
    print("EXTRACTED SECTIONS")
    print("="*60)

    for section_name, content_list in sections.items():
        print(f"\n{section_name.upper()}: {len(content_list)} items")
        for i, content in enumerate(content_list):
            print(f"  Item {i+1} ({len(content)} chars): {content[:150]}...")

if __name__ == "__main__":
    test_section_extraction()
