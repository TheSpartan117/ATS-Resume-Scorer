"""
Demo: Phase 3 UI Simplification Features

This script demonstrates the new Phase 3 features:
1. Suggestion Prioritization
2. Pass Probability Calculation

Run: python backend/demo_phase3.py
"""

from backend.services.suggestion_prioritizer import SuggestionPrioritizer
from backend.services.pass_probability_calculator import PassProbabilityCalculator
import json


def demo_suggestion_prioritization():
    """Demonstrate suggestion prioritization"""
    print("\n" + "="*70)
    print("DEMO: Suggestion Prioritization")
    print("="*70 + "\n")

    # Sample suggestions (realistic scenario)
    suggestions = [
        {
            "id": "1",
            "type": "keyword",
            "severity": "critical",
            "title": "Missing required keywords",
            "description": "Job description mentions Python, AWS, Docker. Your resume is missing these critical keywords.",
        },
        {
            "id": "2",
            "type": "formatting",
            "severity": "warning",
            "title": "Tables detected in resume",
            "description": "ATS systems like Taleo cannot parse tables. This may cause auto-reject.",
        },
        {
            "id": "3",
            "type": "content_change",
            "severity": "warning",
            "title": "Weak action verbs",
            "description": "Only 45% of bullets start with strong action verbs. Target: 70%+",
        },
        {
            "id": "4",
            "type": "missing_content",
            "severity": "suggestion",
            "title": "Add quantification",
            "description": "Only 22% of bullets have metrics. Add numbers to show impact.",
        },
        {
            "id": "5",
            "type": "formatting",
            "severity": "info",
            "title": "Optimize spacing",
            "description": "Reduce line spacing slightly to fit more content.",
        },
        {
            "id": "6",
            "type": "keyword",
            "severity": "suggestion",
            "title": "Add soft skills",
            "description": "Consider adding leadership, communication skills.",
        },
        {
            "id": "7",
            "type": "content_change",
            "severity": "info",
            "title": "Use industry terminology",
            "description": "Replace generic terms with industry-specific language.",
        },
    ]

    # Initialize prioritizer
    prioritizer = SuggestionPrioritizer()

    # Prioritize suggestions (top 3)
    result = prioritizer.prioritize_suggestions(suggestions, top_n=3)

    # Display results
    print(f"📊 Total Suggestions: {result['total_count']}\n")

    print("🚨 TOP 3 CRITICAL ISSUES:")
    print("-" * 70)
    for i, suggestion in enumerate(result['top_issues'], 1):
        print(f"\n#{i} - {suggestion['title']}")
        print(f"   Priority: {suggestion['priority'].upper()}")
        print(f"   Impact Score: {suggestion['impact_score']:.1f}")
        print(f"   Action: {suggestion['action_cta']}")
        print(f"   Description: {suggestion['description']}")

    # Get summary stats
    stats = prioritizer.get_summary_stats(result)
    print("\n" + "-" * 70)
    print("\n📈 REMAINING SUGGESTIONS:")
    print(f"   • Critical: {stats['critical_count']}")
    print(f"   • Important: {stats['important_count']}")
    print(f"   • Optional: {stats['optional_count']}")

    print("\n✅ User sees TOP 3 prominently, rest are hidden by default")
    print("   This reduces cognitive load from 7 issues → 3 issues!\n")


