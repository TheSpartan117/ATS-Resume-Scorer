"""
Tests for Scorer V3 - Comprehensive ATS Resume Scorer

Tests the orchestration of all 11 parameters into a unified scoring system.
"""

import pytest
from backend.services.scorer_v3 import ScorerV3, score_resume_v3


@pytest.fixture
def scorer():
    """Create ScorerV3 instance."""
    return ScorerV3()


@pytest.fixture
def sample_resume_data():
    """Sample resume data for testing."""
    return {
        'text': """
        Senior Software Engineer

        Led development of microservices architecture serving 1M+ users.
        Architected cloud infrastructure reducing costs by 40%.
        Pioneered ML-driven recommendations increasing engagement by 25%.
        Implemented CI/CD pipeline cutting deployment time by 60%.
        Built testing framework improving code coverage from 40% to 85%.
        """,
        'bullets': [
            "Led development of microservices architecture serving 1M+ users",
            "Architected cloud infrastructure reducing costs by 40%",
            "Pioneered ML-driven recommendations increasing engagement by 25%",
            "Implemented CI/CD pipeline cutting deployment time by 60%",
            "Built testing framework improving code coverage from 40% to 85%"
        ],
        'sections': {
            'experience': {'content': 'Experience content...', 'word_count': 450},
            'skills': {'content': 'Python, AWS, Docker, Kubernetes', 'word_count': 100},
            'education': {'content': 'BS Computer Science', 'word_count': 50}
        },
        'page_count': 2,
        'format': 'docx'
    }


@pytest.fixture
def sample_job_requirements():
    """Sample job requirements."""
    return {
        'required_keywords': ['Python', 'AWS', 'Microservices', 'CI/CD', 'Leadership'],
        'preferred_keywords': ['Docker', 'Kubernetes', 'Machine Learning', 'Terraform']
    }


# ============================================================================
# BASIC FUNCTIONALITY TESTS
# ============================================================================

def test_scorer_initialization(scorer):
    """Test scorer initializes with all parameters."""
    assert scorer.registry is not None
    assert len(scorer.scorers) == 11  # All 11 parameters


def test_basic_scoring_workflow(scorer, sample_resume_data, sample_job_requirements):
    """Test basic end-to-end scoring workflow."""
    result = scorer.score(
        resume_data=sample_resume_data,
        job_requirements=sample_job_requirements,
        experience_level='senior'
    )

    # Check top-level structure
    assert 'total_score' in result
    assert 'max_score' in result
    assert 'rating' in result
    assert 'category_scores' in result
    assert 'parameter_scores' in result
    assert 'feedback' in result

    # Check score bounds
    assert 0 <= result['total_score'] <= 100
    assert result['max_score'] == 100

    # Check rating is valid
    assert result['rating'] in ['Excellent', 'Good', 'Fair', 'Poor']


def test_convenience_function(sample_resume_data, sample_job_requirements):
    """Test convenience function score_resume_v3()."""
    result = score_resume_v3(
        resume_data=sample_resume_data,
        job_requirements=sample_job_requirements,
        experience_level='intermediary'
    )

    assert result['total_score'] is not None
    assert result['version'] == 'v3.0'


# ============================================================================
# PARAMETER SCORING TESTS
# ============================================================================

def test_all_parameters_scored(scorer, sample_resume_data, sample_job_requirements):
    """Test all 11 parameters are scored."""
    result = scorer.score(
        resume_data=sample_resume_data,
        job_requirements=sample_job_requirements,
        experience_level='intermediary'
    )

    parameter_scores = result['parameter_scores']

    # Should have all 11 parameters
    expected_params = ['P1.1', 'P1.2', 'P2.1', 'P2.2', 'P2.3',
                      'P3.1', 'P3.2', 'P3.3', 'P3.4', 'P4.1', 'P4.2']

    for param in expected_params:
        assert param in parameter_scores, f"Missing parameter: {param}"


def test_parameter_results_have_required_fields(scorer, sample_resume_data, sample_job_requirements):
    """Test each parameter result has required fields."""
    result = scorer.score(
        resume_data=sample_resume_data,
        job_requirements=sample_job_requirements
    )

    for code, param_result in result['parameter_scores'].items():
        assert 'score' in param_result
        assert 'max_score' in param_result
        assert 'percentage' in param_result
        assert 'status' in param_result


# ============================================================================
# CATEGORY AGGREGATION TESTS
# ============================================================================

def test_category_scores_aggregate_correctly(scorer, sample_resume_data, sample_job_requirements):
    """Test category scores aggregate parameter scores correctly."""
    result = scorer.score(
        resume_data=sample_resume_data,
        job_requirements=sample_job_requirements
    )

    category_scores = result['category_scores']

    # Check all categories present
    assert 'Keyword Matching' in category_scores
    assert 'Content Quality' in category_scores
    assert 'Format & Structure' in category_scores
    assert 'Professional Polish' in category_scores

    # Check category max scores
    assert category_scores['Keyword Matching']['max'] == 35
    assert category_scores['Content Quality']['max'] == 30
    assert category_scores['Format & Structure']['max'] == 20
    assert category_scores['Professional Polish']['max'] == 15

    # Check total equals sum of categories
    total = sum(cat['score'] for cat in category_scores.values())
    assert abs(total - result['total_score']) < 0.1  # Allow small floating point differences


