"""Parser for resume corpus files"""
import logging
import re
from collections import defaultdict
from pathlib import Path
from typing import Dict, Optional, Generator, Set

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


def extract_skills_from_text(text: str) -> Set[str]:
    """
    Extract potential skills from resume text

    Args:
        text: Resume text content

    Returns:
        Set of normalized skills found in text
    """
    # Normalize text to lowercase for matching
    text_lower = text.lower()

    # Extract individual words/tokens that could be skills
    # This captures:
    # - Single words: python, java, aws, sql
    # - Tech terms with special chars: c++, c#, node.js
    # - Compound terms with numbers: office365, windows10
    word_pattern = r'\b[a-z][a-z0-9+#\.]*\b'

    potential_skills = set()
    matches = re.finditer(word_pattern, text_lower)

    # Common stop words to exclude
    stop_words = {
        'the', 'and', 'for', 'with', 'from', 'this', 'that', 'have', 'has',
        'was', 'were', 'been', 'being', 'are', 'will', 'would', 'could',
        'should', 'may', 'can', 'resume', 'experience', 'work', 'job'
    }

    for match in matches:
        skill = match.group(0).strip()

        # Filter criteria:
        # - Minimum length of 2 characters
        # - Not a common stop word
        if len(skill) >= 2 and skill not in stop_words:
            # Remove trailing dots
            skill = skill.rstrip('.')
            if skill:
                potential_skills.add(skill)

    return potential_skills


def extract_skills_database(file_path: Path) -> Dict[str, Dict]:
    """
    Extract skills from skills_it.txt corpus file with frequencies

    Args:
        file_path: Path to skills_it.txt

    Returns:
        Dictionary mapping skill -> {frequency: count}
    """
    skills_db = defaultdict(lambda: {'frequency': 0})

    logger.info(f"Extracting skills from {file_path}")

    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            # Skip separator lines
            if line.strip() == '::::::' or line.strip() == ':::::::':
                continue

            # Parse resume line
            resume = parse_resume_line(line)
            if not resume:
                continue

            # Extract skills from resume text
            skills = extract_skills_from_text(resume['text'])

            # Update frequency count for each skill
            for skill in skills:
                skills_db[skill]['frequency'] += 1

    # Convert defaultdict to regular dict
    result = dict(skills_db)

    logger.info(f"Extracted {len(result)} unique skills")

    return result
