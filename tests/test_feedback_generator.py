"""Tests for FeedbackGenerator service"""
import pytest
from backend.services.feedback_generator import FeedbackGenerator


class TestActionableFeedback:
    """Test generation of actionable feedback"""

    def test_generate_achievement_feedback(self):
        """Should generate specific achievement improvement suggestions"""
        generator = FeedbackGenerator()

        analysis = {
            'achievement_strength': 5.0,  # Low score
            'metrics_found': 1,
            'weak_verbs_count': 3
        }

        feedback = generator.generate_achievement_feedback(analysis)

        assert len(feedback) > 0
        assert any('quantif' in f['suggestion'].lower() for f in feedback)
        assert all('priority' in f for f in feedback)
        assert all('example' in f for f in feedback)

    def test_generate_clarity_feedback(self):
        """Should generate clarity improvement suggestions"""
        generator = FeedbackGenerator()

        analysis = {
            'sentence_clarity': 5.0,
            'weak_phrases_found': ['responsible for', 'worked on'],
            'passive_voice_pct': 60
        }

        feedback = generator.generate_clarity_feedback(analysis)

        assert len(feedback) > 0
        assert any('active voice' in f['suggestion'].lower() for f in feedback)
        assert any('weak phrase' in f['suggestion'].lower() for f in feedback)

    def test_generate_specificity_feedback(self):
        """Should generate specificity improvement suggestions"""
        generator = FeedbackGenerator()

        analysis = {
            'specificity': 2.0,
            'generic_tech_count': 3,
            'vague_metrics_count': 2
        }

        feedback = generator.generate_specificity_feedback(analysis)

        assert len(feedback) > 0
        assert any('specific' in f['suggestion'].lower() for f in feedback)

    def test_feedback_includes_examples(self):
        """All feedback should include concrete examples"""
        generator = FeedbackGenerator()

        analysis = {
            'achievement_strength': 5.0,
            'metrics_found': 0
        }

        feedback = generator.generate_achievement_feedback(analysis)

        for item in feedback:
            assert 'example' in item
            assert item['example'] is not None
            assert len(item['example']) > 0


class TestPriorityLevels:
    """Test feedback priority assignment"""

    def test_critical_issues_high_priority(self):
        """Critical issues should get high priority"""
        generator = FeedbackGenerator()

        # Very low achievement score is critical
        analysis = {
            'achievement_strength': 3.0,  # < 5 is critical
            'metrics_found': 0
        }

        feedback = generator.generate_achievement_feedback(analysis)

        critical_items = [f for f in feedback if f['priority'] == 'high']
        assert len(critical_items) > 0

    def test_moderate_issues_medium_priority(self):
        """Moderate issues should get medium priority"""
        generator = FeedbackGenerator()

        # Moderate achievement score
        analysis = {
            'achievement_strength': 8.0,  # 5-10 is moderate
            'metrics_found': 2
        }

        feedback = generator.generate_achievement_feedback(analysis)

        if len(feedback) > 0:
            assert all(f['priority'] in ['medium', 'low'] for f in feedback)

    def test_minor_issues_low_priority(self):
        """Minor issues should get low priority"""
        generator = FeedbackGenerator()

        # Good achievement score, minor improvements
        analysis = {
            'achievement_strength': 12.0,  # > 10 is good
            'metrics_found': 3
        }

        feedback = generator.generate_achievement_feedback(analysis)

        if len(feedback) > 0:
            assert all(f['priority'] == 'low' for f in feedback)


class TestScoreInterpretation:
    """Test score interpretation and context"""

    def test_interpret_overall_score_excellent(self):
        """Should interpret excellent scores correctly"""
        generator = FeedbackGenerator()

        interpretation = generator.interpret_overall_score(85, level="senior")

        assert interpretation['rating'] == 'excellent'
        assert 'competitive' in interpretation['message'].lower()
        assert len(interpretation['next_steps']) > 0

    def test_interpret_overall_score_good(self):
        """Should interpret good scores correctly"""
        generator = FeedbackGenerator()

        interpretation = generator.interpret_overall_score(72, level="mid")

        assert interpretation['rating'] == 'good'
        assert len(interpretation['improvements']) > 0

    def test_interpret_overall_score_needs_work(self):
        """Should interpret low scores with constructive feedback"""
        generator = FeedbackGenerator()

        interpretation = generator.interpret_overall_score(55, level="entry")

        assert interpretation['rating'] in ['needs_improvement', 'fair']
        assert len(interpretation['focus_areas']) > 0

    def test_interpretation_includes_level_context(self):
        """Interpretation should be tailored to experience level"""
        generator = FeedbackGenerator()

        entry_interp = generator.interpret_overall_score(65, level="entry")
        senior_interp = generator.interpret_overall_score(65, level="senior")

        # Same score, different interpretations
        assert entry_interp['message'] != senior_interp['message']


class TestFeedbackFormatting:
    """Test feedback output formatting"""

    def test_generate_complete_feedback_report(self):
        """Should generate complete structured report"""
        generator = FeedbackGenerator()

        analysis = {
            'overall_score': 70,
            'achievement_strength': 10.0,
            'sentence_clarity': 8.0,
            'specificity': 3.0,
            'grammar': 9.0
        }

        report = generator.generate_complete_feedback(
            analysis,
            level="mid",
            section="experience"
        )

        assert 'interpretation' in report
        assert 'suggestions' in report
        assert 'strengths' in report
        assert 'priority_actions' in report

    def test_suggestions_grouped_by_category(self):
        """Suggestions should be grouped by improvement area"""
        generator = FeedbackGenerator()

        analysis = {
            'achievement_strength': 7.0,
            'sentence_clarity': 6.0,
            'specificity': 4.0
        }

        report = generator.generate_complete_feedback(analysis, level="mid")

        suggestions = report['suggestions']
        categories = {s['category'] for s in suggestions}

        assert len(categories) > 1  # Multiple categories present

    def test_priority_actions_sorted(self):
        """Priority actions should be sorted by importance"""
        generator = FeedbackGenerator()

        analysis = {
            'achievement_strength': 5.0,  # Critical
            'sentence_clarity': 7.0,      # Moderate
            'specificity': 8.0            # Minor
        }

        report = generator.generate_complete_feedback(analysis, level="senior")

        priority_actions = report['priority_actions']

        # First action should be high priority
        if len(priority_actions) > 0:
            assert priority_actions[0]['priority'] == 'high'
