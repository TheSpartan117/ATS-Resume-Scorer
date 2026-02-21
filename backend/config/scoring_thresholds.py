"""
Level-Aware Scoring Thresholds

Centralized configuration for all experience-level-specific thresholds.
Research-based values from Workday, Greenhouse, LinkedIn standards.

Experience Levels:
- Beginner (0-3 years): Entry-level expectations
- Intermediary (3-7 years): Mid-career expectations
- Senior (7+ years): Leadership/expert expectations

Usage:
    from backend.config.scoring_thresholds import get_thresholds_for_level

    thresholds = get_thresholds_for_level('intermediary')
    min_verb_coverage = thresholds['action_verb_coverage_min']
"""

from typing import Dict, Any


# ============================================================================
# BEGINNER THRESHOLDS (0-3 years)
# ============================================================================

BEGINNER_THRESHOLDS = {
    # Page Count
    'page_count': 1,
    'page_count_penalty_per_extra': -2,

    # Word Count (optimal range)
    'word_count_optimal_range': (400, 600),
    'word_count_acceptable_range': (300, 750),

    # Keywords (Required)
    'required_keywords_threshold': 60,  # 60% match = pass (Workday standard)
    'required_keywords_excellent': 80,

    # Keywords (Preferred)
    'preferred_keywords_threshold': 50,
    'preferred_keywords_excellent': 70,

    # Action Verbs
    'action_verb_coverage_min': 70,  # 70% of bullets have action verbs
    'action_verb_tier_avg_min': 1.5,  # Average tier 1.5+ (mix of Tier 1-2)

    # Quantification
    'quantification_rate_min': 30,  # 30% of bullets quantified
    'quantification_weighted_threshold': 25,  # Weighted rate

    # Experience Depth
    'vague_phrases_max_acceptable': 2,  # 0-2 vague phrases acceptable

    # Section Balance
    'experience_section_min': 40,  # 40% minimum
    'skills_section_max': 25,      # 25% maximum
    'summary_section_max': 15,     # 15% maximum

    # Years Experience
    'years_range': (0, 3),
    'years_optimal': 2
}


# ============================================================================
# INTERMEDIARY THRESHOLDS (3-7 years)
# ============================================================================

INTERMEDIARY_THRESHOLDS = {
    # Page Count
    'page_count': [1, 2],  # 1-2 pages acceptable
    'page_count_penalty_per_extra': -2,

    # Word Count
    'word_count_optimal_range': (600, 900),
    'word_count_acceptable_range': (500, 1050),

    # Keywords (Required)
    'required_keywords_threshold': 60,
    'required_keywords_excellent': 85,

    # Keywords (Preferred)
    'preferred_keywords_threshold': 50,
    'preferred_keywords_excellent': 75,

    # Action Verbs
    'action_verb_coverage_min': 80,  # 80% coverage
    'action_verb_tier_avg_min': 2.0,  # Average tier 2.0+ (solid Tier 2)

    # Quantification
    'quantification_rate_min': 50,  # 50% quantified
    'quantification_weighted_threshold': 40,

    # Experience Depth
    'vague_phrases_max_acceptable': 1,  # 0-1 vague phrases

    # Section Balance
    'experience_section_min': 50,  # 50% minimum
    'skills_section_max': 20,      # 20% maximum
    'summary_section_max': 10,     # 10% maximum

    # Years Experience
    'years_range': (3, 7),
    'years_optimal': 5
}


# ============================================================================
# SENIOR THRESHOLDS (7+ years)
# ============================================================================

SENIOR_THRESHOLDS = {
    # Page Count
    'page_count': 2,
    'page_count_penalty_per_extra': -2,

    # Word Count
    'word_count_optimal_range': (800, 1200),
    'word_count_acceptable_range': (700, 1350),

    # Keywords (Required)
    'required_keywords_threshold': 60,
    'required_keywords_excellent': 90,

    # Keywords (Preferred)
    'preferred_keywords_threshold': 50,
    'preferred_keywords_excellent': 80,

    # Action Verbs
    'action_verb_coverage_min': 90,  # 90% coverage
    'action_verb_tier_avg_min': 2.5,  # Average tier 2.5+ (mix of Tier 2-3)

    # Quantification
    'quantification_rate_min': 60,  # 60% quantified
    'quantification_weighted_threshold': 50,

    # Experience Depth
    'vague_phrases_max_acceptable': 0,  # 0 vague phrases (strict)

    # Section Balance
    'experience_section_min': 60,  # 60% minimum (leadership focus)
    'skills_section_max': 15,      # 15% maximum
    'summary_section_max': 10,     # 10% maximum

    # Years Experience
    'years_range': (7, 100),
    'years_optimal': 10
}


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_thresholds_for_level(level: str) -> Dict[str, Any]:
    """
    Get thresholds for a specific experience level.

    Args:
        level: Experience level ('beginner', 'intermediary', or 'senior')
               Case-insensitive.

    Returns:
        Dictionary of thresholds for that level
        Defaults to INTERMEDIARY if level is invalid

    Example:
        >>> thresholds = get_thresholds_for_level('senior')
        >>> thresholds['action_verb_coverage_min']
        90
    """
    level_lower = str(level).lower().strip()

    threshold_map = {
        'beginner': BEGINNER_THRESHOLDS,
        'intermediary': INTERMEDIARY_THRESHOLDS,
        'senior': SENIOR_THRESHOLDS
    }

    return threshold_map.get(level_lower, INTERMEDIARY_THRESHOLDS)


def get_all_thresholds() -> Dict[str, Dict[str, Any]]:
    """Get all threshold configurations."""
    return {
        'beginner': BEGINNER_THRESHOLDS,
        'intermediary': INTERMEDIARY_THRESHOLDS,
        'senior': SENIOR_THRESHOLDS
    }


def validate_thresholds() -> Dict[str, list]:
    """
    Validate all threshold configurations.

    Returns:
        Dictionary with 'errors' and 'warnings' lists
    """
    errors = []
    warnings = []

    for level_name, thresholds in get_all_thresholds().items():
        # Check required keys
        required_keys = [
            'page_count', 'action_verb_coverage_min', 'action_verb_tier_avg_min',
            'quantification_rate_min', 'required_keywords_threshold'
        ]

        for key in required_keys:
            if key not in thresholds:
                errors.append(f"{level_name}: Missing required key '{key}'")

        # Check value ranges
        if 'required_keywords_threshold' in thresholds:
            if not (0 <= thresholds['required_keywords_threshold'] <= 100):
                errors.append(f"{level_name}: required_keywords_threshold must be 0-100")

        if 'action_verb_tier_avg_min' in thresholds:
            if not (0 <= thresholds['action_verb_tier_avg_min'] <= 4):
                errors.append(f"{level_name}: action_verb_tier_avg_min must be 0-4")

    return {'errors': errors, 'warnings': warnings}