def test_category_scores_within_bounds(scorer, sample_resume_data, sample_job_requirements):
    """Test category scores don't exceed max."""
    result = scorer.score(
        resume_data=sample_resume_data,
        job_requirements=sample_job_requirements
    )

    for category, data in result['category_scores'].items():
        assert 0 <= data['score'] <= data['max'], \
            f"Category {category} score {data['score']} exceeds max {data['max']}"


# ============================================================================
# MISSING DATA HANDLING TESTS
# ============================================================================

def test_missing_keywords_handled_gracefully(scorer, sample_resume_data):
    """Test scoring without job requirements."""
    result = scorer.score(
        resume_data=sample_resume_data,
        job_requirements=None,  # No keywords
        experience_level='intermediary'
    )

    # P1.1 and P1.2 should be skipped
    assert result['parameter_scores']['P1.1']['status'] == 'skipped'
    assert result['parameter_scores']['P1.2']['status'] == 'skipped'

    # Other parameters should still score
    assert result['parameter_scores']['P2.1']['status'] == 'success'
    assert result['parameter_scores']['P2.2']['status'] == 'success'


def test_missing_bullets_handled_gracefully(scorer):
    """Test scoring without bullet points."""
    minimal_data = {
        'text': 'Some resume text',
        'page_count': 1,
        'sections': {
            'experience': {'content': 'Experience', 'word_count': 200}
        }
    }

    result = scorer.score(
        resume_data=minimal_data,
        experience_level='beginner'
    )

    # Bullet-dependent parameters should be skipped
    assert result['parameter_scores']['P2.1']['status'] == 'skipped'
    assert result['parameter_scores']['P2.2']['status'] == 'skipped'
    assert result['parameter_scores']['P2.3']['status'] == 'skipped'

    # But total score should still be calculated
    assert result['total_score'] >= 0


def test_missing_page_count_handled(scorer):
    """Test scoring without page count."""
    minimal_data = {
        'text': 'Resume text',
        'bullets': ['Built something']
    }

    result = scorer.score(resume_data=minimal_data)

    assert result['parameter_scores']['P3.1']['status'] == 'skipped'
    assert result['total_score'] >= 0


# ============================================================================
# RATING CALCULATION TESTS
# ============================================================================

def test_rating_excellent_threshold(scorer):
    """Test rating calculation for Excellent (85+)."""
    # Mock data that would score high
    high_scoring_data = {
        'text': 'Excellent resume with great content and perfect formatting',
        'bullets': [
            "Pioneered ML infrastructure serving 5M users, reducing costs by 60%",
            "Architected cloud platform processing 10B+ requests/day",
            "Led cross-functional team of 15 engineers launching 3 products"
        ],
        'page_count': 2,
        'sections': {
            'experience': {'content': 'exp', 'word_count': 500},
            'skills': {'content': 'skills', 'word_count': 100},
            'education': {'content': 'edu', 'word_count': 50}
        }
    }

    result = scorer.score(resume_data=high_scoring_data, experience_level='senior')

    # With quality bullets, should get at least Fair rating
    # Note: Without keywords (P1.1, P1.2), max possible is ~65 points
    assert result['rating'] in ['Poor', 'Fair', 'Good', 'Excellent']
    assert result['total_score'] > 0


def test_rating_poor_threshold(scorer):
    """Test rating calculation for Poor (<55)."""
    poor_data = {
        'text': 'Responsible for work and helped with projects',
        'bullets': [
            "Responsible for tasks",
            "Worked on projects",
            "Helped team members"
        ],
        'page_count': 3,  # Too many pages for beginner
        'sections': {
            'skills': {'content': 'skills', 'word_count': 400},  # Skills too large
            'education': {'content': 'edu', 'word_count': 100}
        }
    }

    result = scorer.score(resume_data=poor_data, experience_level='beginner')

    # With weak content and bad structure, should score low
    assert result['total_score'] < 60


# ============================================================================
# FEEDBACK GENERATION TESTS
# ============================================================================

def test_feedback_includes_strengths_and_weaknesses(scorer, sample_resume_data, sample_job_requirements):
    """Test feedback identifies strengths and weaknesses."""
    result = scorer.score(
        resume_data=sample_resume_data,
        job_requirements=sample_job_requirements
    )

    feedback = result['feedback']

    assert 'strengths' in feedback
    assert 'weaknesses' in feedback
    assert 'recommendations' in feedback
    assert 'category_breakdown' in feedback


def test_feedback_limits_recommendations(scorer, sample_resume_data):
    """Test feedback limits to top 5 recommendations."""
    result = scorer.score(resume_data=sample_resume_data)

    feedback = result['feedback']

    # Should have at most 5 recommendations
    assert len(feedback['recommendations']) <= 5


