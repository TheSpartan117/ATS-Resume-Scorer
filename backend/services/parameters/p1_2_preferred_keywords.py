"""
P1.2 - Preferred Keywords Match (10 points)

Matches "nice-to-have" preferred keywords from job description against resume.
More lenient than required keywords (P1.1) to reflect optional nature.

Scoring: Incremental points per matched keyword (capped at 10 points)
- Each matched keyword adds points based on typical keyword list size
- Formula: score = min(matched_count * points_per_keyword, 10)
- Points per keyword calculated dynamically based on total keyword count
- Minimum 0.5 point per keyword, maximum 1.0 point per keyword

Research basis:
- Preferred keywords are optional but valuable differentiators
- Incremental scoring provides better differentiation between candidates
- Hybrid matching reduces false negatives and handles synonyms/variations
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
    Matches preferred (nice-to-have) keywords with incremental scoring.

    Uses hybrid semantic + exact matching (70%/30%) via HybridKeywordMatcher
    to reduce false negatives and handle synonyms/variations.

    Scoring: Each matched keyword adds points up to maximum of 10
    - Points per keyword calculated dynamically: MAX_SCORE / total_keywords
    - Clamped between MIN_POINTS_PER_KEYWORD and MAX_POINTS_PER_KEYWORD
    - Formula: score = min(matched_count × points_per_keyword, 10)

    More lenient than required keywords to reflect "nice-to-have" nature.
    """

    # Maximum score for this parameter
    MAX_SCORE = 10

    # Points per keyword boundaries
    # - For many keywords (20+): ~0.5 point each
    # - For few keywords (10): ~1.0 point each
    MIN_POINTS_PER_KEYWORD = 0.5
    MAX_POINTS_PER_KEYWORD = 1.0

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
                'points_per_keyword': 0.0,
                'scoring_formula': 'No keywords or resume text',
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
                'points_per_keyword': 0.0,
                'scoring_formula': 'No keywords provided',
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

        # Calculate points per keyword dynamically based on total keyword count
        # Formula: points_per_keyword = MAX_SCORE / total_keywords
        # Clamped between MIN and MAX to handle edge cases
        points_per_keyword = self.MAX_SCORE / total_keywords if total_keywords > 0 else 0
        points_per_keyword = max(self.MIN_POINTS_PER_KEYWORD,
                                min(self.MAX_POINTS_PER_KEYWORD, points_per_keyword))

        # Apply incremental scoring: each matched keyword adds points
        # Formula: score = min(matched_count * points_per_keyword, MAX_SCORE)
        raw_score = matched_count * points_per_keyword
        score = min(round(raw_score, 2), self.MAX_SCORE)

        return {
            'score': score,
            'match_percentage': round(match_percentage, 2),
            'matched_count': matched_count,
            'total_keywords': total_keywords,
            'points_per_keyword': round(points_per_keyword, 2),
            'scoring_formula': f'{matched_count} matched × {round(points_per_keyword, 2)} pts = {score} pts (capped at {self.MAX_SCORE})',
            'matched_keywords': matched_keywords,
            'unmatched_keywords': unmatched_keywords,
            'experience_level': experience_level
        }


    def score(
        self,
        preferred_keywords: List[str],
        resume_text: str,
        experience_level: str = "intermediary"
    ) -> Dict[str, Any]:
        """
        Alias for calculate_score() to maintain consistency with other scorers.

        This method provides a consistent interface across all parameter scorers.
        """
        return self.calculate_score(preferred_keywords, resume_text, experience_level)

    def get_scoring_config(self) -> Dict[str, Any]:
        """
        Get the scoring configuration for this parameter.

        Returns:
            Dictionary with scoring configuration details

        Example:
            >>> matcher = PreferredKeywordsMatcher()
            >>> matcher.get_scoring_config()
            {'max_score': 10, 'min_points_per_keyword': 0.5, ...}
        """
        return {
            'max_score': self.MAX_SCORE,
            'min_points_per_keyword': self.MIN_POINTS_PER_KEYWORD,
            'max_points_per_keyword': self.MAX_POINTS_PER_KEYWORD,
            'match_threshold': self.MATCH_THRESHOLD,
            'scoring_type': 'incremental',
            'formula': 'score = min(matched_count × points_per_keyword, 10)'
        }


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
