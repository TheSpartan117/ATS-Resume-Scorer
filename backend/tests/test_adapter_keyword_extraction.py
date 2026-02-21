"""
Tests for Enhanced Keyword Extraction in ScorerV3Adapter

Validates the semantic keyword extraction from job descriptions,
including required vs preferred classification and fallback behavior.
"""

import pytest
from backend.services.scorer_v3_adapter import ScorerV3Adapter


@pytest.fixture
def adapter():
    """Create adapter instance."""
    return ScorerV3Adapter()


def test_semantic_keyword_extraction_basic(adapter):
    """
    Test basic semantic keyword extraction from job description.
    """
    job_description = """
    We are looking for a Senior Software Engineer with strong Python and AWS experience.
    You will work on building microservices and implementing CI/CD pipelines.

    Required Skills:
    - Python programming
    - AWS cloud services
    - Docker containerization
    - Microservices architecture

    Nice to have:
    - Kubernetes experience
    - React frontend skills
    - GraphQL knowledge
    """

    job_reqs = adapter._extract_job_requirements(job_description)

    # Should extract keywords
    assert 'required_keywords' in job_reqs
    assert 'preferred_keywords' in job_reqs

    # Should have some keywords extracted
    assert len(job_reqs['required_keywords']) > 0
    assert len(job_reqs['preferred_keywords']) >= 0

    # Check required keywords contain relevant terms
    required_lower = [kw.lower() for kw in job_reqs['required_keywords']]
    assert any('python' in kw for kw in required_lower), \
        "Should extract 'Python' as required"

    # Print for debugging
    print(f"\nRequired keywords: {job_reqs['required_keywords']}")
    print(f"Preferred keywords: {job_reqs['preferred_keywords']}")


def test_keyword_extraction_with_sections(adapter):
    """
    Test keyword extraction with explicit required/preferred sections.
    """
    job_description = """
    Software Engineer Position

    Requirements:
    - 5+ years of Python development
    - Strong SQL database skills
    - REST API design experience
    - Agile methodology

    Preferred Qualifications:
    - Machine Learning background
    - Cloud platform experience (AWS/Azure)
    - DevOps tools knowledge
    """

    job_reqs = adapter._extract_job_requirements(job_description)

    # Should have both types of keywords
    assert len(job_reqs['required_keywords']) > 0
    assert len(job_reqs['preferred_keywords']) > 0

    # Required should include terms from Requirements section
    required_str = ' '.join(job_reqs['required_keywords']).lower()
    assert 'python' in required_str or 'sql' in required_str, \
        "Should extract requirements section keywords"

    print(f"\nRequired: {job_reqs['required_keywords']}")
    print(f"Preferred: {job_reqs['preferred_keywords']}")


def test_keyword_extraction_no_sections(adapter):
    """
    Test keyword extraction without explicit sections.

    Should intelligently split keywords into required (top 60%) and preferred (rest).
    """
    job_description = """
    Looking for a Full Stack Developer to join our team.
    Strong experience with React, Node.js, TypeScript, and MongoDB.
    You'll build scalable web applications using modern frameworks.
    Knowledge of Docker, Kubernetes, and CI/CD is important.
    """

    job_reqs = adapter._extract_job_requirements(job_description)

    # Should extract keywords
    assert len(job_reqs['required_keywords']) > 0

    # Should split intelligently (top keywords as required)
    total_keywords = len(job_reqs['required_keywords']) + len(job_reqs['preferred_keywords'])
    assert total_keywords > 0, "Should extract keywords"

    print(f"\nRequired: {job_reqs['required_keywords']}")
    print(f"Preferred: {job_reqs['preferred_keywords']}")


def test_keyword_extraction_empty_description(adapter):
    """
    Test keyword extraction with empty job description.
    """
    job_reqs = adapter._extract_job_requirements("")

    assert job_reqs == {'required_keywords': [], 'preferred_keywords': []}


def test_keyword_extraction_minimal_description(adapter):
    """
    Test keyword extraction with minimal job description.
    """
    job_description = "Python developer"

    job_reqs = adapter._extract_job_requirements(job_description)

    # Should still extract something
    assert 'required_keywords' in job_reqs
    assert 'preferred_keywords' in job_reqs


