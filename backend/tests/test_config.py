"""Test configuration and feature flags"""
import os
import pytest


def test_corpus_feature_flags_default_to_false():
    """Feature flags should default to false"""
    # Clear environment FIRST
    for key in ['ENABLE_CORPUS_KEYWORDS', 'ENABLE_CORPUS_SYNONYMS',
                'ENABLE_ROLE_MAPPINGS', 'ENABLE_ML_SUGGESTIONS']:
        os.environ.pop(key, None)

    # Import AFTER clearing environment
    import importlib
    import backend.config as config
    importlib.reload(config)

    # Now test actual defaults
    assert config.ENABLE_CORPUS_KEYWORDS is False
    assert config.ENABLE_CORPUS_SYNONYMS is False
    assert config.ENABLE_ROLE_MAPPINGS is False
    assert config.ENABLE_ML_SUGGESTIONS is False


def test_corpus_feature_flags_can_be_enabled():
    """Feature flags should respond to environment variables"""
    # Clear environment FIRST
    for key in ['ENABLE_CORPUS_KEYWORDS', 'ENABLE_CORPUS_SYNONYMS',
                'ENABLE_ROLE_MAPPINGS', 'ENABLE_ML_SUGGESTIONS']:
        os.environ.pop(key, None)

    # Set test environment variable
    os.environ['ENABLE_CORPUS_KEYWORDS'] = 'true'

    # Reload config
    import importlib
    import backend.config as config
    importlib.reload(config)

    assert config.ENABLE_CORPUS_KEYWORDS is True

    # Cleanup
    os.environ.pop('ENABLE_CORPUS_KEYWORDS')
