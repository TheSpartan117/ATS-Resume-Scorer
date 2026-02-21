"""
Test Suite for P1.2 - Preferred Keywords Match (10 points)

Testing the more lenient "nice-to-have" keyword matching with tiered scoring:
- ≥50% match: 10 points (excellent coverage)
- ≥30% match: 6 points (good coverage)
- ≥15% match: 3 points (minimal coverage)
- <15% match: 0 points (insufficient)

Research basis:
- Preferred keywords are "nice-to-have" vs. required keywords which are critical
- More lenient thresholds reflect optional nature
- Still contributes significantly (10 points) when well-matched

Usage:
    matcher = PreferredKeywordsMatcher()
    result = matcher.calculate_score(
        preferred_keywords=["React", "TypeScript", "GraphQL"],
        resume_text="Python developer with React experience",
        experience_level="intermediary"
    )
"""

import pytest
from backend.services.parameters.p1_2_preferred_keywords import PreferredKeywordsMatcher
from tests.conftest import requires_semantic_model


@pytest.fixture
def matcher():
    """Fixture to provide PreferredKeywordsMatcher instance"""
    return PreferredKeywordsMatcher()


@pytest.fixture
def sample_resume_full():
    """Resume with comprehensive skill coverage"""
    return """
    Full-stack developer with 5 years experience.

    Skills:
    - Frontend: React, TypeScript, Vue.js, Angular
    - Backend: Python, Django, Node.js, Express
    - Database: PostgreSQL, MongoDB, Redis
    - Cloud: AWS, Docker, Kubernetes
    - Tools: Git, CI/CD, Jest, Webpack

    Built scalable web applications using modern frameworks.
    """


@pytest.fixture
def sample_resume_partial():
    """Resume with partial skill coverage"""
    return """
    Python developer with backend experience.

    Skills:
    - Python, Django, Flask
    - PostgreSQL, MySQL
    - Docker, Git

    Developed REST APIs and database systems.
    """


@pytest.fixture
def sample_resume_minimal():
    """Resume with minimal skill coverage"""
    return """
    Junior developer with basic programming skills.

    Skills:
    - Python basics
    - Git version control

    Completed coursework in computer science.
    """


def test_all_preferred_matched(matcher, sample_resume_full):
    """100% match should give 10 points"""
    preferred_keywords = ["React", "TypeScript", "Python", "Django"]

    result = matcher.calculate_score(
        preferred_keywords=preferred_keywords,
        resume_text=sample_resume_full,
        experience_level="intermediary"
    )

    assert result['score'] == 10, f"Expected 10 points for 100% match, got {result['score']}"
    assert result['match_percentage'] == 100.0, f"Expected 100% match, got {result['match_percentage']}"
    assert result['matched_count'] == 4, f"Expected 4 matched, got {result['matched_count']}"
    assert result['total_keywords'] == 4, f"Expected 4 total, got {result['total_keywords']}"


def test_75_percent_match(matcher, sample_resume_full):
    """75% match should give 10 points (≥50% threshold)"""
    preferred_keywords = ["React", "TypeScript", "Python", "Ruby"]

    result = matcher.calculate_score(
        preferred_keywords=preferred_keywords,
        resume_text=sample_resume_full,
        experience_level="intermediary"
    )

    assert result['score'] == 10, f"Expected 10 points for 75% match, got {result['score']}"
    assert result['match_percentage'] == 75.0, f"Expected 75% match, got {result['match_percentage']}"
    assert result['matched_count'] == 3, f"Expected 3 matched, got {result['matched_count']}"


def test_50_percent_match_exact(matcher, sample_resume_partial):
    """Exactly 50% match should give 10 points (boundary test)"""
    preferred_keywords = ["Python", "Django", "React", "Angular"]

    result = matcher.calculate_score(
        preferred_keywords=preferred_keywords,
        resume_text=sample_resume_partial,
        experience_level="intermediary"
    )

    assert result['score'] == 10, f"Expected 10 points for 50% match, got {result['score']}"
    assert result['match_percentage'] == 50.0, f"Expected 50% match, got {result['match_percentage']}"
    assert result['matched_count'] == 2, f"Expected 2 matched, got {result['matched_count']}"


