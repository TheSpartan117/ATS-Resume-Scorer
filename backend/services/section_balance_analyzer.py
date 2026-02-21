"""
Section Balance Analyzer

Detects disproportionate resume sections indicating:
- Keyword stuffing (Skills section >25%)
- Insufficient detail (Experience section <40%)
- Verbosity (Summary section >15%)

Research basis:
- ResumeWorded analysis: Top resumes have 50-60% experience, <25% skills
- ATS systems flag keyword stuffing when skills section dominates
- Career coaches recommend 10-15% max for summary/objective

Penalty structure:
- Skills >25%: -2 pts (keyword stuffing)
- Experience <40%: -2 pts (insufficient detail)
- Summary >15%: -1 pt (too verbose)
- Maximum penalty: -5 pts total
"""

from typing import Dict, List


class SectionBalanceAnalyzer:
    """
    Analyze resume section balance to detect imbalances.

    Thresholds:
    - Experience: Should be 40-60% of resume
    - Skills: Should be <25% of resume
    - Summary: Should be <15% of resume
    """

    # Section balance thresholds
    THRESHOLDS = {
        'experience': {
            'min': 40,  # Below 40% = insufficient detail
            'max': 100,
            'penalty_below': -2
        },
        'skills': {
            'min': 0,
            'max': 25,  # Above 25% = keyword stuffing
            'penalty_above': -2
        },
        'summary': {
            'min': 0,
            'max': 15,  # Above 15% = too verbose
            'penalty_above': -1
        }
    }

    MAX_PENALTY = -5

    def __init__(self):
        """Initialize analyzer with default thresholds."""
        pass

    def _get_section_percentage(self, sections: Dict, section_name: str) -> float:
        """
        Calculate what percentage of resume a section represents.

        Args:
            sections: Dict of section_name -> {'content': str, 'word_count': int}
            section_name: Name of section to calculate percentage for

        Returns:
            Percentage (0-100)
        """
        if section_name not in sections:
            return 0.0

        total_words = sum(sec.get('word_count', 0) for sec in sections.values())

        if total_words == 0:
            return 0.0

        section_words = sections[section_name].get('word_count', 0)

        return (section_words / total_words) * 100

    def _check_section(self, section_name: str, percentage: float) -> Dict:
        """
        Check if a section violates balance thresholds.

        Args:
            section_name: Name of section
            percentage: Percentage of resume this section represents

        Returns:
            {
                'section': str,
                'percentage': float,
                'issue': str (description),
                'penalty': int
            } or None if no issue
        """
        if section_name not in self.THRESHOLDS:
            return None

        threshold = self.THRESHOLDS[section_name]

        # Check if below minimum
        if 'min' in threshold and 'penalty_below' in threshold:
            if percentage < threshold['min']:
                return {
                    'section': section_name,
                    'percentage': percentage,
                    'issue': f"{section_name.capitalize()} section too small ({percentage:.1f}% < {threshold['min']}%)",
                    'penalty': threshold['penalty_below']
                }

        # Check if above maximum
        if 'max' in threshold and 'penalty_above' in threshold:
            if percentage > threshold['max']:
                return {
                    'section': section_name,
                    'percentage': percentage,
                    'issue': f"{section_name.capitalize()} section too large ({percentage:.1f}% > {threshold['max']}%)",
                    'penalty': threshold['penalty_above']
                }

        return None

    def analyze(self, sections: Dict) -> Dict:
        """
        Analyze section balance and return penalty assessment.

        Args:
            sections: Dict of section_name -> {'content': str, 'word_count': int}

        Returns:
            {
                'penalty_score': int (0 to -5),
                'issues': List[Dict] (details of imbalances),
                'section_percentages': Dict[str, float],
                'total_words': int,
                'max_penalty': int (-5)
            }
        """
        if not sections:
            return {
                'penalty_score': 0,
                'issues': [],
                'section_percentages': {},
                'total_words': 0,
                'max_penalty': self.MAX_PENALTY
            }

        # Calculate percentages for all sections
        section_percentages = {}
        for section_name in sections.keys():
            section_percentages[section_name] = self._get_section_percentage(sections, section_name)

        # Check each section against thresholds
        issues = []
        total_penalty = 0

        for section_name, percentage in section_percentages.items():
            issue = self._check_section(section_name, percentage)
            if issue:
                issues.append(issue)
                total_penalty += issue['penalty']

        # Apply penalty cap
        penalty_score = max(total_penalty, self.MAX_PENALTY)

        total_words = sum(sec.get('word_count', 0) for sec in sections.values())

        return {
            'penalty_score': penalty_score,
            'issues': issues,
            'section_percentages': section_percentages,
            'total_words': total_words,
            'max_penalty': self.MAX_PENALTY
        }


# Singleton instance
_analyzer_instance = None

def get_section_balance_analyzer() -> SectionBalanceAnalyzer:
    """Get singleton instance of SectionBalanceAnalyzer."""
    global _analyzer_instance
    if _analyzer_instance is None:
        _analyzer_instance = SectionBalanceAnalyzer()
    return _analyzer_instance
