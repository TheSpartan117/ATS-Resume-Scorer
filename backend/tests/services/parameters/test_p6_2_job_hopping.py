"""
Test P6.2: Job Hopping Penalty (-3 points maximum)

Tests penalty application for short job stints (<12 months duration).

Penalty Structure:
- Each position <12 months: -1 point
- Maximum penalty: -3 points
- Exceptions: Contract, intern, consultant, temporary roles

Scoring:
- 0 short stints: 0 penalty
- 1 short stint: -1 point
- 2 short stints: -2 points
- 3 short stints: -3 points
- 4+ short stints: -3 points (capped)
"""

import pytest
from backend.services.parameters.p6_2_job_hopping import JobHoppingPenaltyScorer


@pytest.fixture
def scorer():
    """Create JobHoppingPenaltyScorer instance."""
    return JobHoppingPenaltyScorer()


# ============================================================================
# ZERO PENALTY TESTS
# ============================================================================

def test_no_short_stints_zero_penalty(scorer):
    """No short stints = 0 penalty"""
    employment = [
        {'title': 'Senior Engineer', 'start_date': '2020-01', 'end_date': '2022-06'},  # 29 months
        {'title': 'Engineer', 'start_date': '2018-01', 'end_date': '2019-12'},         # 23 months
        {'title': 'Junior Engineer', 'start_date': '2016-06', 'end_date': '2017-12'}   # 18 months
    ]

    result = scorer.score(employment)

    assert result['penalty'] == 0
    assert result['short_stints_count'] == 0
    assert result['flagged_positions'] == []
    assert result['max_penalty'] == -3


def test_empty_employment_history(scorer):
    """Empty employment history = 0 penalty"""
    result = scorer.score([])

    assert result['penalty'] == 0
    assert result['short_stints_count'] == 0
    assert result['flagged_positions'] == []
    assert result['max_penalty'] == -3


# ============================================================================
# PENALTY LEVEL TESTS
# ============================================================================

def test_one_short_stint_minus_one(scorer):
    """1 short stint = -1 point"""
    employment = [
        {'title': 'Senior Engineer', 'start_date': '2021-01', 'end_date': '2023-06'},  # 29 months
        {'title': 'Engineer', 'start_date': '2020-01', 'end_date': '2020-10'},        # 9 months (short)
        {'title': 'Junior Engineer', 'start_date': '2018-01', 'end_date': '2019-12'}   # 23 months
    ]

    result = scorer.score(employment)

    assert result['penalty'] == -1
    assert result['short_stints_count'] == 1
    assert len(result['flagged_positions']) == 1
    assert result['flagged_positions'][0]['title'] == 'Engineer'
    assert result['flagged_positions'][0]['duration_months'] == 9


def test_two_short_stints_minus_two(scorer):
    """2 short stints = -2 points"""
    employment = [
        {'title': 'Senior Engineer', 'start_date': '2022-01', 'end_date': '2023-06'},  # 17 months
        {'title': 'Engineer', 'start_date': '2021-01', 'end_date': '2021-08'},        # 7 months (short)
        {'title': 'Junior Engineer', 'start_date': '2020-01', 'end_date': '2020-10'},  # 9 months (short)
        {'title': 'Intern', 'start_date': '2019-01', 'end_date': '2019-12'}            # 11 months
    ]

    result = scorer.score(employment)

    assert result['penalty'] == -2
    assert result['short_stints_count'] == 2
    assert len(result['flagged_positions']) == 2


def test_three_short_stints_minus_three(scorer):
    """3 short stints = -3 points (max penalty reached)"""
    employment = [
        {'title': 'Engineer A', 'start_date': '2022-01', 'end_date': '2022-09'},  # 8 months (short)
        {'title': 'Engineer B', 'start_date': '2021-01', 'end_date': '2021-10'},  # 9 months (short)
        {'title': 'Engineer C', 'start_date': '2020-01', 'end_date': '2020-08'},  # 7 months (short)
        {'title': 'Senior Engineer', 'start_date': '2018-01', 'end_date': '2019-12'}  # 23 months
    ]

    result = scorer.score(employment)

    assert result['penalty'] == -3
    assert result['short_stints_count'] == 3
    assert len(result['flagged_positions']) == 3


def test_four_short_stints_capped_at_minus_three(scorer):
    """4+ short stints = -3 points (capped at max penalty)"""
    employment = [
        {'title': 'Engineer A', 'start_date': '2023-01', 'end_date': '2023-08'},  # 7 months (short)
        {'title': 'Engineer B', 'start_date': '2022-01', 'end_date': '2022-09'},  # 8 months (short)
        {'title': 'Engineer C', 'start_date': '2021-01', 'end_date': '2021-10'},  # 9 months (short)
        {'title': 'Engineer D', 'start_date': '2020-01', 'end_date': '2020-08'},  # 7 months (short)
        {'title': 'Engineer E', 'start_date': '2019-01', 'end_date': '2019-09'}   # 8 months (short)
    ]

    result = scorer.score(employment)

    assert result['penalty'] == -3  # Capped at -3
    assert result['short_stints_count'] == 5  # All 5 are short
    assert len(result['flagged_positions']) == 5
    assert 'exceeds_max_penalty' in result['details']