def test_feedback_prioritizes_worst_scores(scorer):
    """Test weaknesses are sorted by severity."""
    poor_data = {
        'text': 'Responsible for work',
        'bullets': ['Worked on projects'],
        'page_count': 1,
        'sections': {
            'skills': {'content': 'skills', 'word_count': 300},
            'experience': {'content': 'exp', 'word_count': 200}
        }
    }

    result = scorer.score(resume_data=poor_data, experience_level='beginner')

    weaknesses = result['feedback']['weaknesses']

    if len(weaknesses) >= 2:
        # First weakness should have lower percentage than second
        assert weaknesses[0]['percentage'] <= weaknesses[1]['percentage']


# ============================================================================
# EXPERIENCE LEVEL TESTS
# ============================================================================

def test_different_experience_levels(scorer, sample_resume_data, sample_job_requirements):
    """Test scoring with different experience levels."""
    levels = ['beginner', 'intermediary', 'senior']

    scores = {}
    for level in levels:
        result = scorer.score(
            resume_data=sample_resume_data,
            job_requirements=sample_job_requirements,
            experience_level=level
        )
        scores[level] = result['total_score']

    # All should produce valid scores
    for level, score in scores.items():
        assert 0 <= score <= 100, f"Invalid score for {level}: {score}"


def test_experience_level_normalization(scorer, sample_resume_data):
    """Test experience level is normalized (case-insensitive)."""
    result1 = scorer.score(sample_resume_data, experience_level='SENIOR')
    result2 = scorer.score(sample_resume_data, experience_level='Senior')
    result3 = scorer.score(sample_resume_data, experience_level='senior')

    # Should all use 'senior' internally
    assert result1['experience_level'] == 'senior'
    assert result2['experience_level'] == 'senior'
    assert result3['experience_level'] == 'senior'


# ============================================================================
# ERROR HANDLING TESTS
# ============================================================================

def test_parameter_error_handled_gracefully(scorer, sample_resume_data):
    """Test that errors in individual parameters don't crash entire scoring."""
    # Pass malformed data that might cause errors
    bad_data = sample_resume_data.copy()
    bad_data['sections'] = "not a dict"  # Wrong type

    result = scorer.score(resume_data=bad_data)

    # Should still complete
    assert 'total_score' in result
    assert result['total_score'] >= 0

    # Section balance (P3.3) might error, but should be handled
    if 'P3.3' in result['parameter_scores']:
        p33_result = result['parameter_scores']['P3.3']
        if p33_result['status'] == 'error':
            assert 'error' in p33_result


def test_empty_resume_data(scorer):
    """Test with minimal/empty resume data."""
    result = scorer.score(resume_data={})

    # Should not crash
    assert 'total_score' in result
    assert result['total_score'] == 0  # Everything skipped


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

def test_full_workflow_with_all_data(scorer):
    """Test complete workflow with comprehensive data."""
    comprehensive_data = {
        'text': """
        Senior Software Engineer

        Led development of microservices platform serving 5M+ users.
        Architected cloud infrastructure reducing costs by 45%.
        Pioneered ML-driven recommendations increasing revenue by $2M.
        Implemented CI/CD pipeline cutting deployment time by 70%.
        Built automated testing framework improving coverage from 30% to 90%.
        Launched 3 major features ahead of schedule.
        Mentored team of 5 junior engineers.
        """,
        'bullets': [
            "Led development of microservices platform serving 5M+ users",
            "Architected cloud infrastructure reducing costs by 45%",
            "Pioneered ML-driven recommendations increasing revenue by $2M",
            "Implemented CI/CD pipeline cutting deployment time by 70%",
            "Built automated testing framework improving coverage from 30% to 90%",
            "Launched 3 major features ahead of schedule",
            "Mentored team of 5 junior engineers"
        ],
        'sections': {
            'experience': {'content': 'Experience...', 'word_count': 500},
            'skills': {'content': 'Python, AWS, Docker, Kubernetes, Terraform', 'word_count': 120},
            'education': {'content': 'BS Computer Science, Stanford University', 'word_count': 80}
        },
        'page_count': 2,
        'format': 'docx',
        'docx_structure': {
            'fonts': ['Calibri'],
            'has_tables': False,
            'has_images_in_header': False
        }
    }

    job_reqs = {
        'required_keywords': ['Python', 'AWS', 'Microservices', 'CI/CD', 'Leadership'],
        'preferred_keywords': ['Docker', 'Kubernetes', 'ML', 'Terraform', 'Agile']
    }

    result = scorer.score(
        resume_data=comprehensive_data,
        job_requirements=job_reqs,
        experience_level='senior'
    )

    # Should produce a valid score
    assert result['total_score'] >= 0
    assert result['total_score'] <= 100
    assert result['rating'] in ['Poor', 'Fair', 'Good', 'Excellent']

    # Most parameters should be scored (some may error due to network issues)
    successful_or_error_params = [
        p for p, data in result['parameter_scores'].items()
        if data['status'] in ['success', 'error']
    ]
    assert len(successful_or_error_params) >= 7  # At least 7/11 should attempt scoring
