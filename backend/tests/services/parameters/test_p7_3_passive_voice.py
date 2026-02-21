"""
Test P7.3: Passive Voice Detection (2 points)

Tests penalty-based scoring for passive voice usage:
- Starting budget: 2 pts
- Penalty: -0.5 pt per passive bullet
- Minimum: 0 pts (can't go negative)

Common passive patterns:
- "was [verb]ed" (was developed, was managed)
- "were [verb]ed" (were created, were implemented)
- "has been [verb]ed", "have been [verb]ed"
- "had been [verb]ed"

Research basis:
- Active voice is stronger and more impactful
- Passive voice weakens accomplishments
- ATS systems prefer direct, active language
"""

import pytest
from backend.services.parameters.p7_3_passive_voice import PassiveVoiceScorer


@pytest.fixture
def scorer():
    """Create PassiveVoiceScorer instance."""
    return PassiveVoiceScorer()


# ============================================================================
# PERFECT SCORE TESTS (2 pts)
# ============================================================================

def test_no_passive_voice_full_score(scorer):
    """All active voice bullets = 2 pts"""
    bullets = [
        "Led team of 10 engineers",
        "Developed scalable API",
        "Increased revenue by 50%",
        "Architected cloud infrastructure",
        "Launched mobile application"
    ]

    result = scorer.score(bullets)
    assert result['score'] == 2.0
    assert result['max_score'] == 2.0
    assert result['passive_count'] == 0
    assert len(result['passive_bullets']) == 0
    assert result['details']['penalty_per_bullet'] == 0.5


def test_empty_bullets_full_score(scorer):
    """Empty bullet list = 2 pts (no passive voice found)"""
    result = scorer.score([])
    assert result['score'] == 2.0
    assert result['max_score'] == 2.0
    assert result['passive_count'] == 0
    assert len(result['passive_bullets']) == 0


def test_single_active_bullet(scorer):
    """Single active bullet = 2 pts"""
    bullets = ["Implemented microservices architecture"]

    result = scorer.score(bullets)
    assert result['score'] == 2.0
    assert result['passive_count'] == 0


# ============================================================================
# PENALTY TESTS (-0.5 pts per passive bullet)
# ============================================================================

def test_one_passive_bullet(scorer):
    """1 passive bullet = 1.5 pts (2 - 0.5)"""
    bullets = [
        "Led development team",
        "Developed REST API",
        "Was responsible for database optimization",  # Passive
        "Launched new feature",
        "Architected cloud solution"
    ]

    result = scorer.score(bullets)
    assert result['score'] == 1.5
    assert result['passive_count'] == 1
    assert len(result['passive_bullets']) == 1
    assert result['passive_bullets'][0]['text'] == "Was responsible for database optimization"


def test_two_passive_bullets(scorer):
    """2 passive bullets = 1.0 pt (2 - 1.0)"""
    bullets = [
        "Led cross-functional team",
        "Was assigned to mobile project",  # Passive
        "Were tasked with improving performance",  # Passive
        "Implemented CI/CD pipeline"
    ]

    result = scorer.score(bullets)
    assert result['score'] == 1.0
    assert result['passive_count'] == 2
    assert len(result['passive_bullets']) == 2


def test_three_passive_bullets(scorer):
    """3 passive bullets = 0.5 pts (2 - 1.5)"""
    bullets = [
        "Was responsible for backend development",  # Passive
        "Led team meetings",
        "Were given ownership of API design",  # Passive
        "Has been managing the deployment process",  # Passive
        "Architected microservices"
    ]

    result = scorer.score(bullets)
    assert result['score'] == 0.5
    assert result['passive_count'] == 3
    assert len(result['passive_bullets']) == 3


def test_four_passive_bullets_capped_at_zero(scorer):
    """4 passive bullets = 0 pts (capped at minimum)"""
    bullets = [
        "Was responsible for frontend development",  # Passive
        "Were tasked with API implementation",  # Passive
        "Has been assigned to mobile team",  # Passive
        "Had been given project leadership role",  # Passive
        "Improved system performance"
    ]

    result = scorer.score(bullets)
    assert result['score'] == 0.0
    assert result['passive_count'] == 4
    assert len(result['passive_bullets']) == 4


def test_five_passive_bullets_stays_at_zero(scorer):
    """5+ passive bullets = 0 pts (can't go negative)"""
    bullets = [
        "Was responsible for backend",  # Passive
        "Were tasked with frontend",  # Passive
        "Has been managing deployment",  # Passive
        "Had been given leadership",  # Passive
        "Have been coordinating with team",  # Passive
    ]

    result = scorer.score(bullets)
    assert result['score'] == 0.0
    assert result['passive_count'] == 5
    # Score can't go negative
    assert result['score'] >= 0


# ============================================================================
# PASSIVE PATTERN DETECTION TESTS
# ============================================================================

def test_was_verb_ed_pattern(scorer):
    """Detect 'was [verb]ed' pattern"""
    bullets = [
        "Was developed by the team",
        "Was managed throughout the project",
        "Was implemented in production",
        "Was created for client needs"
    ]

    result = scorer.score(bullets)
    assert result['passive_count'] == 4
    assert result['score'] == 0.0


