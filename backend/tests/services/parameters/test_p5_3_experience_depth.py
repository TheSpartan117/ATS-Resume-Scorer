"""
Tests for P5.3: Experience Depth (2 points)

Tests experience entry depth validation with level-specific minimums.
Validates that resume has sufficient detailed experience entries.
"""

import pytest
from backend.services.parameters.p5_3_experience_depth import ExperienceDepthScorer


class TestExperienceDepthScorer:
    """Test suite for P5.3 experience depth scoring"""

    @pytest.fixture
    def scorer(self):
        """Create scorer instance"""
        return ExperienceDepthScorer()

    # ========================================================================
    # HELPER METHOD: Create complete experience entry
    # ========================================================================

    def _create_complete_entry(
        self,
        title="Software Engineer",
        company="Tech Corp",
        start_date="Jan 2020",
        end_date="Dec 2021",
        bullets=None
    ):
        """Create a complete experience entry with all required components"""
        if bullets is None:
            bullets = [
                "Developed REST API serving 100K requests/day",
                "Led team of 5 engineers"
            ]

        return {
            'title': title,
            'company': company,
            'startDate': start_date,
            'endDate': end_date,
            'achievements': bullets,
            'description': ' '.join(bullets)  # description optional but can be present
        }

    def _create_incomplete_entry(self, **kwargs):
        """Create an incomplete experience entry (missing required fields)"""
        return kwargs

    # ========================================================================
    # BEGINNER LEVEL TESTS (≥2 entries = 2pts)
    # ========================================================================

    def test_beginner_minimum_entries_exactly_2(self, scorer):
        """Beginner: exactly 2 complete entries = 2 points"""
        experiences = [
            self._create_complete_entry(title="Junior Developer", company="Company A"),
            self._create_complete_entry(title="Intern", company="Company B")
        ]

        result = scorer.score(experiences, 'beginner')

        assert result['score'] == 2
        assert result['max_score'] == 2
        assert result['entry_count'] == 2
        assert result['level'] == 'beginner'
        assert result['meets_minimum'] is True
        assert 'minimum' in result['details'].lower()

    def test_beginner_above_minimum_3_entries(self, scorer):
        """Beginner: 3 complete entries = 2 points (exceeds minimum)"""
        experiences = [
            self._create_complete_entry(title="Developer", company="A"),
            self._create_complete_entry(title="Intern", company="B"),
            self._create_complete_entry(title="Contractor", company="C")
        ]

        result = scorer.score(experiences, 'beginner')

        assert result['score'] == 2
        assert result['entry_count'] == 3
        assert result['meets_minimum'] is True

    def test_beginner_below_minimum_1_entry(self, scorer):
        """Beginner: only 1 complete entry = 0 points"""
        experiences = [
            self._create_complete_entry(title="Developer", company="Tech Corp")
        ]

        result = scorer.score(experiences, 'beginner')

        assert result['score'] == 0
        assert result['entry_count'] == 1
        assert result['meets_minimum'] is False
        assert '2' in result['details']  # Should mention required minimum

    def test_beginner_zero_entries(self, scorer):
        """Beginner: 0 complete entries = 0 points"""
        result = scorer.score([], 'beginner')

        assert result['score'] == 0
        assert result['entry_count'] == 0
        assert result['meets_minimum'] is False

    # ========================================================================
    # INTERMEDIARY LEVEL TESTS (≥3 entries = 2pts)
    # ========================================================================

    def test_intermediary_minimum_entries_exactly_3(self, scorer):
        """Intermediary: exactly 3 complete entries = 2 points"""
        experiences = [
            self._create_complete_entry(title="Senior Developer", company="A"),
            self._create_complete_entry(title="Developer", company="B"),
            self._create_complete_entry(title="Junior Developer", company="C")
        ]

        result = scorer.score(experiences, 'intermediary')

        assert result['score'] == 2
        assert result['max_score'] == 2
        assert result['entry_count'] == 3
        assert result['level'] == 'intermediary'
        assert result['meets_minimum'] is True

    def test_intermediary_above_minimum_5_entries(self, scorer):
        """Intermediary: 5 complete entries = 2 points (exceeds minimum)"""
        experiences = [
            self._create_complete_entry(title=f"Developer {i}", company=f"Company {i}")
            for i in range(5)
        ]

        result = scorer.score(experiences, 'intermediary')

        assert result['score'] == 2
        assert result['entry_count'] == 5
        assert result['meets_minimum'] is True

    def test_intermediary_below_minimum_2_entries(self, scorer):
        """Intermediary: only 2 complete entries = 0 points"""
        experiences = [
            self._create_complete_entry(title="Developer", company="A"),
            self._create_complete_entry(title="Engineer", company="B")
        ]

        result = scorer.score(experiences, 'intermediary')

        assert result['score'] == 0
        assert result['entry_count'] == 2
        assert result['meets_minimum'] is False
        assert '3' in result['details']  # Should mention required minimum

    # ========================================================================
    # SENIOR LEVEL TESTS (≥4 entries = 2pts)
    # ========================================================================

    def test_senior_minimum_entries_exactly_4(self, scorer):
        """Senior: exactly 4 complete entries = 2 points"""
        experiences = [
            self._create_complete_entry(title="Engineering Manager", company="A"),
            self._create_complete_entry(title="Senior Engineer", company="B"),
            self._create_complete_entry(title="Tech Lead", company="C"),
            self._create_complete_entry(title="Developer", company="D")
        ]

        result = scorer.score(experiences, 'senior')

        assert result['score'] == 2
        assert result['max_score'] == 2
        assert result['entry_count'] == 4
        assert result['level'] == 'senior'
        assert result['meets_minimum'] is True

    def test_senior_above_minimum_6_entries(self, scorer):
        """Senior: 6 complete entries = 2 points (exceeds minimum)"""
        experiences = [
            self._create_complete_entry(title=f"Role {i}", company=f"Company {i}")
            for i in range(6)
        ]

        result = scorer.score(experiences, 'senior')

        assert result['score'] == 2
        assert result['entry_count'] == 6
        assert result['meets_minimum'] is True

    def test_senior_below_minimum_3_entries(self, scorer):
        """Senior: only 3 complete entries = 0 points"""
        experiences = [
            self._create_complete_entry(title="Manager", company="A"),
            self._create_complete_entry(title="Lead", company="B"),
            self._create_complete_entry(title="Engineer", company="C")
        ]

        result = scorer.score(experiences, 'senior')

        assert result['score'] == 0
        assert result['entry_count'] == 3
        assert result['meets_minimum'] is False
        assert '4' in result['details']  # Should mention required minimum

    def test_senior_below_minimum_1_entry(self, scorer):
        """Senior: only 1 complete entry = 0 points"""
        experiences = [
            self._create_complete_entry(title="CTO", company="Tech Corp")
        ]

        result = scorer.score(experiences, 'senior')

        assert result['score'] == 0
        assert result['entry_count'] == 1
        assert result['meets_minimum'] is False

    # ========================================================================
    # MISSING ENTRY COMPONENTS TESTS
    # ========================================================================

    def test_missing_company_not_counted(self, scorer):
        """Entry missing company should not count as complete"""
        experiences = [
            self._create_complete_entry(title="Engineer", company="A"),
            self._create_incomplete_entry(  # Missing company
                title="Developer",
                startDate="Jan 2020",
                endDate="Dec 2020",
                achievements=["Built features"]
            )
        ]

        result = scorer.score(experiences, 'beginner')

        assert result['entry_count'] == 1  # Only first entry counts
        assert result['score'] == 0  # Below minimum for beginner (needs 2)

    def test_missing_title_not_counted(self, scorer):
        """Entry missing title should not count as complete"""
        experiences = [
            self._create_complete_entry(title="Engineer", company="A"),
            self._create_incomplete_entry(  # Missing title
                company="Tech Corp",
                startDate="Jan 2020",
                endDate="Dec 2020",
                achievements=["Built features"]
            )
        ]

        result = scorer.score(experiences, 'beginner')

        assert result['entry_count'] == 1
        assert result['score'] == 0

    def test_missing_dates_not_counted(self, scorer):
        """Entry missing dates should not count as complete"""
        experiences = [
            self._create_complete_entry(title="Engineer", company="A"),
            self._create_complete_entry(title="Developer", company="B"),
            self._create_incomplete_entry(  # Missing dates
                title="Intern",
                company="C",
                achievements=["Did work"]
            )
        ]

        result = scorer.score(experiences, 'beginner')

        assert result['entry_count'] == 2  # Only first two count
        assert result['score'] == 2  # Meets beginner minimum

    def test_missing_start_date_only_not_counted(self, scorer):
        """Entry missing only start date should not count"""
        experiences = [
            self._create_complete_entry(title="Engineer", company="A"),
            self._create_incomplete_entry(
                title="Developer",
                company="B",
                endDate="Dec 2020",  # Has end date but no start date
                achievements=["Built features"]
            )
        ]

        result = scorer.score(experiences, 'beginner')

        assert result['entry_count'] == 1
        assert result['score'] == 0

    def test_missing_end_date_only_not_counted(self, scorer):
        """Entry missing only end date should not count"""
        experiences = [
            self._create_complete_entry(title="Engineer", company="A"),
            self._create_incomplete_entry(
                title="Developer",
                company="B",
                startDate="Jan 2020",  # Has start date but no end date
                achievements=["Built features"]
            )
        ]

        result = scorer.score(experiences, 'beginner')

        assert result['entry_count'] == 1
        assert result['score'] == 0

    def test_missing_bullets_and_description_not_counted(self, scorer):
        """Entry missing both bullets and description should not count"""
        experiences = [
            self._create_complete_entry(title="Engineer", company="A"),
            self._create_incomplete_entry(  # Missing bullets and description
                title="Developer",
                company="B",
                startDate="Jan 2020",
                endDate="Dec 2020"
            )
        ]

        result = scorer.score(experiences, 'beginner')

        assert result['entry_count'] == 1
        assert result['score'] == 0

    def test_empty_bullets_not_counted(self, scorer):
        """Entry with empty bullets list should not count"""
        experiences = [
            self._create_complete_entry(title="Engineer", company="A"),
            {
                'title': "Developer",
                'company': "B",
                'startDate': "Jan 2020",
                'endDate': "Dec 2020",
                'achievements': []  # Empty list
            }
        ]

        result = scorer.score(experiences, 'beginner')

        assert result['entry_count'] == 1
        assert result['score'] == 0

    def test_has_description_but_no_bullets(self, scorer):
        """Entry with description but no bullets should count as complete"""
        experiences = [
            self._create_complete_entry(title="Engineer", company="A"),
            {
                'title': "Developer",
                'company': "B",
                'startDate': "Jan 2020",
                'endDate': "Dec 2020",
                'description': "Developed web applications and APIs"  # Has description
            }
        ]

        result = scorer.score(experiences, 'beginner')

        assert result['entry_count'] == 2  # Both count
        assert result['score'] == 2  # Meets beginner minimum

    def test_has_bullets_but_no_description(self, scorer):
        """Entry with bullets but no description should count as complete"""
        experiences = [
            self._create_complete_entry(title="Engineer", company="A"),
            {
                'title': "Developer",
                'company': "B",
                'startDate': "Jan 2020",
                'endDate': "Dec 2020",
                'achievements': ["Built API", "Led team"]  # Has bullets
            }
        ]

        result = scorer.score(experiences, 'beginner')

        assert result['entry_count'] == 2  # Both count
        assert result['score'] == 2  # Meets beginner minimum

    # ========================================================================
    # EDGE CASES
    # ========================================================================

    def test_empty_experience_list(self, scorer):
        """Empty experience list = 0 points for all levels"""
        for level in ['beginner', 'intermediary', 'senior']:
            result = scorer.score([], level)

            assert result['score'] == 0
            assert result['entry_count'] == 0
            assert result['meets_minimum'] is False

    def test_none_experience_list(self, scorer):
        """None experience list = 0 points (graceful handling)"""
        result = scorer.score(None, 'beginner')

        assert result['score'] == 0
        assert result['entry_count'] == 0
        assert result['meets_minimum'] is False

    def test_mixed_complete_incomplete_entries_beginner(self, scorer):
        """Mix of complete and incomplete entries - only count complete"""
        experiences = [
            self._create_complete_entry(title="Engineer", company="A"),
            self._create_incomplete_entry(title="Developer"),  # Missing company, dates, bullets
            self._create_complete_entry(title="Intern", company="B"),
            self._create_incomplete_entry(company="C", startDate="Jan 2020")  # Missing title
        ]

        result = scorer.score(experiences, 'beginner')

        assert result['entry_count'] == 2  # Only 2 complete entries
        assert result['score'] == 2  # Meets beginner minimum

    def test_whitespace_only_fields_not_valid(self, scorer):
        """Fields with only whitespace should be considered missing"""
        experiences = [
            self._create_complete_entry(title="Engineer", company="A"),
            {
                'title': "   ",  # Whitespace only
                'company': "B",
                'startDate': "Jan 2020",
                'endDate': "Dec 2020",
                'achievements': ["Built API"]
            }
        ]

        result = scorer.score(experiences, 'beginner')

        assert result['entry_count'] == 1  # Second entry doesn't count
        assert result['score'] == 0

    def test_empty_string_fields_not_valid(self, scorer):
        """Empty string fields should be considered missing"""
        experiences = [
            self._create_complete_entry(title="Engineer", company="A"),
            {
                'title': "Developer",
                'company': "",  # Empty string
                'startDate': "Jan 2020",
                'endDate': "Dec 2020",
                'achievements': ["Built API"]
            }
        ]

        result = scorer.score(experiences, 'beginner')

        assert result['entry_count'] == 1
        assert result['score'] == 0

    def test_case_insensitive_level(self, scorer):
        """Level parameter should be case-insensitive"""
        experiences = [
            self._create_complete_entry() for _ in range(3)
        ]

        for level_variant in ['INTERMEDIARY', 'Intermediary', 'intermediary', 'InTeRmEdIaRy']:
            result = scorer.score(experiences, level_variant)

            assert result['score'] == 2
            assert result['level'].lower() == 'intermediary'

    def test_unknown_level_defaults_to_intermediary(self, scorer):
        """Unknown level should default to intermediary (3 entries minimum)"""
        experiences = [
            self._create_complete_entry() for _ in range(3)
        ]

        result = scorer.score(experiences, 'unknown_level')

        assert result['score'] == 2
        assert result['entry_count'] == 3
        assert result['meets_minimum'] is True

    # ========================================================================
    # RETURN VALUE STRUCTURE TESTS
    # ========================================================================

    def test_return_structure_complete(self, scorer):
        """Verify return dictionary has all required fields"""
        experiences = [
            self._create_complete_entry() for _ in range(2)
        ]

        result = scorer.score(experiences, 'beginner')

        # Check all required keys exist
        assert 'score' in result
        assert 'max_score' in result
        assert 'entry_count' in result
        assert 'level' in result
        assert 'meets_minimum' in result
        assert 'details' in result

        # Check types
        assert isinstance(result['score'], int)
        assert isinstance(result['max_score'], int)
        assert isinstance(result['entry_count'], int)
        assert isinstance(result['level'], str)
        assert isinstance(result['meets_minimum'], bool)
        assert isinstance(result['details'], str)

        # Check value ranges
        assert 0 <= result['score'] <= 2
        assert result['max_score'] == 2
        assert result['entry_count'] >= 0

    def test_details_field_informative(self, scorer):
        """Details field should provide clear feedback"""
        experiences = [
            self._create_complete_entry()
        ]

        result = scorer.score(experiences, 'beginner')

        details = result['details']

        # Should mention the count found
        assert '1' in details

        # Should mention required minimum for level
        assert 'beginner' in details.lower()
        assert '2' in details

    def test_details_mentions_success_when_met(self, scorer):
        """Details should indicate success when minimum is met"""
        experiences = [
            self._create_complete_entry() for _ in range(4)
        ]

        result = scorer.score(experiences, 'senior')

        assert result['meets_minimum'] is True
        details_lower = result['details'].lower()
        assert 'meet' in details_lower or 'sufficient' in details_lower or 'minimum' in details_lower

    # ========================================================================
    # BOUNDARY TESTS
    # ========================================================================

    def test_beginner_boundary_1_entry_fails(self, scorer):
        """Beginner: 1 entry (just below minimum) = 0 points"""
        experiences = [self._create_complete_entry()]
        result = scorer.score(experiences, 'beginner')

        assert result['score'] == 0
        assert result['meets_minimum'] is False

    def test_beginner_boundary_2_entries_passes(self, scorer):
        """Beginner: 2 entries (exactly at minimum) = 2 points"""
        experiences = [self._create_complete_entry() for _ in range(2)]
        result = scorer.score(experiences, 'beginner')

        assert result['score'] == 2
        assert result['meets_minimum'] is True

    def test_intermediary_boundary_2_entries_fails(self, scorer):
        """Intermediary: 2 entries (just below minimum) = 0 points"""
        experiences = [self._create_complete_entry() for _ in range(2)]
        result = scorer.score(experiences, 'intermediary')

        assert result['score'] == 0
        assert result['meets_minimum'] is False

    def test_intermediary_boundary_3_entries_passes(self, scorer):
        """Intermediary: 3 entries (exactly at minimum) = 2 points"""
        experiences = [self._create_complete_entry() for _ in range(3)]
        result = scorer.score(experiences, 'intermediary')

        assert result['score'] == 2
        assert result['meets_minimum'] is True

    def test_senior_boundary_3_entries_fails(self, scorer):
        """Senior: 3 entries (just below minimum) = 0 points"""
        experiences = [self._create_complete_entry() for _ in range(3)]
        result = scorer.score(experiences, 'senior')

        assert result['score'] == 0
        assert result['meets_minimum'] is False

    def test_senior_boundary_4_entries_passes(self, scorer):
        """Senior: 4 entries (exactly at minimum) = 2 points"""
        experiences = [self._create_complete_entry() for _ in range(4)]
        result = scorer.score(experiences, 'senior')

        assert result['score'] == 2
        assert result['meets_minimum'] is True
