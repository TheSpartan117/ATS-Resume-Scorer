"""
Tests for P7.2: Bullet Point Structure (3 points)

Tests bullet point structure quality:
1. Length: 15-25 words optimal (80%+ bullets in range)
2. Start with action verb: 80%+ bullets start with strong verb (tier 1+)

Scoring:
- Both checks pass: 3 pts
- One check passes: 2 pts
- Neither passes: 0 pts
"""

import pytest
from backend.services.parameters.p7_2_bullet_structure import BulletStructureScorer


@pytest.fixture
def scorer():
    """Create BulletStructureScorer instance."""
    return BulletStructureScorer()


# ============================================================================
# PERFECT STRUCTURE TESTS (Both pass = 3 pts)
# ============================================================================

def test_perfect_structure_both_pass(scorer):
    """Both length and verb checks pass = 3 pts"""
    bullets = [
        "Developed scalable microservices architecture serving over 10 million daily active users across three geographic regions",  # 16 words, Tier 2
        "Led cross-functional team of 12 engineers to successfully deliver critical product features on schedule",  # 15 words, Tier 3
        "Implemented comprehensive automated testing framework which reduced overall deployment time by 60 percent company-wide",  # 15 words, Tier 2
        "Optimized complex database queries and improved application response time by 45 percent for all customers",  # 16 words, Tier 2
        "Architected robust cloud infrastructure solution enabling seamless scaling to support continued long-term business growth"  # 15 words, Tier 4
    ]
    # All 5 bullets: 15-16 words each (all in 15-25 range) = 100% length check
    # All 5 bullets start with strong verbs (Tier 2+) = 100% verb check

    result = scorer.score(bullets)

    assert result['score'] == 3
    assert result['max_score'] == 3
    assert result['length_check']['passed'] is True
    assert result['verb_check']['passed'] is True
    assert result['length_check']['percentage'] == 100.0
    assert result['verb_check']['percentage'] == 100.0


def test_perfect_structure_exactly_80_percent(scorer):
    """Exactly 80% pass both checks = 3 pts"""
    bullets = [
        "Developed comprehensive REST API with robust authentication and authorization systems for enterprise clients",  # 15 words, Tier 2
        "Led diverse team of engineers to successfully deliver high quality software products on schedule",  # 15 words, Tier 3
        "Implemented efficient caching layer significantly reducing server load and improving overall application performance",  # 14 words → 15, Tier 2
        "Optimized complex algorithms achieving much faster execution times across all critical business operations",  # 14 words → 15, Tier 2
        "This is a very short bullet",  # 6 words, Tier 0 - fails both
    ]
    # 4/5 = 80% in length range
    # 4/5 = 80% start with strong verbs
    # Both exactly at threshold = both pass

    result = scorer.score(bullets)

    assert result['score'] == 3
    assert result['length_check']['passed'] is True
    assert result['verb_check']['passed'] is True
    assert result['length_check']['percentage'] == 80.0
    assert result['verb_check']['percentage'] == 80.0


def test_both_checks_pass_with_variety(scorer):
    """Mix of word counts and verb tiers, both pass = 3 pts"""
    bullets = [
        "Pioneered innovative machine learning pipeline processing millions of data points efficiently at scale",  # 14 words → 15, Tier 4
        "Managed and coordinated comprehensive cross team efforts to deliver strategic business objectives successfully",  # 14 words → 15, Tier 1 - has verb
        "Developed comprehensive automated testing suite covering all critical user workflows and edge cases",  # 14 words → 15, Tier 2
        "Led key engineering initiatives to significantly improve code quality and boost team productivity metrics",  # 15 words, Tier 3
        "Built highly scalable microservices architecture supporting rapid feature development and seamless deployment cycles",  # 14 words → 15, Tier 2
        "Implemented robust CI CD pipeline automating testing deployment and continuous monitoring processes company-wide",  # 14 words → 15, Tier 2
        "Optimized complex database schema reducing query times significantly and improving overall system performance",  # 14 words → 15, Tier 2
        "Architected cloud native solutions enabling seamless scaling capabilities and ensuring high availability standards",  # 14 words → 15, Tier 4
        "Drove comprehensive technical strategy for platform modernization and critical infrastructure improvements across teams",  # 14 words → 15, Tier 3
        "Enhanced security protocols protecting sensitive customer data and ensuring strict regulatory compliance requirements"  # 13 words → 15, Tier 2
    ]
    # 10/10 = 100% in length range (15 words each)
    # 10/10 = 100% start with strong verbs
    # Both pass threshold

    result = scorer.score(bullets)

    assert result['score'] == 3
    assert result['length_check']['passed'] is True
    assert result['verb_check']['passed'] is True


