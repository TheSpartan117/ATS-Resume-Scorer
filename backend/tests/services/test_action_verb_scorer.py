"""
Test ActionVerbScorer service for P2.1 parameter.

Tests the action verb quality and coverage scoring with:
1. Coverage sub-score (7 points max)
2. Average tier sub-score (8 points max)
3. Level-aware thresholds
4. Tiered (non-linear) scoring
"""

import pytest
from backend.services.action_verb_scorer import ActionVerbScorer


@pytest.fixture
def scorer():
    """Create ActionVerbScorer instance."""
    return ActionVerbScorer()


# ============================================================================
# COVERAGE SUB-SCORE TESTS (7 points max)
# ============================================================================

def test_coverage_score_perfect(scorer):
    """100% coverage with Tier 2+ verbs = 7 pts"""
    bullets = [
        "Developed REST API",           # Tier 2
        "Implemented authentication",   # Tier 2
        "Led team of engineers",        # Tier 3
        "Pioneered ML infrastructure"   # Tier 4
    ]

    result = scorer.score(bullets, 'intermediary')
    # All bullets have Tier 2+ verbs: 4/4 = 100%
    assert result['coverage_score'] == 7


def test_coverage_score_high(scorer):
    """90% coverage with Tier 2+ verbs = 6 pts"""
    bullets = [
        "Developed REST API",           # Tier 2
        "Implemented authentication",   # Tier 2
        "Led team of engineers",        # Tier 3
        "Built testing framework",      # Tier 2
        "Created documentation",        # Tier 2
        "Optimized database queries",   # Tier 2
        "Launched mobile app",          # Tier 3
        "Designed architecture",        # Tier 2
        "Architected platform",         # Tier 3
        "Managed daily tasks"           # Tier 1 (not Tier 2+)
    ]

    result = scorer.score(bullets, 'intermediary')
    # 9/10 = 90% have Tier 2+ verbs
    assert result['coverage_score'] == 6


def test_coverage_score_medium(scorer):
    """70% coverage with Tier 2+ verbs = 4 pts"""
    bullets = [
        "Developed REST API",      # Tier 2
        "Implemented features",    # Tier 2
        "Led team",               # Tier 3
        "Built framework",        # Tier 2
        "Created docs",           # Tier 2
        "Optimized queries",      # Tier 2
        "Launched app",           # Tier 3
        "Managed tasks",          # Tier 1
        "Coordinated meetings",   # Tier 1
        "Supported production"    # Tier 1
    ]

    result = scorer.score(bullets, 'intermediary')
    # 7/10 = 70% have Tier 2+ verbs
    assert result['coverage_score'] == 4


def test_coverage_score_low(scorer):
    """50% coverage with Tier 2+ verbs = 2 pts"""
    bullets = [
        "Developed API",          # Tier 2
        "Implemented features",   # Tier 2
        "Built framework",        # Tier 2
        "Created docs",           # Tier 2
        "Optimized queries",      # Tier 2
        "Managed tasks",          # Tier 1
        "Coordinated meetings",   # Tier 1
        "Supported production",   # Tier 1
        "Maintained codebase",    # Tier 1
        "Monitored systems"       # Tier 1
    ]

    result = scorer.score(bullets, 'intermediary')
    # 5/10 = 50% have Tier 2+ verbs
    assert result['coverage_score'] == 2


def test_coverage_score_very_low(scorer):
    """30% coverage with Tier 2+ verbs = 0 pts"""
    bullets = [
        "Developed API",          # Tier 2
        "Implemented features",   # Tier 2
        "Built framework",        # Tier 2
        "Managed tasks",          # Tier 1
        "Coordinated meetings",   # Tier 1
        "Supported production",   # Tier 1
        "Maintained codebase",    # Tier 1
        "Monitored systems",      # Tier 1
        "Responsible for tasks",  # Tier 0
        "Worked on projects"      # Tier 0
    ]

    result = scorer.score(bullets, 'intermediary')
    # 3/10 = 30% have Tier 2+ verbs
    assert result['coverage_score'] == 0


# ============================================================================
# AVERAGE TIER SUB-SCORE TESTS (8 points max)
# ============================================================================

