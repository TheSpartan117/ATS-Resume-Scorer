"""
Suggestion Prioritizer - Analyzes and prioritizes suggestions by severity and impact.

This module implements Phase 3.1 of the Unified Implementation Plan:
- Prioritizes suggestions based on severity and impact
- Returns top 3 most critical issues
- Groups remaining suggestions for progressive disclosure
"""

from typing import List, Dict, Optional, Tuple
from enum import Enum


class Priority(str, Enum):
    """Priority levels for suggestions"""
    CRITICAL = "critical"
    IMPORTANT = "important"
    OPTIONAL = "optional"


class ImpactCategory(str, Enum):
    """Impact categories for prioritization"""
    ATS_REJECTION = "ats_rejection"  # Will cause auto-rejection
    KEYWORD_MATCH = "keyword_match"  # Affects keyword matching score
    FORMATTING = "formatting"  # Formatting issues
    CONTENT_QUALITY = "content_quality"  # Content quality improvements
    MINOR = "minor"  # Minor improvements


class SuggestionPrioritizer:
    """
    Prioritizes suggestions by severity and impact.

    Prioritization algorithm:
    1. Critical severity + ATS rejection = Top priority
    2. High severity + keyword matching = High priority
    3. Medium severity + formatting = Medium priority
    4. Low severity or minor improvements = Low priority
    """

    # Impact scores for different types
    IMPACT_SCORES = {
        ImpactCategory.ATS_REJECTION: 100,
        ImpactCategory.KEYWORD_MATCH: 80,
        ImpactCategory.FORMATTING: 60,
        ImpactCategory.CONTENT_QUALITY: 40,
        ImpactCategory.MINOR: 20,
    }

    # Severity multipliers
    SEVERITY_MULTIPLIERS = {
        "critical": 3.0,
        "high": 2.0,
        "warning": 1.5,
        "medium": 1.0,
        "suggestion": 0.7,
        "low": 0.5,
        "info": 0.3,
    }

    def __init__(self):
        """Initialize the suggestion prioritizer"""
        pass

    def _calculate_impact_score(self, suggestion: Dict) -> float:
        """
        Calculate impact score for a suggestion.

        Args:
            suggestion: Suggestion dictionary with type, severity, etc.

        Returns:
            Impact score (0-300)
        """
        # Determine impact category
        suggestion_type = suggestion.get("type", "").lower()
        severity = suggestion.get("severity", "info").lower()
        title = suggestion.get("title", "").lower()
        description = suggestion.get("description", "").lower()

        # Check for ATS rejection keywords
        if any(keyword in title or keyword in description for keyword in [
            "auto-reject", "auto reject", "rejected", "must have", "required"
        ]):
            impact_category = ImpactCategory.ATS_REJECTION
        # Check for keyword-related issues
        elif "keyword" in title or "keyword" in description or suggestion_type == "keyword":
            impact_category = ImpactCategory.KEYWORD_MATCH
        # Check for formatting issues
        elif "format" in title or "format" in description or suggestion_type == "formatting":
            impact_category = ImpactCategory.FORMATTING
        # Check for content quality
        elif suggestion_type in ["missing_content", "content_change", "writing"]:
            impact_category = ImpactCategory.CONTENT_QUALITY
        else:
            impact_category = ImpactCategory.MINOR

        # Calculate base impact score
        base_impact = self.IMPACT_SCORES[impact_category]

        # Apply severity multiplier
        severity_multiplier = self.SEVERITY_MULTIPLIERS.get(severity, 1.0)

        # Final score
        impact_score = base_impact * severity_multiplier

        return impact_score

    def _assign_priority_label(self, impact_score: float) -> Priority:
        """
        Assign priority label based on impact score.

        Args:
            impact_score: Calculated impact score

        Returns:
            Priority label (CRITICAL, IMPORTANT, OPTIONAL)
        """
        if impact_score >= 150:
            return Priority.CRITICAL
        elif impact_score >= 80:
            return Priority.IMPORTANT
        else:
            return Priority.OPTIONAL

    def _create_action_cta(self, suggestion: Dict) -> str:
        """
        Create a clear call-to-action for a suggestion.

        Args:
            suggestion: Suggestion dictionary

        Returns:
            Clear CTA string
        """
        suggestion_type = suggestion.get("type", "").lower()

        cta_map = {
            "missing_content": "Add missing content",
            "keyword": "Add keywords",
            "formatting": "Fix formatting",
            "writing": "Improve writing",
            "content_change": "Update content",
            "missing_section": "Add section",
        }

        return cta_map.get(suggestion_type, "Review and fix")

    def prioritize_suggestions(
        self,
        suggestions: List[Dict],
        top_n: int = 3
    ) -> Dict:
        """
        Prioritize suggestions and return top N most critical.

        Args:
            suggestions: List of suggestion dictionaries
            top_n: Number of top suggestions to return (default: 3)

        Returns:
            Dictionary with:
                - top_issues: List of top N critical issues
                - remaining_by_priority: Remaining suggestions grouped by priority
                - total_count: Total number of suggestions
        """
        if not suggestions:
            return {
                "top_issues": [],
                "remaining_by_priority": {
                    Priority.CRITICAL: [],
                    Priority.IMPORTANT: [],
                    Priority.OPTIONAL: [],
                },
                "total_count": 0,
            }

        # Calculate impact scores for all suggestions
        scored_suggestions = []
        for suggestion in suggestions:
            impact_score = self._calculate_impact_score(suggestion)
            priority = self._assign_priority_label(impact_score)
            cta = self._create_action_cta(suggestion)

            # Enrich suggestion with priority data
            enriched_suggestion = {
                **suggestion,
                "impact_score": impact_score,
                "priority": priority,
                "action_cta": cta,
            }
            scored_suggestions.append(enriched_suggestion)

        # Sort by impact score (descending)
        scored_suggestions.sort(key=lambda x: x["impact_score"], reverse=True)

        # Get top N issues
        top_issues = scored_suggestions[:top_n]

        # Group remaining suggestions by priority
        remaining = scored_suggestions[top_n:]
        remaining_by_priority = {
            Priority.CRITICAL: [],
            Priority.IMPORTANT: [],
            Priority.OPTIONAL: [],
        }

        for suggestion in remaining:
            priority = suggestion["priority"]
            remaining_by_priority[priority].append(suggestion)

        return {
            "top_issues": top_issues,
            "remaining_by_priority": remaining_by_priority,
            "total_count": len(suggestions),
        }

    def get_summary_stats(self, prioritized: Dict) -> Dict:
        """
        Get summary statistics for prioritized suggestions.

        Args:
            prioritized: Output from prioritize_suggestions()

        Returns:
            Dictionary with summary stats
        """
        remaining = prioritized["remaining_by_priority"]

        return {
            "top_count": len(prioritized["top_issues"]),
            "critical_count": len(remaining[Priority.CRITICAL]),
            "important_count": len(remaining[Priority.IMPORTANT]),
            "optional_count": len(remaining[Priority.OPTIONAL]),
            "total_count": prioritized["total_count"],
        }
