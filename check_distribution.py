#!/usr/bin/env python3
"""
Quick check to show the actual distribution without running full pytest.
This helps verify our understanding of the current behavior.
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from backend.services.parser import ResumeData
from backend.services.scorer_v2 import AdaptiveScorer
from backend.services.role_taxonomy import ExperienceLevel


def quick_distribution_check():
    """
    Create a few test resumes and check their scores in Quality Coach mode.
    """
    print("=" * 80)
    print("Quick Distribution Check - Quality Coach Mode")
    print("=" * 80)

    scorer = AdaptiveScorer()

    # Create a few test resumes representing different quality levels
    test_cases = [
        {
            "name": "Empty Resume (Poor)",
            "data": ResumeData(
                fileName="empty.pdf",
                contact={},
                experience=[],
                education=[],
                skills=[],
                certifications=[],
                metadata={"pageCount": 1, "wordCount": 50, "hasPhoto": False, "fileFormat": "pdf"}
            )
        },
        {
            "name": "Minimal Resume (Poor)",
            "data": ResumeData(
                fileName="minimal.pdf",
                contact={"email": "user@example.com"},
                experience=[{"title": "Worker", "company": "Company"}],
                education=[],
                skills=["Excel"],
                certifications=[],
                metadata={"pageCount": 1, "wordCount": 80, "hasPhoto": True, "fileFormat": "docx"}
            )
        },
        {
            "name": "Basic Resume (Mediocre)",
            "data": ResumeData(
                fileName="basic.pdf",
                contact={"name": "John Doe", "email": "john@example.com", "phone": "555-1234"},
                experience=[{
                    "title": "Software Developer",
                    "company": "Tech Co",
                    "description": "Built features. Fixed bugs. Improved performance by 15%."
                }],
                education=[{"degree": "BS Computer Science"}],
                skills=["Python", "JavaScript", "React"],
                certifications=[],
                metadata={"pageCount": 1, "wordCount": 300, "hasPhoto": False, "fileFormat": "pdf"}
            )
        },
        {
            "name": "Good Resume (Good)",
            "data": ResumeData(
                fileName="good.pdf",
                contact={
                    "name": "Jane Smith",
                    "email": "jane@example.com",
                    "phone": "555-5678",
                    "location": "San Francisco, CA",
                    "linkedin": "linkedin.com/in/janesmith"
                },
                experience=[{
                    "title": "Senior Software Engineer",
                    "company": "BigTech Corp",
                    "description": "- Developed 12 microservices using Python and FastAPI\n"
                                 "- Reduced API latency by 40% through optimization\n"
                                 "- Mentored 3 junior developers\n"
                                 "- Implemented CI/CD pipeline reducing deployment time by 60%"
                }],
                education=[{"degree": "BS Computer Science", "institution": "Stanford University"}],
                skills=["Python", "FastAPI", "Docker", "Kubernetes", "AWS", "PostgreSQL"],
                certifications=[{"name": "AWS Certified Developer"}],
                metadata={"pageCount": 2, "wordCount": 600, "hasPhoto": False, "fileFormat": "pdf"}
            )
        }
    ]

    scores = []
    for test_case in test_cases:
        result = scorer.score(
            resume_data=test_case["data"],
            role_id="software_engineer",
            level=ExperienceLevel("mid"),
            job_description=None,  # Quality Coach mode
            mode="auto"
        )

        score = result["overallScore"]
        scores.append(score)

        print(f"\n{test_case['name']}:")
        print(f"  Score: {score:.1f}/100")
        print(f"  Mode: {result['mode']}")

        breakdown = result["breakdown"]
        print(f"  Breakdown:")
        print(f"    - Role Keywords: {breakdown['role_keywords']['score']:.1f}/25")
        print(f"    - Content Quality: {breakdown['content_quality']['score']:.1f}/30")
        print(f"    - Format: {breakdown['format']['score']:.1f}/25")
        print(f"    - Professional Polish: {breakdown['professional_polish']['score']:.1f}/20")

    # Calculate simple distribution
    poor_count = sum(1 for s in scores if s <= 40)
    mediocre_count = sum(1 for s in scores if 41 <= s <= 60)
    good_count = sum(1 for s in scores if 61 <= s <= 75)
    very_good_count = sum(1 for s in scores if 76 <= s <= 85)
    exceptional_count = sum(1 for s in scores if s > 85)

    total = len(scores)

    print("\n" + "=" * 80)
    print("Distribution Summary")
    print("=" * 80)
    print(f"Total resumes: {total}")
    print(f"Average score: {sum(scores) / total:.1f}")
    print(f"\nDistribution:")
    print(f"  0-40 (Poor):        {poor_count}/{total} ({poor_count/total*100:.1f}%)")
    print(f"  41-60 (Mediocre):   {mediocre_count}/{total} ({mediocre_count/total*100:.1f}%)")
    print(f"  61-75 (Good):       {good_count}/{total} ({good_count/total*100:.1f}%)")
    print(f"  76-85 (Very Good):  {very_good_count}/{total} ({very_good_count/total*100:.1f}%)")
    print(f"  86-100 (Exception): {exceptional_count}/{total} ({exceptional_count/total*100:.1f}%)")

    print("\n" + "=" * 80)
    print("Interpretation")
    print("=" * 80)
    print("Quality Coach mode is intentionally generous:")
    print("- Only truly deficient resumes score below 40")
    print("- Resumes with some content/structure get 40+ even if flawed")
    print("- This encourages candidates while providing constructive feedback")
    print("=" * 80)


if __name__ == "__main__":
    quick_distribution_check()
