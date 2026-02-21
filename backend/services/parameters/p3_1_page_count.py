"""
P3.1: Page Count Optimization (5 points)

Evaluates resume page count based on experience level.
Level-appropriate page counts prevent information overload or insufficient detail.

Level-Specific Expectations:
- Beginner (0-3 years): 1 page optimal, 2 pages acceptable
- Intermediary (3-7 years): 1-2 pages optimal, 3 pages acceptable
- Senior (7+ years): 2 pages optimal, 3 pages acceptable

Scoring:
- Beginner: 1 page = 5pts, 2 pages = 3pts, 3+ pages = 0pts
- Intermediary: 1-2 pages = 5pts, 3 pages = 2pts, 4+ pages = 0pts
- Senior: 2 pages = 5pts, 3 pages = 4pts, 1 page = 2pts, 4+ pages = 0pts

Research Basis:
- Workday/Greenhouse standard: 1 page for <5 years, 2 pages for 5+ years
- Senior resumes need more space for leadership/impact demonstration
- Beginner resumes should be concise (limited relevant experience)
"""

from typing import Dict, Any, Union, List


class PageCountScorer:
    """Scores resume page count based on experience level."""

    def score(self, page_count: int, level: str) -> Dict[str, Any]:
        """
        Score page count appropriateness for experience level.

        Args:
            page_count: Number of pages in the resume
            level: Experience level ('beginner', 'intermediary', 'senior')

        Returns:
            Dictionary containing:
            - score: Points earned (0-5)
            - level: Experience level used
            - page_count: Number of pages
            - optimal_pages: Optimal page count(s) for this level
            - meets_optimal: Whether page count is optimal
            - recommendation: Actionable feedback
        """
        # Normalize level
        level_normalized = str(level).lower().strip()

        # Handle invalid page counts
        if page_count <= 0:
            return self._invalid_page_count_result(page_count, level)

        # Score based on level
        if level_normalized == 'beginner':
            return self._score_beginner(page_count, level)
        elif level_normalized == 'senior':
            return self._score_senior(page_count, level)
        else:
            # Default to intermediary for any other level
            return self._score_intermediary(page_count, level)

    def _score_beginner(self, page_count: int, level: str) -> Dict[str, Any]:
        """
        Score for beginner level (0-3 years).

        Scoring:
        - 1 page: 5 pts (optimal - beginner should be concise)
        - 2 pages: 3 pts (acceptable but not ideal)
        - 3+ pages: 0 pts (too long for beginner level)
        """
        if page_count == 1:
            return {
                'score': 5,
                'level': level,
                'page_count': page_count,
                'optimal_pages': 1,
                'meets_optimal': True,
                'recommendation': 'Optimal page count for beginner level. Your resume is concise and focused.'
            }
        elif page_count == 2:
            return {
                'score': 3,
                'level': level,
                'page_count': page_count,
                'optimal_pages': 1,
                'meets_optimal': False,
                'recommendation': 'Consider condensing to 1 page. Beginners (0-3 years) should keep resumes brief and impactful.'
            }
        else:  # 3+ pages
            return {
                'score': 0,
                'level': level,
                'page_count': page_count,
                'optimal_pages': 1,
                'meets_optimal': False,
                'recommendation': f'{page_count} pages is too long for beginner level. Reduce to 1 page by focusing on most relevant experiences and achievements.'
            }

    def _score_intermediary(self, page_count: int, level: str) -> Dict[str, Any]:
        """
        Score for intermediary level (3-7 years).

        Scoring:
        - 1-2 pages: 5 pts (optimal range)
        - 3 pages: 2 pts (acceptable but getting long)
        - 4+ pages: 0 pts (too long)
        """
        if page_count in [1, 2]:
            return {
                'score': 5,
                'level': level,
                'page_count': page_count,
                'optimal_pages': [1, 2],
                'meets_optimal': True,
                'recommendation': f'{page_count} page{"s" if page_count > 1 else ""} is optimal for intermediary level. Your resume length is appropriate for your experience.'
            }
        elif page_count == 3:
            return {
                'score': 2,
                'level': level,
                'page_count': page_count,
                'optimal_pages': [1, 2],
                'meets_optimal': False,
                'recommendation': 'Consider condensing to 2 pages. Focus on most impactful achievements and recent experience.'
            }
        else:  # 4+ pages
            return {
                'score': 0,
                'level': level,
                'page_count': page_count,
                'optimal_pages': [1, 2],
                'meets_optimal': False,
                'recommendation': f'{page_count} pages is too long for intermediary level. Reduce to 1-2 pages by removing older or less relevant experiences.'
            }

    def _score_senior(self, page_count: int, level: str) -> Dict[str, Any]:
        """
        Score for senior level (7+ years).

        Scoring:
        - 2 pages: 5 pts (optimal - standard for senior)
        - 3 pages: 4 pts (acceptable for extensive experience/leadership)
        - 1 page: 2 pts (too brief, likely missing important details)
        - 4+ pages: 0 pts (too long, loses focus)
        """
        if page_count == 2:
            return {
                'score': 5,
                'level': level,
                'page_count': page_count,
                'optimal_pages': 2,
                'meets_optimal': True,
                'recommendation': 'Perfect length for senior level. 2 pages allows you to demonstrate leadership impact while maintaining focus.'
            }
        elif page_count == 3:
            return {
                'score': 4,
                'level': level,
                'page_count': page_count,
                'optimal_pages': 2,
                'meets_optimal': False,
                'recommendation': '3 pages is acceptable for extensive senior experience, but consider condensing to 2 pages for better impact and readability.'
            }
        elif page_count == 1:
            return {
                'score': 2,
                'level': level,
                'page_count': page_count,
                'optimal_pages': 2,
                'meets_optimal': False,
                'recommendation': '1 page is too brief for senior level (7+ years). Expand to 2 pages to showcase leadership accomplishments, technical depth, and strategic impact.'
            }
        else:  # 4+ pages
            return {
                'score': 0,
                'level': level,
                'page_count': page_count,
                'optimal_pages': 2,
                'meets_optimal': False,
                'recommendation': f'{page_count} pages is too long, even for senior level. Reduce to 2 pages by focusing on leadership impact, strategic initiatives, and most recent 10-15 years.'
            }

    def _invalid_page_count_result(self, page_count: int, level: str) -> Dict[str, Any]:
        """Return result for invalid page count (0 or negative)."""
        return {
            'score': 0,
            'level': level,
            'page_count': page_count,
            'optimal_pages': self._get_optimal_pages_for_level(level),
            'meets_optimal': False,
            'recommendation': 'Invalid page count. Resume must have at least 1 page.'
        }

    def _get_optimal_pages_for_level(self, level: str) -> Union[int, List[int]]:
        """Get optimal page count(s) for a level."""
        level_normalized = str(level).lower().strip()

        if level_normalized == 'beginner':
            return 1
        elif level_normalized == 'senior':
            return 2
        else:  # intermediary or default
            return [1, 2]


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
