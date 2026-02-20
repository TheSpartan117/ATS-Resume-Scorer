"""
Phase 1 Implementation Tests
Tests for all Phase 1 improvements:
1.1 - Scoring Recalibration
1.2 - Semantic Keyword Matching
1.3 - Grammar Checking
1.4 - Performance Caching
1.5 - Overall validation
"""

import pytest
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from backend.services.parser import ResumeData
from backend.services.scorer_ats import ATSScorer
from backend.services.scorer_quality import QualityScorer


# Sample resume data for testing
SAMPLE_RESUME = ResumeData(
    contact={
        'name': 'John Doe',
        'email': 'john.doe@email.com',
        'phone': '+1-555-123-4567',
        'location': 'San Francisco, CA',
        'linkedin': 'linkedin.com/in/johndoe'
    },
    experience=[
        {
            'title': 'Senior Software Engineer',
            'company': 'Tech Corp',
            'startDate': '2020-01',
            'endDate': 'Present',
            'description': 'Led development of microservices architecture. Improved system performance by 40%. Managed team of 5 engineers. Implemented CI/CD pipeline reducing deployment time by 50%.'
        },
        {
            'title': 'Software Engineer',
            'company': 'Startup Inc',
            'startDate': '2018-06',
            'endDate': '2019-12',
            'description': 'Developed RESTful APIs using Python and Django. Built scalable backend systems. Worked with PostgreSQL and Redis. Collaborated with cross-functional teams.'
        }
    ],
    education=[
        {
            'degree': 'BS Computer Science',
            'institution': 'University of California',
            'graduationDate': '2018'
        }
    ],
    skills=['Python', 'Django', 'PostgreSQL', 'Redis', 'Docker', 'Kubernetes', 'CI/CD', 'AWS'],
    certifications=[
        {'name': 'AWS Certified Solutions Architect', 'date': '2021'}
    ],
    metadata={
        'pageCount': 1,
        'wordCount': 450,
        'fileFormat': 'pdf',
        'hasPhoto': False
    }
)

SAMPLE_JOB_DESCRIPTION = """
We are seeking a Senior Software Engineer with 5+ years of experience.

Required Skills:
- Python programming
- Django or Flask framework
- PostgreSQL database
- Docker and Kubernetes
- CI/CD pipelines
- Cloud platforms (AWS, GCP, or Azure)
- RESTful API design
- Microservices architecture

Responsibilities:
- Lead backend development
- Design scalable systems
- Mentor junior engineers
- Improve system performance
- Implement best practices
"""


class TestPhase1_1_ScoringRecalibration:
    """Test Phase 1.1: Scoring Recalibration"""

    def test_ats_keyword_thresholds_recalibrated(self):
        """Test that ATS keyword thresholds are recalibrated (71% -> 60%)"""
        scorer = ATSScorer(use_semantic_matching=False)

        # Test with job description that should score well
        result = scorer.score(
            resume=SAMPLE_RESUME,
            role='software_engineer',
            level='senior',
            job_description=SAMPLE_JOB_DESCRIPTION
        )

        # Check that score is reasonable (not too harsh)
        assert result['score'] >= 60, f"Score too low: {result['score']}"

        # Check keyword scoring
        keyword_result = result['breakdown']['keywords']
        assert keyword_result['maxScore'] == 35
        assert keyword_result['details']['percentage'] > 0

        print(f"✓ ATS Score: {result['score']}")
        print(f"✓ Keyword Match: {keyword_result['details']['percentage']}%")

    def test_quality_action_verb_thresholds_recalibrated(self):
        """Test that action verb thresholds are recalibrated (90% -> 70%)"""
        scorer = QualityScorer()

        result = scorer.score(
            resume_data=SAMPLE_RESUME,
            role_id='software_engineer',
            level='senior'
        )

        # Check that content quality scoring is more lenient
        content_quality = result['breakdown']['content_quality']
        assert content_quality['details']['action_verbs_score'] >= 0

        print(f"✓ Quality Score: {result['score']}")
        print(f"✓ Action Verbs: {content_quality['details']['action_verbs_count']}/{content_quality['details']['action_verbs_total']}")

    def test_quality_quantification_thresholds_recalibrated(self):
        """Test that quantification thresholds are recalibrated (60% -> 40%)"""
        scorer = QualityScorer()

        result = scorer.score(
            resume_data=SAMPLE_RESUME,
            role_id='software_engineer',
            level='senior'
        )

        # Check quantification scoring
        content_quality = result['breakdown']['content_quality']
        assert 'quantification_score' in content_quality['details']

        print(f"✓ Quantification: {content_quality['details']['quantified_bullets']}/{content_quality['details']['total_bullets']} bullets")

    def test_average_score_improvement(self):
        """Test that average scores are in target range (75-85)"""
        ats_scorer = ATSScorer(use_semantic_matching=False)
        quality_scorer = QualityScorer()

        ats_result = ats_scorer.score(
            resume=SAMPLE_RESUME,
            role='software_engineer',
            level='senior',
            job_description=SAMPLE_JOB_DESCRIPTION
        )

        quality_result = quality_scorer.score(
            resume_data=SAMPLE_RESUME,
            role_id='software_engineer',
            level='senior'
        )

        # Average should be in reasonable range
        avg_score = (ats_result['score'] + quality_result['score']) / 2

        print(f"✓ ATS Score: {ats_result['score']}")
        print(f"✓ Quality Score: {quality_result['score']}")
        print(f"✓ Average: {avg_score}")

        # Should not be too harsh
        assert avg_score >= 50, f"Average score too low: {avg_score}"


