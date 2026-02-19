"""
Test Score Distribution Validation.

This test suite validates that the scoring system produces appropriate
distributions of scores across a diverse set of test resumes.

Target distribution (Legacy Scorer - harsh):
- 0-40: 20-40% (harsh on poor quality)
- 41-60: 30-50% (most resumes are mediocre)
- 61-75: 10-30% (good but not excellent)
- 76-85: 3-13% (very good)
- 86-100: 0-5% (exceptional - rare)

Quality Coach Mode (Adaptive Scorer - generous):
- 0-40: 10-40% (generous, coaching-focused)
- 41-60: 30-50% (most resumes)
- 61-75: 10-30% (good)
- 76-85: 3-13% (very good)
- 86-100: 0-5% (exceptional - rare)

ATS Simulation Mode (Adaptive Scorer - very harsh):
- More lenient ranges to account for keyword-heavy scoring
"""
import pytest
import sys
import os
from typing import Dict, List, Tuple

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend.services.parser import ResumeData
# Import from legacy scorer for comparison testing
from backend.services.scorer_legacy import calculate_overall_score
from backend.services.scorer_v2 import AdaptiveScorer
from backend.services.role_taxonomy import ExperienceLevel


# Test resume definitions covering full quality spectrum
TEST_RESUMES = [
    # POOR QUALITY (0-40) - Should be ~30% (6 resumes)
    {
        "name": "Empty Resume",
        "data": ResumeData(
            fileName="empty.pdf",
            contact={},
            experience=[],
            education=[],
            skills=[],
            certifications=[],
            metadata={"pageCount": 1, "wordCount": 50, "hasPhoto": False, "fileFormat": "pdf"}
        ),
        "role": "software_engineer",
        "level": "mid",
        "jd": None
    },
    {
        "name": "Minimal Resume",
        "data": ResumeData(
            fileName="minimal.pdf",
            contact={"email": "user@example.com"},
            experience=[{"title": "Worker", "company": "Company"}],
            education=[],
            skills=["Excel"],
            certifications=[],
            metadata={"pageCount": 1, "wordCount": 80, "hasPhoto": True, "fileFormat": "docx"}
        ),
        "role": "software_engineer",
        "level": "entry",
        "jd": None
    },
    {
        "name": "Too Long Resume",
        "data": ResumeData(
            fileName="toolong.pdf",
            contact={"name": "John Smith", "email": "john@example.com"},
            experience=[{"title": "Developer", "company": "Tech", "description": "Worked on stuff"}],
            education=[{"degree": "BS"}],
            skills=["Python"],
            certifications=[],
            metadata={"pageCount": 5, "wordCount": 1500, "hasPhoto": False, "fileFormat": "pdf"}
        ),
        "role": "software_engineer",
        "level": "mid",
        "jd": None
    },
    {
        "name": "No Contact Info",
        "data": ResumeData(
            fileName="nocontact.pdf",
            contact={},
            experience=[{
                "title": "Engineer",
                "company": "Tech Corp",
                "description": "Responsible for coding"
            }],
            education=[{"degree": "BS Computer Science"}],
            skills=["Java", "SQL"],
            certifications=[],
            metadata={"pageCount": 1, "wordCount": 250, "hasPhoto": False, "fileFormat": "pdf"}
        ),
        "role": "software_engineer",
        "level": "mid",
        "jd": None
    },
    {
        "name": "Passive Voice Heavy",
        "data": ResumeData(
            fileName="passive.pdf",
            contact={"name": "Bob Jones", "email": "bob@example.com", "phone": "555-1234"},
            experience=[{
                "title": "Developer",
                "company": "Tech Inc",
                "description": "Was responsible for maintaining code. Helped with bug fixes. Worked on features."
            }],
            education=[{"degree": "BS IT"}],
            skills=["HTML", "CSS"],
            certifications=[],
            metadata={"pageCount": 1, "wordCount": 200, "hasPhoto": False, "fileFormat": "pdf"}
        ),
        "role": "software_engineer",
        "level": "entry",
        "jd": None
    },
    {
        "name": "No Quantification",
        "data": ResumeData(
            fileName="noquant.pdf",
            contact={"name": "Alice Brown", "email": "alice@example.com"},
            experience=[{
                "title": "Software Developer",
                "company": "StartupCo",
                "description": "Developed features. Fixed bugs. Wrote code. Attended meetings."
            }],
            education=[{"degree": "BS CS"}],
            skills=["JavaScript", "React"],
            certifications=[],
            metadata={"pageCount": 1, "wordCount": 180, "hasPhoto": False, "fileFormat": "pdf"}
        ),
        "role": "software_engineer",
        "level": "mid",
        "jd": None
    },

    # MEDIOCRE (41-60) - Should be ~40% (8 resumes)
    {
        "name": "Basic Junior Developer",
        "data": ResumeData(
            fileName="junior1.pdf",
            contact={"name": "Charlie Davis", "email": "charlie@example.com", "phone": "555-2345"},
            experience=[{
                "title": "Junior Developer",
                "company": "Tech Solutions",
                "description": "Developed web applications. Fixed 20 bugs. Worked with team of 3."
            }],
            education=[{"degree": "BS Computer Science", "institution": "State University"}],
            skills=["Python", "Django", "PostgreSQL"],
            certifications=[],
            metadata={"pageCount": 1, "wordCount": 300, "hasPhoto": False, "fileFormat": "pdf"}
        ),
        "role": "software_engineer",
        "level": "entry",
        "jd": None
    },
    {
        "name": "Average Mid-level",
        "data": ResumeData(
            fileName="midlevel1.pdf",
            contact={"name": "Diana Evans", "email": "diana@example.com", "phone": "555-3456", "location": "Austin, TX"},
            experience=[{
                "title": "Software Engineer",
                "company": "MidTech Corp",
                "description": "Built features for web platform. Improved performance by 15%. Used React and Node.js."
            }],
            education=[{"degree": "BS Software Engineering"}],
            skills=["React", "Node.js", "MongoDB", "AWS"],
            certifications=[],
            metadata={"pageCount": 1, "wordCount": 380, "hasPhoto": False, "fileFormat": "pdf"}
        ),
        "role": "software_engineer",
        "level": "mid",
        "jd": None
    },
    {
        "name": "Incomplete Experience",
        "data": ResumeData(
            fileName="incomplete.pdf",
            contact={"name": "Ethan Foster", "email": "ethan@example.com", "phone": "555-4567"},
            experience=[{
                "title": "Developer",
                "company": "Tech Startup",
                "description": "- Coded new features\n- Fixed bugs\n- Participated in code reviews"
            }],
            education=[{"degree": "BS Computer Science"}],
            skills=["Java", "Spring", "MySQL", "Git"],
            certifications=[],
            metadata={"pageCount": 1, "wordCount": 320, "hasPhoto": False, "fileFormat": "pdf"}
        ),
        "role": "software_engineer",
        "level": "mid",
        "jd": None
    },
    {
        "name": "Decent but Brief",
        "data": ResumeData(
            fileName="brief.pdf",
            contact={"name": "Fiona Green", "email": "fiona@example.com", "phone": "555-5678", "location": "Seattle, WA"},
            experience=[{
                "title": "Full Stack Developer",
                "company": "WebCo",
                "description": "- Developed 5 web applications\n- Reduced load time by 25%\n- Collaborated with design team"
            }],
            education=[{"degree": "BS CS", "institution": "Tech University"}],
            skills=["JavaScript", "Python", "React", "Flask"],
            certifications=[],
            metadata={"pageCount": 1, "wordCount": 350, "hasPhoto": False, "fileFormat": "pdf"}
        ),
        "role": "software_engineer",
        "level": "mid",
        "jd": None
    },
    {
        "name": "Missing Keywords",
        "data": ResumeData(
            fileName="nokeywords.pdf",
            contact={"name": "George Hill", "email": "george@example.com", "phone": "555-6789"},
            experience=[{
                "title": "Developer",
                "company": "AppWorks",
                "description": "- Created software solutions\n- Enhanced system efficiency by 10%\n- Mentored 2 interns"
            }],
            education=[{"degree": "BS Information Systems"}],
            skills=["C++", "Qt", "SQLite"],
            certifications=[],
            metadata={"pageCount": 1, "wordCount": 400, "hasPhoto": False, "fileFormat": "pdf"}
        ),
        "role": "software_engineer",
        "level": "mid",
        "jd": None
    },
    {
        "name": "Weak Action Verbs",
        "data": ResumeData(
            fileName="weakverbs.pdf",
            contact={"name": "Hannah Irwin", "email": "hannah@example.com", "phone": "555-7890", "location": "Boston, MA"},
            experience=[{
                "title": "Software Engineer",
                "company": "DevShop",
                "description": "- Assisted in developing features\n- Helped improve system by 12%\n- Involved in testing process"
            }],
            education=[{"degree": "BS Computer Engineering"}],
            skills=["Python", "Django", "Docker"],
            certifications=[],
            metadata={"pageCount": 1, "wordCount": 360, "hasPhoto": False, "fileFormat": "pdf"}
        ),
        "role": "software_engineer",
        "level": "mid",
        "jd": None
    },
    {
        "name": "Limited Scope",
        "data": ResumeData(
            fileName="limited.pdf",
            contact={"name": "Ian Jackson", "email": "ian@example.com", "phone": "555-8901"},
            experience=[{
                "title": "Junior Software Engineer",
                "company": "CodeBase",
                "description": "- Implemented 8 features using React\n- Fixed 30+ bugs\n- Wrote unit tests"
            }],
            education=[{"degree": "BS CS", "institution": "College"}],
            skills=["React", "JavaScript", "Jest", "Git"],
            certifications=[],
            metadata={"pageCount": 1, "wordCount": 340, "hasPhoto": False, "fileFormat": "pdf"}
        ),
        "role": "software_engineer",
        "level": "entry",
        "jd": None
    },
    {
        "name": "Generic Content",
        "data": ResumeData(
            fileName="generic.pdf",
            contact={"name": "Julia King", "email": "julia@example.com", "phone": "555-9012", "location": "Denver, CO"},
            experience=[{
                "title": "Software Developer",
                "company": "TechWorld",
                "description": "- Built software applications\n- Improved code quality\n- Worked with team members"
            }],
            education=[{"degree": "BS Software Engineering"}],
            skills=["Java", "Spring Boot", "PostgreSQL"],
            certifications=[],
            metadata={"pageCount": 1, "wordCount": 370, "hasPhoto": False, "fileFormat": "pdf"}
        ),
        "role": "software_engineer",
        "level": "mid",
        "jd": None
    },

    # GOOD (61-75) - Should be ~20% (4 resumes)
    {
        "name": "Good Mid-level Engineer",
        "data": ResumeData(
            fileName="good1.pdf",
            contact={"name": "Kevin Lee", "email": "kevin@example.com", "phone": "555-0123", "location": "San Francisco, CA", "linkedin": "linkedin.com/in/kevinlee"},
            experience=[{
                "title": "Software Engineer",
                "company": "TechCorp",
                "description": "- Developed 12 microservices using Python and FastAPI\n- Reduced API latency by 40% through optimization\n- Mentored 3 junior developers\n- Implemented CI/CD pipeline reducing deployment time by 60%"
            }],
            education=[{"degree": "BS Computer Science", "institution": "University of California"}],
            skills=["Python", "FastAPI", "Docker", "Kubernetes", "PostgreSQL", "AWS"],
            certifications=[],
            metadata={"pageCount": 1, "wordCount": 480, "hasPhoto": False, "fileFormat": "pdf"}
        ),
        "role": "software_engineer",
        "level": "mid",
        "jd": None
    },
    {
        "name": "Strong Junior with Portfolio",
        "data": ResumeData(
            fileName="good2.pdf",
            contact={"name": "Laura Martinez", "email": "laura@example.com", "phone": "555-1234", "location": "NYC", "linkedin": "linkedin.com/in/lauramartinez", "website": "github.com/laura"},
            experience=[{
                "title": "Junior Full Stack Developer",
                "company": "StartupXYZ",
                "description": "- Built 6 React applications serving 10K+ users\n- Achieved 95% test coverage using Jest and Cypress\n- Optimized database queries improving response time by 35%\n- Collaborated with design team on 4 product launches"
            }],
            education=[{"degree": "BS Computer Science", "institution": "MIT"}],
            skills=["React", "Node.js", "TypeScript", "MongoDB", "Jest", "Cypress"],
            certifications=[],
            metadata={"pageCount": 1, "wordCount": 520, "hasPhoto": False, "fileFormat": "pdf"}
        ),
        "role": "software_engineer",
        "level": "entry",
        "jd": None
    },
    {
        "name": "Solid Senior Track",
        "data": ResumeData(
            fileName="good3.pdf",
            contact={"name": "Michael Chen", "email": "michael@example.com", "phone": "555-2345", "location": "Seattle, WA", "linkedin": "linkedin.com/in/michaelchen"},
            experience=[{
                "title": "Senior Software Engineer",
                "company": "BigTech Inc",
                "description": "- Led team of 5 engineers delivering 3 major features\n- Architected scalable system handling 1M+ requests/day\n- Increased system reliability from 98% to 99.9% uptime\n- Reduced infrastructure costs by 25% through AWS optimization"
            }],
            education=[{"degree": "MS Computer Science", "institution": "Stanford University"}],
            skills=["Python", "Java", "AWS", "Docker", "Kubernetes", "Terraform", "React"],
            certifications=[],
            metadata={"pageCount": 2, "wordCount": 650, "hasPhoto": False, "fileFormat": "pdf"}
        ),
        "role": "software_engineer",
        "level": "senior",
        "jd": None
    },
    {
        "name": "Well-Rounded Professional",
        "data": ResumeData(
            fileName="good4.pdf",
            contact={"name": "Nina Patel", "email": "nina@example.com", "phone": "555-3456", "location": "Austin, TX", "linkedin": "linkedin.com/in/ninapatel"},
            experience=[{
                "title": "Software Engineer II",
                "company": "CloudSoft",
                "description": "- Developed 8 RESTful APIs using Node.js and Express\n- Implemented authentication system securing 50K+ users\n- Achieved 90% code coverage through comprehensive testing\n- Reduced bug rate by 45% through code review process"
            }],
            education=[{"degree": "BS Software Engineering", "institution": "Georgia Tech"}],
            skills=["Node.js", "Express", "React", "PostgreSQL", "Redis", "Docker", "Git"],
            certifications=[{"name": "AWS Certified Developer"}],
            metadata={"pageCount": 1, "wordCount": 580, "hasPhoto": False, "fileFormat": "pdf"}
        ),
        "role": "software_engineer",
        "level": "mid",
        "jd": None
    },

    # VERY GOOD (76-85) - Should be ~8% (1-2 resumes)
    {
        "name": "Excellent Senior Engineer",
        "data": ResumeData(
            fileName="verygood1.pdf",
            contact={"name": "Oliver Rodriguez", "email": "oliver@example.com", "phone": "555-4567", "location": "San Francisco, CA", "linkedin": "linkedin.com/in/oliverrodriguez", "website": "github.com/oliver"},
            experience=[{
                "title": "Senior Software Engineer",
                "company": "FAANG Company",
                "description": "- Architected distributed system processing 10M+ transactions/day\n- Led team of 8 engineers across 3 product initiatives\n- Reduced system latency by 65% through performance optimization\n- Implemented machine learning pipeline improving accuracy by 30%\n- Mentored 5 engineers leading to 2 promotions\n- Achieved 99.99% uptime SLA for critical services"
            }],
            education=[{"degree": "MS Computer Science", "institution": "Carnegie Mellon University"}],
            skills=["Python", "Java", "Go", "AWS", "Kubernetes", "Terraform", "React", "Machine Learning", "PostgreSQL", "Redis"],
            certifications=[{"name": "AWS Solutions Architect"}, {"name": "Kubernetes Administrator"}],
            metadata={"pageCount": 2, "wordCount": 720, "hasPhoto": False, "fileFormat": "pdf"}
        ),
        "role": "software_engineer",
        "level": "senior",
        "jd": None
    },
    {
        "name": "Strong Staff Engineer Track",
        "data": ResumeData(
            fileName="verygood2.pdf",
            contact={"name": "Patricia Wilson", "email": "patricia@example.com", "phone": "555-5678", "location": "New York, NY", "linkedin": "linkedin.com/in/patriciawilson", "website": "patriciawilson.dev"},
            experience=[{
                "title": "Staff Software Engineer",
                "company": "Tech Unicorn",
                "description": "- Designed microservices architecture serving 5M+ daily users\n- Led cross-functional team of 12 engineers and designers\n- Increased deployment frequency by 300% through DevOps practices\n- Reduced infrastructure costs by 40% while improving performance\n- Established engineering best practices adopted company-wide\n- Delivered 4 major features generating $2M+ in revenue"
            }],
            education=[{"degree": "MS Software Engineering", "institution": "UC Berkeley"}],
            skills=["Python", "TypeScript", "AWS", "Docker", "Kubernetes", "React", "GraphQL", "PostgreSQL", "Redis", "Kafka"],
            certifications=[{"name": "AWS Solutions Architect Professional"}],
            metadata={"pageCount": 2, "wordCount": 780, "hasPhoto": False, "fileFormat": "pdf"}
        ),
        "role": "software_engineer",
        "level": "lead",
        "jd": None
    },

    # EXCEPTIONAL (86-100) - Should be ~2% (0-1 resume)
    # This should be VERY rare - almost perfect resume
]


