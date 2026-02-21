"""
Section Balance Analyzer

Detects keyword stuffing and poor section balance by analyzing resume section proportions.

Research basis:
- Greenhouse ATS: Skills sections >25% flagged as keyword stuffing
- ResumeWorded: Ideal resume is 50-60% experience, <25% skills, <15% summary
- Career coaches: Experience should dominate (40%+ minimum)

Penalty structure:
- Skills section >25%: -2 points (keyword stuffing indicator)
- Experience section <40%: -2 points (insufficient detail)
- Summary section >15%: -1 point (too verbose)
- Maximum cumulative penalty: -5 points
"""

from typing import Dict, List


class SectionBalanceAnalyzer:
    """
    Analyze resume section balance to detect keyword stuffing and poor structure.

    Ideal proportions:
    - Experience: 50-60% (minimum 40%)
    - Skills: 15-20% (maximum 25%)
    - Education: 10-15%
    - Summary: 5-10% (maximum 15%)
    """

    # Thresholds for penalties
    THRESHOLDS = {
        'experience': {
            'min': 40.0,  # Below this: -2 points
            'ideal_min': 50.0,
            'ideal_max': 60.0,
            'penalty': -2
        },
        'skills': {
            'max': 25.0,  # Above this: -2 points
            'ideal_max': 20.0,
            'penalty': -2
        },
        'summary': {
            'max': 15.0,  # Above this: -1 point
            'ideal_max': 10.0,
            'penalty': -1
        }
    }

    MAX_PENALTY = -5

    def __init__(self):
        """Initialize analyzer with thresholds."""
        pass

    def _calculate_percentages(self, sections: Dict[str, int]) -> Dict[str, float]:
        """
        Calculate percentage of total for each section.

        Args:
            sections: Dict mapping section name to word/character count

        Returns:
            Dict mapping section name to percentage (0-100)
        """
        total = sum(sections.values())

        if total == 0:
            return {section: 0.0 for section in sections}

        percentages = {}
        for section, count in sections.items():
            percentages[section] = (count / total) * 100.0

        return percentages

    def _check_violations(self, percentages: Dict[str, float]) -> List[Dict]:
        """
        Check for section balance violations.

        Args:
            percentages: Section percentages

        Returns:
            List of violation dictionaries
        """
        violations = []

        # Check experience section (too small)
        if 'experience' in percentages:
            exp_pct = percentages['experience']
            exp_threshold = self.THRESHOLDS['experience']

            if exp_pct < exp_threshold['min']:
                violations.append({
                    'section': 'experience',
                    'actual_percentage': exp_pct,
                    'threshold': f">={exp_threshold['min']}%",
                    'penalty': exp_threshold['penalty'],
                    'message': f"Experience section is {exp_pct:.1f}% (should be >={exp_threshold['min']}%)"
                })

        # Check skills section (too large - keyword stuffing indicator)
        if 'skills' in percentages:
            skills_pct = percentages['skills']
            skills_threshold = self.THRESHOLDS['skills']

            if skills_pct > skills_threshold['max']:
                violations.append({
                    'section': 'skills',
                    'actual_percentage': skills_pct,
                    'threshold': f"<={skills_threshold['max']}%",
                    'penalty': skills_threshold['penalty'],
                    'message': f"Skills section is {skills_pct:.1f}% (should be <={skills_threshold['max']}%) - possible keyword stuffing"
                })

        # Check summary section (too large - too verbose)
        if 'summary' in percentages:
            summary_pct = percentages['summary']
            summary_threshold = self.THRESHOLDS['summary']

            if summary_pct > summary_threshold['max']:
                violations.append({
                    'section': 'summary',
                    'actual_percentage': summary_pct,
                    'threshold': f"<={summary_threshold['max']}%",
                    'penalty': summary_threshold['penalty'],
                    'message': f"Summary section is {summary_pct:.1f}% (should be <={summary_threshold['max']}%) - too verbose"
                })

        return violations

    def analyze(self, sections: Dict[str, int]) -> Dict:
        """
        Analyze section balance and calculate penalties.

        Args:
            sections: Dict mapping section name to word/character count
                     e.g., {'experience': 500, 'skills': 200, 'education': 150, 'summary': 150}

        Returns:
            {
                'section_percentages': Dict[str, float],
                'violations': List[Dict],
                'penalty_score': int (0 to -5),
                'is_balanced': bool,
                'max_penalty': int (-5)
            }
        """
        if not sections:
            return {
                'section_percentages': {},
                'violations': [],
                'penalty_score': 0,
                'is_balanced': True,
                'max_penalty': self.MAX_PENALTY
            }

        # Calculate percentages
        percentages = self._calculate_percentages(sections)

        # Check for violations
        violations = self._check_violations(percentages)

        # Calculate total penalty (with cap)
        total_penalty = sum(v['penalty'] for v in violations)
        penalty_score = max(total_penalty, self.MAX_PENALTY)

        # Determine if balanced
        is_balanced = len(violations) == 0

        return {
            'section_percentages': percentages,
            'violations': violations,
            'penalty_score': penalty_score,
            'is_balanced': is_balanced,
            'max_penalty': self.MAX_PENALTY
        }

    def get_ideal_balance(self) -> Dict[str, str]:
        """Get ideal section balance guidelines."""
        return {
            'experience': '50-60% (minimum 40%)',
            'skills': '15-20% (maximum 25%)',
            'education': '10-15%',
            'summary': '5-10% (maximum 15%)'
        }


# Singleton instance
_analyzer_instance = None

def get_section_balance_analyzer() -> SectionBalanceAnalyzer:
    """Get singleton instance of SectionBalanceAnalyzer."""
    global _analyzer_instance
    if _analyzer_instance is None:
        _analyzer_instance = SectionBalanceAnalyzer()
    return _analyzer_instance
