"""
Tests for P2.2 - Quantification Rate & Quality Scorer (10 pts)

This parameter uses the QuantificationClassifier to evaluate:
1. Weighted quantification rate (HIGH=1.0, MEDIUM=0.7, LOW=0.3)
2. Level-aware thresholds (Beginner: 30%, Intermediary: 40%, Senior: 50%)
3. Tiered scoring system
4. Detailed quality breakdown

Test-Driven Development:
- Write failing test first
- Implement minimal code to pass
- Verify tests pass
- Commit
"""

import pytest
from backend.services.quantification_scorer import QuantificationScorer


@pytest.fixture
def scorer():
    """Create scorer instance for testing."""
    return QuantificationScorer()


# ============================================================================
# BEGINNER LEVEL TESTS (30% threshold)
# ============================================================================

def test_beginner_excellent_quantification(scorer):
    """Beginner: 50% weighted rate >= 30% threshold = 10 points"""
    bullets = [
        "Increased revenue by 45%",  # HIGH (1.0)
        "Reduced costs by $200K annually",  # HIGH (1.0)
        "Led team of 12 engineers",  # MEDIUM (0.7)
        "Completed project in 6 months",  # MEDIUM (0.7)
        "Worked on various projects",  # NONE (0)
        "Improved system performance"  # NONE (0)
    ]
    # Weighted: (1.0 + 1.0 + 0.7 + 0.7) / 6 = 3.4 / 6 = 56.7%

    result = scorer.score(bullets, 'beginner')

    assert result['score'] == 10
    assert result['weighted_quantification_rate'] >= 50.0
    assert result['high_count'] == 2
    assert result['medium_count'] == 2
    assert result['low_count'] == 0


def test_beginner_good_quantification(scorer):
    """Beginner: 25% weighted rate (between threshold-10% and threshold) = 6 points"""
    bullets = [
        "Led team of 5 engineers",  # MEDIUM (0.7)
        "Completed project in 3 months",  # MEDIUM (0.7)
        "Worked on backend development",  # NONE (0)
        "Improved system architecture",  # NONE (0)
        "Collaborated with stakeholders",  # NONE (0)
    ]
    # Weighted: (0.7 + 0.7) / 5 = 1.4 / 5 = 28%
    # Threshold is 30%, 28% is >= (30-10)=20% but < 30%, so 6 points

    result = scorer.score(bullets, 'beginner')

    assert result['score'] == 6
    assert 20.0 <= result['weighted_quantification_rate'] < 30.0


def test_beginner_acceptable_quantification(scorer):
    """Beginner: 15% weighted rate (between threshold-20% and threshold-10%) = 3 points"""
    bullets = [
        "Fixed 20 bugs",  # LOW (0.3)
        "Worked on 5 projects",  # LOW (0.3)
        "Responsible for backend",  # NONE (0)
        "Developed new features",  # NONE (0)
        "Improved performance",  # NONE (0)
    ]
    # Weighted: (0.3 + 0.3) / 5 = 0.6 / 5 = 12%
    # Threshold is 30%, 12% is >= (30-20)=10% but < (30-10)=20%, so 3 points

    result = scorer.score(bullets, 'beginner')

    assert result['score'] == 3
    assert 10.0 <= result['weighted_quantification_rate'] < 20.0


def test_beginner_poor_quantification(scorer):
    """Beginner: < 10% weighted rate (below threshold-20%) = 0 points"""
    bullets = [
        "Responsible for backend development",
        "Worked with team members",
        "Improved system architecture",
        "Developed various features",
        "Collaborated with stakeholders"
    ]
    # Weighted: 0 / 5 = 0%

    result = scorer.score(bullets, 'beginner')

    assert result['score'] == 0
    assert result['weighted_quantification_rate'] < 10.0
    assert result['quantified_count'] == 0


# ============================================================================
# INTERMEDIARY LEVEL TESTS (40% threshold)
# ============================================================================

def test_intermediary_excellent_quantification(scorer):
    """Intermediary: 60% weighted rate >= 40% threshold = 10 points"""
    bullets = [
        "Increased user engagement by 150%",  # HIGH (1.0)
        "Reduced API latency by 50%",  # HIGH (1.0)
        "Boosted revenue from $2M to $5M",  # HIGH (1.0)
        "Led team of 8 developers",  # MEDIUM (0.7)
        "Developed new features"  # NONE (0)
    ]
    # Weighted: (1.0 + 1.0 + 1.0 + 0.7) / 5 = 3.7 / 5 = 74%

    result = scorer.score(bullets, 'intermediary')

    assert result['score'] == 10
    assert result['weighted_quantification_rate'] >= 40.0
    assert result['high_count'] == 3


