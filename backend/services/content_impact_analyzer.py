"""
Content Impact Analyzer - Core component for evaluating resume content quality.

This module provides sophisticated content analysis including:
- Achievement strength scoring (CAR structure detection)
- Sentence clarity analysis
- Specificity evaluation
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional


class ContentImpactAnalyzer:
    """
    Analyzes resume content quality using NLP techniques.

    Evaluates:
    - Achievement strength (Context-Action-Result structure)
    - Sentence clarity (length, weak phrases, active voice)
    - Specificity (technologies, metrics, actions)
    """

    def __init__(self):
        """Initialize analyzer with pattern data"""
        self.patterns_dir = Path(__file__).parent.parent / "data" / "patterns"
        self._load_patterns()

    def _load_patterns(self):
        """Load pattern data from JSON files"""
        try:
            # Load action verb tiers
            with open(self.patterns_dir / "action_verb_tiers.json") as f:
                verb_data = json.load(f)
                self.verb_tiers = {}
                for tier_name, verbs in verb_data.items():
                    # Robust tier number parsing with fallback
                    try:
                        tier_num = int(tier_name.split('_')[1])
                    except (IndexError, ValueError):
                        # Fallback: extract first digit found
                        match = re.search(r'\d+', tier_name)
                        if match:
                            tier_num = int(match.group())
                        else:
                            raise ValueError(f"Cannot extract tier number from: {tier_name}")

                    for verb in verbs:
                        self.verb_tiers[verb.lower()] = tier_num

            # Load metric patterns
            with open(self.patterns_dir / "metric_patterns.json") as f:
                metric_data = json.load(f)
                self.metric_patterns = metric_data['patterns']
                self.metric_quality_weights = metric_data['quality_weights']

            # Load weak phrases
            with open(self.patterns_dir / "weak_phrases.json") as f:
                self.weak_phrases = json.load(f)

            # Load generic-to-specific mappings
            with open(self.patterns_dir / "generic_to_specific.json") as f:
                self.generic_to_specific = json.load(f)

        except FileNotFoundError as e:
            raise RuntimeError(f"Pattern file not found: {e}")
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Invalid JSON in pattern file: {e}")
        except (KeyError, ValueError) as e:
            raise RuntimeError(f"Invalid pattern file format: {e}")

    def classify_verb_tier(self, verb: str) -> int:
        """
        Classify action verb strength tier (0-4).

        Args:
            verb: Action verb or phrase to classify

        Returns:
            Tier number: 4 (transformational), 3 (leadership), 2 (execution),
                        1 (support), 0 (weak)
        """
        verb_lower = verb.lower().strip()
        return self.verb_tiers.get(verb_lower, 1)  # Default to tier 1 (neutral)

    def extract_metrics(self, text: str) -> List[Dict]:
        """
        Extract quantifiable metrics from text.

        Args:
            text: Text to analyze

        Returns:
            List of metric dictionaries with 'value', 'type', and 'quality'
        """
        metrics = []

        for metric_type, pattern in self.metric_patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                # Handle tuple matches (from capturing groups)
                if isinstance(match, tuple):
                    value = match[0] if match[0] else match[1]
                else:
                    value = match

                metrics.append({
                    'value': value,
                    'type': metric_type,
                    'quality': self.evaluate_metric_quality(metric_type)
                })

        return metrics

    def evaluate_metric_quality(self, metric_type: str) -> float:
        """
        Rate metric quality/impact (0-1 scale).

        Args:
            metric_type: Type of metric (percentage, money, etc.)

        Returns:
            Quality score (1.0 = excellent, 0.5 = basic)
        """
        return self.metric_quality_weights.get(metric_type, 0.5)

    def analyze_achievement_structure(self, bullet: str) -> Dict:
        """
        Analyze bullet for CAR (Context-Action-Result) structure.

        Args:
            bullet: Resume bullet point text

        Returns:
            Dictionary with score, components, and explanation
        """
        # Component 1: CONTEXT Detection (excludes weak indicators like "to")
        context_indicators = [
            "for", "to address", "given", "facing", "with",
            "across", "managing", "overseeing", "in", "at"
        ]
        has_context = any(indicator in bullet.lower() for indicator in context_indicators)

        # Component 2: ACTION Detection
        action_verb = self._extract_leading_verb(bullet)
        action_strength = self.classify_verb_tier(action_verb)

        # Component 3: RESULT Detection
        metrics = self.extract_metrics(bullet)

        # Component 4: CAUSALITY Detection (strong causal indicators only)
        strong_causality_words = [
            "by", "through", "via", "resulting in",
            "leading to", "enabling", "allowing"
        ]
        weak_causality_words = ["to"]

        has_strong_causality = any(word in bullet.lower() for word in strong_causality_words)
        has_weak_causality = "to" in bullet.lower()
        has_causality = has_strong_causality or has_weak_causality

        # SCORING LOGIC
        score = 0

        # Perfect CAR structure (14-15 pts) - full CAR with STRONG causality
        if has_context and action_strength >= 3 and len(metrics) >= 1 and has_strong_causality:
            # Even better with multiple metrics
            if len(metrics) >= 2:
                score = 14.5
            else:
                score = 14

        # Excellent AR with multiple metrics (13-14 pts)
        elif action_strength >= 3 and len(metrics) >= 2:
            score = 13

        # Good AR structure (11-13 pts) - strong action + result
        elif action_strength >= 3 and len(metrics) >= 1:
            score = 12

        # Moderate: Action + vague result (8-10 pts)
        elif action_strength >= 2 and (len(metrics) >= 1 or has_context):
            score = 9

        # Weak: Just action or duty (3-7 pts)
        elif action_strength >= 1:
            # Slightly better if has context or "and" connections
            if has_context or " and " in bullet.lower():
                score = 4
            # Even weaker if no metrics, no context, tier 1 verb
            elif len(metrics) == 0 and action_strength == 1:
                score = 2  # Borderline very weak
            else:
                score = 3

        # Very weak: No clear action (0-2 pts)
        else:
            score = 1

        return {
            'score': score,
            'has_context': has_context,
            'action_strength': action_strength,
            'action_verb': action_verb,
            'metrics_found': metrics,
            'has_causality': has_causality,
            'explanation': self._generate_car_explanation(score, action_strength, len(metrics))
        }

    def _extract_leading_verb(self, bullet: str) -> str:
        """
        Extract the leading action verb from a bullet point.

        Args:
            bullet: Bullet point text

        Returns:
            Leading verb or phrase
        """
        # Remove bullet markers
        text = re.sub(r'^[•\-\*]\s*', '', bullet.strip())

        # Extract first 1-3 words (handles "responsible for" etc.)
        words = text.split()
        if not words:
            return ""

        # Check for 2-word phrases first
        if len(words) >= 2:
            two_word = f"{words[0]} {words[1]}".lower()
            if two_word in self.verb_tiers:
                return two_word

        # Return first word
        return words[0].lower()

    def _generate_car_explanation(self, score: float, action_strength: int, metric_count: int) -> str:
        """Generate explanation for achievement score"""
        if score >= 14:
            return "Excellent: Clear CAR structure with strong action, multiple metrics, and causality"
        elif score >= 11:
            return "Good: Strong action with quantified results"
        elif score >= 8:
            return "Moderate: Has action and some results but vague"
        elif score >= 3:
            return "Weak: Just a duty statement without clear results"
        else:
            return "Very weak: No clear action or achievement"

    def score_achievement_strength(self, bullets: List[str], level: str = "mid") -> float:
        """
        Score overall achievement strength across all bullets.

        Args:
            bullets: List of experience bullet points
            level: Experience level (entry, mid, senior, lead, executive)

        Returns:
            Achievement strength score (0-15 points)
        """
        if not bullets:
            return 0.0

        bullet_scores = []

        for bullet in bullets:
            # Skip empty or very short bullets
            if not bullet or len(bullet.strip()) < 10:
                continue

            # Analyze CAR structure
            analysis = self.analyze_achievement_structure(bullet)
            score = analysis['score']

            # Apply level-based adjustments
            score = self._adjust_score_for_level(score, level, bullet)

            bullet_scores.append(score)

        if not bullet_scores:
            return 0.0

        # Return weighted average (capped at 15)
        avg_score = sum(bullet_scores) / len(bullet_scores)
        return min(avg_score, 15.0)

    def _adjust_score_for_level(self, raw_score: float, level: str, bullet: str) -> float:
        """
        Adjust achievement score based on experience level appropriateness.

        Args:
            raw_score: Raw achievement score
            level: Experience level
            bullet: Bullet text

        Returns:
            Adjusted score
        """
        # Get action verb strength
        verb = self._extract_leading_verb(bullet)
        verb_tier = self.classify_verb_tier(verb)

        # Entry level: more lenient, no penalty for tier 1+ verbs
        if level == "entry":
            if verb_tier >= 1:
                return raw_score  # No penalty
            else:
                return raw_score * 0.8

        # Senior+: expect tier 3+ verbs, but don't over-penalize good bullets
        elif level in ["senior", "lead", "executive"]:
            if verb_tier >= 3:
                return raw_score  # Good
            elif verb_tier >= 2:
                return raw_score * 0.95  # Acceptable
            else:
                return raw_score * 0.7  # Too junior

        # Mid level: expect tier 2+ verbs (default case)
        else:
            if verb_tier >= 2:
                return raw_score
            else:
                return raw_score * 0.85

        return raw_score

    def score_sentence_length(self, sentences: List[str], section: str = "experience") -> float:
        """
        Score sentence length appropriateness (max 3 pts).

        Args:
            sentences: List of sentences to analyze
            section: Section type (experience, summary, education)

        Returns:
            Length score (0-3 points)
        """
        optimal_ranges = {
            "experience": (15, 25),
            "summary": (10, 20),
            "education": (5, 15),
        }

        optimal_min, optimal_max = optimal_ranges.get(section, (15, 25))

        length_scores = []
        for sentence in sentences:
            if not sentence or len(sentence.strip()) < 3:
                continue

            word_count = len(sentence.split())

            if optimal_min <= word_count <= optimal_max:
                score = 1.0  # Perfect
            elif (optimal_min - 3) <= word_count <= (optimal_max + 5):
                score = 0.85  # Very close to optimal
            elif (optimal_min - 7) <= word_count <= (optimal_max + 10):
                score = 0.5  # Acceptable
            else:
                score = 0.0  # Too short/long

            length_scores.append(score)

        if not length_scores:
            return 0.0

        return (sum(length_scores) / len(length_scores)) * 3  # Max 3 pts

    def detect_weak_phrases(self, text: str) -> Dict:
        """
        Detect and penalize weak phrases (max 4 pts).

        Args:
            text: Text to analyze

        Returns:
            Dictionary with score, penalties, and found phrases
        """
        text_lower = text.lower()
        penalties = 0
        found_phrases = []

        for category, phrases in self.weak_phrases.items():
            for phrase in phrases:
                if phrase in text_lower:
                    penalties += 1
                    found_phrases.append((phrase, category))

        # Max -4 pts penalty
        score = max(0, 4 - min(penalties, 4))

        return {
            'score': score,
            'penalties': min(penalties, 4),
            'found': found_phrases
        }

    def calculate_active_voice_percentage(self, text: str) -> float:
        """
        Calculate percentage of sentences in active voice.

        Args:
            text: Text to analyze

        Returns:
            Active voice percentage (0-100)
        """
        # Split into sentences
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]

        if not sentences:
            return 100.0

        passive_indicators = [
            r"was \w+ed",
            r"were \w+ed",
            r"has been \w+ed",
            r"have been \w+ed",
            r"being \w+ed",
            r"been \w+ed"
        ]

        passive_count = 0
        for sentence in sentences:
            if any(re.search(pattern, sentence.lower()) for pattern in passive_indicators):
                passive_count += 1

        active_percentage = ((len(sentences) - passive_count) / len(sentences)) * 100
        return active_percentage

    def score_sentence_clarity(self, bullets: List[str], section: str = "experience") -> float:
        """
        Score overall sentence clarity (max 10 pts).

        Breakdown:
        - Sentence length: 3 pts
        - Weak phrase detection: 4 pts
        - Active voice: 3 pts

        Args:
            bullets: List of bullet points
            section: Section type

        Returns:
            Clarity score (0-10 points)
        """
        if not bullets:
            return 0.0

        # Combine all bullets into text
        text = " ".join(bullets)

        # Component 1: Sentence length (3 pts)
        length_score = self.score_sentence_length(bullets, section)

        # Component 2: Weak phrase detection (4 pts)
        weak_phrase_result = self.detect_weak_phrases(text)
        weak_phrase_score = weak_phrase_result['score']

        # Component 3: Active voice (3 pts)
        active_pct = self.calculate_active_voice_percentage(text)
        if active_pct >= 90:
            active_score = 3.0
        elif active_pct >= 75:
            active_score = 2.0
        elif active_pct >= 60:
            active_score = 1.0
        else:
            active_score = 0.0

        total_score = length_score + weak_phrase_score + active_score
        return min(total_score, 10.0)

    def score_technology_specificity(self, text: str) -> float:
        """
        Score technology/tool specificity (max 2 pts).

        Args:
            text: Text to analyze

        Returns:
            Technology specificity score (0-2 points)
        """
        text_lower = text.lower()
        specific_count = 0
        generic_count = 0

        # Count specific and generic mentions
        for category, terms in self.generic_to_specific.items():
            # Count specific examples
            if 'specific_examples' in terms:
                for tech in terms['specific_examples']:
                    if tech.lower() in text_lower:
                        specific_count += 1

            # Count generic terms
            if 'generic_terms' in terms:
                for generic_term in terms['generic_terms']:
                    if generic_term.lower() in text_lower:
                        generic_count += 1

        # Calculate specificity ratio
        if specific_count + generic_count == 0:
            return 1.0  # No tech mentioned (neutral)

        specificity_ratio = specific_count / (specific_count + generic_count)

        if specificity_ratio >= 0.8:
            return 2.0  # Highly specific
        elif specificity_ratio >= 0.5:
            return 1.0  # Moderately specific
        else:
            return 0.0  # Too generic

    def score_metric_specificity(self, text: str) -> float:
        """
        Score metric precision (max 2 pts).

        Args:
            text: Text to analyze

        Returns:
            Metric specificity score (0-2 points)
        """
        vague_metrics = [
            "significant", "substantial", "considerable", "major",
            "notable", "meaningful", "impressive", "dramatic",
            "many", "several", "numerous", "various"
        ]

        # Extract precise metrics
        precise_metrics = self.extract_metrics(text)

        # Count vague metric claims
        vague_count = sum(1 for word in vague_metrics if word in text.lower())

        # Score based on precision
        if len(precise_metrics) >= 3 and vague_count == 0:
            return 2.0  # Highly precise
        elif len(precise_metrics) >= 1 and vague_count <= 1:
            return 1.0  # Moderately precise
        else:
            return 0.0  # Too vague

    def score_action_specificity(self, text: str) -> float:
        """
        Score action verb specificity (max 1 pt).

        Args:
            text: Text to analyze

        Returns:
            Action specificity score (0-1 point)
        """
        concrete_actions = [
            "architected", "refactored", "migrated", "deployed",
            "launched", "scaled", "optimized", "automated",
            "integrated", "implemented", "engineered", "designed"
        ]

        abstract_actions = [
            "built", "improved", "enhanced", "developed",
            "worked", "helped", "supported", "managed"
        ]

        text_lower = text.lower()
        concrete_count = sum(1 for verb in concrete_actions if verb in text_lower)
        abstract_count = sum(1 for verb in abstract_actions if verb in text_lower)

        if concrete_count >= abstract_count and concrete_count > 0:
            return 1.0
        else:
            return 0.0

    def score_specificity(self, bullets: List[str]) -> float:
        """
        Score overall specificity (max 5 pts).

        Breakdown:
        - Technology specificity: 2 pts
        - Metric specificity: 2 pts
        - Action specificity: 1 pt

        Args:
            bullets: List of bullet points

        Returns:
            Specificity score (0-5 points)
        """
        if not bullets:
            return 0.0

        text = " ".join(bullets)

        tech_score = self.score_technology_specificity(text)
        metric_score = self.score_metric_specificity(text)
        action_score = self.score_action_specificity(text)

        total = tech_score + metric_score + action_score
        return min(total, 5.0)

    def score_impact_quality(
        self,
        bullets: List[str],
        level: str = "mid",
        section: str = "experience"
    ) -> Dict:
        """
        Score overall impact quality (max 30 pts).

        Breakdown:
        - Achievement strength: 15 pts
        - Sentence clarity: 10 pts
        - Specificity: 5 pts

        Args:
            bullets: List of bullet points
            level: Experience level
            section: Section type (experience, summary, education)

        Returns:
            Dictionary with scores and breakdown
        """
        if not bullets:
            return {
                'total_score': 0.0,
                'achievement_strength': 0.0,
                'sentence_clarity': 0.0,
                'specificity': 0.0,
                'details': 'No content to analyze'
            }

        # Special handling for summary section
        if section == "summary":
            # Skip achievement analysis, focus on clarity and specificity
            clarity_score = self.score_sentence_clarity(bullets, section)
            specificity_score = self.score_specificity(bullets)

            # Scale scores to fit 30-point scale
            # Summary: 60% clarity, 40% specificity
            total = (clarity_score * 1.8) + (specificity_score * 2.4)

            return {
                'total_score': min(total, 30.0),
                'achievement_strength': 0.0,  # N/A for summary
                'sentence_clarity': clarity_score,
                'specificity': specificity_score,
                'details': 'Summary section - relaxed analysis'
            }

        # Experience section: full analysis
        achievement_score = self.score_achievement_strength(bullets, level)
        clarity_score = self.score_sentence_clarity(bullets, section)
        specificity_score = self.score_specificity(bullets)

        total_score = achievement_score + clarity_score + specificity_score

        return {
            'total_score': min(total_score, 30.0),
            'achievement_strength': achievement_score,
            'sentence_clarity': clarity_score,
            'specificity': specificity_score,
            'details': f'Full impact analysis for {section} section'
        }
