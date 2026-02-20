"""
Tests for Phase 3: UI Simplification

Tests the following components:
- SuggestionPrioritizer: Prioritization algorithm
- PassProbabilityCalculator: Pass probability calculation
- API Integration: Score endpoint returns prioritized data
"""

import pytest
from backend.services.suggestion_prioritizer import SuggestionPrioritizer, Priority, ImpactCategory
from backend.services.pass_probability_calculator import PassProbabilityCalculator, ConfidenceLevel


class TestSuggestionPrioritizer:
    """Test suggestion prioritization logic"""

    def setup_method(self):
        """Set up test fixtures"""
        self.prioritizer = SuggestionPrioritizer()

    def test_empty_suggestions(self):
        """Test prioritization with no suggestions"""
        result = self.prioritizer.prioritize_suggestions([])

        assert result["top_issues"] == []
        assert result["total_count"] == 0
        assert len(result["remaining_by_priority"]) == 3

    def test_prioritize_by_severity(self):
        """Test that critical severity is prioritized"""
        suggestions = [
            {
                "id": "1",
                "type": "keyword",
                "severity": "info",
                "title": "Low priority",
                "description": "Not important",
            },
            {
                "id": "2",
                "type": "keyword",
                "severity": "critical",
                "title": "High priority",
                "description": "Very important with auto-reject",
            },
        ]

        result = self.prioritizer.prioritize_suggestions(suggestions, top_n=1)

        assert len(result["top_issues"]) == 1
        assert result["top_issues"][0]["id"] == "2"
        assert result["top_issues"][0]["priority"] == Priority.CRITICAL

    def test_prioritize_by_impact_type(self):
        """Test that ATS rejection issues are highest priority"""
        suggestions = [
            {
                "id": "1",
                "type": "keyword",
                "severity": "warning",
                "title": "Missing keywords",
                "description": "Add keywords",
            },
            {
                "id": "2",
                "type": "formatting",
                "severity": "warning",
                "title": "Format issue",
                "description": "This will cause auto-reject",
            },
        ]

        result = self.prioritizer.prioritize_suggestions(suggestions, top_n=1)

        # ID 2 should be first because it mentions auto-reject
        assert result["top_issues"][0]["id"] == "2"

    def test_top_n_limit(self):
        """Test that top_n correctly limits results"""
        suggestions = [
            {
                "id": str(i),
                "type": "keyword",
                "severity": "critical",
                "title": f"Issue {i}",
                "description": "Description",
            }
            for i in range(10)
        ]

        result = self.prioritizer.prioritize_suggestions(suggestions, top_n=3)

        assert len(result["top_issues"]) == 3
        assert result["total_count"] == 10

    def test_priority_grouping(self):
        """Test that remaining suggestions are grouped by priority"""
        suggestions = [
            {
                "id": "1",
                "type": "keyword",
                "severity": "critical",
                "title": "Critical issue",
                "description": "auto-reject",
            },
            {
                "id": "2",
                "type": "keyword",
                "severity": "warning",
                "title": "Important issue",
                "description": "keyword match",
            },
            {
                "id": "3",
                "type": "formatting",
                "severity": "info",
                "title": "Minor issue",
                "description": "small improvement",
            },
        ]

        result = self.prioritizer.prioritize_suggestions(suggestions, top_n=1)

        # Check that remaining are properly grouped
        remaining = result["remaining_by_priority"]
        assert Priority.CRITICAL in remaining or Priority.IMPORTANT in remaining
        assert len(result["top_issues"]) == 1

    def test_action_cta_generation(self):
        """Test that appropriate CTAs are generated"""
        suggestions = [
            {"id": "1", "type": "keyword", "severity": "critical", "title": "Test", "description": "Test"},
            {"id": "2", "type": "formatting", "severity": "warning", "title": "Test", "description": "Test"},
            {"id": "3", "type": "missing_content", "severity": "info", "title": "Test", "description": "Test"},
        ]

        result = self.prioritizer.prioritize_suggestions(suggestions, top_n=3)

        assert result["top_issues"][0]["action_cta"] == "Add keywords"
        assert result["top_issues"][1]["action_cta"] == "Fix formatting"
        assert result["top_issues"][2]["action_cta"] == "Add missing content"

    def test_summary_stats(self):
        """Test summary statistics generation"""
        suggestions = [
            {"id": str(i), "type": "keyword", "severity": "critical", "title": "Test", "description": "auto-reject"}
            for i in range(2)
        ] + [
            {"id": str(i+2), "type": "formatting", "severity": "warning", "title": "Test", "description": "format"}
            for i in range(3)
        ] + [
            {"id": str(i+5), "type": "content_change", "severity": "info", "title": "Test", "description": "minor"}
            for i in range(5)
        ]

        result = self.prioritizer.prioritize_suggestions(suggestions, top_n=3)
        stats = self.prioritizer.get_summary_stats(result)

        assert stats["top_count"] == 3
        assert stats["total_count"] == 10