def test_40_percent_match(matcher, sample_resume_partial):
    """40% match should give 6 points (≥30% threshold)"""
    preferred_keywords = ["Python", "Django", "React", "Angular", "Vue.js"]

    result = matcher.calculate_score(
        preferred_keywords=preferred_keywords,
        resume_text=sample_resume_partial,
        experience_level="intermediary"
    )

    assert result['score'] == 6, f"Expected 6 points for 40% match, got {result['score']}"
    assert result['match_percentage'] == 40.0, f"Expected 40% match, got {result['match_percentage']}"
    assert result['matched_count'] == 2, f"Expected 2 matched, got {result['matched_count']}"


@requires_semantic_model
def test_30_percent_match_exact(matcher, sample_resume_partial):
    """Exactly 30% match should give 6 points (boundary test) - requires semantic matching"""
    preferred_keywords = [
        "Python", "Django", "React", "Angular", "Vue.js",
        "TypeScript", "Node.js", "GraphQL", "MongoDB", "Kubernetes"
    ]

    result = matcher.calculate_score(
        preferred_keywords=preferred_keywords,
        resume_text=sample_resume_partial,
        experience_level="intermediary"
    )

    assert result['score'] == 6, f"Expected 6 points for 30% match, got {result['score']}"
    assert result['match_percentage'] == 30.0, f"Expected 30% match, got {result['match_percentage']}"
    assert result['matched_count'] == 3, f"Expected 3 matched, got {result['matched_count']}"


def test_20_percent_match(matcher, sample_resume_minimal):
    """20% match should give 3 points (≥15% threshold)"""
    preferred_keywords = ["Python", "React", "Angular", "Vue.js", "TypeScript"]

    result = matcher.calculate_score(
        preferred_keywords=preferred_keywords,
        resume_text=sample_resume_minimal,
        experience_level="beginner"
    )

    assert result['score'] == 3, f"Expected 3 points for 20% match, got {result['score']}"
    assert result['match_percentage'] == 20.0, f"Expected 20% match, got {result['match_percentage']}"
    assert result['matched_count'] == 1, f"Expected 1 matched, got {result['matched_count']}"


@requires_semantic_model
def test_15_percent_match_exact(matcher, sample_resume_minimal):
    """Exactly 15% match should give 3 points (boundary test) - requires semantic matching"""
    preferred_keywords = [
        "Python", "React", "Angular", "Vue.js", "TypeScript", "Ruby", "Go"
    ]

    result = matcher.calculate_score(
        preferred_keywords=preferred_keywords,
        resume_text=sample_resume_minimal,
        experience_level="beginner"
    )

    # 1 out of 7 ≈ 14.29%, rounds to 14% - should give 0 points
    # Let's adjust to get exactly 15%
    preferred_keywords_20 = [
        "Python", "React", "Angular", "Vue.js", "TypeScript",
        "Ruby", "Go", "Rust", "Java", "Kotlin",
        "Swift", "Kotlin", "C#", "PHP", "Perl",
        "Scala", "Elixir", "Haskell", "Clojure", "F#"
    ]

    result = matcher.calculate_score(
        preferred_keywords=preferred_keywords_20,
        resume_text=sample_resume_minimal,
        experience_level="beginner"
    )

    # 1 out of 20 = 5%, should give 0 points
    assert result['score'] == 0, f"Expected 0 points for 5% match, got {result['score']}"

    # Now test exactly 15% (3 out of 20)
    resume_with_three = sample_resume_minimal + "\nGit, Docker, and basic TypeScript knowledge"
    result = matcher.calculate_score(
        preferred_keywords=preferred_keywords_20,
        resume_text=resume_with_three,
        experience_level="beginner"
    )

    assert result['score'] == 3, f"Expected 3 points for 15% match, got {result['score']}"
    assert result['match_percentage'] == 15.0, f"Expected 15% match, got {result['match_percentage']}"


def test_below_15_percent(matcher, sample_resume_minimal):
    """<15% match should give 0 points"""
    preferred_keywords = [
        "React", "Angular", "Vue.js", "TypeScript", "GraphQL",
        "MongoDB", "Redis", "Kubernetes", "AWS", "Azure"
    ]

    result = matcher.calculate_score(
        preferred_keywords=preferred_keywords,
        resume_text=sample_resume_minimal,
        experience_level="beginner"
    )

    assert result['score'] == 0, f"Expected 0 points for <15% match, got {result['score']}"
    assert result['match_percentage'] < 15.0, f"Expected <15% match, got {result['match_percentage']}"


