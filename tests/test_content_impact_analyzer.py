"""Tests for ContentImpactAnalyzer service"""
import pytest
from backend.services.content_impact_analyzer import ContentImpactAnalyzer


class TestAchievementStrength:
    """Test achievement strength scoring"""

    @pytest.fixture
    def analyzer(self):
        """Shared analyzer instance for all tests"""
        return ContentImpactAnalyzer()

    def test_classify_verb_tier_transformational(self, analyzer):
        """Tier 4 verbs should return 4"""
        assert analyzer.classify_verb_tier("transformed") == 4
        assert analyzer.classify_verb_tier("pioneered") == 4

    def test_classify_verb_tier_leadership(self, analyzer):
        """Tier 3 verbs should return 3"""
        assert analyzer.classify_verb_tier("led") == 3
        assert analyzer.classify_verb_tier("architected") == 3

    def test_classify_verb_tier_execution(self, analyzer):
        """Tier 2 verbs should return 2"""
        assert analyzer.classify_verb_tier("developed") == 2
        assert analyzer.classify_verb_tier("implemented") == 2

    def test_classify_verb_tier_support(self, analyzer):
        """Tier 1 verbs should return 1"""
        assert analyzer.classify_verb_tier("managed") == 1
        assert analyzer.classify_verb_tier("coordinated") == 1

    def test_classify_verb_tier_weak(self, analyzer):
        """Tier 0 verbs should return 0"""
        assert analyzer.classify_verb_tier("responsible for") == 0
        assert analyzer.classify_verb_tier("worked on") == 0

    def test_classify_verb_tier_unknown(self, analyzer):
        """Unknown verbs should return 1 (neutral)"""
        assert analyzer.classify_verb_tier("xyz") == 1


class TestMetricDetection:
    """Test metric pattern detection"""

    @pytest.fixture
    def analyzer(self):
        """Shared analyzer instance for all tests"""
        return ContentImpactAnalyzer()

    def test_extract_metrics_percentage(self, analyzer):
        """Should extract percentage metrics"""
        text = "Increased revenue by 45% and reduced costs by 30%"
        metrics = analyzer.extract_metrics(text)
        assert len(metrics) >= 2
        assert any(m['value'] == '45%' and m['type'] == 'percentage' for m in metrics)
        assert any(m['value'] == '30%' and m['type'] == 'percentage' for m in metrics)

    def test_extract_metrics_money(self, analyzer):
        """Should extract money metrics"""
        text = "Generated $2M in revenue and saved $500K in costs"
        metrics = analyzer.extract_metrics(text)
        assert len(metrics) == 2
        assert any(m['value'] == '$2M' and m['type'] == 'money' for m in metrics)
        assert any(m['value'] == '$500K' and m['type'] == 'money' for m in metrics)

    def test_extract_metrics_multiplier(self, analyzer):
        """Should extract multiplier metrics"""
        text = "Improved performance by 3x"
        metrics = analyzer.extract_metrics(text)
        assert len(metrics) >= 1
        assert any(m['value'] == '3x' and m['type'] == 'multiplier' for m in metrics)

    def test_extract_metrics_count(self, analyzer):
        """Should extract count metrics"""
        text = "Managed 12 teams and 150 users"
        metrics = analyzer.extract_metrics(text)
        assert len(metrics) >= 2
        # Should find "12 teams" and "150 users"

    def test_evaluate_metric_quality_high(self, analyzer):
        """Money and percentage should be high quality (1.0)"""
        assert analyzer.evaluate_metric_quality('money') == 1.0
        assert analyzer.evaluate_metric_quality('percentage') == 1.0

    def test_evaluate_metric_quality_medium(self, analyzer):
        """Counts and time should be medium quality (0.7)"""
        assert analyzer.evaluate_metric_quality('count') == 0.7
        assert analyzer.evaluate_metric_quality('time') == 0.7