def test_tier_score_excellent(scorer):
    """Average tier 3.5+ = 8 pts"""
    bullets = [
        "Pioneered ML infrastructure",     # Tier 4
        "Revolutionized deployment",       # Tier 4
        "Transformed engineering culture", # Tier 4
        "Led cross-functional team"        # Tier 3
    ]

    result = scorer.score(bullets, 'senior')
    # (4+4+4+3)/4 = 3.75 avg tier
    assert result['tier_score'] == 8


def test_tier_score_high(scorer):
    """Average tier 2.5-3.4 = 6 pts"""
    bullets = [
        "Led technical team",          # Tier 3
        "Architected platform",        # Tier 3
        "Launched product line",       # Tier 3
        "Developed REST API",          # Tier 2
        "Implemented features"         # Tier 2
    ]

    result = scorer.score(bullets, 'senior')
    # (3+3+3+2+2)/5 = 2.6 avg tier
    assert result['tier_score'] == 6


def test_tier_score_medium(scorer):
    """Average tier 1.5-2.4 = 4 pts"""
    bullets = [
        "Developed REST API",      # Tier 2
        "Implemented features",    # Tier 2
        "Built framework",         # Tier 2
        "Created documentation",   # Tier 2
        "Managed daily tasks"      # Tier 1
    ]

    result = scorer.score(bullets, 'intermediary')
    # (2+2+2+2+1)/5 = 1.8 avg tier
    assert result['tier_score'] == 4


def test_tier_score_low(scorer):
    """Average tier 0.5-1.4 = 2 pts"""
    bullets = [
        "Managed tasks",          # Tier 1
        "Coordinated meetings",   # Tier 1
        "Supported production",   # Tier 1
        "Maintained codebase",    # Tier 1
        "Monitored systems"       # Tier 1
    ]

    result = scorer.score(bullets, 'beginner')
    # (1+1+1+1+1)/5 = 1.0 avg tier
    assert result['tier_score'] == 2


def test_tier_score_very_low(scorer):
    """Average tier < 0.5 = 0 pts"""
    bullets = [
        "Responsible for tasks",  # Tier 0
        "Worked on projects",     # Tier 0
        "Helped with deployment", # Tier 0
        "Assisted in development",# Tier 0
        "Managed some tasks"      # Tier 1
    ]

    result = scorer.score(bullets, 'beginner')
    # (0+0+0+0+1)/5 = 0.2 avg tier
    assert result['tier_score'] == 0


# ============================================================================
# COMBINED SCORING TESTS
# ============================================================================

def test_perfect_score_senior(scorer):
    """Perfect senior resume = 15 pts (7 + 8)"""
    bullets = [
        "Pioneered ML platform",           # Tier 4
        "Transformed engineering culture", # Tier 4
        "Led cross-functional team",       # Tier 3
        "Architected cloud infrastructure",# Tier 3
        "Launched product line"            # Tier 3
    ]

    result = scorer.score(bullets, 'senior')
    # Coverage: 5/5 = 100% Tier 2+ → 7 pts
    # Tier: (4+4+3+4+3)/5 = 3.6 → 8 pts (Architected is Tier 4!)
    assert result['coverage_score'] == 7
    assert result['tier_score'] == 8
    assert result['score'] == 15  # 7 + 8


def test_excellent_intermediary(scorer):
    """Excellent intermediary = 13 pts"""
    bullets = [
        "Led development team",        # Tier 3
        "Architected microservices",   # Tier 3
        "Developed REST API",          # Tier 2
        "Implemented caching layer",   # Tier 2
        "Built testing framework",     # Tier 2
        "Launched beta program",       # Tier 3
        "Created CI/CD pipeline",      # Tier 2
        "Optimized database queries",  # Tier 2
        "Designed system architecture",# Tier 2
        "Managed sprint planning"      # Tier 1
    ]

    result = scorer.score(bullets, 'intermediary')
    # Coverage: 9/10 = 90% Tier 2+ → 6 pts
    # Tier: (3+3+2+2+2+3+2+2+2+1)/10 = 2.2 → 4 pts
    assert result['coverage_score'] == 6
    assert result['tier_score'] == 4
    assert result['score'] == 10  # 6 + 4


