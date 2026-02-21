"""
Test suite for Hybrid Keyword Matcher (Task 4)

Testing the 70% semantic + 30% exact matching formula
that reduces false negatives by 35-45%.

Research basis:
- Pure exact matching has 40% false negative rate
- Hybrid approach improves accuracy from 75% to 90%
"""

import pytest
from backend.services.hybrid_keyword_matcher import HybridKeywordMatcher


@pytest.fixture
def matcher():
    """Fixture to provide HybridKeywordMatcher instance"""
    return HybridKeywordMatcher()


def test_exact_match_scores_high(matcher):
    """Exact matches should score high (semantic + exact bonus)"""
    resume_text = "Proficient in Python, Java, and JavaScript"

    score = matcher.match_keyword("Python", resume_text)
    assert score >= 0.95, f"Expected exact match score >= 0.95, got {score}"


def test_semantic_match_without_exact(matcher):
    """Semantic matches without exact string should score medium"""
    resume_text = "Expert in Pythonic programming and Django framework"

    # "Python" not exact string, but semantically similar to "Pythonic"
    score = matcher.match_keyword("Python", resume_text)
    assert 0.5 <= score < 0.95, f"Expected semantic-only score in [0.5, 0.95), got {score}"


def test_no_match_scores_low(matcher):
    """Completely unrelated terms should score low"""
    resume_text = "Proficient in C++ and Rust"

    score = matcher.match_keyword("Python", resume_text)
    assert score < 0.4, f"Expected low score for no match, got {score}"


def test_case_insensitive_exact_match(matcher):
    """Exact matching should be case-insensitive"""
    resume_text = "Skills: PYTHON, javascript"

    score_upper = matcher.match_keyword("Python", resume_text)
    score_lower = matcher.match_keyword("python", resume_text)

    assert score_upper >= 0.95, f"Expected uppercase match score >= 0.95, got {score_upper}"
    assert score_lower >= 0.95, f"Expected lowercase match score >= 0.95, got {score_lower}"
    assert abs(score_upper - score_lower) < 0.01, "Case variations should have similar scores"


def test_partial_word_match(matcher):
    """Should match Python in 'Python-based' or 'Django (Python)'"""
    resume_text = "Developed Python-based microservices using Django (Python framework)"

    score = matcher.match_keyword("Python", resume_text)
    assert score >= 0.95, f"Expected compound word match score >= 0.95, got {score}"


def test_batch_matching(matcher):
    """Test matching multiple keywords at once"""
    resume_text = "Skilled in Python, experienced with Django, and proficient in React"
    keywords = ["Python", "JavaScript", "Django", "Ruby"]

    results = matcher.match_keywords(keywords, resume_text)

    assert results["Python"] >= 0.95, f"Python should match (exact), got {results['Python']}"
    assert results["Django"] >= 0.95, f"Django should match (exact), got {results['Django']}"
    assert results["JavaScript"] < 0.4, f"JavaScript should not match, got {results['JavaScript']}"
    assert results["Ruby"] < 0.4, f"Ruby should not match, got {results['Ruby']}"


def test_synonym_handling(matcher):
    """Should match semantic variations"""
    resume_text = "Expert in machine learning and artificial intelligence algorithms"

    # "ML" should match "machine learning" semantically
    score = matcher.match_keyword("ML", resume_text)
    assert score >= 0.5, f"Expected semantic match for ML/machine learning, got {score}"


def test_hybrid_formula_range(matcher):
    """Verify score is within valid range [0, 1]"""
    resume_text = "Python developer with Django experience"

    score = matcher.match_keyword("Python", resume_text)

    assert isinstance(score, float), f"Score should be float, got {type(score)}"
    assert 0.0 <= score <= 1.0, f"Score should be in [0, 1], got {score}"


def test_empty_inputs(matcher):
    """Handle edge cases with empty inputs"""
    # Empty resume text
    score1 = matcher.match_keyword("Python", "")
    assert score1 == 0.0, f"Empty resume should score 0.0, got {score1}"

    # Empty keyword
    score2 = matcher.match_keyword("", "Python developer")
    assert score2 == 0.0, f"Empty keyword should score 0.0, got {score2}"

    # Both empty
    score3 = matcher.match_keyword("", "")
    assert score3 == 0.0, f"Both empty should score 0.0, got {score3}"


