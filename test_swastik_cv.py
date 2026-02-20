#!/usr/bin/env python3
"""Test script to upload and score Swastik Paul's CV"""

import requests
import json
from pathlib import Path

# API endpoint
BASE_URL = "http://localhost:8000"
CV_PATH = "/Users/sabuj.mondal/Downloads/SWASTIK PAUL_CV_DIG_TRSFN STGY_PM-2.pdf"

def upload_and_score():
    """Upload CV and get score"""

    # Check if file exists
    cv_file = Path(CV_PATH)
    if not cv_file.exists():
        print(f"❌ CV file not found: {CV_PATH}")
        return

    print(f"📄 Uploading: {cv_file.name}")
    print(f"   Size: {cv_file.stat().st_size / 1024:.1f} KB")
    print()

    # Upload file
    with open(cv_file, 'rb') as f:
        files = {'file': (cv_file.name, f, 'application/pdf')}
        data = {
            'role': 'product_manager',  # Swastik is a PM
            'level': 'senior'            # Based on his experience
        }

        try:
            print("🚀 Uploading and scoring...")
            response = requests.post(
                f"{BASE_URL}/api/upload",
                files=files,
                data=data,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()

                print("\n" + "="*60)
                print("✅ SCORING RESULTS")
                print("="*60)

                # Overall scores
                if 'ats_score' in result:
                    print(f"\n📊 ATS Score: {result['ats_score']}/100")

                if 'quality_score' in result:
                    print(f"📊 Quality Score: {result['quality_score']}/100")

                # Section detection
                if 'sections' in result:
                    print(f"\n📑 Detected Sections ({len(result['sections'])} found):")
                    for section in result['sections']:
                        title = section.get('title', 'Unknown')
                        section_id = section.get('section_id', '')
                        content_preview = section.get('content', '')[:80]
                        print(f"   • {title} ({section_id})")
                        if content_preview:
                            print(f"     Preview: {content_preview}...")

                # Check for "missing summary" issue
                if 'suggestions' in result:
                    missing_summary_found = False
                    for suggestion in result['suggestions']:
                        if 'summary' in suggestion.get('title', '').lower() and 'missing' in suggestion.get('title', '').lower():
                            missing_summary_found = True
                            print(f"\n❌ ISSUE FOUND: {suggestion.get('title')}")
                            print(f"   Description: {suggestion.get('description', '')}")
                            break

                    if not missing_summary_found:
                        print("\n✅ No 'missing summary' issue found!")

                # Show breakdown
                if 'breakdown' in result:
                    print(f"\n📈 Score Breakdown:")
                    for key, value in result['breakdown'].items():
                        print(f"   • {key}: {value}")

                # Save full response
                output_file = Path("test_swastik_cv_result.json")
                with open(output_file, 'w') as f:
                    json.dump(result, f, indent=2)
                print(f"\n💾 Full results saved to: {output_file}")

            else:
                print(f"❌ Upload failed with status {response.status_code}")
                print(f"Response: {response.text[:500]}")

        except requests.exceptions.ConnectionError:
            print("❌ Cannot connect to backend. Is it running on port 8000?")
        except requests.exceptions.Timeout:
            print("❌ Request timed out. Backend might be processing...")
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    upload_and_score()
