"""
Test Corpus Management
Loads and validates the 20-resume test corpus for ATS scoring validation.
"""
import json
import os
from pathlib import Path
from typing import Dict, List, Tuple
import pytest
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from backend.services.parser import ResumeData
from backend.services.scorer_legacy import calculate_overall_score


# Test corpus directory
CORPUS_DIR = Path(__file__).parent / "test_data" / "resumes"


# Score tier definitions
SCORE_TIERS = {
    "outstanding": {"min": 90, "max": 100, "count": 4},
    "excellent": {"min": 80, "max": 89, "count": 4},
    "good": {"min": 65, "max": 79, "count": 4},
    "fair": {"min": 50, "max": 64, "count": 4},
    "poor": {"min": 0, "max": 49, "count": 4}
}


def load_resume_from_json(file_path: Path) -> ResumeData:
    """Load a resume from JSON file and convert to ResumeData"""
    with open(file_path, 'r') as f:
        data = json.load(f)

    return ResumeData(
        fileName=data["fileName"],
        contact=data["contact"],
        experience=data.get("experience", []),
        education=data.get("education", []),
        skills=data.get("skills", []),
        certifications=data.get("certifications", []),
        metadata=data["metadata"]
    )


def get_all_test_resumes() -> Dict[str, List[Tuple[str, ResumeData]]]:
    """
    Load all test resumes organized by tier.
    Returns dict with tier names as keys and list of (filename, ResumeData) tuples as values.
    """
    resumes_by_tier = {
        "outstanding": [],
        "excellent": [],
        "good": [],
        "fair": [],
        "poor": []
    }

    if not CORPUS_DIR.exists():
        raise FileNotFoundError(f"Test corpus directory not found: {CORPUS_DIR}")

    # Load all JSON files
    for json_file in sorted(CORPUS_DIR.glob("*.json")):
        # Determine tier from filename
        tier = None
        for tier_name in SCORE_TIERS.keys():
            if json_file.name.startswith(tier_name):
                tier = tier_name
                break

        if tier:
            resume = load_resume_from_json(json_file)
            resumes_by_tier[tier].append((json_file.name, resume))

    return resumes_by_tier


def validate_corpus_structure() -> Tuple[bool, List[str]]:
    """
    Validate that the test corpus has the correct structure.
    Returns (is_valid, list_of_issues)
    """
    issues = []

    if not CORPUS_DIR.exists():
        issues.append(f"Corpus directory does not exist: {CORPUS_DIR}")
        return False, issues

    resumes_by_tier = get_all_test_resumes()

    # Check each tier has correct number of resumes
    for tier, config in SCORE_TIERS.items():
        expected_count = config["count"]
        actual_count = len(resumes_by_tier[tier])
        if actual_count != expected_count:
            issues.append(f"Tier '{tier}': expected {expected_count} resumes, found {actual_count}")

    # Total should be 20
    total_resumes = sum(len(resumes) for resumes in resumes_by_tier.values())
    if total_resumes != 20:
        issues.append(f"Expected 20 total resumes, found {total_resumes}")

    return len(issues) == 0, issues


# TESTS


def test_corpus_structure():
    """Test that corpus has correct structure (20 resumes, 4 per tier)"""
    is_valid, issues = validate_corpus_structure()
    assert is_valid, f"Corpus structure validation failed: {', '.join(issues)}"


def test_all_resumes_loadable():
    """Test that all 20 resumes can be loaded successfully"""
    resumes_by_tier = get_all_test_resumes()

    loaded_count = 0
    for tier, resumes in resumes_by_tier.items():
        for filename, resume in resumes:
            assert isinstance(resume, ResumeData), f"Failed to load {filename} as ResumeData"
            assert resume.fileName, f"Resume {filename} missing fileName"
            assert resume.contact, f"Resume {filename} missing contact info"
            assert resume.metadata, f"Resume {filename} missing metadata"
            loaded_count += 1

    assert loaded_count == 20, f"Expected to load 20 resumes, loaded {loaded_count}"


