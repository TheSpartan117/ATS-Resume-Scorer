#!/usr/bin/env python3
"""Quick test to verify quality scorer imports and basic functionality"""

import sys
sys.path.insert(0, '/Users/sabuj.mondal/ats-resume-scorer/backend')

from services.scorer_quality import QualityScorer
from services.parser import ResumeData

def test_basic_functionality():
    """Test basic scorer functionality"""
    print("Testing QualityScorer...")

    # Create scorer
    scorer = QualityScorer()
    print("✓ Scorer initialized")

    # Create sample resume
    resume = ResumeData(
        fileName="test.pdf",
        contact={
            "name": "Jane Doe",
            "email": "jane@gmail.com",
            "phone": "555-1234"
        },
        experience=[{
            "title": "Software Engineer",
            "company": "Tech Co",
            "startDate": "Jan 2020",
            "endDate": "Present",
            "description": """
- Developed microservices reducing latency by 40%
- Led team of 5 engineers
- Implemented CI/CD pipeline
            """
        }],
        education=[{
            "degree": "BS Computer Science",
            "institution": "University"
        }],
        skills=["Python", "AWS", "Docker"],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 400, "hasPhoto": False, "fileFormat": "pdf"}
    )
    print("✓ Sample resume created")

    # Score resume
    try:
        result = scorer.score(resume, "software_engineer", "mid")
        print("✓ Scoring completed")

        # Validate structure
        assert 'score' in result, "Missing 'score' in result"
        assert 'breakdown' in result, "Missing 'breakdown' in result"
        print(f"✓ Score: {result['score']}")

        # Check breakdown
        breakdown = result['breakdown']
        required_categories = ['content_quality', 'achievement_depth', 'keywords_fit', 'polish', 'readability']
        for cat in required_categories:
            assert cat in breakdown, f"Missing category: {cat}"
            assert 'score' in breakdown[cat], f"Missing score in {cat}"
            assert 'max_score' in breakdown[cat], f"Missing max_score in {cat}"
            assert 'details' in breakdown[cat], f"Missing details in {cat}"
            print(f"  ✓ {cat}: {breakdown[cat]['score']}/{breakdown[cat]['max_score']}")

        # Verify max scores sum to 100
        total_max = sum(cat['max_score'] for cat in breakdown.values())
        assert total_max == 100, f"Max scores should sum to 100, got {total_max}"
        print(f"✓ Max scores sum correctly: {total_max}")

        print("\n✓ All tests passed!")
        return True

    except Exception as e:
        print(f"✗ Error during scoring: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_basic_functionality()
    sys.exit(0 if success else 1)