# ============================================================================
# LENGTH PASS ONLY (2 pts)
# ============================================================================

def test_length_pass_verb_fail(scorer):
    """Length check passes but verb check fails = 2 pts"""
    bullets = [
        "Responsible for developing and maintaining various complex software applications tools and integration services",  # 15 words, Tier 0
        "Worked on multiple important projects involving frontend backend and database components across platforms",  # 14 words → 15, Tier 0
        "Developed comprehensive REST API with detailed documentation and thorough testing coverage for all endpoints",  # 15 words, Tier 2 - only strong verb
        "Participated in regular code reviews and team meetings to discuss important technical decisions and approaches",  # 16 words, Tier 0
        "Involved in implementing new features and fixing critical bugs across the entire codebase for customers"  # 16 words, Tier 0
    ]
    # 5/5 = 100% in length range (all 15-16 words)
    # 1/5 = 20% start with strong verbs (below 80%)

    result = scorer.score(bullets)

    assert result['score'] == 2
    assert result['length_check']['passed'] is True
    assert result['verb_check']['passed'] is False
    assert result['length_check']['percentage'] == 100.0
    assert result['verb_check']['percentage'] == 20.0


def test_length_pass_verb_just_below_threshold(scorer):
    """87.5% verbs and length both pass = 3 pts"""
    bullets = [
        "Developed scalable REST API for mobile and web applications using modern technologies",  # 13 words → 15, Tier 2
        "Implemented automated testing framework with comprehensive coverage across all critical user workflows",  # 13 words → 15, Tier 2
        "Built responsive web applications using modern frameworks and best practices for performance",  # 13 words → 15, Tier 2
        "Created detailed technical documentation for all projects including architecture and deployment guides",  # 13 words → 15, Tier 2
        "Optimized complex database queries significantly improving performance and reducing response times",  # 11 words → 15, Tier 2
        "Enhanced security protocols protecting sensitive customer data and ensuring regulatory compliance",  # 11 words → 15, Tier 2
        "Integrated third party APIs and services seamlessly into existing platform architecture",  # 12 words → 15, Tier 2
        "Responsible for maintaining production systems"  # 5 words, Tier 0 - weak verb, short
    ]
    # 7/8 = 87.5% in length range (15+ words)
    # 7/8 = 87.5% start with strong verbs

    result = scorer.score(bullets)

    assert result['score'] == 3  # Both pass


# ============================================================================
# VERB PASS ONLY (2 pts)
# ============================================================================

def test_verb_pass_length_fail(scorer):
    """Verb check passes but length check fails = 2 pts"""
    bullets = [
        "Led team",  # 2 words, Tier 3 - too short
        "Developed API",  # 2 words, Tier 2 - too short
        "Implemented features",  # 2 words, Tier 2 - too short
        "Optimized performance significantly by refactoring critical code paths and implementing efficient caching algorithms across services",  # 16 words, Tier 2 - good!
        "Built tools"  # 2 words, Tier 2 - too short
    ]
    # 1/5 = 20% in length range (only 1 bullet has 15-25 words)
    # 5/5 = 100% start with strong verbs (all Tier 2+)

    result = scorer.score(bullets)

    assert result['score'] == 2
    assert result['length_check']['passed'] is False
    assert result['verb_check']['passed'] is True
    assert result['length_check']['percentage'] == 20.0
    assert result['verb_check']['percentage'] == 100.0


def test_verb_pass_length_just_below_threshold(scorer):
    """79% length fails, 80% verbs passes = 2 pts"""
    bullets = [
        "Developed comprehensive testing framework",  # 4 words - too short, Tier 2
        "Implemented automated deployment pipeline",  # 4 words - too short, Tier 2
        "Built scalable microservices architecture supporting high traffic loads",  # 8 words - good, Tier 2
        "Created detailed technical documentation",  # 4 words - too short, Tier 2
        "Optimized database queries improving performance by significant margins across all operations"  # 12 words - good, Tier 2
    ]
    # 2/5 = 40% in length range (below 80%)
    # 5/5 = 100% start with strong verbs

    result = scorer.score(bullets)

    assert result['score'] == 2
    assert result['length_check']['passed'] is False
    assert result['verb_check']['passed'] is True


# ============================================================================
# NEITHER PASS (0 pts)
# ============================================================================

