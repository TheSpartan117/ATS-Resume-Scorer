"""
Tests for P6.4 - Date/Formatting Errors Penalty (-2 pts max)

Penalizes date and formatting inconsistencies in experience section.
"""

import pytest
from backend.services.parameters.p6_4_formatting_errors import DateFormattingScorer


@pytest.fixture
def scorer():
    """Create DateFormattingScorer instance"""
    return DateFormattingScorer()


class TestDateFormattingScorerPerfectFormatting:
    """Test cases with perfect date formatting (0 penalty)"""

    def test_consistent_month_year_format(self, scorer):
        """Consistent 'Month YYYY' format = 0 penalty"""
        experience = [
            {"dates": "Jan 2020 - Mar 2022"},
            {"dates": "Apr 2018 - Dec 2019"},
            {"dates": "May 2016 - Present"}
        ]
        result = scorer.score(experience)

        assert result['penalty'] == 0
        assert result['has_invalid_dates'] is False
        assert result['has_inconsistent_formatting'] is False
        assert len(result['error_types']) == 0

    def test_consistent_yyyy_mm_format(self, scorer):
        """Consistent 'YYYY-MM' format = 0 penalty"""
        experience = [
            {"dates": "2020-01 - 2022-03"},
            {"dates": "2018-04 - 2019-12"},
            {"dates": "2016-05 - Present"}
        ]
        result = scorer.score(experience)

        assert result['penalty'] == 0
        assert result['has_invalid_dates'] is False
        assert result['has_inconsistent_formatting'] is False

    def test_consistent_mm_yyyy_format(self, scorer):
        """Consistent 'MM/YYYY' format = 0 penalty"""
        experience = [
            {"dates": "01/2020 - 03/2022"},
            {"dates": "04/2018 - 12/2019"},
            {"dates": "05/2016 - Present"}
        ]
        result = scorer.score(experience)

        assert result['penalty'] == 0
        assert result['has_invalid_dates'] is False
        assert result['has_inconsistent_formatting'] is False

    def test_year_only_format(self, scorer):
        """Consistent year-only format = 0 penalty"""
        experience = [
            {"dates": "2020 - 2022"},
            {"dates": "2018 - 2019"},
            {"dates": "2016 - Present"}
        ]
        result = scorer.score(experience)

        assert result['penalty'] == 0
        assert result['has_invalid_dates'] is False
        assert result['has_inconsistent_formatting'] is False

    def test_present_keyword(self, scorer):
        """'Present' as end date is valid = 0 penalty"""
        experience = [
            {"dates": "Jan 2020 - Present"},
            {"dates": "Mar 2018 - Dec 2019"}
        ]
        result = scorer.score(experience)

        assert result['penalty'] == 0

    def test_current_keyword(self, scorer):
        """'Current' as end date is valid = 0 penalty"""
        experience = [
            {"dates": "Jan 2020 - Current"},
            {"dates": "Mar 2018 - Dec 2019"}
        ]
        result = scorer.score(experience)

        assert result['penalty'] == 0


class TestDateFormattingScorerInvalidDates:
    """Test cases with invalid dates (-1 pt)"""

    def test_invalid_month_13(self, scorer):
        """Month 13 is invalid = -1 pt"""
        experience = [
            {"dates": "2020-13 - 2021-01"}
        ]
        result = scorer.score(experience)

        assert result['penalty'] == -1
        assert result['has_invalid_dates'] is True
        assert 'invalid_dates' in result['error_types']
        assert len(result['error_details']['invalid_dates']) > 0

    def test_invalid_month_00(self, scorer):
        """Month 00 is invalid = -1 pt"""
        experience = [
            {"dates": "2020-00 - 2021-01"}
        ]
        result = scorer.score(experience)

        assert result['penalty'] == -1
        assert result['has_invalid_dates'] is True

    def test_invalid_february_31(self, scorer):
        """Feb 31 is invalid = -1 pt"""
        experience = [
            {"dates": "Feb 31 2020 - Mar 2021"}
        ]
        result = scorer.score(experience)

        assert result['penalty'] == -1
        assert result['has_invalid_dates'] is True

    def test_invalid_day_32(self, scorer):
        """Day 32 is invalid = -1 pt"""
        experience = [
            {"dates": "32/01/2020 - 15/03/2021"}
        ]
        result = scorer.score(experience)

        assert result['penalty'] == -1
        assert result['has_invalid_dates'] is True

    def test_invalid_day_00(self, scorer):
        """Day 00 is invalid = -1 pt"""
        experience = [
            {"dates": "00/01/2020 - 15/03/2021"}
        ]
        result = scorer.score(experience)

        assert result['penalty'] == -1
        assert result['has_invalid_dates'] is True

    def test_multiple_invalid_dates_still_one_penalty(self, scorer):
        """Multiple invalid dates still only -1 pt total"""
        experience = [
            {"dates": "2020-13 - 2021-01"},
            {"dates": "Feb 31 2019 - Mar 2020"},
            {"dates": "00/05/2018 - 12/06/2019"}
        ]
        result = scorer.score(experience)

        assert result['penalty'] == -1
        assert result['has_invalid_dates'] is True
        assert len(result['error_details']['invalid_dates']) >= 3


