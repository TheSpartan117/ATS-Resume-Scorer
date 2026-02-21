"""
Test RequiredKeywordsMatcher Service - Task 11: P1.1 Required Keywords Match (25 pts)

Tests the HIGHEST-WEIGHTED parameter in the ATS scorer.

Research basis:
- 60% keyword match is industry standard passing threshold (Workday)
- Tiered scoring rewards strong matches
- Hybrid matching reduces false negatives by 35-45%

Scoring structure:
- ≥60% match = 25 points (full credit)
- ≥40% match = 15 points (partial credit)
- ≥25% match = 5 points (minimal credit)
- <25% match = 0 points (fail)
"""

import pytest
from backend.services.required_keywords_matcher import RequiredKeywordsMatcher


@pytest.fixture
def matcher():
    """Create matcher instance for testing."""
    return RequiredKeywordsMatcher()


@pytest.fixture
def sample_resume():
    """Sample resume text for testing."""
    return """
    Software Engineer with 5 years of experience in Python development.

    Experience:
    - Developed REST APIs using Django and Flask frameworks
    - Built microservices with Docker and Kubernetes
    - Implemented CI/CD pipelines with Jenkins
    - Worked with PostgreSQL and MongoDB databases
    - Created unit tests with pytest

    Skills: Python, Django, Docker, PostgreSQL, REST API, Git
    """


class TestRequiredKeywordsMatcherBasic:
    """Test basic matching functionality."""

    def test_perfect_match(self, matcher, sample_resume):
        """Test 100% keyword match (6/6) → 25 points."""
        keywords = ["Python", "Django", "Docker", "PostgreSQL", "REST API", "Git"]

        result = matcher.calculate_score(
            keywords=keywords,
            resume_text=sample_resume,
            experience_level="intermediary"
        )

        assert result['match_rate'] >= 99.0, "Should match all keywords"
        assert result['score'] == 25, "100% match should get full 25 points"
        assert result['matched_keywords'] == 6
        assert result['total_keywords'] == 6

    def test_good_match_60_percent(self, matcher, sample_resume):
        """Test 60% keyword match (6/10) → 25 points (threshold met)."""
        keywords = [
            "Python", "Django", "Docker", "PostgreSQL", "REST API", "Git",  # 6 matched
            "React", "TypeScript", "AWS", "Redis"  # 4 unmatched
        ]

        result = matcher.calculate_score(
            keywords=keywords,
            resume_text=sample_resume,
            experience_level="intermediary"
        )

        assert 58 <= result['match_rate'] <= 65, "Should match ~60% of keywords"
        assert result['score'] == 25, "≥60% match should get full 25 points"
        assert result['matched_keywords'] == 6
        assert result['total_keywords'] == 10

    def test_partial_match_50_percent(self, matcher, sample_resume):
        """Test 50% keyword match (5/10) → 15 points (partial credit)."""
        keywords = [
            "Python", "Django", "Docker", "PostgreSQL", "Git",  # 5 matched
            "React", "TypeScript", "AWS", "Redis", "Go"  # 5 unmatched
        ]

        result = matcher.calculate_score(
            keywords=keywords,
            resume_text=sample_resume,
            experience_level="intermediary"
        )

        assert 45 <= result['match_rate'] <= 55, "Should match ~50% of keywords"
        assert result['score'] == 15, "≥40% but <60% should get 15 points"
        assert result['matched_keywords'] == 5

    def test_minimal_match_30_percent(self, matcher, sample_resume):
        """Test 30% keyword match (3/10) → 5 points (minimal credit)."""
        keywords = [
            "Python", "Django", "Docker",  # 3 matched
            "React", "Angular", "Vue", "TypeScript", "Go", "Rust", "Swift"  # 7 unmatched
        ]

        result = matcher.calculate_score(
            keywords=keywords,
            resume_text=sample_resume,
            experience_level="intermediary"
        )

        assert 25 <= result['match_rate'] <= 35, "Should match ~30% of keywords"
        assert result['score'] == 5, "≥25% but <40% should get 5 points"
        assert result['matched_keywords'] == 3

    def test_fail_match_20_percent(self, matcher, sample_resume):
        """Test 20% keyword match (2/10) → 0 points (fail)."""
        keywords = [
            "Python", "Docker",  # 2 matched
            "React", "Angular", "Vue", "TypeScript", "Go", "Rust", "Swift", "Kotlin"  # 8 unmatched
        ]

        result = matcher.calculate_score(
            keywords=keywords,
            resume_text=sample_resume,
            experience_level="intermediary"
        )

        assert result['match_rate'] < 25, "Should match <25% of keywords"
        assert result['score'] == 0, "<25% match should get 0 points (fail)"
        assert result['matched_keywords'] == 2


