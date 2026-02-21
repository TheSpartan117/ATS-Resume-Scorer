"""
Keyword extraction and classification from job descriptions.

This module extracts keywords from job descriptions and classifies them as
required vs preferred. It integrates with the synonym database for intelligent
matching, which is crucial for ATS Simulation mode scoring.
"""

import re
from typing import Dict, List, Set, Tuple

from services.synonym_database import get_all_synonyms


# Technical keywords to extract from job descriptions
TECH_KEYWORDS = [
    # Programming Languages
    "python", "java", "javascript", "typescript", "c++", "c#", "golang", "ruby",
    "php", "swift", "kotlin", "rust", "scala", "r", "perl", "shell",

    # Cloud Platforms
    "aws", "azure", "gcp", "ibm cloud", "oracle cloud",

    # AWS Services
    "ec2", "s3", "lambda", "rds", "dynamodb", "cloudformation", "eks", "ecs",

    # DevOps & CI/CD
    "kubernetes", "docker", "terraform", "jenkins", "gitlab", "github actions",
    "circleci", "travis ci", "ansible", "puppet", "chef", "vagrant",

    # Version Control
    "git", "svn", "mercurial",

    # Databases - SQL
    "postgresql", "mysql", "sql server", "oracle", "sqlite", "mariadb",

    # Databases - NoSQL
    "mongodb", "redis", "cassandra", "couchdb", "elasticsearch", "neo4j",

    # Web Frameworks
    "react", "angular", "vue", "django", "flask", "express", "spring", "laravel",

    # Mobile Development
    "android", "ios", "react native", "flutter",

    # Testing & QA
    "selenium", "junit", "pytest", "jest", "mocha", "cypress",
    "test driven development", "behavior driven development",

    # Data Science & ML
    "machine learning", "deep learning", "natural language processing",
    "computer vision", "artificial intelligence", "data science",
    "tensorflow", "pytorch", "scikit-learn", "pandas", "numpy",
    "matplotlib", "jupyter",

    # Methodologies & Practices
    "agile", "scrum", "kanban", "ci/cd", "microservices", "rest api",
    "graphql", "soap", "api", "sdk",

    # Project Management
    "jira", "confluence", "slack", "trello", "asana",

    # Security
    "security", "authentication", "oauth", "jwt", "ssl", "encryption",

    # Networking
    "http", "tcp/ip", "dns", "load balancing", "cdn",

    # Monitoring & Logging
    "prometheus", "grafana", "datadog", "new relic", "splunk", "elk",

    # Big Data
    "hadoop", "spark", "kafka", "airflow", "flink",
]

# Soft skills to extract from job descriptions
SOFT_SKILLS = [
    "leadership", "communication", "problem solving", "teamwork",
    "time management", "adaptability", "critical thinking", "mentoring",
    "collaboration", "analytical thinking", "organization", "prioritization",
    "flexibility", "creativity", "attention to detail", "self-motivated",
]

# Indicators that a keyword is required
REQUIRED_INDICATORS = [
    "required", "must have", "essential", "mandatory", "critical",
    "necessary", "need", "needs", "require", "requires",
]

# Indicators that a keyword is preferred/nice-to-have
PREFERRED_INDICATORS = [
    "preferred", "nice to have", "bonus", "plus", "desired",
    "a plus", "would be nice", "ideal", "optional", "advantageous",
]


def extract_keywords_from_jd(job_description: str) -> Dict[str, List[str]]:
    """
    Extract and classify keywords from job description.

    This function extracts technical keywords and soft skills from a job
    description and classifies them as required or preferred based on
    contextual indicators and frequency analysis.

    Args:
        job_description: The job description text to analyze

    Returns:
        Dictionary with three keys:
        - "required": List of required keywords
        - "preferred": List of preferred keywords
        - "all": List of all keywords found (required + preferred)

    Examples:
        >>> jd = "Required: Python, Docker. Preferred: Kubernetes"
        >>> result = extract_keywords_from_jd(jd)
        >>> "python" in result["required"]
        True
        >>> "kubernetes" in result["preferred"]
        True
    """
    text_lower = job_description.lower()

    # Find all keywords present in the job description
    found_keywords: Set[str] = set()

    # Check technical keywords
    for keyword in TECH_KEYWORDS:
        if match_with_synonyms(keyword, text_lower):
            found_keywords.add(keyword)

    # Check soft skills
    for skill in SOFT_SKILLS:
        if match_with_synonyms(skill, text_lower):
            found_keywords.add(skill)

    # Classify keywords as required or preferred
    required, preferred = _classify_keywords(found_keywords, text_lower)

    return {
        "required": sorted(list(required)),
        "preferred": sorted(list(preferred)),
        "all": sorted(list(found_keywords)),
    }


