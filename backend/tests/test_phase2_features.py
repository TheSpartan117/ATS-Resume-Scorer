"""
Comprehensive tests for Phase 2: Core Features

Tests all Phase 2 components:
1. ATS Parsing Simulation
2. Hard Skills vs Soft Skills Categorization
3. Confidence Scoring
4. Semantic Matching (Phase 1 dependency)
"""

import pytest
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from services.ats_simulator import ATSSimulator, analyze_ats_compatibility
from services.skills_categorizer import SkillsCategorizer, analyze_skills
from services.confidence_scorer import (
    ConfidenceScorer,
    add_confidence_intervals,
    format_score_with_confidence
)
from services.semantic_matcher import SemanticKeywordMatcher


# Sample test data

SAMPLE_RESUME_TEXT = """
John Doe
john.doe@email.com | (555) 123-4567 | San Francisco, CA

PROFESSIONAL SUMMARY
Senior Software Engineer with 5+ years of experience in Python, Java, and AWS.
Strong leadership and communication skills with proven track record of delivering
complex projects on time.

EXPERIENCE
Senior Software Engineer | Tech Corp | 2020-Present
- Led team of 5 engineers in developing microservices architecture using Docker and Kubernetes
- Improved system performance by 40% through optimization
- Collaborated with cross-functional teams to deliver features
- Mentored junior developers and conducted code reviews

Software Engineer | StartupXYZ | 2018-2020
- Developed REST APIs using Python and FastAPI
- Implemented CI/CD pipelines with GitHub Actions
- Worked with PostgreSQL and Redis for data storage

EDUCATION
B.S. Computer Science | University of California | 2018

SKILLS
Python, Java, JavaScript, AWS, Docker, Kubernetes, PostgreSQL, Redis,
REST APIs, Microservices, CI/CD, Agile, Leadership, Communication, Teamwork
"""

SAMPLE_JOB_DESCRIPTION = """
Senior Software Engineer

We're looking for a Senior Software Engineer with:
- 5+ years of Python development experience
- Experience with AWS and cloud infrastructure
- Docker and Kubernetes expertise
- Strong problem-solving and communication skills
- Leadership experience
- Bachelor's degree in Computer Science

Nice to have:
- FastAPI or Django experience
- PostgreSQL knowledge
- CI/CD pipeline experience
"""

RESUME_WITH_TABLES = """
John Doe
Contact: john@email.com

Experience:
|--------------------|----------|
| Company            | Years    |
|--------------------|----------|
| Tech Corp          | 3 years  |
| StartupXYZ         | 2 years  |
|--------------------|----------|
"""

RESUME_SIMPLE = """
John Doe
Email: john@email.com
Phone: 555-1234

Experience:
- Software Engineer at Tech Corp (2020-2023)
- Junior Developer at StartupXYZ (2018-2020)

Education:
- B.S. Computer Science, 2018

Skills: Python, Java, AWS
"""


# Test Suite 1: ATS Simulator Tests

class TestATSSimulator:
    """Test ATS platform simulation"""

    def test_simulator_initialization(self):
        """Test that ATSSimulator initializes correctly"""
        simulator = ATSSimulator()
        assert simulator is not None
        assert len(simulator.platforms) == 3
        assert 'Taleo' in simulator.platforms
        assert 'Workday' in simulator.platforms
        assert 'Greenhouse' in simulator.platforms

    def test_taleo_simulation_with_tables(self):
        """Test Taleo simulation detects tables (critical issue)"""
        simulator = ATSSimulator()
        result = simulator.simulate_taleo(RESUME_WITH_TABLES)

        assert result['platform'] == 'Taleo (Oracle)'
        assert result['pass_probability'] < 80  # Tables should reduce score
        assert len(result['issues']) > 0

        # Check that table issue is detected
        issue_messages = [issue['message'] for issue in result['issues']]
        assert any('table' in msg.lower() for msg in issue_messages)

    def test_taleo_simulation_simple_resume(self):
        """Test Taleo simulation with simple, compatible resume"""
        simulator = ATSSimulator()
        result = simulator.simulate_taleo(RESUME_SIMPLE)

        assert result['platform'] == 'Taleo (Oracle)'
        assert result['pass_probability'] >= 70  # Should pass
        assert result['rating'] in ['Good', 'Very Good', 'Excellent']

    def test_workday_simulation(self):
        """Test Workday simulation (moderate parser)"""
        simulator = ATSSimulator()
        result = simulator.simulate_workday(SAMPLE_RESUME_TEXT)

        assert result['platform'] == 'Workday'
        assert result['market_share'] == '45%'
        assert 0 <= result['pass_probability'] <= 100
        assert 'issues' in result
        assert 'parsing_notes' in result

    def test_greenhouse_simulation(self):
        """Test Greenhouse simulation (most lenient)"""
        simulator = ATSSimulator()
        result = simulator.simulate_greenhouse(SAMPLE_RESUME_TEXT)

        assert result['platform'] == 'Greenhouse'
        assert result['market_share'] == '15%'
        assert result['pass_probability'] >= 80  # Should be high (lenient)
        assert result['rating'] in ['Very Good', 'Excellent']

    def test_overall_ats_compatibility(self):
        """Test overall ATS compatibility across all platforms"""
        simulator = ATSSimulator()
        result = simulator.get_overall_ats_compatibility(SAMPLE_RESUME_TEXT)

        assert 'overall_score' in result
        assert 'platforms' in result
        assert 'Taleo' in result['platforms']
        assert 'Workday' in result['platforms']
        assert 'Greenhouse' in result['platforms']
        assert 'recommendations' in result
        assert 0 <= result['overall_score'] <= 100

    def test_analyze_ats_compatibility_convenience(self):
        """Test convenience function"""
        result = analyze_ats_compatibility(SAMPLE_RESUME_TEXT)

        assert result is not None
        assert 'overall_score' in result
        assert 'platforms' in result


