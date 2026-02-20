"""Configuration and feature flags for ATS scorer"""
import os


def str_to_bool(value: str) -> bool:
    """Convert string to boolean"""
    return value.lower() in ('true', '1', 'yes', 'on')


# Corpus Integration Feature Flags
ENABLE_CORPUS_KEYWORDS = str_to_bool(os.getenv('ENABLE_CORPUS_KEYWORDS', 'false'))
ENABLE_CORPUS_SYNONYMS = str_to_bool(os.getenv('ENABLE_CORPUS_SYNONYMS', 'false'))
ENABLE_ROLE_MAPPINGS = str_to_bool(os.getenv('ENABLE_ROLE_MAPPINGS', 'false'))
ENABLE_ML_SUGGESTIONS = str_to_bool(os.getenv('ENABLE_ML_SUGGESTIONS', 'false'))
