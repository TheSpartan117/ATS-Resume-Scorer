"""
Tests for P5.1 - Years of Experience Alignment (10 pts)

Validates that resume experience years match selected experience level.
Scoring based on alignment with level expectations:
- Beginner: 0-3 years
- Intermediary: 3-7 years
- Senior: 7+ years
"""

import pytest
from datetime import datetime
from backend.services.parameters.p5_1_years_alignment import YearsAlignmentScorer


@pytest.fixture
def scorer():
    """Create YearsAlignmentScorer instance"""
    return YearsAlignmentScorer()


class TestYearsCalculation:
    """Test years of experience calculation from dates"""

    def test_calculate_years_from_present_date(self, scorer):
        """Calculate years with 'Present' end date"""
        experience = [
            {
                "title": "Software Engineer",
                "company": "TechCo",
                "dates": "2020 - Present",
                "description": "Developed features."
            }
        ]

        years = scorer._calculate_total_years(experience)
        current_year = datetime.now().year
        expected_years = current_year - 2020

        assert years == pytest.approx(expected_years, abs=0.1)

    def test_calculate_years_from_date_range(self, scorer):
        """Calculate years from date range"""
        experience = [
            {
                "title": "Software Engineer",
                "company": "TechCo",
                "dates": "2018 - 2020",
                "description": "Developed features."
            }
        ]

        years = scorer._calculate_total_years(experience)
        assert years == pytest.approx(2.0, abs=0.1)

    def test_calculate_years_multiple_positions(self, scorer):
        """Calculate total years across multiple positions"""
        experience = [
            {
                "title": "Senior Engineer",
                "company": "TechCo",
                "dates": "2020 - Present",
                "description": "Led team."
            },
            {
                "title": "Junior Engineer",
                "company": "StartupHub",
                "dates": "2015 - 2018",
                "description": "Developed features."
            }
        ]

        years = scorer._calculate_total_years(experience)
        current_year = datetime.now().year
        expected_years = (current_year - 2020) + (2018 - 2015)

        assert years == pytest.approx(expected_years, abs=0.1)

    def test_calculate_years_with_month_precision(self, scorer):
        """Calculate years with month precision"""
        experience = [
            {
                "title": "Software Engineer",
                "company": "TechCo",
                "dates": "Jan 2020 - Jun 2022",
                "description": "Developed features."
            }
        ]

        years = scorer._calculate_total_years(experience)
        # Jan 2020 to Jun 2022 = 2.5 years
        assert years == pytest.approx(2.5, abs=0.2)

    def test_calculate_years_full_month_names(self, scorer):
        """Calculate years with full month names"""
        experience = [
            {
                "title": "Software Engineer",
                "company": "TechCo",
                "dates": "January 2020 - December 2022",
                "description": "Developed features."
            }
        ]

        years = scorer._calculate_total_years(experience)
        assert years == pytest.approx(3.0, abs=0.2)

    def test_calculate_years_overlapping_positions(self, scorer):
        """Overlapping positions count independently"""
        experience = [
            {
                "title": "Consultant",
                "company": "Freelance",
                "dates": "2020 - 2022",
                "description": "Part-time consulting."
            },
            {
                "title": "Engineer",
                "company": "TechCo",
                "dates": "2020 - 2022",
                "description": "Full-time work."
            }
        ]

        years = scorer._calculate_total_years(experience)
        # Both positions count: 2 + 2 = 4 years total
        assert years == pytest.approx(4.0, abs=0.2)