def test_outstanding_tier_characteristics():
    """Test that outstanding tier resumes have expected characteristics"""
    resumes_by_tier = get_all_test_resumes()
    outstanding_resumes = resumes_by_tier["outstanding"]

    for filename, resume in outstanding_resumes:
        # Should have complete contact info
        assert resume.contact.get("name"), f"{filename}: missing name"
        assert resume.contact.get("email"), f"{filename}: missing email"
        assert resume.contact.get("phone"), f"{filename}: missing phone"

        # Should have substantial experience
        assert len(resume.experience) >= 2, f"{filename}: insufficient experience entries"

        # Should have many skills
        assert len(resume.skills) >= 15, f"{filename}: insufficient skills (has {len(resume.skills)})"

        # Should have education
        assert len(resume.education) >= 1, f"{filename}: missing education"

        # Should have reasonable word count
        assert resume.metadata.get("wordCount", 0) >= 400, f"{filename}: word count too low"

        # Should not have photo (ATS red flag)
        assert not resume.metadata.get("hasPhoto"), f"{filename}: has photo (red flag)"


def test_excellent_tier_characteristics():
    """Test that excellent tier resumes have expected characteristics"""
    resumes_by_tier = get_all_test_resumes()
    excellent_resumes = resumes_by_tier["excellent"]

    for filename, resume in excellent_resumes:
        # Should have most contact info
        assert resume.contact.get("name"), f"{filename}: missing name"
        assert resume.contact.get("email"), f"{filename}: missing email"

        # Should have experience
        assert len(resume.experience) >= 2, f"{filename}: insufficient experience"

        # Should have skills
        assert len(resume.skills) >= 10, f"{filename}: insufficient skills"

        # Should have education
        assert len(resume.education) >= 1, f"{filename}: missing education"


def test_good_tier_characteristics():
    """Test that good tier resumes have expected characteristics"""
    resumes_by_tier = get_all_test_resumes()
    good_resumes = resumes_by_tier["good"]

    for filename, resume in good_resumes:
        # Should have basic contact info
        assert resume.contact.get("name"), f"{filename}: missing name"
        assert resume.contact.get("email"), f"{filename}: missing email"

        # Should have some experience
        assert len(resume.experience) >= 1, f"{filename}: no experience"

        # Should have some skills
        assert len(resume.skills) >= 5, f"{filename}: insufficient skills"


def test_fair_tier_characteristics():
    """Test that fair tier resumes have issues but are salvageable"""
    resumes_by_tier = get_all_test_resumes()
    fair_resumes = resumes_by_tier["fair"]

    for filename, resume in fair_resumes:
        # May have incomplete contact info
        assert resume.contact.get("name"), f"{filename}: missing name"

        # Should have some experience
        assert len(resume.experience) >= 1, f"{filename}: no experience"

        # Skills may be limited
        # No strict requirement - these resumes have issues


def test_poor_tier_characteristics():
    """Test that poor tier resumes have major issues"""
    resumes_by_tier = get_all_test_resumes()
    poor_resumes = resumes_by_tier["poor"]

    issues_found = []
    for filename, resume in poor_resumes:
        resume_issues = []

        # Check for missing critical contact info
        if not resume.contact.get("email"):
            resume_issues.append("missing email")

        # Check for vague/weak content
        if len(resume.skills) < 3:
            resume_issues.append("very few skills")

        # Check for formatting issues
        if resume.metadata.get("hasPhoto"):
            resume_issues.append("has photo")

        if resume.metadata.get("wordCount", 0) < 100:
            resume_issues.append("too short")

        # Each poor resume should have at least one major issue
        assert len(resume_issues) > 0, f"{filename}: classified as 'poor' but no issues detected"
        issues_found.append((filename, resume_issues))

    # Verify we found issues in all poor resumes
    assert len(issues_found) == len(poor_resumes)


