"""
Performance Tests for Scorer V3

Validates that scoring operations complete within acceptable time limits:
- Single resume scoring: <2 seconds (requirement)
- Batch scoring: <5 seconds for 10 resumes
- Parameter-level operations: <500ms each

These tests ensure production readiness and user experience quality.
"""

import pytest
import time
from backend.services.scorer_v3 import ScorerV3, score_resume_v3


@pytest.fixture
def scorer():
    """Create ScorerV3 instance."""
    return ScorerV3()


@pytest.fixture
def comprehensive_resume_data():
    """Comprehensive resume data for performance testing."""
    return {
        'text': """
        Senior Software Engineer

        Experienced full-stack developer with 8+ years building scalable systems.

        EXPERIENCE
        Senior Software Engineer | Tech Corp | 2020-Present
        - Led development of microservices platform serving 5M+ users
        - Architected cloud infrastructure reducing costs by 45%
        - Pioneered ML-driven recommendations increasing revenue by $2M
        - Implemented CI/CD pipeline cutting deployment time by 70%
        - Built automated testing framework improving coverage from 30% to 90%

        Software Engineer | StartupCo | 2017-2020
        - Developed REST APIs handling 10K requests/second
        - Reduced database query time by 60% through optimization
        - Launched 3 major features ahead of schedule
        - Mentored team of 5 junior engineers

        SKILLS
        Python, Django, React, TypeScript, AWS, Docker, Kubernetes, PostgreSQL,
        Redis, Terraform, CI/CD, Git, Agile, Microservices, REST API

        EDUCATION
        BS Computer Science | Stanford University | 2017
        """,
        'bullets': [
            "Led development of microservices platform serving 5M+ users",
            "Architected cloud infrastructure reducing costs by 45%",
            "Pioneered ML-driven recommendations increasing revenue by $2M",
            "Implemented CI/CD pipeline cutting deployment time by 70%",
            "Built automated testing framework improving coverage from 30% to 90%",
            "Developed REST APIs handling 10K requests/second",
            "Reduced database query time by 60% through optimization",
            "Launched 3 major features ahead of schedule",
            "Mentored team of 5 junior engineers"
        ],
        'sections': {
            'experience': {
                'content': 'Senior Software Engineer | Tech Corp | 2020-Present...',
                'word_count': 450
            },
            'skills': {
                'content': 'Python, Django, React, TypeScript, AWS, Docker...',
                'word_count': 120
            },
            'education': {
                'content': 'BS Computer Science | Stanford University | 2017',
                'word_count': 80
            }
        },
        'page_count': 2,
        'format': 'pdf',
        'experience': [
            {
                'title': 'Senior Software Engineer',
                'company': 'Tech Corp',
                'startDate': '2020-01',
                'endDate': 'Present',
                'description': 'Led development of microservices platform'
            },
            {
                'title': 'Software Engineer',
                'company': 'StartupCo',
                'startDate': '2017-06',
                'endDate': '2020-01',
                'description': 'Developed REST APIs'
            }
        ],
        'contact': {
            'email': 'engineer@example.com',
            'phone': '555-0123'
        }
    }


@pytest.fixture
def job_requirements():
    """Sample job requirements."""
    return {
        'required_keywords': ['Python', 'AWS', 'Microservices', 'CI/CD', 'Leadership'],
        'preferred_keywords': ['Docker', 'Kubernetes', 'React', 'TypeScript', 'Terraform']
    }


# ============================================================================
# CORE PERFORMANCE TESTS
# ============================================================================

def test_single_resume_scoring_performance(scorer, comprehensive_resume_data, job_requirements):
    """
    Critical: Single resume scoring must complete in <2 seconds.

    This is the primary user-facing operation and must be fast.
    """
    start_time = time.time()

    result = scorer.score(
        resume_data=comprehensive_resume_data,
        job_requirements=job_requirements,
        experience_level='senior'
    )

    elapsed_time = time.time() - start_time

    # Assert result is valid
    assert 'total_score' in result
    assert result['total_score'] >= 0

    # Performance requirement: <2 seconds
    assert elapsed_time < 2.0, \
        f"Scoring took {elapsed_time:.2f}s, requirement is <2s"

    # Log performance for monitoring
    print(f"\n✓ Single resume scored in {elapsed_time:.3f}s")


def test_scoring_without_keywords_performance(scorer, comprehensive_resume_data):
    """
    Scoring without job requirements should be even faster (<1.5s).

    Skips keyword matching parameters (P1.1, P1.2).
    """
    start_time = time.time()

    result = scorer.score(
        resume_data=comprehensive_resume_data,
        job_requirements=None,
        experience_level='intermediary'
    )

    elapsed_time = time.time() - start_time

    assert 'total_score' in result

    # Should be faster without keyword matching
    assert elapsed_time < 1.5, \
        f"No-keywords scoring took {elapsed_time:.2f}s, expected <1.5s"

    print(f"\n✓ No-keywords scoring in {elapsed_time:.3f}s")