class TestPassProbabilityCalculator:
    """Test pass probability calculation logic"""

    def setup_method(self):
        """Set up test fixtures"""
        self.calculator = PassProbabilityCalculator()

    def test_base_probability_high_score(self):
        """Test base probability for high scores"""
        prob = self.calculator._calculate_base_probability(95)
        assert prob == 95.0

    def test_base_probability_low_score(self):
        """Test base probability for low scores"""
        prob = self.calculator._calculate_base_probability(45)
        assert prob == 15.0

    def test_auto_reject_penalty(self):
        """Test that auto-reject severely reduces probability"""
        base_prob = 80.0
        adjusted = self.calculator._apply_critical_adjustments(
            base_prob,
            auto_reject=True,
            critical_issues=[]
        )

        # Should be reduced by 70%
        assert adjusted == 24.0

    def test_critical_issues_penalty(self):
        """Test that critical issues reduce probability"""
        base_prob = 80.0
        critical_issues = ["Issue 1", "Issue 2", "Issue 3"]
        adjusted = self.calculator._apply_critical_adjustments(
            base_prob,
            auto_reject=False,
            critical_issues=critical_issues
        )

        # Each issue reduces by 5%
        # 80 * 0.95 * 0.95 * 0.95 = 68.59
        assert adjusted < base_prob
        assert adjusted > 65

    def test_platform_difficulty(self):
        """Test that Taleo is strictest platform"""
        from backend.services.pass_probability_calculator import ATSPlatform

        taleo_prob = self.calculator._calculate_platform_probability(
            80.0,
            ATSPlatform.TALEO,
            90.0
        )

        greenhouse_prob = self.calculator._calculate_platform_probability(
            80.0,
            ATSPlatform.GREENHOUSE,
            90.0
        )

        # Taleo should be stricter (lower probability)
        assert taleo_prob < greenhouse_prob

    def test_format_score_impact(self):
        """Test that format score affects platform probability"""
        from backend.services.pass_probability_calculator import ATSPlatform

        good_format = self.calculator._calculate_platform_probability(
            70.0,
            ATSPlatform.TALEO,
            90.0
        )

        bad_format = self.calculator._calculate_platform_probability(
            70.0,
            ATSPlatform.TALEO,
            40.0
        )

        # Good format should have higher probability
        assert good_format > bad_format

    def test_confidence_level_with_job_description(self):
        """Test confidence level is high with job description"""
        confidence = self.calculator._determine_confidence_level(
            has_job_description=True,
            keyword_match_rate=0.75,
            format_score=85.0
        )

        assert confidence == ConfidenceLevel.HIGH

    def test_confidence_level_without_data(self):
        """Test confidence level is low without sufficient data"""
        confidence = self.calculator._determine_confidence_level(
            has_job_description=False,
            keyword_match_rate=None,
            format_score=50.0
        )

        assert confidence == ConfidenceLevel.LOW

    def test_interpretation_high_probability(self):
        """Test interpretation for high pass probability"""
        interpretation = self.calculator._get_interpretation(85.0)
        assert "High chance" in interpretation

    def test_interpretation_low_probability(self):
        """Test interpretation for low pass probability"""
        interpretation = self.calculator._get_interpretation(30.0)
        assert "Low chance" in interpretation or "needs improvement" in interpretation

    def test_full_calculation(self):
        """Test complete pass probability calculation"""
        result = self.calculator.calculate_pass_probability(
            overall_score=75.0,
            breakdown={
                "formatting": {"score": 18, "maxScore": 20, "issues": []}
            },
            auto_reject=False,
            critical_issues=[],
            keyword_details={"match_rate": 0.65},
            job_description="Software engineer position"
        )

        assert "overall_probability" in result
        assert "platform_breakdown" in result
        assert "confidence_level" in result
        assert "interpretation" in result
        assert "color_code" in result
        assert "based_on_score" in result

        # Check platform breakdown
        assert "Taleo" in result["platform_breakdown"]
        assert "Workday" in result["platform_breakdown"]
        assert "Greenhouse" in result["platform_breakdown"]

        # Check probability is reasonable
        assert 0 <= result["overall_probability"] <= 100

    def test_color_code_green(self):
        """Test that high probability gets green color"""
        result = self.calculator.calculate_pass_probability(
            overall_score=90.0,
            breakdown={},
            auto_reject=False,
            critical_issues=[],
            keyword_details=None,
            job_description=None
        )

        assert result["color_code"] == "green"

    def test_color_code_yellow(self):
        """Test that moderate probability gets yellow color"""
        result = self.calculator.calculate_pass_probability(
            overall_score=70.0,
            breakdown={},
            auto_reject=False,
            critical_issues=[],
            keyword_details=None,
            job_description=None
        )

        assert result["color_code"] == "yellow"

    def test_color_code_red(self):
        """Test that low probability gets red color"""
        result = self.calculator.calculate_pass_probability(
            overall_score=50.0,
            breakdown={},
            auto_reject=False,
            critical_issues=[],
            keyword_details=None,
            job_description=None
        )

        assert result["color_code"] == "red"


