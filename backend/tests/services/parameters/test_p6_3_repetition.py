"""
Test P6.3: Word Repetition Penalty (-5 points max)

Tests penalty scoring based on:
- Verb used 3+ times: -1 pt per verb
- Maximum penalty: -5 pts
- Case insensitive matching
- Focus on action verbs at bullet starts

Penalty structure:
- 0-2 uses of same verb: 0 penalty
- 3+ uses: -1 pt per verb
- Cap: -5 pts maximum
"""

import pytest
from backend.services.parameters.p6_3_repetition import RepetitionPenaltyScorer


@pytest.fixture
def scorer():
    """Create RepetitionPenaltyScorer instance."""
    return RepetitionPenaltyScorer()


# ============================================================================
# NO REPETITION TESTS
# ============================================================================

def test_no_repetition_zero_penalty(scorer):
    """No verb repetition = 0 penalty"""
    bullets = [
        "Led team of 10 engineers",
        "Developed scalable API",
        "Implemented CI/CD pipeline",
        "Architected cloud infrastructure",
        "Launched mobile application"
    ]

    result = scorer.score(bullets)
    assert result['penalty'] == 0
    assert result['repeated_verbs'] == []
    assert len(result['repetition_details']) == 0


def test_empty_bullets_zero_penalty(scorer):
    """Empty bullet list = 0 penalty"""
    result = scorer.score([])
    assert result['penalty'] == 0
    assert result['repeated_verbs'] == []
    assert len(result['repetition_details']) == 0


def test_single_bullet_zero_penalty(scorer):
    """Single bullet = 0 penalty"""
    bullets = ["Led team of engineers"]

    result = scorer.score(bullets)
    assert result['penalty'] == 0
    assert result['repeated_verbs'] == []


# ============================================================================
# BELOW THRESHOLD TESTS (2 uses = no penalty)
# ============================================================================

def test_verb_used_twice_no_penalty(scorer):
    """Verb used 2 times (below threshold) = 0 penalty"""
    bullets = [
        "Developed feature A using Python",
        "Developed feature B using Java",
        "Implemented feature C using Go"
    ]
    # "developed" used 2 times = no penalty

    result = scorer.score(bullets)
    assert result['penalty'] == 0
    assert result['repeated_verbs'] == []


def test_multiple_verbs_used_twice_no_penalty(scorer):
    """Multiple verbs each used 2 times = 0 penalty"""
    bullets = [
        "Developed feature A",
        "Developed feature B",
        "Implemented feature C",
        "Implemented feature D",
        "Built feature E",
        "Built feature F"
    ]
    # All verbs used exactly 2 times = no penalty

    result = scorer.score(bullets)
    assert result['penalty'] == 0
    assert result['repeated_verbs'] == []


# ============================================================================
# THRESHOLD TESTS (3 uses = -1 pt)
# ============================================================================

def test_verb_used_three_times_one_point_penalty(scorer):
    """Verb used exactly 3 times = -1 pt penalty"""
    bullets = [
        "Developed feature A",
        "Developed feature B",
        "Developed feature C",
        "Implemented feature D"
    ]
    # "developed" used 3 times = -1 pt

    result = scorer.score(bullets)
    assert result['penalty'] == -1
    assert len(result['repeated_verbs']) == 1
    assert result['repeated_verbs'][0] == 'developed'
    assert len(result['repetition_details']) == 1
    assert result['repetition_details'][0]['word'] == 'developed'
    assert result['repetition_details'][0]['count'] == 3
    assert result['repetition_details'][0]['penalty'] == -1


def test_verb_used_four_times_one_point_penalty(scorer):
    """Verb used 4 times = -1 pt penalty (not -2)"""
    bullets = [
        "Developed feature A",
        "Developed feature B",
        "Developed feature C",
        "Developed feature D",
        "Implemented feature E"
    ]
    # "developed" used 4 times = still -1 pt

    result = scorer.score(bullets)
    assert result['penalty'] == -1
    assert len(result['repeated_verbs']) == 1
    assert result['repetition_details'][0]['count'] == 4
    assert result['repetition_details'][0]['penalty'] == -1