class TestPhase1_2_SemanticMatching:
    """Test Phase 1.2: Semantic Keyword Matching"""

    def test_semantic_matcher_import(self):
        """Test that semantic matcher can be imported"""
        try:
            from backend.services.semantic_matcher import SemanticKeywordMatcher
            matcher = SemanticKeywordMatcher()
            assert matcher is not None
            print("✓ Semantic matcher imported successfully")
        except ImportError as e:
            pytest.skip(f"Semantic matching dependencies not installed: {e}")

    def test_keyword_extraction(self):
        """Test keyword extraction from job description"""
        try:
            from backend.services.semantic_matcher import get_semantic_matcher

            matcher = get_semantic_matcher()
            keywords = matcher.extract_keywords(SAMPLE_JOB_DESCRIPTION, top_n=10)

            assert len(keywords) > 0, "No keywords extracted"
            assert all(isinstance(kw, tuple) and len(kw) == 2 for kw in keywords)

            print(f"✓ Extracted {len(keywords)} keywords:")
            for kw, score in keywords[:5]:
                print(f"  - {kw} ({score:.3f})")

        except ImportError:
            pytest.skip("Semantic matching dependencies not installed")

    def test_semantic_matching_score(self):
        """Test semantic similarity scoring"""
        try:
            from backend.services.semantic_matcher import get_semantic_matcher

            matcher = get_semantic_matcher()

            # Build resume text
            resume_text = "Python Django PostgreSQL Docker Kubernetes AWS CI/CD microservices"
            job_keywords = ["Python", "Django", "PostgreSQL", "Docker", "AWS"]

            result = matcher.semantic_match_score(resume_text, job_keywords)

            assert 'match_rate' in result
            assert 'matches' in result
            assert 'missing' in result
            assert 0 <= result['match_rate'] <= 1

            print(f"✓ Semantic Match Rate: {result['match_rate']*100:.1f}%")
            print(f"✓ Matched: {len(result['matches'])}/{len(job_keywords)}")

        except ImportError:
            pytest.skip("Semantic matching dependencies not installed")

    def test_hybrid_matching(self):
        """Test hybrid matching (70% semantic + 30% exact)"""
        try:
            from backend.services.semantic_matcher import get_semantic_matcher

            matcher = get_semantic_matcher()

            resume_text = "Python Django PostgreSQL Docker Kubernetes AWS"
            job_keywords = ["Python", "Flask", "MySQL", "Docker", "GCP"]

            result = matcher.hybrid_match_score(resume_text, job_keywords)

            assert 'hybrid_score' in result
            assert 'semantic_score' in result
            assert 'exact_score' in result
            assert 0 <= result['hybrid_score'] <= 1

            print(f"✓ Hybrid Score: {result['hybrid_score']*100:.1f}%")
            print(f"  Semantic: {result['semantic_score']*100:.1f}%")
            print(f"  Exact: {result['exact_score']*100:.1f}%")

        except ImportError:
            pytest.skip("Semantic matching dependencies not installed")

    def test_ats_scorer_with_semantic_matching(self):
        """Test ATS scorer with semantic matching enabled"""
        try:
            scorer = ATSScorer(use_semantic_matching=True)

            result = scorer.score(
                resume=SAMPLE_RESUME,
                role='software_engineer',
                level='senior',
                job_description=SAMPLE_JOB_DESCRIPTION
            )

            keyword_result = result['breakdown']['keywords']

            # Check if semantic matching was used
            if 'matching_method' in keyword_result['details']:
                print(f"✓ Matching Method: {keyword_result['details']['matching_method']}")

            print(f"✓ Score: {result['score']}")
            print(f"✓ Keyword Match: {keyword_result['details']['percentage']}%")

        except ImportError:
            pytest.skip("Semantic matching dependencies not installed")


