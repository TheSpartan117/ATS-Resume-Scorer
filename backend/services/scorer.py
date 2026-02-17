"""
Resume scoring engine that evaluates resumes based on ATS best practices.
"""
from typing import Dict, List, Tuple
from services.parser import ResumeData


def score_contact_info(resume: ResumeData) -> Dict:
    """
    Score contact information completeness (10 points max).

    Scoring breakdown:
    - Name: 2 points
    - Email: 2 points
    - Phone: 2 points
    - Location: 2 points
    - LinkedIn/Website: 2 points

    Args:
        resume: ResumeData object with parsed resume information

    Returns:
        Dict with "score" (int) and "issues" (List[Tuple[str, str]])
        where each issue is (severity, message)
    """
    score = 0
    issues: List[Tuple[str, str]] = []
    contact = resume.contact

    # Name (2 points)
    if contact.get("name"):
        score += 2
    else:
        issues.append(("critical", "Missing: Full name"))

    # Email (2 points)
    if contact.get("email"):
        score += 2
    else:
        issues.append(("critical", "Missing: Email address"))

    # Phone (2 points)
    if contact.get("phone"):
        score += 2
    else:
        issues.append(("warning", "Missing: Phone number"))

    # Location (2 points)
    if contact.get("location"):
        score += 2
    else:
        issues.append(("suggestion", "Add location (City, State)"))

    # LinkedIn or Website (2 points)
    if contact.get("linkedin") or contact.get("website"):
        score += 2
    else:
        issues.append(("suggestion", "Add LinkedIn profile or portfolio"))

    return {
        "score": score,
        "issues": issues
    }


def score_formatting(resume: ResumeData) -> Dict:
    """
    Score resume formatting and structure (20 points max).

    Scoring breakdown:
    - Appropriate length (1-2 pages): 8 points
    - No photo (ATS-friendly): 4 points
    - Clean file format (PDF preferred): 4 points
    - Reasonable word count: 4 points

    Args:
        resume: ResumeData object with parsed resume information

    Returns:
        Dict with "score" (int) and "issues" (List[Tuple[str, str]])
    """
    score = 0
    issues: List[Tuple[str, str]] = []
    metadata = resume.metadata

    # Page count (8 points)
    page_count = metadata.get("pageCount", 0)
    if page_count == 1 or page_count == 2:
        score += 8
    elif page_count == 3:
        score += 4
        issues.append(("warning", "Resume is 3 pages - consider condensing to 2 pages"))
    elif page_count > 3:
        score += 2
        issues.append(("warning", f"Resume is {page_count} pages - too long, should be 1-2 pages"))
    else:
        issues.append(("critical", "Unable to determine page count"))

    # Photo check (4 points)
    if not metadata.get("hasPhoto", False):
        score += 4
    else:
        issues.append(("warning", "Resume contains a photo - remove for ATS compatibility"))

    # File format (4 points)
    file_format = metadata.get("fileFormat", "").lower()
    if file_format == "pdf":
        score += 4
    elif file_format == "docx":
        score += 3
        issues.append(("info", "PDF format is preferred over DOCX for ATS systems"))
    else:
        score += 1
        issues.append(("warning", f"Unusual file format: {file_format}"))

    # Word count (4 points)
    word_count = metadata.get("wordCount", 0)
    if 300 <= word_count <= 800:
        score += 4
    elif 200 <= word_count < 300 or 800 < word_count <= 1000:
        score += 3
        if word_count < 300:
            issues.append(("info", f"Resume is brief ({word_count} words) - consider adding more detail"))
        else:
            issues.append(("info", f"Resume is lengthy ({word_count} words) - consider being more concise"))
    elif word_count < 200:
        score += 1
        issues.append(("warning", f"Resume is too brief ({word_count} words)"))
    elif word_count > 1000:
        score += 2
        issues.append(("warning", f"Resume is too lengthy ({word_count} words)"))
    else:
        issues.append(("critical", "Unable to determine word count"))

    return {
        "score": score,
        "issues": issues
    }


def score_content(resume: ResumeData) -> Dict:
    """
    Score resume content quality (30 points max).

    TODO: Implement content scoring based on:
    - Experience section completeness
    - Education section
    - Quantifiable achievements
    - Action verbs usage

    Args:
        resume: ResumeData object with parsed resume information

    Returns:
        Dict with "score" (int) and "issues" (List[Tuple[str, str]])
    """
    # Placeholder implementation
    return {
        "score": 0,
        "issues": [("info", "Content scoring not yet implemented")]
    }