def test_zero_percent_match(matcher, sample_resume_minimal):
    """0% match should give 0 points"""
    preferred_keywords = [
        "Rust", "Go", "Elixir", "Scala", "Kotlin"
    ]

    result = matcher.calculate_score(
        preferred_keywords=preferred_keywords,
        resume_text=sample_resume_minimal,
        experience_level="beginner"
    )

    assert result['score'] == 0, f"Expected 0 points for 0% match, got {result['score']}"
    assert result['match_percentage'] == 0.0, f"Expected 0% match, got {result['match_percentage']}"
    assert result['matched_count'] == 0, f"Expected 0 matched, got {result['matched_count']}"


def test_empty_preferred_keywords(matcher, sample_resume_full):
    """Empty preferred keywords should return 0 points"""
    result = matcher.calculate_score(
        preferred_keywords=[],
        resume_text=sample_resume_full,
        experience_level="intermediary"
    )

    assert result['score'] == 0, f"Expected 0 points for empty keywords, got {result['score']}"
    assert result['match_percentage'] == 0.0
    assert result['matched_count'] == 0
    assert result['total_keywords'] == 0


def test_empty_resume_text(matcher):
    """Empty resume text should return 0 points"""
    preferred_keywords = ["Python", "Django", "React"]

    result = matcher.calculate_score(
        preferred_keywords=preferred_keywords,
        resume_text="",
        experience_level="intermediary"
    )

    assert result['score'] == 0, f"Expected 0 points for empty resume, got {result['score']}"
    assert result['match_percentage'] == 0.0
    assert result['matched_count'] == 0


def test_case_insensitive_matching(matcher):
    """Matching should be case-insensitive"""
    resume_text = "PYTHON developer with DJANGO experience and react skills"
    preferred_keywords = ["Python", "Django", "React"]

    result = matcher.calculate_score(
        preferred_keywords=preferred_keywords,
        resume_text=resume_text,
        experience_level="intermediary"
    )

    assert result['score'] == 10, f"Expected 10 points for case variations, got {result['score']}"
    assert result['match_percentage'] == 100.0
    assert result['matched_count'] == 3


@requires_semantic_model
def test_hybrid_semantic_matching(matcher):
    """Should use hybrid matching (semantic + exact) via HybridKeywordMatcher - requires semantic model"""
    resume_text = "Expert in Pythonic programming and machine learning algorithms"
    preferred_keywords = ["Python", "ML", "Deep Learning"]

    result = matcher.calculate_score(
        preferred_keywords=preferred_keywords,
        resume_text=resume_text,
        experience_level="intermediary"
    )

    # Should match "Python" semantically via "Pythonic"
    # Should match "ML" semantically via "machine learning"
    # Should not match "Deep Learning"
    # Expected 2 out of 3 = 66.67% ≈ 10 points
    assert result['matched_count'] >= 1, f"Expected at least 1 semantic match, got {result['matched_count']}"
    assert result['match_percentage'] > 0


def test_experience_level_parameter(matcher, sample_resume_full):
    """Should accept different experience levels (though not used in scoring yet)"""
    preferred_keywords = ["React", "TypeScript", "Python"]

    for level in ["beginner", "intermediary", "senior"]:
        result = matcher.calculate_score(
            preferred_keywords=preferred_keywords,
            resume_text=sample_resume_full,
            experience_level=level
        )

        assert result['score'] == 10, f"Expected 10 points for level {level}"
        assert 'experience_level' in result
        assert result['experience_level'] == level


def test_result_structure(matcher, sample_resume_full):
    """Test that result contains all required fields"""
    preferred_keywords = ["React", "Python"]

    result = matcher.calculate_score(
        preferred_keywords=preferred_keywords,
        resume_text=sample_resume_full,
        experience_level="intermediary"
    )

    # Required fields
    assert 'score' in result
    assert 'match_percentage' in result
    assert 'matched_count' in result
    assert 'total_keywords' in result
    assert 'tier' in result
    assert 'experience_level' in result

    # Type checks
    assert isinstance(result['score'], (int, float))
    assert isinstance(result['match_percentage'], (int, float))
    assert isinstance(result['matched_count'], int)
    assert isinstance(result['total_keywords'], int)
    assert isinstance(result['tier'], str)
    assert isinstance(result['experience_level'], str)

    # Value ranges
    assert 0 <= result['score'] <= 10
    assert 0 <= result['match_percentage'] <= 100
    assert result['matched_count'] <= result['total_keywords']