def test_intermediary_good_quantification(scorer):
    """Intermediary: 35% weighted rate (between threshold-10% and threshold) = 6 points"""
    bullets = [
        "Improved performance 2x faster",  # HIGH (1.0)
        "Managed 15 concurrent projects",  # MEDIUM (0.7)
        "Worked on backend services",  # NONE (0)
        "Developed REST APIs",  # NONE (0)
        "Collaborated with teams"  # NONE (0)
    ]
    # Weighted: (1.0 + 0.7) / 5 = 1.7 / 5 = 34%
    # Threshold is 40%, 34% is >= (40-10)=30% but < 40%, so 6 points

    result = scorer.score(bullets, 'intermediary')

    assert result['score'] == 6
    assert 30.0 <= result['weighted_quantification_rate'] < 40.0


def test_intermediary_acceptable_quantification(scorer):
    """Intermediary: 25% weighted rate (between threshold-20% and threshold-10%) = 3 points"""
    bullets = [
        "Led team of 6 engineers",  # MEDIUM (0.7)
        "Developed features",  # NONE (0)
        "Improved architecture",  # NONE (0)
        "Worked on microservices",  # NONE (0)
        "Collaborated with PM"  # NONE (0)
    ]
    # Weighted: (0.7) / 5 = 0.7 / 5 = 14%
    # Threshold is 40%, 14% is >= (40-20)=20% but < (40-10)=30%...
    # Wait, 14% < 20%, so this should be 0 points. Let me fix the test.

    result = scorer.score(bullets, 'intermediary')

    # Actually 14% < 20% (threshold-20%), so this is 0 points
    assert result['score'] == 0
    assert result['weighted_quantification_rate'] < 20.0


def test_intermediary_acceptable_quantification_corrected(scorer):
    """Intermediary: 25% weighted rate (between threshold-20% and threshold-10%) = 3 points"""
    bullets = [
        "Led team of 8 engineers",  # MEDIUM (0.7)
        "Completed in 4 months",  # MEDIUM (0.7)
        "Developed features",  # NONE (0)
        "Improved architecture",  # NONE (0)
        "Worked on microservices"  # NONE (0)
    ]
    # Weighted: (0.7 + 0.7) / 5 = 1.4 / 5 = 28%
    # Threshold is 40%, 28% is >= (40-20)=20% but < (40-10)=30%, so 3 points

    result = scorer.score(bullets, 'intermediary')

    assert result['score'] == 3
    assert 20.0 <= result['weighted_quantification_rate'] < 30.0


# ============================================================================
# SENIOR LEVEL TESTS (50% threshold)
# ============================================================================

def test_senior_excellent_quantification(scorer):
    """Senior: 80% weighted rate >= 50% threshold = 10 points"""
    bullets = [
        "Scaled system to handle 10M+ users (3x growth)",  # HIGH (1.0)
        "Reduced infrastructure costs by $500K (40%)",  # HIGH (1.0)
        "Increased team productivity by 60%",  # HIGH (1.0)
        "Led cross-functional team of 20",  # MEDIUM (0.7)
        "Architected microservices"  # NONE (0)
    ]
    # Weighted: (1.0 + 1.0 + 1.0 + 0.7) / 5 = 3.7 / 5 = 74%

    result = scorer.score(bullets, 'senior')

    assert result['score'] == 10
    assert result['weighted_quantification_rate'] >= 50.0
    assert result['high_count'] == 3
    assert result['medium_count'] == 1


def test_senior_good_quantification(scorer):
    """Senior: 45% weighted rate (between threshold-10% and threshold) = 6 points"""
    bullets = [
        "Improved system performance 2x",  # HIGH (1.0)
        "Led team of 12 engineers",  # MEDIUM (0.7)
        "Architected new platform",  # NONE (0)
        "Mentored junior developers",  # NONE (0)
        "Drove technical strategy"  # NONE (0)
    ]
    # Weighted: (1.0 + 0.7) / 5 = 1.7 / 5 = 34%
    # Threshold is 50%, 34% is < (50-10)=40%, so this should be 3 points, not 6.
    # Let me recalculate.

    result = scorer.score(bullets, 'senior')

    # 34% is >= (50-20)=30% but < (50-10)=40%, so 3 points
    assert result['score'] == 3
    assert 30.0 <= result['weighted_quantification_rate'] < 40.0


def test_senior_good_quantification_corrected(scorer):
    """Senior: 45% weighted rate (between threshold-10% and threshold) = 6 points"""
    bullets = [
        "Increased revenue by 45%",  # HIGH (1.0)
        "Reduced latency by 70%",  # HIGH (1.0)
        "Led team of 15",  # MEDIUM (0.7)
        "Architected platform",  # NONE (0)
        "Mentored developers"  # NONE (0)
    ]
    # Weighted: (1.0 + 1.0 + 0.7) / 5 = 2.7 / 5 = 54%
    # Threshold is 50%, 54% >= 50%, so 10 points, not 6.
    # For 6 points, need 40% <= rate < 50%

    result = scorer.score(bullets, 'senior')

    assert result['score'] == 10  # Actually perfect score
    assert result['weighted_quantification_rate'] >= 50.0


