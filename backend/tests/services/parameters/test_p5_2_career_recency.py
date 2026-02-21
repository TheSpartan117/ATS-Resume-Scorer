"""
Test P5.2: Career Recency (3 points)

Tests scoring based on recency of most recent employment.

Scoring:
- Currently employed (Present/ongoing): 3 pts
- Left within 3 months: 2 pts
- Left 3-12 months ago: 1 pt
- Left >12 months ago: 0 pts
"""

import pytest
from datetime import datetime, timedelta
from backend.services.parameters.p5_2_career_recency import CareerRecencyScorer


@pytest.fixture
def scorer():
    """Create CareerRecencyScorer instance."""
    return CareerRecencyScorer()


# ============================================================================
# CURRENTLY EMPLOYED TESTS (3 pts)
# ============================================================================

def test_currently_employed_present(scorer):
    """Currently employed with 'Present' = 3 pts"""
    experience = [
        {
            'title': 'Senior Engineer',
            'company': 'Tech Corp',
            'dates': '2020 - Present'
        }
    ]

    result = scorer.score(experience)

    assert result['score'] == 3
    assert result['max_score'] == 3
    assert result['recency_status'] == 'currently_employed'
    assert result['months_since_last'] == 0
    assert result['most_recent_end_date'] == 'Present'


def test_currently_employed_current(scorer):
    """Currently employed with 'Current' = 3 pts"""
    experience = [
        {
            'title': 'Product Manager',
            'company': 'Startup Inc',
            'dates': 'Jan 2021 - Current'
        }
    ]

    result = scorer.score(experience)

    assert result['score'] == 3
    assert result['recency_status'] == 'currently_employed'
    assert result['months_since_last'] == 0


def test_currently_employed_ongoing(scorer):
    """Currently employed with 'ongoing' = 3 pts"""
    experience = [
        {
            'title': 'Data Scientist',
            'company': 'AI Labs',
            'dates': '2022 - ongoing'
        }
    ]

    result = scorer.score(experience)

    assert result['score'] == 3
    assert result['recency_status'] == 'currently_employed'


def test_currently_employed_multiple_jobs(scorer):
    """Most recent job is current = 3 pts"""
    experience = [
        {
            'title': 'Junior Engineer',
            'company': 'Old Corp',
            'dates': '2018 - 2020'
        },
        {
            'title': 'Senior Engineer',
            'company': 'New Corp',
            'dates': '2020 - Present'
        }
    ]

    result = scorer.score(experience)

    assert result['score'] == 3
    assert result['recency_status'] == 'currently_employed'


# ============================================================================
# LEFT WITHIN 3 MONTHS TESTS (2 pts)
# ============================================================================

def test_left_1_month_ago(scorer):
    """Left 1 month ago = 2 pts"""
    one_month_ago = (datetime.now() - timedelta(days=30)).strftime('%Y-%m')

    experience = [
        {
            'title': 'Engineer',
            'company': 'Tech Corp',
            'dates': f'2020 - {one_month_ago}'
        }
    ]

    result = scorer.score(experience)

    assert result['score'] == 2
    assert result['max_score'] == 3
    assert result['recency_status'] == 'left_within_3_months'
    assert 0 < result['months_since_last'] <= 3


def test_left_2_months_ago(scorer):
    """Left 2 months ago = 2 pts"""
    two_months_ago = (datetime.now() - timedelta(days=60)).strftime('%Y-%m')

    experience = [
        {
            'title': 'Developer',
            'company': 'Software Inc',
            'dates': f'2019-01 - {two_months_ago}'
        }
    ]

    result = scorer.score(experience)

    assert result['score'] == 2
    assert result['recency_status'] == 'left_within_3_months'
    assert 0 < result['months_since_last'] <= 3


