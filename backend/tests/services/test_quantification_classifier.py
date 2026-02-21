import pytest
from backend.services.quantification_classifier import QuantificationClassifier, MetricQuality

@pytest.fixture
def classifier():
    return QuantificationClassifier()

def test_high_value_metrics(classifier):
    """High-value metrics: percentages, money, multipliers"""
    high_value_bullets = [
        "Increased revenue by 45%",
        "Reduced costs by $200K annually",
        "Improved performance 3x faster",
        "Boosted engagement from 2% to 15%"
    ]

    for bullet in high_value_bullets:
        quality = classifier.classify_bullet(bullet)
        assert quality == MetricQuality.HIGH
        assert quality.weight == 1.0

def test_medium_value_metrics(classifier):
    """Medium-value metrics: team sizes, durations, scale"""
    medium_value_bullets = [
        "Led team of 12 engineers",
        "Completed project in 6 months",
        "Serving 100K+ active users",
        "Managed 15 concurrent projects"
    ]

    for bullet in medium_value_bullets:
        quality = classifier.classify_bullet(bullet)
        assert quality == MetricQuality.MEDIUM
        assert quality.weight == 0.7

def test_low_value_metrics(classifier):
    """Low-value metrics: bare numbers without context"""
    low_value_bullets = [
        "Worked on 5 projects",
        "Fixed 20 bugs",
        "Attended 10 meetings"
    ]

    for bullet in low_value_bullets:
        quality = classifier.classify_bullet(bullet)
        assert quality == MetricQuality.LOW
        assert quality.weight == 0.3

def test_no_metrics(classifier):
    """No quantifiable metrics"""
    no_metric_bullets = [
        "Responsible for backend development",
        "Improved system performance",
        "Worked with stakeholders"
    ]

    for bullet in no_metric_bullets:
        quality = classifier.classify_bullet(bullet)
        assert quality is None

def test_classify_bullets_batch(classifier):
    """Test batch classification with statistics"""
    bullets = [
        "Increased revenue by 45%",           # HIGH (1.0)
        "Led team of 12 engineers",           # MEDIUM (0.7)
        "Worked on 5 projects",               # LOW (0.3)
        "Improved system performance"         # NONE (0.0)
    ]

    result = classifier.classify_bullets(bullets)

    assert result['total_bullets'] == 4
    assert result['quantified_count'] == 3
    assert result['high_count'] == 1
    assert result['medium_count'] == 1
    assert result['low_count'] == 1
    # Weighted: (1.0 + 0.7 + 0.3) / 4 * 100 = 50%
    assert abs(result['weighted_quantification_rate'] - 50.0) < 0.1
