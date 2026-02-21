"""
P3.1: Page Count Optimization (5 points)

Evaluates resume page count with a preference for conciseness.
Modern recruiting favors brief, scannable resumes regardless of experience level.

Universal Scoring (all levels):
- 1 page: 5 pts (optimal - concise and focused)
- 2 pages: 4 pts (acceptable - small penalty for length)
- 3 pages: 2 pts (too long - hard to scan quickly)
- 4+ pages: 0 pts (way too long - loses focus)

Rationale:
- Recruiters spend 6-7 seconds on initial resume scan
- Concise resumes are easier to review and remember
- 1 page forces prioritization of most impactful achievements
- Longer resumes dilute key messages and reduce readability
"""

from typing import Dict, Any, Union, List


class PageCountScorer:
    """Scores resume page count based on experience level."""

    def score(self, page_count: int, level: str) -> Dict[str, Any]:
        """
        Score page count with universal preference for conciseness.

        Args:
            page_count: Number of pages in the resume
            level: Experience level (kept for compatibility but not used in scoring)

        Returns:
            Dictionary containing:
            - score: Points earned (0-5)
            - level: Experience level used
            - page_count: Number of pages
            - optimal_pages: Optimal page count (always 1)
            - meets_optimal: Whether page count is optimal
            - recommendation: Actionable feedback
        """
        # Handle invalid page counts
        if page_count <= 0:
            return self._invalid_page_count_result(page_count, level)

        # Universal scoring regardless of experience level
        return self._score_universal(page_count, level)

    def _score_universal(self, page_count: int, level: str) -> Dict[str, Any]:
        """
        Universal scoring for all experience levels.
        Prioritizes conciseness regardless of experience.

        Scoring:
        - 1 page: 5 pts (optimal - concise and focused)
        - 2 pages: 4 pts (acceptable - small penalty for length)
        - 3 pages: 2 pts (too long - hard to scan quickly)
        - 4+ pages: 0 pts (way too long - loses focus)
        """
        if page_count == 1:
            return {
                'score': 5,
                'level': level,
                'page_count': page_count,
                'optimal_pages': 1,
                'meets_optimal': True,
                'recommendation': 'Perfect length. 1 page is concise, focused, and easy for recruiters to scan quickly.'
            }
        elif page_count == 2:
            return {
                'score': 4,
                'level': level,
                'page_count': page_count,
                'optimal_pages': 1,
                'meets_optimal': False,
                'recommendation': '2 pages is acceptable but consider condensing to 1 page. Focus on your most impactful achievements to improve scannability.'
            }
        elif page_count == 3:
            return {
                'score': 2,
                'level': level,
                'page_count': page_count,
                'optimal_pages': 1,
                'meets_optimal': False,
                'recommendation': '3 pages is too long. Reduce to 1-2 pages by removing less relevant experiences and focusing on recent, high-impact achievements.'
            }
        else:  # 4+ pages
            return {
                'score': 0,
                'level': level,
                'page_count': page_count,
                'optimal_pages': 1,
                'meets_optimal': False,
                'recommendation': f'{page_count} pages is way too long. Drastically reduce to 1 page by showcasing only your most critical accomplishments and relevant skills.'
            }

    def _invalid_page_count_result(self, page_count: int, level: str) -> Dict[str, Any]:
        """Return result for invalid page count (0 or negative)."""
        return {
            'score': 0,
            'level': level,
            'page_count': page_count,
            'optimal_pages': 1,
            'meets_optimal': False,
            'recommendation': 'Invalid page count. Resume must have at least 1 page.'
        }


def score_page_count(page_count: int, level: str) -> Dict[str, Any]:
    """
    Convenience function to score page count.

    Args:
        page_count: Number of pages in the resume
        level: Experience level ('beginner', 'intermediary', 'senior')

    Returns:
        Score result dictionary

    Example:
        >>> result = score_page_count(page_count=2, level='senior')
        >>> result['score']
        5
        >>> result['recommendation']
        'Perfect length for senior level...'
    """
    scorer = PageCountScorer()
    return scorer.score(page_count, level)