def test_minimal_resume_scoring_performance(scorer):
    """
    Minimal resume (many skipped parameters) should be very fast (<1s).
    """
    minimal_data = {
        'text': 'Junior developer with Python experience.',
        'bullets': ['Worked on Python projects'],
        'page_count': 1,
        'sections': {
            'experience': {'content': 'Junior developer', 'word_count': 10}
        },
        'experience': []
    }

    start_time = time.time()

    result = scorer.score(
        resume_data=minimal_data,
        experience_level='beginner'
    )

    elapsed_time = time.time() - start_time

    assert 'total_score' in result

    # Minimal data should be very fast
    assert elapsed_time < 1.0, \
        f"Minimal scoring took {elapsed_time:.2f}s, expected <1s"

    print(f"\n✓ Minimal resume scored in {elapsed_time:.3f}s")


def test_convenience_function_performance(comprehensive_resume_data, job_requirements):
    """
    Test the convenience function score_resume_v3() performance.
    """
    start_time = time.time()

    result = score_resume_v3(
        resume_data=comprehensive_resume_data,
        job_requirements=job_requirements,
        experience_level='senior'
    )

    elapsed_time = time.time() - start_time

    assert result['total_score'] >= 0
    assert elapsed_time < 2.0, \
        f"Convenience function took {elapsed_time:.2f}s, requirement is <2s"

    print(f"\n✓ Convenience function in {elapsed_time:.3f}s")


# ============================================================================
# BATCH PERFORMANCE TESTS
# ============================================================================

def test_batch_scoring_performance(scorer, comprehensive_resume_data, job_requirements):
    """
    Batch scoring of 10 resumes should complete in <5 seconds.

    Important for API endpoints that might handle multiple concurrent requests.
    """
    # Create variations of the resume
    resumes = []
    for i in range(10):
        resume_copy = comprehensive_resume_data.copy()
        resume_copy['text'] = comprehensive_resume_data['text'] + f" Variation {i}"
        resumes.append(resume_copy)

    start_time = time.time()

    results = []
    for resume in resumes:
        result = scorer.score(
            resume_data=resume,
            job_requirements=job_requirements,
            experience_level='senior'
        )
        results.append(result)

    elapsed_time = time.time() - start_time

    assert len(results) == 10
    assert all(r['total_score'] >= 0 for r in results)

    # Batch requirement: <5 seconds for 10 resumes
    assert elapsed_time < 5.0, \
        f"Batch scoring took {elapsed_time:.2f}s, requirement is <5s for 10 resumes"

    avg_time = elapsed_time / 10
    print(f"\n✓ Batch scored 10 resumes in {elapsed_time:.2f}s (avg {avg_time:.3f}s/resume)")


# ============================================================================
# PARAMETER-LEVEL PERFORMANCE TESTS
# ============================================================================

def test_keyword_matching_performance(scorer, comprehensive_resume_data, job_requirements):
    """
    Keyword matching (P1.1, P1.2) should complete quickly.

    Note: Semantic matching may add latency in online mode.
    """
    from backend.services.parameters.p1_1_required_keywords import RequiredKeywordsMatcher
    from backend.services.parameters.p1_2_preferred_keywords import PreferredKeywordsMatcher

    p1_1_matcher = RequiredKeywordsMatcher()
    p1_2_matcher = PreferredKeywordsMatcher()

    # P1.1 performance
    start_time = time.time()
    p1_1_result = p1_1_matcher.score(
        keywords=job_requirements['required_keywords'],
        resume_text=comprehensive_resume_data['text'],
        level='senior'
    )
    p1_1_time = time.time() - start_time

    assert p1_1_result['score'] >= 0
    print(f"\n✓ P1.1 (Required Keywords) in {p1_1_time:.3f}s")

    # P1.2 performance
    start_time = time.time()
    p1_2_result = p1_2_matcher.calculate_score(
        preferred_keywords=job_requirements['preferred_keywords'],
        resume_text=comprehensive_resume_data['text'],
        experience_level='senior'
    )
    p1_2_time = time.time() - start_time

    assert p1_2_result['score'] >= 0
    print(f"✓ P1.2 (Preferred Keywords) in {p1_2_time:.3f}s")

    # Combined should be fast (note: semantic matching may take longer)
    total_time = p1_1_time + p1_2_time
    assert total_time < 1.0, \
        f"Keyword matching took {total_time:.2f}s, should be <1s"


def test_content_quality_performance(scorer, comprehensive_resume_data):
    """
    Content quality parameters (P2.x) should be fast.
    """
    from backend.services.parameters.p2_1_action_verbs import ActionVerbScorer
    from backend.services.parameters.p2_2_quantification import QuantificationScorer

    bullets = comprehensive_resume_data['bullets']

    # P2.1 performance
    start_time = time.time()
    p2_1_scorer = ActionVerbScorer()
    p2_1_result = p2_1_scorer.score(bullets=bullets, level='senior')
    p2_1_time = time.time() - start_time

    assert p2_1_result['score'] >= 0
    assert p2_1_time < 0.5, f"P2.1 took {p2_1_time:.3f}s, should be <0.5s"
    print(f"\n✓ P2.1 (Action Verbs) in {p2_1_time:.3f}s")

    # P2.2 performance
    start_time = time.time()
    p2_2_scorer = QuantificationScorer()
    p2_2_result = p2_2_scorer.score(bullets=bullets, level='senior')
    p2_2_time = time.time() - start_time

    assert p2_2_result['score'] >= 0
    assert p2_2_time < 0.5, f"P2.2 took {p2_2_time:.3f}s, should be <0.5s"
    print(f"✓ P2.2 (Quantification) in {p2_2_time:.3f}s")