class TestHybridMatching:
    """Test hybrid semantic+exact matching reduces false negatives."""

    def test_semantic_variations(self, matcher):
        """Test that semantic matching catches variations."""
        resume = "Expertise in Pythonic programming and Django web framework"
        keywords = ["Python", "Django"]

        result = matcher.calculate_score(
            keywords=keywords,
            resume_text=resume,
            experience_level="intermediary"
        )

        # Both should match via hybrid approach
        assert result['matched_keywords'] == 2, "Should match 'Pythonic' → 'Python' semantically"
        assert result['match_rate'] >= 95.0

    def test_exact_match_bonus(self, matcher):
        """Test that exact matches score higher than semantic matches."""
        resume_exact = "Python and Django experience"
        resume_semantic = "Pythonic programming with DRF"
        keywords = ["Python", "Django"]

        result_exact = matcher.calculate_score(keywords, resume_exact, "intermediary")
        result_semantic = matcher.calculate_score(keywords, resume_semantic, "intermediary")

        # Both should match but exact should have slightly higher individual scores
        assert result_exact['match_rate'] >= result_semantic['match_rate']

    def test_compound_keywords(self, matcher):
        """Test matching compound keywords like 'REST API'."""
        resume = "Built RESTful APIs with Django REST Framework"
        keywords = ["REST API", "Django"]

        result = matcher.calculate_score(keywords, resume, "intermediary")

        assert result['matched_keywords'] == 2, "Should match compound keywords"


class TestLevelAwareThresholds:
    """Test that thresholds adjust based on experience level."""

    def test_beginner_thresholds(self, matcher, sample_resume):
        """Beginner: Same thresholds (60/40/25) but expectations may differ."""
        keywords = ["Python", "Django", "Docker", "PostgreSQL", "Git", "React"]

        result = matcher.calculate_score(
            keywords=keywords,
            resume_text=sample_resume,
            experience_level="beginner"
        )

        # 5/6 matched ≈ 83%
        assert result['score'] == 25, "83% > 60% threshold → 25 points"

    def test_senior_thresholds(self, matcher, sample_resume):
        """Senior: Same scoring thresholds."""
        keywords = ["Python", "Django", "Docker", "PostgreSQL", "Git", "React"]

        result = matcher.calculate_score(
            keywords=keywords,
            resume_text=sample_resume,
            experience_level="senior"
        )

        assert result['score'] == 25, "83% > 60% threshold → 25 points"


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_keywords(self, matcher, sample_resume):
        """Test with empty keyword list."""
        result = matcher.calculate_score(
            keywords=[],
            resume_text=sample_resume,
            experience_level="intermediary"
        )

        assert result['score'] == 0
        assert result['match_rate'] == 0.0
        assert result['matched_keywords'] == 0
        assert result['total_keywords'] == 0

    def test_empty_resume(self, matcher):
        """Test with empty resume text."""
        result = matcher.calculate_score(
            keywords=["Python", "Django"],
            resume_text="",
            experience_level="intermediary"
        )

        assert result['score'] == 0
        assert result['match_rate'] == 0.0
        assert result['matched_keywords'] == 0

    def test_single_keyword(self, matcher, sample_resume):
        """Test with single keyword."""
        result = matcher.calculate_score(
            keywords=["Python"],
            resume_text=sample_resume,
            experience_level="intermediary"
        )

        assert result['matched_keywords'] == 1
        assert result['match_rate'] == 100.0
        assert result['score'] == 25

    def test_case_insensitive(self, matcher):
        """Test case-insensitive matching."""
        resume = "PYTHON and python and Python"
        keywords = ["Python"]

        result = matcher.calculate_score(keywords, resume, "intermediary")

        assert result['matched_keywords'] == 1
        assert result['match_rate'] == 100.0


