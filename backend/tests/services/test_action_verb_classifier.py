import pytest
from backend.services.action_verb_classifier import ActionVerbClassifier, VerbTier

def test_verb_tier_enum_points():
    """Test that VerbTier enum has correct point values."""
    assert VerbTier.TIER_4.points == 4
    assert VerbTier.TIER_3.points == 3
    assert VerbTier.TIER_2.points == 2
    assert VerbTier.TIER_1.points == 1
    assert VerbTier.TIER_0.points == 0

def test_classify_transformational_verb():
    """Test classification of Tier 4 transformational verbs."""
    classifier = ActionVerbClassifier()
    assert classifier.classify_bullet("Pioneered new ML architecture") == VerbTier.TIER_4
    assert classifier.classify_bullet("Revolutionized deployment process") == VerbTier.TIER_4

def test_classify_leadership_verb():
    """Test classification of Tier 3 leadership verbs."""
    classifier = ActionVerbClassifier()
    assert classifier.classify_bullet("Led team of 5 engineers") == VerbTier.TIER_3
    assert classifier.classify_bullet("Launched new product feature") == VerbTier.TIER_3

def test_classify_execution_verb():
    """Test classification of Tier 2 execution verbs."""
    classifier = ActionVerbClassifier()
    assert classifier.classify_bullet("Developed REST API") == VerbTier.TIER_2
    assert classifier.classify_bullet("Implemented authentication system") == VerbTier.TIER_2

def test_classify_support_verb():
    """Test classification of Tier 1 support verbs."""
    classifier = ActionVerbClassifier()
    assert classifier.classify_bullet("Managed project timeline") == VerbTier.TIER_1
    assert classifier.classify_bullet("Coordinated with stakeholders") == VerbTier.TIER_1

def test_classify_weak_verb():
    """Test classification of Tier 0 weak verbs."""
    classifier = ActionVerbClassifier()
    assert classifier.classify_bullet("Responsible for testing") == VerbTier.TIER_0
    assert classifier.classify_bullet("Worked on backend features") == VerbTier.TIER_0

def test_classify_no_verb():
    """Test classification when no action verb present."""
    classifier = ActionVerbClassifier()
    assert classifier.classify_bullet("Some random text") == VerbTier.TIER_0