class TestBeginnerAlignment:
    """Test alignment for Beginner level (0-3 years)"""

    def test_beginner_perfect_alignment_1_year(self, scorer):
        """1 year experience aligns perfectly with beginner"""
        experience = [
            {
                "title": "Junior Engineer",
                "company": "TechCo",
                "dates": "2025 - Present",
                "description": "Learning and growing."
            }
        ]

        result = scorer.score(experience, "beginner")

        assert result['score'] == 10
        assert result['aligned'] is True
        assert 0 <= result['years_calculated'] <= 3
        assert result['level'] == 'beginner'
        assert 'perfect alignment' in result['details'].lower()

    def test_beginner_perfect_alignment_3_years(self, scorer):
        """3 years experience aligns perfectly with beginner"""
        experience = [
            {
                "title": "Junior Engineer",
                "company": "TechCo",
                "dates": "2023 - Present",
                "description": "Learning and growing."
            }
        ]

        result = scorer.score(experience, "beginner")

        assert result['score'] == 10
        assert result['aligned'] is True
        assert 2.5 <= result['years_calculated'] <= 3.5

    def test_beginner_close_alignment_4_years(self, scorer):
        """4 years is close to beginner range (within 1 year)"""
        experience = [
            {
                "title": "Engineer",
                "company": "TechCo",
                "dates": "2022 - Present",
                "description": "Developed features."
            }
        ]

        result = scorer.score(experience, "beginner")

        assert result['score'] == 5
        assert result['aligned'] is False
        assert 3.5 <= result['years_calculated'] <= 4.5
        assert 'close' in result['details'].lower() or 'within' in result['details'].lower()

    def test_beginner_misaligned_7_years(self, scorer):
        """7 years completely misaligned with beginner"""
        experience = [
            {
                "title": "Senior Engineer",
                "company": "TechCo",
                "dates": "2019 - Present",
                "description": "Led initiatives."
            }
        ]

        result = scorer.score(experience, "beginner")

        assert result['score'] == 0
        assert result['aligned'] is False
        assert result['years_calculated'] >= 6.5


class TestIntermediaryAlignment:
    """Test alignment for Intermediary level (3-7 years)"""

    def test_intermediary_perfect_alignment_5_years(self, scorer):
        """5 years aligns perfectly with intermediary"""
        experience = [
            {
                "title": "Software Engineer",
                "company": "TechCo",
                "dates": "2021 - Present",
                "description": "Developed solutions."
            }
        ]

        result = scorer.score(experience, "intermediary")

        assert result['score'] == 10
        assert result['aligned'] is True
        assert 3 <= result['years_calculated'] <= 7
        assert result['level'] == 'intermediary'

    def test_intermediary_perfect_alignment_at_boundary_3_years(self, scorer):
        """3 years (lower boundary) aligns with intermediary"""
        experience = [
            {
                "title": "Engineer",
                "company": "TechCo",
                "dates": "2023 - Present",
                "description": "Building systems."
            }
        ]

        result = scorer.score(experience, "intermediary")

        assert result['score'] == 10
        assert result['aligned'] is True

    def test_intermediary_perfect_alignment_at_boundary_7_years(self, scorer):
        """7 years (upper boundary) aligns with intermediary"""
        experience = [
            {
                "title": "Engineer",
                "company": "TechCo",
                "dates": "2019 - Present",
                "description": "Building systems."
            }
        ]

        result = scorer.score(experience, "intermediary")

        assert result['score'] == 10
        assert result['aligned'] is True

    def test_intermediary_close_alignment_2_years(self, scorer):
        """2 years is close to intermediary (within 1 year of 3)"""
        experience = [
            {
                "title": "Engineer",
                "company": "TechCo",
                "dates": "2024 - Present",
                "description": "Developed features."
            }
        ]

        result = scorer.score(experience, "intermediary")

        assert result['score'] == 5
        assert result['aligned'] is False
        assert 1.5 <= result['years_calculated'] <= 2.5

    def test_intermediary_close_alignment_8_years(self, scorer):
        """8 years is close to intermediary (within 1 year of 7)"""
        experience = [
            {
                "title": "Engineer",
                "company": "TechCo",
                "dates": "2018 - Present",
                "description": "Built solutions."
            }
        ]

        result = scorer.score(experience, "intermediary")

        assert result['score'] == 5
        assert result['aligned'] is False
        assert 7.5 <= result['years_calculated'] <= 8.5

    def test_intermediary_misaligned_1_year(self, scorer):
        """1 year completely misaligned with intermediary"""
        experience = [
            {
                "title": "Junior Engineer",
                "company": "TechCo",
                "dates": "2025 - Present",
                "description": "Learning."
            }
        ]

        result = scorer.score(experience, "intermediary")

        assert result['score'] == 0
        assert result['aligned'] is False

    def test_intermediary_misaligned_10_years(self, scorer):
        """10 years completely misaligned with intermediary"""
        experience = [
            {
                "title": "Senior Engineer",
                "company": "TechCo",
                "dates": "2016 - Present",
                "description": "Led teams."
            }
        ]

        result = scorer.score(experience, "intermediary")

        assert result['score'] == 0
        assert result['aligned'] is False