@pytest.mark.integration
class TestPhase3Integration:
    """Integration tests for Phase 3 features"""

    def test_prioritizer_with_real_suggestions(self):
        """Test prioritizer with realistic suggestion data"""
        suggestions = [
            {
                "id": "1",
                "type": "keyword",
                "severity": "critical",
                "title": "Missing required keywords",
                "description": "Job description requires Python, AWS, Docker. Your resume is missing these.",
            },
            {
                "id": "2",
                "type": "formatting",
                "severity": "warning",
                "title": "Tables detected",
                "description": "ATS systems like Taleo cannot parse tables properly.",
            },
            {
                "id": "3",
                "type": "content_change",
                "severity": "suggestion",
                "title": "Weak action verbs",
                "description": "Use stronger action verbs in your bullet points.",
            },
            {
                "id": "4",
                "type": "missing_content",
                "severity": "info",
                "title": "Consider adding metrics",
                "description": "Quantify your achievements with numbers.",
            },
        ]

        prioritizer = SuggestionPrioritizer()
        result = prioritizer.prioritize_suggestions(suggestions, top_n=3)

        # Keyword issue should be in top 3
        top_ids = [s["id"] for s in result["top_issues"]]
        assert "1" in top_ids

        # Check all suggestions are accounted for
        total_in_result = len(result["top_issues"])
        for items in result["remaining_by_priority"].values():
            total_in_result += len(items)
        assert total_in_result == len(suggestions)

    def test_calculator_with_real_score_data(self):
        """Test calculator with realistic score breakdown"""
        breakdown = {
            "keywords": {"score": 25, "maxScore": 35, "issues": []},
            "formatting": {"score": 18, "maxScore": 20, "issues": []},
            "experience": {"score": 15, "maxScore": 20, "issues": []},
            "contact": {"score": 5, "maxScore": 5, "issues": []},
        }

        calculator = PassProbabilityCalculator()
        result = calculator.calculate_pass_probability(
            overall_score=73.0,
            breakdown=breakdown,
            auto_reject=False,
            critical_issues=[],
            keyword_details={"match_rate": 0.60},
            job_description="Full stack developer position"
        )

        # Should have moderate-to-good pass probability
        assert 50 <= result["overall_probability"] <= 85

        # All platforms should have probabilities
        for platform in ["Taleo", "Workday", "Greenhouse"]:
            assert platform in result["platform_breakdown"]
            assert "probability" in result["platform_breakdown"][platform]
            assert "status" in result["platform_breakdown"][platform]
