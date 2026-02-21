"""
Pytest configuration and fixtures for ATS Resume Scorer tests.
"""

import pytest
from backend.services.semantic_matcher import get_semantic_matcher


def is_semantic_model_available():
    """Check if semantic transformer model is available."""
    try:
        matcher = get_semantic_matcher()
        matcher._lazy_init()
        return matcher._model is not None
    except Exception:
        return False


# Create pytest marker for tests requiring semantic matching
requires_semantic_model = pytest.mark.skipif(
    not is_semantic_model_available(),
    reason="Semantic transformer model not available (offline mode or network error)"
)


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers", 
        "requires_semantic: mark test as requiring semantic transformer model to be available"
    )
