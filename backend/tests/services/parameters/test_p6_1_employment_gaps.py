"""
Test P6.1: Employment Gaps Penalty (-5 points max)

Tests penalty system for employment gaps:
- Uses GapDetector from foundation layer
- -1 point per 6 months of gap
- Gaps <3 months are ignored
- Maximum penalty: -5 points

Gap Detection Rules:
- Only gaps ≥3 months count toward penalty
- Penalty = -(total_gap_months // 6)
- Capped at -5 points maximum

Test Coverage:
1. No gaps (0 penalty)
2. Small gaps <3 months (0 penalty)
3. Exactly 6 months gap (-1 pt)
4. Exactly 12 months gap (-2 pts)
5. 30 months gap (capped at -5 pts)
6. Multiple gaps accumulation
7. Edge cases (empty history, single job, invalid dates)
"""

import pytest
from backend.services.parameters.p6_1_employment_gaps import EmploymentGapsPenalty


@pytest.fixture
def penalty_calculator():
    """Create EmploymentGapsPenalty instance."""
    return EmploymentGapsPenalty()


# ============================================================================
# NO GAPS TESTS
# ============================================================================

def test_no_gaps_continuous_employment(penalty_calculator):
    """Continuous employment with no gaps = 0 penalty"""
    employment_history = [
        {'start_date': '2020-01', 'end_date': '2021-12'},
        {'start_date': '2022-01', 'end_date': '2023-06'},
        {'start_date': '2023-07', 'end_date': 'Present'}
    ]

    result = penalty_calculator.score(employment_history)
    assert result['penalty'] == 0
    assert result['max_penalty'] == -5
    assert result['gaps_detected'] == 0
    assert result['total_months'] == 0
    assert result['gap_details'] == []


def test_no_gaps_single_job(penalty_calculator):
    """Single job (no opportunity for gaps) = 0 penalty"""
    employment_history = [
        {'start_date': '2020-01', 'end_date': 'Present'}
    ]

    result = penalty_calculator.score(employment_history)
    assert result['penalty'] == 0
    assert result['gaps_detected'] == 0
    assert result['total_months'] == 0


def test_no_gaps_overlapping_jobs(penalty_calculator):
    """Overlapping jobs (freelance + full-time) = 0 penalty"""
    employment_history = [
        {'start_date': '2020-01', 'end_date': '2021-06'},
        {'start_date': '2021-03', 'end_date': '2022-12'},  # Overlaps with previous
        {'start_date': '2022-06', 'end_date': 'Present'}    # Overlaps with previous
    ]

    result = penalty_calculator.score(employment_history)
    assert result['penalty'] == 0
    assert result['total_months'] == 0


# ============================================================================
# SMALL GAPS (< 3 MONTHS) - NO PENALTY
# ============================================================================

def test_small_gap_2_months_ignored(penalty_calculator):
    """2-month gap (under threshold) = 0 penalty"""
    employment_history = [
        {'start_date': '2020-01', 'end_date': '2021-06'},
        {'start_date': '2021-08', 'end_date': 'Present'}  # 2-month gap (July)
    ]

    result = penalty_calculator.score(employment_history)
    assert result['penalty'] == 0
    assert result['total_months'] == 2
    assert result['gaps_detected'] == 0  # No gaps ≥3 months
    assert result['gap_details'] == []


def test_multiple_small_gaps_no_penalty(penalty_calculator):
    """Multiple gaps under 3 months each = 0 penalty"""
    employment_history = [
        {'start_date': '2020-01', 'end_date': '2020-06'},
        {'start_date': '2020-08', 'end_date': '2021-03'},  # 2-month gap
        {'start_date': '2021-05', 'end_date': '2022-01'},  # 2-month gap
        {'start_date': '2022-03', 'end_date': 'Present'}   # 2-month gap
    ]
    # Total 6 months but all individual gaps <3 months

    result = penalty_calculator.score(employment_history)
    assert result['penalty'] == 0
    assert result['total_months'] == 6
    assert result['gaps_detected'] == 0


# ============================================================================
# SINGLE GAP TESTS - GRADUATED PENALTIES
# ============================================================================

def test_exactly_3_months_gap_no_penalty(penalty_calculator):
    """3-month gap (threshold boundary) = 0 penalty (need 6 months for -1 pt)"""
    employment_history = [
        {'start_date': '2020-01', 'end_date': '2020-06'},
        {'start_date': '2020-09', 'end_date': 'Present'}  # 3-month gap
    ]

    result = penalty_calculator.score(employment_history)
    assert result['penalty'] == 0  # 3 // 6 = 0
    assert result['total_months'] == 3
    assert result['gaps_detected'] == 1  # Gap ≥3 months detected
    assert len(result['gap_details']) == 1


