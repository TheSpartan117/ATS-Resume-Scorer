#!/usr/bin/env python3
"""
Quick verification script for grammar improvements.
Tests key functionality without full pytest setup.
"""

from services.red_flags_validator import RedFlagsValidator
from services.parser import ResumeData


def create_resume(description):
    """Helper to create test resume"""
    return ResumeData(
        fileName="test.pdf",
        contact={"name": "Test User"},
        experience=[{
            "title": "Software Engineer",
            "company": "Tech Company",
            "startDate": "Jan 2020",
            "endDate": "Present",
            "description": description
        }],
        education=[],
        skills=["Python"],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
    )


def main():
    print("\n" + "="*70)
    print("Grammar Improvements Verification - Solution 1")
    print("="*70 + "\n")

    validator = RedFlagsValidator()

    # Test 1: Resume vocabulary (should NOT flag technical terms)
    print("Test 1: Resume vocabulary (technical terms should NOT be flagged)")
    print("-" * 70)
    resume = create_resume(
        "Developed applications using Python, JavaScript, React, Django, PostgreSQL, "
        "Docker, Kubernetes, AWS, Jenkins, GitLab, and Terraform."
    )
    result = validator.validate_grammar(resume)
    typos = [i for i in result if i['category'] == 'typo']
    print(f"Technical terms found as typos: {len(typos)}")
    if typos:
        for t in typos:
            print(f"  - {t['message']}")
    print(f"Result: {'✓ PASS' if len(typos) <= 1 else '✗ FAIL'}\n")

    # Test 2: Verb tense consistency
    print("Test 2: Verb tense consistency")
    print("-" * 70)
    resume = create_resume("Managed a team and developing new features")
    result = validator.validate_grammar(resume)
    grammar = [i for i in result if i['category'] == 'grammar' and 'tense' in i['message'].lower()]
    print(f"Found tense issues: {len(grammar)}")
    if grammar:
        for g in grammar:
            print(f"  - {g['message']}")
    print(f"Result: {'✓ PASS' if len(grammar) > 0 else '✗ FAIL'}\n")

    # Test 3: Plural with numbers
    print("Test 3: Plural with numbers")
    print("-" * 70)
    resume = create_resume("Software engineer with 5 year of experience")
    result = validator.validate_grammar(resume)
    grammar = [i for i in result if i['category'] == 'grammar' and 'year' in i['message'].lower()]
    print(f"Found plural issues: {len(grammar)}")
    if grammar:
        for g in grammar:
            print(f"  - {g['message']}")
    print(f"Result: {'✓ PASS' if len(grammar) > 0 else '✗ FAIL'}\n")

    # Test 4: Passive voice
    print("Test 4: Passive voice detection")
    print("-" * 70)
    resume = create_resume(
        "The project was completed by the team. The features were implemented by me."
    )
    result = validator.validate_grammar(resume)
    grammar = [i for i in result if i['category'] == 'grammar' and 'passive' in i['message'].lower()]
    print(f"Found passive voice: {len(grammar)}")
    if grammar:
        for g in grammar:
            print(f"  - {g['message']}")
    print(f"Result: {'✓ PASS' if len(grammar) > 0 else '✗ FAIL'}\n")

    # Test 5: Article errors
    print("Test 5: Article errors")
    print("-" * 70)
    resume = create_resume("I am engineer with experience")
    result = validator.validate_grammar(resume)
    grammar = [i for i in result if i['category'] == 'grammar' and 'article' in i['message'].lower()]
    print(f"Found article errors: {len(grammar)}")
    if grammar:
        for g in grammar:
            print(f"  - {g['message']}")
    print(f"Result: {'✓ PASS' if len(grammar) > 0 else '✗ FAIL'}\n")

    # Test 6: Preposition errors
    print("Test 6: Preposition errors")
    print("-" * 70)
    resume = create_resume("Worked in Google as a software engineer")
    result = validator.validate_grammar(resume)
    grammar = [i for i in result if i['category'] == 'grammar' and ('at' in i['message'].lower() or 'preposition' in i['message'].lower())]
    print(f"Found preposition errors: {len(grammar)}")
    if grammar:
        for g in grammar:
            print(f"  - {g['message']}")
    print(f"Result: {'✓ PASS' if len(grammar) > 0 else '✗ FAIL'}\n")

    # Test 7: Long sentences
    print("Test 7: Long sentence detection")
    print("-" * 70)
    long_text = " ".join(["I managed a team and worked on projects"] * 5)
    resume = create_resume(long_text)
    result = validator.validate_grammar(resume)
    grammar = [i for i in result if i['category'] == 'grammar' and 'long' in i['message'].lower()]
    print(f"Found long sentences: {len(grammar)}")
    if grammar:
        for g in grammar:
            print(f"  - {g['message']}")
    print(f"Result: {'✓ PASS' if len(grammar) > 0 else '✗ FAIL'}\n")

    # Test 8: Good grammar (no false positives)
    print("Test 8: Good grammar (minimal false positives)")
    print("-" * 70)
    resume = create_resume(
        "Led a team of 5 engineers in developing scalable microservices. "
        "Implemented CI/CD pipelines using Jenkins and Docker. "
        "Improved system performance by 40 percent through optimization."
    )
    result = validator.validate_grammar(resume)
    all_issues = [i for i in result if i['category'] in ['grammar', 'typo']]
    print(f"Total issues found: {len(all_issues)}")
    if all_issues:
        for i in all_issues:
            print(f"  - [{i['category']}] {i['message']}")
    print(f"Result: {'✓ PASS' if len(all_issues) <= 2 else '✗ FAIL'}\n")

    print("="*70)
    print("Verification complete!")
    print("="*70 + "\n")


if __name__ == '__main__':
    main()