# ============================================================================
# EXEMPTION TESTS (Contract/Intern/Consultant/Temp)
# ============================================================================

def test_contract_roles_excluded(scorer):
    """Contract roles with short stints don't count toward penalty"""
    employment = [
        {'title': 'Contract Engineer', 'start_date': '2022-01', 'end_date': '2022-08'},     # 7 months, but contract
        {'title': 'Contractor - Backend', 'start_date': '2021-01', 'end_date': '2021-09'},  # 8 months, but contractor
        {'title': 'Senior Engineer', 'start_date': '2019-01', 'end_date': '2020-12'}        # 23 months
    ]

    result = scorer.score(employment)

    assert result['penalty'] == 0
    assert result['short_stints_count'] == 0  # Excluded stints don't count
    assert len(result['flagged_positions']) == 2  # Still flagged but marked as excluded
    assert result['flagged_positions'][0]['is_excluded'] is True
    assert result['flagged_positions'][1]['is_excluded'] is True


def test_intern_roles_excluded(scorer):
    """Intern roles with short stints don't count toward penalty"""
    employment = [
        {'title': 'Software Engineer Intern', 'start_date': '2022-06', 'end_date': '2022-09'},  # 3 months
        {'title': 'Internship - Data Science', 'start_date': '2021-06', 'end_date': '2021-08'},  # 2 months
        {'title': 'Engineer', 'start_date': '2019-01', 'end_date': '2020-12'}                     # 23 months
    ]

    result = scorer.score(employment)

    assert result['penalty'] == 0
    assert result['short_stints_count'] == 0


def test_consultant_roles_excluded(scorer):
    """Consultant roles with short stints don't count toward penalty"""
    employment = [
        {'title': 'Technical Consultant', 'start_date': '2022-01', 'end_date': '2022-09'},  # 8 months
        {'title': 'Consulting Engineer', 'start_date': '2021-01', 'end_date': '2021-07'},   # 6 months
        {'title': 'Engineer', 'start_date': '2019-01', 'end_date': '2020-12'}                # 23 months
    ]

    result = scorer.score(employment)

    assert result['penalty'] == 0
    assert result['short_stints_count'] == 0


def test_temporary_roles_excluded(scorer):
    """Temporary roles with short stints don't count toward penalty"""
    employment = [
        {'title': 'Temporary Engineer', 'start_date': '2022-01', 'end_date': '2022-08'},  # 7 months
        {'title': 'Temp Software Developer', 'start_date': '2021-01', 'end_date': '2021-09'},  # 8 months
        {'title': 'Engineer', 'start_date': '2019-01', 'end_date': '2020-12'}              # 23 months
    ]

    result = scorer.score(employment)

    assert result['penalty'] == 0
    assert result['short_stints_count'] == 0


def test_mixed_exempt_and_penalized(scorer):
    """Mix of exempt and penalized short stints"""
    employment = [
        {'title': 'Engineer A', 'start_date': '2023-01', 'end_date': '2023-08'},           # 7 months (penalized)
        {'title': 'Contract Engineer', 'start_date': '2022-01', 'end_date': '2022-09'},    # 8 months (exempt)
        {'title': 'Engineer B', 'start_date': '2021-01', 'end_date': '2021-10'},          # 9 months (penalized)
        {'title': 'Intern Developer', 'start_date': '2020-06', 'end_date': '2020-09'},     # 3 months (exempt)
        {'title': 'Senior Engineer', 'start_date': '2018-01', 'end_date': '2019-12'}       # 23 months
    ]

    result = scorer.score(employment)

    assert result['penalty'] == -2  # Only 2 non-exempt short stints
    assert result['short_stints_count'] == 2
    assert len(result['flagged_positions']) == 4  # All 4 short stints tracked


# ============================================================================
# EDGE CASE TESTS
# ============================================================================

def test_exactly_twelve_months_not_penalized(scorer):
    """Position with exactly 12 months duration should NOT be penalized"""
    employment = [
        {'title': 'Engineer', 'start_date': '2022-01', 'end_date': '2023-01'},  # Exactly 12 months
        {'title': 'Senior Engineer', 'start_date': '2020-01', 'end_date': '2021-12'}  # 23 months
    ]

    result = scorer.score(employment)

    assert result['penalty'] == 0
    assert result['short_stints_count'] == 0


def test_eleven_months_is_penalized(scorer):
    """Position with 11 months duration should be penalized"""
    employment = [
        {'title': 'Engineer', 'start_date': '2022-01', 'end_date': '2022-12'},  # 11 months
        {'title': 'Senior Engineer', 'start_date': '2020-01', 'end_date': '2021-12'}  # 23 months
    ]

    result = scorer.score(employment)

    assert result['penalty'] == -1
    assert result['short_stints_count'] == 1