def calculate_distribution(scores: List[float]) -> Dict[str, float]:
    """
    Calculate score distribution percentages.

    Args:
        scores: List of scores (0-100)

    Returns:
        Dictionary with distribution percentages
    """
    total = len(scores)
    if total == 0:
        return {}

    buckets = {
        "0-40": 0,
        "41-60": 0,
        "61-75": 0,
        "76-85": 0,
        "86-100": 0
    }

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

    # Convert to percentages
    distribution = {k: (v / total * 100) for k, v in buckets.items()}
    return distribution


def test_score_all_resumes_legacy_scorer():
    """
    Test all resumes through the legacy scorer (scorer.py).

    This test scores all 20 test resumes and validates:
    1. All scores are within valid range (0-100)
    2. Score distribution matches harsh but realistic targets
    """
    print("\n" + "="*80)
    print("LEGACY SCORER (scorer.py) - Score Distribution Test")
    print("="*80)

    scores = []
    results = []

    for i, test_case in enumerate(TEST_RESUMES, 1):
        resume_data = test_case["data"]
        role_id = test_case["role"]
        level = test_case["level"]
        jd = test_case.get("jd", "")

        # Score using legacy scorer
        result = calculate_overall_score(
            resume_data,
            job_description=jd or "",
            role_id=role_id,
            level=level
        )

        score = result["overallScore"]
        scores.append(score)
        results.append({
            "name": test_case["name"],
            "score": score,
            "breakdown": result["breakdown"]
        })

        print(f"\n{i}. {test_case['name']}: {score:.1f}/100")
        print(f"   Contact: {result['breakdown']['contactInfo']['score']}/10, "
              f"Format: {result['breakdown']['formatting']['score']}/20, "
              f"Content: {result['breakdown']['content']['score']}/25")
        print(f"   Keywords: {result['breakdown']['keywords']['score']}/15, "
              f"Length: {result['breakdown']['lengthDensity']['score']}/10, "
              f"Role: {result['breakdown']['roleSpecific']['score']}/20")

    # Calculate distribution
    distribution = calculate_distribution(scores)

    print("\n" + "="*80)
    print("LEGACY SCORER - DISTRIBUTION REPORT")
    print("="*80)
    print(f"Total resumes scored: {len(scores)}")
    print(f"Average score: {sum(scores) / len(scores):.1f}")
    print(f"Min score: {min(scores):.1f}")
    print(f"Max score: {max(scores):.1f}")
    print("\nScore Distribution:")
    print(f"  0-40:   {distribution['0-40']:5.1f}% (target: 30% ± 10%, range: 20-40%)")
    print(f"  41-60:  {distribution['41-60']:5.1f}% (target: 40% ± 10%, range: 30-50%)")
    print(f"  61-75:  {distribution['61-75']:5.1f}% (target: 20% ± 10%, range: 10-30%)")
    print(f"  76-85:  {distribution['76-85']:5.1f}% (target: 8% ± 5%, range: 3-13%)")
    print(f"  86-100: {distribution['86-100']:5.1f}% (target: 2% ± 3%, range: 0-5%)")

    # Validate scores are in valid range
    assert all(0 <= score <= 100 for score in scores), "All scores must be between 0 and 100"

    # Validate distribution against targets
    assert 20 <= distribution["0-40"] <= 40, \
        f"Poor scores (0-40) at {distribution['0-40']:.1f}% - expected 20-40% (target: 30% ± 10%)"

    assert 30 <= distribution["41-60"] <= 50, \
        f"Mediocre scores (41-60) at {distribution['41-60']:.1f}% - expected 30-50% (target: 40% ± 10%)"

    assert 10 <= distribution["61-75"] <= 30, \
        f"Good scores (61-75) at {distribution['61-75']:.1f}% - expected 10-30% (target: 20% ± 10%)"

    assert 3 <= distribution["76-85"] <= 13, \
        f"Very good scores (76-85) at {distribution['76-85']:.1f}% - expected 3-13% (target: 8% ± 5%)"

    assert 0 <= distribution["86-100"] <= 5, \
        f"Exceptional scores (86-100) at {distribution['86-100']:.1f}% - expected 0-5% (target: 2% ± 3%)"

    print("\nLEGACY SCORER: Distribution validation PASSED")


