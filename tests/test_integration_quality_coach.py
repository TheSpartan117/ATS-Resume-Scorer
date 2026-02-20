"""Integration tests for Quality Coach recalibration"""
import pytest
from backend.services.scorer_v2 import AdaptiveScorer
from backend.services.parser import ResumeData, Section, ContactInfo, Metadata


class TestQualityCoachIntegration:
    """Test the integrated Quality Coach scoring flow"""

    def create_sample_resume(self) -> ResumeData:
        """Create a sample resume data object for testing"""
        contact = ContactInfo(
            name="John Doe",
            email="john@example.com",
            phone="555-1234",
            location="San Francisco, CA"
        )

        metadata = Metadata(
            pageCount=1,
            wordCount=450,
            hasPhoto=False,
            fileSize=50000
        )

        # Create experience section with quality bullets
        experience_section = Section(
            section_type="experience",
            content=[
                {
                    "company": "Tech Corp",
                    "title": "Senior Software Engineer",
                    "dates": "2020-2023",
                    "bullets": [
                        "Led team of 8 engineers to deliver cloud migration reducing costs by 40% in Q3",
                        "Architected microservices API using Node.js and PostgreSQL, reducing latency by 60%",
                        "Launched 3 products generating $2M ARR in 6 months"
                    ]
                }
            ]
        )

        sections = [experience_section]

        return ResumeData(
            contact=contact,
            sections=sections,
            metadata=metadata,
            fullText="Led team of 8 engineers to deliver cloud migration reducing costs by 40% in Q3. Architected microservices API using Node.js and PostgreSQL, reducing latency by 60%. Launched 3 products generating $2M ARR in 6 months."
        )

    def test_quality_coach_scoring_with_enhancements(self):
        """Test that quality coach mode returns enhanced feedback and benchmarks"""
        scorer = AdaptiveScorer()
        resume_data = self.create_sample_resume()

        result = scorer.score(
            resume_data=resume_data,
            role_id="software_engineer",
            level="senior",
            job_description=None,  # Quality coach mode
            mode="quality_coach"
        )

        # Verify basic structure
        assert "overallScore" in result
        assert result["mode"] == "quality_coach"
        assert "breakdown" in result

        # Verify enhanced feedback is present
        assert "enhanced_feedback" in result
        feedback = result["enhanced_feedback"]
        assert "interpretation" in feedback
        assert "priority_actions" in feedback
        assert "all_suggestions" in feedback
        assert "identified_strengths" in feedback

        # Verify interpretation structure
        assert "rating" in feedback["interpretation"]
        assert "message" in feedback["interpretation"]

        # Verify priority actions structure
        if len(feedback["priority_actions"]) > 0:
            action = feedback["priority_actions"][0]
            assert "priority" in action
            assert "suggestion" in action
            assert "example" in action

    def test_content_quality_uses_impact_analyzer(self):
        """Test that content quality scoring uses ContentImpactAnalyzer"""
        scorer = AdaptiveScorer()
        resume_data = self.create_sample_resume()

        result = scorer.score(
            resume_data=resume_data,
            role_id="software_engineer",
            level="senior",
            mode="quality_coach"
        )

        # Good resume should score well on content
        content_breakdown = result["breakdown"]["content_quality"]
        assert content_breakdown["score"] > 20  # Out of 30

    def test_grammar_scoring_uses_severity_weights(self):
        """Test that professional polish uses severity-weighted grammar scoring"""
        scorer = AdaptiveScorer()
        resume_data = self.create_sample_resume()

        result = scorer.score(
            resume_data=resume_data,
            role_id="software_engineer",
            level="senior",
            mode="quality_coach"
        )

        # Verify polish scoring
        polish_breakdown = result["breakdown"]["professional_polish"]
        assert "score" in polish_breakdown
        assert polish_breakdown["maxScore"] == 20

    def test_benchmark_data_included(self):
        """Test that benchmark comparison data is included"""
        scorer = AdaptiveScorer()
        resume_data = self.create_sample_resume()

        result = scorer.score(
            resume_data=resume_data,
            role_id="software_engineer",
            level="senior",
            mode="quality_coach"
        )

        # Benchmark data might be None if insufficient data, but key should exist
        assert "benchmark_data" in result

    def test_weak_resume_gets_actionable_feedback(self):
        """Test that weak resumes receive specific, actionable feedback"""
        contact = ContactInfo(
            name="Jane Doe",
            email="jane@example.com",
            phone="555-5678",
            location="Boston, MA"
        )

        metadata = Metadata(
            pageCount=1,
            wordCount=200,
            hasPhoto=False,
            fileSize=30000
        )

        # Weak bullets
        experience_section = Section(
            section_type="experience",
            content=[
                {
                    "company": "Some Company",
                    "title": "Developer",
                    "dates": "2021-2023",
                    "bullets": [
                        "Responsible for developing applications",
                        "Worked on various projects",
                        "Helped with team coordination"
                    ]
                }
            ]
        )

        weak_resume = ResumeData(
            contact=contact,
            sections=[experience_section],
            metadata=metadata,
            fullText="Responsible for developing applications. Worked on various projects. Helped with team coordination."
        )

        scorer = AdaptiveScorer()
        result = scorer.score(
            resume_data=weak_resume,
            role_id="software_engineer",
            level="mid",
            mode="quality_coach"
        )

        # Should have low score
        assert result["overallScore"] < 60

        # Should have high-priority feedback
        feedback = result["enhanced_feedback"]
        assert len(feedback["priority_actions"]) > 0

        # First priority action should be high priority
        if len(feedback["priority_actions"]) > 0:
            assert feedback["priority_actions"][0]["priority"] == "high"


