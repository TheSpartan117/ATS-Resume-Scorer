import pytest
from datetime import datetime
from backend.services.gap_detector import GapDetector

@pytest.fixture
def detector():
    return GapDetector()

def test_no_gaps_continuous_employment(detector):
    """Continuous employment with no gaps = no penalty"""
    employment = [
        {'start_date': '2020-01', 'end_date': '2022-06'},
        {'start_date': '2022-06', 'end_date': '2024-12'}
    ]

    result = detector.detect(employment)

    assert result['total_gap_months'] == 0
    assert result['penalty_score'] == 0
    assert len(result['gaps']) == 0

def test_small_gap_under_threshold(detector):
    """Gap <3 months = no penalty"""
    employment = [
        {'start_date': '2020-01', 'end_date': '2022-06'},
        {'start_date': '2022-08', 'end_date': '2024-12'}  # 2 month gap
    ]

    result = detector.detect(employment)

    assert result['total_gap_months'] == 2
    assert result['penalty_score'] == 0  # Under 3 month threshold

def test_6_month_gap(detector):
    """6 month gap = -1 pt penalty"""
    employment = [
        {'start_date': '2020-01', 'end_date': '2021-12'},
        {'start_date': '2022-06', 'end_date': '2024-12'}  # 6 month gap
    ]

    result = detector.detect(employment)

    assert result['total_gap_months'] == 6
    assert result['penalty_score'] == -1
    assert len(result['gaps']) == 1

def test_12_month_gap(detector):
    """13 month gap = -2 pt penalty"""
    employment = [
        {'start_date': '2020-01', 'end_date': '2021-12'},
        {'start_date': '2023-01', 'end_date': '2024-12'}  # 13 month gap (Jan 2022-Jan 2023)
    ]

    result = detector.detect(employment)

    assert result['total_gap_months'] == 13
    assert result['penalty_score'] == -2  # 13/6 = 2 penalties

def test_multiple_gaps(detector):
    """Multiple gaps should accumulate"""
    employment = [
        {'start_date': '2018-01', 'end_date': '2019-06'},
        {'start_date': '2020-01', 'end_date': '2021-06'},  # 7 month gap
        {'start_date': '2022-01', 'end_date': '2023-06'}   # 7 month gap
    ]

    result = detector.detect(employment)

    assert result['total_gap_months'] == 14  # 7 + 7
    assert result['penalty_score'] == -2  # 14/6 = 2 penalties
    assert len(result['gaps']) == 2

def test_penalty_cap_at_5_points(detector):
    """Penalty should not exceed -5 points"""
    employment = [
        {'start_date': '2015-01', 'end_date': '2016-01'},
        {'start_date': '2020-01', 'end_date': '2024-12'}  # 4 year (48 month) gap
    ]

    result = detector.detect(employment)

    # 48/6 = 8 penalties, but cap at -5
    assert result['penalty_score'] == -5

def test_parse_various_date_formats(detector):
    """Should handle different date formats"""
    employment_formats = [
        {'start_date': '2020-01', 'end_date': '2021-06'},
        {'start_date': '01/2021', 'end_date': '06/2022'},
        {'start_date': 'Jan 2022', 'end_date': 'Dec 2023'}
    ]

    result = detector.detect(employment_formats)

    # Should parse all formats and detect gaps
    assert isinstance(result['penalty_score'], int)

def test_current_employment(detector):
    """Should handle 'Present' or None as end date"""
    employment = [
        {'start_date': '2020-01', 'end_date': '2022-06'},
        {'start_date': '2022-08', 'end_date': 'Present'}  # Current job
    ]

    result = detector.detect(employment)

    assert result['total_gap_months'] == 2
    assert result['penalty_score'] == 0

def test_gap_details(detector):
    """Gap details should include start, end, and duration"""
    employment = [
        {'start_date': '2020-01', 'end_date': '2020-12'},
        {'start_date': '2021-07', 'end_date': '2022-12'}  # 7 month gap
    ]

    result = detector.detect(employment)

    gap = result['gaps'][0]
    assert 'start_date' in gap
    assert 'end_date' in gap
    assert 'duration_months' in gap
    assert gap['duration_months'] == 7

def test_empty_employment_history(detector):
    """Should handle empty employment history gracefully"""
    employment = []

    result = detector.detect(employment)

    assert result['total_gap_months'] == 0
    assert result['penalty_score'] == 0
    assert len(result['gaps']) == 0