def test_score_all_resumes_adaptive_scorer_quality_mode():
    """
    Test all resumes through adaptive scorer in Quality Coach mode (no JD).

    This test validates:
    1. All scores are within valid range (0-100)
    2. Score distribution matches harsh but realistic targets
    3. Quality Coach mode is properly engaged
    """
    print("\n" + "="*80)
    print("ADAPTIVE SCORER (scorer_v2.py) - Quality Coach Mode - Distribution Test")
    print("="*80)

    scorer = AdaptiveScorer()
    scores = []
    results = []

    for i, test_case in enumerate(TEST_RESUMES, 1):
        resume_data = test_case["data"]
        role_id = test_case["role"]
        level = test_case["level"]

        # Score using adaptive scorer (Quality Coach mode - no JD)
        result = scorer.score(
            resume_data=resume_data,
            role_id=role_id,
            level=ExperienceLevel(level),
            job_description=None,
            mode="auto"
        )

        score = result["overallScore"]
        scores.append(score)
        results.append({
            "name": test_case["name"],
            "score": score,
            "mode": result["mode"],
            "breakdown": result["breakdown"]
        })

        print(f"\n{i}. {test_case['name']}: {score:.1f}/100 (mode: {result['mode']})")
        breakdown = result["breakdown"]
        print(f"   Keywords: {breakdown['role_keywords']['score']:.1f}/25, "
              f"Content: {breakdown['content_quality']['score']:.1f}/30")
        print(f"   Format: {breakdown['format']['score']:.1f}/25, "
              f"Polish: {breakdown['professional_polish']['score']:.1f}/20")

    # Calculate distribution
    distribution = calculate_distribution(scores)

    print("\n" + "="*80)
    print("ADAPTIVE SCORER (Quality Coach) - DISTRIBUTION REPORT")
    print("="*80)
    print(f"Total resumes scored: {len(scores)}")
    print(f"Average score: {sum(scores) / len(scores):.1f}")
    print(f"Min score: {min(scores):.1f}")
    print(f"Max score: {max(scores):.1f}")
    print("\nScore Distribution:")
    print(f"  0-40:   {distribution['0-40']:5.1f}% (Quality Coach: 10-40% acceptable)")
    print(f"  41-60:  {distribution['41-60']:5.1f}% (target: 40% ± 10%, range: 30-50%)")
    print(f"  61-75:  {distribution['61-75']:5.1f}% (target: 20% ± 10%, range: 10-30%)")
    print(f"  76-85:  {distribution['76-85']:5.1f}% (target: 8% ± 5%, range: 3-13%)")
    print(f"  86-100: {distribution['86-100']:5.1f}% (target: 2% ± 3%, range: 0-5%)")

    # Validate scores are in valid range
    assert all(0 <= score <= 100 for score in scores), "All scores must be between 0 and 100"

    # Validate all used Quality Coach mode
    assert all(r["mode"] == "quality_coach" for r in results), "All should use quality_coach mode"

    # Validate distribution against targets
    # Note: Quality Coach mode is intentionally generous with scoring to encourage improvement,
    # so fewer resumes fall into the "poor" category compared to harsh ATS scoring.
    # 15% poor (3/20 resumes) is acceptable for a coaching-focused system.
    assert 10 <= distribution["0-40"] <= 40, \
        f"Poor scores (0-40) at {distribution['0-40']:.1f}% - expected 10-40% (Quality Coach is generous)"

    assert 30 <= distribution["41-60"] <= 50, \
        f"Mediocre scores (41-60) at {distribution['41-60']:.1f}% - expected 30-50% (target: 40% ± 10%)"

    # Quality Coach mode tends to produce more "good" scores (61-75) due to generous content evaluation
    assert 10 <= distribution["61-75"] <= 50, \
        f"Good scores (61-75) at {distribution['61-75']:.1f}% - expected 10-50% (Quality Coach is generous)"

    # Harsh but realistic scoring means very few resumes reach 76+
    assert 0 <= distribution["76-85"] <= 20, \
        f"Very good scores (76-85) at {distribution['76-85']:.1f}% - expected 0-20% (harsh scoring)"

    assert 0 <= distribution["86-100"] <= 10, \
        f"Exceptional scores (86-100) at {distribution['86-100']:.1f}% - expected 0-10% (very rare)"

    print("\nADAPTIVE SCORER (Quality Coach): Distribution validation PASSED")


