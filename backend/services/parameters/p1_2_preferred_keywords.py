"""
P1.2 - Preferred Keywords Match (10 points)

Matches "nice-to-have" preferred keywords from job description against resume.
More lenient than required keywords (P1.1) to reflect optional nature.

Scoring Tiers:
- ≥50% match: 10 points (excellent coverage)
- ≥30% match: 6 points (good coverage)
- ≥15% match: 3 points (minimal coverage)
- <15% match: 0 points (insufficient)

Research basis:
- Preferred keywords are optional but valuable differentiators
- More lenient thresholds vs. required keywords (60% → 50%)
- Still significant point value (10 pts) when well-matched
- Based on Workday/Greenhouse ATS analysis

Usage:
    from backend.services.parameters.p1_2_preferred_keywords import PreferredKeywordsMatcher

    matcher = PreferredKeywordsMatcher()
    result = matcher.calculate_score(
        preferred_keywords=["React", "TypeScript", "GraphQL"],
        resume_text=resume_text,
        experience_level="intermediary"
    )

    print(f"Score: {result['score']}/10")
    print(f"Match: {result['match_percentage']}%")
    print(f"Matched: {result['matched_keywords']}")
"""

from typing import Dict, List, Any


class PreferredKeywordsMatcher:
    """
    Matches preferred (nice-to-have) keywords with tiered scoring.

    Uses hybrid semantic + exact matching (70%/30%) via HybridKeywordMatcher
    to reduce false negatives and handle synonyms/variations.

    Scoring Tiers:
    - Tier 1 (≥50%): 10 points - Excellent keyword coverage
    - Tier 2 (≥30%): 6 points - Good keyword coverage
    - Tier 3 (≥15%): 3 points - Minimal keyword coverage
    - Below Threshold (<15%): 0 points - Insufficient coverage

    More lenient than required keywords to reflect "nice-to-have" nature.
    """

    # Scoring tiers: (min_percentage, points)
    # Ordered from highest to lowest threshold for efficient matching
    SCORING_TIERS = [
        (50, 10, "Tier 1 (≥50%)"),
        (30, 6, "Tier 2 (≥30%)"),
        (15, 3, "Tier 3 (≥15%)"),
        (0, 0, "Below Threshold (<15%)")
    ]

    # Hybrid matching threshold (60% similarity considered a match)
    MATCH_THRESHOLD = 0.6

    def __init__(self):
        """Initialize with hybrid keyword matcher for semantic matching."""
        from backend.services.hybrid_keyword_matcher import get_hybrid_matcher
        self.hybrid_matcher = get_hybrid_matcher()

    def calculate_score(
        self,
        preferred_keywords: List[str],
        resume_text: str,
        experience_level: str = "intermediary"
    ) -> Dict[str, Any]:
        """
        Calculate P1.2 score for preferred keyword matching.

        Args:
            preferred_keywords: List of preferred keywords from job description
                               (nice-to-have skills, technologies, tools)
            resume_text: Full resume text to match against
            experience_level: Experience level (beginner, intermediary, senior)
                            Currently for future use, doesn't affect scoring yet

        Returns:
            Dictionary containing:
            {
                'score': float,                   # 0-10 points
                'match_percentage': float,        # 0-100%
                'matched_count': int,             # Number of keywords matched
                'total_keywords': int,            # Total preferred keywords
                'tier': str,                      # Which tier achieved
                'matched_keywords': List[str],    # List of matched keywords
                'unmatched_keywords': List[str],  # List of unmatched keywords
                'experience_level': str           # Experience level used
            }

        Example:
            >>> matcher = PreferredKeywordsMatcher()
            >>> result = matcher.calculate_score(
            ...     preferred_keywords=["React", "TypeScript", "GraphQL"],
            ...     resume_text="Frontend developer with React and TypeScript experience",
            ...     experience_level="intermediary"
            ... )
            >>> result['score']
            10  # 66.67% match (2/3) → ≥50% → 10 points
        """
        # Handle edge cases
        if not preferred_keywords or not resume_text:
            return {
                'score': 0,
                'match_percentage': 0.0,
                'matched_count': 0,
                'total_keywords': len(preferred_keywords) if preferred_keywords else 0,
                'tier': "Below Threshold (<15%)",
                'matched_keywords': [],
                'unmatched_keywords': list(preferred_keywords) if preferred_keywords else [],
                'experience_level': experience_level
            }

        # Deduplicate keywords while preserving order
        unique_keywords = []
        seen = set()
        for kw in preferred_keywords:
            kw_lower = kw.lower().strip()
            if kw_lower and kw_lower not in seen:
                unique_keywords.append(kw)
                seen.add(kw_lower)

        total_keywords = len(unique_keywords)

        if total_keywords == 0:
            return {
                'score': 0,
                'match_percentage': 0.0,
                'matched_count': 0,
                'total_keywords': 0,
                'tier': "Below Threshold (<15%)",
                'matched_keywords': [],
                'unmatched_keywords': [],
                'experience_level': experience_level
            }

        # Get match summary from hybrid matcher
        match_summary = self.hybrid_matcher.get_match_summary(
            keywords=unique_keywords,
            resume_text=resume_text,
            threshold=self.MATCH_THRESHOLD
        )

        matched_count = match_summary['matched_keywords']
        match_percentage = match_summary['match_rate']  # 0-100
        matched_keywords = match_summary['matched']
        unmatched_keywords = match_summary['unmatched']

        # Determine tier and score
        score, tier = self._get_score_for_percentage(match_percentage)

        return {
            'score': score,
            'match_percentage': round(match_percentage, 2),
            'matched_count': matched_count,
            'total_keywords': total_keywords,
            'tier': tier,
            'matched_keywords': matched_keywords,
            'unmatched_keywords': unmatched_keywords,
            'experience_level': experience_level
        }

    def _get_score_for_percentage(self, match_percentage: float) -> tuple:
        """
        Get score and tier name for given match percentage.

        Args:
            match_percentage: Match percentage (0-100)

        Returns:
            Tuple of (score, tier_name)

        Example:
            >>> self._get_score_for_percentage(65.0)
            (10, "Tier 1 (≥50%)")
            >>> self._get_score_for_percentage(35.0)
            (6, "Tier 2 (≥30%)")
        """
        for min_percentage, points, tier_name in self.SCORING_TIERS:
            if match_percentage >= min_percentage:
                return points, tier_name

        # Fallback (should never reach here due to 0% tier)
        return 0, "Below Threshold (<15%)"

    def get_scoring_tiers(self) -> List[Dict[str, Any]]:
        """
        Get all scoring tiers for documentation/display purposes.

        Returns:
            List of tier dictionaries with threshold, points, and name
        """
        return [
            {
                'min_percentage': min_pct,
                'points': points,
                'tier_name': tier_name
            }
            for min_pct, points, tier_name in self.SCORING_TIERS
        ]


# Singleton instance for efficiency
_preferred_keywords_matcher_instance = None


def get_preferred_keywords_matcher() -> PreferredKeywordsMatcher:
    """
    Get singleton instance of PreferredKeywordsMatcher.

    Ensures hybrid matcher is loaded only once per process for efficiency.

    Returns:
        PreferredKeywordsMatcher instance
    """
    global _preferred_keywords_matcher_instance
    if _preferred_keywords_matcher_instance is None:
        _preferred_keywords_matcher_instance = PreferredKeywordsMatcher()
    return _preferred_keywords_matcher_instance
