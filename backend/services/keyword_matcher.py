"""
Keyword matching engine with O(1) lookup and synonym support.
Matches resume text against role keywords with fuzzy matching.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Set
from fuzzywuzzy import fuzz


class KeywordMatcher:
    """
    Matches keywords with synonym expansion and fuzzy matching.
    Performance: O(1) lookups using hash sets.
    """

    def __init__(self):
        """Load keyword database and synonyms"""
        self.data_dir = Path(__file__).parent.parent / "data"

        # Load role keywords
        with open(self.data_dir / "keywords" / "role_keywords.json", 'r') as f:
            self.role_keywords = json.load(f)

        # Load synonyms
        with open(self.data_dir / "synonyms" / "skill_synonyms.json", 'r') as f:
            self.synonyms = json.load(f)

        # Build reverse synonym map for faster lookup
        self.reverse_synonyms = {}
        for primary, variations in self.synonyms.items():
            for variation in variations:
                self.reverse_synonyms[variation.lower()] = primary

    def normalize_text(self, text: str) -> str:
        """Normalize text: lowercase, remove special chars"""
        return re.sub(r'[^a-z0-9\s]', ' ', text.lower())

    def tokenize(self, text: str) -> Set[str]:
        """Tokenize text into unique words and bigrams"""
        normalized = self.normalize_text(text)
        tokens = set(normalized.split())

        # Also include bigrams for compound terms like "machine learning"
        words = normalized.split()
        bigrams = [f"{words[i]} {words[i+1]}" for i in range(len(words)-1)]
        tokens.update(bigrams)

        return tokens

    def expand_with_synonyms(self, keyword: str) -> Set[str]:
        """Expand keyword with all synonyms"""
        keyword_lower = keyword.lower()
        variations = {keyword_lower}

        # Check if this keyword has synonyms (primary key)
        if keyword_lower in self.synonyms:
            variations.update([v.lower() for v in self.synonyms[keyword_lower]])

        # Check if this keyword is a synonym of another term (reverse lookup)
        if keyword_lower in self.reverse_synonyms:
            primary = self.reverse_synonyms[keyword_lower]
            variations.add(primary)
            # Also add all other synonyms of the primary term
            if primary in self.synonyms:
                variations.update([v.lower() for v in self.synonyms[primary]])

        return variations

    def match_keywords(self, resume_text: str, keywords: List[str]) -> Dict:
        """
        Match keywords against resume text with synonym support.

        Returns:
            {
                'percentage': float,
                'matched': List[str],
                'missing': List[str]
            }
        """
        if not keywords:
            return {
                'percentage': 0,
                'matched': [],
                'missing': []
            }

        resume_tokens = self.tokenize(resume_text)

        matched = []
        missing = []

        for keyword in keywords:
            # Expand keyword with synonyms
            keyword_variations = self.expand_with_synonyms(keyword)

            # Check if any variation is in resume
            found = False
            for variation in keyword_variations:
                if variation in resume_tokens:
                    matched.append(keyword)
                    found = True
                    break

            if not found:
                # Try fuzzy matching (80% threshold)
                for token in resume_tokens:
                    for variation in keyword_variations:
                        if fuzz.ratio(token, variation) >= 80:
                            matched.append(keyword)
                            found = True
                            break
                    if found:
                        break

            if not found:
                missing.append(keyword)

        percentage = (len(matched) / len(keywords) * 100) if keywords else 0

        return {
            'percentage': percentage,
            'matched': matched,
            'missing': missing
        }

    def match_role_keywords(self, resume_text: str, role: str, level: str) -> Dict:
        """
        Match resume against role-specific keywords.

        Args:
            resume_text: Full resume text
            role: Role ID (e.g., "software_engineer")
            level: Experience level (e.g., "mid")

        Returns:
            Match result with percentage, matched, and missing keywords
        """
        role_level_key = f"{role}_{level}"

        if role_level_key not in self.role_keywords:
            return {
                'percentage': 0,
                'matched': [],
                'missing': [],
                'error': f"Role/level not found: {role_level_key}"
            }

        keywords = self.role_keywords[role_level_key]
        return self.match_keywords(resume_text, keywords)

    def match_job_description(self, resume_text: str, job_description: str) -> Dict:
        """
        Match resume against job description keywords.
        Extracts important keywords from JD and matches against resume.
        """
        # Extract keywords from JD (words > 3 chars, not stopwords)
        stopwords = {
            'the', 'and', 'for', 'with', 'this', 'that', 'from', 'have',
            'will', 'your', 'they', 'been', 'their', 'what', 'which', 'when',
            'where', 'about', 'would', 'there', 'could', 'should'
        }

        jd_tokens = self.tokenize(job_description)
        jd_keywords = [
            token for token in jd_tokens
            if len(token) > 3 and token not in stopwords
        ]

        # Limit to top 50 most relevant keywords (by frequency and uniqueness)
        # For now, just take first 50 unique tokens
        jd_keywords = list(set(jd_keywords))[:50]

        return self.match_keywords(resume_text, jd_keywords)