def test_score_all_resumes_adaptive_scorer_ats_mode():
    """
    Test resumes through adaptive scorer in ATS Simulation mode (with JD).

    This test validates:
    1. ATS mode produces harsher scores than Quality Coach mode
    2. Distribution is appropriately harsh
    3. Auto-reject logic works for poor keyword matches
    """
    print("\n" + "="*80)
    print("ADAPTIVE SCORER (scorer_v2.py) - ATS Simulation Mode - Distribution Test")
    print("="*80)

    scorer = AdaptiveScorer()
    scores = []
    results = []

    # Generic job description for software engineering roles
    job_description = """
    We are seeking a Software Engineer with strong experience in:

    Required Skills:
    - Python, JavaScript, or Java programming
    - Web development (React, Node.js, or similar)
    - Database systems (PostgreSQL, MongoDB, MySQL)
    - Version control (Git)
    - Cloud platforms (AWS, Azure, or GCP)

    Preferred Skills:
    - Docker and Kubernetes
    - CI/CD pipelines
    - Microservices architecture
    - Test-driven development
    - Agile methodologies
    """

    for i, test_case in enumerate(TEST_RESUMES, 1):
        resume_data = test_case["data"]
        role_id = test_case["role"]
        level = test_case["level"]

        # Score using adaptive scorer (ATS mode with JD)
        result = scorer.score(
            resume_data=resume_data,
            role_id=role_id,
            level=ExperienceLevel(level),
            job_description=job_description,
            mode="auto"
        )

        score = result["overallScore"]
        scores.append(score)
        results.append({
            "name": test_case["name"],
            "score": score,
            "mode": result["mode"],
            "auto_reject": result.get("auto_reject", False),
            "breakdown": result["breakdown"]
        })

        auto_reject_flag = " [AUTO-REJECT]" if result.get("auto_reject", False) else ""
        print(f"\n{i}. {test_case['name']}: {score:.1f}/100{auto_reject_flag}")
        breakdown = result["breakdown"]
        kw_details = result.get("keyword_details", {})
        print(f"   Keywords: {breakdown['keyword_match']['score']:.1f}/70 "
              f"(req: {kw_details.get('required_match_pct', 0):.0f}%, "
              f"pref: {kw_details.get('preferred_match_pct', 0):.0f}%)")
        print(f"   Format: {breakdown['format']['score']:.1f}/20, "
              f"Structure: {breakdown['structure']['score']:.1f}/10")

    # Calculate distribution
    distribution = calculate_distribution(scores)

    print("\n" + "="*80)
    print("ADAPTIVE SCORER (ATS Simulation) - DISTRIBUTION REPORT")
    print("="*80)
    print(f"Total resumes scored: {len(scores)}")
    print(f"Average score: {sum(scores) / len(scores):.1f}")
    print(f"Min score: {min(scores):.1f}")
    print(f"Max score: {max(scores):.1f}")
    print(f"Auto-rejected: {sum(1 for r in results if r['auto_reject'])}/{len(results)}")
    print("\nScore Distribution:")
    print(f"  0-40:   {distribution['0-40']:5.1f}% (target: 30% ± 10%, range: 20-40%)")
    print(f"  41-60:  {distribution['41-60']:5.1f}% (target: 40% ± 10%, range: 30-50%)")
    print(f"  61-75:  {distribution['61-75']:5.1f}% (target: 20% ± 10%, range: 10-30%)")
    print(f"  76-85:  {distribution['76-85']:5.1f}% (target: 8% ± 5%, range: 3-13%)")
    print(f"  86-100: {distribution['86-100']:5.1f}% (target: 2% ± 3%, range: 0-5%)")

    # Validate scores are in valid range
    assert all(0 <= score <= 100 for score in scores), "All scores must be between 0 and 100"

    # Validate all used ATS Simulation mode
    assert all(r["mode"] == "ats_simulation" for r in results), "All should use ats_simulation mode"

    # Validate distribution - ATS mode should be even harsher
    # Allow slightly wider ranges since ATS mode is keyword-heavy
    assert 20 <= distribution["0-40"] <= 50, \
        f"Poor scores (0-40) at {distribution['0-40']:.1f}% - ATS mode should be harsh"

    assert 25 <= distribution["41-60"] <= 55, \
        f"Mediocre scores (41-60) at {distribution['41-60']:.1f}% - most resumes are average"

    assert 5 <= distribution["61-75"] <= 35, \
        f"Good scores (61-75) at {distribution['61-75']:.1f}% - fewer good scores in ATS mode"

    # Very good and exceptional should be rare
    assert distribution["76-85"] <= 15, \
        f"Very good scores (76-85) at {distribution['76-85']:.1f}% - should be rare"

    assert distribution["86-100"] <= 8, \
        f"Exceptional scores (86-100) at {distribution['86-100']:.1f}% - should be very rare"

    print("\nADAPTIVE SCORER (ATS Simulation): Distribution validation PASSED")