def _classify_keywords(keywords: Set[str], text: str) -> Tuple[Set[str], Set[str]]:
    """
    Classify keywords as required or preferred based on context.

    Classification logic:
    1. Check context around keyword for required/preferred indicators
    2. Check frequency - if keyword appears 3+ times, likely required
    3. Default: classify as preferred

    Args:
        keywords: Set of keywords to classify
        text: The full text (lowercase) to analyze

    Returns:
        Tuple of (required_keywords, preferred_keywords)
    """
    required: Set[str] = set()
    preferred: Set[str] = set()

    for keyword in keywords:
        # Get all synonyms for the keyword
        all_forms = get_all_synonyms(keyword)

        # Count total occurrences across all synonym forms
        total_count = 0
        closest_required_distance = float('inf')
        closest_preferred_distance = float('inf')

        for form in all_forms:
            # Count occurrences of this form
            pattern = r'\b' + re.escape(form) + r'\b'
            matches = re.finditer(pattern, text, re.IGNORECASE)

            for match in matches:
                total_count += 1
                keyword_position = match.start()

                # Get context BEFORE the keyword (preceding indicators matter most)
                # Also get a smaller window after for indicators on the same line
                context_before = _get_keyword_context(form, text, keyword_position, window_before=100, window_after=0)
                context_after = _get_keyword_context(form, text, keyword_position, window_before=0, window_after=20)

                # Look for indicators primarily in the text BEFORE the keyword
                # This prevents indicators from the next section from affecting current keyword
                for indicator in REQUIRED_INDICATORS:
                    # Check before context
                    if indicator in context_before:
                        # Find the rightmost occurrence (closest to keyword)
                        indicator_pos = context_before.rfind(indicator)
                        distance = len(context_before) - indicator_pos
                        closest_required_distance = min(closest_required_distance, distance)

                for indicator in PREFERRED_INDICATORS:
                    # Check before context
                    if indicator in context_before:
                        indicator_pos = context_before.rfind(indicator)
                        distance = len(context_before) - indicator_pos
                        closest_preferred_distance = min(closest_preferred_distance, distance)

        # Classification decision based on closest indicator
        if closest_preferred_distance < closest_required_distance:
            preferred.add(keyword)
        elif closest_required_distance < float('inf'):
            required.add(keyword)
        elif total_count >= 3:
            # High frequency suggests it's required
            required.add(keyword)
        else:
            # Default: classify as preferred
            preferred.add(keyword)

    return required, preferred


def _get_keyword_context(
    keyword: str,
    text: str,
    position: int,
    window_before: int = 50,
    window_after: int = 50
) -> str:
    """
    Get text context around keyword occurrence.

    Extracts a window of text before and after the keyword position
    to analyze contextual indicators.

    Args:
        keyword: The keyword to find
        text: The full text
        position: The position where keyword was found
        window_before: Number of characters before to include (default: 50)
        window_after: Number of characters after to include (default: 50)

    Returns:
        Context string around the keyword

    Examples:
        >>> text = "We require Python experience for this role"
        >>> context = _get_keyword_context("python", text, 11)
        >>> "require" in context.lower()
        True
    """
    start = max(0, position - window_before)
    end = min(len(text), position + len(keyword) + window_after)

    return text[start:end]


def match_with_synonyms(keyword: str, text: str) -> bool:
    """
    Check if keyword or any of its synonyms appear in text.

    Uses the SYNONYM_DATABASE to find all related terms and checks
    if any of them appear in the text. This enables intelligent matching
    where "kubernetes" can match "k8s" in the text.

    Args:
        keyword: The keyword to search for
        text: The text to search in (should be lowercase)

    Returns:
        True if keyword or any synonym is found, False otherwise

    Examples:
        >>> match_with_synonyms("python", "I know python")
        True

        >>> match_with_synonyms("kubernetes", "I use k8s daily")
        True

        >>> match_with_synonyms("python", "I know Java")
        False
    """
    # Get all forms of this keyword (including synonyms)
    all_forms = get_all_synonyms(keyword)

    # Check if any form appears in the text
    for form in all_forms:
        # Use word boundary regex to match whole words only
        # This prevents "python" from matching "pythonic" or "py" from matching "copy"
        pattern = r'\b' + re.escape(form) + r'\b'
        if re.search(pattern, text, re.IGNORECASE):
            return True

    return False