# ============================================================================
# MULTIPLE REPETITION TESTS
# ============================================================================

def test_three_different_verbs_repeated_three_points_penalty(scorer):
    """3 different verbs each used 3+ times = -3 pts"""
    bullets = [
        "Developed feature A",
        "Developed feature B",
        "Developed feature C",
        "Implemented feature D",
        "Implemented feature E",
        "Implemented feature F",
        "Built feature G",
        "Built feature H",
        "Built feature I"
    ]
    # "developed" used 3 times = -1
    # "implemented" used 3 times = -1
    # "built" used 3 times = -1
    # Total = -3

    result = scorer.score(bullets)
    assert result['penalty'] == -3
    assert len(result['repeated_verbs']) == 3
    assert set(result['repeated_verbs']) == {'developed', 'implemented', 'built'}
    assert len(result['repetition_details']) == 3


def test_two_verbs_repeated_one_not_two_points_penalty(scorer):
    """2 verbs repeated, 1 below threshold = -2 pts"""
    bullets = [
        "Developed feature A",
        "Developed feature B",
        "Developed feature C",
        "Implemented feature D",
        "Implemented feature E",
        "Implemented feature F",
        "Built feature G",
        "Built feature H"
    ]
    # "developed" used 3 times = -1
    # "implemented" used 3 times = -1
    # "built" used 2 times = 0
    # Total = -2

    result = scorer.score(bullets)
    assert result['penalty'] == -2
    assert len(result['repeated_verbs']) == 2
    assert set(result['repeated_verbs']) == {'developed', 'implemented'}


# ============================================================================
# CAP TESTS (max -5 pts)
# ============================================================================

def test_six_repeated_verbs_capped_at_five_points(scorer):
    """6 repeated verbs capped at -5 pts maximum"""
    bullets = [
        # Verb 1: developed (3x)
        "Developed feature A",
        "Developed feature B",
        "Developed feature C",
        # Verb 2: implemented (3x)
        "Implemented feature D",
        "Implemented feature E",
        "Implemented feature F",
        # Verb 3: built (3x)
        "Built feature G",
        "Built feature H",
        "Built feature I",
        # Verb 4: created (3x)
        "Created feature J",
        "Created feature K",
        "Created feature L",
        # Verb 5: designed (3x)
        "Designed feature M",
        "Designed feature N",
        "Designed feature O",
        # Verb 6: managed (3x)
        "Managed feature P",
        "Managed feature Q",
        "Managed feature R"
    ]
    # 6 verbs repeated = -6 pts normally
    # But capped at -5 pts

    result = scorer.score(bullets)
    assert result['penalty'] == -5
    assert len(result['repeated_verbs']) == 6
    assert len(result['repetition_details']) == 6


def test_ten_repeated_verbs_still_capped_at_five_points(scorer):
    """10 repeated verbs still capped at -5 pts maximum"""
    bullets = []
    verbs = ['developed', 'implemented', 'built', 'created', 'designed',
             'managed', 'established', 'coordinated', 'organized', 'facilitated']

    # Each verb used 3 times
    for verb in verbs:
        for i in range(3):
            bullets.append(f"{verb.capitalize()} feature {i}")

    # 10 verbs repeated = -10 pts normally
    # But capped at -5 pts

    result = scorer.score(bullets)
    assert result['penalty'] == -5
    assert len(result['repeated_verbs']) == 10
    assert len(result['repetition_details']) == 10