# Test Suite 2: Skills Categorizer Tests

class TestSkillsCategorizer:
    """Test hard/soft skills categorization"""

    def test_categorizer_initialization(self):
        """Test that SkillsCategorizer initializes correctly"""
        categorizer = SkillsCategorizer()
        assert categorizer is not None
        assert len(categorizer.hard_skills_set) > 0
        assert len(categorizer.soft_skills_set) > 0

    def test_extract_hard_skills(self):
        """Test extraction of hard skills from resume"""
        categorizer = SkillsCategorizer()
        result = categorizer.extract_skills(SAMPLE_RESUME_TEXT)

        assert 'hard_skills' in result
        assert 'soft_skills' in result

        hard_skills = result['hard_skills']
        assert 'python' in hard_skills
        assert 'aws' in hard_skills
        assert 'docker' in hard_skills
        assert 'kubernetes' in hard_skills

    def test_extract_soft_skills(self):
        """Test extraction of soft skills from resume"""
        categorizer = SkillsCategorizer()
        result = categorizer.extract_skills(SAMPLE_RESUME_TEXT)

        soft_skills = result['soft_skills']
        assert 'leadership' in soft_skills
        assert 'communication' in soft_skills
        assert 'teamwork' in soft_skills

    def test_categorize_with_job_description(self):
        """Test skills categorization with job description matching"""
        categorizer = SkillsCategorizer()
        result = categorizer.categorize_skills(SAMPLE_RESUME_TEXT, SAMPLE_JOB_DESCRIPTION)

        assert 'resume_skills' in result
        assert 'job_skills' in result
        assert 'hard_skills_analysis' in result
        assert 'soft_skills_analysis' in result
        assert 'overall_match' in result
        assert 'recommendations' in result

        # Check match rates
        hard_analysis = result['hard_skills_analysis']
        assert 'match_rate' in hard_analysis
        assert 'matched_skills' in hard_analysis
        assert 'missing_skills' in hard_analysis
        assert 0 <= hard_analysis['match_rate'] <= 100

    def test_skills_match_calculation(self):
        """Test match rate calculation between resume and job"""
        categorizer = SkillsCategorizer()
        result = categorizer.categorize_skills(SAMPLE_RESUME_TEXT, SAMPLE_JOB_DESCRIPTION)

        # Should have good match for hard skills (Python, AWS, Docker mentioned)
        hard_match = result['hard_skills_analysis']['match_rate']
        assert hard_match > 50  # Should match majority of hard skills

        # Check that matched skills are identified
        matched = result['hard_skills_analysis']['matched_skills']
        assert len(matched) > 0

    def test_analyze_skills_convenience(self):
        """Test convenience function"""
        result = analyze_skills(SAMPLE_RESUME_TEXT, SAMPLE_JOB_DESCRIPTION)

        assert result is not None
        assert 'resume_skills' in result
        assert 'hard_skills_analysis' in result


# Test Suite 3: Confidence Scorer Tests