def test_left_3_months_ago_boundary(scorer):
    """Left exactly 3 months ago = 2 pts (boundary case)"""
    three_months_ago = (datetime.now() - timedelta(days=90)).strftime('%Y-%m')

    experience = [
        {
            'title': 'Analyst',
            'company': 'Data Corp',
            'dates': f'2020-06 - {three_months_ago}'
        }
    ]

    result = scorer.score(experience)

    assert result['score'] == 2
    assert result['recency_status'] == 'left_within_3_months'


# ============================================================================
# LEFT 3-12 MONTHS AGO TESTS (1 pt)
# ============================================================================

def test_left_4_months_ago(scorer):
    """Left 4 months ago = 1 pt"""
    four_months_ago = (datetime.now() - timedelta(days=120)).strftime('%Y-%m')

    experience = [
        {
            'title': 'Manager',
            'company': 'Business Corp',
            'dates': f'2018 - {four_months_ago}'
        }
    ]

    result = scorer.score(experience)

    assert result['score'] == 1
    assert result['recency_status'] == 'left_3_12_months_ago'
    assert 3 < result['months_since_last'] <= 12


def test_left_6_months_ago(scorer):
    """Left 6 months ago = 1 pt"""
    six_months_ago = (datetime.now() - timedelta(days=180)).strftime('%Y-%m')

    experience = [
        {
            'title': 'Consultant',
            'company': 'Advisory LLC',
            'dates': f'2019-01 - {six_months_ago}'
        }
    ]

    result = scorer.score(experience)

    assert result['score'] == 1
    assert result['recency_status'] == 'left_3_12_months_ago'


def test_left_12_months_ago_boundary(scorer):
    """Left exactly 12 months ago = 1 pt (boundary case)"""
    twelve_months_ago = (datetime.now() - timedelta(days=365)).strftime('%Y-%m')

    experience = [
        {
            'title': 'Director',
            'company': 'Enterprise Inc',
            'dates': f'2015 - {twelve_months_ago}'
        }
    ]

    result = scorer.score(experience)

    assert result['score'] == 1
    assert result['recency_status'] == 'left_3_12_months_ago'


# ============================================================================
# LEFT >12 MONTHS AGO TESTS (0 pts)
# ============================================================================

def test_left_13_months_ago(scorer):
    """Left 13 months ago = 0 pts"""
    thirteen_months_ago = (datetime.now() - timedelta(days=395)).strftime('%Y-%m')

    experience = [
        {
            'title': 'Engineer',
            'company': 'Old Corp',
            'dates': f'2015 - {thirteen_months_ago}'
        }
    ]

    result = scorer.score(experience)

    assert result['score'] == 0
    assert result['recency_status'] == 'left_over_12_months_ago'
    assert result['months_since_last'] > 12


def test_left_2_years_ago(scorer):
    """Left 2 years ago = 0 pts"""
    two_years_ago = (datetime.now() - timedelta(days=730)).strftime('%Y-%m')

    experience = [
        {
            'title': 'Developer',
            'company': 'Legacy Systems',
            'dates': f'2010 - {two_years_ago}'
        }
    ]

    result = scorer.score(experience)

    assert result['score'] == 0
    assert result['recency_status'] == 'left_over_12_months_ago'
    assert result['months_since_last'] > 12


def test_left_5_years_ago(scorer):
    """Left 5 years ago = 0 pts"""
    experience = [
        {
            'title': 'Analyst',
            'company': 'Ancient Corp',
            'dates': '2010 - 2019'
        }
    ]

    result = scorer.score(experience)

    assert result['score'] == 0
    assert result['recency_status'] == 'left_over_12_months_ago'


# ============================================================================
# DATE PARSING VARIATIONS TESTS
# ============================================================================

def test_date_format_yyyy_mm(scorer):
    """Handle YYYY-MM format"""
    experience = [
        {
            'title': 'Engineer',
            'company': 'Tech Corp',
            'dates': '2020-01 - Present'
        }
    ]

    result = scorer.score(experience)

    assert result['score'] == 3
    assert result['recency_status'] == 'currently_employed'