def test_exactly_five_repeated_verbs_five_points_penalty(scorer):
    """Exactly 5 repeated verbs = -5 pts (at cap, not over)"""
    bullets = [
        # Verb 1: developed (3x)
        "Developed feature A",
        "Developed feature B",
        "Developed feature C",
        # Verb 2: implemented (3x)
        "Implemented feature D",
        "Implemented feature E",
        "Implemented feature F",
        # Verb 3: built (3x)
        "Built feature G",
        "Built feature H",
        "Built feature I",
        # Verb 4: created (3x)
        "Created feature J",
        "Created feature K",
        "Created feature L",
        # Verb 5: designed (3x)
        "Designed feature M",
        "Designed feature N",
        "Designed feature O"
    ]
    # Exactly 5 verbs repeated = -5 pts

    result = scorer.score(bullets)
    assert result['penalty'] == -5
    assert len(result['repeated_verbs']) == 5


# ============================================================================
# CASE INSENSITIVITY TESTS
# ============================================================================

def test_case_insensitive_matching(scorer):
    """Verbs matched case-insensitively"""
    bullets = [
        "Developed feature A",
        "DEVELOPED feature B",
        "developed feature C",
        "DevelopeD feature D"
    ]
    # All should be counted as "developed" (4 times) = -1 pt

    result = scorer.score(bullets)
    assert result['penalty'] == -1
    assert len(result['repeated_verbs']) == 1
    assert result['repeated_verbs'][0] == 'developed'
    assert result['repetition_details'][0]['count'] == 4


def test_mixed_case_multiple_verbs(scorer):
    """Multiple verbs with mixed cases"""
    bullets = [
        "Developed feature A",
        "DEVELOPED feature B",
        "developed feature C",
        "Implemented feature D",
        "IMPLEMENTED feature E",
        "implemented feature F"
    ]
    # "developed" (3x) and "implemented" (3x) = -2 pts

    result = scorer.score(bullets)
    assert result['penalty'] == -2
    assert len(result['repeated_verbs']) == 2
    assert set(result['repeated_verbs']) == {'developed', 'implemented'}


# ============================================================================
# EDGE CASES
# ============================================================================

def test_bullets_with_leading_markers(scorer):
    """Handles bullets with leading markers (•, -, *)"""
    bullets = [
        "• Developed feature A",
        "- Developed feature B",
        "* Developed feature C",
        "  - Implemented feature D"
    ]
    # "developed" used 3 times = -1 pt

    result = scorer.score(bullets)
    assert result['penalty'] == -1
    assert result['repeated_verbs'][0] == 'developed'


def test_bullets_with_extra_whitespace(scorer):
    """Handles bullets with extra whitespace"""
    bullets = [
        "   Developed feature A   ",
        "Developed feature B",
        "  Developed feature C  "
    ]
    # "developed" used 3 times = -1 pt

    result = scorer.score(bullets)
    assert result['penalty'] == -1


def test_bullets_with_no_recognizable_verbs(scorer):
    """Bullets with no recognizable verbs = 0 penalty"""
    bullets = [
        "Just some random text here",
        "Another random sentence",
        "No action verbs at all"
    ]

    result = scorer.score(bullets)
    assert result['penalty'] == 0
    assert result['repeated_verbs'] == []


def test_ignore_common_words(scorer):
    """Common words (the, a, and, etc.) are ignored"""
    bullets = [
        "The team developed feature A",
        "The team implemented feature B",
        "The team built feature C"
    ]
    # "the" should be ignored, actual verbs extracted
    # No repetition = 0 penalty

    result = scorer.score(bullets)
    assert result['penalty'] == 0


def test_verb_with_different_tenses_counted_separately(scorer):
    """Different verb forms counted separately (develop vs developed)"""
    bullets = [
        "Develop feature A",
        "Develop feature B",
        "Develop feature C",
        "Developed feature D",
        "Developed feature E",
        "Developing feature F"
    ]
    # "develop" used 3 times = -1
    # "developed" used 2 times = 0
    # "developing" used 1 time = 0
    # Total = -1

    result = scorer.score(bullets)
    assert result['penalty'] == -1
    assert len(result['repeated_verbs']) == 1
    assert result['repeated_verbs'][0] == 'develop'


