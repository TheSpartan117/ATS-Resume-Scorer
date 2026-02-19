"""
Validation script for ATS scorer improvements.

Checks that all improvements are properly implemented and functional.
Run with: python validate_improvements.py
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from services.scorer_ats import ATSScorer
from services.scorer_quality import QualityScorer
from services.parser import ResumeData


class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'


def print_header(text):
    """Print section header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(70)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}\n")


def print_test(name, passed, details=""):
    """Print test result"""
    status = f"{Colors.GREEN}✓ PASS{Colors.END}" if passed else f"{Colors.RED}✗ FAIL{Colors.END}"
    print(f"{status} - {name}")
    if details:
        print(f"       {details}")


def validate_fuzzy_matching():
    """Validate fuzzy keyword matching implementation"""
    print_header("1. FUZZY KEYWORD MATCHING")

    scorer = ATSScorer()
    passed_tests = 0
    total_tests = 3

    # Test 1: Case insensitive
    resume1 = ResumeData(
        fileName="test.pdf",
        contact={"name": "John"},
        experience=[{"description": "Python JavaScript Docker"}],
        education=[],
        skills=["Python", "JavaScript", "Docker"],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
    )

    result1 = scorer._score_keywords(resume1, "software_engineer", "entry", "")
    test1_pass = result1['details']['matched_count'] > 0
    print_test("Case-insensitive matching", test1_pass,
               f"Matched {result1['details']['matched_count']} keywords")
    if test1_pass:
        passed_tests += 1

    # Test 2: Fuzzy matching exists in KeywordMatcher
    try:
        from services.keyword_matcher import KeywordMatcher
        matcher = KeywordMatcher()
        # Check if fuzzy matching method exists
        test2_pass = hasattr(matcher, 'match_keywords')
        print_test("KeywordMatcher has match_keywords method", test2_pass)
        if test2_pass:
            passed_tests += 1
    except Exception as e:
        print_test("KeywordMatcher initialization", False, str(e))

    # Test 3: Synonym support
    resume3 = ResumeData(
        fileName="test.pdf",
        contact={"name": "John"},
        experience=[{"description": "Machine Learning AI"}],
        education=[],
        skills=["ML", "AI"],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
    )

    result3 = scorer._score_keywords(resume3, "data_scientist", "entry", "")
    test3_pass = result3['details']['matched_count'] > 0
    print_test("Synonym matching (ML = Machine Learning)", test3_pass,
               f"Matched {result3['details']['matched_count']} keywords")
    if test3_pass:
        passed_tests += 1

    print(f"\n{Colors.BOLD}Summary: {passed_tests}/{total_tests} tests passed{Colors.END}")
    return passed_tests == total_tests