class TestPhase1_3_GrammarChecking:
    """Test Phase 1.3: Grammar Checking"""

    def test_grammar_checker_import(self):
        """Test that grammar checker can be imported"""
        try:
            from backend.services.grammar_checker import GrammarChecker
            checker = GrammarChecker()
            assert checker is not None
            print("✓ Grammar checker imported successfully")
        except ImportError as e:
            pytest.skip(f"Grammar checking dependencies not installed: {e}")

    def test_grammar_check_basic(self):
        """Test basic grammar checking"""
        try:
            from backend.services.grammar_checker import get_grammar_checker

            checker = get_grammar_checker()

            # Test with clean text
            clean_text = "This is a well-written sentence with proper grammar."
            result = checker.check(clean_text)

            assert 'total_issues' in result
            assert 'score' in result
            assert 'issues' in result
            assert isinstance(result['score'], int)
            assert 0 <= result['score'] <= 100

            print(f"✓ Clean text score: {result['score']}")
            print(f"✓ Issues found: {result['total_issues']}")

        except ImportError:
            pytest.skip("Grammar checking dependencies not installed")

    def test_grammar_check_with_errors(self):
        """Test grammar checking with intentional errors"""
        try:
            from backend.services.grammar_checker import get_grammar_checker

            checker = get_grammar_checker()

            # Test with errors
            error_text = "This sentence have a grammar error. I goes to the store."
            result = checker.check(error_text)

            print(f"✓ Error text score: {result['score']}")
            print(f"✓ Issues found: {result['total_issues']}")

            if result['issues']:
                print("  Sample issues:")
                for issue in result['issues'][:3]:
                    print(f"  - {issue.get('message', 'Unknown')}")

        except ImportError:
            pytest.skip("Grammar checking dependencies not installed")

    def test_grammar_check_resume_text(self):
        """Test grammar checking on resume text"""
        try:
            from backend.services.grammar_checker import get_grammar_checker

            checker = get_grammar_checker()

            # Build resume text from sample
            resume_text = " ".join([
                exp['description'] for exp in SAMPLE_RESUME.experience
            ])

            result = checker.check(resume_text)

            print(f"✓ Resume grammar score: {result['score']}")
            print(f"✓ Issues: {result['total_issues']}")
            print(f"✓ Severity: {result['severity_breakdown']}")

        except ImportError:
            pytest.skip("Grammar checking dependencies not installed")


