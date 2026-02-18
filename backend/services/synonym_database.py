"""
Synonym database for intelligent keyword matching.

This module provides a comprehensive mapping of related terms to enable
better keyword matching in ATS resume scoring. It supports both direct
lookup (main keyword -> synonyms) and reverse lookup (synonym -> main keyword).
"""

import json
from pathlib import Path
from typing import Dict, List, Set


def _load_synonym_database() -> Dict[str, List[str]]:
    """Load synonym database from JSON file."""
    json_path = Path(__file__).parent.parent / "data" / "synonyms" / "skill_synonyms.json"

    if not json_path.exists():
        raise FileNotFoundError(
            f"Synonym database not found at {json_path}. "
            "Run backend/scripts/build_synonym_database.py to generate it."
        )

    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)


# Load synonym database from JSON file
SYNONYM_DATABASE = _load_synonym_database()


def get_all_synonyms(keyword: str) -> List[str]:
    """
    Get all synonyms for a given keyword.

    Supports both direct lookup (main keyword -> synonyms) and
    reverse lookup (synonym -> main keyword).

    Args:
        keyword: The keyword to look up (case-insensitive)

    Returns:
        List of all synonyms including the keyword itself

    Examples:
        >>> get_all_synonyms("python")
        ['python', 'py', 'python3', 'python2', 'cpython']

        >>> get_all_synonyms("k8s")  # Reverse lookup
        ['k8s', 'kubernetes', 'kube']
    """
    keyword_lower = keyword.lower().strip()
    result_set: Set[str] = {keyword_lower}

    # Direct lookup: keyword is a main entry
    if keyword_lower in SYNONYM_DATABASE:
        result_set.update(SYNONYM_DATABASE[keyword_lower])

    # Reverse lookup: keyword is a synonym
    for main_keyword, synonyms in SYNONYM_DATABASE.items():
        if keyword_lower in synonyms:
            result_set.add(main_keyword)
            result_set.update(synonyms)
            break  # Found it, no need to continue

    return sorted(list(result_set))


def expand_keywords(keywords: List[str]) -> List[str]:
    """
    Expand a list of keywords to include all their synonyms.

    Args:
        keywords: List of keywords to expand

    Returns:
        Deduplicated list of all keywords and their synonyms

    Examples:
        >>> expand_keywords(["python", "aws"])
        ['amazon aws', 'amazon web services', 'aws', 'cpython', 'py',
         'python', 'python2', 'python3']
    """
    expanded_set: Set[str] = set()

    for keyword in keywords:
        synonyms = get_all_synonyms(keyword)
        expanded_set.update(synonyms)

    return sorted(list(expanded_set))
