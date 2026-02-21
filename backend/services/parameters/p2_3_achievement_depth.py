"""
P2.3: Achievement Depth / Vague Phrases (5 points)

Penalizes weak, vague language that lacks achievement clarity.
Uses VaguePhraseDetector to identify passive, non-specific descriptions.

Scoring Formula:
- 0 vague phrases = 5 points (EXCELLENT - strong, specific achievements)
- 1-2 vague phrases = 4 points (GOOD - mostly specific)
- 3-4 vague phrases = 2 points (FAIR - too many vague descriptions)
- 5+ vague phrases = 0 points (POOR - predominantly vague)

Research Basis:
- ResumeWorded: Strong action verbs > passive responsibility statements
- Jobscan: Specific achievements outperform generic duties by 60%
- TopResume: Vague phrases like "responsible for" reduce ATS scores
"""

from typing import List, Dict, Any
from services.vague_phrase_detector import VaguePhraseDetector


class AchievementDepthScorer:
    """
    Score resumes based on achievement depth and specificity.

    Penalizes vague, passive phrases that indicate weak achievement descriptions.
    Rewards strong, specific, results-oriented bullet points.
    """

    def __init__(self):
        self.detector = VaguePhraseDetector()
        self.max_score = 5

    def score(self, bullets: List[str]) -> Dict[str, Any]:
        """
        Score bullets based on achievement depth (absence of vague phrases).

        Args:
            bullets: List of resume bullet points across all sections

        Returns:
            {
                'score': int (0-5),
                'max_score': int (5),
                'vague_phrase_count': int,
                'found_phrases': List[str],
                'penalty_tier': str ('EXCELLENT', 'GOOD', 'FAIR', 'POOR'),
                'feedback': str
            }
        """
        # Handle edge case: empty bullets
        if not bullets:
            return {
                'score': 5,
                'max_score': self.max_score,
                'vague_phrase_count': 0,
                'found_phrases': [],
                'penalty_tier': 'EXCELLENT',
                'feedback': 'No bullets provided to analyze. Default to excellent score.'
            }

        # Combine all bullets into single text for detection
        resume_text = ' '.join(bullets)

        # Use VaguePhraseDetector to find vague phrases
        detection_result = self.detector.detect(resume_text)

        vague_count = detection_result['vague_phrase_count']
        found_phrases = detection_result['found_phrases']

        # Calculate score based on penalty structure
        score, penalty_tier = self._calculate_score(vague_count)

        # Generate detailed feedback
        feedback = self._generate_feedback(
            vague_count,
            found_phrases,
            score,
            penalty_tier,
            len(bullets)
        )

        return {
            'score': score,
            'max_score': self.max_score,
            'vague_phrase_count': vague_count,
            'found_phrases': found_phrases,
            'penalty_tier': penalty_tier,
            'feedback': feedback
        }

    def _calculate_score(self, vague_count: int) -> tuple:
        """
        Calculate score and penalty tier based on vague phrase count.

        Args:
            vague_count: Number of vague phrases detected

        Returns:
            Tuple of (score, penalty_tier)
        """
        if vague_count == 0:
            return 5, 'EXCELLENT'
        elif 1 <= vague_count <= 2:
            return 4, 'GOOD'
        elif 3 <= vague_count <= 4:
            return 2, 'FAIR'
        else:  # 5+
            return 0, 'POOR'

    def _generate_feedback(
        self,
        vague_count: int,
        found_phrases: List[str],
        score: int,
        penalty_tier: str,
        total_bullets: int
    ) -> str:
        """Generate detailed feedback about achievement depth."""

        feedback_parts = []

        # Overall performance
        feedback_parts.append(
            f"Achievement Depth Score: {score}/{self.max_score} points. "
            f"Detected {vague_count} vague phrase(s) across {total_bullets} bullet points. "
            f"Performance: {penalty_tier}."
        )

        # Performance-specific feedback
        if penalty_tier == 'EXCELLENT':
            feedback_parts.append(
                "\n\nExcellent achievement specificity! Your resume uses strong, "
                "action-oriented language with no vague phrases. This demonstrates "
                "clear ownership and measurable impact."
            )

        elif penalty_tier == 'GOOD':
            feedback_parts.append(
                f"\n\nGood achievement specificity with {vague_count} minor issue(s). "
                "Most of your bullets are specific and action-oriented. "
                "Consider replacing the following vague phrases with stronger action verbs:"
            )
            # List found phrases
            unique_phrases = list(set(found_phrases))
            for phrase in unique_phrases[:3]:  # Show up to 3 examples
                feedback_parts.append(f"\n  - \"{phrase}\"")

        elif penalty_tier == 'FAIR':
            feedback_parts.append(
                f"\n\nAchievement specificity needs improvement. Found {vague_count} vague phrases. "
                "These weaken your impact statements and reduce ATS effectiveness."
            )
            # List found phrases
            unique_phrases = list(set(found_phrases))
            feedback_parts.append("\n\nVague phrases to replace:")
            for phrase in unique_phrases[:5]:  # Show up to 5 examples
                feedback_parts.append(f"\n  - \"{phrase}\"")

        else:  # POOR
            feedback_parts.append(
                f"\n\nSignificant achievement depth issues. Detected {vague_count} vague phrases. "
                "Your resume relies heavily on passive responsibility statements rather than "
                "specific achievements."
            )
            # List found phrases
            unique_phrases = list(set(found_phrases))
            feedback_parts.append("\n\nVague phrases to replace:")
            for phrase in unique_phrases[:8]:  # Show up to 8 examples
                feedback_parts.append(f"\n  - \"{phrase}\"")

        # Improvement suggestions (for non-excellent scores)
        if score < 5:
            feedback_parts.append("\n\nImprovement strategies:")

            suggestions = []

            if any(phrase in found_phrases for phrase in ['responsible for', 'duties included', 'tasked with']):
                suggestions.append(
                    "Replace responsibility statements with achievement statements. "
                    "Instead of 'Responsible for API development', use 'Developed RESTful API serving 100K requests/day'."
                )

            if any(phrase in found_phrases for phrase in ['worked on', 'helped with', 'assisted with']):
                suggestions.append(
                    "Replace weak verbs with strong action verbs. "
                    "Instead of 'Worked on performance optimization', use 'Optimized query performance, reducing latency by 60%'."
                )

            if any(phrase in found_phrases for phrase in ['involved in', 'participated in', 'contributed to']):
                suggestions.append(
                    "Show ownership and leadership. "
                    "Instead of 'Participated in code reviews', use 'Led code review process, establishing standards adopted by 15-person team'."
                )

            if any(phrase in found_phrases for phrase in ['exposure to', 'familiar with', 'knowledge of']):
                suggestions.append(
                    "Demonstrate application, not just awareness. "
                    "Instead of 'Exposure to Docker', use 'Containerized 12 microservices using Docker, reducing deployment time by 70%'."
                )

            # Add suggestions to feedback
            for i, suggestion in enumerate(suggestions[:3], 1):  # Show up to 3 suggestions
                feedback_parts.append(f"\n{i}. {suggestion}")

            # Generic tip if no specific matches
            if not suggestions:
                feedback_parts.append(
                    "\n1. Replace vague phrases with specific action verbs (developed, implemented, led, optimized)"
                    "\n2. Add quantifiable results (%, $, time saved, scale)"
                    "\n3. Show ownership and impact, not just participation"
                )

        return "".join(feedback_parts)


# Convenience function for direct usage
def score_achievement_depth(bullets: List[str]) -> Dict[str, Any]:
    """
    Score achievement depth based on vague phrase detection.

    Args:
        bullets: List of resume bullet points

    Returns:
        Scoring result dictionary

    Example:
        >>> bullets = [
        ...     "Developed high-performance API serving 1M requests/day",
        ...     "Responsible for code reviews",  # VAGUE
        ...     "Implemented CI/CD pipeline reducing deploy time by 80%"
        ... ]
        >>> result = score_achievement_depth(bullets)
        >>> print(f"Score: {result['score']}/5 ({result['penalty_tier']})")
    """
    scorer = AchievementDepthScorer()
    return scorer.score(bullets)
