"""
Tests for P1.1: Required Keywords Match (25 points)

Tests the highest-weighted parameter that uses hybrid semantic+exact matching
to evaluate required keyword coverage with tiered scoring.

Scoring tiers (Workday standard - 60% passing):
- ≥60%: 25 points
- ≥40%: 15 points
- ≥25%: 5 points
- <25%: 0 points
"""

import pytest
from backend.services.parameters.p1_1_required_keywords import RequiredKeywordsMatcher
from tests.conftest import requires_semantic_model


@pytest.fixture
def matcher():
    """Create matcher instance for tests."""
    return RequiredKeywordsMatcher()


# ============================================================================
# TIER SCORING TESTS
# ============================================================================

def test_all_keywords_matched(matcher):
    """100% match = 25 points"""
    keywords = ['Python', 'Django', 'REST API']
    resume_text = "Expert in Python and Django. Built REST API services."

    result = matcher.score(keywords, resume_text, 'intermediary')

    assert result['match_percentage'] >= 90
    assert result['score'] == 25
    assert result['max_score'] == 25
    assert len(result['matched_keywords']) == 3
    assert len(result['unmatched_keywords']) == 0


def test_60_percent_match(matcher):
    """60% match = 25 points (meets threshold)"""
    keywords = ['Python', 'Django', 'AWS', 'Docker', 'Redis']
    resume_text = "Python developer with Django and AWS experience."

    result = matcher.score(keywords, resume_text, 'intermediary')

    # 3/5 = 60%
    assert 55 <= result['match_percentage'] <= 65
    assert result['score'] == 25
    assert len(result['matched_keywords']) == 3


def test_40_percent_match(matcher):
    """40-59% match = 15 points"""
    keywords = ['Python', 'Django', 'AWS', 'Docker', 'Redis']
    resume_text = "Python developer with some Django knowledge."

    result = matcher.score(keywords, resume_text, 'intermediary')

    # 2/5 = 40%
    assert 35 <= result['match_percentage'] <= 45
    assert result['score'] == 15


def test_25_percent_match(matcher):
    """25-39% match = 5 points"""
    keywords = ['Python', 'Django', 'AWS', 'Docker']
    resume_text = "Python developer."

    result = matcher.score(keywords, resume_text, 'intermediary')

    # 1/4 = 25%
    assert 20 <= result['match_percentage'] <= 30
    assert result['score'] == 5


def test_below_25_percent(matcher):
    """<25% match = 0 points"""
    keywords = ['Python', 'Django', 'AWS', 'Docker', 'Redis']
    resume_text = "Java developer with Spring Boot."

    result = matcher.score(keywords, resume_text, 'intermediary')

    assert result['match_percentage'] < 25
    assert result['score'] == 0


# ============================================================================
# SEMANTIC MATCHING TESTS
# ============================================================================

@requires_semantic_model
def test_semantic_matching_works(matcher):
    """Semantic matching should catch variations"""
    keywords = ['Machine Learning', 'Python']
    resume_text = "ML engineer with Pythonic coding practices."

    result = matcher.score(keywords, resume_text, 'intermediary')

    # Should match both via semantic similarity
    assert result['match_percentage'] >= 80
    assert result['score'] == 25  # Should get full points


@requires_semantic_model
def test_semantic_matching_abbreviations(matcher):
    """Semantic matching should handle abbreviations"""
    keywords = ['API', 'UI/UX', 'CI/CD']
    resume_text = "Built APIs with great user interface design. Set up continuous integration pipelines."

    result = matcher.score(keywords, resume_text, 'intermediary')

    # Should match all three via semantic similarity
    assert result['match_percentage'] >= 80


def test_hybrid_matching_compound_terms(matcher):
    """Hybrid matching should handle compound terms"""
    keywords = ['React', 'Node.js', 'TypeScript']
    resume_text = "Frontend developer using React.js and Node.js. Strong TypeScript skills."

    result = matcher.score(keywords, resume_text, 'intermediary')

    # All should match via exact or semantic
    assert result['match_percentage'] >= 90
    assert result['score'] == 25


# ============================================================================
# DETAILED BREAKDOWN TESTS
# ============================================================================

def test_detailed_breakdown(matcher):
    """Should return detailed match breakdown"""
    keywords = ['Python', 'Django', 'AWS']
    resume_text = "Python and Django developer."

    result = matcher.score(keywords, resume_text, 'intermediary')

    # Check structure
    assert 'matched_keywords' in result
    assert 'unmatched_keywords' in result
    assert 'match_details' in result
    assert 'match_percentage' in result
    assert 'score' in result
    assert 'max_score' in result
    assert 'tier_applied' in result

    # Check content
    assert 'Python' in result['matched_keywords']
    assert 'Django' in result['matched_keywords']
    assert 'AWS' in result['unmatched_keywords']

    # Check match details has scores for all keywords
    assert 'Python' in result['match_details']
    assert 'Django' in result['match_details']
    assert 'AWS' in result['match_details']


def test_match_details_have_scores(matcher):
    """Match details should contain score for each keyword"""
    keywords = ['Python', 'React', 'SQL']
    resume_text = "Python developer with database experience."

    result = matcher.score(keywords, resume_text, 'intermediary')

    # All keywords should have scores
    for keyword in keywords:
        assert keyword in result['match_details']
        assert 0.0 <= result['match_details'][keyword] <= 1.0


# ============================================================================
# EDGE CASES
# ============================================================================

def test_empty_keywords_list(matcher):
    """Empty keywords should return full score"""
    keywords = []
    resume_text = "Python developer with extensive experience."

    result = matcher.score(keywords, resume_text, 'intermediary')

    assert result['score'] == 25
    assert result['match_percentage'] == 100.0
    assert result['matched_keywords'] == []
    assert result['unmatched_keywords'] == []