class TestCARStructureDetection:
    """Test Context-Action-Result structure detection"""

    def test_analyze_achievement_perfect_car(self):
        """Perfect CAR structure should score 14-15 pts"""
        analyzer = ContentImpactAnalyzer()
        bullet = "Architected API for mobile app, reducing latency by 60% through Redis caching"
        result = analyzer.analyze_achievement_structure(bullet)

        assert result['score'] >= 14
        assert result['has_context'] is True
        assert result['action_strength'] >= 3
        assert len(result['metrics_found']) >= 1
        assert result['has_causality'] is True

    def test_analyze_achievement_good_ar(self):
        """Good Action-Result should score 11-13 pts"""
        analyzer = ContentImpactAnalyzer()
        bullet = "Led team of 8 engineers to deliver $2M project"
        result = analyzer.analyze_achievement_structure(bullet)

        assert 11 <= result['score'] <= 13
        assert result['action_strength'] >= 3
        assert len(result['metrics_found']) >= 1

    def test_analyze_achievement_moderate(self):
        """Moderate achievement should score 8-10 pts"""
        analyzer = ContentImpactAnalyzer()
        bullet = "Improved system performance significantly"
        result = analyzer.analyze_achievement_structure(bullet)

        assert 8 <= result['score'] <= 10

    def test_analyze_achievement_weak_duty(self):
        """Weak duty statement should score 3-7 pts"""
        analyzer = ContentImpactAnalyzer()
        bullet = "Managed projects and teams"
        result = analyzer.analyze_achievement_structure(bullet)

        assert 3 <= result['score'] <= 7
        assert result['action_strength'] >= 1

    def test_analyze_achievement_very_weak(self):
        """Very weak statement should score 0-2 pts"""
        analyzer = ContentImpactAnalyzer()
        bullet = "Product management responsibilities"
        result = analyzer.analyze_achievement_structure(bullet)

        assert 0 <= result['score'] <= 2


class TestAchievementStrengthScorer:
    """Test overall achievement strength scoring"""

    def test_score_achievement_strength_strong_bullets(self):
        """Multiple strong bullets should score near 15"""
        analyzer = ContentImpactAnalyzer()
        bullets = [
            "Led team of 8 to deliver $2M project ahead of schedule",
            "Architected API reducing latency by 60% through Redis caching",
            "Launched 3 products generating $1.5M ARR in 6 months"
        ]
        score = analyzer.score_achievement_strength(bullets)
        assert 13 <= score <= 15

    def test_score_achievement_strength_weak_bullets(self):
        """Weak duty statements should score low"""
        analyzer = ContentImpactAnalyzer()
        bullets = [
            "Responsible for product management",
            "Worked on various projects",
            "Helped with team coordination"
        ]
        score = analyzer.score_achievement_strength(bullets)
        assert 0 <= score <= 5

    def test_score_achievement_strength_mixed(self):
        """Mixed quality should score in middle"""
        analyzer = ContentImpactAnalyzer()
        bullets = [
            "Led team of 8 engineers delivering 3 projects",
            "Developed features and coordinated with stakeholders",
            "Managed tasks and deliverables"
        ]
        score = analyzer.score_achievement_strength(bullets)
        assert 6 <= score <= 10


class TestSentenceClarityScorer:
    """Test sentence clarity analysis"""

    def test_score_sentence_length_optimal(self):
        """Optimal length (15-25 words) should score 3 pts"""
        analyzer = ContentImpactAnalyzer()
        sentence = "Led team of 8 engineers to deliver cloud migration reducing costs by 40%"
        # 14 words - close to optimal
        score = analyzer.score_sentence_length([sentence], "experience")
        assert score >= 2.5

    def test_score_sentence_length_too_short(self):
        """Very short sentences should score low"""
        analyzer = ContentImpactAnalyzer()
        sentences = ["Managed teams", "Led projects"]
        score = analyzer.score_sentence_length(sentences, "experience")
        assert score <= 1.0

    def test_detect_weak_phrases_multiple(self):
        """Multiple weak phrases should be penalized"""
        analyzer = ContentImpactAnalyzer()
        text = "Responsible for working on various projects and helped with coordination"
        result = analyzer.detect_weak_phrases(text)

        assert result['score'] <= 2  # Heavy penalty
        assert len(result['found']) >= 3  # At least 3 weak phrases

    def test_detect_weak_phrases_none(self):
        """No weak phrases should score 4 pts"""
        analyzer = ContentImpactAnalyzer()
        text = "Led team of 8 to deliver $2M project ahead of schedule"
        result = analyzer.detect_weak_phrases(text)

        assert result['score'] == 4
        assert len(result['found']) == 0

    def test_calculate_active_voice_percentage_all_active(self):
        """All active voice should return 100%"""
        analyzer = ContentImpactAnalyzer()
        text = "Led teams. Delivered projects. Improved systems."
        pct = analyzer.calculate_active_voice_percentage(text)
        assert pct >= 90

    def test_calculate_active_voice_percentage_mixed(self):
        """Mixed voice should return appropriate percentage"""
        analyzer = ContentImpactAnalyzer()
        text = "Led teams. Projects were delivered. Systems were improved."
        pct = analyzer.calculate_active_voice_percentage(text)
        assert 30 <= pct <= 70

    def test_score_sentence_clarity_excellent(self):
        """Excellent clarity should score near 10"""
        analyzer = ContentImpactAnalyzer()
        bullets = [
            "Led team of 8 engineers to deliver cloud migration reducing infrastructure costs",
            "Architected high-performance API reducing latency by 60% for mobile users",
            "Delivered major product launch ahead of schedule with zero downtime"
        ]
        score = analyzer.score_sentence_clarity(bullets, "experience")
        assert score >= 8


