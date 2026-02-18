#!/usr/bin/env python
"""
Quick validation script for test corpus.
Run this to verify the corpus structure is correct.
"""
import json
import sys
from pathlib import Path

CORPUS_DIR = Path(__file__).parent / "test_data" / "resumes"

def main():
    print("=" * 60)
    print("TEST RESUME CORPUS VALIDATION")
    print("=" * 60)

    if not CORPUS_DIR.exists():
        print(f"✗ ERROR: Corpus directory not found: {CORPUS_DIR}")
        sys.exit(1)

    # Count files by tier
    tiers = {
        "outstanding": [],
        "excellent": [],
        "good": [],
        "fair": [],
        "poor": []
    }

    for json_file in sorted(CORPUS_DIR.glob("*.json")):
        for tier in tiers.keys():
            if json_file.name.startswith(tier):
                tiers[tier].append(json_file.name)
                break

    # Validate structure
    errors = []
    warnings = []

    print("\nCorpus Structure:")
    print("-" * 60)

    total = 0
    for tier, files in tiers.items():
        count = len(files)
        total += count
        status = "✓" if count == 4 else "✗"
        print(f"{status} {tier.capitalize():12} {count}/4 resumes")

        if count != 4:
            errors.append(f"Tier '{tier}' has {count} resumes (expected 4)")

        for filename in files:
            print(f"    - {filename}")

    print(f"\nTotal: {total}/20 resumes")

    if total != 20:
        errors.append(f"Total resume count is {total} (expected 20)")

    # Validate JSON structure
    print("\nValidating JSON Structure:")
    print("-" * 60)

    required_fields = ["fileName", "contact", "experience", "education", "skills", "metadata"]

    for json_file in sorted(CORPUS_DIR.glob("*.json")):
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)

            # Check required fields
            missing = [field for field in required_fields if field not in data]
            if missing:
                errors.append(f"{json_file.name}: missing fields {missing}")
            else:
                print(f"✓ {json_file.name}")

            # Check contact info
            if "contact" in data:
                if not data["contact"].get("name"):
                    warnings.append(f"{json_file.name}: missing contact name")
                if not data["contact"].get("email") and "outstanding" in json_file.name:
                    warnings.append(f"{json_file.name}: outstanding resume missing email")

            # Check metadata
            if "metadata" in data:
                if "wordCount" not in data["metadata"]:
                    warnings.append(f"{json_file.name}: missing wordCount in metadata")

        except json.JSONDecodeError as e:
            errors.append(f"{json_file.name}: Invalid JSON - {e}")
        except Exception as e:
            errors.append(f"{json_file.name}: Error - {e}")

    # Print results
    print("\nValidation Results:")
    print("=" * 60)

    if errors:
        print(f"\n✗ ERRORS ({len(errors)}):")
        for error in errors:
            print(f"  - {error}")

    if warnings:
        print(f"\n⚠ WARNINGS ({len(warnings)}):")
        for warning in warnings:
            print(f"  - {warning}")

    if not errors and not warnings:
        print("✓ All validations passed!")
        print("\nCorpus is ready for testing.")
        print("\nNext steps:")
        print("  1. Run: pytest tests/test_corpus.py -v")
        print("  2. Check: pytest tests/test_corpus.py::test_score_distribution_by_tier -v -s")
        return 0
    elif not errors:
        print("\n✓ Structure is valid (warnings can be ignored)")
        return 0
    else:
        print("\n✗ Validation failed - please fix errors above")
        return 1

if __name__ == "__main__":
    sys.exit(main())