class TestDateFormattingScorerInconsistentFormatting:
    """Test cases with inconsistent formatting (-1 pt)"""

    def test_mixing_month_year_and_yyyy_mm(self, scorer):
        """Mixing 'Jan 2020' with '2020-02' = -1 pt"""
        experience = [
            {"dates": "Jan 2020 - Mar 2022"},
            {"dates": "2018-04 - 2019-12"}
        ]
        result = scorer.score(experience)

        assert result['penalty'] == -1
        assert result['has_inconsistent_formatting'] is True
        assert 'inconsistent_formatting' in result['error_types']
        assert len(result['error_details']['inconsistent_formatting']) > 0

    def test_mixing_month_year_and_mm_yyyy(self, scorer):
        """Mixing 'Jan 2020' with '01/2020' = -1 pt"""
        experience = [
            {"dates": "Jan 2020 - Mar 2022"},
            {"dates": "01/2018 - 12/2019"}
        ]
        result = scorer.score(experience)

        assert result['penalty'] == -1
        assert result['has_inconsistent_formatting'] is True

    def test_mixing_yyyy_mm_and_mm_yyyy(self, scorer):
        """Mixing '2020-01' with '01/2020' = -1 pt"""
        experience = [
            {"dates": "2020-01 - 2022-03"},
            {"dates": "01/2018 - 12/2019"}
        ]
        result = scorer.score(experience)

        assert result['penalty'] == -1
        assert result['has_inconsistent_formatting'] is True

    def test_mixing_year_only_with_month_year(self, scorer):
        """Mixing '2020' with 'Jan 2020' = -1 pt"""
        experience = [
            {"dates": "2020 - 2022"},
            {"dates": "Jan 2018 - Dec 2019"}
        ]
        result = scorer.score(experience)

        assert result['penalty'] == -1
        assert result['has_inconsistent_formatting'] is True

    def test_multiple_format_variations(self, scorer):
        """Multiple format variations still -1 pt total"""
        experience = [
            {"dates": "Jan 2020 - Mar 2022"},
            {"dates": "2018-04 - 2019-12"},
            {"dates": "01/2016 - 05/2017"},
            {"dates": "2014 - 2015"}
        ]
        result = scorer.score(experience)

        assert result['penalty'] == -1
        assert result['has_inconsistent_formatting'] is True


class TestDateFormattingScorerBothErrors:
    """Test cases with both invalid dates and inconsistent formatting"""

    def test_invalid_dates_and_inconsistent_formatting(self, scorer):
        """Both errors = -2 pts (capped)"""
        experience = [
            {"dates": "Jan 2020 - 2022-13"},  # Invalid month + mixed format
            {"dates": "2018-04 - 2019-12"}    # Different format
        ]
        result = scorer.score(experience)

        assert result['penalty'] == -2
        assert result['has_invalid_dates'] is True
        assert result['has_inconsistent_formatting'] is True
        assert len(result['error_types']) == 2

    def test_penalty_capped_at_minus_two(self, scorer):
        """Penalty capped at -2 pts even with many errors"""
        experience = [
            {"dates": "2020-13 - Feb 31 2022"},  # Multiple invalid dates
            {"dates": "01/2018 - 12/2019"},      # Different format
            {"dates": "Jan 2016 - Present"},     # Another format
            {"dates": "2014-00 - 2015-15"}       # More invalid dates
        ]
        result = scorer.score(experience)

        assert result['penalty'] == -2
        assert result['penalty'] >= -2  # Never goes below -2


