"""
Resume scoring engine that evaluates resumes based on ATS best practices.
"""
import re
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
    Score resume content quality (25 points max).

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
    Score keyword optimization for ATS (15 points max).

    Scoring:
    - With JD: Match percentage * 15 points (0-100% match)
    - With role: 10 points if key role keywords present
    - Without context: 10 points default, suggest adding JD

    Args:
        resume: ResumeData object with parsed resume information
        job_description: Optional job description to match against

    Returns:
        Dict with "score" (int) and "issues" (List[Tuple[str, str]])
    """
    score = 0
    issues: List[Tuple[str, str]] = []

    # Extract resume text (combine all text fields)
    resume_text = " ".join([
        resume.contact.get("name", ""),
        " ".join([str(exp) for exp in resume.experience]),
        " ".join([str(edu) for edu in resume.education]),
        " ".join(resume.skills)
    ]).lower()

    if job_description:
        # Extract keywords from JD (simple: words > 4 chars, not stopwords)
        jd_keywords = extract_important_keywords(job_description)

        # Count matches
        matches = sum(1 for keyword in jd_keywords if keyword.lower() in resume_text)
        match_percentage = (matches / len(jd_keywords)) * 100 if jd_keywords else 0

        score = int((match_percentage / 100) * 15)

        if match_percentage < 40:
            issues.append(("critical", f"Low keyword match: {match_percentage:.0f}% - add key terms from job description"))
        elif match_percentage < 60:
            issues.append(("warning", f"Moderate keyword match: {match_percentage:.0f}% - consider adding more relevant terms"))

        # Identify missing keywords
        missing = [kw for kw in jd_keywords[:5] if kw.lower() not in resume_text]
        if missing:
            issues.append(("suggestion", f"Missing key terms: {', '.join(missing)}"))
    else:
        # No JD provided - give default score
        score = 10
        issues.append(("suggestion", "Provide job description for better keyword matching"))

    return {"score": score, "issues": issues}


def extract_important_keywords(text: str) -> List[str]:
    """Extract important keywords from text (simple implementation)"""
    # Common stopwords to exclude
    stopwords = set(['the', 'and', 'for', 'with', 'this', 'that', 'from', 'have', 'will', 'your', 'they', 'been', 'their'])

    # Split and filter
    words = re.findall(r'\b\w{4,}\b', text.lower())
    keywords = [w for w in words if w not in stopwords]

    # Return unique keywords
    return list(set(keywords))[:50]  # Limit to 50 keywords


def score_length_density(resume: ResumeData) -> Dict:
    """
    Score resume length and content density (10 points max).

    TODO: Implement length and density scoring based on:
    - Optimal length (1-2 pages)
    - Content density (text vs whitespace ratio)
    - Section balance
    - Conciseness metrics

    Args:
        resume: ResumeData object with parsed resume information

    Returns:
        Dict with "score" (int) and "issues" (List[Tuple[str, str]])
    """
    # Placeholder implementation
    return {
        "score": 0,
        "issues": [("info", "Length and density scoring not yet implemented")]
    }


def score_industry_specific(resume: ResumeData, industry: str = "") -> Dict:
    """
    Score industry-specific requirements (20 points max).

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
    - Content quality: 25 points
    - Keywords: 15 points
    - Length & Density: 10 points
    - Industry-specific: 20 points

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
    length_density_result = score_length_density(resume)
    industry_result = score_industry_specific(resume, industry)

    # Calculate total score
    total_score = (
        contact_result["score"] +
        formatting_result["score"] +
        content_result["score"] +
        keywords_result["score"] +
        length_density_result["score"] +
        industry_result["score"]
    )

    # Aggregate all issues
    all_issues = (
        contact_result["issues"] +
        formatting_result["issues"] +
        content_result["issues"] +
        keywords_result["issues"] +
        length_density_result["issues"] +
        industry_result["issues"]
    )

    # Categorize issues by severity
    critical_issues = [issue for issue in all_issues if issue[0] == "critical"]
    warnings = [issue for issue in all_issues if issue[0] == "warning"]
    suggestions = [issue for issue in all_issues if issue[0] == "suggestion"]
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
                "maxScore": 25,
                "issues": content_result["issues"]
            },
            "keywords": {
                "score": keywords_result["score"],
                "maxScore": 15,
                "issues": keywords_result["issues"]
            },
            "lengthDensity": {
                "score": length_density_result["score"],
                "maxScore": 10,
                "issues": length_density_result["issues"]
            },
            "industrySpecific": {
                "score": industry_result["score"],
                "maxScore": 20,
                "issues": industry_result["issues"]
            }
        },
        "issues": {
            "critical": critical_issues,
            "warnings": warnings,
            "suggestions": suggestions,
            "info": info
        }
    }