class TestSpecificityScorer:
    """Test specificity analysis"""

    def test_score_technology_specificity_high(self):
        """Specific tech mentions should score 2 pts"""
        analyzer = ContentImpactAnalyzer()
        text = "Built API using Node.js, Express, PostgreSQL, and Redis"
        score = analyzer.score_technology_specificity(text)
        assert score >= 1.5

    def test_score_technology_specificity_low(self):
        """Generic mentions should score 0 pts"""
        analyzer = ContentImpactAnalyzer()
        text = "Developed applications using modern frameworks and databases"
        score = analyzer.score_technology_specificity(text)
        assert score <= 0.5

    def test_score_metric_specificity_high(self):
        """Precise numbers should score 2 pts"""
        analyzer = ContentImpactAnalyzer()
        text = "Increased revenue by 45% from $1.2M to $1.8M in 6 months"
        score = analyzer.score_metric_specificity(text)
        assert score >= 1.5

    def test_score_metric_specificity_low(self):
        """Vague claims should score 0 pts"""
        analyzer = ContentImpactAnalyzer()
        text = "Significantly improved performance metrics"
        score = analyzer.score_metric_specificity(text)
        assert score <= 0.5

    def test_score_action_specificity_high(self):
        """Concrete actions should score 1 pt"""
        analyzer = ContentImpactAnalyzer()
        text = "Architected microservices, refactored legacy codebase"
        score = analyzer.score_action_specificity(text)
        assert score >= 0.8

    def test_score_specificity_overall(self):
        """Overall specificity should aggregate all components"""
        analyzer = ContentImpactAnalyzer()
        bullets = ["Architected API using Node.js and PostgreSQL, reducing latency by 60%"]
        score = analyzer.score_specificity(bullets)
        assert 4 <= score <= 5  # Near maximum


class TestImpactQualityScorer:
    """Test main impact quality scoring"""

    def test_score_impact_quality_excellent(self):
        """Excellent CV should score near 30"""
        analyzer = ContentImpactAnalyzer()
        bullets = [
            "Led team of 8 engineers to deliver cloud migration, reducing costs by 40% in Q3",
            "Architected microservices API using Node.js and PostgreSQL, reducing latency by 60%",
            "Launched 3 products generating $2M ARR in 6 months"
        ]
        result = analyzer.score_impact_quality(bullets, level="senior", section="experience")

        assert result['total_score'] >= 25
        assert result['achievement_strength'] >= 12
        assert result['sentence_clarity'] >= 8
        assert result['specificity'] >= 4

    def test_score_impact_quality_weak(self):
        """Weak CV should score low"""
        analyzer = ContentImpactAnalyzer()
        bullets = [
            "Responsible for product management",
            "Worked on various projects",
            "Helped with team coordination"
        ]
        result = analyzer.score_impact_quality(bullets, level="mid", section="experience")

        assert result['total_score'] <= 10
        assert result['achievement_strength'] <= 5

    def test_score_impact_quality_summary_section(self):
        """Summary section should use relaxed rules"""
        analyzer = ContentImpactAnalyzer()
        summary = [
            "Product Manager with 8+ years building SaaS platforms.",
            "Led 15+ product launches generating $10M+ ARR.",
            "Expert in Agile, roadmapping, and cross-functional leadership."
        ]
        result = analyzer.score_impact_quality(summary, level="senior", section="summary")

        # Summary should skip achievement analysis but check clarity/specificity
        assert result['total_score'] > 0