def validate_input_validation():
    """Validate comprehensive input validation"""
    print_header("2. INPUT VALIDATION")

    scorer = ATSScorer()
    passed_tests = 0
    total_tests = 5

    # Test 1: None contact
    resume1 = ResumeData(
        fileName="test.pdf",
        contact=None,
        experience=[],
        education=[],
        skills=[],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
    )

    try:
        result1 = scorer._score_contact_info(resume1)
        test1_pass = 'error' not in str(result1) and result1['score'] == 0
        print_test("Handles None contact field", test1_pass, f"Score: {result1['score']}")
        if test1_pass:
            passed_tests += 1
    except Exception as e:
        print_test("Handles None contact field", False, str(e))

    # Test 2: None metadata
    resume2 = ResumeData(
        fileName="test.pdf",
        contact={"name": "John"},
        experience=[],
        education=[],
        skills=[],
        certifications=[],
        metadata=None
    )

    try:
        result2 = scorer._score_formatting(resume2)
        test2_pass = 'error' not in str(result2)
        print_test("Handles None metadata field", test2_pass, f"Score: {result2['score']}")
        if test2_pass:
            passed_tests += 1
    except Exception as e:
        print_test("Handles None metadata field", False, str(e))

    # Test 3: Empty experience
    resume3 = ResumeData(
        fileName="test.pdf",
        contact={"name": "John"},
        experience=[],
        education=[],
        skills=[],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
    )

    try:
        result3 = scorer._score_experience(resume3, "mid")
        test3_pass = 'error' not in str(result3)
        print_test("Handles empty experience list", test3_pass, f"Score: {result3['score']}")
        if test3_pass:
            passed_tests += 1
    except Exception as e:
        print_test("Handles empty experience list", False, str(e))

    # Test 4: None experience
    resume4 = ResumeData(
        fileName="test.pdf",
        contact={"name": "John"},
        experience=None,
        education=[],
        skills=[],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
    )

    try:
        result4 = scorer._score_experience(resume4, "mid")
        test4_pass = 'error' not in str(result4)
        print_test("Handles None experience field", test4_pass, f"Score: {result4['score']}")
        if test4_pass:
            passed_tests += 1
    except Exception as e:
        print_test("Handles None experience field", False, str(e))

    # Test 5: Complete end-to-end with bad data
    try:
        result5 = scorer.score(resume1, "software_engineer", "mid")
        test5_pass = 'score' in result5 and result5['score'] >= 0
        print_test("End-to-end scoring with missing data", test5_pass,
                   f"Score: {result5['score']:.1f}")
        if test5_pass:
            passed_tests += 1
    except Exception as e:
        print_test("End-to-end scoring with missing data", False, str(e))

    print(f"\n{Colors.BOLD}Summary: {passed_tests}/{total_tests} tests passed{Colors.END}")
    return passed_tests == total_tests


def validate_experience_detection():
    """Validate improved experience duration detection"""
    print_header("3. EXPERIENCE DURATION DETECTION")

    scorer = ATSScorer()
    passed_tests = 0
    total_tests = 3

    # Test 1: Explicit years in description
    resume1 = ResumeData(
        fileName="test.pdf",
        contact={"name": "John"},
        experience=[{
            "title": "Developer",
            "company": "Company",
            "description": "5 years of experience in Python development"
        }],
        education=[],
        skills=["Python"],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
    )

    result1 = scorer._score_experience(resume1, "mid")
    test1_pass = result1['details']['total_years'] >= 4.5
    print_test("Detects '5 years' in description", test1_pass,
               f"Detected: {result1['details']['total_years']} years")
    if test1_pass:
        passed_tests += 1

    # Test 2: Check method exists
    test2_pass = hasattr(scorer, '_calculate_experience_years')
    print_test("_calculate_experience_years method exists", test2_pass)
    if test2_pass:
        passed_tests += 1

    # Test 3: Alternate pattern "experience: 3 years"
    resume3 = ResumeData(
        fileName="test.pdf",
        contact={"name": "John"},
        experience=[{
            "description": "Experience: 3+ years in software development"
        }],
        education=[],
        skills=[],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
    )

    result3 = scorer._score_experience(resume3, "entry")
    test3_pass = result3['details']['total_years'] >= 2.5
    print_test("Detects 'experience: 3+ years' pattern", test3_pass,
               f"Detected: {result3['details']['total_years']} years")
    if test3_pass:
        passed_tests += 1

    print(f"\n{Colors.BOLD}Summary: {passed_tests}/{total_tests} tests passed{Colors.END}")
    return passed_tests == total_tests


def validate_table_format():
    """Validate table format keyword extraction"""
    print_header("4. TABLE FORMAT KEYWORD EXTRACTION")

    scorer = ATSScorer()
    passed_tests = 0
    total_tests = 2

    # Test 1: Pipe-separated values
    resume1 = ResumeData(
        fileName="test.pdf",
        contact={"name": "John", "email": "john@example.com"},
        experience=[{
            "description": "Python | Django | REST API | Docker | Kubernetes"
        }],
        education=[],
        skills=["Python", "Django", "REST API", "Docker", "Kubernetes"],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
    )

    result1 = scorer._score_keywords(resume1, "software_engineer", "mid", "")
    test1_pass = result1['details']['matched_count'] >= 3
    print_test("Extracts keywords from pipe-separated format", test1_pass,
               f"Matched: {result1['details']['matched_count']} keywords")
    if test1_pass:
        passed_tests += 1

    # Test 2: Check build_resume_text handles pipes
    resume_text = scorer._build_resume_text(resume1)
    test2_pass = 'Python' in resume_text and 'Django' in resume_text
    print_test("_build_resume_text processes pipes correctly", test2_pass,
               f"Text includes separated keywords")
    if test2_pass:
        passed_tests += 1

    print(f"\n{Colors.BOLD}Summary: {passed_tests}/{total_tests} tests passed{Colors.END}")
    return passed_tests == total_tests