class TestServiceIndependence:
    """Test that individual services work correctly"""

    def test_writing_quality_analyzer_independent(self):
        """WritingQualityAnalyzer should work independently"""
        from backend.services.writing_quality_analyzer import WritingQualityAnalyzer

        analyzer = WritingQualityAnalyzer()

        # Test with no errors
        result = analyzer.score_grammar_with_severity([])
        assert result['score'] == 10.0

        # Test with errors
        errors = [
            {'category': 'spelling', 'message': 'Typo: managment'},
            {'category': 'grammar', 'message': 'Subject-verb agreement'}
        ]
        result = analyzer.score_grammar_with_severity(errors)
        assert result['score'] == 6.5  # 10 - 2 - 1.5

    def test_context_aware_scorer_independent(self):
        """ContextAwareScorer should work independently"""
        from backend.services.context_aware_scorer import ContextAwareScorer

        scorer = ContextAwareScorer()

        # Test level multipliers
        adjusted = scorer.apply_level_multiplier(10.0, "entry", "gap_penalty")
        assert adjusted == 6.0  # 10 * 0.6

        adjusted = scorer.apply_level_multiplier(10.0, "senior", "gap_penalty")
        assert adjusted == 10.0  # 10 * 1.0

    def test_feedback_generator_independent(self):
        """FeedbackGenerator should work independently"""
        from backend.services.feedback_generator import FeedbackGenerator

        generator = FeedbackGenerator()

        analysis = {
            'achievement_strength': 5.0,
            'metrics_found': 1
        }

        feedback = generator.generate_achievement_feedback(analysis)
        assert len(feedback) > 0
        assert all('suggestion' in f for f in feedback)
        assert all('example' in f for f in feedback)

    def test_benchmark_tracker_independent(self):
        """BenchmarkTracker should work independently"""
        from backend.services.benchmark_tracker import BenchmarkTracker

        tracker = BenchmarkTracker()

        # Track some scores
        tracker.track_score(75, "software_engineer", "senior")
        tracker.track_score(80, "software_engineer", "senior")
        tracker.track_score(85, "software_engineer", "senior")

        assert tracker.get_score_count(role="software_engineer", level="senior") == 3

        stats = tracker.get_statistics("software_engineer", "senior")
        assert stats['mean'] == 80.0
        assert stats['median'] == 80.0