def test_exactly_6_months_gap_minus_1(penalty_calculator):
    """6-month gap = -1 point"""
    employment_history = [
        {'start_date': '2020-01', 'end_date': '2020-06'},
        {'start_date': '2020-12', 'end_date': 'Present'}  # 6-month gap
    ]

    result = penalty_calculator.score(employment_history)
    assert result['penalty'] == -1
    assert result['total_months'] == 6
    assert result['gaps_detected'] == 1
    assert len(result['gap_details']) == 1
    assert result['gap_details'][0]['duration_months'] == 6


def test_exactly_12_months_gap_minus_2(penalty_calculator):
    """12-month gap = -2 points"""
    employment_history = [
        {'start_date': '2020-01', 'end_date': '2020-12'},
        {'start_date': '2021-12', 'end_date': 'Present'}  # 12-month gap
    ]

    result = penalty_calculator.score(employment_history)
    assert result['penalty'] == -2
    assert result['total_months'] == 12
    assert result['gaps_detected'] == 1


def test_18_months_gap_minus_3(penalty_calculator):
    """18-month gap = -3 points"""
    employment_history = [
        {'start_date': '2019-01', 'end_date': '2019-06'},
        {'start_date': '2020-12', 'end_date': 'Present'}  # 18-month gap
    ]

    result = penalty_calculator.score(employment_history)
    assert result['penalty'] == -3
    assert result['total_months'] == 18


def test_24_months_gap_minus_4(penalty_calculator):
    """24-month gap = -4 points"""
    employment_history = [
        {'start_date': '2018-01', 'end_date': '2018-12'},
        {'start_date': '2020-12', 'end_date': 'Present'}  # 24-month gap
    ]

    result = penalty_calculator.score(employment_history)
    assert result['penalty'] == -4
    assert result['total_months'] == 24


def test_30_months_gap_capped_at_minus_5(penalty_calculator):
    """30-month gap = -5 points (capped at maximum)"""
    employment_history = [
        {'start_date': '2018-01', 'end_date': '2018-06'},
        {'start_date': '2020-12', 'end_date': 'Present'}  # 30-month gap
    ]

    result = penalty_calculator.score(employment_history)
    assert result['penalty'] == -5  # Capped at max
    assert result['total_months'] == 30
    assert result['gaps_detected'] == 1


def test_50_months_gap_still_capped_at_minus_5(penalty_calculator):
    """50-month gap = -5 points (hard cap)"""
    employment_history = [
        {'start_date': '2015-01', 'end_date': '2015-12'},
        {'start_date': '2020-02', 'end_date': 'Present'}  # 50-month gap
    ]

    result = penalty_calculator.score(employment_history)
    assert result['penalty'] == -5  # Capped at max
    assert result['total_months'] == 50


# ============================================================================
# MULTIPLE GAPS - ACCUMULATION
# ============================================================================

def test_multiple_gaps_accumulate(penalty_calculator):
    """Multiple gaps accumulate: 6 months + 6 months = -2 points"""
    employment_history = [
        {'start_date': '2018-01', 'end_date': '2018-06'},
        {'start_date': '2018-12', 'end_date': '2019-06'},  # 6-month gap
        {'start_date': '2019-12', 'end_date': 'Present'}   # 6-month gap
    ]

    result = penalty_calculator.score(employment_history)
    assert result['penalty'] == -2  # 12 total months // 6 = -2
    assert result['total_months'] == 12
    assert result['gaps_detected'] == 2
    assert len(result['gap_details']) == 2


def test_mixed_gaps_small_and_large(penalty_calculator):
    """Mix of small (<3mo) and large (≥3mo) gaps"""
    employment_history = [
        {'start_date': '2018-01', 'end_date': '2018-06'},
        {'start_date': '2018-08', 'end_date': '2019-03'},  # 2-month gap (ignored)
        {'start_date': '2019-10', 'end_date': '2020-03'},  # 7-month gap (counted)
        {'start_date': '2020-05', 'end_date': 'Present'}   # 2-month gap (ignored)
    ]
    # Total: 2 + 7 + 2 = 11 months
    # Penalty: 11 // 6 = -1 point

    result = penalty_calculator.score(employment_history)
    assert result['penalty'] == -1
    assert result['total_months'] == 11
    assert result['gaps_detected'] == 1  # Only 1 gap ≥3 months