class TestDateFormattingScorerMissingDates:
    """Test cases with missing or empty dates"""

    def test_missing_dates_field(self, scorer):
        """Missing dates field = 0 penalty (no data to penalize)"""
        experience = [
            {"title": "Software Engineer", "company": "Tech Corp"}
        ]
        result = scorer.score(experience)

        assert result['penalty'] == 0

    def test_empty_dates_string(self, scorer):
        """Empty dates string = 0 penalty"""
        experience = [
            {"dates": ""},
            {"dates": "Jan 2020 - Present"}
        ]
        result = scorer.score(experience)

        assert result['penalty'] == 0

    def test_none_dates_value(self, scorer):
        """None dates value = 0 penalty"""
        experience = [
            {"dates": None},
            {"dates": "Jan 2020 - Present"}
        ]
        result = scorer.score(experience)

        assert result['penalty'] == 0

    def test_all_missing_dates(self, scorer):
        """All missing dates = 0 penalty"""
        experience = [
            {"title": "Software Engineer"},
            {"title": "Product Manager"}
        ]
        result = scorer.score(experience)

        assert result['penalty'] == 0


class TestDateFormattingScorerEdgeCases:
    """Test edge cases and special scenarios"""

    def test_empty_experience_list(self, scorer):
        """Empty experience list = 0 penalty"""
        result = scorer.score([])

        assert result['penalty'] == 0
        assert result['has_invalid_dates'] is False
        assert result['has_inconsistent_formatting'] is False

    def test_single_experience_entry(self, scorer):
        """Single entry cannot be inconsistent = max -1 pt for invalid dates"""
        experience = [
            {"dates": "2020-13 - 2021-01"}
        ]
        result = scorer.score(experience)

        assert result['penalty'] >= -1
        assert result['has_invalid_dates'] is True
        assert result['has_inconsistent_formatting'] is False

    def test_whitespace_handling(self, scorer):
        """Extra whitespace doesn't cause issues"""
        experience = [
            {"dates": "  Jan 2020  -  Mar 2022  "},
            {"dates": " Apr 2018  - Dec 2019"}
        ]
        result = scorer.score(experience)

        assert result['penalty'] == 0

    def test_case_insensitive_months(self, scorer):
        """Month names are case insensitive"""
        experience = [
            {"dates": "JAN 2020 - MAR 2022"},
            {"dates": "apr 2018 - dec 2019"},
            {"dates": "May 2016 - Present"}
        ]
        result = scorer.score(experience)

        assert result['penalty'] == 0

    def test_abbreviated_vs_full_month_names(self, scorer):
        """Abbreviated and full month names are both valid"""
        experience = [
            {"dates": "Jan 2020 - Mar 2022"},
            {"dates": "January 2018 - December 2019"}
        ]
        result = scorer.score(experience)

        # Both are valid month formats, so should be consistent
        assert result['has_invalid_dates'] is False

    def test_date_range_format_variations(self, scorer):
        """Different separators (-, to, –) are handled"""
        experience = [
            {"dates": "Jan 2020 - Mar 2022"},
            {"dates": "Apr 2018 to Dec 2019"},
            {"dates": "May 2016 – Present"}  # em dash
        ]
        result = scorer.score(experience)

        # These are same format, just different separators
        assert result['penalty'] == 0

    def test_ongoing_role_variations(self, scorer):
        """'Present', 'Current', 'Now' are all valid"""
        experience = [
            {"dates": "Jan 2020 - Present"},
            {"dates": "Apr 2018 - Current"},
            {"dates": "May 2016 - Now"}
        ]
        result = scorer.score(experience)

        assert result['penalty'] == 0

    def test_partial_dates_with_full_dates(self, scorer):
        """Mixing month-year with day-month-year formats"""
        experience = [
            {"dates": "Jan 2020 - Mar 2022"},
            {"dates": "15 Apr 2018 - 30 Dec 2019"}
        ]
        result = scorer.score(experience)

        # Different granularity is inconsistent
        assert result['has_inconsistent_formatting'] is True