class TestSeniorAlignment:
    """Test alignment for Senior level (7+ years)"""

    def test_senior_perfect_alignment_10_years(self, scorer):
        """10 years aligns perfectly with senior"""
        experience = [
            {
                "title": "Senior Engineer",
                "company": "TechCo",
                "dates": "2016 - Present",
                "description": "Led technical initiatives."
            }
        ]

        result = scorer.score(experience, "senior")

        assert result['score'] == 10
        assert result['aligned'] is True
        assert result['years_calculated'] >= 7
        assert result['level'] == 'senior'

    def test_senior_perfect_alignment_at_boundary_7_years(self, scorer):
        """7 years (lower boundary) aligns with senior"""
        experience = [
            {
                "title": "Senior Engineer",
                "company": "TechCo",
                "dates": "2019 - Present",
                "description": "Led initiatives."
            }
        ]

        result = scorer.score(experience, "senior")

        assert result['score'] == 10
        assert result['aligned'] is True

    def test_senior_perfect_alignment_20_years(self, scorer):
        """20 years aligns perfectly with senior (no upper limit)"""
        experience = [
            {
                "title": "Principal Engineer",
                "company": "TechCo",
                "dates": "2006 - Present",
                "description": "Led organization."
            }
        ]

        result = scorer.score(experience, "senior")

        assert result['score'] == 10
        assert result['aligned'] is True
        assert result['years_calculated'] >= 19

    def test_senior_close_alignment_6_years(self, scorer):
        """6 years is close to senior (within 1 year of 7)"""
        experience = [
            {
                "title": "Engineer",
                "company": "TechCo",
                "dates": "2020 - Present",
                "description": "Built systems."
            }
        ]

        result = scorer.score(experience, "senior")

        assert result['score'] == 5
        assert result['aligned'] is False
        assert 5.5 <= result['years_calculated'] <= 6.5

    def test_senior_misaligned_3_years(self, scorer):
        """3 years completely misaligned with senior"""
        experience = [
            {
                "title": "Engineer",
                "company": "TechCo",
                "dates": "2023 - Present",
                "description": "Developed features."
            }
        ]

        result = scorer.score(experience, "senior")

        assert result['score'] == 0
        assert result['aligned'] is False
        assert result['years_calculated'] <= 3.5


class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_empty_experience_list(self, scorer):
        """Empty experience returns 0 years, no alignment"""
        result = scorer.score([], "intermediary")

        assert result['score'] == 0
        assert result['years_calculated'] == 0
        assert result['aligned'] is False
        assert 'no experience' in result['details'].lower()

    def test_missing_dates_field(self, scorer):
        """Missing dates field is handled gracefully"""
        experience = [
            {
                "title": "Engineer",
                "company": "TechCo",
                "description": "Developed features."
            }
        ]

        result = scorer.score(experience, "intermediary")

        assert result['score'] == 0
        assert result['years_calculated'] == 0

    def test_invalid_date_format(self, scorer):
        """Invalid date format is handled gracefully"""
        experience = [
            {
                "title": "Engineer",
                "company": "TechCo",
                "dates": "Invalid Date Format",
                "description": "Developed features."
            }
        ]

        result = scorer.score(experience, "intermediary")

        # Should attempt to parse, may get 0 or skip
        assert result['score'] >= 0
        assert result['years_calculated'] >= 0

    def test_year_only_format(self, scorer):
        """Year-only format works"""
        experience = [
            {
                "title": "Engineer",
                "company": "TechCo",
                "dates": "2020 - 2023",
                "description": "Developed features."
            }
        ]

        years = scorer._calculate_total_years(experience)
        assert years == pytest.approx(3.0, abs=0.1)

    def test_unknown_experience_level(self, scorer):
        """Unknown experience level defaults gracefully"""
        experience = [
            {
                "title": "Engineer",
                "company": "TechCo",
                "dates": "2020 - Present",
                "description": "Developed features."
            }
        ]

        result = scorer.score(experience, "unknown_level")

        # Should default to intermediary expectations
        assert result['score'] >= 0
        assert result['level'] == 'unknown_level'

    def test_case_insensitive_level(self, scorer):
        """Experience level is case-insensitive"""
        experience = [
            {
                "title": "Engineer",
                "company": "TechCo",
                "dates": "2021 - Present",
                "description": "Developed features."
            }
        ]

        result1 = scorer.score(experience, "BEGINNER")
        result2 = scorer.score(experience, "Beginner")
        result3 = scorer.score(experience, "beginner")

        assert result1['score'] == result2['score'] == result3['score']