class TestConfidenceScorer:
    """Test confidence interval calculations"""

    def test_scorer_initialization(self):
        """Test that ConfidenceScorer initializes correctly"""
        scorer = ConfidenceScorer()
        assert scorer is not None
        assert scorer.confidence_level == 0.95
        assert scorer.z_score == 1.960

    def test_calculate_with_confidence(self):
        """Test basic confidence interval calculation"""
        scorer = ConfidenceScorer()
        result = scorer.calculate_with_confidence(score=75.0, sample_size=30)

        assert result.score == 75.0
        assert result.confidence_lower < result.score
        assert result.confidence_upper > result.score
        assert result.margin_of_error > 0
        assert result.confidence_level == 0.95
        assert result.confidence_text != ""
        assert result.reliability_rating != ""

    def test_confidence_interval_bounds(self):
        """Test that confidence intervals stay within 0-100 range"""
        scorer = ConfidenceScorer()

        # Test high score
        result_high = scorer.calculate_with_confidence(score=98.0, sample_size=20)
        assert result_high.confidence_lower >= 0
        assert result_high.confidence_upper <= 100

        # Test low score
        result_low = scorer.calculate_with_confidence(score=5.0, sample_size=20)
        assert result_low.confidence_lower >= 0
        assert result_low.confidence_upper <= 100

    def test_sample_size_effect(self):
        """Test that larger sample size reduces margin of error"""
        scorer = ConfidenceScorer()

        small_sample = scorer.calculate_with_confidence(score=75.0, sample_size=10)
        large_sample = scorer.calculate_with_confidence(score=75.0, sample_size=100)

        assert large_sample.margin_of_error < small_sample.margin_of_error

    def test_keyword_confidence(self):
        """Test confidence calculation for keyword matching"""
        scorer = ConfidenceScorer()
        result = scorer.calculate_keyword_confidence(
            match_rate=70.0,
            total_keywords=20,
            matched_keywords=14
        )

        assert result.score == 70.0
        assert result.margin_of_error > 0

    def test_ats_pass_confidence(self):
        """Test confidence calculation for ATS pass probability"""
        scorer = ConfidenceScorer()
        result = scorer.calculate_ats_pass_confidence(
            pass_probability=80.0,
            num_checks=3  # 3 platforms
        )

        assert result.score == 80.0
        assert result.confidence_lower < 80.0
        assert result.confidence_upper > 80.0

    def test_add_confidence_intervals_convenience(self):
        """Test convenience function for multiple scores"""
        scores = {
            'keyword_score': 75.0,
            'quality_score': 82.0
        }
        sample_sizes = {
            'keyword_score': 30,
            'quality_score': 50
        }

        result = add_confidence_intervals(scores, sample_sizes)

        assert 'keyword_score' in result
        assert 'quality_score' in result
        assert 'confidence_interval' in result['keyword_score']
        assert 'margin_of_error' in result['keyword_score']

    def test_format_score_with_confidence(self):
        """Test score formatting with confidence"""
        text = format_score_with_confidence(78.0, 35)

        assert "78" in text
        assert "±" in text
        assert "confidence" in text.lower()


# Test Suite 4: Semantic Matcher Tests (Phase 1 dependency)

class TestSemanticMatcher:
    """Test semantic keyword matching"""

    def test_matcher_initialization(self):
        """Test that SemanticKeywordMatcher initializes"""
        matcher = SemanticKeywordMatcher()
        assert matcher is not None

    def test_extract_keywords_basic(self):
        """Test basic keyword extraction"""
        matcher = SemanticKeywordMatcher()
        keywords = matcher.extract_keywords(SAMPLE_JOB_DESCRIPTION, top_n=10)

        assert isinstance(keywords, list)
        assert len(keywords) > 0
        # Should extract key skills like Python, AWS, etc.

    def test_semantic_match_score(self):
        """Test semantic matching between resume and keywords"""
        matcher = SemanticKeywordMatcher()
        keywords = ['python', 'aws', 'docker', 'kubernetes', 'leadership']

        result = matcher.semantic_match_score(SAMPLE_RESUME_TEXT, keywords, threshold=0.7)

        assert 'match_rate' in result
        assert 'matches' in result
        assert 'total_keywords' in result
        assert 'matched_keywords' in result
        assert 'method' in result
        assert 0 <= result['match_rate'] <= 100

    def test_keyword_comparison(self):
        """Test similarity comparison between keywords"""
        matcher = SemanticKeywordMatcher()

        # Similar keywords
        similarity_high = matcher.compare_keywords('python', 'python programming')
        assert similarity_high > 0.7

        # Unrelated keywords
        similarity_low = matcher.compare_keywords('python', 'accounting')
        assert similarity_low < 0.5

    def test_detailed_keyword_matching(self):
        """Test complete keyword matching workflow"""
        matcher = SemanticKeywordMatcher()
        result = matcher.get_keyword_matches_detailed(
            SAMPLE_RESUME_TEXT,
            SAMPLE_JOB_DESCRIPTION,
            top_n=15
        )

        assert 'match_rate' in result
        assert 'extracted_keywords' in result
        assert 'matched_keywords' in result
        assert 'missing_keywords' in result
        assert len(result['extracted_keywords']) > 0


# Test Suite 5: Integration Tests

class TestPhase2Integration:
    """Test integration between Phase 2 components"""

    def test_full_phase2_analysis(self):
        """Test running all Phase 2 features together"""
        # 1. ATS Simulation
        ats_result = analyze_ats_compatibility(SAMPLE_RESUME_TEXT)
        assert ats_result['overall_score'] > 0

        # 2. Skills Categorization
        skills_result = analyze_skills(SAMPLE_RESUME_TEXT, SAMPLE_JOB_DESCRIPTION)
        assert skills_result['resume_skills_count']['total'] > 0

        # 3. Confidence Scoring
        scores = {'ats_score': ats_result['overall_score']}
        confidence_result = add_confidence_intervals(scores)
        assert 'ats_score' in confidence_result

        # All components should work together
        assert ats_result is not None
        assert skills_result is not None
        assert confidence_result is not None

    def test_phase2_with_metadata(self):
        """Test Phase 2 features with metadata"""
        metadata = {
            'format': 'pdf',
            'page_count': 2,
            'word_count': 450
        }

        result = analyze_ats_compatibility(SAMPLE_RESUME_TEXT, metadata)
        assert result is not None
        assert result['overall_score'] > 0


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