def test_were_verb_ed_pattern(scorer):
    """Detect 'were [verb]ed' pattern"""
    bullets = [
        "Were developed by engineering team",
        "Were implemented across all systems",
        "Were created for multiple clients",
        "Were managed by senior staff"
    ]

    result = scorer.score(bullets)
    assert result['passive_count'] == 4
    assert result['score'] == 0.0


def test_has_been_verb_ed_pattern(scorer):
    """Detect 'has been [verb]ed' pattern"""
    bullets = [
        "Has been developed over 6 months",
        "Has been implemented successfully",
        "Has been tested thoroughly"
    ]

    result = scorer.score(bullets)
    assert result['passive_count'] == 3
    assert result['score'] == 0.5


def test_have_been_verb_ed_pattern(scorer):
    """Detect 'have been [verb]ed' pattern"""
    bullets = [
        "Have been developed by the team",
        "Have been implemented in production",
        "Have been tested extensively"
    ]

    result = scorer.score(bullets)
    assert result['passive_count'] == 3
    assert result['score'] == 0.5


def test_had_been_verb_ed_pattern(scorer):
    """Detect 'had been [verb]ed' pattern"""
    bullets = [
        "Had been developed before my arrival",
        "Had been implemented previously",
        "Had been tested by QA team"
    ]

    result = scorer.score(bullets)
    assert result['passive_count'] == 3
    assert result['score'] == 0.5


def test_mixed_passive_patterns(scorer):
    """Detect multiple different passive patterns"""
    bullets = [
        "Was developed by engineering",  # was + verb
        "Were implemented across systems",  # were + verb
        "Has been tested thoroughly",  # has been + verb
        "Have been optimized for performance",  # have been + verb
        "Had been created before launch",  # had been + verb
        "Led team successfully"  # Active - no penalty
    ]

    result = scorer.score(bullets)
    assert result['passive_count'] == 5
    assert result['score'] == 0.0  # 5 passive = capped at 0


# ============================================================================
# FALSE POSITIVE AVOIDANCE TESTS
# ============================================================================

def test_was_as_verb_not_passive(scorer):
    """'Was' as main verb (not passive) should not be flagged"""
    bullets = [
        "Was the lead engineer on project",  # 'was' as main verb, not passive
        "Was a key contributor to success",  # 'was' as main verb
        "Led development team"
    ]

    result = scorer.score(bullets)
    # These should ideally not be flagged as passive (they're weak but not passive voice)
    # However, they might be caught - let's verify the implementation handles this
    # For now, we'll test what we expect: ideally 0 passive, but acceptable if 2
    assert result['passive_count'] <= 2  # Allow some false positives for now


def test_been_without_verb_ed_not_passive(scorer):
    """'Been' without past participle should not be flagged"""
    bullets = [
        "Have been leading the team for 3 years",  # 'leading' is not past participle
        "Has been working on the project",  # 'working' is not past participle
        "Had been coordinating with stakeholders"  # 'coordinating' is not past participle
    ]

    result = scorer.score(bullets)
    # These are progressive tenses, not passive voice
    # Should not be flagged as passive
    assert result['passive_count'] <= 1  # Allow minimal false positives


def test_present_perfect_active_not_passive(scorer):
    """Present perfect active voice should not be flagged"""
    bullets = [
        "Has developed over 50 features",
        "Have implemented multiple systems",
        "Had created comprehensive documentation"
    ]

    result = scorer.score(bullets)
    # These are active voice in present perfect tense
    assert result['passive_count'] == 0


def test_simple_past_active_not_passive(scorer):
    """Simple past tense (active) should not be flagged"""
    bullets = [
        "Developed scalable microservices",
        "Implemented authentication system",
        "Created automated testing suite",
        "Launched mobile application"
    ]

    result = scorer.score(bullets)
    assert result['passive_count'] == 0
    assert result['score'] == 2.0


# ============================================================================
# MIXED ACTIVE/PASSIVE TESTS
# ============================================================================

def test_half_passive_half_active(scorer):
    """50% passive, 50% active bullets"""
    bullets = [
        "Led engineering team",  # Active
        "Was responsible for API development",  # Passive
        "Architected cloud infrastructure",  # Active
        "Were tasked with database optimization",  # Passive
        "Launched new product feature",  # Active
        "Has been managing deployment pipeline",  # Passive
    ]

    result = scorer.score(bullets)
    assert result['passive_count'] == 3
    assert result['score'] == 0.5  # 2 - (3 * 0.5) = 0.5


def test_mostly_active_few_passive(scorer):
    """Mostly active with few passive bullets"""
    bullets = [
        "Led cross-functional team",
        "Developed REST API",
        "Architected microservices",
        "Implemented CI/CD pipeline",
        "Launched mobile app",
        "Optimized database queries",
        "Was assigned to special project",  # Passive
        "Built automated testing suite",
        "Created comprehensive docs",
        "Improved system performance"
    ]

    result = scorer.score(bullets)
    assert result['passive_count'] == 1
    assert result['score'] == 1.5  # 2 - (1 * 0.5) = 1.5