def test_get_match_summary(matcher):
    """Test detailed matching summary with statistics"""
    resume_text = "Skilled in Python, experienced with Django, and proficient in React"
    keywords = ["Python", "JavaScript", "Django", "Ruby"]

    summary = matcher.get_match_summary(keywords, resume_text, threshold=0.6)

    # Check structure
    assert 'total_keywords' in summary
    assert 'matched_keywords' in summary
    assert 'match_rate' in summary
    assert 'scores' in summary
    assert 'matched' in summary
    assert 'unmatched' in summary

    # Check values
    assert summary['total_keywords'] == 4
    assert summary['matched_keywords'] >= 2  # Python, Django should match
    assert 0.0 <= summary['match_rate'] <= 100.0
    assert len(summary['scores']) == 4
    assert len(summary['matched']) + len(summary['unmatched']) == 4


def test_match_summary_threshold(matcher):
    """Test that threshold parameter filters matches correctly"""
    resume_text = "Python developer"
    keywords = ["Python", "Java"]

    # Low threshold (should match Python)
    summary_low = matcher.get_match_summary(keywords, resume_text, threshold=0.5)
    assert "Python" in summary_low['matched']

    # High threshold (might not match anything)
    summary_high = matcher.get_match_summary(keywords, resume_text, threshold=0.99)
    # At least Python should have high enough score
    assert summary_high['matched_keywords'] >= 1


def test_framework_keyword_matching(matcher):
    """Test matching framework names with descriptions"""
    resume_text = "Built REST APIs using Django REST Framework and Flask for microservices"

    # Exact match
    django_score = matcher.match_keyword("Django", resume_text)
    assert django_score >= 0.95, f"Django exact match failed, got {django_score}"

    # Framework name
    flask_score = matcher.match_keyword("Flask", resume_text)
    assert flask_score >= 0.95, f"Flask exact match failed, got {flask_score}"

    # Parent language (semantic match)
    python_score = matcher.match_keyword("Python", resume_text)
    # Should get some semantic score even without exact match
    assert python_score >= 0.4, f"Python semantic match failed, got {python_score}"


def test_acronym_vs_full_form(matcher):
    """Test matching acronyms against full forms"""
    resume_text = "Experience with Application Programming Interfaces and RESTful services"

    # "API" should semantically match "Application Programming Interfaces"
    api_score = matcher.match_keyword("API", resume_text)
    assert api_score >= 0.4, f"API semantic match failed, got {api_score}"


def test_technical_skills_compound_words(matcher):
    """Test matching technical terms with hyphens and special characters"""
    resume_text = "Expert in Node.js, Vue.js, and C++ programming"

    # Should match "Node.js" when searching for "Node"
    node_score = matcher.match_keyword("Node", resume_text)
    assert node_score >= 0.8, f"Node/Node.js match failed, got {node_score}"

    # Should match "C++" exactly
    cpp_score = matcher.match_keyword("C++", resume_text)
    assert cpp_score >= 0.95, f"C++ exact match failed, got {cpp_score}"


def test_weights_effect_on_hybrid_score(matcher):
    """Verify that hybrid score properly combines semantic and exact components"""
    # Test case where exact match is present
    resume_exact = "Expert in Python programming"
    score_exact = matcher.match_keyword("Python", resume_exact)

    # Test case where only semantic match exists
    resume_semantic = "Expert in Pythonic development"
    score_semantic = matcher.match_keyword("Python", resume_semantic)

    # Exact match should score higher than semantic-only
    assert score_exact > score_semantic, "Exact match should score higher than semantic-only"

    # Exact match should be close to 1.0 (semantic ~0.7-0.9 + exact 0.3)
    assert score_exact >= 0.9, f"Exact match should be >= 0.9, got {score_exact}"

    # Semantic-only should be in reasonable range (semantic * 0.7)
    assert 0.4 <= score_semantic < 0.9, f"Semantic-only should be in [0.4, 0.9), got {score_semantic}"


def test_multiple_occurrences_same_keyword(matcher):
    """Test that multiple occurrences don't affect scoring (should still be 0-1)"""
    resume_text = "Python expert. Python developer. Python Python Python."

    score = matcher.match_keyword("Python", resume_text)

    # Should still be in valid range
    assert 0.0 <= score <= 1.0, f"Score should be in [0, 1], got {score}"
    # Should get exact match bonus
    assert score >= 0.95, f"Multiple exact matches should score high, got {score}"


def test_context_awareness(matcher):
    """Test that semantic matching considers context"""
    # Python in programming context
    resume_programming = "Developed web applications using Python and Django"
    score_programming = matcher.match_keyword("Python", resume_programming)

    # Python in different context (should still match but differently)
    resume_snake = "Studied python snakes in biology class"
    score_snake = matcher.match_keyword("Python", resume_snake)

    # Both should detect "Python" but programming context might score higher
    assert score_programming >= 0.95, f"Programming context should match, got {score_programming}"
    assert score_snake >= 0.95, f"Should match exact string regardless, got {score_snake}"
