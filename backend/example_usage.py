#!/usr/bin/env python3
"""
Example usage of ResumeScorer - Main Scorer Orchestrator.

This demonstrates the key features of the ResumeScorer class:
1. ATS mode scoring with job description
2. Quality mode scoring without job description
3. Score interpretation
4. Actionable recommendations
5. Caching for mode switching
"""

import sys
sys.path.insert(0, '/Users/sabuj.mondal/ats-resume-scorer/backend')

from services.scorer_v2 import ResumeScorer
from services.parser import ResumeData
from services.role_taxonomy import ExperienceLevel


def print_separator():
    print("\n" + "="*70 + "\n")


def print_result(result, title):
    """Pretty print scoring result"""
    print(f"📊 {title}")
    print(f"   Score: {result['score']:.1f}/100")
    print(f"   Interpretation: {result['interpretation']}")
    print(f"   Mode: {result['mode']}")

    print(f"\n   📋 Breakdown:")
    for category, data in result['breakdown'].items():
        score = data['score']
        max_score = data['maxScore']
        pct = (score / max_score * 100) if max_score > 0 else 0
        print(f"      • {category}: {score:.1f}/{max_score} ({pct:.0f}%)")

    if result.get('strengths'):
        print(f"\n   💪 Strengths:")
        for strength in result['strengths']:
            print(f"      • {strength}")

    if result.get('recommendations'):
        print(f"\n   💡 Recommendations:")
        for i, rec in enumerate(result['recommendations'][:5], 1):
            print(f"      {i}. {rec}")

    if result.get('keyword_details'):
        kw = result['keyword_details']
        print(f"\n   🔑 Keywords:")
        if 'required_matched' in kw:
            print(f"      Required: {kw['required_matched']}/{kw['required_total']} ({kw['required_match_pct']:.0f}%)")
        if 'preferred_matched' in kw:
            print(f"      Preferred: {kw['preferred_matched']}/{kw['preferred_total']} ({kw['preferred_match_pct']:.0f}%)")


def example_1_ats_mode():
    """Example 1: ATS Mode with Job Description"""
    print("EXAMPLE 1: ATS Mode (Keyword-Heavy)")
    print_separator()

    # Create sample resume
    resume = ResumeData(
        fileName="john_doe_resume.pdf",
        contact={
            "name": "John Doe",
            "email": "john.doe@email.com",
            "phone": "+1-555-0100"
        },
        experience=[{
            "title": "Senior Software Engineer",
            "company": "Tech Corp",
            "description": """
            • Led team of 5 engineers building microservices with Python and AWS
            • Reduced deployment time by 60% through CI/CD automation
            • Implemented Kubernetes orchestration for container management
            • Designed RESTful APIs using Flask and FastAPI
            """
        }, {
            "title": "Software Engineer",
            "company": "StartUp Inc",
            "description": """
            • Developed full-stack web applications using React and Node.js
            • Implemented Docker containerization for development environments
            • Collaborated with product team on feature requirements
            """
        }],
        education=[{
            "degree": "BS Computer Science",
            "institution": "Stanford University"
        }],
        skills=["Python", "AWS", "Docker", "Kubernetes", "React", "Flask", "FastAPI"],
        certifications=[],
        metadata={
            "pageCount": 1,
            "wordCount": 450,
            "hasPhoto": False,
            "fileFormat": "pdf"
        }
    )

    # Job description
    job_description = """
    Senior Backend Engineer

    Required Skills:
    - Python programming (5+ years)
    - AWS cloud services (EC2, S3, Lambda)
    - Docker and containerization
    - Kubernetes orchestration
    - Microservices architecture
    - RESTful API design

    Preferred Skills:
    - React or Vue.js
    - TypeScript
    - GraphQL
    - CI/CD pipelines
    - Agile methodologies
    """

    # Score in ATS mode
    scorer = ResumeScorer()
    result = scorer.score(
        resume=resume,
        role="software_engineer",
        level=ExperienceLevel.SENIOR,
        mode='ats',
        job_description=job_description
    )

    print_result(result, "ATS Simulation Results")

    if result.get('auto_reject'):
        print(f"\n   ⚠️  AUTO-REJECT: {result['rejection_reason']}")