def test_multiple_gaps_reach_cap(penalty_calculator):
    """Multiple gaps totaling >30 months = capped at -5"""
    employment_history = [
        {'start_date': '2015-01', 'end_date': '2015-12'},
        {'start_date': '2016-06', 'end_date': '2017-03'},  # 6-month gap
        {'start_date': '2018-01', 'end_date': '2018-06'},  # 10-month gap
        {'start_date': '2019-08', 'end_date': '2020-01'},  # 14-month gap
        {'start_date': '2020-06', 'end_date': 'Present'}   # 5-month gap
    ]
    # Total: 6 + 10 + 14 + 5 = 35 months
    # Penalty: 35 // 6 = -5 (actually -5.83 but capped)

    result = penalty_calculator.score(employment_history)
    assert result['penalty'] == -5
    assert result['total_months'] == 35
    assert result['gaps_detected'] == 4


# ============================================================================
# EDGE CASES
# ============================================================================

def test_empty_employment_history(penalty_calculator):
    """Empty history = 0 penalty"""
    result = penalty_calculator.score([])
    assert result['penalty'] == 0
    assert result['gaps_detected'] == 0
    assert result['total_months'] == 0


def test_none_employment_history(penalty_calculator):
    """None history = 0 penalty"""
    result = penalty_calculator.score(None)
    assert result['penalty'] == 0
    assert result['gaps_detected'] == 0


def test_missing_dates_handled_gracefully(penalty_calculator):
    """Missing or invalid dates are handled gracefully"""
    employment_history = [
        {'start_date': '2020-01', 'end_date': '2020-12'},
        {'start_date': None, 'end_date': '2021-06'},  # Missing start date
        {'start_date': '2021-06', 'end_date': 'Present'}
    ]

    result = penalty_calculator.score(employment_history)
    # Should not crash, calculates based on valid dates only
    assert result['penalty'] >= -5
    assert result['penalty'] <= 0


def test_date_format_variations(penalty_calculator):
    """Different date formats are handled correctly"""
    employment_history = [
        {'start_date': '2020-01', 'end_date': '2020-06'},
        {'start_date': '01/2021', 'end_date': 'Present'}  # Different format
    ]

    result = penalty_calculator.score(employment_history)
    assert result['penalty'] == -1  # 7-month gap (June 2020 to Jan 2021)
    assert result['total_months'] == 7


def test_present_current_keywords(penalty_calculator):
    """'Present', 'Current' keywords handled for ongoing employment"""
    employment_history = [
        {'start_date': '2018-01', 'end_date': '2020-06'},
        {'start_date': '2021-01', 'end_date': 'Current'}  # 7-month gap
    ]

    result = penalty_calculator.score(employment_history)
    assert result['penalty'] == -1
    assert result['total_months'] == 7


def test_unsorted_employment_history(penalty_calculator):
    """Unsorted history is handled correctly (detector sorts by start date)"""
    employment_history = [
        {'start_date': '2021-01', 'end_date': 'Present'},
        {'start_date': '2018-01', 'end_date': '2018-12'},
        {'start_date': '2019-06', 'end_date': '2020-06'}  # 6-month gap between jobs
    ]

    result = penalty_calculator.score(employment_history)
    # Gaps: 2018-12 to 2019-06 = 6 months
    #       2020-06 to 2021-01 = 7 months
    # Total: 13 months = -2 points
    assert result['penalty'] == -2
    assert result['total_months'] == 13


# ============================================================================
# RESULT STRUCTURE VALIDATION
# ============================================================================

def test_result_structure_complete(penalty_calculator):
    """Result contains all required fields"""
    employment_history = [
        {'start_date': '2020-01', 'end_date': '2020-06'},
        {'start_date': '2021-01', 'end_date': 'Present'}  # 7-month gap
    ]

    result = penalty_calculator.score(employment_history)

    # Required fields
    assert 'penalty' in result
    assert 'max_penalty' in result
    assert 'gaps_detected' in result
    assert 'total_months' in result
    assert 'gap_details' in result

    # Field types
    assert isinstance(result['penalty'], int)
    assert isinstance(result['max_penalty'], int)
    assert isinstance(result['gaps_detected'], int)
    assert isinstance(result['total_months'], int)
    assert isinstance(result['gap_details'], list)

    # Field constraints
    assert result['penalty'] <= 0
    assert result['penalty'] >= -5
    assert result['max_penalty'] == -5
    assert result['gaps_detected'] >= 0
    assert result['total_months'] >= 0


def test_gap_details_structure(penalty_calculator):
    """Gap details contain correct information"""
    employment_history = [
        {'start_date': '2020-01', 'end_date': '2020-06'},
        {'start_date': '2021-01', 'end_date': 'Present'}  # 7-month gap
    ]

    result = penalty_calculator.score(employment_history)

    assert len(result['gap_details']) == 1
    gap = result['gap_details'][0]

    assert 'start_date' in gap
    assert 'end_date' in gap
    assert 'duration_months' in gap
    assert gap['duration_months'] == 7