def test_senior_needs_six_points(scorer):
    """Senior: Need exactly 6 points (40-50% range)"""
    bullets = [
        "Improved performance 2x",  # HIGH (1.0)
        "Serving 500K+ users",  # MEDIUM (0.7)
        "Led development",  # NONE (0)
        "Architected solution",  # NONE (0)
        "Mentored team"  # NONE (0)
    ]
    # Weighted: (1.0 + 0.7) / 5 = 1.7 / 5 = 34%
    # 34% < 40%, so this is 3 points
    # Need more metrics for 6 points

    result = scorer.score(bullets, 'senior')

    assert result['score'] == 3


def test_senior_six_points_correct(scorer):
    """Senior: Exactly 6 points (40-50% range)"""
    bullets = [
        "Increased efficiency by 35%",  # HIGH (1.0)
        "Led team of 10",  # MEDIUM (0.7)
        "Serving 200K users",  # MEDIUM (0.7)
        "Architected platform",  # NONE (0)
        "Mentored developers"  # NONE (0)
    ]
    # Weighted: (1.0 + 0.7 + 0.7) / 5 = 2.4 / 5 = 48%
    # Threshold is 50%, 48% is >= (50-10)=40% but < 50%, so 6 points

    result = scorer.score(bullets, 'senior')

    assert result['score'] == 6
    assert 40.0 <= result['weighted_quantification_rate'] < 50.0


# ============================================================================
# EDGE CASES
# ============================================================================

def test_empty_bullets(scorer):
    """Empty bullet list should return 0 points"""
    result = scorer.score([], 'intermediary')

    assert result['score'] == 0
    assert result['weighted_quantification_rate'] == 0.0
    assert result['quantified_count'] == 0
    assert result['high_count'] == 0
    assert result['medium_count'] == 0
    assert result['low_count'] == 0


def test_single_bullet_high_quality(scorer):
    """Single high-quality bullet should score appropriately"""
    bullets = ["Increased revenue by 150%"]

    result = scorer.score(bullets, 'beginner')

    # Weighted: 1.0 / 1 = 100% (way above 30% threshold)
    assert result['score'] == 10
    assert result['weighted_quantification_rate'] == 100.0
    assert result['high_count'] == 1


def test_invalid_level_defaults_to_intermediary(scorer):
    """Invalid experience level should default to intermediary"""
    bullets = [
        "Increased performance by 50%",
        "Led team of 8"
    ]

    result = scorer.score(bullets, 'invalid_level')

    # Should use intermediary threshold (40%)
    # Weighted: (1.0 + 0.7) / 2 = 85%
    assert result['score'] == 10  # Above 40% threshold


def test_detailed_breakdown_returned(scorer):
    """Scorer should return detailed quality breakdown"""
    bullets = [
        "Increased revenue by 45%",  # HIGH
        "Reduced costs by $100K",  # HIGH
        "Led team of 10",  # MEDIUM
        "Serving 50K users",  # MEDIUM
        "Fixed 15 bugs",  # LOW
        "Worked on features"  # NONE
    ]

    result = scorer.score(bullets, 'intermediary')

    # Verify all expected fields are present
    assert 'score' in result
    assert 'weighted_quantification_rate' in result
    assert 'quantified_count' in result
    assert 'total_bullets' in result
    assert 'high_count' in result
    assert 'medium_count' in result
    assert 'low_count' in result
    assert 'level' in result
    assert 'threshold' in result
    assert 'explanation' in result

    # Verify counts
    assert result['total_bullets'] == 6
    assert result['quantified_count'] == 5
    assert result['high_count'] == 2
    assert result['medium_count'] == 2
    assert result['low_count'] == 1


def test_all_low_quality_metrics(scorer):
    """All low-quality metrics should still award some points if above threshold"""
    bullets = [
        "Fixed 20 bugs",  # LOW
        "Attended 15 meetings",  # LOW
        "Worked on 8 projects",  # LOW
        "Completed 12 tasks"  # MEDIUM (matches 'project_count' pattern)
    ]
    # Weighted: (0.3 + 0.3 + 0.3 + 0.7) / 4 = 1.6 / 4 = 40%

    result = scorer.score(bullets, 'intermediary')

    # 40% = exactly at intermediary threshold = 10 points
    assert result['score'] == 10
    assert result['weighted_quantification_rate'] == 40.0
    assert result['low_count'] == 3
    assert result['medium_count'] == 1


def test_mixed_quality_distribution(scorer):
    """Test with various quality levels"""
    bullets = [
        "Increased revenue by 200%",  # HIGH
        "Cut costs by $1M",  # HIGH
        "Led team of 15",  # MEDIUM
        "Completed in 8 months",  # MEDIUM
        "Fixed 50 bugs",  # LOW
        "Attended 20 meetings",  # LOW
        "Developed features",  # NONE
        "Improved architecture"  # NONE
    ]
    # Weighted: (1.0 + 1.0 + 0.7 + 0.7 + 0.3 + 0.3) / 8 = 4.0 / 8 = 50%

    result = scorer.score(bullets, 'senior')

    # Exactly at 50% threshold for senior = 10 points
    assert result['score'] == 10
    assert result['weighted_quantification_rate'] == 50.0
    assert result['high_count'] == 2
    assert result['medium_count'] == 2
    assert result['low_count'] == 2