def example_2_quality_mode():
    """Example 2: Quality Mode without Job Description"""
    print("EXAMPLE 2: Quality Mode (Balanced Scoring)")
    print_separator()

    # Same resume as Example 1
    resume = ResumeData(
        fileName="john_doe_resume.pdf",
        contact={
            "name": "John Doe",
            "email": "john.doe@email.com",
            "phone": "+1-555-0100"
        },
        experience=[{
            "title": "Senior Software Engineer",
            "company": "Tech Corp",
            "description": """
            • Led team of 5 engineers building microservices with Python and AWS
            • Reduced deployment time by 60% through CI/CD automation
            • Implemented Kubernetes orchestration for container management
            • Designed RESTful APIs using Flask and FastAPI
            """
        }, {
            "title": "Software Engineer",
            "company": "StartUp Inc",
            "description": """
            • Developed full-stack web applications using React and Node.js
            • Implemented Docker containerization for development environments
            • Collaborated with product team on feature requirements
            """
        }],
        education=[{
            "degree": "BS Computer Science",
            "institution": "Stanford University"
        }],
        skills=["Python", "AWS", "Docker", "Kubernetes", "React", "Flask", "FastAPI"],
        certifications=[],
        metadata={
            "pageCount": 1,
            "wordCount": 450,
            "hasPhoto": False,
            "fileFormat": "pdf"
        }
    )

    # Score in Quality mode (no job description needed)
    scorer = ResumeScorer()
    result = scorer.score(
        resume=resume,
        role="software_engineer",
        level=ExperienceLevel.SENIOR,
        mode='quality'
    )

    print_result(result, "Quality Coach Results")

    if result.get('cta'):
        print(f"\n   📢 Call to Action: {result['cta']}")


def example_3_mode_switching():
    """Example 3: Quick Mode Switching with Cache"""
    print("EXAMPLE 3: Mode Switching with Caching")
    print_separator()

    resume = ResumeData(
        fileName="jane_smith_resume.pdf",
        contact={
            "name": "Jane Smith",
            "email": "jane@email.com",
            "phone": "+1-555-0200"
        },
        experience=[{
            "title": "Data Scientist",
            "company": "AI Labs",
            "description": """
            • Built machine learning models using Python and TensorFlow
            • Improved prediction accuracy by 25% through feature engineering
            • Deployed models to production using AWS SageMaker
            """
        }],
        education=[{
            "degree": "MS Data Science",
            "institution": "MIT"
        }],
        skills=["Python", "TensorFlow", "AWS", "Machine Learning", "SQL"],
        certifications=[],
        metadata={
            "pageCount": 1,
            "wordCount": 350,
            "hasPhoto": False,
            "fileFormat": "pdf"
        }
    )

    job_description = """
    Required: Python, Machine Learning, TensorFlow, AWS
    Preferred: PyTorch, Docker, Kubernetes
    """

    # Initialize scorer with caching
    scorer = ResumeScorer()

    # Simulate caching validation results
    resume_hash = "jane_smith_abc123"
    validation_cache = {
        "grammar_checked": True,
        "format_validated": True,
        "timestamp": "2026-02-19T10:00:00Z"
    }
    scorer.cache_validation_results(resume_hash, validation_cache)
    print("✓ Cached validation results for resume")

    # Score in ATS mode
    print("\nScoring in ATS mode...")
    ats_result = scorer.score(
        resume=resume,
        role="data_scientist",
        level=ExperienceLevel.MID,
        mode='ats',
        job_description=job_description
    )
    print(f"   ATS Score: {ats_result['score']:.1f} ({ats_result['interpretation']})")

    # Quick switch to Quality mode (using cached validation)
    print("\nSwitching to Quality mode...")
    quality_result = scorer.score(
        resume=resume,
        role="data_scientist",
        level=ExperienceLevel.MID,
        mode='quality'
    )
    print(f"   Quality Score: {quality_result['score']:.1f} ({quality_result['interpretation']})")

    # Retrieve cached validation
    cached = scorer.get_cached_validation(resume_hash)
    if cached:
        print(f"\n✓ Retrieved cached validation: {cached}")

    # Clean up
    scorer.clear_cache()
    print("✓ Cache cleared")


def example_4_interpretation_ranges():
    """Example 4: Score Interpretation Ranges"""
    print("EXAMPLE 4: Score Interpretation Ranges")
    print_separator()

    scorer = ResumeScorer()

    test_scores = [95, 80, 70, 55, 30]

    print("Score → Interpretation:")
    for score in test_scores:
        interpretation = scorer._interpret_score(score)
        print(f"   {score:3d}/100 → {interpretation}")

    print("\nInterpretation Ranges:")
    print("   86-100: Excellent")
    print("   76-85:  Very good")
    print("   61-75:  Good")
    print("   41-60:  Needs improvement")
    print("   0-40:   Needs significant improvement")


def main():
    """Run all examples"""
    print("\n" + "="*70)
    print(" ResumeScorer - Main Scorer Orchestrator Examples")
    print("="*70)

    try:
        example_1_ats_mode()
        print_separator()

        example_2_quality_mode()
        print_separator()

        example_3_mode_switching()
        print_separator()

        example_4_interpretation_ranges()
        print_separator()

        print("✓ All examples completed successfully!")
        print("="*70 + "\n")

    except Exception as e:
        print(f"\n✗ Error running examples: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