def score_keywords(resume: ResumeData, job_description: str = "") -> Dict:
    """
    Score keyword optimization for ATS (20 points max).

    TODO: Implement keyword matching against job description:
    - Extract key skills and requirements from job description
    - Match against resume content
    - Check for industry-standard terminology

    Args:
        resume: ResumeData object with parsed resume information
        job_description: Optional job description to match against

    Returns:
        Dict with "score" (int) and "issues" (List[Tuple[str, str]])
    """
    # Placeholder implementation
    return {
        "score": 0,
        "issues": [("info", "Keyword scoring not yet implemented")]
    }


def score_skills(resume: ResumeData) -> Dict:
    """
    Score skills section quality (10 points max).

    TODO: Implement skills scoring based on:
    - Presence of skills section
    - Number of relevant skills
    - Categorization of skills

    Args:
        resume: ResumeData object with parsed resume information

    Returns:
        Dict with "score" (int) and "issues" (List[Tuple[str, str]])
    """
    # Placeholder implementation
    return {
        "score": 0,
        "issues": [("info", "Skills scoring not yet implemented")]
    }


def score_industry_specific(resume: ResumeData, industry: str = "") -> Dict:
    """
    Score industry-specific requirements (10 points max).

    TODO: Implement industry-specific scoring:
    - Tech: GitHub, portfolio, technical skills
    - Finance: Certifications, quantitative achievements
    - Healthcare: Licenses, certifications

    Args:
        resume: ResumeData object with parsed resume information
        industry: Industry to evaluate against

    Returns:
        Dict with "score" (int) and "issues" (List[Tuple[str, str]])
    """
    # Placeholder implementation
    return {
        "score": 0,
        "issues": [("info", "Industry-specific scoring not yet implemented")]
    }


def calculate_overall_score(resume: ResumeData, job_description: str = "", industry: str = "") -> Dict:
    """
    Calculate overall ATS score by aggregating all scoring components.

    Total possible score: 100 points
    - Contact info: 10 points
    - Formatting: 20 points
    - Content quality: 30 points
    - Keywords: 20 points
    - Skills: 10 points
    - Industry-specific: 10 points

    Args:
        resume: ResumeData object with parsed resume information
        job_description: Optional job description for keyword matching
        industry: Optional industry for industry-specific scoring

    Returns:
        Dict with overall score, breakdown, and all issues
    """
    # Score each component
    contact_result = score_contact_info(resume)
    formatting_result = score_formatting(resume)
    content_result = score_content(resume)
    keywords_result = score_keywords(resume, job_description)
    skills_result = score_skills(resume)
    industry_result = score_industry_specific(resume, industry)

    # Calculate total score
    total_score = (
        contact_result["score"] +
        formatting_result["score"] +
        content_result["score"] +
        keywords_result["score"] +
        skills_result["score"] +
        industry_result["score"]
    )

    # Aggregate all issues
    all_issues = (
        contact_result["issues"] +
        formatting_result["issues"] +
        content_result["issues"] +
        keywords_result["issues"] +
        skills_result["issues"] +
        industry_result["issues"]
    )

    # Categorize issues by severity
    critical_issues = [issue for issue in all_issues if issue[0] == "critical"]
    warnings = [issue for issue in all_issues if issue[0] == "warning"]
    info = [issue for issue in all_issues if issue[0] == "info"]

    return {
        "overallScore": total_score,
        "maxScore": 100,
        "breakdown": {
            "contactInfo": {
                "score": contact_result["score"],
                "maxScore": 10,
                "issues": contact_result["issues"]
            },
            "formatting": {
                "score": formatting_result["score"],
                "maxScore": 20,
                "issues": formatting_result["issues"]
            },
            "content": {
                "score": content_result["score"],
                "maxScore": 30,
                "issues": content_result["issues"]
            },
            "keywords": {
                "score": keywords_result["score"],
                "maxScore": 20,
                "issues": keywords_result["issues"]
            },
            "skills": {
                "score": skills_result["score"],
                "maxScore": 10,
                "issues": skills_result["issues"]
            },
            "industrySpecific": {
                "score": industry_result["score"],
                "maxScore": 10,
                "issues": industry_result["issues"]
            }
        },
        "issues": {
            "critical": critical_issues,
            "warnings": warnings,
            "info": info
        }
    }