# ============================================================================
# STRESS TESTS
# ============================================================================

def test_large_resume_performance(scorer):
    """
    Test performance with an unusually large resume (3000+ words).

    Should still complete in <3 seconds.
    """
    # Create large resume by repeating content
    large_text = """
    Senior Software Engineer with extensive experience.
    Led development of distributed systems. Architected cloud solutions.
    Implemented CI/CD pipelines. Built testing frameworks.
    """ * 100  # ~3000 words

    large_bullets = [
        f"Led development of feature {i} serving {i*1000} users"
        for i in range(50)
    ]

    large_resume = {
        'text': large_text,
        'bullets': large_bullets,
        'page_count': 5,
        'sections': {
            'experience': {'content': large_text, 'word_count': 3000}
        },
        'experience': []
    }

    start_time = time.time()

    result = scorer.score(
        resume_data=large_resume,
        experience_level='senior'
    )

    elapsed_time = time.time() - start_time

    assert result['total_score'] >= 0

    # Large resumes get 50% more time allowance
    assert elapsed_time < 3.0, \
        f"Large resume took {elapsed_time:.2f}s, limit is 3s"

    print(f"\n✓ Large resume (3000+ words) scored in {elapsed_time:.3f}s")


def test_repeated_scoring_performance(scorer, comprehensive_resume_data, job_requirements):
    """
    Test that repeated scoring maintains consistent performance.

    Validates no memory leaks or performance degradation.
    """
    times = []

    for i in range(5):
        start_time = time.time()

        result = scorer.score(
            resume_data=comprehensive_resume_data,
            job_requirements=job_requirements,
            experience_level='senior'
        )

        elapsed_time = time.time() - start_time
        times.append(elapsed_time)

        assert result['total_score'] >= 0

    avg_time = sum(times) / len(times)
    max_time = max(times)

    # All iterations should be under 2s
    assert max_time < 2.0, \
        f"Slowest iteration took {max_time:.2f}s, requirement is <2s"

    # Check for performance degradation (last shouldn't be >20% slower than first)
    degradation = (times[-1] - times[0]) / times[0] * 100
    assert abs(degradation) < 20, \
        f"Performance degraded by {degradation:.1f}%, should be <20%"

    print(f"\n✓ Repeated scoring: avg {avg_time:.3f}s, max {max_time:.3f}s")


# ============================================================================
# INITIALIZATION PERFORMANCE
# ============================================================================

def test_scorer_initialization_performance():
    """
    Scorer initialization should be fast (<1s).

    Important for cold-start scenarios (serverless, first API request).
    """
    start_time = time.time()

    scorer = ScorerV3()

    elapsed_time = time.time() - start_time

    assert scorer is not None
    assert len(scorer.scorers) == 21

    # Initialization should be quick
    assert elapsed_time < 1.0, \
        f"Scorer initialization took {elapsed_time:.2f}s, should be <1s"

    print(f"\n✓ Scorer initialized in {elapsed_time:.3f}s")


# ============================================================================
# PERFORMANCE SUMMARY
# ============================================================================

@pytest.mark.slow
def test_performance_benchmark_summary(scorer, comprehensive_resume_data, job_requirements):
    """
    Comprehensive performance benchmark with detailed timing breakdown.

    Run with: pytest -v -m slow
    """
    print("\n" + "="*70)
    print("PERFORMANCE BENCHMARK SUMMARY")
    print("="*70)

    # Full scoring with keywords
    start = time.time()
    result_full = scorer.score(comprehensive_resume_data, job_requirements, 'senior')
    time_full = time.time() - start

    # Scoring without keywords
    start = time.time()
    result_no_kw = scorer.score(comprehensive_resume_data, None, 'senior')
    time_no_kw = time.time() - start

    # Minimal resume
    minimal = {
        'text': 'Developer',
        'bullets': ['Coded'],
        'page_count': 1,
        'sections': {'experience': {'content': 'Dev', 'word_count': 1}},
        'experience': []
    }
    start = time.time()
    result_minimal = scorer.score(minimal, None, 'beginner')
    time_minimal = time.time() - start

    print(f"\nFull Resume + Keywords:  {time_full:.3f}s  (Target: <2.0s)")
    print(f"Full Resume, No Keywords: {time_no_kw:.3f}s  (Target: <1.5s)")
    print(f"Minimal Resume:           {time_minimal:.3f}s  (Target: <1.0s)")

    print(f"\nParameter Count: {len(result_full['parameter_scores'])}")
    print(f"Successful Parameters: {sum(1 for p in result_full['parameter_scores'].values() if p['status'] == 'success')}")

    print("="*70 + "\n")

    # All should meet targets
    assert time_full < 2.0
    assert time_no_kw < 1.5
    assert time_minimal < 1.0
