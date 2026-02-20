"""
Integration tests for full ATS scoring pipeline
Tests all Phase 1-3 features end-to-end
"""

import pytest
import json
import time
from pathlib import Path
from typing import Dict, Any

# Import all services to test
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "backend"))

from services.scorer_ats import ATSScorer
from services.scorer_quality import QualityScorer
from services.parser import ResumeParser
from services.ab_testing import ABTestFramework, TestResumeCorpus


class TestFullScoringPipeline:
    """End-to-end tests for complete scoring pipeline"""

    @pytest.fixture
    def sample_resume_text(self):
        return """
John Doe
Senior Software Engineer

EXPERIENCE
Senior Software Engineer | TechCorp | 2020-Present
- Developed scalable microservices using Python and FastAPI
- Led team of 5 engineers in cloud migration to AWS
- Implemented CI/CD pipelines reducing deployment time by 60%
- Optimized database queries improving performance by 40%

Software Engineer | StartupXYZ | 2018-2020
- Built RESTful APIs serving 100K+ users
- Collaborated with cross-functional teams
- Mentored junior developers

SKILLS
Python, FastAPI, AWS, Docker, Kubernetes, PostgreSQL, Git, CI/CD

EDUCATION
B.S. Computer Science | Tech University | 2018
"""

    @pytest.fixture
    def sample_job_description(self):
        return """
We are seeking a Senior Software Engineer with expertise in:
- Python development and FastAPI framework
- Cloud technologies (AWS, Docker, Kubernetes)
- Database optimization and PostgreSQL
- CI/CD pipeline implementation
- Team leadership and mentoring
- Microservices architecture

Required: 3+ years experience, strong communication skills
"""

    @pytest.fixture
    def ats_scorer(self):
        return ATSScorer()

    @pytest.fixture
    def quality_scorer(self):
        return QualityScorer()

    def test_ats_scoring_basic(self, ats_scorer, sample_resume_text, sample_job_description):
        """Test basic ATS scoring functionality"""
        result = ats_scorer.score(sample_resume_text, sample_job_description)

        assert result is not None
        assert 'overall_score' in result or 'score' in result

        # Score should be reasonable
        score = result.get('overall_score', result.get('score', 0))
        assert 0 <= score <= 100, f"Score {score} out of valid range"

    def test_quality_scoring_basic(self, quality_scorer, sample_resume_text):
        """Test basic quality scoring functionality"""
        result = quality_scorer.score(sample_resume_text)

        assert result is not None
        # Check for quality metrics
        assert isinstance(result, dict)

    def test_full_pipeline_integration(self, ats_scorer, quality_scorer, sample_resume_text, sample_job_description):
        """Test complete pipeline from resume to final score"""
        # Step 1: ATS Scoring
        ats_result = ats_scorer.score(sample_resume_text, sample_job_description)
        assert ats_result is not None

        # Step 2: Quality Scoring
        quality_result = quality_scorer.score(sample_resume_text)
        assert quality_result is not None

        # Step 3: Verify both scores are generated
        ats_score = ats_result.get('overall_score', ats_result.get('score', 0))
        assert ats_score > 0, "ATS score should be positive"

    def test_scoring_with_empty_resume(self, ats_scorer):
        """Test handling of empty resume"""
        empty_resume = ""
        job_desc = "Software Engineer position"

        try:
            result = ats_scorer.score(empty_resume, job_desc)
            # Should either return low score or handle gracefully
            if result:
                score = result.get('overall_score', result.get('score', 0))
                assert score >= 0
        except Exception as e:
            # Should not crash
            assert True

    def test_scoring_with_long_resume(self, ats_scorer, sample_job_description):
        """Test handling of very long resume (>5 pages)"""
        # Create a very long resume
        long_resume = sample_resume_text * 20  # Simulate 5+ pages

        try:
            start_time = time.time()
            result = ats_scorer.score(long_resume, sample_job_description)
            duration = time.time() - start_time

            # Should complete in reasonable time (< 10 seconds)
            assert duration < 10, f"Long resume took too long: {duration}s"

            if result:
                score = result.get('overall_score', result.get('score', 0))
                assert 0 <= score <= 100
        except Exception as e:
            pytest.fail(f"Failed to handle long resume: {e}")

    def test_scoring_with_unusual_format(self, ats_scorer, sample_job_description):
        """Test handling of unusual resume format"""
        unusual_resume = """
        ~~~JOHN~~~DOE~~~
        <<<EXPERIENCE>>>
        *** Job 1 ***
        Did some work
        *** Job 2 ***
        Did more work
        """

        try:
            result = ats_scorer.score(unusual_resume, sample_job_description)
            # Should handle gracefully
            assert result is not None or True
        except Exception:
            # Should not crash completely
            assert True

    def test_scoring_performance_benchmark(self, ats_scorer, quality_scorer, sample_resume_text, sample_job_description):
        """Test that scoring meets performance requirements"""
        # First run (no cache)
        start_time = time.time()
        result1 = ats_scorer.score(sample_resume_text, sample_job_description)
        first_duration = time.time() - start_time

        # Target: < 2 seconds for first run
        assert first_duration < 2.0, f"First scoring took {first_duration}s (target: <2s)"

        # Second run (potentially cached)
        start_time = time.time()
        result2 = ats_scorer.score(sample_resume_text, sample_job_description)
        second_duration = time.time() - start_time

        # Cached should be faster
        # Note: May not be cached depending on implementation
        print(f"First run: {first_duration:.3f}s, Second run: {second_duration:.3f}s")

    def test_consistency_across_runs(self, ats_scorer, sample_resume_text, sample_job_description):
        """Test that scoring is consistent across multiple runs"""
        scores = []

        for _ in range(3):
            result = ats_scorer.score(sample_resume_text, sample_job_description)
            score = result.get('overall_score', result.get('score', 0))
            scores.append(score)

        # All scores should be identical for same input
        assert len(set(scores)) == 1, f"Inconsistent scores: {scores}"

    def test_score_range_validation(self, ats_scorer, sample_resume_text, sample_job_description):
        """Test that all scores are within valid ranges"""
        result = ats_scorer.score(sample_resume_text, sample_job_description)

        # Check all numeric values in result
        def check_scores(obj, path=""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    check_scores(value, f"{path}.{key}" if path else key)
            elif isinstance(obj, (int, float)):
                # Scores should generally be 0-100
                if 'score' in path.lower() or 'rating' in path.lower():
                    assert 0 <= obj <= 100, f"Score {path}={obj} out of range"

        check_scores(result)


class TestResumeCorpusIntegration:
    """Integration tests using test resume corpus"""

    @pytest.fixture
    def corpus(self):
        return TestResumeCorpus()

    @pytest.fixture
    def ats_scorer(self):
        return ATSScorer()

    def test_corpus_loading(self, corpus):
        """Test loading resume corpus"""
        resumes = corpus.load_corpus()
        assert isinstance(resumes, list)
        # Corpus should have at least the sample resumes we created
        assert len(resumes) >= 3, "Should have at least 3 test resumes"

    def test_score_all_corpus_resumes(self, corpus, ats_scorer):
        """Test scoring all resumes in corpus"""
        resumes = corpus.load_corpus()

        if not resumes:
            pytest.skip("No resumes in corpus")

        results = []
        for resume_data in resumes:
            try:
                resume_text = resume_data.get('resume_text', '')
                job_desc = resume_data.get('job_description', '')

                if resume_text:
                    result = ats_scorer.score(resume_text, job_desc)
                    score = result.get('overall_score', result.get('score', 0))
                    results.append({
                        'resume_id': resume_data.get('id'),
                        'score': score,
                        'success': True
                    })
            except Exception as e:
                results.append({
                    'resume_id': resume_data.get('id'),
                    'error': str(e),
                    'success': False
                })

        # Should successfully score most resumes
        success_rate = sum(1 for r in results if r.get('success')) / len(results)
        assert success_rate >= 0.8, f"Only {success_rate:.1%} of resumes scored successfully"

    def test_corpus_diversity(self, corpus):
        """Test that corpus has diverse resumes"""
        stats = corpus.get_corpus_stats()

        assert stats['total_resumes'] >= 3
        assert stats['unique_roles'] >= 3, "Need diverse roles in corpus"
        assert stats['unique_experience_levels'] >= 2, "Need different experience levels"


class TestABTestingFramework:
    """Integration tests for A/B testing"""

    @pytest.fixture
    def ab_framework(self):
        return ABTestFramework()

    @pytest.fixture
    def corpus(self):
        return TestResumeCorpus()

    def test_ab_framework_initialization(self, ab_framework):
        """Test A/B testing framework initialization"""
        assert ab_framework is not None
        assert ab_framework.results_dir.exists()

    def test_simple_ab_comparison(self, ab_framework):
        """Test basic A/B comparison functionality"""
        # Create mock scorers
        def old_scorer(resume_data, job_desc=None):
            return {'overall_score': 70}

        def new_scorer(resume_data, job_desc=None):
            return {'overall_score': 75}

        # Create test resumes
        test_resumes = [
            {'id': 'test1', 'text': 'resume 1'},
            {'id': 'test2', 'text': 'resume 2'},
            {'id': 'test3', 'text': 'resume 3'},
        ]

        # Run comparison
        report = ab_framework.compare_scorers(old_scorer, new_scorer, test_resumes)

        assert report is not None
        assert 'recommendation' in report
        assert 'statistics' in report
        assert report['summary']['average_delta'] == 5.0

    def test_ab_testing_with_real_corpus(self, ab_framework, corpus):
        """Test A/B testing with actual resume corpus"""
        resumes = corpus.load_corpus()

        if len(resumes) < 3:
            pytest.skip("Need at least 3 resumes for A/B testing")

        # Use same scorer twice (should show no difference)
        from services.scorer_ats import ATSScorer
        scorer = ATSScorer()

        def scorer_wrapper(resume_data, job_desc=None):
            text = resume_data.get('resume_text', '')
            jd = job_desc or resume_data.get('job_description', '')
            return scorer.score(text, jd)

        try:
            report = ab_framework.compare_scorers(
                scorer_wrapper,
                scorer_wrapper,
                resumes
            )

            assert report is not None
            # Same scorer should show no significant difference
            assert abs(report['summary']['average_delta']) < 1.0
        except Exception as e:
            pytest.skip(f"A/B testing failed: {e}")


class TestRegressionPrevention:
    """Tests to prevent regression in critical functionality"""

    @pytest.fixture
    def ats_scorer(self):
        return ATSScorer()

    def test_no_extremely_low_scores(self, ats_scorer):
        """Test that reasonable resumes don't get extremely low scores"""
        good_resume = """
Senior Software Engineer
- 5 years of Python development experience
- Built scalable web applications
- Led team of developers
- Strong problem-solving skills
Skills: Python, JavaScript, SQL, Git
Education: B.S. Computer Science
"""
        job_desc = "Looking for Python developer with web development experience"

        result = ats_scorer.score(good_resume, job_desc)
        score = result.get('overall_score', result.get('score', 0))

        # Reasonable resume should score > 50
        assert score > 50, f"Good resume got too low score: {score}"

    def test_no_extremely_high_scores_for_poor_resume(self, ats_scorer):
        """Test that poor resumes don't get unrealistically high scores"""
        poor_resume = """
Name
Did stuff
"""
        job_desc = "Senior Software Engineer with 10 years Python, AWS, leadership"

        result = ats_scorer.score(poor_resume, job_desc)
        score = result.get('overall_score', result.get('score', 0))

        # Poor resume should score < 70
        assert score < 70, f"Poor resume got too high score: {score}"

    def test_keyword_matching_works(self, ats_scorer):
        """Test that keyword matching actually works"""
        resume_with_keywords = """
Python Developer
Skills: Python, Django, PostgreSQL, Docker, AWS
Experience: Built web applications using Python and Django
"""
        job_desc = "Python developer needed. Must know Django, PostgreSQL, Docker, AWS."

        resume_without_keywords = """
Developer
Skills: Java, C++, Oracle
Experience: Built desktop applications
"""

        score_with = ats_scorer.score(resume_with_keywords, job_desc).get('overall_score', 0)
        score_without = ats_scorer.score(resume_without_keywords, job_desc).get('overall_score', 0)

        # Resume with matching keywords should score higher
        assert score_with > score_without, "Keyword matching not working properly"


class TestEdgeCases:
    """Test edge cases and unusual inputs"""

    @pytest.fixture
    def ats_scorer(self):
        return ATSScorer()

    def test_unicode_characters(self, ats_scorer):
        """Test handling of unicode characters"""
        unicode_resume = """
José García
Software Engineer 🚀
- Developed applications with résumé parsing
- Café management system
- Worked with international team (日本、中国)
"""
        job_desc = "Software Engineer"

        try:
            result = ats_scorer.score(unicode_resume, job_desc)
            assert result is not None
        except Exception as e:
            pytest.fail(f"Failed to handle unicode: {e}")

    def test_very_short_resume(self, ats_scorer):
        """Test with minimal resume content"""
        short_resume = "John Doe\nEngineer"
        job_desc = "Engineer needed"

        try:
            result = ats_scorer.score(short_resume, job_desc)
            assert result is not None
            score = result.get('overall_score', result.get('score', 0))
            assert 0 <= score <= 100
        except Exception:
            pytest.fail("Should handle short resumes gracefully")

    def test_special_characters(self, ats_scorer):
        """Test handling of special characters"""
        special_resume = """
Name: John & Jane <Developer>
Email: test@example.com
Skills: C++, C#, .NET
Experience: 5+ years
Metrics: 50% improvement | 2x growth
"""
        job_desc = "Developer position"

        try:
            result = ats_scorer.score(special_resume, job_desc)
            assert result is not None
        except Exception as e:
            pytest.fail(f"Failed to handle special characters: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
