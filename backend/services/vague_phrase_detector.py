"""
Vague Phrase Detector

Identifies weak, passive phrases that indicate low-impact achievements.
Used for Achievement Depth scoring (Parameter P2.3).

Research basis:
- ResumeWorded study: Resumes with 3+ vague phrases score 40% lower
- Career coaches recommend max 1-2 passive phrases per resume
- ATS systems penalize lack of specificity and measurable impact
"""

import json
import re
from pathlib import Path
from typing import Dict, List


class VaguePhraseDetector:
    """
    Detect vague, passive phrases in resume text.

    Penalty structure (for Achievement Depth parameter):
    - 0 phrases: 5 points (excellent specificity)
    - 1-2 phrases: 4 points (minor issue)
    - 3-4 phrases: 2 points (moderate concern)
    - 5+ phrases: 0 points (poor specificity)
    """

    def __init__(self, data_path: str = None):
        """Initialize detector with vague phrases data."""
        if data_path is None:
            data_path = Path(__file__).parent.parent / "data" / "vague_phrases.json"

        with open(data_path, 'r') as f:
            data = json.load(f)

        self.vague_phrases = data['vague_phrases']

        # Compile regex patterns for case-insensitive matching
        self.patterns = [
            (phrase, re.compile(r'\b' + re.escape(phrase) + r'\b', re.IGNORECASE))
            for phrase in self.vague_phrases
        ]

    def detect(self, text: str) -> Dict:
        """
        Detect all vague phrases in the text.

        Args:
            text: Resume text or section

        Returns:
            {
                'count': int (total occurrences),
                'phrases_found': [
                    {
                        'phrase': str (original phrase from data),
                        'matches': List[str] (actual text matches),
                        'occurrences': int
                    }
                ]
            }
        """
        if not text:
            return {'count': 0, 'phrases_found': []}

        phrases_found = []
        total_count = 0

        for phrase, pattern in self.patterns:
            matches = pattern.findall(text)
            if matches:
                occurrences = len(matches)
                total_count += occurrences
                phrases_found.append({
                    'phrase': phrase,
                    'matches': matches,
                    'occurrences': occurrences
                })

        return {
            'count': total_count,
            'phrases_found': phrases_found
        }

    def get_penalty_score(self, vague_phrase_count: int) -> int:
        """
        Calculate penalty score based on vague phrase count.

        Scoring structure (out of 5 points):
        - 0 phrases: 5 points (no penalty)
        - 1-2 phrases: 4 points (minor penalty)
        - 3-4 phrases: 2 points (moderate penalty)
        - 5+ phrases: 0 points (full penalty)

        Args:
            vague_phrase_count: Total number of vague phrases found

        Returns:
            Score from 0-5
        """
        if vague_phrase_count == 0:
            return 5
        elif vague_phrase_count <= 2:
            return 4
        elif vague_phrase_count <= 4:
            return 2
        else:  # 5+
            return 0

    def analyze_resume(self, resume_text: str) -> Dict:
        """
        Complete analysis with detection and scoring.

        Args:
            resume_text: Full resume text

        Returns:
            {
                'vague_phrase_count': int,
                'penalty_score': int (0-5),
                'max_score': int (always 5),
                'phrases_found': List[Dict]
            }
        """
        detection_result = self.detect(resume_text)
        count = detection_result['count']
        score = self.get_penalty_score(count)

        return {
            'vague_phrase_count': count,
            'penalty_score': score,
            'max_score': 5,
            'phrases_found': detection_result['phrases_found']
        }


# Singleton instance
_detector_instance = None

def get_vague_phrase_detector() -> VaguePhraseDetector:
    """Get singleton instance of VaguePhraseDetector."""
    global _detector_instance
    if _detector_instance is None:
        _detector_instance = VaguePhraseDetector()
    return _detector_instance
