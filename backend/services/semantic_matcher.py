"""
Semantic Keyword Matcher - Phase 1.2
Uses sentence-transformers and KeyBERT for intelligent keyword matching.

This module provides:
- Semantic keyword extraction from job descriptions
- Similarity-based matching (understands synonyms and related terms)
- Hybrid matching (combines semantic + exact string matching)
"""

from typing import List, Dict, Tuple
import re
import logging
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
from functools import lru_cache

logger = logging.getLogger(__name__)

# Timeout in seconds for downloading/loading the sentence-transformers model.
# On Render free tier the download can hang for minutes; 30s is generous enough
# for a cached model but short enough to avoid blocking requests.
_MODEL_LOAD_TIMEOUT_SECONDS = 30

# Phase 1.4: Caching support
try:
    from backend.services.cache_utils import cache_embeddings, cache_keywords
    CACHING_AVAILABLE = True
except ImportError:
    CACHING_AVAILABLE = False
    # Fallback decorators that do nothing
    def cache_embeddings(expire=None):
        return lambda f: f
    def cache_keywords(expire=None):
        return lambda f: f


class SemanticKeywordMatcher:
    """
    Semantic keyword matcher using sentence-transformers.

    Features:
    - Extract keywords from job descriptions using KeyBERT
    - Calculate semantic similarity between resume and keywords
    - Hybrid scoring: 70% semantic + 30% exact matching
    """

    def __init__(self):
        """Initialize semantic models (lazy loading for performance)"""
        self._model = None
        self._keybert = None
        self._initialized = False
        self._init_failed = False  # Permanently skip retries after timeout/failure

    def _lazy_init(self):
        """
        Lazy initialization with a hard timeout.

        On Render free tier, downloading the 80 MB all-MiniLM-L6-v2 model can
        block for several minutes if the file is not already cached.  We run the
        download in a background thread and give it _MODEL_LOAD_TIMEOUT_SECONDS
        to complete.  If it times out or raises any exception we permanently fall
        back to exact keyword matching so subsequent requests are not affected.
        """
        if self._initialized or self._init_failed:
            return

        def _load():
            from sentence_transformers import SentenceTransformer
            from keybert import KeyBERT
            model = SentenceTransformer('all-MiniLM-L6-v2')
            return model, KeyBERT(model)

        try:
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(_load)
                try:
                    self._model, self._keybert = future.result(timeout=_MODEL_LOAD_TIMEOUT_SECONDS)
                    self._initialized = True
                    logger.info("Semantic matcher initialized successfully")
                except FuturesTimeoutError:
                    logger.warning(
                        "Semantic matcher model download timed out after %ds — "
                        "falling back to exact keyword matching",
                        _MODEL_LOAD_TIMEOUT_SECONDS,
                    )
                    self._init_failed = True
                except Exception as e:
                    logger.warning(
                        "Could not load sentence-transformers model (%s) — "
                        "falling back to exact keyword matching", e
                    )
                    self._init_failed = True
        except ImportError as e:
            raise ImportError(
                "Required packages not installed. Run: "
                "pip install sentence-transformers keybert"
            ) from e

    @cache_keywords(expire=1800)  # Cache for 30 minutes
    def extract_keywords(
        self,
        job_description: str,
        top_n: int = 20,
        diversity: float = 0.7
    ) -> List[Tuple[str, float]]:
        """
        Extract key phrases from job description using KeyBERT.

        Phase 1.4: Results are cached for 30 minutes for performance.

        Args:
            job_description: Job description text
            top_n: Number of keywords to extract (default: 20)
            diversity: MMR diversity parameter 0-1 (default: 0.7)
                      Higher = more diverse keywords

        Returns:
            List of (keyword, relevance_score) tuples
        """
        self._lazy_init()

        if not job_description or len(job_description.strip()) < 10:
            return []

        # If model failed to load (or timed out), use fallback immediately
        if self._keybert is None or self._init_failed:
            return self._fallback_keyword_extraction(job_description, top_n)

        try:
            # Extract keywords using KeyBERT
            keywords = self._keybert.extract_keywords(
                job_description,
                keyphrase_ngram_range=(1, 2),  # 1-2 word phrases (trigrams too specific to match)
                stop_words='english',
                top_n=top_n,
                use_mmr=True,  # Use Maximal Marginal Relevance for diversity
                diversity=diversity
            )
            return keywords
        except Exception as e:
            # Fallback to simple extraction if KeyBERT fails
            print(f"KeyBERT extraction failed: {e}")
            return self._fallback_keyword_extraction(job_description, top_n)

    @cache_embeddings(expire=7200)  # Cache embeddings for 2 hours
    def semantic_match_score(
        self,
        resume_text: str,
        job_keywords: List[str],
        similarity_threshold: float = 0.7
    ) -> Dict:
        """
        Calculate semantic similarity between resume and job keywords.

        Phase 1.4: Embeddings are cached for 2 hours for performance.

        Args:
            resume_text: Full resume text
            job_keywords: List of keywords from job description
            similarity_threshold: Minimum similarity to count as match (0-1)

        Returns:
            Dictionary with:
            - match_rate: Percentage of keywords matched (0-1)
            - matches: List of matched keywords with scores
            - missing: List of unmatched keywords
        """
        self._lazy_init()

        if not resume_text or not job_keywords:
            return {
                'match_rate': 0.0,
                'matches': [],
                'missing': job_keywords or []
            }

        # If model failed to load (or timed out), use exact matching fallback
        if self._model is None or self._init_failed:
            return self._fallback_exact_matching(resume_text, job_keywords, similarity_threshold)

        try:
            from sentence_transformers import util

            # Encode resume text
            resume_embedding = self._model.encode(
                resume_text,
                convert_to_tensor=True,
                show_progress_bar=False
            )

            # Encode keywords
            keyword_embeddings = self._model.encode(
                job_keywords,
                convert_to_tensor=True,
                show_progress_bar=False
            )

            # Calculate cosine similarities
            similarities = util.cos_sim(resume_embedding, keyword_embeddings)[0]

            # Count high-confidence matches
            matches = []
            missing = []

            for i, keyword in enumerate(job_keywords):
                similarity = similarities[i].item()
                if similarity >= similarity_threshold:
                    matches.append({
                        'keyword': keyword,
                        'similarity': round(similarity, 3)
                    })
                else:
                    missing.append(keyword)

            match_rate = len(matches) / len(job_keywords) if job_keywords else 0.0

            return {
                'match_rate': match_rate,
                'matches': matches,
                'missing': missing
            }
        except Exception as e:
            print(f"Semantic matching failed: {e}")
            # Fallback to exact matching
            return self._fallback_exact_match(resume_text, job_keywords)

    def hybrid_match_score(
        self,
        resume_text: str,
        job_keywords: List[str],
        semantic_weight: float = 0.7,
        exact_weight: float = 0.3
    ) -> Dict:
        """
        Hybrid matching: combines semantic (70%) + exact (30%) matching.

        Args:
            resume_text: Full resume text
            job_keywords: List of keywords from job description
            semantic_weight: Weight for semantic matching (default: 0.7)
            exact_weight: Weight for exact matching (default: 0.3)

        Returns:
            Dictionary with:
            - hybrid_score: Combined score (0-1)
            - semantic_score: Semantic matching score
            - exact_score: Exact matching score
            - matched_keywords: List of matched keywords
            - missing_keywords: List of missing keywords
        """
        # Semantic matching
        semantic_result = self.semantic_match_score(resume_text, job_keywords)
        semantic_score = semantic_result['match_rate']

        # Exact matching
        exact_result = self._fallback_exact_match(resume_text, job_keywords)
        exact_score = exact_result['match_rate']

        # Combine scores
        hybrid_score = (semantic_weight * semantic_score) + (exact_weight * exact_score)

        # Merge matched/missing keywords (prefer semantic results)
        matched_keywords = semantic_result['matches']
        missing_keywords = semantic_result['missing']

        return {
            'hybrid_score': hybrid_score,
            'semantic_score': semantic_score,
            'exact_score': exact_score,
            'matched_keywords': matched_keywords,
            'missing_keywords': missing_keywords,
            'total_keywords': len(job_keywords)
        }

    def _fallback_keyword_extraction(
        self,
        text: str,
        top_n: int = 20
    ) -> List[Tuple[str, float]]:
        """
        Fallback keyword extraction using simple frequency analysis.
        Used when KeyBERT is not available or fails.

        Args:
            text: Text to extract keywords from
            top_n: Number of keywords to extract

        Returns:
            List of (keyword, score) tuples
        """
        # Clean text
        text = text.lower()

        # Remove common stop words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
            'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
            'should', 'could', 'may', 'might', 'must', 'can', 'this', 'that',
            'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they'
        }

        # Extract words
        words = re.findall(r'\b[a-z]{3,}\b', text)

        # Count frequencies
        word_freq = {}
        for word in words:
            if word not in stop_words:
                word_freq[word] = word_freq.get(word, 0) + 1

        # Sort by frequency
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)

        # Normalize scores to 0-1
        max_freq = sorted_words[0][1] if sorted_words else 1
        normalized = [(word, freq / max_freq) for word, freq in sorted_words[:top_n]]

        return normalized

    def _fallback_exact_matching(
        self,
        resume_text: str,
        job_keywords: List[str],
        similarity_threshold: float = 0.7
    ) -> Dict:
        """
        Fallback exact string matching when semantic model is unavailable.
        Ignores similarity_threshold since exact matching is binary (match or no match).

        Args:
            resume_text: Full resume text
            job_keywords: List of keywords to match
            similarity_threshold: Ignored (for API compatibility)

        Returns:
            Dictionary with match_rate, matches, and missing
        """
        return self._fallback_exact_match(resume_text, job_keywords)

    def _fallback_exact_match(
        self,
        resume_text: str,
        job_keywords: List[str]
    ) -> Dict:
        """
        Fallback exact string matching (case-insensitive).

        Args:
            resume_text: Full resume text
            job_keywords: List of keywords to match

        Returns:
            Dictionary with match_rate, matches, and missing
        """
        resume_lower = resume_text.lower()

        matches = []
        missing = []

        for keyword in job_keywords:
            keyword_lower = keyword.lower()
            if keyword_lower in resume_lower:
                matches.append({
                    'keyword': keyword,
                    'similarity': 1.0  # Exact match
                })
            else:
                missing.append(keyword)

        match_rate = len(matches) / len(job_keywords) if job_keywords else 0.0

        return {
            'match_rate': match_rate,
            'matches': matches,
            'missing': missing
        }


# Singleton instance for caching
_semantic_matcher_instance = None


def get_semantic_matcher() -> SemanticKeywordMatcher:
    """
    Get singleton instance of SemanticKeywordMatcher.
    This ensures models are only loaded once per process.

    Returns:
        SemanticKeywordMatcher instance
    """
    global _semantic_matcher_instance
    if _semantic_matcher_instance is None:
        _semantic_matcher_instance = SemanticKeywordMatcher()
    return _semantic_matcher_instance