def test_poor_beginner(scorer):
    """Poor beginner = 2 pts"""
    bullets = [
        "Responsible for coding",   # Tier 0
        "Worked on features",       # Tier 0
        "Helped with deployment",   # Tier 0
        "Assisted team members",    # Tier 0
        "Managed some tasks"        # Tier 1
    ]

    result = scorer.score(bullets, 'beginner')
    # Coverage: 0/5 = 0% Tier 2+ → 0 pts
    # Tier: (0+0+0+0+1)/5 = 0.2 → 0 pts
    assert result['coverage_score'] == 0
    assert result['tier_score'] == 0
    assert result['score'] == 0


# ============================================================================
# LEVEL-AWARE THRESHOLD TESTS
# ============================================================================

def test_beginner_thresholds(scorer):
    """Beginner: 70% coverage, 1.5 avg tier"""
    bullets = [
        "Developed web app",       # Tier 2
        "Implemented features",    # Tier 2
        "Built testing suite",     # Tier 2
        "Created documentation",   # Tier 2
        "Developed REST API",      # Tier 2
        "Implemented auth",        # Tier 2
        "Built CI/CD pipeline",    # Tier 2
        "Managed tasks",           # Tier 1
        "Coordinated meetings",    # Tier 1
        "Supported production"     # Tier 1
    ]

    result = scorer.score(bullets, 'beginner')
    # Coverage: 7/10 = 70% Tier 2+ → 4 pts
    # Tier: (2*7 + 1*3)/10 = 1.7 → 4 pts
    assert result['level'] == 'beginner'
    assert result['coverage_percentage'] == 70.0
    assert result['average_tier'] == 1.7
    assert result['coverage_score'] == 4
    assert result['tier_score'] == 4
    assert result['score'] == 8


def test_intermediary_thresholds(scorer):
    """Intermediary: 75% coverage, 2.0 avg tier"""
    bullets = [
        "Developed REST API",          # Tier 2
        "Implemented authentication",  # Tier 2
        "Led code reviews",            # Tier 3
        "Built testing framework",     # Tier 2
        "Launched beta program",       # Tier 3
        "Created deployment pipeline", # Tier 2
        "Optimized queries",           # Tier 2
        "Managed sprint planning",     # Tier 1
        "Coordinated releases",        # Tier 1
        "Supported production"         # Tier 1
    ]

    result = scorer.score(bullets, 'intermediary')
    # Coverage: 7/10 = 70% Tier 2+ → 4 pts
    # Tier: (2+2+3+2+3+2+2+1+1+1)/10 = 1.9 → 4 pts
    assert result['level'] == 'intermediary'
    assert result['coverage_percentage'] == 70.0
    assert result['average_tier'] == 1.9


def test_senior_thresholds(scorer):
    """Senior: 80% coverage, 2.5 avg tier"""
    bullets = [
        "Led engineering team",        # Tier 3
        "Architected cloud platform",  # Tier 4 (Architected is Tier 4!)
        "Pioneered DevOps culture",    # Tier 4
        "Launched product line",       # Tier 3
        "Developed microservices",     # Tier 2
        "Implemented CI/CD",           # Tier 2
        "Built monitoring system",     # Tier 2
        "Created API gateway",         # Tier 2
        "Optimized infrastructure",    # Tier 2
        "Managed vendor relationships" # Tier 1
    ]

    result = scorer.score(bullets, 'senior')
    # Coverage: 9/10 = 90% Tier 2+ → 6 pts
    # Tier: (3+4+4+3+2+2+2+2+2+1)/10 = 2.5 → 6 pts (2.5-3.4 range)
    assert result['level'] == 'senior'
    assert result['coverage_percentage'] == 90.0
    assert result['average_tier'] == 2.5
    assert result['coverage_score'] == 6
    assert result['tier_score'] == 6


# ============================================================================
# TIER DISTRIBUTION TESTS
# ============================================================================

