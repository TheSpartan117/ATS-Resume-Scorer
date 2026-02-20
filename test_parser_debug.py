#!/usr/bin/env python3
"""Debug script to test PDF parsing"""

import sys
sys.path.insert(0, '/Users/sabuj.mondal/ats-resume-scorer')

from backend.services.parser import parse_pdf
from pathlib import Path

CV_PATH = "/Users/sabuj.mondal/Downloads/SWASTIK PAUL_CV_DIG_TRSFN STGY_PM-2.pdf"

def test_parser():
    cv_file = Path(CV_PATH)

    if not cv_file.exists():
        print(f"❌ File not found: {CV_PATH}")
        return

    print(f"📄 Testing parser with: {cv_file.name}")
    print()

    with open(cv_file, 'rb') as f:
        file_content = f.read()

    # Parse the PDF
    resume_data = parse_pdf(file_content, cv_file.name)

    print("="*60)
    print("PARSED RESUME DATA")
    print("="*60)
    print()

    print(f"Name: {resume_data.contact.get('name', 'N/A')}")
    print(f"Email: {resume_data.contact.get('email', 'N/A')}")
    print(f"Phone: {resume_data.contact.get('phone', 'N/A')}")
    print()

    # Check summary field
    if resume_data.summary:
        print(f"✅ SUMMARY FOUND:")
        print(f"   Length: {len(resume_data.summary)} chars")
        print(f"   Content: {resume_data.summary[:200]}...")
    else:
        print("❌ NO SUMMARY DETECTED")
    print()

    print(f"Experience entries: {len(resume_data.experience)}")
    print(f"Education entries: {len(resume_data.education)}")
    print(f"Skills: {len(resume_data.skills)}")
    print(f"Certifications: {len(resume_data.certifications)}")

if __name__ == "__main__":
    test_parser()