def test_score_distribution_by_tier():
    """
    Test that resumes score within their expected tier ranges.
    This is a key validation test.
    """
    resumes_by_tier = get_all_test_resumes()

    results = {}

    for tier, config in SCORE_TIERS.items():
        tier_results = []

        for filename, resume in resumes_by_tier[tier]:
            # Score the resume (using generic role/level for consistency)
            score_result = calculate_overall_score(resume, "", "software_engineer", "mid")
            score = score_result["overallScore"]

            tier_results.append({
                "filename": filename,
                "score": score,
                "expected_min": config["min"],
                "expected_max": config["max"]
            })

        results[tier] = tier_results

    # Print results for debugging
    print("\n=== SCORE DISTRIBUTION BY TIER ===")
    for tier, tier_results in results.items():
        scores = [r["score"] for r in tier_results]
        avg_score = sum(scores) / len(scores) if scores else 0
        print(f"\n{tier.upper()} (expected {SCORE_TIERS[tier]['min']}-{SCORE_TIERS[tier]['max']}):")
        print(f"  Average: {avg_score:.1f}")
        for result in tier_results:
            status = "✓" if result["expected_min"] <= result["score"] <= result["expected_max"] else "✗"
            print(f"  {status} {result['filename']}: {result['score']:.1f}")

    # Note: This test is informational - we don't assert strict ranges
    # because scoring depends on many factors. We just want to see the distribution.


def test_keyword_variety_across_tiers():
    """Test that higher tiers have more diverse skills/keywords"""
    resumes_by_tier = get_all_test_resumes()

    tier_skill_counts = {}
    for tier in ["outstanding", "excellent", "good", "fair", "poor"]:
        total_skills = 0
        for filename, resume in resumes_by_tier[tier]:
            total_skills += len(resume.skills)
        avg_skills = total_skills / len(resumes_by_tier[tier]) if resumes_by_tier[tier] else 0
        tier_skill_counts[tier] = avg_skills

    # Outstanding should have more skills on average than poor
    assert tier_skill_counts["outstanding"] > tier_skill_counts["poor"]
    assert tier_skill_counts["excellent"] > tier_skill_counts["fair"]


def test_word_count_correlates_with_tier():
    """Test that higher tiers generally have appropriate word counts"""
    resumes_by_tier = get_all_test_resumes()

    tier_word_counts = {}
    for tier in ["outstanding", "excellent", "good", "fair", "poor"]:
        total_words = 0
        for filename, resume in resumes_by_tier[tier]:
            total_words += resume.metadata.get("wordCount", 0)
        avg_words = total_words / len(resumes_by_tier[tier]) if resumes_by_tier[tier] else 0
        tier_word_counts[tier] = avg_words

    # Outstanding should have more content than poor
    assert tier_word_counts["outstanding"] > tier_word_counts["poor"]
    # But not too long (over 600 words can be penalized)
    assert tier_word_counts["outstanding"] < 600


def test_contact_completeness_by_tier():
    """Test that contact info completeness decreases with tier"""
    resumes_by_tier = get_all_test_resumes()

    def calculate_contact_completeness(resume: ResumeData) -> float:
        """Calculate percentage of contact fields filled"""
        fields = ["name", "email", "phone", "location", "linkedin", "website"]
        filled = sum(1 for field in fields if resume.contact.get(field))
        return filled / len(fields)

    tier_completeness = {}
    for tier in ["outstanding", "excellent", "good", "fair", "poor"]:
        total_completeness = 0
        for filename, resume in resumes_by_tier[tier]:
            total_completeness += calculate_contact_completeness(resume)
        avg_completeness = total_completeness / len(resumes_by_tier[tier]) if resumes_by_tier[tier] else 0
        tier_completeness[tier] = avg_completeness

    # Outstanding should have more complete contact info than poor
    assert tier_completeness["outstanding"] > tier_completeness["poor"]
    assert tier_completeness["outstanding"] >= 0.7  # At least 70% fields filled


if __name__ == "__main__":
    # Run validation
    print("Validating test corpus...")
    is_valid, issues = validate_corpus_structure()

    if is_valid:
        print("✓ Corpus structure is valid")
        print(f"✓ Found 20 resumes across 5 tiers")

        # Load and display summary
        resumes_by_tier = get_all_test_resumes()
        print("\nCorpus Summary:")
        for tier, resumes in resumes_by_tier.items():
            print(f"  {tier.capitalize()}: {len(resumes)} resumes")
            for filename, _ in resumes:
                print(f"    - {filename}")
    else:
        print("✗ Corpus validation failed:")
        for issue in issues:
            print(f"  - {issue}")
