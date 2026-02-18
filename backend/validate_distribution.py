#!/usr/bin/env python3
"""
Simple distribution validation script to check scoring calibration.

This script scores 20 test resumes and reports the distribution.
Can be run with: python validate_distribution.py
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from services.parser import ResumeData
from services.scorer_legacy import calculate_overall_score
from services.scorer_v2 import AdaptiveScorer
from services.role_taxonomy import ExperienceLevel


# Simple test resumes covering the quality spectrum
def create_test_resumes():
    """Create 20 test resumes spanning quality levels."""
    return [
        # 6 POOR (0-40)
        ("Empty", ResumeData("empty.pdf", {}, [], [], [], [], {"pageCount": 1, "wordCount": 50, "hasPhoto": False, "fileFormat": "pdf"})),
        ("Minimal", ResumeData("min.pdf", {"email": "a@b.com"}, [{"title": "Worker"}], [], ["Excel"], [], {"pageCount": 1, "wordCount": 80, "hasPhoto": True, "fileFormat": "docx"})),
        ("Too Long", ResumeData("long.pdf", {"name": "John", "email": "j@e.com"}, [{"title": "Dev"}], [{"degree": "BS"}], ["Python"], [], {"pageCount": 5, "wordCount": 1500, "hasPhoto": False, "fileFormat": "pdf"})),
        ("No Contact", ResumeData("nocontact.pdf", {}, [{"title": "Eng", "description": "Responsible for coding"}], [{"degree": "BS CS"}], ["Java", "SQL"], [], {"pageCount": 1, "wordCount": 250, "hasPhoto": False, "fileFormat": "pdf"})),
        ("Passive", ResumeData("passive.pdf", {"name": "Bob", "email": "b@e.com", "phone": "555"}, [{"title": "Dev", "description": "Was responsible for code. Helped with bugs."}], [{"degree": "BS"}], ["HTML"], [], {"pageCount": 1, "wordCount": 200, "hasPhoto": False, "fileFormat": "pdf"})),
        ("No Quant", ResumeData("noquant.pdf", {"name": "Alice", "email": "a@e.com"}, [{"title": "Dev", "description": "Developed features. Fixed bugs."}], [{"degree": "BS CS"}], ["JS", "React"], [], {"pageCount": 1, "wordCount": 180, "hasPhoto": False, "fileFormat": "pdf"})),

        # 8 MEDIOCRE (41-60)
        ("Basic Junior", ResumeData("jr1.pdf", {"name": "Charlie", "email": "c@e.com", "phone": "555"}, [{"title": "Junior Dev", "description": "Developed apps. Fixed 20 bugs."}], [{"degree": "BS CS", "institution": "State U"}], ["Python", "Django"], [], {"pageCount": 1, "wordCount": 300, "hasPhoto": False, "fileFormat": "pdf"})),
        ("Avg Mid", ResumeData("mid1.pdf", {"name": "Diana", "email": "d@e.com", "phone": "555", "location": "Austin"}], [{"title": "Engineer", "description": "Built features. Improved perf by 15%. Used React."}], [{"degree": "BS SE"}], ["React", "Node", "AWS"], [], {"pageCount": 1, "wordCount": 380, "hasPhoto": False, "fileFormat": "pdf"})),
        ("Incomplete", ResumeData("inc.pdf", {"name": "Ethan", "email": "e@e.com", "phone": "555"}, [{"title": "Dev", "description": "- Coded features\n- Fixed bugs\n- Did reviews"}], [{"degree": "BS CS"}], ["Java", "Spring"], [], {"pageCount": 1, "wordCount": 320, "hasPhoto": False, "fileFormat": "pdf"})),
        ("Brief", ResumeData("brief.pdf", {"name": "Fiona", "email": "f@e.com", "phone": "555", "location": "Seattle"}], [{"title": "Full Stack", "description": "- Built 5 apps\n- Reduced load by 25%\n- Worked with design"}], [{"degree": "BS CS"}], ["JS", "Python", "React"], [], {"pageCount": 1, "wordCount": 350, "hasPhoto": False, "fileFormat": "pdf"})),
        ("No Keywords", ResumeData("nokw.pdf", {"name": "George", "email": "g@e.com", "phone": "555"}, [{"title": "Dev", "description": "- Created solutions\n- Enhanced efficiency by 10%\n- Mentored 2 interns"}], [{"degree": "BS IS"}], ["C++", "Qt"], [], {"pageCount": 1, "wordCount": 400, "hasPhoto": False, "fileFormat": "pdf"})),
        ("Weak Verbs", ResumeData("weak.pdf", {"name": "Hannah", "email": "h@e.com", "phone": "555", "location": "Boston"}], [{"title": "Engineer", "description": "- Assisted in developing\n- Helped improve by 12%\n- Involved in testing"}], [{"degree": "BS CE"}], ["Python", "Django"], [], {"pageCount": 1, "wordCount": 360, "hasPhoto": False, "fileFormat": "pdf"})),
        ("Limited", ResumeData("lim.pdf", {"name": "Ian", "email": "i@e.com", "phone": "555"}, [{"title": "Junior SE", "description": "- Implemented 8 features\n- Fixed 30+ bugs\n- Wrote tests"}], [{"degree": "BS CS"}], ["React", "JS", "Jest"], [], {"pageCount": 1, "wordCount": 340, "hasPhoto": False, "fileFormat": "pdf"})),
        ("Generic", ResumeData("gen.pdf", {"name": "Julia", "email": "j@e.com", "phone": "555", "location": "Denver"}], [{"title": "Developer", "description": "- Built apps\n- Improved quality\n- Worked with team"}], [{"degree": "BS SE"}], ["Java", "Spring"], [], {"pageCount": 1, "wordCount": 370, "hasPhoto": False, "fileFormat": "pdf"})),

        # 4 GOOD (61-75)
        ("Good Mid", ResumeData("good1.pdf", {"name": "Kevin", "email": "k@e.com", "phone": "555", "location": "SF", "linkedin": "li.com/kevin"}, [{"title": "Engineer", "description": "- Developed 12 microservices with Python\n- Reduced latency by 40%\n- Mentored 3 juniors\n- Implemented CI/CD reducing deploy time by 60%"}], [{"degree": "BS CS", "institution": "UC"}], ["Python", "FastAPI", "Docker", "K8s", "AWS"], [], {"pageCount": 1, "wordCount": 480, "hasPhoto": False, "fileFormat": "pdf"})),
        ("Strong Jr", ResumeData("good2.pdf", {"name": "Laura", "email": "l@e.com", "phone": "555", "location": "NYC", "linkedin": "li.com/laura", "website": "gh.com/laura"}, [{"title": "Jr Full Stack", "description": "- Built 6 React apps serving 10K+ users\n- Achieved 95% test coverage\n- Optimized queries improving response by 35%"}], [{"degree": "BS CS", "institution": "MIT"}], ["React", "Node", "TS", "Mongo"], [], {"pageCount": 1, "wordCount": 520, "hasPhoto": False, "fileFormat": "pdf"})),
        ("Solid Sr", ResumeData("good3.pdf", {"name": "Michael", "email": "m@e.com", "phone": "555", "location": "Seattle", "linkedin": "li.com/michael"}, [{"title": "Senior SE", "description": "- Led team of 5 delivering 3 features\n- Architected system handling 1M+ requests/day\n- Increased uptime from 98% to 99.9%\n- Reduced costs by 25%"}], [{"degree": "MS CS", "institution": "Stanford"}], ["Python", "Java", "AWS", "Docker", "K8s"], [], {"pageCount": 2, "wordCount": 650, "hasPhoto": False, "fileFormat": "pdf"})),
        ("Well-Rounded", ResumeData("good4.pdf", {"name": "Nina", "email": "n@e.com", "phone": "555", "location": "Austin", "linkedin": "li.com/nina"}, [{"title": "SE II", "description": "- Developed 8 REST APIs\n- Implemented auth for 50K+ users\n- Achieved 90% coverage\n- Reduced bugs by 45%"}], [{"degree": "BS SE", "institution": "GT"}], ["Node", "Express", "React", "Postgres"], [{"name": "AWS Dev"}], {"pageCount": 1, "wordCount": 580, "hasPhoto": False, "fileFormat": "pdf"})),

        # 2 VERY GOOD (76-85)
        ("Excellent Sr", ResumeData("vg1.pdf", {"name": "Oliver", "email": "o@e.com", "phone": "555", "location": "SF", "linkedin": "li.com/oliver", "website": "gh.com/oliver"}, [{"title": "Senior SE", "description": "- Architected distributed system processing 10M+ txns/day\n- Led team of 8 across 3 initiatives\n- Reduced latency by 65%\n- Implemented ML pipeline improving accuracy by 30%\n- Mentored 5 engineers leading to 2 promos\n- Achieved 99.99% SLA"}], [{"degree": "MS CS", "institution": "CMU"}], ["Python", "Java", "Go", "AWS", "K8s", "ML"], [{"name": "AWS SA"}, {"name": "K8s Admin"}], {"pageCount": 2, "wordCount": 720, "hasPhoto": False, "fileFormat": "pdf"})),
        ("Staff Track", ResumeData("vg2.pdf", {"name": "Patricia", "email": "p@e.com", "phone": "555", "location": "NYC", "linkedin": "li.com/patricia", "website": "patricia.dev"}, [{"title": "Staff SE", "description": "- Designed microservices for 5M+ daily users\n- Led cross-functional team of 12\n- Increased deploy freq by 300%\n- Reduced costs by 40% while improving perf\n- Established best practices company-wide\n- Delivered 4 features generating $2M+ revenue"}], [{"degree": "MS SE", "institution": "Berkeley"}], ["Python", "TS", "AWS", "Docker", "K8s", "React"], [{"name": "AWS SA Pro"}], {"pageCount": 2, "wordCount": 780, "hasPhoto": False, "fileFormat": "pdf"})),

        # 0 EXCEPTIONAL (86-100) - Should be extremely rare
    ]


def calculate_distribution(scores):
    """Calculate distribution percentages."""
    if not scores:
        return {}

    buckets = {"0-40": 0, "41-60": 0, "61-75": 0, "76-85": 0, "86-100": 0}
    for score in scores:
        if score <= 40:
            buckets["0-40"] += 1
        elif score <= 60:
            buckets["41-60"] += 1
        elif score <= 75:
            buckets["61-75"] += 1
        elif score <= 85:
            buckets["76-85"] += 1
        else:
            buckets["86-100"] += 1

    total = len(scores)
    return {k: (v / total * 100) for k, v in buckets.items()}


def main():
    """Run distribution validation."""
    print("="*80)
    print("SCORE DISTRIBUTION VALIDATION")
    print("="*80)
    print("\nScoring 20 diverse test resumes...")

    test_resumes = create_test_resumes()

    # Test Legacy Scorer
    print("\n" + "="*80)
    print("1. LEGACY SCORER (scorer.py)")
    print("="*80)

    legacy_scores = []
    for i, (name, resume_data) in enumerate(test_resumes, 1):
        result = calculate_overall_score(resume_data, "", "software_engineer", "mid")
        score = result["overallScore"]
        legacy_scores.append(score)
        print(f"{i:2d}. {name:<20} {score:5.1f}/100")

    legacy_dist = calculate_distribution(legacy_scores)
    print(f"\nDistribution:")
    print(f"  0-40:   {legacy_dist['0-40']:5.1f}% (target: 30% ± 10%)")
    print(f"  41-60:  {legacy_dist['41-60']:5.1f}% (target: 40% ± 10%)")
    print(f"  61-75:  {legacy_dist['61-75']:5.1f}% (target: 20% ± 10%)")
    print(f"  76-85:  {legacy_dist['76-85']:5.1f}% (target: 8% ± 5%)")
    print(f"  86-100: {legacy_dist['86-100']:5.1f}% (target: 2% ± 3%)")
    print(f"Average: {sum(legacy_scores)/len(legacy_scores):.1f}")

    # Test Adaptive Scorer - Quality Coach
    print("\n" + "="*80)
    print("2. ADAPTIVE SCORER - Quality Coach Mode")
    print("="*80)

    scorer = AdaptiveScorer()
    adaptive_scores = []
    for i, (name, resume_data) in enumerate(test_resumes, 1):
        result = scorer.score(resume_data, "software_engineer", ExperienceLevel.MID, None, "auto")
        score = result["overallScore"]
        adaptive_scores.append(score)
        print(f"{i:2d}. {name:<20} {score:5.1f}/100")

    adaptive_dist = calculate_distribution(adaptive_scores)
    print(f"\nDistribution:")
    print(f"  0-40:   {adaptive_dist['0-40']:5.1f}% (target: 30% ± 10%)")
    print(f"  41-60:  {adaptive_dist['41-60']:5.1f}% (target: 40% ± 10%)")
    print(f"  61-75:  {adaptive_dist['61-75']:5.1f}% (target: 20% ± 10%)")
    print(f"  76-85:  {adaptive_dist['76-85']:5.1f}% (target: 8% ± 5%)")
    print(f"  86-100: {adaptive_dist['86-100']:5.1f}% (target: 2% ± 3%)")
    print(f"Average: {sum(adaptive_scores)/len(adaptive_scores):.1f}")

    # Validation
    print("\n" + "="*80)
    print("VALIDATION RESULTS")
    print("="*80)

    def check_range(value, target, tolerance, label):
        min_val = target - tolerance
        max_val = target + tolerance
        status = "PASS" if min_val <= value <= max_val else "FAIL"
        print(f"{label:<15} {value:5.1f}% (range: {min_val:4.0f}-{max_val:4.0f}%) [{status}]")
        return status == "PASS"

    all_pass = True
    print("\nLegacy Scorer:")
    all_pass &= check_range(legacy_dist["0-40"], 30, 10, "0-40:")
    all_pass &= check_range(legacy_dist["41-60"], 40, 10, "41-60:")
    all_pass &= check_range(legacy_dist["61-75"], 20, 10, "61-75:")
    all_pass &= check_range(legacy_dist["76-85"], 8, 5, "76-85:")
    all_pass &= check_range(legacy_dist["86-100"], 2, 3, "86-100:")

    print("\nAdaptive Scorer:")
    all_pass &= check_range(adaptive_dist["0-40"], 30, 10, "0-40:")
    all_pass &= check_range(adaptive_dist["41-60"], 40, 10, "41-60:")
    all_pass &= check_range(adaptive_dist["61-75"], 20, 10, "61-75:")
    all_pass &= check_range(adaptive_dist["76-85"], 8, 5, "76-85:")
    all_pass &= check_range(adaptive_dist["86-100"], 2, 3, "86-100:")

    print("\n" + "="*80)
    if all_pass:
        print("DISTRIBUTION VALIDATION: PASSED")
        print("Scoring system produces harsh but realistic distributions.")
    else:
        print("DISTRIBUTION VALIDATION: FAILED")
        print("Scoring system needs calibration adjustment.")
    print("="*80)

    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
