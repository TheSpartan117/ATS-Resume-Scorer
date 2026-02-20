"""Parser for resume corpus files"""
import logging
from pathlib import Path
from typing import Dict, Optional, Generator

logger = logging.getLogger(__name__)


def parse_resume_line(line: str) -> Optional[Dict]:
    """
    Parse a single resume line from resume_samples.txt

    Format: ID:::Occupations;;;:::Resume Text

    Args:
        line: Raw line from file

    Returns:
        Dict with id, occupations, text or None if malformed
    """
    try:
        parts = line.split(':::')
        if len(parts) != 3:
            return None

        resume_id = parts[0].strip()
        occupations = [occ.strip() for occ in parts[1].split(';') if occ.strip()]
        text = parts[2].strip()

        return {
            'id': resume_id,
            'occupations': occupations,
            'text': text
        }
    except Exception as e:
        logger.debug(f"Failed to parse line: {e}")
        return None


def stream_resume_samples(file_path: Path) -> Generator[Dict, None, None]:
    """
    Stream resume samples from file (memory efficient)

    Args:
        file_path: Path to resume_samples.txt

    Yields:
        Parsed resume dictionaries
    """
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            resume = parse_resume_line(line)
            if resume:
                yield resume