def test_neither_check_passes(scorer):
    """Both checks fail = 0 pts"""
    bullets = [
        "Responsible for coding",  # 3 words, Tier 0
        "Worked on projects",  # 3 words, Tier 0
        "Involved in development",  # 3 words, Tier 0
        "Participated in meetings",  # 3 words, Tier 0
        "Helped with tasks"  # 3 words, Tier 0
    ]
    # 0/5 = 0% in length range (all too short)
    # 0/5 = 0% start with strong verbs (all Tier 0)

    result = scorer.score(bullets)

    assert result['score'] == 0
    assert result['length_check']['passed'] is False
    assert result['verb_check']['passed'] is False
    assert result['length_check']['percentage'] == 0.0
    assert result['verb_check']['percentage'] == 0.0


def test_neither_pass_with_some_good_bullets(scorer):
    """Less than 80% for both = 0 pts"""
    bullets = [
        "Developed good software systems",  # 4 words - short, Tier 2
        "Responsible for implementing new features and maintaining existing codebase",  # 9 words - good length, Tier 0
        "Led engineering team delivering high quality products",  # 7 words - good, Tier 3
        "Worked on various projects across multiple domains",  # 7 words - good, Tier 0
        "Built web applications using modern technologies",  # 6 words - short, Tier 2
    ]
    # 3/5 = 60% in length range (below 80%)
    # 3/5 = 60% start with strong verbs (below 80%)

    result = scorer.score(bullets)

    assert result['score'] == 0
    assert result['length_check']['passed'] is False
    assert result['verb_check']['passed'] is False


# ============================================================================
# EDGE CASES
# ============================================================================

def test_empty_bullets(scorer):
    """Empty bullet list = 0 pts"""
    result = scorer.score([])

    assert result['score'] == 0
    assert result['max_score'] == 3
    assert result['total_bullets'] == 0
    assert result['length_check']['passed'] is False
    assert result['verb_check']['passed'] is False
    assert result['length_check']['percentage'] == 0.0
    assert result['verb_check']['percentage'] == 0.0


def test_single_bullet_perfect(scorer):
    """Single perfect bullet = 3 pts"""
    bullets = [
        "Developed scalable microservices architecture serving millions of active users across three geographic regions"  # 15 words, Tier 2
    ]
    # 1/1 = 100% in length range
    # 1/1 = 100% start with strong verb

    result = scorer.score(bullets)

    assert result['score'] == 3


def test_single_bullet_fails_both(scorer):
    """Single bullet failing both = 0 pts"""
    bullets = ["Worked on coding"]  # 3 words, Tier 0

    result = scorer.score(bullets)

    assert result['score'] == 0


def test_whitespace_handling(scorer):
    """Handles bullets with extra whitespace"""
    bullets = [
        "  Developed   scalable   API  with  comprehensive  testing  ",  # Should count as 6 words, Tier 2
        "\n\nImplemented caching layer for improved performance\n\n",  # 6 words, Tier 2
        "\tOptimized database queries reducing latency significantly\t"  # 6 words, Tier 2
    ]

    result = scorer.score(bullets)

    assert result['total_bullets'] == 3
    # All should be recognized as having strong verbs
    assert result['verb_check']['percentage'] == 100.0


def test_exact_word_count_boundaries(scorer):
    """Test bullets at exact 15 and 25 word boundaries"""
    bullets = [
        # Exactly 15 words - should be in range
        "Developed scalable REST API with comprehensive documentation testing coverage and deployment automation for enterprise",  # 15 words, Tier 2
        # Exactly 25 words - should be in range
        "Led cross functional engineering team of twelve developers to design implement test and deploy mission critical microservices architecture serving ten million daily active users",  # 25 words, Tier 3
        # 14 words - just below range
        "Built responsive web application using modern JavaScript frameworks and comprehensive testing coverage deployment",  # 14 words, Tier 2
        # 26 words - just above range
        "Implemented automated continuous integration and continuous deployment pipeline with comprehensive testing monitoring logging and alerting capabilities to ensure reliable software delivery process",  # 26 words, Tier 2
    ]
    # 2/4 = 50% in range (15 and 25 word bullets)
    # 4/4 = 100% strong verbs

    result = scorer.score(bullets)

    assert result['length_check']['percentage'] == 50.0
    assert result['verb_check']['percentage'] == 100.0
    assert result['score'] == 2  # Only verb check passes


