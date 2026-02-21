import pytest
from backend.services.vague_phrase_detector import VaguePhraseDetector

@pytest.fixture
def detector():
    return VaguePhraseDetector()

def test_no_vague_phrases(detector):
    """Resume with no vague phrases should score 5 points"""
    resume_text = """
    Led team of 10 engineers to deliver microservices architecture.
    Architected scalable API serving 100K+ requests/day.
    Increased system performance by 45% through optimization.
    """

    result = detector.detect(resume_text)

    assert result['vague_phrase_count'] == 0
    assert result['score'] == 5
    assert len(result['found_phrases']) == 0

def test_one_vague_phrase(detector):
    """1 vague phrase should score 4 points"""
    resume_text = """
    Responsible for backend development using Python and Django.
    Led team of 5 engineers to deliver new features.
    """

    result = detector.detect(resume_text)

    assert result['vague_phrase_count'] == 1
    assert result['score'] == 4
    assert 'responsible for' in result['found_phrases']

def test_multiple_vague_phrases(detector):
    """3-4 vague phrases should score 2 points"""
    resume_text = """
    Responsible for backend development.
    Worked on API integrations.
    Helped with database optimization.
    Involved in code reviews.
    """

    result = detector.detect(resume_text)

    assert result['vague_phrase_count'] == 4
    assert result['score'] == 2
    assert len(result['found_phrases']) == 4

def test_many_vague_phrases(detector):
    """5+ vague phrases should score 0 points"""
    resume_text = """
    Responsible for development.
    Worked on features.
    Helped with testing.
    Involved in deployments.
    Participated in planning.
    Contributed to documentation.
    """

    result = detector.detect(resume_text)

    assert result['vague_phrase_count'] >= 5
    assert result['score'] == 0

def test_case_insensitive_detection(detector):
    """Detection should be case-insensitive"""
    resume_text = """
    RESPONSIBLE FOR development.
    Worked On features.
    """

    result = detector.detect(resume_text)

    assert result['vague_phrase_count'] == 2
    assert result['score'] == 4

def test_duplicate_phrase_detection(detector):
    """Same vague phrase used multiple times counts multiple times"""
    resume_text = """
    Responsible for backend.
    Responsible for frontend.
    Responsible for testing.
    """

    result = detector.detect(resume_text)

    assert result['vague_phrase_count'] == 3
    assert result['score'] == 2

def test_result_structure(detector):
    """Verify result dictionary structure"""
    resume_text = "Worked on Python projects"

    result = detector.detect(resume_text)

    assert 'vague_phrase_count' in result
    assert 'score' in result
    assert 'found_phrases' in result
    assert 'penalty_breakdown' in result
    assert isinstance(result['found_phrases'], list)
    assert isinstance(result['score'], int)
    assert 0 <= result['score'] <= 5