def test_date_format_mon_yyyy(scorer):
    """Handle Mon YYYY format"""
    experience = [
        {
            'title': 'Developer',
            'company': 'Software Inc',
            'dates': 'Jan 2020 - Present'
        }
    ]

    result = scorer.score(experience)

    assert result['score'] == 3


def test_date_format_month_yyyy(scorer):
    """Handle Month YYYY format"""
    experience = [
        {
            'title': 'Manager',
            'company': 'Business Corp',
            'dates': 'January 2020 - Present'
        }
    ]

    result = scorer.score(experience)

    assert result['score'] == 3


def test_date_format_yyyy_only(scorer):
    """Handle YYYY only format"""
    experience = [
        {
            'title': 'Consultant',
            'company': 'Advisory LLC',
            'dates': '2020 - Present'
        }
    ]

    result = scorer.score(experience)

    assert result['score'] == 3


def test_date_format_mixed(scorer):
    """Handle mixed date formats in different jobs"""
    one_month_ago = (datetime.now() - timedelta(days=30)).strftime('%Y-%m')

    experience = [
        {
            'title': 'Junior Dev',
            'company': 'Old Corp',
            'dates': 'Jan 2018 - Dec 2020'
        },
        {
            'title': 'Senior Dev',
            'company': 'New Corp',
            'dates': f'2020-12 - {one_month_ago}'
        }
    ]

    result = scorer.score(experience)

    assert result['score'] == 2
    assert result['recency_status'] == 'left_within_3_months'


# ============================================================================
# MULTIPLE JOBS TESTS
# ============================================================================

def test_multiple_jobs_most_recent_current(scorer):
    """With multiple jobs, use most recent end date (currently employed)"""
    experience = [
        {
            'title': 'Entry Level',
            'company': 'First Corp',
            'dates': '2015 - 2017'
        },
        {
            'title': 'Mid Level',
            'company': 'Second Corp',
            'dates': '2017 - 2020'
        },
        {
            'title': 'Senior Level',
            'company': 'Current Corp',
            'dates': '2020 - Present'
        }
    ]

    result = scorer.score(experience)

    assert result['score'] == 3
    assert result['recency_status'] == 'currently_employed'


def test_multiple_jobs_most_recent_old(scorer):
    """With multiple old jobs, use most recent end date"""
    experience = [
        {
            'title': 'Engineer I',
            'company': 'Corp A',
            'dates': '2010 - 2015'
        },
        {
            'title': 'Engineer II',
            'company': 'Corp B',
            'dates': '2015 - 2018'
        }
    ]

    result = scorer.score(experience)

    assert result['score'] == 0
    assert result['recency_status'] == 'left_over_12_months_ago'
    assert result['most_recent_end_date'] == '2018'


def test_jobs_out_of_order(scorer):
    """Jobs listed out of chronological order - should still find most recent"""
    two_months_ago = (datetime.now() - timedelta(days=60)).strftime('%Y-%m')

    experience = [
        {
            'title': 'Current Job',
            'company': 'Latest Corp',
            'dates': f'2021 - {two_months_ago}'
        },
        {
            'title': 'Old Job',
            'company': 'First Corp',
            'dates': '2015 - 2018'
        },
        {
            'title': 'Middle Job',
            'company': 'Second Corp',
            'dates': '2018 - 2021'
        }
    ]

    result = scorer.score(experience)

    assert result['score'] == 2
    assert result['recency_status'] == 'left_within_3_months'


# ============================================================================
# EDGE CASES
# ============================================================================

def test_empty_experience(scorer):
    """Empty experience = 0 pts"""
    result = scorer.score([])

    assert result['score'] == 0
    assert result['max_score'] == 3
    assert result['recency_status'] == 'no_experience'
    assert result['months_since_last'] is None
    assert result['most_recent_end_date'] is None


