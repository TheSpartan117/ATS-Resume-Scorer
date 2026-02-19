"""
Utility functions for scoring operations.
"""


def normalize_scoring_mode(mode: str, job_description: str = "") -> str:
    """
    Normalize scoring mode to standard values.

    Args:
        mode: The input mode string (e.g., "ats", "quality", "auto", etc.)
        job_description: Optional job description text for auto-detection

    Returns:
        Normalized mode string: "ats_simulation" or "quality_coach"

    Examples:
        >>> normalize_scoring_mode("ats")
        'ats_simulation'
        >>> normalize_scoring_mode("quality")
        'quality_coach'
        >>> normalize_scoring_mode("auto", "Python developer needed")
        'ats_simulation'
        >>> normalize_scoring_mode("auto", "")
        'quality_coach'
    """
    # Default to auto if no mode specified
    mode = mode or "auto"

    # Normalize legacy mode names
    if mode == "ats":
        mode = "ats_simulation"
    elif mode == "quality":
        mode = "quality_coach"

    # Auto-detect mode based on job description
    if mode == "auto":
        mode = "ats_simulation" if job_description else "quality_coach"

    return mode
