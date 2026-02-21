import pytest
from backend.services.job_hopping_detector import JobHoppingDetector

@pytest.fixture
def detector():
    return JobHoppingDetector()

def test_no_job_hopping_all_long_stints(detector):
    """All positions >1 year = no penalty"""
    employment = [
        {'title': 'Software Engineer', 'start_date': '2018-01', 'end_date': '2020-06'},  # 2.5 years
        {'title': 'Senior Engineer', 'start_date': '2020-06', 'end_date': '2023-12'}     # 3.5 years
    ]

    result = detector.detect(employment)

    assert result['short_stints_count'] == 0
    assert result['penalty_score'] == 0
    assert len(result['short_stints']) == 0

def test_one_short_stint(detector):
    """One position <1 year = -1 pt penalty"""
    employment = [
        {'title': 'Engineer I', 'start_date': '2020-01', 'end_date': '2020-09'},  # 8 months
        {'title': 'Engineer II', 'start_date': '2020-09', 'end_date': '2024-12'}  # 4+ years
    ]

    result = detector.detect(employment)

    assert result['short_stints_count'] == 1
    assert result['penalty_score'] == -1
    assert len(result['short_stints']) == 1

def test_multiple_short_stints(detector):
    """3 short stints = -3 pt penalty"""
    employment = [
        {'title': 'Engineer A', 'start_date': '2020-01', 'end_date': '2020-08'},  # 7 months
        {'title': 'Engineer B', 'start_date': '2020-09', 'end_date': '2021-04'},  # 7 months
        {'title': 'Engineer C', 'start_date': '2021-05', 'end_date': '2021-12'},  # 7 months
        {'title': 'Engineer D', 'start_date': '2022-01', 'end_date': '2024-12'}   # 3 years
    ]

    result = detector.detect(employment)

    assert result['short_stints_count'] == 3
    assert result['penalty_score'] == -3

def test_penalty_cap_at_3_points(detector):
    """More than 3 short stints should still cap at -3 pts"""
    employment = [
        {'title': 'Job 1', 'start_date': '2018-01', 'end_date': '2018-06'},  # 5 months
        {'title': 'Job 2', 'start_date': '2018-07', 'end_date': '2019-01'},  # 6 months
        {'title': 'Job 3', 'start_date': '2019-02', 'end_date': '2019-08'},  # 6 months
        {'title': 'Job 4', 'start_date': '2019-09', 'end_date': '2020-03'},  # 6 months
        {'title': 'Job 5', 'start_date': '2020-04', 'end_date': '2024-12'}   # 4+ years
    ]

    result = detector.detect(employment)

    # 4 short stints, but penalty capped at -3
    assert result['short_stints_count'] == 4
    assert result['penalty_score'] == -3

def test_contract_roles_excluded(detector):
    """Contract positions should not count as job hopping"""
    employment = [
        {'title': 'Contract Engineer', 'start_date': '2020-01', 'end_date': '2020-09'},  # 8 months
        {'title': 'Contractor', 'start_date': '2020-10', 'end_date': '2021-03'},         # 5 months
        {'title': 'Engineer', 'start_date': '2021-04', 'end_date': '2024-12'}            # 3+ years
    ]

    result = detector.detect(employment)

    # Contract roles excluded from penalty
    assert result['short_stints_count'] == 0
    assert result['penalty_score'] == 0

def test_intern_roles_excluded(detector):
    """Internships should not count as job hopping"""
    employment = [
        {'title': 'Software Intern', 'start_date': '2019-06', 'end_date': '2019-09'},  # 3 months
        {'title': 'Engineer', 'start_date': '2020-01', 'end_date': '2024-12'}          # 5 years
    ]

    result = detector.detect(employment)

    assert result['short_stints_count'] == 0
    assert result['penalty_score'] == 0

def test_exactly_12_months_not_considered_short(detector):
    """Position exactly 12 months should NOT be penalized"""
    employment = [
        {'title': 'Engineer', 'start_date': '2020-01', 'end_date': '2021-01'},  # Exactly 12 months
        {'title': 'Senior Engineer', 'start_date': '2021-02', 'end_date': '2024-12'}
    ]

    result = detector.detect(employment)

    # 12 months = threshold, not short stint
    assert result['short_stints_count'] == 0
    assert result['penalty_score'] == 0

def test_11_months_considered_short(detector):
    """Position <12 months should be penalized"""
    employment = [
        {'title': 'Engineer', 'start_date': '2020-01', 'end_date': '2020-12'},  # 11 months
        {'title': 'Senior Engineer', 'start_date': '2021-01', 'end_date': '2024-12'}
    ]

    result = detector.detect(employment)

    assert result['short_stints_count'] == 1
    assert result['penalty_score'] == -1

def test_short_stint_details(detector):
    """Short stint details should include title, duration, reason excluded"""
    employment = [
        {'title': 'Junior Dev', 'start_date': '2020-01', 'end_date': '2020-08'},  # 7 months
        {'title': 'Senior Dev', 'start_date': '2020-09', 'end_date': '2024-12'}
    ]

    result = detector.detect(employment)

    stint = result['short_stints'][0]
    assert 'title' in stint
    assert 'duration_months' in stint
    assert stint['duration_months'] == 7
    assert 'is_excluded' in stint
    assert stint['is_excluded'] is False

def test_empty_employment_history(detector):
    """Should handle empty employment history gracefully"""
    employment = []

    result = detector.detect(employment)

    assert result['short_stints_count'] == 0
    assert result['penalty_score'] == 0