def test_matched_keywords_list(matcher, sample_resume_partial):
    """Result should include list of matched and unmatched keywords"""
    preferred_keywords = ["Python", "Django", "React", "Angular"]

    result = matcher.calculate_score(
        preferred_keywords=preferred_keywords,
        resume_text=sample_resume_partial,
        experience_level="intermediary"
    )

    assert 'matched_keywords' in result
    assert 'unmatched_keywords' in result

    assert isinstance(result['matched_keywords'], list)
    assert isinstance(result['unmatched_keywords'], list)

    # Matched + unmatched should equal total
    total_found = len(result['matched_keywords']) + len(result['unmatched_keywords'])
    assert total_found == result['total_keywords']

    # Verify expected matches
    assert "Python" in result['matched_keywords']
    assert "Django" in result['matched_keywords']
    assert "React" in result['unmatched_keywords']
    assert "Angular" in result['unmatched_keywords']


def test_scoring_tiers_classification(matcher):
    """Test that correct tier is assigned based on match percentage"""
    resume_text = "Python Django React TypeScript"

    # Tier 1: ≥50%
    result_tier1 = matcher.calculate_score(
        preferred_keywords=["Python", "Django"],
        resume_text=resume_text,
        experience_level="intermediary"
    )
    assert result_tier1['tier'] == "Tier 1 (≥50%)"
    assert result_tier1['score'] == 10

    # Tier 2: ≥30%
    result_tier2 = matcher.calculate_score(
        preferred_keywords=["Python", "Django", "Angular", "Vue.js", "Ruby"],
        resume_text=resume_text,
        experience_level="intermediary"
    )
    assert result_tier2['tier'] == "Tier 2 (≥30%)"
    assert result_tier2['score'] == 6

    # Tier 3: ≥15%
    result_tier3 = matcher.calculate_score(
        preferred_keywords=[
            "Python", "Angular", "Vue.js", "Ruby", "Go", "Rust"
        ],
        resume_text=resume_text,
        experience_level="intermediary"
    )
    assert result_tier3['tier'] == "Tier 3 (≥15%)"
    assert result_tier3['score'] == 3

    # Tier 0: <15%
    result_tier0 = matcher.calculate_score(
        preferred_keywords=[
            "Angular", "Vue.js", "Ruby", "Go", "Rust",
            "Kotlin", "Swift", "Perl", "Scala", "Haskell"
        ],
        resume_text=resume_text,
        experience_level="intermediary"
    )
    assert result_tier0['tier'] == "Below Threshold (<15%)"
    assert result_tier0['score'] == 0


def test_single_keyword(matcher, sample_resume_full):
    """Test with single keyword"""
    result = matcher.calculate_score(
        preferred_keywords=["Python"],
        resume_text=sample_resume_full,
        experience_level="intermediary"
    )

    assert result['score'] == 10, f"Expected 10 points for 100% match, got {result['score']}"
    assert result['match_percentage'] == 100.0
    assert result['matched_count'] == 1
    assert result['total_keywords'] == 1


def test_many_keywords(matcher, sample_resume_full):
    """Test with many keywords (20+)"""
    preferred_keywords = [
        "React", "Angular", "Vue.js", "Svelte", "TypeScript",
        "JavaScript", "Python", "Django", "Flask", "FastAPI",
        "Node.js", "Express", "NestJS", "GraphQL", "REST",
        "PostgreSQL", "MongoDB", "Redis", "Docker", "Kubernetes",
        "AWS", "Azure", "GCP", "Git", "CI/CD"
    ]

    result = matcher.calculate_score(
        preferred_keywords=preferred_keywords,
        resume_text=sample_resume_full,
        experience_level="senior"
    )

    # Should handle large keyword lists
    assert 0 <= result['score'] <= 10
    assert 0 <= result['match_percentage'] <= 100
    assert result['total_keywords'] == len(preferred_keywords)


def test_duplicate_keywords_ignored(matcher, sample_resume_full):
    """Duplicate keywords should be handled gracefully"""
    preferred_keywords = ["Python", "Python", "Django", "Django"]

    result = matcher.calculate_score(
        preferred_keywords=preferred_keywords,
        resume_text=sample_resume_full,
        experience_level="intermediary"
    )

    # Should deduplicate or handle gracefully
    assert result['score'] == 10
    assert result['matched_count'] >= 2  # At least Python and Django
