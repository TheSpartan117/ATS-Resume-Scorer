#!/usr/bin/env python3
"""
Example usage of Quality Mode Scorer.
Demonstrates scoring different quality resumes.
"""

import sys
sys.path.insert(0, '/Users/sabuj.mondal/ats-resume-scorer/backend')

from services.scorer_quality import QualityScorer
from services.parser import ResumeData


def create_excellent_resume():
    """Create a high-quality resume example"""
    return ResumeData(
        fileName="excellent_resume.pdf",
        contact={
            "name": "Sarah Johnson",
            "email": "sarah.johnson@gmail.com",
            "phone": "555-123-4567",
            "linkedin": "linkedin.com/in/sarahjohnson",
            "location": "Seattle, WA"
        },
        experience=[{
            "title": "Senior Software Engineer",
            "company": "Tech Corp",
            "startDate": "Jan 2020",
            "endDate": "Present",
            "description": """
- Architected microservices platform reducing deployment time by 70% for 100+ services
- Led team of 10 engineers delivering cloud migration, saving $500K annually
- Implemented automated CI/CD pipeline increasing release velocity by 5x
- Optimized database queries improving API response time by 60%
- Developed monitoring system detecting 95% of production issues proactively
- Mentored 5 junior engineers, with 3 promoted to mid-level roles
            """
        }, {
            "title": "Software Engineer",
            "company": "Startup Inc",
            "startDate": "Jun 2018",
            "endDate": "Dec 2019",
            "description": """
- Built RESTful APIs serving 200K+ daily active users with 99.9% uptime
- Reduced infrastructure costs by 40% through optimization and right-sizing
- Launched mobile app features improving user engagement by 35%
- Implemented real-time data pipeline processing 1M+ events daily
            """
        }],
        education=[{
            "degree": "BS Computer Science",
            "institution": "University of Washington",
            "graduationDate": "2018",
            "gpa": "3.8"
        }],
        skills=[
            "Python", "Java", "AWS", "Docker", "Kubernetes", "React",
            "Node.js", "PostgreSQL", "Redis", "CI/CD", "Microservices"
        ],
        certifications=[{"name": "AWS Certified Solutions Architect"}],
        metadata={"pageCount": 1, "wordCount": 550, "hasPhoto": False, "fileFormat": "pdf"}
    )


def create_poor_resume():
    """Create a low-quality resume example"""
    return ResumeData(
        fileName="poor_resume.pdf",
        contact={
            "name": "John Smith",
            "email": "john_smith_99@hotmail.com",
            "phone": "5551234567"
        },
        experience=[{
            "title": "Software Developer",
            "company": "Some Company",
            "startDate": "2020",
            "endDate": "2022",
            "description": """
- Worked on various projects
- Responsible for coding tasks
- Helped with debugging
- Participated in team meetings
- Assisted senior developers
            """
        }],
        education=[{
            "degree": "Computer Science",
            "institution": "State College"
        }],
        skills=["Java", "SQL", "Git"],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 150, "hasPhoto": False, "fileFormat": "pdf"}
    )


def print_score_report(name: str, result: dict):
    """Print a formatted score report"""
    print(f"\n{'='*60}")
    print(f"QUALITY SCORE REPORT: {name}")
    print(f"{'='*60}")
    print(f"\nOverall Score: {result['score']:.1f}/100")
    print(f"\nCategory Breakdown:")
    print(f"{'Category':<25} {'Score':<15} {'Max':<10}")
    print(f"{'-'*50}")

    for category, data in result['breakdown'].items():
        cat_name = category.replace('_', ' ').title()
        print(f"{cat_name:<25} {data['score']:.1f:<15} {data['max_score']:<10}")

    # Print some detailed feedback
    print(f"\n{'='*60}")
    print("DETAILED FEEDBACK:")
    print(f"{'='*60}")

    # Content Quality
    cq = result['breakdown']['content_quality']['details']
    print(f"\nContent Quality:")
    print(f"  - {cq['action_verbs_feedback']}")
    print(f"  - {cq['quantification_feedback']}")
    print(f"  - {cq['depth_feedback']}")

    # Achievement Depth
    ad = result['breakdown']['achievement_depth']['details']
    print(f"\nAchievement Depth:")
    print(f"  - {ad['metrics_feedback']}")
    print(f"  - {ad['vague_feedback']}")

    # Keywords/Fit
    kf = result['breakdown']['keywords_fit']['details']
    print(f"\nKeywords/Fit:")
    print(f"  - {kf['feedback']}")

    # Polish
    pol = result['breakdown']['polish']['details']
    print(f"\nPolish:")
    print(f"  - {pol['grammar_feedback']}")
    print(f"  - {pol['professional_feedback']}")

    # Readability
    read = result['breakdown']['readability']['details']
    print(f"\nReadability:")
    print(f"  - {read['structure_feedback']}")
    print(f"  - {read['length_feedback']}")


def main():
    """Run scoring examples"""
    print("Quality Mode Scorer - Example Usage")
    print("="*60)

    scorer = QualityScorer()

    # Score excellent resume
    print("\n\n1. SCORING EXCELLENT RESUME")
    excellent_resume = create_excellent_resume()
    excellent_result = scorer.score(
        excellent_resume,
        role_id="software_engineer",
        level="senior"
    )
    print_score_report("Excellent Resume", excellent_result)

    # Score poor resume
    print("\n\n2. SCORING POOR RESUME")
    poor_resume = create_poor_resume()
    poor_result = scorer.score(
        poor_resume,
        role_id="software_engineer",
        level="mid"
    )
    print_score_report("Poor Resume", poor_result)

    # Summary comparison
    print("\n\n" + "="*60)
    print("COMPARISON SUMMARY")
    print("="*60)
    print(f"Excellent Resume Score: {excellent_result['score']:.1f}/100")
    print(f"Poor Resume Score: {poor_result['score']:.1f}/100")
    print(f"Difference: {excellent_result['score'] - poor_result['score']:.1f} points")
    print("\nKey Differences:")
    print("- Action verbs: Excellent uses strong verbs, Poor uses vague phrases")
    print("- Quantification: Excellent has metrics (70%, $500K), Poor has none")
    print("- Achievement depth: Excellent shows impact, Poor lists responsibilities")
    print("- Professional polish: Excellent has proper email/format, Poor uses outdated email")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