def test_missing_start_date_ignored(scorer):
    """Positions with missing start_date are ignored"""
    employment = [
        {'title': 'Engineer A', 'start_date': None, 'end_date': '2023-01'},
        {'title': 'Engineer B', 'start_date': '2022-01', 'end_date': '2022-08'},  # 7 months (penalized)
        {'title': 'Senior Engineer', 'start_date': '2020-01', 'end_date': '2021-12'}  # 23 months
    ]

    result = scorer.score(employment)

    assert result['penalty'] == -1
    assert result['short_stints_count'] == 1


def test_missing_end_date_ignored(scorer):
    """Positions with missing end_date are ignored"""
    employment = [
        {'title': 'Engineer A', 'start_date': '2023-01', 'end_date': None},
        {'title': 'Engineer B', 'start_date': '2022-01', 'end_date': '2022-08'},  # 7 months (penalized)
        {'title': 'Senior Engineer', 'start_date': '2020-01', 'end_date': '2021-12'}  # 23 months
    ]

    result = scorer.score(employment)

    assert result['penalty'] == -1
    assert result['short_stints_count'] == 1


def test_missing_title_handled(scorer):
    """Positions with missing title are handled gracefully"""
    employment = [
        {'start_date': '2022-01', 'end_date': '2022-08'},  # 7 months, no title
        {'title': 'Senior Engineer', 'start_date': '2020-01', 'end_date': '2021-12'}  # 23 months
    ]

    result = scorer.score(employment)

    assert result['penalty'] == -1
    assert result['short_stints_count'] == 1
    assert result['flagged_positions'][0]['title'] == 'Unknown'


def test_present_as_end_date(scorer):
    """'Present' as end_date should be handled (use current date)"""
    employment = [
        {'title': 'Current Engineer', 'start_date': '2023-01', 'end_date': 'Present'},  # Should be >12 months by now (2026-02)
        {'title': 'Senior Engineer', 'start_date': '2020-01', 'end_date': '2021-12'}     # 23 months
    ]

    result = scorer.score(employment)

    # Current position started 2023-01, now is 2026-02, so ~37 months - not penalized
    assert result['penalty'] == 0
    assert result['short_stints_count'] == 0


# ============================================================================
# RESULT STRUCTURE VALIDATION
# ============================================================================

def test_result_structure(scorer):
    """Verify result structure matches requirements"""
    employment = [
        {'title': 'Engineer A', 'start_date': '2022-01', 'end_date': '2022-08'},  # 7 months (short)
        {'title': 'Engineer B', 'start_date': '2020-01', 'end_date': '2021-12'}   # 23 months
    ]

    result = scorer.score(employment)

    # Required keys
    assert 'penalty' in result
    assert 'short_stints_count' in result
    assert 'flagged_positions' in result
    assert 'details' in result
    assert 'max_penalty' in result

    # Penalty should be negative or zero
    assert result['penalty'] <= 0

    # Max penalty constant
    assert result['max_penalty'] == -3

    # Flagged positions structure
    assert isinstance(result['flagged_positions'], list)
    if len(result['flagged_positions']) > 0:
        flagged = result['flagged_positions'][0]
        assert 'title' in flagged
        assert 'duration_months' in flagged
        assert 'is_excluded' in flagged


# ============================================================================
# DETAILED OUTPUT TESTS
# ============================================================================

def test_details_field_content(scorer):
    """Verify details field provides useful information"""
    employment = [
        {'title': 'Engineer A', 'start_date': '2023-01', 'end_date': '2023-08'},  # 7 months (short)
        {'title': 'Engineer B', 'start_date': '2022-01', 'end_date': '2022-09'},  # 8 months (short)
        {'title': 'Senior Engineer', 'start_date': '2020-01', 'end_date': '2021-12'}  # 23 months
    ]

    result = scorer.score(employment)

    details = result['details']
    assert 'total_positions' in details
    assert 'positions_analyzed' in details
    assert details['total_positions'] == 3

    # Penalty description
    assert result['penalty'] == -2
    assert result['short_stints_count'] == 2


def test_exclusion_reason_in_flagged_positions(scorer):
    """Verify excluded positions have exclusion_reason"""
    employment = [
        {'title': 'Contract Engineer', 'start_date': '2022-01', 'end_date': '2022-08'},  # 7 months, contract
        {'title': 'Engineer', 'start_date': '2020-01', 'end_date': '2021-12'}            # 23 months
    ]

    result = scorer.score(employment)

    assert len(result['flagged_positions']) == 1
    flagged = result['flagged_positions'][0]
    assert flagged['is_excluded'] is True
    assert 'exclusion_reason' in flagged
    assert 'Contract' in flagged['exclusion_reason']