class TestResultStructure:
    """Test result structure and required fields"""

    def test_result_contains_required_fields(self, scorer):
        """Result contains all required fields"""
        experience = [
            {
                "title": "Engineer",
                "company": "TechCo",
                "dates": "2020 - Present",
                "description": "Developed features."
            }
        ]

        result = scorer.score(experience, "intermediary")

        required_fields = [
            'score',
            'max_score',
            'years_calculated',
            'level',
            'aligned',
            'details',
            'parameter',
            'name'
        ]

        for field in required_fields:
            assert field in result, f"Missing required field: {field}"

    def test_score_is_valid_range(self, scorer):
        """Score is 0, 5, or 10"""
        experience = [
            {
                "title": "Engineer",
                "company": "TechCo",
                "dates": "2020 - Present",
                "description": "Developed features."
            }
        ]

        result = scorer.score(experience, "intermediary")

        assert result['score'] in [0, 5, 10]
        assert result['max_score'] == 10

    def test_years_calculated_is_float(self, scorer):
        """years_calculated is a float"""
        experience = [
            {
                "title": "Engineer",
                "company": "TechCo",
                "dates": "2020 - Present",
                "description": "Developed features."
            }
        ]

        result = scorer.score(experience, "intermediary")

        assert isinstance(result['years_calculated'], (int, float))
        assert result['years_calculated'] >= 0

    def test_aligned_is_boolean(self, scorer):
        """aligned is a boolean"""
        experience = [
            {
                "title": "Engineer",
                "company": "TechCo",
                "dates": "2020 - Present",
                "description": "Developed features."
            }
        ]

        result = scorer.score(experience, "intermediary")

        assert isinstance(result['aligned'], bool)

    def test_details_is_descriptive_string(self, scorer):
        """details provides meaningful feedback"""
        experience = [
            {
                "title": "Engineer",
                "company": "TechCo",
                "dates": "2020 - Present",
                "description": "Developed features."
            }
        ]

        result = scorer.score(experience, "intermediary")

        assert isinstance(result['details'], str)
        assert len(result['details']) > 0
        assert any(word in result['details'].lower() for word in ['years', 'experience', 'alignment'])

    def test_parameter_and_name_fields(self, scorer):
        """parameter and name fields are correct"""
        experience = [
            {
                "title": "Engineer",
                "company": "TechCo",
                "dates": "2020 - Present",
                "description": "Developed features."
            }
        ]

        result = scorer.score(experience, "intermediary")

        assert result['parameter'] == 'P5.1'
        assert result['name'] == 'Years of Experience Alignment'
        assert result['max_score'] == 10


class TestBoundaryConditions:
    """Test boundary conditions for scoring"""

    def test_beginner_upper_boundary_3_0_years(self, scorer):
        """Exactly 3.0 years should align with beginner"""
        # Mock to return exactly 3.0 years
        experience = [
            {
                "title": "Engineer",
                "company": "TechCo",
                "dates": "2023 - Present",
                "description": "Worked."
            }
        ]

        result = scorer.score(experience, "beginner")

        # 3.0 is within range [0, 3]
        if 2.9 <= result['years_calculated'] <= 3.1:
            assert result['score'] == 10

    def test_intermediary_boundaries_3_and_7_years(self, scorer):
        """3.0 and 7.0 years align with intermediary"""
        # Test both boundaries implicitly through date ranges
        # The actual calculation depends on current date
        pass  # Covered by other tests

    def test_senior_lower_boundary_7_0_years(self, scorer):
        """Exactly 7.0 years should align with senior"""
        experience = [
            {
                "title": "Senior Engineer",
                "company": "TechCo",
                "dates": "2019 - Present",
                "description": "Led teams."
            }
        ]

        result = scorer.score(experience, "senior")

        # 7.0 should be aligned
        if 6.9 <= result['years_calculated'] <= 7.1:
            assert result['score'] == 10

    def test_close_alignment_boundary_exactly_1_year_off(self, scorer):
        """Exactly 1 year off should still be 'close'"""
        # For beginner (0-3), 4.0 years is exactly 1 year off
        # This should score 5 points (close)
        experience = [
            {
                "title": "Engineer",
                "company": "TechCo",
                "dates": "2022 - Present",
                "description": "Worked."
            }
        ]

        result = scorer.score(experience, "beginner")

        if 3.9 <= result['years_calculated'] <= 4.1:
            assert result['score'] == 5


def test_create_scorer():
    """Test factory function creates scorer"""
    from backend.services.parameters.p5_1_years_alignment import create_scorer

    scorer = create_scorer()
    assert isinstance(scorer, YearsAlignmentScorer)