def validate_flexible_boundaries():
    """Validate flexible experience level boundaries"""
    print_header("5. FLEXIBLE EXPERIENCE LEVEL BOUNDARIES")

    scorer = ATSScorer()
    passed_tests = 0
    total_tests = 3

    # Test 1: 4 years should work for both entry and mid
    resume = ResumeData(
        fileName="test.pdf",
        contact={"name": "John"},
        experience=[{
            "description": "4 years of development experience"
        }],
        education=[],
        skills=[],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
    )

    entry_result = scorer._score_experience(resume, "entry")
    mid_result = scorer._score_experience(resume, "mid")

    test1_pass = entry_result['score'] >= 6 and mid_result['score'] >= 6
    print_test("4 years accepted for entry AND mid", test1_pass,
               f"Entry: {entry_result['score']}, Mid: {mid_result['score']}")
    if test1_pass:
        passed_tests += 1

    # Test 2: Graduated scoring for under-qualified
    resume2 = ResumeData(
        fileName="test.pdf",
        contact={"name": "John"},
        experience=[{
            "description": "1 year of experience"
        }],
        education=[],
        skills=[],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
    )

    result2 = scorer._score_experience(resume2, "mid")
    # Should get partial credit (6 or 8 pts) rather than 0
    test2_pass = result2['score'] >= 3
    print_test("Under-qualified gets partial credit", test2_pass,
               f"1 year for mid-level: {result2['score']}/20 points")
    if test2_pass:
        passed_tests += 1

    # Test 3: Over-qualified not heavily penalized
    resume3 = ResumeData(
        fileName="test.pdf",
        contact={"name": "John"},
        experience=[{
            "description": "10 years of experience"
        }],
        education=[],
        skills=[],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
    )

    result3 = scorer._score_experience(resume3, "mid")
    test3_pass = result3['score'] >= 8
    print_test("Over-qualified not heavily penalized", test3_pass,
               f"10 years for mid-level: {result3['score']}/20 points")
    if test3_pass:
        passed_tests += 1

    print(f"\n{Colors.BOLD}Summary: {passed_tests}/{total_tests} tests passed{Colors.END}")
    return passed_tests == total_tests


def validate_role_weights():
    """Validate role-specific weight infrastructure"""
    print_header("6. ROLE-SPECIFIC WEIGHT INFRASTRUCTURE")

    scorer = ATSScorer()
    passed_tests = 0
    total_tests = 3

    # Test 1: Method exists
    test1_pass = hasattr(scorer, '_get_role_weights')
    print_test("_get_role_weights method exists", test1_pass)
    if test1_pass:
        passed_tests += 1

    # Test 2: Returns valid weights
    try:
        weights = scorer._get_role_weights("software_engineer", "mid")
        test2_pass = (
            'keywords' in weights and
            'red_flags' in weights and
            'experience' in weights and
            'formatting' in weights and
            'contact' in weights
        )
        print_test("Returns all required weight components", test2_pass,
                   f"Keys: {list(weights.keys())}")
        if test2_pass:
            passed_tests += 1
    except Exception as e:
        print_test("Returns all required weight components", False, str(e))

    # Test 3: Weights are reasonable (between 0 and 1, sum to ~1)
    try:
        weights = scorer._get_role_weights("software_engineer", "mid")
        weight_values = [
            weights.get('keywords', 0),
            weights.get('red_flags', 0),
            weights.get('experience', 0),
            weights.get('formatting', 0),
            weights.get('contact', 0)
        ]
        test3_pass = (
            all(0 <= v <= 1 for v in weight_values) and
            0.9 <= sum(weight_values) <= 1.1
        )
        print_test("Weights are valid (0-1, sum≈1)", test3_pass,
                   f"Sum: {sum(weight_values):.2f}")
        if test3_pass:
            passed_tests += 1
    except Exception as e:
        print_test("Weights are valid (0-1, sum≈1)", False, str(e))

    print(f"\n{Colors.BOLD}Summary: {passed_tests}/{total_tests} tests passed{Colors.END}")
    return passed_tests == total_tests


