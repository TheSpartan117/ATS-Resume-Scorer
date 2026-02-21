"""
P5.3: Experience Depth (2 points)

Validates sufficient detail in experience section based on experience level.
Ensures resume has adequate number of detailed experience entries.

Level-Specific Minimums:
- Beginner (0-3 years): ≥2 detailed entries = 2 points
- Intermediary (3-7 years): ≥3 detailed entries = 2 points
- Senior (7+ years): ≥4 detailed entries = 2 points

Entry Requirements:
Each entry must have ALL of the following:
- Company name
- Job title
- Dates (both start and end)
- Bullets OR description (at least one)

Scoring:
- Meets minimum = 2 points
- Below minimum = 0 points

Research Basis:
- TopResume: Detailed experience entries demonstrate depth and credibility
- ResumeWorded: ATS systems prioritize resumes with complete work history
- Career experts: Level-appropriate depth prevents gaps and builds trust
"""

from typing import List, Dict, Any, Optional


class ExperienceDepthScorer:
    """
    Score resumes based on experience entry depth and completeness.

    Validates that resume has sufficient number of detailed experience entries
    appropriate for the candidate's experience level.
    """

    def __init__(self):
        self.max_score = 2
        self.level_minimums = {
            'beginner': 2,
            'intermediary': 3,
            'senior': 4
        }

    def score(self, experiences: Optional[List[Dict]], level: str) -> Dict[str, Any]:
        """
        Score experience depth based on number of complete entries.

        Args:
            experiences: List of experience entries from parsed resume
            level: Experience level ('beginner', 'intermediary', 'senior')

        Returns:
            {
                'score': int (0 or 2),
                'max_score': int (2),
                'entry_count': int,
                'level': str,
                'meets_minimum': bool,
                'details': str
            }
        """
        # Normalize level
        level_normalized = str(level).lower().strip()

        # Handle None or empty experiences
        if not experiences:
            return self._create_result(
                score=0,
                entry_count=0,
                level=level,
                meets_minimum=False,
                details=self._generate_details(0, level_normalized, False)
            )

        # Count complete entries
        complete_count = self._count_complete_entries(experiences)

        # Get minimum required for this level
        minimum_required = self._get_minimum_for_level(level_normalized)

        # Determine if minimum is met
        meets_minimum = complete_count >= minimum_required

        # Calculate score
        score = self.max_score if meets_minimum else 0

        # Generate details
        details = self._generate_details(complete_count, level_normalized, meets_minimum)

        return self._create_result(
            score=score,
            entry_count=complete_count,
            level=level,
            meets_minimum=meets_minimum,
            details=details
        )

    def _count_complete_entries(self, experiences: List[Dict]) -> int:
        """
        Count number of complete experience entries.

        A complete entry must have:
        - title (non-empty)
        - company (non-empty)
        - startDate (non-empty)
        - endDate (non-empty)
        - achievements (non-empty list) OR description (non-empty)

        Args:
            experiences: List of experience dictionaries

        Returns:
            Count of complete entries
        """
        count = 0

        for entry in experiences:
            if self._is_complete_entry(entry):
                count += 1

        return count

    def _is_complete_entry(self, entry: Dict) -> bool:
        """
        Check if an experience entry is complete.

        Args:
            entry: Experience dictionary

        Returns:
            True if entry has all required components
        """
        # Check title (required, non-empty)
        title = entry.get('title', '').strip()
        if not title:
            return False

        # Check company (required, non-empty)
        company = entry.get('company', '').strip()
        if not company:
            return False

        # Check dates (both required, non-empty)
        start_date = entry.get('startDate', '').strip()
        end_date = entry.get('endDate', '').strip()
        if not start_date or not end_date:
            return False

        # Check bullets or description (at least one required)
        achievements = entry.get('achievements', [])
        description = entry.get('description', '').strip()

        has_bullets = isinstance(achievements, list) and len(achievements) > 0
        has_description = bool(description)

        if not has_bullets and not has_description:
            return False

        return True

    def _get_minimum_for_level(self, level: str) -> int:
        """
        Get minimum entry count required for a level.

        Args:
            level: Experience level (normalized)

        Returns:
            Minimum required entry count
        """
        # Default to intermediary if level not recognized
        return self.level_minimums.get(level, self.level_minimums['intermediary'])

    def _generate_details(self, count: int, level: str, meets_minimum: bool) -> str:
        """
        Generate detailed feedback about experience depth.

        Args:
            count: Number of complete entries found
            level: Experience level
            meets_minimum: Whether minimum was met

        Returns:
            Detailed feedback string
        """
        minimum_required = self._get_minimum_for_level(level)

        if meets_minimum:
            return (
                f"Experience depth is sufficient for {level} level. "
                f"Found {count} complete experience entries (minimum: {minimum_required}). "
                f"Each entry includes company, title, dates, and detailed bullets/description."
            )
        else:
            return (
                f"Experience depth is insufficient for {level} level. "
                f"Found {count} complete experience entries, but {minimum_required} are required. "
                f"Ensure each entry includes: company name, job title, dates (start and end), "
                f"and detailed bullets or description. Add more detailed experience entries to meet the minimum."
            )

    def _create_result(
        self,
        score: int,
        entry_count: int,
        level: str,
        meets_minimum: bool,
        details: str
    ) -> Dict[str, Any]:
        """
        Create standardized result dictionary.

        Args:
            score: Points earned
            entry_count: Number of complete entries
            level: Experience level
            meets_minimum: Whether minimum was met
            details: Feedback details

        Returns:
            Result dictionary
        """
        return {
            'score': score,
            'max_score': self.max_score,
            'entry_count': entry_count,
            'level': level,
            'meets_minimum': meets_minimum,
            'details': details
        }


# Convenience function for direct usage
def score_experience_depth(experiences: Optional[List[Dict]], level: str) -> Dict[str, Any]:
    """
    Score experience depth based on entry completeness.

    Args:
        experiences: List of experience entries from parsed resume
        level: Experience level ('beginner', 'intermediary', 'senior')

    Returns:
        Scoring result dictionary

    Example:
        >>> experiences = [
        ...     {
        ...         'title': 'Software Engineer',
        ...         'company': 'Tech Corp',
        ...         'startDate': 'Jan 2020',
        ...         'endDate': 'Dec 2021',
        ...         'achievements': ['Built API', 'Led team']
        ...     },
        ...     {
        ...         'title': 'Junior Developer',
        ...         'company': 'Startup Inc',
        ...         'startDate': 'Jun 2018',
        ...         'endDate': 'Dec 2019',
        ...         'description': 'Developed web applications'
        ...     }
        ... ]
        >>> result = score_experience_depth(experiences, 'beginner')
        >>> print(f"Score: {result['score']}/2, Entries: {result['entry_count']}")
    """
    scorer = ExperienceDepthScorer()
    return scorer.score(experiences, level)
