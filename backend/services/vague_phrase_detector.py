"""
Vague Phrase Detector for Achievement Depth Scoring

Detects passive, vague phrases that indicate weak achievement descriptions.
Part of P2.3 (Achievement Depth) parameter.

Penalty structure:
- 0 instances: 5 points (excellent - strong, specific achievements)
- 1-2 instances: 4 points (good - mostly specific)
- 3-4 instances: 2 points (weak - too many vague descriptions)
- 5+ instances: 0 points (poor - predominantly vague)

Research basis: ResumeWorded, Jobscan analysis
"""

import json
import re
from pathlib import Path
from typing import Dict, List


class VaguePhraseDetector:
    """Detect vague, passive phrases in resume text."""

    def __init__(self, data_path: str = None):
        """Initialize detector with vague phrase patterns."""
        if data_path is None:
            data_path = Path(__file__).parent.parent / "data" / "vague_phrases.json"

        with open(data_path, 'r') as f:
            data = json.load(f)

        self.vague_phrases = data['vague_phrases']
        self.penalty_structure = data['penalty_structure']

        # Compile regex patterns for efficient matching
        # Case-insensitive, word boundary aware
        self.patterns = []
        for phrase in self.vague_phrases:
            # Escape special regex characters, use word boundaries
            pattern = re.compile(r'\b' + re.escape(phrase) + r'\b', re.IGNORECASE)
            self.patterns.append((phrase, pattern))

    def detect(self, resume_text: str) -> Dict:
        """
        Detect vague phrases in resume text and calculate penalty score.

        Args:
            resume_text: Full resume text or relevant section

        Returns:
            {
                'vague_phrase_count': int,  # Total occurrences
                'score': int,               # Points (0-5)
                'found_phrases': List[str], # Phrases found
                'penalty_breakdown': str    # Which penalty tier
            }
        """
        if not resume_text:
            return {
                'vague_phrase_count': 0,
                'score': 5,
                'found_phrases': [],
                'penalty_breakdown': '0 instances'
            }

        found_phrases = []

        # Count all occurrences of all vague phrases
        for phrase, pattern in self.patterns:
            matches = pattern.findall(resume_text)
            if matches:
                # Add phrase for each occurrence (handles duplicates)
                found_phrases.extend([phrase] * len(matches))

        vague_count = len(found_phrases)

        # Calculate score based on penalty structure
        if vague_count == 0:
            score = 5
            breakdown = '0 instances'
        elif 1 <= vague_count <= 2:
            score = 4
            breakdown = '1-2 instances'
        elif 3 <= vague_count <= 4:
            score = 2
            breakdown = '3-4 instances'
        else:  # 5+
            score = 0
            breakdown = '5+ instances'

        return {
            'vague_phrase_count': vague_count,
            'score': score,
            'found_phrases': found_phrases,
            'penalty_breakdown': breakdown
        }

    def get_vague_phrases_list(self) -> List[str]:
        """Get list of all vague phrases being detected."""
        return self.vague_phrases.copy()