def test_single_keyword_matched(matcher):
    """Single keyword matched should return 100%"""
    keywords = ['Python']
    resume_text = "Expert Python developer."

    result = matcher.score(keywords, resume_text, 'intermediary')

    assert result['match_percentage'] >= 90
    assert result['score'] == 25


def test_single_keyword_unmatched(matcher):
    """Single keyword unmatched should return 0%"""
    keywords = ['Python']
    resume_text = "Java and C++ developer."

    result = matcher.score(keywords, resume_text, 'intermediary')

    assert result['match_percentage'] < 25
    assert result['score'] == 0


def test_case_insensitive_matching(matcher):
    """Should handle case variations"""
    keywords = ['python', 'DJANGO', 'React']
    resume_text = "Python, Django, and react developer."

    result = matcher.score(keywords, resume_text, 'intermediary')

    # All should match despite case differences
    assert result['match_percentage'] >= 90
    assert result['score'] == 25


# ============================================================================
# LEVEL-SPECIFIC TESTS
# ============================================================================

def test_beginner_level(matcher):
    """Should work with beginner level"""
    keywords = ['Python', 'Django', 'Git']
    resume_text = "Python developer with Django and Git experience."

    result = matcher.score(keywords, resume_text, 'beginner')

    assert result['match_percentage'] >= 90
    assert result['score'] == 25


def test_senior_level(matcher):
    """Should work with senior level"""
    keywords = ['Python', 'Django', 'AWS', 'Docker', 'Kubernetes']
    resume_text = "Senior Python developer. Django expert with AWS infrastructure. Docker and Kubernetes deployments."

    result = matcher.score(keywords, resume_text, 'senior')

    assert result['match_percentage'] >= 90
    assert result['score'] == 25


# ============================================================================
# REAL-WORLD SCENARIOS
# ============================================================================

def test_realistic_job_description(matcher):
    """Test with realistic job description keywords"""
    keywords = [
        'Python', 'Django', 'REST API', 'PostgreSQL', 'Redis',
        'AWS', 'Docker', 'Git', 'Agile', 'CI/CD'
    ]
    resume_text = """
    Senior Software Engineer with 5 years experience.

    Skills:
    - Python programming and Django framework
    - Built RESTful APIs serving millions of requests
    - Database design with PostgreSQL and Redis caching
    - Deployed on AWS using Docker containers
    - Git version control and agile methodology
    """

    result = matcher.score(keywords, resume_text, 'intermediary')

    # Should match most keywords (Python, Django, REST, PostgreSQL, Redis, AWS, Docker, Git, Agile)
    # CI/CD might not match perfectly
    assert result['match_percentage'] >= 80  # 8-9/10 = 80-90%
    assert result['score'] == 25


def test_poor_match_scenario(matcher):
    """Test scenario with poor keyword match"""
    keywords = [
        'React', 'Angular', 'Vue.js', 'TypeScript', 'JavaScript',
        'Node.js', 'MongoDB', 'GraphQL', 'Redux', 'Webpack'
    ]
    resume_text = """
    Python Backend Developer

    Experience with Django, Flask, and FastAPI.
    Database expertise in PostgreSQL and MySQL.
    RESTful API design and microservices architecture.
    """

    result = matcher.score(keywords, resume_text, 'intermediary')

    # Very few matches expected (maybe JavaScript via semantic)
    assert result['match_percentage'] < 25
    assert result['score'] == 0


def test_partial_match_scenario(matcher):
    """Test scenario with partial keyword match"""
    keywords = [
        'Python', 'Django', 'Flask', 'FastAPI', 'SQLAlchemy',
        'Celery', 'RabbitMQ', 'Docker', 'Kubernetes', 'AWS'
    ]
    resume_text = """
    Python Developer with 3 years experience.

    Built web applications using Django and Flask.
    Implemented background tasks with Celery.
    Deployed using Docker on AWS infrastructure.
    """

    result = matcher.score(keywords, resume_text, 'intermediary')

    # Should match: Python, Django, Flask, Celery, Docker, AWS = 6/10 = 60%
    # Might also catch FastAPI semantically
    assert 50 <= result['match_percentage'] <= 70
    assert result['score'] == 25  # Should meet 60% threshold


# ============================================================================
# BOUNDARY TESTS
# ============================================================================

def test_exactly_60_percent_boundary(matcher):
    """Test exact 60% match boundary"""
    keywords = ['A', 'B', 'C', 'D', 'E']
    # Ensure exactly 3/5 match (60%)
    resume_text = "Skills include A, B, and C."

    result = matcher.score(keywords, resume_text, 'intermediary')

    # Should be at or near 60%
    assert result['match_percentage'] >= 55
    assert result['score'] == 25  # Should get full points at threshold


def test_exactly_40_percent_boundary(matcher):
    """Test exact 40% match boundary"""
    keywords = ['A', 'B', 'C', 'D', 'E']
    # Ensure exactly 2/5 match (40%)
    resume_text = "Skills include A and B."

    result = matcher.score(keywords, resume_text, 'intermediary')

    # Should be at or near 40%
    assert 35 <= result['match_percentage'] <= 45
    assert result['score'] == 15


def test_exactly_25_percent_boundary(matcher):
    """Test exact 25% match boundary"""
    keywords = ['A', 'B', 'C', 'D']
    # Ensure exactly 1/4 match (25%)
    resume_text = "Skills include A."

    result = matcher.score(keywords, resume_text, 'intermediary')

    # Should be at or near 25%
    assert 20 <= result['match_percentage'] <= 30
    assert result['score'] == 5
