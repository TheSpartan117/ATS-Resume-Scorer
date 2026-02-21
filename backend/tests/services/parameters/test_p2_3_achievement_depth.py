"""
Tests for P2.3: Achievement Depth / Vague Phrases (5 points)

Tests vague phrase detection and penalty scoring.
Uses VaguePhraseDetector from backend.services.vague_phrase_detector.
"""

import pytest
from backend.services.parameters.p2_3_achievement_depth import AchievementDepthScorer


class TestAchievementDepthScorer:
    """Test suite for P2.3 achievement depth scoring"""

    @pytest.fixture
    def scorer(self):
        """Create scorer instance"""
        return AchievementDepthScorer()

    # ========================================================================
    # CORE SCORING TESTS (5 point scale)
    # ========================================================================

    def test_zero_vague_phrases_excellent(self, scorer):
        """0 vague phrases = 5 points (EXCELLENT)"""
        bullets = [
            "Developed RESTful API serving 100K+ requests/day",
            "Implemented caching layer reducing latency by 60%",
            "Led team of 8 engineers delivering 3 major features",
            "Optimized database queries improving performance 3x"
        ]

        result = scorer.score(bullets)

        assert result['score'] == 5
        assert result['vague_phrase_count'] == 0
        assert result['penalty_tier'] == 'EXCELLENT'

    def test_one_vague_phrase_good(self, scorer):
        """1-2 vague phrases = 4 points (GOOD)"""
        bullets = [
            "Responsible for backend development",  # VAGUE
            "Implemented authentication system with OAuth 2.0",
            "Optimized API endpoints reducing response time by 40%",
            "Led migration to microservices architecture"
        ]

        result = scorer.score(bullets)

        assert result['score'] == 4
        assert result['vague_phrase_count'] == 1
        assert result['penalty_tier'] == 'GOOD'
        assert 'responsible for' in result['found_phrases']

    def test_two_vague_phrases_good(self, scorer):
        """1-2 vague phrases = 4 points (GOOD)"""
        bullets = [
            "Worked on frontend features",           # VAGUE
            "Helped with deployment automation",     # VAGUE
            "Built CI/CD pipeline reducing deploy time by 70%",
            "Architected scalable microservices infrastructure"
        ]

        result = scorer.score(bullets)

        assert result['score'] == 4
        assert result['vague_phrase_count'] == 2
        assert result['penalty_tier'] == 'GOOD'
        assert 'worked on' in result['found_phrases']
        assert 'helped with' in result['found_phrases']

    def test_three_vague_phrases_fair(self, scorer):
        """3-4 vague phrases = 2 points (FAIR)"""
        bullets = [
            "Responsible for database management",   # VAGUE
            "Involved in API development",           # VAGUE
            "Worked with team members",              # VAGUE
            "Implemented monitoring dashboard with real-time alerts"
        ]

        result = scorer.score(bullets)

        assert result['score'] == 2
        assert result['vague_phrase_count'] == 3
        assert result['penalty_tier'] == 'FAIR'

    def test_four_vague_phrases_fair(self, scorer):
        """3-4 vague phrases = 2 points (FAIR)"""
        bullets = [
            "Responsible for code reviews",          # VAGUE
            "Tasked with performance testing",       # VAGUE
            "Participated in sprint planning",       # VAGUE
            "Helped with bug fixes",                 # VAGUE
            "Developed authentication service"
        ]

        result = scorer.score(bullets)

        assert result['score'] == 2
        assert result['vague_phrase_count'] == 4
        assert result['penalty_tier'] == 'FAIR'

    def test_five_plus_vague_phrases_poor(self, scorer):
        """5+ vague phrases = 0 points (POOR)"""
        bullets = [
            "Responsible for backend services",      # VAGUE
            "Worked on various projects",            # VAGUE
            "Helped with documentation",             # VAGUE
            "Involved in testing efforts",           # VAGUE
            "Participated in code reviews",          # VAGUE
            "Supported team initiatives"             # VAGUE (contains "supported")
        ]

        result = scorer.score(bullets)

        assert result['score'] == 0
        assert result['vague_phrase_count'] >= 5
        assert result['penalty_tier'] == 'POOR'

    # ========================================================================
    # PHRASE DETECTION TESTS
    # ========================================================================

    def test_detect_responsible_for(self, scorer):
        """Detect 'responsible for' phrase"""
        bullets = ["Responsible for managing team of 10 engineers"]

        result = scorer.score(bullets)

        assert result['vague_phrase_count'] == 1
        assert 'responsible for' in result['found_phrases']

    def test_detect_worked_on(self, scorer):
        """Detect 'worked on' phrase"""
        bullets = ["Worked on frontend and backend components"]

        result = scorer.score(bullets)

        assert result['vague_phrase_count'] == 1
        assert 'worked on' in result['found_phrases']

    def test_detect_helped_with(self, scorer):
        """Detect 'helped with' phrase"""
        bullets = ["Helped with deployment and monitoring"]

        result = scorer.score(bullets)

        assert result['vague_phrase_count'] == 1
        assert 'helped with' in result['found_phrases']

    def test_detect_involved_in(self, scorer):
        """Detect 'involved in' phrase"""
        bullets = ["Involved in architecture design and implementation"]

        result = scorer.score(bullets)

        assert result['vague_phrase_count'] == 1
        assert 'involved in' in result['found_phrases']

    def test_detect_multiple_different_phrases(self, scorer):
        """Detect multiple different vague phrases"""
        bullets = [
            "Responsible for API development",
            "Worked on database optimization",
            "Participated in code reviews",
            "Tasked with security audits"
        ]

        result = scorer.score(bullets)

        assert result['vague_phrase_count'] == 4
        assert 'responsible for' in result['found_phrases']
        assert 'worked on' in result['found_phrases']
        assert 'participated in' in result['found_phrases']
        assert 'tasked with' in result['found_phrases']

    def test_detect_multiple_same_phrase(self, scorer):
        """Count multiple occurrences of same phrase"""
        bullets = [
            "Responsible for backend development",
            "Responsible for code quality",
            "Responsible for team mentoring"
        ]

        result = scorer.score(bullets)

        assert result['vague_phrase_count'] == 3
        # Should have 3 instances of 'responsible for'
        assert result['found_phrases'].count('responsible for') == 3

    def test_case_insensitive_detection(self, scorer):
        """Detect phrases regardless of case"""
        bullets = [
            "RESPONSIBLE FOR backend services",
            "Worked On various features",
            "helped with deployment"
        ]

        result = scorer.score(bullets)

        assert result['vague_phrase_count'] == 3

    # ========================================================================
    # EDGE CASES
    # ========================================================================

    def test_empty_bullets(self, scorer):
        """Empty bullets = 5 points (no vague phrases)"""
        result = scorer.score([])

        assert result['score'] == 5
        assert result['vague_phrase_count'] == 0
        assert result['found_phrases'] == []
        assert 'no bullets' in result['feedback'].lower()

    def test_single_bullet_no_vague(self, scorer):
        """Single bullet without vague phrases = 5 points"""
        bullets = ["Architected microservices platform handling 1M requests/day"]

        result = scorer.score(bullets)

        assert result['score'] == 5
        assert result['vague_phrase_count'] == 0

    def test_single_bullet_with_vague(self, scorer):
        """Single bullet with vague phrase = 4 points"""
        bullets = ["Responsible for system architecture"]

        result = scorer.score(bullets)

        assert result['score'] == 4
        assert result['vague_phrase_count'] == 1

    def test_phrase_in_middle_of_bullet(self, scorer):
        """Detect vague phrase not at start of bullet"""
        bullets = ["Successfully worked on critical infrastructure projects"]

        result = scorer.score(bullets)

        assert result['vague_phrase_count'] == 1
        assert 'worked on' in result['found_phrases']

    def test_partial_word_match_not_detected(self, scorer):
        """Should not match partial words"""
        bullets = [
            "Reworked on system architecture",  # Should NOT match 'worked on'
            "Worked onboarding process"         # Should NOT match 'worked on'
        ]

        result = scorer.score(bullets)

        # Should detect 0 vague phrases (word boundaries matter)
        assert result['vague_phrase_count'] == 0

    # ========================================================================
    # FEEDBACK QUALITY
    # ========================================================================

    def test_feedback_includes_count(self, scorer):
        """Feedback should include vague phrase count"""
        bullets = [
            "Responsible for backend",
            "Worked on frontend",
            "Helped with testing"
        ]

        result = scorer.score(bullets)

        assert '3' in result['feedback']
        assert 'vague' in result['feedback'].lower()

    def test_feedback_excellent_performance(self, scorer):
        """Excellent performance should have positive feedback"""
        bullets = [
            "Developed high-performance API",
            "Implemented real-time analytics",
            "Led team of 12 engineers"
        ]

        result = scorer.score(bullets)

        assert result['score'] == 5
        assert 'excellent' in result['feedback'].lower() or 'strong' in result['feedback'].lower()

    def test_feedback_suggests_improvement_when_poor(self, scorer):
        """Poor performance should suggest improvements"""
        bullets = [
            "Responsible for development",
            "Worked on features",
            "Helped with testing",
            "Involved in deployment",
            "Participated in reviews"
        ]

        result = scorer.score(bullets)

        assert result['score'] == 0
        assert 'improve' in result['feedback'].lower() or 'replace' in result['feedback'].lower()

    def test_feedback_lists_found_phrases(self, scorer):
        """Feedback should list found vague phrases"""
        bullets = [
            "Responsible for API development",
            "Worked on database optimization"
        ]

        result = scorer.score(bullets)

        assert result['score'] == 4
        # Feedback should mention the specific phrases found
        feedback_lower = result['feedback'].lower()
        assert 'responsible for' in feedback_lower or 'worked on' in feedback_lower

    # ========================================================================
    # INTEGRATION WITH VAGUEPHRASEDECTOR
    # ========================================================================

    def test_uses_vague_phrase_detector(self, scorer):
        """Scorer should use VaguePhraseDetector internally"""
        bullets = [
            "Exposure to cloud technologies",    # VAGUE
            "Knowledge of Python and Java",      # VAGUE
            "Familiar with Agile methodologies"  # VAGUE
        ]

        result = scorer.score(bullets)

        assert result['vague_phrase_count'] == 3
        assert 'exposure to' in result['found_phrases']
        assert 'knowledge of' in result['found_phrases']
        assert 'familiar with' in result['found_phrases']

    def test_all_vague_phrases_from_json(self, scorer):
        """Test various vague phrases from vague_phrases.json"""
        bullets = [
            "Responsible for team management",
            "Worked on backend services",
            "Helped with deployment",
            "Involved in architecture design",
            "Participated in sprint planning",
            "Contributed to code quality",
            "Assisted with testing",
            "Exposure to cloud platforms",
            "Familiar with Docker",
            "Knowledge of Kubernetes",
            "Tasked with optimization",
            "Duties included monitoring",
            "Handled customer requests",
            "Dealt with production issues",
            "Supported team initiatives",
            "Was part of core team",
            "Engaged in refactoring",
            "Associated with key projects",
            "Worked with stakeholders",
            "Worked alongside engineers",
            "Collaborated on features"
        ]

        result = scorer.score(bullets)

        # Should detect all 21 vague phrases
        assert result['vague_phrase_count'] == 21
        assert result['score'] == 0  # 5+ vague phrases = 0 points
        assert result['penalty_tier'] == 'POOR'

    # ========================================================================
    # RETURN VALUE STRUCTURE
    # ========================================================================

    def test_return_structure_complete(self, scorer):
        """Verify return dictionary has all required fields"""
        bullets = ["Responsible for development"]

        result = scorer.score(bullets)

        # Check all required keys exist
        assert 'score' in result
        assert 'max_score' in result
        assert 'vague_phrase_count' in result
        assert 'found_phrases' in result
        assert 'penalty_tier' in result
        assert 'feedback' in result

        # Check types
        assert isinstance(result['score'], int)
        assert isinstance(result['max_score'], int)
        assert isinstance(result['vague_phrase_count'], int)
        assert isinstance(result['found_phrases'], list)
        assert isinstance(result['penalty_tier'], str)
        assert isinstance(result['feedback'], str)

        # Check value ranges
        assert 0 <= result['score'] <= 5
        assert result['max_score'] == 5
        assert result['vague_phrase_count'] >= 0
