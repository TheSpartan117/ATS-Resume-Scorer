"""
Confidence Scoring Service

Adds statistical confidence intervals to all scores, providing users with
transparency about score uncertainty and reliability.

Uses statistical methods to calculate confidence intervals based on:
- Sample size (number of data points)
- Score variability
- Measurement uncertainty
"""

import math
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class ConfidenceScore:
    """Represents a score with confidence interval"""
    score: float
    confidence_lower: float
    confidence_upper: float
    confidence_level: float  # e.g., 0.95 for 95% confidence
    margin_of_error: float
    confidence_text: str
    reliability_rating: str


class ConfidenceScorer:
    """
    Calculates confidence intervals for resume scores.

    Provides statistical confidence intervals to indicate
    the reliability and uncertainty of scoring results.
    """

    def __init__(self, confidence_level: float = 0.95):
        """
        Initialize confidence scorer.

        Args:
            confidence_level: Confidence level (default 0.95 for 95%)
        """
        self.confidence_level = confidence_level

        # Z-scores for common confidence levels
        self.z_scores = {
            0.90: 1.645,
            0.95: 1.960,
            0.99: 2.576
        }

        self.z_score = self.z_scores.get(confidence_level, 1.960)

    def calculate_with_confidence(
        self,
        score: float,
        sample_size: int = None,
        score_components: list = None,
        measurement_type: str = 'percentage'
    ) -> ConfidenceScore:
        """
        Calculate score with confidence interval.

        Args:
            score: The main score (0-100)
            sample_size: Number of data points used (e.g., number of keywords checked)
            score_components: List of component scores for variance calculation
            measurement_type: Type of measurement ('percentage', 'count', 'binary')

        Returns:
            ConfidenceScore object with confidence interval
        """
        # Determine sample size if not provided
        if sample_size is None:
            if score_components:
                sample_size = len(score_components)
            else:
                # Default reasonable sample size
                sample_size = 20

        # Ensure minimum sample size for statistical validity
        sample_size = max(sample_size, 5)

        # Calculate standard error based on measurement type
        if measurement_type == 'percentage':
            # For percentage scores (binomial proportion)
            standard_error = self._calculate_proportion_se(score, sample_size)
        elif measurement_type == 'binary':
            # For binary outcomes (pass/fail)
            standard_error = self._calculate_binary_se(score, sample_size)
        else:
            # For general continuous scores
            if score_components:
                standard_error = self._calculate_variance_se(score_components, sample_size)
            else:
                # Estimate based on score and sample size
                standard_error = self._estimate_se(score, sample_size)

        # Calculate margin of error
        margin_of_error = self.z_score * standard_error

        # Calculate confidence interval bounds
        confidence_lower = max(0, score - margin_of_error)
        confidence_upper = min(100, score + margin_of_error)

        # Generate confidence text
        confidence_text = self._generate_confidence_text(
            score, margin_of_error, confidence_lower, confidence_upper
        )

        # Determine reliability rating
        reliability_rating = self._get_reliability_rating(
            margin_of_error, sample_size
        )

        return ConfidenceScore(
            score=round(score, 1),
            confidence_lower=round(confidence_lower, 1),
            confidence_upper=round(confidence_upper, 1),
            confidence_level=self.confidence_level,
            margin_of_error=round(margin_of_error, 1),
            confidence_text=confidence_text,
            reliability_rating=reliability_rating
        )

    def _calculate_proportion_se(self, score: float, sample_size: int) -> float:
        """
        Calculate standard error for proportion (percentage scores).

        Uses binomial proportion standard error formula:
        SE = sqrt(p * (1 - p) / n)

        Args:
            score: Score as percentage (0-100)
            sample_size: Number of observations

        Returns:
            Standard error in percentage points
        """
        # Convert score to proportion (0-1)
        p = score / 100.0

        # Handle edge cases
        p = max(0.01, min(0.99, p))  # Avoid division issues at extremes

        # Calculate standard error
        se = math.sqrt((p * (1 - p)) / sample_size)

        # Convert back to percentage points
        return se * 100

    def _calculate_binary_se(self, score: float, sample_size: int) -> float:
        """
        Calculate standard error for binary outcomes.

        For pass/fail type scores where we're estimating probability.

        Args:
            score: Probability score (0-100)
            sample_size: Number of trials

        Returns:
            Standard error in percentage points
        """
        # Same as proportion SE for binary outcomes
        return self._calculate_proportion_se(score, sample_size)

    def _calculate_variance_se(self, scores: list, sample_size: int) -> float:
        """
        Calculate standard error from actual score variance.

        Uses sample standard deviation:
        SE = s / sqrt(n)

        Args:
            scores: List of component scores
            sample_size: Number of samples

        Returns:
            Standard error
        """
        if not scores or len(scores) < 2:
            return 5.0  # Default SE if insufficient data

        # Calculate mean
        mean = sum(scores) / len(scores)

        # Calculate sample variance
        variance = sum((x - mean) ** 2 for x in scores) / (len(scores) - 1)

        # Calculate standard deviation
        std_dev = math.sqrt(variance)

        # Calculate standard error
        se = std_dev / math.sqrt(sample_size)

        return se

    def _estimate_se(self, score: float, sample_size: int) -> float:
        """
        Estimate standard error when only score and sample size are known.

        Uses heuristic based on score position and sample size.

        Args:
            score: The score (0-100)
            sample_size: Number of observations

        Returns:
            Estimated standard error
        """
        # Scores near middle (50) have higher variance
        # Scores near extremes (0, 100) have lower variance
        distance_from_middle = abs(score - 50)
        variance_factor = 1 - (distance_from_middle / 50)

        # Base SE decreases with sample size
        base_se = 15 / math.sqrt(sample_size)

        # Adjust by variance factor
        estimated_se = base_se * (0.5 + variance_factor * 0.5)

        return estimated_se

    def _generate_confidence_text(
        self,
        score: float,
        margin: float,
        lower: float,
        upper: float
    ) -> str:
        """
        Generate human-readable confidence interval text.

        Args:
            score: Main score
            margin: Margin of error
            lower: Lower bound
            upper: Upper bound

        Returns:
            Formatted confidence text
        """
        confidence_pct = int(self.confidence_level * 100)

        # Format with appropriate precision
        if margin < 1:
            return f"{score:.1f} ± {margin:.1f} points ({confidence_pct}% confidence)"
        else:
            return f"{score:.0f} ± {margin:.0f} points ({confidence_pct}% confidence)"

    def _get_reliability_rating(self, margin_of_error: float, sample_size: int) -> str:
        """
        Determine reliability rating based on margin of error and sample size.

        Args:
            margin_of_error: Calculated margin of error
            sample_size: Number of observations

        Returns:
            Reliability rating string
        """
        # Consider both margin and sample size
        if margin_of_error <= 3 and sample_size >= 50:
            return "Very High"
        elif margin_of_error <= 5 and sample_size >= 30:
            return "High"
        elif margin_of_error <= 8 and sample_size >= 15:
            return "Moderate"
        elif margin_of_error <= 12:
            return "Fair"
        else:
            return "Low"

    def add_confidence_to_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add confidence intervals to a scoring result dictionary.

        Automatically detects score fields and adds confidence intervals.

        Args:
            result: Dictionary containing scores

        Returns:
            Updated dictionary with confidence intervals
        """
        # Fields that represent scores (0-100 scale)
        score_fields = [
            'overall_score', 'keyword_score', 'quality_score',
            'formatting_score', 'experience_score', 'ats_score'
        ]

        for field in score_fields:
            if field in result and isinstance(result[field], (int, float)):
                score = result[field]

                # Try to find associated metadata for better confidence calculation
                sample_size = result.get(f'{field}_sample_size', None)
                components = result.get(f'{field}_components', None)

                # Calculate confidence
                confidence = self.calculate_with_confidence(
                    score=score,
                    sample_size=sample_size,
                    score_components=components
                )

                # Add confidence data to result
                result[f'{field}_confidence'] = {
                    'score': confidence.score,
                    'lower': confidence.confidence_lower,
                    'upper': confidence.confidence_upper,
                    'margin': confidence.margin_of_error,
                    'text': confidence.confidence_text,
                    'reliability': confidence.reliability_rating
                }

        return result

    def calculate_keyword_confidence(
        self,
        match_rate: float,
        total_keywords: int,
        matched_keywords: int
    ) -> ConfidenceScore:
        """
        Calculate confidence for keyword matching scores.

        Args:
            match_rate: Percentage of keywords matched (0-100)
            total_keywords: Total number of keywords in job description
            matched_keywords: Number of keywords found in resume

        Returns:
            ConfidenceScore with confidence interval
        """
        return self.calculate_with_confidence(
            score=match_rate,
            sample_size=total_keywords,
            measurement_type='percentage'
        )

    def calculate_ats_pass_confidence(
        self,
        pass_probability: float,
        num_checks: int
    ) -> ConfidenceScore:
        """
        Calculate confidence for ATS pass probability.

        Args:
            pass_probability: Estimated pass probability (0-100)
            num_checks: Number of ATS compatibility checks performed

        Returns:
            ConfidenceScore with confidence interval
        """
        return self.calculate_with_confidence(
            score=pass_probability,
            sample_size=num_checks,
            measurement_type='binary'
        )

    def calculate_quality_confidence(
        self,
        quality_score: float,
        component_scores: list
    ) -> ConfidenceScore:
        """
        Calculate confidence for quality scores.

        Args:
            quality_score: Overall quality score (0-100)
            component_scores: List of individual component scores

        Returns:
            ConfidenceScore with confidence interval
        """
        return self.calculate_with_confidence(
            score=quality_score,
            sample_size=len(component_scores),
            score_components=component_scores,
            measurement_type='percentage'
        )

    def get_confidence_explanation(self, confidence: ConfidenceScore) -> Dict[str, str]:
        """
        Generate detailed explanation of confidence interval.

        Args:
            confidence: ConfidenceScore object

        Returns:
            Dict with explanation text
        """
        confidence_pct = int(self.confidence_level * 100)

        return {
            'interpretation': f"We are {confidence_pct}% confident that your true score is between "
                            f"{confidence.confidence_lower:.0f} and {confidence.confidence_upper:.0f}.",
            'reliability': f"This score has {confidence.reliability_rating.lower()} reliability based on "
                          f"the amount of data available.",
            'meaning': "A smaller margin of error (±) indicates more precise measurement. "
                      "More data points lead to higher confidence.",
            'recommendation': self._get_confidence_recommendation(confidence)
        }

    def _get_confidence_recommendation(self, confidence: ConfidenceScore) -> str:
        """Generate recommendation based on confidence level"""
        if confidence.margin_of_error > 10:
            return "The margin of error is relatively high. Consider this score as a general estimate."
        elif confidence.margin_of_error > 5:
            return "The score is moderately precise. It provides a good indication of your resume quality."
        else:
            return "The score is highly precise with low uncertainty."


# Convenience functions

def add_confidence_intervals(
    scores: Dict[str, float],
    sample_sizes: Dict[str, int] = None
) -> Dict[str, Dict]:
    """
    Quick function to add confidence intervals to multiple scores.

    Usage:
        scores = {'keyword_score': 75, 'quality_score': 82}
        sample_sizes = {'keyword_score': 30, 'quality_score': 50}
        results = add_confidence_intervals(scores, sample_sizes)
    """
    scorer = ConfidenceScorer()
    results = {}

    sample_sizes = sample_sizes or {}

    for score_name, score_value in scores.items():
        sample_size = sample_sizes.get(score_name, None)
        confidence = scorer.calculate_with_confidence(score_value, sample_size)

        results[score_name] = {
            'score': confidence.score,
            'confidence_interval': f"[{confidence.confidence_lower:.1f}, {confidence.confidence_upper:.1f}]",
            'margin_of_error': confidence.margin_of_error,
            'text': confidence.confidence_text,
            'reliability': confidence.reliability_rating
        }

    return results


def format_score_with_confidence(score: float, sample_size: int = None) -> str:
    """
    Format a score with its confidence interval for display.

    Usage:
        display_text = format_score_with_confidence(78, 35)
        # Returns: "78 ± 4 points (95% confidence)"
    """
    scorer = ConfidenceScorer()
    confidence = scorer.calculate_with_confidence(score, sample_size)
    return confidence.confidence_text