class TestDateFormattingScorerResultStructure:
    """Test result structure and completeness"""

    def test_result_contains_required_fields(self, scorer):
        """Result contains all required fields"""
        experience = [
            {"dates": "Jan 2020 - Present"}
        ]
        result = scorer.score(experience)

        required_fields = [
            'penalty',
            'error_types',
            'error_details',
            'has_invalid_dates',
            'has_inconsistent_formatting',
            'parameter',
            'name',
            'max_penalty'
        ]

        for field in required_fields:
            assert field in result, f"Missing required field: {field}"

    def test_penalty_is_negative_or_zero(self, scorer):
        """Penalty is always negative or zero"""
        experience = [
            {"dates": "2020-13 - 2021-01"}
        ]
        result = scorer.score(experience)

        assert result['penalty'] <= 0

    def test_penalty_within_bounds(self, scorer):
        """Penalty is between -2 and 0"""
        experience = [
            {"dates": "2020-13 - Feb 31 2022"},
            {"dates": "01/2018 - 12/2019"},
            {"dates": "Jan 2016 - Present"}
        ]
        result = scorer.score(experience)

        assert -2 <= result['penalty'] <= 0

    def test_error_types_is_list(self, scorer):
        """error_types is a list"""
        experience = [
            {"dates": "Jan 2020 - Present"}
        ]
        result = scorer.score(experience)

        assert isinstance(result['error_types'], list)

    def test_error_details_is_dict(self, scorer):
        """error_details is a dictionary"""
        experience = [
            {"dates": "Jan 2020 - Present"}
        ]
        result = scorer.score(experience)

        assert isinstance(result['error_details'], dict)

    def test_error_details_structure(self, scorer):
        """error_details has correct structure"""
        experience = [
            {"dates": "2020-13 - 2021-01"},
            {"dates": "Jan 2018 - Present"}
        ]
        result = scorer.score(experience)

        assert 'invalid_dates' in result['error_details']
        assert 'inconsistent_formatting' in result['error_details']
        assert isinstance(result['error_details']['invalid_dates'], list)
        assert isinstance(result['error_details']['inconsistent_formatting'], list)

    def test_metadata_fields_present(self, scorer):
        """Metadata fields are present"""
        experience = [
            {"dates": "Jan 2020 - Present"}
        ]
        result = scorer.score(experience)

        assert result['parameter'] == 'P6.4'
        assert result['name'] == 'Date/Formatting Errors'
        assert result['max_penalty'] == -2


class TestDateFormattingScorerComplexScenarios:
    """Test complex real-world scenarios"""

    def test_realistic_perfect_resume(self, scorer):
        """Realistic perfect resume with consistent formatting"""
        experience = [
            {
                "title": "Senior Product Manager",
                "company": "Tech Corp",
                "dates": "Jan 2020 - Present"
            },
            {
                "title": "Product Manager",
                "company": "StartUp Inc",
                "dates": "Jun 2018 - Dec 2019"
            },
            {
                "title": "Associate Product Manager",
                "company": "Big Company",
                "dates": "Aug 2016 - May 2018"
            }
        ]
        result = scorer.score(experience)

        assert result['penalty'] == 0
        assert len(result['error_types']) == 0

    def test_realistic_inconsistent_resume(self, scorer):
        """Realistic resume with mixed date formats"""
        experience = [
            {
                "title": "Senior Product Manager",
                "company": "Tech Corp",
                "dates": "Jan 2020 - Present"
            },
            {
                "title": "Product Manager",
                "company": "StartUp Inc",
                "dates": "2018-06 - 2019-12"
            },
            {
                "title": "Associate Product Manager",
                "company": "Big Company",
                "dates": "08/2016 - 05/2018"
            }
        ]
        result = scorer.score(experience)

        assert result['penalty'] == -1
        assert result['has_inconsistent_formatting'] is True

    def test_realistic_problematic_resume(self, scorer):
        """Realistic resume with both invalid dates and inconsistent formatting"""
        experience = [
            {
                "title": "Senior Product Manager",
                "company": "Tech Corp",
                "dates": "Jan 2020 - Present"
            },
            {
                "title": "Product Manager",
                "company": "StartUp Inc",
                "dates": "2018-13 - 2019-12"  # Invalid month
            },
            {
                "title": "Associate Product Manager",
                "company": "Big Company",
                "dates": "08/2016 - 05/2018"  # Different format
            }
        ]
        result = scorer.score(experience)

        assert result['penalty'] == -2
        assert result['has_invalid_dates'] is True
        assert result['has_inconsistent_formatting'] is True
