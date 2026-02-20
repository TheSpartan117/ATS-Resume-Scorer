"""
Context-Aware Scorer - Applies experience level and section-specific adjustments.

This module provides:
- Experience level multipliers
- Section-specific scoring rules
- Contextual score adjustments
"""

import re
from typing import Dict, List


class ContextAwareScorer:
    """
    Applies contextual adjustments to quality scores based on experience level and section type.

    Components:
    - Experience level multipliers (entry: 0.6x, mid: 0.8x, senior: 1.0x, lead: 1.1x, exec: 1.2x)
    - Section-specific scoring rules
    - Adaptive quality expectations
    """

    # Experience level multipliers for different metrics
    LEVEL_MULTIPLIERS = {
        'entry': {
            'gap_penalty': 0.6,        # More lenient on gaps
            'achievement_bonus': 0.7,  # Lower achievement expectations
            'specificity_req': 0.7,    # Less specific language required
            'strategic_bonus': 0.5,    # Tactical focus expected
        },
        'mid': {
            'gap_penalty': 0.8,
            'achievement_bonus': 0.9,
            'specificity_req': 0.9,
            'strategic_bonus': 0.7,
        },
        'senior': {
            'gap_penalty': 1.0,        # Standard expectations
            'achievement_bonus': 1.0,
            'specificity_req': 1.0,
            'strategic_bonus': 0.9,
        },
        'lead': {
            'gap_penalty': 1.1,        # Stricter on gaps
            'achievement_bonus': 1.1,  # Higher achievement bar
            'specificity_req': 1.1,
            'strategic_bonus': 1.1,
        },
        'executive': {
            'gap_penalty': 1.2,
            'achievement_bonus': 1.2,
            'specificity_req': 1.0,    # Can be less specific, more strategic
            'strategic_bonus': 1.2,
        }
    }

    def apply_level_multiplier(self, base_score: float, level: str, metric: str) -> float:
        """
        Apply experience level multiplier to a score.

        Args:
            base_score: The base score to adjust
            level: Experience level (entry, mid, senior, lead, executive)
            metric: The metric type (gap_penalty, achievement_bonus, etc.)

        Returns:
            Adjusted score with multiplier applied
        """
        # Normalize level
        level = level.lower()
        if level not in self.LEVEL_MULTIPLIERS:
            level = 'mid'  # Default to mid-level

        multiplier = self.LEVEL_MULTIPLIERS[level].get(metric, 1.0)
        return base_score * multiplier

    def score_section_content(self, content: str, section: str, level: str) -> Dict:
        """
        Score content with section-specific rules.

        Args:
            content: The text content to analyze
            section: Section type (summary, experience, education)
            level: Experience level

        Returns:
            Dictionary with score and section-specific metrics
        """
        section = section.lower()

        if section == "summary":
            return self._score_summary_section(content, level)
        elif section == "experience":
            return self._score_experience_section(content, level)
        elif section == "education":
            return self._score_education_section(content, level)
        else:
            return {'score': 0, 'details': 'Unknown section'}

    def _score_summary_section(self, content: str, level: str) -> Dict:
        """Score summary/profile section with specific requirements."""
        score = 0
        details = {}

        # Check for years of experience
        has_years = bool(re.search(r'\d+\+?\s*years?', content, re.IGNORECASE))
        details['has_years_experience'] = has_years
        if has_years:
            score += 3

        # Check for quantified impact
        has_metrics = bool(re.search(r'\$?\d+[MKB%]|\d+\+', content))
        details['has_quantified_impact'] = has_metrics
        if has_metrics:
            score += 3

        # Check for role clarity
        role_keywords = ['manager', 'engineer', 'designer', 'analyst', 'specialist', 'director', 'lead']
        has_role = any(keyword in content.lower() for keyword in role_keywords)
        details['has_role_clarity'] = has_role
        if has_role:
            score += 2

        # Check for specialization/expertise
        expertise_keywords = ['expert', 'specialist', 'focused on', 'specialized in', 'skilled in']
        has_expertise = any(keyword in content.lower() for keyword in expertise_keywords)
        details['has_expertise_statement'] = has_expertise
        if has_expertise:
            score += 2

        return {
            'score': score,
            'max_score': 10,
            **details
        }

    def _score_experience_section(self, content: str, level: str) -> Dict:
        """Score experience section focusing on achievements."""
        score = 0
        details = {}

        # Count achievement indicators (CAR pattern elements)
        achievement_verbs = ['led', 'launched', 'delivered', 'achieved', 'increased', 'reduced', 'improved', 'built', 'designed', 'architected']
        achievement_count = sum(1 for verb in achievement_verbs if verb in content.lower())
        details['achievement_count'] = achievement_count

        # More achievements expected at higher levels
        expected_count = {'entry': 2, 'mid': 3, 'senior': 4, 'lead': 5, 'executive': 5}.get(level, 3)
        achievement_ratio = min(achievement_count / expected_count, 1.0)
        score += achievement_ratio * 5

        # Check for quantifiable results
        metrics_found = len(re.findall(r'\d+%|\$\d+[MKB]?|\d+x', content))
        details['metrics_found'] = metrics_found
        score += min(metrics_found, 3)  # Max 3 points

        # Check for team leadership (important for senior+)
        has_leadership = bool(re.search(r'led\s+team|managed\s+\d+|team\s+of\s+\d+', content, re.IGNORECASE))
        details['has_leadership'] = has_leadership
        if has_leadership and level in ['senior', 'lead', 'executive']:
            score += 2

        return {
            'score': score,
            'max_score': 10,
            **details
        }

    def _score_education_section(self, content: str, level: str) -> Dict:
        """Score education section checking relevance."""
        score = 5  # Baseline for having education
        details = {}

        # Check for degree level
        degree_patterns = {
            'phd': 3,
            'doctorate': 3,
            'master': 2,
            'mba': 2,
            'bachelor': 1,
            'b.s.': 1,
            'b.a.': 1,
        }

        content_lower = content.lower()
        for degree, points in degree_patterns.items():
            if degree in content_lower:
                score += points
                details['degree_level'] = degree
                break

        # Check for GPA (if high)
        gpa_match = re.search(r'gpa[:\s]+([3-4]\.\d+)', content_lower)
        if gpa_match:
            gpa = float(gpa_match.group(1))
            if gpa >= 3.5:
                score += 1
                details['has_high_gpa'] = True

        return {
            'score': min(score, 10),
            'max_score': 10,
            **details
        }

    def adjust_quality_score(
        self,
        quality_scores: Dict,
        level: str,
        section: str = "experience"
    ) -> Dict:
        """
        Apply contextual adjustments to quality scores.

        Args:
            quality_scores: Dictionary with component scores
            level: Experience level
            section: Section being scored

        Returns:
            Adjusted scores with explanation of adjustments
        """
        adjusted_scores = {}
        adjustments_made = []

        # Adjust achievement strength based on level
        if 'achievement_strength' in quality_scores:
            base = quality_scores['achievement_strength']
            adjusted = self.apply_level_multiplier(base, level, 'achievement_bonus')
            adjusted_scores['achievement_strength'] = adjusted

            if adjusted != base:
                adjustments_made.append(f"Achievement expectations adjusted for {level} level")

        # Adjust specificity requirements
        if 'specificity' in quality_scores:
            base = quality_scores['specificity']
            adjusted = self.apply_level_multiplier(base, level, 'specificity_req')
            adjusted_scores['specificity'] = adjusted

            if adjusted != base:
                adjustments_made.append(f"Specificity requirements adjusted for {level} level")

        # Pass through other scores unchanged
        for key in ['sentence_clarity', 'grammar', 'format']:
            if key in quality_scores:
                adjusted_scores[key] = quality_scores[key]

        # Calculate total
        total_score = sum(adjusted_scores.values())

        return {
            'adjusted_scores': adjusted_scores,
            'total_score': total_score,
            'adjustments_applied': len(adjustments_made) > 0,
            'adjustments': adjustments_made
        }