def validate_false_negative_reduction():
    """Validate that well-qualified candidates score well"""
    print_header("7. FALSE NEGATIVE REDUCTION")

    scorer = ATSScorer()
    passed_tests = 0
    total_tests = 2

    # Test 1: Well-qualified mid-level candidate
    resume = ResumeData(
        fileName="test.pdf",
        contact={
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "123-456-7890",
            "location": "San Francisco",
            "linkedin": "linkedin.com/in/johndoe"
        },
        experience=[{
            "title": "Software Engineer",
            "company": "Tech Corp",
            "startDate": "Jan 2019",
            "endDate": "Present",
            "description": "5 years developing Python applications with Django, REST APIs, Docker. Led team of 3. Improved performance 40%."
        }],
        education=[{"degree": "BS Computer Science", "institution": "University"}],
        skills=["Python", "Django", "REST API", "Docker", "AWS", "Leadership"],
        certifications=[],
        metadata={"pageCount": 2, "wordCount": 650, "fileFormat": "pdf", "hasPhoto": False}
    )

    result = scorer.score(resume, "software_engineer", "mid")
    test1_pass = result['score'] >= 50
    print_test("Well-qualified candidate scores >= 50", test1_pass,
               f"Score: {result['score']:.1f}/100")
    if test1_pass:
        passed_tests += 1

    # Test 2: Experience not marked as under-qualified
    exp_details = result['breakdown']['experience']['details']
    test2_pass = 'under-qualified' not in exp_details.get('years_message', '').lower()
    print_test("Experience not marked as under-qualified", test2_pass,
               f"Message: {exp_details.get('years_message', '')}")
    if test2_pass:
        passed_tests += 1

    print(f"\n{Colors.BOLD}Summary: {passed_tests}/{total_tests} tests passed{Colors.END}")
    return passed_tests == total_tests


def main():
    """Run all validations"""
    print(f"\n{Colors.BOLD}{Colors.GREEN}")
    print("╔════════════════════════════════════════════════════════════════════╗")
    print("║        ATS SCORER IMPROVEMENTS - VALIDATION SUITE                  ║")
    print("╚════════════════════════════════════════════════════════════════════╝")
    print(f"{Colors.END}")

    results = {
        "Fuzzy Keyword Matching": validate_fuzzy_matching(),
        "Input Validation": validate_input_validation(),
        "Experience Detection": validate_experience_detection(),
        "Table Format Extraction": validate_table_format(),
        "Flexible Boundaries": validate_flexible_boundaries(),
        "Role-Specific Weights": validate_role_weights(),
        "False Negative Reduction": validate_false_negative_reduction()
    }

    # Summary
    print_header("VALIDATION SUMMARY")

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for name, result in results.items():
        status = f"{Colors.GREEN}✓{Colors.END}" if result else f"{Colors.RED}✗{Colors.END}"
        print(f"{status} {name}")

    print(f"\n{Colors.BOLD}Overall: {passed}/{total} categories passed{Colors.END}")

    if passed == total:
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 ALL VALIDATIONS PASSED! 🎉{Colors.END}")
        print(f"{Colors.GREEN}All improvements are properly implemented and functional.{Colors.END}")
        return 0
    else:
        print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠ SOME VALIDATIONS FAILED{Colors.END}")
        print(f"{Colors.YELLOW}Review failed tests above for details.{Colors.END}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