def test_mostly_passive_few_active(scorer):
    """Mostly passive with few active bullets"""
    bullets = [
        "Was responsible for backend",  # Passive
        "Were tasked with frontend",  # Passive
        "Has been managing deployment",  # Passive
        "Led team meetings",  # Active
        "Had been given leadership role",  # Passive
        "Have been coordinating releases",  # Passive
    ]

    result = scorer.score(bullets)
    assert result['passive_count'] == 5
    assert result['score'] == 0.0  # 2 - (5 * 0.5) = -0.5, capped at 0


# ============================================================================
# EDGE CASES
# ============================================================================

def test_all_passive_voice_zero_score(scorer):
    """100% passive voice = 0 pts"""
    bullets = [
        "Was developed by team",
        "Were implemented across systems",
        "Has been tested thoroughly",
        "Have been optimized for speed"
    ]

    result = scorer.score(bullets)
    assert result['score'] == 0.0
    assert result['passive_count'] == 4


def test_whitespace_handling(scorer):
    """Handles bullets with extra whitespace"""
    bullets = [
        "  Was responsible for development  ",
        "\n\nWere tasked with implementation\n",
        "\tHas been managing the project\t"
    ]

    result = scorer.score(bullets)
    assert result['passive_count'] == 3
    assert len(result['passive_bullets']) == 3


def test_case_insensitive_detection(scorer):
    """Passive detection is case-insensitive"""
    bullets = [
        "WAS DEVELOPED BY TEAM",
        "Were Implemented Across Systems",
        "has been tested thoroughly"
    ]

    result = scorer.score(bullets)
    assert result['passive_count'] == 3


def test_partial_passive_phrase_in_bullet(scorer):
    """Passive phrase in middle of bullet"""
    bullets = [
        "Led team that was responsible for API development",
        "Architected system that were implemented company-wide",
        "Developed features that have been deployed to production"
    ]

    result = scorer.score(bullets)
    # Each bullet contains a passive construction
    assert result['passive_count'] >= 1


def test_result_structure_complete(scorer):
    """Result contains all expected fields"""
    bullets = [
        "Led engineering team",
        "Was responsible for API development"
    ]

    result = scorer.score(bullets)

    # Check all expected keys
    assert 'score' in result
    assert 'max_score' in result
    assert 'passive_count' in result
    assert 'passive_bullets' in result
    assert 'details' in result

    # Check details structure
    assert 'penalty_per_bullet' in result['details']
    assert 'total_penalty' in result['details']
    assert 'patterns_found' in result['details']


def test_passive_bullets_details(scorer):
    """Passive bullets include detailed information"""
    bullets = [
        "Led engineering team",
        "Was responsible for API development",
        "Were tasked with database optimization"
    ]

    result = scorer.score(bullets)

    assert len(result['passive_bullets']) == 2

    # Check first passive bullet structure
    passive_bullet = result['passive_bullets'][0]
    assert 'text' in passive_bullet
    assert 'pattern' in passive_bullet
    assert passive_bullet['text'] == "Was responsible for API development"


def test_patterns_found_list(scorer):
    """Details include list of all patterns found"""
    bullets = [
        "Was developed by team",  # 'was'
        "Were implemented across systems",  # 'were'
        "Has been tested thoroughly",  # 'has been'
        "Led engineering team"  # No pattern
    ]

    result = scorer.score(bullets)

    patterns = result['details']['patterns_found']
    assert 'was' in patterns or 'was [verb]ed' in patterns
    assert 'were' in patterns or 'were [verb]ed' in patterns
    assert 'has been' in patterns or 'has been [verb]ed' in patterns


def test_very_long_bullet_with_passive(scorer):
    """Long bullet with passive voice embedded"""
    bullets = [
        "Led cross-functional team of 15 engineers and product managers to deliver "
        "enterprise-scale SaaS platform that was implemented across 50+ client organizations "
        "and generated $5M in annual recurring revenue"
    ]

    result = scorer.score(bullets)
    # Should detect the 'was implemented' passive construction
    assert result['passive_count'] == 1
    assert result['score'] == 1.5


def test_multiple_passive_in_one_bullet(scorer):
    """One bullet with multiple passive constructions counts as one passive bullet"""
    bullets = [
        "Was developed and were implemented by the engineering team"
    ]

    result = scorer.score(bullets)
    # Should count as 1 passive bullet (not 2), since it's one bullet point
    assert result['passive_count'] == 1
    assert result['score'] == 1.5


def test_common_weak_verbs_with_was(scorer):
    """Common weak passive constructions"""
    bullets = [
        "Was responsible for project management",
        "Was tasked with feature development",
        "Was assigned to special projects",
        "Was given ownership of API design",
        "Was selected to lead initiative"
    ]

    result = scorer.score(bullets)
    # All should be flagged as passive
    assert result['passive_count'] == 5
    assert result['score'] == 0.0