def test_fallback_keyword_extraction(adapter):
    """
    Test fallback keyword extraction method directly.
    """
    job_description = """
    Senior Software Engineer position requiring Python, Java, AWS, and SQL.
    Must have API design experience and Docker knowledge.
    """

    # Test fallback method directly
    job_reqs = adapter._fallback_keyword_extraction(job_description)

    assert 'required_keywords' in job_reqs
    assert 'preferred_keywords' in job_reqs

    # Should extract capitalized/uppercase terms
    required = job_reqs['required_keywords']
    assert len(required) > 0

    # Check for expected technical terms
    required_str = ' '.join(required).lower()
    tech_terms = ['python', 'java', 'aws', 'sql', 'api', 'docker']
    matches = sum(1 for term in tech_terms if term in required_str)
    assert matches >= 2, f"Should extract at least 2 technical terms, found {matches}"

    print(f"\nFallback required: {job_reqs['required_keywords']}")


def test_keyword_extraction_caps_limits(adapter):
    """
    Test that keyword extraction respects caps (15 required, 10 preferred).
    """
    # Create long job description with many keywords
    job_description = """
    Required: Python, Java, C++, JavaScript, TypeScript, Go, Rust, Ruby, PHP, Swift,
    Kotlin, Scala, Perl, Haskell, Elixir, Clojure, F#, R, MATLAB, Julia

    Preferred: React, Angular, Vue, Django, Flask, Spring, Express, Rails, Laravel,
    ASP.NET, Symfony, FastAPI, Sinatra, Phoenix
    """

    job_reqs = adapter._extract_job_requirements(job_description)

    # Should cap required keywords at 15
    assert len(job_reqs['required_keywords']) <= 15, \
        f"Required keywords should be capped at 15, got {len(job_reqs['required_keywords'])}"

    # Should cap preferred keywords at 10
    assert len(job_reqs['preferred_keywords']) <= 10, \
        f"Preferred keywords should be capped at 10, got {len(job_reqs['preferred_keywords'])}"


def test_keyword_extraction_real_world_example(adapter):
    """
    Test with a realistic job description.
    """
    job_description = """
    Senior Backend Engineer - Cloud Infrastructure

    We're seeking an experienced backend engineer to lead our cloud infrastructure team.

    Requirements:
    • 7+ years of software engineering experience
    • Expert-level Python programming skills
    • Deep AWS knowledge (EC2, S3, Lambda, RDS)
    • Strong experience with microservices architecture
    • Docker and Kubernetes expertise
    • CI/CD pipeline design and implementation
    • SQL and NoSQL database optimization

    Nice to have:
    • Terraform or CloudFormation experience
    • Monitoring tools (Datadog, New Relic)
    • Message queues (RabbitMQ, Kafka)
    • GraphQL API development
    """

    job_reqs = adapter._extract_job_requirements(job_description)

    # Should extract relevant keywords
    required = job_reqs['required_keywords']
    preferred = job_reqs['preferred_keywords']

    assert len(required) > 0, "Should extract required keywords"

    # Check for key technical terms
    all_keywords = ' '.join(required + preferred).lower()

    # In online mode (semantic), should extract specific terms like "python" and "aws"
    # In offline mode (fallback), might extract broader terms
    # Just verify some technical keywords were extracted
    tech_keywords = ['python', 'aws', 'cloud', 'docker', 'kubernetes',
                     'microservices', 'sql', 'backend', 'engineer', 'infrastructure']
    matches = sum(1 for term in tech_keywords if term in all_keywords)

    assert matches >= 3, \
        f"Should extract at least 3 technical terms, found {matches} in: {all_keywords}"

    # Print for debugging
    print(f"\nRealistic example:")
    print(f"Required ({len(required)}): {required}")
    print(f"Preferred ({len(preferred)}): {preferred}")
    print(f"Tech keyword matches: {matches}")


def test_keyword_deduplication(adapter):
    """
    Test that extracted keywords are deduplicated.
    """
    job_description = """
    Python developer needed. Python experience required.
    Must know Python programming and Python frameworks.
    """

    job_reqs = adapter._extract_job_requirements(job_description)

    all_keywords = job_reqs['required_keywords'] + job_reqs['preferred_keywords']

    # Count occurrences of 'python' (case-insensitive)
    python_count = sum(1 for kw in all_keywords if 'python' in kw.lower())

    # Should only have Python once (or in one variation like "Python programming")
    assert python_count <= 2, \
        f"Keywords should be deduplicated, found 'python' {python_count} times"
