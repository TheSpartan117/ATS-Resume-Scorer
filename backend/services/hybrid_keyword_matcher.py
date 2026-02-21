"""
Hybrid Keyword Matcher - Task 4: Semantic+Exact Keyword Matching

Combines semantic similarity (70%) with exact matching (30%) to reduce false negatives.

Formula: match_score = (semantic_similarity * 0.7) + (exact_match * 0.3)

Research basis:
- Pure exact matching: 40% false negative rate
- Hybrid approach: Reduces false negatives by 35-45%
- Expected accuracy improvement: 75% → 90%

Source: ATS Research Comprehensive Report (Workday, Greenhouse analysis)

Examples:
- Keyword "Python" matches "Python" (exact): score ≈ 1.0
- Keyword "Python" matches "Pythonic" (semantic): score ≈ 0.6-0.7
- Keyword "Python" matches "Django (Python framework)": score ≈ 1.0
"""

import re
from typing import Dict, List


class HybridKeywordMatcher:
    """
    Hybrid keyword matching combining semantic similarity and exact matching.

    Weights:
    - Semantic similarity: 70% (using sentence-transformers all-MiniLM-L6-v2)
    - Exact match: 30% (case-insensitive string match with word boundaries)

    This approach reduces false negatives significantly:
    - "Python" matches "Python-based", "Pythonic", "Django (Python)"
    - "ML" matches "machine learning", "Machine Learning"
    - "API" matches "APIs", "RESTful API"
    """

    def __init__(self):
        """Initialize with semantic matcher from existing service."""
        from backend.services.semantic_matcher import get_semantic_matcher

        self.semantic_matcher_service = get_semantic_matcher()
        self.semantic_weight = 0.7
        self.exact_weight = 0.3
        self._model = None
        self._initialized = False

    def _lazy_init(self):
        """Lazy initialization to load model only when needed."""
        if self._initialized:
            return

        # Initialize the semantic matcher and get access to the model
        self.semantic_matcher_service._lazy_init()
        self._model = self.semantic_matcher_service._model
        self._initialized = True

    def _exact_match_score(self, keyword: str, text: str) -> float:
        """
        Check if keyword appears in text (case-insensitive, word boundary aware).

        Handles:
        - Case variations: "Python", "python", "PYTHON"
        - Compound words: "Python-based", "Django (Python)", "Node.js"
        - Word boundaries: Won't match "Pyt" in "Python"

        Args:
            keyword: The keyword to search for
            text: The text to search in

        Returns:
            1.0 if keyword found (exact or as part of compound word)
            0.0 if not found
        """
        if not keyword or not text:
            return 0.0

        # Case-insensitive search with word boundaries
        # \b ensures we match whole words or word-like components
        # Handles: "Python", "Python-based", "Django (Python)", etc.
        pattern = re.compile(r'\b' + re.escape(keyword) + r'\b', re.IGNORECASE)

        return 1.0 if pattern.search(text) else 0.0

    def _semantic_match_score(self, keyword: str, text: str) -> float:
        """
        Calculate semantic similarity between keyword and text.

        Uses sentence-transformers model (all-MiniLM-L6-v2) to compute
        embedding similarity via cosine similarity.

        Examples of semantic matches:
        - "Python" → "Pythonic programming" (0.7-0.8)
        - "ML" → "machine learning" (0.6-0.7)
        - "API" → "RESTful APIs" (0.6-0.7)

        Args:
            keyword: The keyword to match
            text: The text to match against

        Returns:
            Float between 0.0 and 1.0 representing semantic similarity
        """
        if not keyword or not text:
            return 0.0

        self._lazy_init()

        try:
            from sentence_transformers import util

            # Encode keyword and text into embeddings
            keyword_embedding = self._model.encode(
                keyword,
                convert_to_tensor=True,
                show_progress_bar=False
            )

            text_embedding = self._model.encode(
                text,
                convert_to_tensor=True,
                show_progress_bar=False
            )

            # Calculate cosine similarity
            similarity = util.cos_sim(keyword_embedding, text_embedding)[0][0].item()

            # Clamp to [0, 1] range (cosine sim can be -1 to 1, but we only care about positive)
            return max(0.0, min(1.0, similarity))

        except Exception as e:
            # Fallback to 0 if semantic matching fails
            print(f"Semantic matching failed for '{keyword}': {e}")
            return 0.0

    def match_keyword(self, keyword: str, resume_text: str) -> float:
        """
        Match a single keyword against resume text using hybrid approach.

        This is the core matching algorithm that combines:
        1. Semantic similarity (70%): Understands synonyms and related terms
        2. Exact match bonus (30%): Rewards exact keyword presence

        Args:
            keyword: The keyword to match (e.g., "Python", "machine learning")
            resume_text: Full resume text or relevant section

        Returns:
            Match score between 0.0 and 1.0

        Formula:
            score = (semantic_similarity * 0.7) + (exact_match * 0.3)

        Examples:
            - "Python" in "Python developer" → ~1.0 (semantic + exact)
            - "Python" in "Pythonic code" → ~0.6 (semantic only)
            - "Python" in "C++ developer" → ~0.1 (no match)
        """
        semantic_score = self._semantic_match_score(keyword, resume_text)
        exact_score = self._exact_match_score(keyword, resume_text)

        # Hybrid formula: 70% semantic + 30% exact
        hybrid_score = (semantic_score * self.semantic_weight) + (exact_score * self.exact_weight)

        return hybrid_score

    def match_keywords(self, keywords: List[str], resume_text: str) -> Dict[str, float]:
        """
        Match multiple keywords against resume text efficiently.

        Useful for batch processing job description keywords against a resume.

        Args:
            keywords: List of keywords to match (e.g., ["Python", "Django", "React"])
            resume_text: Full resume text or relevant section

        Returns:
            Dictionary mapping keyword → match score
            Example: {"Python": 0.98, "Django": 0.95, "React": 0.15}
        """
        if not keywords:
            return {}

        results = {}
        for keyword in keywords:
            results[keyword] = self.match_keyword(keyword, resume_text)

        return results

    def get_match_summary(
        self,
        keywords: List[str],
        resume_text: str,
        threshold: float = 0.6
    ) -> Dict:
        """
        Get detailed matching summary with statistics.

        Useful for understanding match quality and debugging scoring.

        Args:
            keywords: List of keywords to match
            resume_text: Resume text
            threshold: Minimum score to consider a match (default: 0.6 = 60%)

        Returns:
            Dictionary containing:
            {
                'total_keywords': int,           # Total number of keywords
                'matched_keywords': int,         # Number of keywords above threshold
                'match_rate': float,             # Percentage of matched keywords (0-100)
                'scores': Dict[str, float],      # Individual keyword scores
                'matched': List[str],            # List of matched keywords
                'unmatched': List[str]           # List of unmatched keywords
            }

        Example:
            >>> summary = matcher.get_match_summary(
            ...     ["Python", "Django", "React"],
            ...     "Python developer with Django experience"
            ... )
            >>> summary
            {
                'total_keywords': 3,
                'matched_keywords': 2,
                'match_rate': 66.67,
                'scores': {'Python': 0.98, 'Django': 0.95, 'React': 0.12},
                'matched': ['Python', 'Django'],
                'unmatched': ['React']
            }
        """
        scores = self.match_keywords(keywords, resume_text)

        matched = [kw for kw, score in scores.items() if score >= threshold]
        unmatched = [kw for kw, score in scores.items() if score < threshold]

        total = len(keywords)
        matched_count = len(matched)
        match_rate = (matched_count / total * 100) if total > 0 else 0.0

        return {
            'total_keywords': total,
            'matched_keywords': matched_count,
            'match_rate': match_rate,
            'scores': scores,
            'matched': matched,
            'unmatched': unmatched
        }


# Singleton instance for efficiency
_hybrid_matcher_instance = None


def get_hybrid_matcher() -> HybridKeywordMatcher:
    """
    Get singleton instance of HybridKeywordMatcher.

    Ensures model is loaded only once per process for efficiency.

    Returns:
        HybridKeywordMatcher instance
    """
    global _hybrid_matcher_instance
    if _hybrid_matcher_instance is None:
        _hybrid_matcher_instance = HybridKeywordMatcher()
    return _hybrid_matcher_instance