# ============================================================================
# RESULT STRUCTURE TESTS
# ============================================================================

def test_result_structure_complete(scorer):
    """Result contains all required fields"""
    bullets = [
        "Developed feature A",
        "Developed feature B",
        "Developed feature C"
    ]

    result = scorer.score(bullets)

    # Check all required keys exist
    assert 'penalty' in result
    assert 'repeated_verbs' in result
    assert 'repetition_details' in result

    # Check types
    assert isinstance(result['penalty'], int)
    assert isinstance(result['repeated_verbs'], list)
    assert isinstance(result['repetition_details'], list)

    # Check penalty is negative or zero
    assert result['penalty'] <= 0


def test_repetition_details_structure(scorer):
    """repetition_details has correct structure"""
    bullets = [
        "Developed feature A",
        "Developed feature B",
        "Developed feature C",
        "Implemented feature D",
        "Implemented feature E",
        "Implemented feature F"
    ]

    result = scorer.score(bullets)

    assert len(result['repetition_details']) == 2

    for detail in result['repetition_details']:
        assert 'word' in detail
        assert 'count' in detail
        assert 'penalty' in detail
        assert isinstance(detail['word'], str)
        assert isinstance(detail['count'], int)
        assert isinstance(detail['penalty'], int)
        assert detail['count'] >= 3
        assert detail['penalty'] == -1


def test_repetition_details_sorted_by_count(scorer):
    """repetition_details sorted by count (most repeated first)"""
    bullets = [
        # "developed" used 5 times
        "Developed feature A",
        "Developed feature B",
        "Developed feature C",
        "Developed feature D",
        "Developed feature E",
        # "implemented" used 3 times
        "Implemented feature F",
        "Implemented feature G",
        "Implemented feature H",
        # "built" used 4 times
        "Built feature I",
        "Built feature J",
        "Built feature K",
        "Built feature L"
    ]

    result = scorer.score(bullets)

    # Should be sorted: developed (5), built (4), implemented (3)
    assert result['repetition_details'][0]['word'] == 'developed'
    assert result['repetition_details'][0]['count'] == 5
    assert result['repetition_details'][1]['word'] == 'built'
    assert result['repetition_details'][1]['count'] == 4
    assert result['repetition_details'][2]['word'] == 'implemented'
    assert result['repetition_details'][2]['count'] == 3


# ============================================================================
# INTEGRATION WITH REPETITION DETECTOR
# ============================================================================

def test_uses_repetition_detector_with_correct_thresholds(scorer):
    """Scorer uses RepetitionDetector with threshold=3, max_penalty=5"""
    bullets = [
        "Developed feature A",
        "Developed feature B",
        "Developed feature C"
    ]

    result = scorer.score(bullets)

    # Verify it respects threshold of 3
    assert result['penalty'] == -1

    # Test that it caps at 5
    bullets_many = []
    for i in range(8):  # 8 different verbs
        verb = f"verb{i}"
        for j in range(3):
            bullets_many.append(f"{verb.capitalize()} feature {j}")

    result_many = scorer.score(bullets_many)
    assert result_many['penalty'] == -5  # Capped at -5


def test_real_world_resume_scenario(scorer):
    """Real-world resume with mixed repetition"""
    bullets = [
        "Led cross-functional team of 12 engineers",
        "Developed microservices architecture",
        "Developed REST API endpoints",
        "Developed frontend components",
        "Implemented CI/CD pipeline",
        "Implemented automated testing",
        "Architected cloud infrastructure",
        "Managed project timeline and deliverables",
        "Coordinated with stakeholders",
        "Optimized database performance"
    ]
    # "developed" used 3 times = -1
    # "implemented" used 2 times = 0
    # Total = -1

    result = scorer.score(bullets)
    assert result['penalty'] == -1
    assert len(result['repeated_verbs']) == 1
    assert result['repeated_verbs'][0] == 'developed'