def test_single_job_current(scorer):
    """Single current job = 3 pts"""
    experience = [
        {
            'title': 'Engineer',
            'company': 'Tech Corp',
            'dates': '2020 - Present'
        }
    ]

    result = scorer.score(experience)

    assert result['score'] == 3


def test_single_job_old(scorer):
    """Single old job = 0 pts"""
    experience = [
        {
            'title': 'Engineer',
            'company': 'Old Corp',
            'dates': '2010 - 2015'
        }
    ]

    result = scorer.score(experience)

    assert result['score'] == 0


def test_missing_dates_field(scorer):
    """Job without dates field = skip that job"""
    experience = [
        {
            'title': 'Engineer',
            'company': 'Tech Corp'
            # No dates field
        },
        {
            'title': 'Developer',
            'company': 'Software Inc',
            'dates': '2020 - Present'
        }
    ]

    result = scorer.score(experience)

    # Should use the valid job
    assert result['score'] == 3
    assert result['recency_status'] == 'currently_employed'


def test_unparseable_dates(scorer):
    """Unparseable dates = skip that job"""
    experience = [
        {
            'title': 'Engineer',
            'company': 'Tech Corp',
            'dates': 'invalid date format'
        },
        {
            'title': 'Developer',
            'company': 'Software Inc',
            'dates': '2020 - Present'
        }
    ]

    result = scorer.score(experience)

    # Should use the valid job
    assert result['score'] == 3


def test_only_unparseable_dates(scorer):
    """All jobs have unparseable dates = 0 pts"""
    experience = [
        {
            'title': 'Engineer',
            'company': 'Tech Corp',
            'dates': 'some random text'
        }
    ]

    result = scorer.score(experience)

    assert result['score'] == 0
    assert result['recency_status'] == 'no_valid_dates'


def test_case_insensitive_present(scorer):
    """'Present' variations are case-insensitive"""
    test_cases = ['present', 'PRESENT', 'Present', 'pResEnT']

    for present_variation in test_cases:
        experience = [
            {
                'title': 'Engineer',
                'company': 'Tech Corp',
                'dates': f'2020 - {present_variation}'
            }
        ]

        result = scorer.score(experience)
        assert result['score'] == 3, f"Failed for variation: {present_variation}"


def test_now_keyword(scorer):
    """'Now' keyword = currently employed"""
    experience = [
        {
            'title': 'Engineer',
            'company': 'Tech Corp',
            'dates': '2020 - Now'
        }
    ]

    result = scorer.score(experience)

    assert result['score'] == 3
    assert result['recency_status'] == 'currently_employed'


def test_result_structure(scorer):
    """Result has all required fields"""
    experience = [
        {
            'title': 'Engineer',
            'company': 'Tech Corp',
            'dates': '2020 - Present'
        }
    ]

    result = scorer.score(experience)

    # Check all required fields
    assert 'score' in result
    assert 'max_score' in result
    assert 'recency_status' in result
    assert 'months_since_last' in result
    assert 'most_recent_end_date' in result
    assert 'details' in result

    assert result['max_score'] == 3


def test_whitespace_handling(scorer):
    """Handle extra whitespace in dates"""
    experience = [
        {
            'title': 'Engineer',
            'company': 'Tech Corp',
            'dates': '  2020  -  Present  '
        }
    ]

    result = scorer.score(experience)

    assert result['score'] == 3


def test_dash_variations(scorer):
    """Handle different dash types in date ranges"""
    dash_variations = [
        '2020 - Present',
        '2020 – Present',  # en dash
        '2020 — Present',  # em dash
        '2020-Present',
        '2020- Present',
        '2020 -Present'
    ]

    for dates in dash_variations:
        experience = [
            {
                'title': 'Engineer',
                'company': 'Tech Corp',
                'dates': dates
            }
        ]

        result = scorer.score(experience)
        assert result['score'] == 3, f"Failed for dates: {dates}"
