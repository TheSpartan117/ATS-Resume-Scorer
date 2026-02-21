import pytest
from backend.services.repetition_detector import RepetitionDetector

@pytest.fixture
def detector():
    return RepetitionDetector()

def test_no_repetition(detector):
    """No repeated verbs = no penalty"""
    bullets = [
        "Developed REST API",
        "Implemented caching",
        "Designed database schema",
        "Architected microservices"
    ]

    result = detector.detect(bullets)

    assert result['penalty_score'] == 0
    assert result['repeated_words'] == []

def test_single_repetition_under_threshold(detector):
    """Verb used 2 times (under threshold) = no penalty"""
    bullets = [
        "Led team of 5 engineers",
        "Led API integration project"
    ]

    result = detector.detect(bullets)

    assert result['penalty_score'] == 0

def test_single_verb_repeated_3_times(detector):
    """Verb used exactly 3 times (threshold) = -1 pt"""
    bullets = [
        "Led backend team",
        "Led API migration",
        "Led code reviews"
    ]

    result = detector.detect(bullets)

    assert result['penalty_score'] == -1
    assert len(result['repeated_words']) == 1
    assert result['repeated_words'][0]['word'] == 'led'
    assert result['repeated_words'][0]['count'] == 3

def test_verb_repeated_5_times(detector):
    """Verb used 5 times = -1 pt (same as 3)"""
    bullets = [
        "Managed project A",
        "Managed project B",
        "Managed project C",
        "Managed project D",
        "Managed project E"
    ]

    result = detector.detect(bullets)

    assert result['penalty_score'] == -1
    assert result['repeated_words'][0]['count'] == 5

def test_multiple_verbs_repeated(detector):
    """Multiple verbs repeated = cumulative penalty (capped at -3)"""
    bullets = [
        "Developed feature A",
        "Developed feature B",
        "Developed feature C",
        "Managed team A",
        "Managed team B",
        "Managed team C",
        "Built system A",
        "Built system B",
        "Built system C"
    ]

    result = detector.detect(bullets)

    # 3 verbs repeated 3+ times = -3 pts (penalty cap)
    assert result['penalty_score'] == -3
    assert len(result['repeated_words']) == 3

def test_penalty_cap_at_3_points(detector):
    """Penalty should not exceed -3 points"""
    bullets = [
        "Led A", "Led B", "Led C",
        "Managed D", "Managed E", "Managed F",
        "Developed G", "Developed H", "Developed I",
        "Built J", "Built K", "Built L",
        "Created M", "Created N", "Created O"
    ]

    result = detector.detect(bullets)

    # 5 verbs repeated, but cap at -3
    assert result['penalty_score'] == -3
    assert len(result['repeated_words']) >= 3

def test_case_insensitive_detection(detector):
    """Should detect repetition regardless of case"""
    bullets = [
        "Led team A",
        "led team B",
        "LED team C"
    ]

    result = detector.detect(bullets)

    assert result['penalty_score'] == -1
    assert result['repeated_words'][0]['count'] == 3

def test_ignores_common_words(detector):
    """Should ignore common words like 'the', 'and', 'to'"""
    bullets = [
        "Led the team to success",
        "Managed the project to completion",
        "Developed the API to production"
    ]

    result = detector.detect(bullets)

    # 'the' and 'to' used 3 times each, but ignored
    assert result['penalty_score'] == 0

def test_only_counts_first_word_of_bullet(detector):
    """Should only check action verbs (first word) for repetition"""
    bullets = [
        "Developed system using Python",
        "Implemented feature using Python",
        "Created tool using Python"
    ]

    result = detector.detect(bullets)

    # 'Python' appears 3 times but not as action verb
    # 'developed', 'implemented', 'created' each appear once
    assert result['penalty_score'] == 0

def test_analyze_with_full_details(detector):
    """analyze() should return comprehensive results"""
    bullets = [
        "Led team A",
        "Led team B",
        "Led team C",
        "Developed feature X"
    ]

    analysis = detector.analyze(bullets)

    assert analysis['total_bullets'] == 4
    assert analysis['penalty_score'] == -1
    assert analysis['max_penalty'] == -3
    assert 'repeated_words' in analysis
    assert len(analysis['repeated_words']) == 1
