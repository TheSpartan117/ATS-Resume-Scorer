#!/usr/bin/env python
"""Quick validation script for P5.1 Years of Experience Alignment"""

from services.parameters.p5_1_years_alignment import create_scorer

def test_basic_functionality():
    """Test basic functionality of the scorer"""
    scorer = create_scorer()

    # Test 1: Beginner with 2 years (should score 10)
    experience_beginner = [
        {
            "title": "Junior Engineer",
            "company": "TechCo",
            "dates": "2024 - Present",
            "description": "Learning and growing."
        }
    ]
    result = scorer.score(experience_beginner, "beginner")
    print(f"Test 1 - Beginner with ~2 years:")
    print(f"  Score: {result['score']}/10")
    print(f"  Years: {result['years_calculated']}")
    print(f"  Aligned: {result['aligned']}")
    print(f"  Details: {result['details']}")
    print()

    # Test 2: Intermediary with 5 years (should score 10)
    experience_intermediary = [
        {
            "title": "Software Engineer",
            "company": "TechCo",
            "dates": "2021 - Present",
            "description": "Developed solutions."
        }
    ]
    result = scorer.score(experience_intermediary, "intermediary")
    print(f"Test 2 - Intermediary with ~5 years:")
    print(f"  Score: {result['score']}/10")
    print(f"  Years: {result['years_calculated']}")
    print(f"  Aligned: {result['aligned']}")
    print(f"  Details: {result['details']}")
    print()

    # Test 3: Senior with 10 years (should score 10)
    experience_senior = [
        {
            "title": "Senior Engineer",
            "company": "TechCo",
            "dates": "2016 - Present",
            "description": "Led initiatives."
        }
    ]
    result = scorer.score(experience_senior, "senior")
    print(f"Test 3 - Senior with ~10 years:")
    print(f"  Score: {result['score']}/10")
    print(f"  Years: {result['years_calculated']}")
    print(f"  Aligned: {result['aligned']}")
    print(f"  Details: {result['details']}")
    print()

    # Test 4: Misalignment - Beginner with 10 years (should score 0)
    result = scorer.score(experience_senior, "beginner")
    print(f"Test 4 - Beginner with ~10 years (misaligned):")
    print(f"  Score: {result['score']}/10")
    print(f"  Years: {result['years_calculated']}")
    print(f"  Aligned: {result['aligned']}")
    print(f"  Details: {result['details']}")
    print()

    # Test 5: Multiple positions
    experience_multiple = [
        {
            "title": "Senior Engineer",
            "company": "TechCo",
            "dates": "2020 - Present",
            "description": "Led team."
        },
        {
            "title": "Junior Engineer",
            "company": "StartupHub",
            "dates": "2015 - 2018",
            "description": "Developed features."
        }
    ]
    result = scorer.score(experience_multiple, "senior")
    print(f"Test 5 - Multiple positions (total ~9 years):")
    print(f"  Score: {result['score']}/10")
    print(f"  Years: {result['years_calculated']}")
    print(f"  Aligned: {result['aligned']}")
    print(f"  Details: {result['details']}")
    print()

    print("✅ All basic validation tests completed!")

if __name__ == "__main__":
    test_basic_functionality()
