"""
Required Keywords Matcher Service - Task 11: P1.1 Required Keywords Match (25 pts)

This is the HIGHEST-WEIGHTED parameter in the ATS scorer.

Scoring structure (tiered, not linear):
- ≥60% match = 25 points (full credit) - Industry standard passing threshold
- ≥40% match = 15 points (partial credit)
- ≥25% match = 5 points (minimal credit)
- <25% match = 0 points (fail)

Research basis:
- 60% keyword match is the standard passing threshold (Workday)
- Hybrid matching (semantic + exact) reduces false negatives by 35-45%
- Tiered scoring better reflects real ATS behavior than linear scoring

Formula:
- Uses HybridKeywordMatcher (70% semantic + 30% exact)
- Match threshold: 0.6 (60% similarity to consider a keyword "matched")
- Level-aware thresholds from scoring_thresholds.py

Source: ATS Research Comprehensive Report (Workday, Greenhouse, Lever analysis)
"""

from typing import Dict, List, Any
from services.hybrid_keyword_matcher import get_hybrid_matcher
from config.scoring_thresholds import get_thresholds_for_level


class RequiredKeywordsMatcher:
    """
    Match required keywords against resume using hybrid semantic+exact matching.

    This is Parameter P1.1 - the highest-weighted parameter in the ATS scorer.
    Research shows that keyword match rate is the #1 factor in ATS screening.

    Key features:
    - Tiered scoring (not linear) based on match rate
    - Hybrid matching reduces false negatives
    - Level-aware thresholds
    - Detailed match statistics
    """

    # Maximum points for this parameter
    MAX_POINTS = 25

    # Tiered scoring thresholds (research-backed)
    TIER_THRESHOLDS = {
        'excellent': 60,  # ≥60% = 25 pts (Workday standard)
        'partial': 40,    # ≥40% = 15 pts
        'minimal': 25,    # ≥25% = 5 pts
        'fail': 0         # <25% = 0 pts
    }

    # Point allocation per tier
    TIER_POINTS = {
        'excellent': 25,
        'partial': 15,
        'minimal': 5,
        'fail': 0
    }

    # Match threshold for hybrid matcher (0.6 = 60% similarity)
    MATCH_THRESHOLD = 0.6

    def __init__(self):
        """Initialize with hybrid keyword matcher."""
        self.hybrid_matcher = get_hybrid_matcher()

    def _determine_tier(self, match_rate: float) -> str:
        """
        Determine scoring tier based on match rate.

        Args:
            match_rate: Percentage of keywords matched (0-100)

        Returns:
            Tier name: 'excellent', 'partial', 'minimal', or 'fail'
        """
        if match_rate >= self.TIER_THRESHOLDS['excellent']:
            return 'excellent'
        elif match_rate >= self.TIER_THRESHOLDS['partial']:
            return 'partial'
        elif match_rate >= self.TIER_THRESHOLDS['minimal']:
            return 'minimal'
        else:
            return 'fail'

    def _calculate_tier_score(self, tier: str) -> int:
        """
        Get point value for a tier.

        Args:
            tier: Tier name ('excellent', 'partial', 'minimal', 'fail')

        Returns:
            Point value for that tier
        """
        return self.TIER_POINTS.get(tier, 0)

    def calculate_score(
        self,
        keywords: List[str],
        resume_text: str,
        experience_level: str = "intermediary"
    ) -> Dict[str, Any]:
        """
        Calculate required keywords match score using hybrid matching.

        This implements the tiered scoring approach:
        1. Match each keyword against resume (hybrid semantic+exact)
        2. Calculate match rate (% of keywords matched)
        3. Determine tier based on match rate
        4. Assign points based on tier

        Args:
            keywords: List of required keywords from job description
            resume_text: Full resume text
            experience_level: Experience level ('beginner', 'intermediary', 'senior')

        Returns:
            Dictionary containing:
            {
                'score': int,              # Points awarded (0-25)
                'match_rate': float,       # Percentage of keywords matched (0-100)
                'matched_keywords': int,   # Number of keywords matched
                'total_keywords': int,     # Total number of keywords
                'threshold_met': bool,     # Whether passing threshold (60%) was met
                'tier': str,               # Scoring tier ('excellent', 'partial', 'minimal', 'fail')
                'details': Dict            # Detailed match information
            }

        Example:
            >>> matcher = RequiredKeywordsMatcher()
            >>> result = matcher.calculate_score(
            ...     keywords=["Python", "Django", "Docker", "PostgreSQL"],
            ...     resume_text="Python developer with Django and Docker experience",
            ...     experience_level="intermediary"
            ... )
            >>> result['score']
            25
            >>> result['match_rate']
            75.0
            >>> result['tier']
            'excellent'
        """
        # Handle edge cases
        if not keywords or not resume_text:
            return {
                'score': 0,
                'match_rate': 0.0,
                'matched_keywords': 0,
                'total_keywords': len(keywords) if keywords else 0,
                'threshold_met': False,
                'tier': 'fail',
                'details': {
                    'individual_scores': {},
                    'matched': [],
                    'unmatched': keywords if keywords else []
                }
            }

        # Get level-specific thresholds (for future enhancement)
        thresholds = get_thresholds_for_level(experience_level)

        # Use hybrid matcher to get match summary
        match_summary = self.hybrid_matcher.get_match_summary(
            keywords=keywords,
            resume_text=resume_text,
            threshold=self.MATCH_THRESHOLD
        )

        # Extract match statistics
        match_rate = match_summary['match_rate']
        matched_count = match_summary['matched_keywords']
        total_count = match_summary['total_keywords']

        # Determine tier and calculate score
        tier = self._determine_tier(match_rate)
        score = self._calculate_tier_score(tier)

        # Check if passing threshold met (60%)
        threshold_met = match_rate >= self.TIER_THRESHOLDS['excellent']

        return {
            'score': score,
            'match_rate': match_rate,
            'matched_keywords': matched_count,
            'total_keywords': total_count,
            'threshold_met': threshold_met,
            'tier': tier,
            'details': {
                'individual_scores': match_summary['scores'],
                'matched': match_summary['matched'],
                'unmatched': match_summary['unmatched']
            }
        }

    def get_feedback(self, result: Dict[str, Any]) -> List[str]:
        """
        Generate actionable feedback based on matching results.

        Args:
            result: Result dictionary from calculate_score()

        Returns:
            List of feedback messages

        Example:
            >>> feedback = matcher.get_feedback(result)
            >>> print(feedback[0])
            "Excellent keyword match! Your resume contains 75% of required keywords."
        """
        feedback = []
        tier = result['tier']
        match_rate = result['match_rate']
        matched = result['matched_keywords']
        total = result['total_keywords']

        if tier == 'excellent':
            feedback.append(
                f"✓ Excellent keyword match! Your resume contains {match_rate:.0f}% "
                f"({matched}/{total}) of required keywords."
            )
        elif tier == 'partial':
            feedback.append(
                f"⚠ Partial keyword match. Your resume contains {match_rate:.0f}% "
                f"({matched}/{total}) of required keywords. Try to reach 60% for full credit."
            )
            # Suggest adding unmatched keywords
            unmatched = result['details']['unmatched']
            if unmatched:
                top_missing = unmatched[:3]
                feedback.append(
                    f"Consider adding these missing keywords: {', '.join(top_missing)}"
                )
        elif tier == 'minimal':
            feedback.append(
                f"⚠ Low keyword match. Your resume contains only {match_rate:.0f}% "
                f"({matched}/{total}) of required keywords. This may not pass ATS screening."
            )
            unmatched = result['details']['unmatched']
            if unmatched:
                top_missing = unmatched[:5]
                feedback.append(
                    f"Priority keywords to add: {', '.join(top_missing)}"
                )
        else:  # fail
            feedback.append(
                f"✗ Keyword match failed. Your resume contains only {match_rate:.0f}% "
                f"({matched}/{total}) of required keywords. Most ATS systems require ≥60%."
            )
            unmatched = result['details']['unmatched']
            if unmatched:
                feedback.append(
                    f"Critical keywords missing: {', '.join(unmatched[:5])}"
                )

        return feedback


# Singleton instance for efficiency
_required_keywords_matcher_instance = None


def get_required_keywords_matcher() -> RequiredKeywordsMatcher:
    """
    Get singleton instance of RequiredKeywordsMatcher.

    Ensures matcher is instantiated only once per process for efficiency.

    Returns:
        RequiredKeywordsMatcher instance
    """
    global _required_keywords_matcher_instance
    if _required_keywords_matcher_instance is None:
        _required_keywords_matcher_instance = RequiredKeywordsMatcher()
    return _required_keywords_matcher_instance
