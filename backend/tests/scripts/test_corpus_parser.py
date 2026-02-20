"""Test corpus parsing functionality"""
import pytest
from pathlib import Path


def test_parse_resume_line():
    """Should parse resume sample line format"""
    from backend.scripts.corpus_parser import parse_resume_line

    sample = "C:\\path\\1.html#1:::Software Engineer;Python Developer:::Sample resume text here"

    result = parse_resume_line(sample)

    assert result['id'] == "C:\\path\\1.html#1"
    assert 'Software Engineer' in result['occupations']
    assert 'Python Developer' in result['occupations']
    assert result['text'] == "Sample resume text here"


def test_parse_resume_line_handles_malformed():
    """Should handle malformed lines gracefully"""
    from backend.scripts.corpus_parser import parse_resume_line

    malformed = "invalid format"

    result = parse_resume_line(malformed)

    assert result is None


def test_stream_resume_samples():
    """Should stream resumes without loading all into memory"""
    from backend.scripts.corpus_parser import stream_resume_samples

    # Create small test file
    test_file = Path('/tmp/test_resumes.txt')
    test_file.write_text(
        "1:::Engineer:::Resume 1\n"
        "2:::Manager:::Resume 2\n"
    )

    resumes = list(stream_resume_samples(test_file))

    assert len(resumes) == 2
    assert resumes[0]['id'] == '1'
    assert resumes[1]['occupations'] == ['Manager']

    # Cleanup
    test_file.unlink()


def test_extract_skills_from_corpus():
    """Should extract skills with frequencies from corpus"""
    from backend.scripts.corpus_parser import extract_skills_database

    # Create test file
    test_file = Path('/tmp/test_skills.txt')
    test_file.write_text(
        ":::::::\n"
        "1:::Software Engineer:::Resume with Python and Java\n"
        ":::::::\n"
        ":::::::\n"
        "2:::Data Scientist:::Resume with Python and SQL\n"
        ":::::::\n"
    )

    skills_db = extract_skills_database(test_file)

    assert 'python' in skills_db
    assert skills_db['python']['frequency'] == 2
    assert 'java' in skills_db
    assert skills_db['java']['frequency'] == 1

    # Cleanup
    test_file.unlink()
