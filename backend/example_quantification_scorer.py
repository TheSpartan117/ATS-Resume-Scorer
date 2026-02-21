#!/usr/bin/env python3
"""
Example usage of QuantificationScorer (P2.2)

Demonstrates real-world usage with sample resumes at different levels.
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from services.quantification_scorer import QuantificationScorer


def print_result(title: str, result: dict):
    """Pretty print scoring result."""
    print(f"\n{'='*70}")
    print(f"{title}")
    print(f"{'='*70}")
    print(f"Score: {result['score']}/10 points")
    print(f"Weighted Rate: {result['weighted_quantification_rate']}%")
    print(f"Threshold: {result['threshold']}% ({result['level']} level)")
    print(f"\nQuality Breakdown:")
    print(f"  - High-value metrics: {result['high_count']}")
    print(f"  - Medium-value metrics: {result['medium_count']}")
    print(f"  - Low-value metrics: {result['low_count']}")
    print(f"  - Total quantified: {result['quantified_count']}/{result['total_bullets']}")
    print(f"\nExplanation:")
    print(f"  {result['explanation']}")


def example_beginner_resume():
    """Example: Entry-level software engineer (0-3 years)"""
    print("\n" + "█"*70)
    print("EXAMPLE 1: Beginner Software Engineer (0-3 years)")
    print("█"*70)

    scorer = QuantificationScorer()

    # Weak resume - no quantification
    weak_bullets = [
        "Developed web applications using React",
        "Worked on backend API development",
        "Collaborated with team members",
        "Improved code quality",
        "Fixed bugs and issues"
    ]
    print("\n--- Weak Resume (No Metrics) ---")
    result = scorer.score(weak_bullets, 'beginner')
    print_result("WEAK: No Quantification", result)

    print("\nRecommendations:")
    for i, rec in enumerate(scorer.get_recommendations(result), 1):
        print(f"  {i}. {rec}")

    # Strong resume - good quantification
    strong_bullets = [
        "Developed 5 React components, reducing page load time by 30%",
        "Built REST API serving 10K+ daily requests",
        "Fixed 25+ bugs, improving app stability by 40%",
        "Collaborated with team of 6 developers",
        "Completed bootcamp project in 8 weeks"
    ]
    print("\n\n--- Strong Resume (Well Quantified) ---")
    result = scorer.score(strong_bullets, 'beginner')
    print_result("STRONG: Good Quantification", result)


def example_intermediary_resume():
    """Example: Mid-level product manager (3-7 years)"""
    print("\n\n" + "█"*70)
    print("EXAMPLE 2: Intermediary Product Manager (3-7 years)")
    print("█"*70)

    scorer = QuantificationScorer()

    # Mediocre resume - some quantification
    mediocre_bullets = [
        "Managed product roadmap and priorities",
        "Led cross-functional team",
        "Launched 3 new features in Q4",
        "Improved user engagement metrics",
        "Conducted user research sessions",
        "Collaborated with engineering team"
    ]
    print("\n--- Mediocre Resume (Weak Metrics) ---")
    result = scorer.score(mediocre_bullets, 'intermediary')
    print_result("MEDIOCRE: Insufficient Quantification", result)

    print("\nRecommendations:")
    for i, rec in enumerate(scorer.get_recommendations(result), 1):
        print(f"  {i}. {rec}")

    # Excellent resume - strong quantification
    excellent_bullets = [
        "Increased monthly active users by 150% (from 50K to 125K)",
        "Launched 3 features generating $500K incremental revenue",
        "Led cross-functional team of 12 across design, eng, marketing",
        "Improved user retention by 35% through A/B testing",
        "Reduced customer churn from 8% to 5% (38% improvement)",
        "Delivered product roadmap in 6 months, 2 weeks ahead of schedule"
    ]
    print("\n\n--- Excellent Resume (Strong Business Impact) ---")
    result = scorer.score(excellent_bullets, 'intermediary')
    print_result("EXCELLENT: Strong Quantification", result)


def example_senior_resume():
    """Example: Senior engineering manager (7+ years)"""
    print("\n\n" + "█"*70)
    print("EXAMPLE 3: Senior Engineering Manager (7+ years)")
    print("█"*70)

    scorer = QuantificationScorer()

    # Weak senior resume - insufficient for level
    weak_senior_bullets = [
        "Led engineering team",
        "Architected microservices platform",
        "Mentored junior developers",
        "Improved system reliability",
        "Drove technical strategy",
        "Collaborated with executive team"
    ]
    print("\n--- Weak Senior Resume (No Metrics) ---")
    result = scorer.score(weak_senior_bullets, 'senior')
    print_result("WEAK: Insufficient for Senior Level", result)

    print("\nRecommendations:")
    for i, rec in enumerate(scorer.get_recommendations(result), 1):
        print(f"  {i}. {rec}")

    # Strong senior resume - leadership + impact
    strong_senior_bullets = [
        "Scaled platform to 10M+ users, achieving 99.99% uptime (4x growth)",
        "Reduced infrastructure costs by $2M annually (40% savings)",
        "Led engineering org of 50+ across 6 teams, 3 time zones",
        "Improved deployment frequency from weekly to daily (7x faster)",
        "Grew team from 15 to 50 engineers over 2 years",
        "Architected microservices migration, reducing latency by 60%"
    ]
    print("\n\n--- Strong Senior Resume (Leadership + Impact) ---")
    result = scorer.score(strong_senior_bullets, 'senior')
    print_result("STRONG: Excellent Senior Quantification", result)


def example_quality_comparison():
    """Compare different metric qualities"""
    print("\n\n" + "█"*70)
    print("EXAMPLE 4: Metric Quality Comparison")
    print("█"*70)

    scorer = QuantificationScorer()

    # Low-quality metrics only
    low_quality = [
        "Fixed 20 bugs",
        "Attended 15 meetings",
        "Worked on 8 projects",
        "Completed 12 tasks",
        "Reviewed 30 pull requests"
    ]
    print("\n--- LOW Quality Metrics (Bare Numbers) ---")
    result = scorer.score(low_quality, 'intermediary')
    print_result("LOW: Activity Counts", result)

    # Medium-quality metrics
    medium_quality = [
        "Led team of 8 engineers",
        "Completed project in 6 months",
        "Managed 12 concurrent features",
        "Serving 100K+ active users",
        "Supported 5 cross-functional teams"
    ]
    print("\n\n--- MEDIUM Quality Metrics (Scope Indicators) ---")
    result = scorer.score(medium_quality, 'intermediary')
    print_result("MEDIUM: Team/Time/Scale", result)

    # High-quality metrics
    high_quality = [
        "Increased revenue by 45%",
        "Reduced costs by $200K annually",
        "Improved performance 3x faster",
        "Boosted conversion from 2% to 8% (4x increase)",
        "Cut deployment time from 2 hours to 15 minutes"
    ]
    print("\n\n--- HIGH Quality Metrics (Business Impact) ---")
    result = scorer.score(high_quality, 'intermediary')
    print_result("HIGH: Business Impact", result)

    # Mixed quality - realistic resume
    mixed_quality = [
        "Increased user retention by 35%",           # HIGH
        "Led team of 10 engineers",                  # MEDIUM
        "Serving 500K+ monthly active users",        # MEDIUM
        "Fixed 50+ critical bugs",                   # LOW
        "Developed new feature set",                 # NONE
        "Collaborated with stakeholders"             # NONE
    ]
    print("\n\n--- MIXED Quality (Realistic Resume) ---")
    result = scorer.score(mixed_quality, 'intermediary')
    print_result("MIXED: Typical Resume", result)


def example_improvement_journey():
    """Show progression from weak to strong"""
    print("\n\n" + "█"*70)
    print("EXAMPLE 5: Resume Improvement Journey")
    print("█"*70)

    scorer = QuantificationScorer()

    print("\n--- VERSION 1: Initial (Vague) ---")
    v1 = [
        "Developed web applications",
        "Improved system performance",
        "Worked on various projects",
        "Collaborated with team"
    ]
    result_v1 = scorer.score(v1, 'intermediary')
    print(f"Score: {result_v1['score']}/10, Rate: {result_v1['weighted_quantification_rate']}%")

    print("\n--- VERSION 2: Added Numbers (Low Quality) ---")
    v2 = [
        "Developed 5 web applications",
        "Improved system performance",
        "Worked on 10 projects",
        "Collaborated with team of 6"
    ]
    result_v2 = scorer.score(v2, 'intermediary')
    print(f"Score: {result_v2['score']}/10, Rate: {result_v2['weighted_quantification_rate']}%")
    print(f"Improvement: +{result_v2['score'] - result_v1['score']} points")

    print("\n--- VERSION 3: Added Scope (Medium Quality) ---")
    v3 = [
        "Developed 5 web applications serving 50K users",
        "Improved system performance over 6 months",
        "Led 10 concurrent projects",
        "Collaborated with cross-functional team of 6"
    ]
    result_v3 = scorer.score(v3, 'intermediary')
    print(f"Score: {result_v3['score']}/10, Rate: {result_v3['weighted_quantification_rate']}%")
    print(f"Improvement: +{result_v3['score'] - result_v2['score']} points")

    print("\n--- VERSION 4: Added Impact (High Quality) ---")
    v4 = [
        "Developed 5 applications serving 50K users, increasing engagement by 40%",
        "Improved system performance by 60% (from 500ms to 200ms)",
        "Led 10 concurrent projects, delivering $300K revenue",
        "Collaborated with team of 6, reducing time-to-market by 30%"
    ]
    result_v4 = scorer.score(v4, 'intermediary')
    print(f"Score: {result_v4['score']}/10, Rate: {result_v4['weighted_quantification_rate']}%")
    print(f"Improvement: +{result_v4['score'] - result_v3['score']} points")
    print(f"\nTotal Journey: {result_v1['score']} → {result_v4['score']} points ({result_v4['score'] - result_v1['score']} point gain!)")


def main():
    """Run all examples."""
    print("="*70)
    print("QUANTIFICATION SCORER (P2.2) - EXAMPLES")
    print("="*70)
    print("\nDemonstrating weighted metric quality scoring across experience levels.")
    print("Weights: HIGH=1.0 (business impact), MEDIUM=0.7 (scope), LOW=0.3 (bare numbers)")

    example_beginner_resume()
    example_intermediary_resume()
    example_senior_resume()
    example_quality_comparison()
    example_improvement_journey()

    print("\n\n" + "="*70)
    print("EXAMPLES COMPLETE")
    print("="*70)
    print("\nKey Takeaways:")
    print("1. Business impact metrics (%, $, multipliers) score highest")
    print("2. Scope indicators (team sizes, durations, scale) are valuable")
    print("3. Bare numbers without context score lowest")
    print("4. Higher experience levels require more quantification")
    print("5. Quality matters more than quantity")


if __name__ == "__main__":
    main()