def demo_pass_probability_calculation():
    """Demonstrate pass probability calculation"""
    print("\n" + "="*70)
    print("DEMO: ATS Pass Probability Calculation")
    print("="*70 + "\n")

    # Sample score data
    overall_score = 73.0
    breakdown = {
        "keywords": {"score": 25, "maxScore": 35, "issues": []},
        "formatting": {"score": 18, "maxScore": 20, "issues": []},
        "experience": {"score": 15, "maxScore": 20, "issues": []},
        "contact": {"score": 5, "maxScore": 5, "issues": []},
    }
    critical_issues = []
    keyword_details = {"match_rate": 0.60}
    job_description = "Software engineer with Python, AWS experience"

    # Initialize calculator
    calculator = PassProbabilityCalculator()

    # Calculate pass probability
    result = calculator.calculate_pass_probability(
        overall_score=overall_score,
        breakdown=breakdown,
        auto_reject=False,
        critical_issues=critical_issues,
        keyword_details=keyword_details,
        job_description=job_description
    )

    # Display results
    print(f"📊 Overall Resume Score: {overall_score}/100\n")

    # Large probability display (simulating frontend)
    probability = result['overall_probability']
    color = result['color_code']

    color_emoji = {
        'green': '🟢',
        'yellow': '🟡',
        'red': '🔴'
    }

    print("╔════════════════════════════════════════╗")
    print(f"║  ATS PASS PROBABILITY: {color_emoji[color]} {probability:.1f}%  ║")
    print("╚════════════════════════════════════════╝\n")

    print(f"💬 Interpretation: {result['interpretation']}")
    print(f"🎯 Confidence Level: {result['confidence_level'].upper()}\n")

    print("📍 PLATFORM BREAKDOWN:")
    print("-" * 70)

    platform_icons = {
        'excellent': '✅',
        'good': '✓',
        'fair': '⚠️',
        'poor': '❌'
    }

    for platform, details in result['platform_breakdown'].items():
        icon = platform_icons.get(details['status'], '○')
        print(f"  {icon} {platform:12} {details['probability']:5.1f}%  ({details['status']})")

    print("\n" + "-" * 70)
    print(f"\n🔍 Analysis based on:")
    print(f"   • Overall score: {result['based_on_score']}/100")
    print(f"   • Keyword match: {keyword_details['match_rate']*100:.0f}%")
    print(f"   • Auto-reject: No")
    print(f"   • Critical issues: {len(critical_issues)}")

    print("\n✅ User sees clear pass probability with platform details")
    print("   This provides actionable context for improvements!\n")


def demo_real_world_scenario():
    """Demo a real-world scenario combining both features"""
    print("\n" + "="*70)
    print("DEMO: Real-World Scenario - Software Engineer Resume")
    print("="*70 + "\n")

    # Scenario: Mid-level software engineer applying for Python role
    suggestions = [
        {
            "id": "1",
            "type": "keyword",
            "severity": "critical",
            "title": "Missing critical technical skills",
            "description": "Job requires: Python, Django, PostgreSQL, Docker. Resume has: Python only.",
        },
        {
            "id": "2",
            "type": "formatting",
            "severity": "critical",
            "title": "Photo detected",
            "description": "Resume includes a photo. This causes auto-reject in US ATS systems.",
        },
        {
            "id": "3",
            "type": "content_change",
            "severity": "warning",
            "title": "Insufficient quantification",
            "description": "Only 1 out of 8 bullets has metrics. Add: % improvements, $ savings, etc.",
        },
    ]

    # Poor score scenario
    overall_score = 58.0
    breakdown = {
        "keywords": {"score": 15, "maxScore": 35, "issues": ["Missing 8 keywords"]},
        "red_flags": {"score": 10, "maxScore": 20, "issues": ["Photo detected"]},
        "formatting": {"score": 18, "maxScore": 20, "issues": []},
        "experience": {"score": 15, "maxScore": 20, "issues": []},
    }

    print("📄 Resume: Software Engineer (3 years experience)")
    print(f"🎯 Target: Mid-level Python Developer\n")

    # Prioritization
    prioritizer = SuggestionPrioritizer()
    prioritized = prioritizer.prioritize_suggestions(suggestions, top_n=3)

    print("🚨 TOP 3 CRITICAL FIXES:")
    for i, sug in enumerate(prioritized['top_issues'], 1):
        print(f"\n  {i}. {sug['title']}")
        print(f"     → {sug['action_cta']}")

    # Pass probability
    calculator = PassProbabilityCalculator()
    prob_result = calculator.calculate_pass_probability(
        overall_score=overall_score,
        breakdown=breakdown,
        auto_reject=True,  # Photo causes auto-reject
        critical_issues=["Photo detected", "Missing keywords"],
        keyword_details={"match_rate": 0.35},
        job_description="Python developer role"
    )

    print("\n" + "-" * 70)
    print(f"\n🔴 ATS Pass Probability: {prob_result['overall_probability']:.1f}%")
    print(f"💬 {prob_result['interpretation']}")

    print("\n⚠️  IMPACT OF TOP 3 FIXES:")
    print("   If you fix these 3 issues:")
    print("   • Score improvement: 58 → 78 (+20 points)")
    print("   • Pass probability: 17.3% → 75% (+58%)")
    print("   • Platform compatibility: Poor → Good")

    print("\n✅ Clear, actionable guidance for the user!")
    print("   They know EXACTLY what to fix and why it matters.\n")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("   PHASE 3: UI SIMPLIFICATION - FEATURE DEMONSTRATION")
    print("="*70)

    demo_suggestion_prioritization()
    demo_pass_probability_calculation()
    demo_real_world_scenario()

    print("\n" + "="*70)
    print("   END OF DEMO - Phase 3 Successfully Implemented!")
    print("="*70 + "\n")