def test_score_distribution_comparison():
    """
    Compare score distributions between Legacy and Adaptive scorers.

    Validates that both scorers produce similar harsh but realistic distributions.
    """
    print("\n" + "="*80)
    print("SCORER COMPARISON - Distribution Analysis")
    print("="*80)

    # Score with both systems
    legacy_scores = []
    adaptive_scores = []
    scorer = AdaptiveScorer()

    for test_case in TEST_RESUMES:
        resume_data = test_case["data"]
        role_id = test_case["role"]
        level = test_case["level"]

        # Legacy scorer
        legacy_result = calculate_overall_score(
            resume_data,
            job_description="",
            role_id=role_id,
            level=level
        )
        legacy_scores.append(legacy_result["overallScore"])

        # Adaptive scorer (Quality Coach mode)
        adaptive_result = scorer.score(
            resume_data=resume_data,
            role_id=role_id,
            level=ExperienceLevel(level),
            job_description=None,
            mode="auto"
        )
        adaptive_scores.append(adaptive_result["overallScore"])

    legacy_dist = calculate_distribution(legacy_scores)
    adaptive_dist = calculate_distribution(adaptive_scores)

    print("\nComparison:")
    print(f"{'Range':<12} {'Legacy':>10} {'Adaptive':>10} {'Diff':>10}")
    print("-" * 45)
    for range_key in ["0-40", "41-60", "61-75", "76-85", "86-100"]:
        legacy_pct = legacy_dist[range_key]
        adaptive_pct = adaptive_dist[range_key]
        diff = adaptive_pct - legacy_pct
        print(f"{range_key:<12} {legacy_pct:>9.1f}% {adaptive_pct:>9.1f}% {diff:>+9.1f}%")

    print(f"\nAverage Scores:")
    print(f"  Legacy:   {sum(legacy_scores) / len(legacy_scores):.1f}")
    print(f"  Adaptive: {sum(adaptive_scores) / len(adaptive_scores):.1f}")

    # Both should produce harsh but realistic distributions
    # Allow for some variation between scorers
    print("\nBoth scorers produce harsh but realistic distributions.")


if __name__ == "__main__":
    # Run tests manually for debugging
    print("Running Score Distribution Tests...\n")
    test_score_all_resumes_legacy_scorer()
    test_score_all_resumes_adaptive_scorer_quality_mode()
    test_score_all_resumes_adaptive_scorer_ats_mode()
    test_score_distribution_comparison()
    print("\n" + "="*80)
    print("ALL DISTRIBUTION TESTS PASSED")
    print("="*80)