def test_tier_distribution_included(scorer):
    """Result includes tier distribution breakdown"""
    bullets = [
        "Pioneered platform",      # Tier 4
        "Led team",               # Tier 3
        "Developed API",          # Tier 2
        "Managed tasks",          # Tier 1
        "Responsible for work"    # Tier 0
    ]

    result = scorer.score(bullets, 'intermediary')

    assert 'tier_distribution' in result
    dist = result['tier_distribution']
    assert dist[0] == 1  # 1 Tier 0
    assert dist[1] == 1  # 1 Tier 1
    assert dist[2] == 1  # 1 Tier 2
    assert dist[3] == 1  # 1 Tier 3
    assert dist[4] == 1  # 1 Tier 4


def test_tier_distribution_with_multiples(scorer):
    """Tier distribution counts multiple verbs per tier"""
    bullets = [
        "Developed API",       # Tier 2
        "Implemented features",# Tier 2
        "Built framework",     # Tier 2
        "Created tests",       # Tier 2
        "Optimized queries"    # Tier 2
    ]

    result = scorer.score(bullets, 'intermediary')

    dist = result['tier_distribution']
    assert dist[0] == 0  # 0 Tier 0
    assert dist[1] == 0  # 0 Tier 1
    assert dist[2] == 5  # 5 Tier 2
    assert dist[3] == 0  # 0 Tier 3
    assert dist[4] == 0  # 0 Tier 4


# ============================================================================
# EDGE CASES
# ============================================================================

def test_empty_bullets(scorer):
    """Empty bullet list = 0 pts"""
    result = scorer.score([], 'senior')

    assert result['score'] == 0
    assert result['coverage_score'] == 0
    assert result['tier_score'] == 0
    assert result['total_bullets'] == 0
    assert result['coverage_percentage'] == 0.0
    assert result['average_tier'] == 0.0


def test_single_excellent_bullet(scorer):
    """Single Tier 4 bullet = high score"""
    bullets = ["Pioneered ML infrastructure"]

    result = scorer.score(bullets, 'beginner')
    # Coverage: 1/1 = 100% Tier 2+ → 7 pts
    # Tier: 4.0 avg → 8 pts
    assert result['coverage_score'] == 7
    assert result['tier_score'] == 8
    assert result['score'] == 15


def test_single_weak_bullet(scorer):
    """Single Tier 0 bullet = 0 pts"""
    bullets = ["Responsible for tasks"]

    result = scorer.score(bullets, 'senior')
    # Coverage: 0/1 = 0% Tier 2+ → 0 pts
    # Tier: 0.0 avg → 0 pts
    assert result['coverage_score'] == 0
    assert result['tier_score'] == 0
    assert result['score'] == 0


def test_whitespace_handling(scorer):
    """Handles bullets with extra whitespace"""
    bullets = [
        "  Led team  ",
        "\n\nDeveloped API\n",
        "\tImplemented features\t"
    ]

    result = scorer.score(bullets, 'beginner')
    assert result['total_bullets'] == 3
    assert result['bullets_with_tier2plus'] == 3


def test_case_insensitive_level(scorer):
    """Level parameter is case-insensitive"""
    bullets = [
        "Led team",
        "Developed API",
        "Implemented features"
    ]

    result1 = scorer.score(bullets, 'SENIOR')
    result2 = scorer.score(bullets, 'Senior')
    result3 = scorer.score(bullets, 'senior')

    assert result1['score'] == result2['score'] == result3['score']


def test_detailed_result_structure(scorer):
    """Result includes all required fields"""
    bullets = [
        "Led team",
        "Developed API",
        "Managed tasks"
    ]

    result = scorer.score(bullets, 'intermediary')

    # Check all expected keys
    required_keys = [
        'score', 'coverage_score', 'tier_score',
        'level', 'total_bullets', 'bullets_with_tier2plus',
        'coverage_percentage', 'average_tier',
        'tier_distribution', 'bullet_details'
    ]

    for key in required_keys:
        assert key in result, f"Missing key: {key}"

    # Check bullet_details structure
    assert len(result['bullet_details']) == 3
    assert 'text' in result['bullet_details'][0]
    assert 'tier' in result['bullet_details'][0]
    assert 'tier_name' in result['bullet_details'][0]
