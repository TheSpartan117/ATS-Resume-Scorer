"""Tests for ContextAwareScorer service"""
import pytest
from backend.services.context_aware_scorer import ContextAwareScorer


class TestExperienceLevelAdjustments:
    """Test experience level multiplier adjustments"""

    def test_entry_level_multiplier(self):
        """Entry level should have 0.6x penalty for gaps"""
        scorer = ContextAwareScorer()
        base_score = 20.0
        adjusted = scorer.apply_level_multiplier(
            base_score,
            level="entry",
            metric="gap_penalty"
        )

        assert adjusted == 12.0  # 20 * 0.6

    def test_mid_level_multiplier(self):
        """Mid level should have 0.8x penalty for gaps"""
        scorer = ContextAwareScorer()
        base_score = 20.0
        adjusted = scorer.apply_level_multiplier(
            base_score,
            level="mid",
            metric="gap_penalty"
        )

        assert adjusted == 16.0  # 20 * 0.8

    def test_senior_level_no_adjustment(self):
        """Senior level should have no adjustment (1.0x)"""
        scorer = ContextAwareScorer()
        base_score = 20.0
        adjusted = scorer.apply_level_multiplier(
            base_score,
            level="senior",
            metric="gap_penalty"
        )

        assert adjusted == 20.0  # 20 * 1.0

    def test_lead_level_bonus(self):
        """Lead level should have 1.1x bonus for achievements"""
        scorer = ContextAwareScorer()
        base_score = 10.0
        adjusted = scorer.apply_level_multiplier(
            base_score,
            level="lead",
            metric="achievement_bonus"
        )

        assert adjusted == 11.0  # 10 * 1.1

    def test_executive_level_bonus(self):
        """Executive level should have 1.2x bonus for strategic content"""
        scorer = ContextAwareScorer()
        base_score = 10.0
        adjusted = scorer.apply_level_multiplier(
            base_score,
            level="executive",
            metric="strategic_bonus"
        )

        assert adjusted == 12.0  # 10 * 1.2


class TestSectionSpecificScoring:
    """Test section-specific handling"""

    def test_summary_section_requirements(self):
        """Summary should require specific elements"""
        scorer = ContextAwareScorer()

        # Good summary
        summary = "Product Manager with 8+ years building SaaS platforms. Led 15+ launches generating $10M+ ARR."
        result = scorer.score_section_content(summary, section="summary", level="senior")

        assert result['score'] > 0
        assert 'has_years_experience' in result
        assert 'has_quantified_impact' in result

    def test_experience_section_achievement_focus(self):
        """Experience should focus on achievements"""
        scorer = ContextAwareScorer()

        bullets = [
            "Led team of 8 engineers to deliver cloud migration",
            "Reduced costs by 40% through infrastructure optimization"
        ]
        result = scorer.score_section_content("\n".join(bullets), section="experience", level="senior")

        assert result['score'] > 0
        assert 'achievement_count' in result

    def test_education_section_relevance(self):
        """Education should check degree relevance"""
        scorer = ContextAwareScorer()

        education = "B.S. Computer Science, MIT, 2018. GPA: 3.9/4.0"
        result = scorer.score_section_content(education, section="education", level="entry")

        assert result['score'] > 0


class TestContextualScoreAdjustment:
    """Test full contextual score adjustment"""

    def test_adjust_quality_score_entry_level(self):
        """Entry level CV should receive lenient adjustments"""
        scorer = ContextAwareScorer()

        quality_scores = {
            'achievement_strength': 8.0,  # Lower expectations
            'sentence_clarity': 7.0,
            'specificity': 3.0,
            'grammar': 8.0
        }

        adjusted = scorer.adjust_quality_score(
            quality_scores,
            level="entry",
            section="experience"
        )

        assert adjusted['total_score'] > 0
        assert adjusted['adjustments_applied'] == True

    def test_adjust_quality_score_senior_level(self):
        """Senior level CV should have stricter standards"""
        scorer = ContextAwareScorer()

        quality_scores = {
            'achievement_strength': 12.0,  # Higher expectations
            'sentence_clarity': 8.0,
            'specificity': 4.0,
            'grammar': 9.0
        }

        adjusted = scorer.adjust_quality_score(
            quality_scores,
            level="senior",
            section="experience"
        )

        assert adjusted['total_score'] > 0
        assert adjusted['adjustments_applied'] == True