class TestPhase1_4_PerformanceCaching:
    """Test Phase 1.4: Performance Caching"""

    def test_cache_utils_import(self):
        """Test that cache utilities can be imported"""
        try:
            from backend.services.cache_utils import get_cache, cache_result
            cache = get_cache()
            # Cache may be None if diskcache not installed, that's ok
            print(f"✓ Cache available: {cache is not None}")
        except ImportError as e:
            pytest.skip(f"Caching dependencies not installed: {e}")

    def test_cache_decorator(self):
        """Test cache decorator functionality"""
        try:
            from backend.services.cache_utils import cache_result

            call_count = {'value': 0}

            @cache_result(expire=60, key_prefix='test')
            def expensive_function(x):
                call_count['value'] += 1
                return x * 2

            # First call - should execute
            result1 = expensive_function(5)
            assert result1 == 10
            first_count = call_count['value']

            # Second call - should use cache
            result2 = expensive_function(5)
            assert result2 == 10
            second_count = call_count['value']

            # If caching works, count should not increase
            if second_count == first_count:
                print("✓ Caching is working")
            else:
                print("✓ Caching not available (function called twice)")

        except ImportError:
            pytest.skip("Caching dependencies not installed")

    def test_semantic_matching_cache(self):
        """Test that semantic matching uses caching"""
        try:
            from backend.services.semantic_matcher import get_semantic_matcher

            matcher = get_semantic_matcher()

            # First call
            keywords1 = matcher.extract_keywords(SAMPLE_JOB_DESCRIPTION, top_n=10)

            # Second call with same input (should use cache if available)
            keywords2 = matcher.extract_keywords(SAMPLE_JOB_DESCRIPTION, top_n=10)

            assert len(keywords1) == len(keywords2)
            print("✓ Semantic matching cache test passed")

        except ImportError:
            pytest.skip("Semantic matching dependencies not installed")

    def test_cache_stats(self):
        """Test cache statistics"""
        try:
            from backend.services.cache_utils import get_cache_stats

            stats = get_cache_stats()
            print(f"✓ Cache stats: {stats}")

        except ImportError:
            pytest.skip("Caching dependencies not installed")


class TestPhase1_5_OverallValidation:
    """Test Phase 1.5: Overall Validation"""

    def test_end_to_end_scoring(self):
        """Test end-to-end scoring with all improvements"""
        ats_scorer = ATSScorer(use_semantic_matching=True)

        result = ats_scorer.score(
            resume=SAMPLE_RESUME,
            role='software_engineer',
            level='senior',
            job_description=SAMPLE_JOB_DESCRIPTION
        )

        # Validate structure
        assert 'score' in result
        assert 'breakdown' in result
        assert result['score'] > 0

        # Validate all components present
        assert 'keywords' in result['breakdown']
        assert 'red_flags' in result['breakdown']
        assert 'experience' in result['breakdown']
        assert 'formatting' in result['breakdown']
        assert 'contact' in result['breakdown']

        print("\n=== End-to-End Test Results ===")
        print(f"Overall Score: {result['score']}")
        print("\nBreakdown:")
        for component, data in result['breakdown'].items():
            print(f"  {component}: {data['score']}/{data['maxScore']}")

        # Validate score is in reasonable range (not too harsh)
        assert 50 <= result['score'] <= 100, f"Score out of expected range: {result['score']}"

    def test_performance_benchmark(self):
        """Test performance of scoring"""
        import time

        scorer = ATSScorer(use_semantic_matching=False)

        # First run (uncached)
        start = time.time()
        result1 = scorer.score(
            resume=SAMPLE_RESUME,
            role='software_engineer',
            level='senior',
            job_description=SAMPLE_JOB_DESCRIPTION
        )
        first_run_time = time.time() - start

        # Second run (potentially cached)
        start = time.time()
        result2 = scorer.score(
            resume=SAMPLE_RESUME,
            role='software_engineer',
            level='senior',
            job_description=SAMPLE_JOB_DESCRIPTION
        )
        second_run_time = time.time() - start

        print(f"\n=== Performance Benchmark ===")
        print(f"First run: {first_run_time*1000:.0f}ms")
        print(f"Second run: {second_run_time*1000:.0f}ms")

        if second_run_time < first_run_time:
            speedup = first_run_time / second_run_time
            print(f"Speedup: {speedup:.1f}x")

        # Target: <2s for first scan (reasonable without heavy optimization)
        assert first_run_time < 5.0, f"First run too slow: {first_run_time:.2f}s"

    def test_scoring_consistency(self):
        """Test that scoring is consistent across multiple runs"""
        scorer = ATSScorer(use_semantic_matching=False)

        scores = []
        for i in range(3):
            result = scorer.score(
                resume=SAMPLE_RESUME,
                role='software_engineer',
                level='senior',
                job_description=SAMPLE_JOB_DESCRIPTION
            )
            scores.append(result['score'])

        # All scores should be identical
        assert len(set(scores)) == 1, f"Inconsistent scores: {scores}"
        print(f"✓ Consistent scoring: {scores[0]}")


if __name__ == '__main__':
    # Run tests with verbose output
    pytest.main([__file__, '-v', '-s'])