class TestDetailedBreakdown:
    """Test detailed match statistics in response."""

    def test_response_structure(self, matcher, sample_resume):
        """Test that response includes all required fields."""
        keywords = ["Python", "Django", "React"]

        result = matcher.calculate_score(keywords, sample_resume, "intermediary")

        # Required fields
        assert 'score' in result
        assert 'match_rate' in result
        assert 'matched_keywords' in result
        assert 'total_keywords' in result
        assert 'threshold_met' in result
        assert 'tier' in result

        # Type checks
        assert isinstance(result['score'], (int, float))
        assert isinstance(result['match_rate'], float)
        assert isinstance(result['matched_keywords'], int)
        assert isinstance(result['total_keywords'], int)
        assert isinstance(result['threshold_met'], bool)
        assert isinstance(result['tier'], str)

    def test_threshold_met_flag(self, matcher, sample_resume):
        """Test threshold_met flag is set correctly."""
        # Pass case (60%+)
        result_pass = matcher.calculate_score(
            keywords=["Python", "Django", "Docker", "PostgreSQL", "Git"],
            resume_text=sample_resume,
            experience_level="intermediary"
        )
        assert result_pass['threshold_met'] is True

        # Fail case (<60%)
        result_fail = matcher.calculate_score(
            keywords=["Python", "React", "Angular", "Vue", "TypeScript", "Go"],
            resume_text=sample_resume,
            experience_level="intermediary"
        )
        assert result_fail['threshold_met'] is False

    def test_tier_labels(self, matcher, sample_resume):
        """Test that tier labels are returned correctly."""
        # Excellent (≥60%)
        result_excellent = matcher.calculate_score(
            keywords=["Python", "Django", "Docker"],
            resume_text=sample_resume,
            experience_level="intermediary"
        )
        assert result_excellent['tier'] == "excellent"

        # Partial (≥40%)
        result_partial = matcher.calculate_score(
            keywords=["Python", "Django", "React", "Angular", "Vue"],
            resume_text=sample_resume,
            experience_level="intermediary"
        )
        assert result_partial['tier'] == "partial"

        # Minimal (≥25%)
        result_minimal = matcher.calculate_score(
            keywords=["Python", "React", "Angular", "Vue", "TypeScript"],
            resume_text=sample_resume,
            experience_level="intermediary"
        )
        assert result_minimal['tier'] == "minimal"

        # Fail (<25%)
        result_fail = matcher.calculate_score(
            keywords=["Python", "React", "Angular", "Vue", "TypeScript", "Go", "Rust"],
            resume_text=sample_resume,
            experience_level="intermediary"
        )
        assert result_fail['tier'] == "fail"


class TestMaxPoints:
    """Test maximum points configuration."""

    def test_max_points_constant(self, matcher):
        """Test that max points is 25."""
        assert matcher.MAX_POINTS == 25

    def test_cannot_exceed_max(self, matcher, sample_resume):
        """Test that score cannot exceed 25 points."""
        # Perfect match should get exactly 25, not more
        keywords = ["Python", "Django", "Docker", "PostgreSQL"]

        result = matcher.calculate_score(keywords, sample_resume, "intermediary")

        assert result['score'] <= 25, "Score should never exceed max points"
        assert result['score'] == 25, "Perfect match gets exactly 25 points"
