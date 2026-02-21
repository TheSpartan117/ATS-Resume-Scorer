"""
Parameter Registry - Central registry for all ATS scoring parameters

Provides singleton access to all 12 core scoring parameters (P1.1-P4.2)
with metadata, categories, and scorer class instances.

Total: 100 points across 4 categories:
- Keyword Matching (35pts): P1.1-P1.2
- Content Quality (30pts): P2.1-P2.3
- Format & Structure (20pts): P3.1-P3.4
- Professional Polish (15pts): P4.1-P4.2
"""

from typing import Dict, Optional, Any


class ParameterRegistry:
    """
    Singleton registry for all ATS scoring parameters.

    Provides centralized access to parameter metadata, scorer classes,
    and category organization.
    """

    _instance = None

    def __new__(cls):
        """Implement singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize_registry()
        return cls._instance

    def _initialize_registry(self):
        """Initialize the parameter registry with all scorers."""
        # Import all scorer classes
        from backend.services.parameters.p1_1_required_keywords import RequiredKeywordsMatcher
        from backend.services.parameters.p1_2_preferred_keywords import PreferredKeywordsMatcher
        from backend.services.parameters.p2_1_action_verbs import ActionVerbScorer
        from backend.services.parameters.p2_2_quantification import QuantificationScorer
        from backend.services.parameters.p2_3_achievement_depth import AchievementDepthScorer
        from backend.services.parameters.p3_1_page_count import PageCountScorer
        from backend.services.parameters.p3_2_word_count import WordCountScorer
        from backend.services.parameters.p3_3_section_balance import SectionBalanceScorer
        from backend.services.parameters.p3_4_ats_formatting import ATSFormattingScorer
        from backend.services.parameters.p4_1_grammar import GrammarScorer
        from backend.services.parameters.p4_2_professional_standards import ProfessionalStandardsScorer

        # Define all parameters with metadata
        self._parameters = {
            'P1.1': {
                'code': 'P1.1',
                'name': 'Required Keywords Match',
                'description': 'Matches required keywords using hybrid semantic+exact matching with tiered scoring',
                'category': 'Keyword Matching',
                'max_score': 25,
                'scorer_class': RequiredKeywordsMatcher
            },
            'P1.2': {
                'code': 'P1.2',
                'name': 'Preferred Keywords Match',
                'description': 'Matches preferred keywords with more lenient thresholds than required keywords',
                'category': 'Keyword Matching',
                'max_score': 10,
                'scorer_class': PreferredKeywordsMatcher
            },
            'P2.1': {
                'code': 'P2.1',
                'name': 'Action Verb Quality',
                'description': 'Evaluates bullet points using 5-tier action verb classification with coverage and quality metrics',
                'category': 'Content Quality',
                'max_score': 15,
                'scorer_class': ActionVerbScorer
            },
            'P2.2': {
                'code': 'P2.2',
                'name': 'Quantification Rate',
                'description': 'Assesses metric quality using weighted scoring (HIGH/MEDIUM/LOW)',
                'category': 'Content Quality',
                'max_score': 10,
                'scorer_class': QuantificationScorer
            },
            'P2.3': {
                'code': 'P2.3',
                'name': 'Achievement Depth',
                'description': 'Detects vague passive language to identify weak achievements',
                'category': 'Content Quality',
                'max_score': 5,
                'scorer_class': AchievementDepthScorer
            },
            'P3.1': {
                'code': 'P3.1',
                'name': 'Page Count',
                'description': 'Validates resume length against level-specific page standards',
                'category': 'Format & Structure',
                'max_score': 5,
                'scorer_class': PageCountScorer
            },
            'P3.2': {
                'code': 'P3.2',
                'name': 'Word Count',
                'description': 'Ensures word count falls within optimal ranges for experience level',
                'category': 'Format & Structure',
                'max_score': 3,
                'scorer_class': WordCountScorer
            },
            'P3.3': {
                'code': 'P3.3',
                'name': 'Section Balance',
                'description': 'Detects keyword stuffing and poor content distribution',
                'category': 'Format & Structure',
                'max_score': 5,
                'scorer_class': SectionBalanceScorer
            },
            'P3.4': {
                'code': 'P3.4',
                'name': 'ATS Formatting',
                'description': 'Validates ATS-compatible formatting (fonts, tables, headers)',
                'category': 'Format & Structure',
                'max_score': 7,
                'scorer_class': ATSFormattingScorer
            },
            'P4.1': {
                'code': 'P4.1',
                'name': 'Grammar & Spelling',
                'description': 'Checks grammar and spelling errors with tiered penalty system',
                'category': 'Professional Polish',
                'max_score': 10,
                'scorer_class': GrammarScorer
            },
            'P4.2': {
                'code': 'P4.2',
                'name': 'Professional Standards',
                'description': 'Validates professional tone and appropriate language',
                'category': 'Professional Polish',
                'max_score': 5,
                'scorer_class': ProfessionalStandardsScorer
            }
        }

    def get_all_scorers(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all registered parameters with full metadata.

        Returns:
            Dictionary mapping parameter codes to metadata dicts
        """
        return self._parameters.copy()

    def get_scorer(self, code: str) -> Optional[Dict[str, Any]]:
        """
        Get specific parameter by code.

        Args:
            code: Parameter code (e.g., 'P1.1')

        Returns:
            Parameter metadata dict or None if not found
        """
        return self._parameters.get(code)

    def get_max_score(self) -> int:
        """
        Get total maximum score across all parameters.

        Returns:
            Total max score (should be 100)
        """
        return sum(param['max_score'] for param in self._parameters.values())

    def get_scorers_by_category(self, category: str) -> Dict[str, Dict[str, Any]]:
        """
        Get all parameters in a specific category.

        Args:
            category: Category name (e.g., 'Keyword Matching')

        Returns:
            Dictionary of parameters in that category
        """
        return {
            code: param
            for code, param in self._parameters.items()
            if param['category'] == category
        }

    def get_max_score_by_category(self) -> Dict[str, int]:
        """
        Calculate maximum score per category.

        Returns:
            Dictionary mapping category names to total max scores
        """
        category_scores = {}

        for param in self._parameters.values():
            category = param['category']
            max_score = param['max_score']

            if category not in category_scores:
                category_scores[category] = 0

            category_scores[category] += max_score

        return category_scores


# Convenience function for global access
def get_parameter_registry() -> ParameterRegistry:
    """Get the singleton parameter registry instance."""
    return ParameterRegistry()