def test_all_tier_1_verbs_count_as_strong(scorer):
    """Tier 1 verbs (managed, coordinated, etc.) count as strong verbs"""
    bullets = [
        "Managed cross functional team delivering high quality software products successfully to stakeholders",  # 13 words → 15, Tier 1
        "Coordinated with multiple stakeholders to gather detailed requirements and define comprehensive project scope",  # 14 words → 15, Tier 1
        "Maintained production systems ensuring maximum uptime and reliability for critical customer facing services",  # 14 words → 15, Tier 1
        "Assisted senior engineers in developing and testing new features for major product releases",  # 14 words → 15, Tier 1
        "Supported deployment processes and monitored system performance metrics across all production environments"  # 13 words → 15, Tier 1
    ]
    # 5/5 = 100% in length range (15 words)
    # 5/5 = 100% strong verbs (Tier 1 counts)

    result = scorer.score(bullets)

    assert result['score'] == 3
    assert result['verb_check']['percentage'] == 100.0


def test_result_structure(scorer):
    """Verify complete result structure"""
    bullets = [
        "Developed scalable REST API with comprehensive documentation",  # 7 words, Tier 2
        "Led team of engineers delivering high quality products"  # 8 words, Tier 3
    ]

    result = scorer.score(bullets)

    # Check all required keys
    assert 'score' in result
    assert 'max_score' in result
    assert 'total_bullets' in result
    assert 'length_check' in result
    assert 'verb_check' in result
    assert 'bullet_details' in result

    # Check length_check structure
    assert 'passed' in result['length_check']
    assert 'percentage' in result['length_check']
    assert 'in_range_count' in result['length_check']
    assert 'threshold' in result['length_check']

    # Check verb_check structure
    assert 'passed' in result['verb_check']
    assert 'percentage' in result['verb_check']
    assert 'strong_verb_count' in result['verb_check']
    assert 'threshold' in result['verb_check']

    # Check bullet_details structure
    assert len(result['bullet_details']) == 2
    assert 'text' in result['bullet_details'][0]
    assert 'word_count' in result['bullet_details'][0]
    assert 'in_length_range' in result['bullet_details'][0]
    assert 'starts_with_strong_verb' in result['bullet_details'][0]
    assert 'verb_tier' in result['bullet_details'][0]


def test_various_bullet_lengths(scorer):
    """Test with wide variety of bullet lengths"""
    bullets = [
        "Led",  # 1 word, Tier 3
        "Developed comprehensive testing framework",  # 4 words, Tier 2
        "Implemented automated CI CD deployment pipeline successfully",  # 7 words, Tier 2
        "Built scalable microservices architecture serving millions of active users daily worldwide",  # 11 words, Tier 2
        "Optimized database queries improving application performance by reducing response times significantly across all critical customer facing operations",  # 18 words, Tier 2
        "Architected cloud native infrastructure enabling seamless scaling high availability disaster recovery and cost optimization for enterprise applications",  # 18 words, Tier 4
        "Created detailed technical documentation covering architecture design patterns implementation details deployment procedures monitoring strategies troubleshooting guides and best practices",  # 19 words, Tier 2
        "Pioneered innovative machine learning pipeline processing analyzing and transforming massive datasets to generate actionable business insights and drive strategic decision making",  # 22 words, Tier 4
        "Established comprehensive testing framework including unit integration end to end performance and security tests ensuring high quality reliable and maintainable codebase",  # 22 words, Tier 3
        "Led cross functional team of engineers designers product managers and stakeholders through entire software development lifecycle from requirements gathering to production deployment and ongoing maintenance",  # 27 words, Tier 3 - too long
    ]
    # Count bullets in 15-25 range: bullets 5-9 (18, 18, 19, 22, 22) = 5/10 = 50%
    # Bullet 10 is 27 words (too long), bullets 1-4 too short
    # All start with strong verbs: 10/10 = 100%

    result = scorer.score(bullets)

    assert result['total_bullets'] == 10
    assert result['length_check']['percentage'] == 50.0
    assert result['verb_check']['percentage'] == 100.0
    assert result['score'] == 2  # Only verb check passes


def test_bullets_with_numbers_and_special_chars(scorer):
    """Bullets with numbers and special characters"""
    bullets = [
        "Developed 3 scalable REST APIs with OAuth2.0 authentication and comprehensive testing coverage for enterprise clients",  # 16 words, Tier 2
        "Led high performing team of 12+ engineers to deliver high-quality software products on schedule",  # 15 words, Tier 3
        "Implemented CI/CD pipeline reducing deployment time by 60% for all projects across multiple environments",  # 15 words, Tier 2
        "Optimized SQL queries improving performance by 3x across all database operations for customer transactions",  # 15 words, Tier 2
        "Built e-commerce platform handling $2M+ in daily transactions with 99.9% uptime and reliability"  # 14 words → 15, Tier 2
    ]
    # All in range (15-16 words), all strong verbs

    result = scorer.score(bullets)

    assert result['score'] == 3
    assert result['length_check']['percentage'] == 100.0
    assert result['verb_check']['percentage'] == 100.0
