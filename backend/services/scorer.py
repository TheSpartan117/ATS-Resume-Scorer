"""
Resume scoring engine that evaluates resumes based on ATS best practices.
"""
import re
from typing import Dict, List, Tuple
from backend.services.parser import ResumeData


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

    Scoring:
    - Action verbs usage: 5 points
    - Quantified achievements: 8 points
    - Low buzzword count: 5 points
    - No excessive repetition: 4 points
    - Optimal bullet length: 3 points
    """
    score = 0
    issues: List[Tuple[str, str]] = []

    # Get all text
    experience_text = " ".join([str(exp) for exp in resume.experience])
    all_text = experience_text + " " + " ".join([str(edu) for edu in resume.education])

    # Check for action verbs (5 points)
    action_verbs = ['led', 'managed', 'developed', 'created', 'implemented', 'designed',
                    'built', 'launched', 'improved', 'increased', 'decreased', 'achieved',
                    'established', 'optimized', 'streamlined', 'spearheaded']

    action_verb_count = sum(1 for verb in action_verbs if verb in all_text.lower())
    if action_verb_count >= 5:
        score += 5
    elif action_verb_count >= 3:
        score += 3
        issues.append(("suggestion", f"Use more action verbs (found {action_verb_count}, aim for 5+)"))
    else:
        score += 1
        issues.append(("warning", f"Few action verbs found ({action_verb_count}) - start bullets with strong action verbs"))

    # Check for quantified achievements (8 points)
    numbers_found = len(re.findall(r'\d+[%$,\d]*', all_text))
    if numbers_found >= 5:
        score += 8
    elif numbers_found >= 3:
        score += 5
        issues.append(("suggestion", f"Add more quantified achievements (found {numbers_found}, aim for 5+)"))
    elif numbers_found >= 1:
        score += 3
        issues.append(("warning", f"Few quantified achievements ({numbers_found}) - add numbers, percentages, dollar amounts"))
    else:
        issues.append(("critical", "No quantified achievements - add measurable results"))

    # Check buzzwords (5 points) - FEWER is better
    buzzwords = ['synergy', 'rockstar', 'ninja', 'guru', 'passionate', 'team player',
                 'think outside', 'go-getter', 'self-starter', 'results-driven']

    buzzword_count = sum(1 for word in buzzwords if word in all_text.lower())
    if buzzword_count == 0:
        score += 5
    elif buzzword_count <= 2:
        score += 3
        issues.append(("info", f"Minimize buzzwords (found {buzzword_count}) - use specific achievements instead"))
    else:
        score += 1
        issues.append(("warning", f"Too many buzzwords ({buzzword_count}) - replace with concrete achievements"))

    # Check repetition (4 points)
    words = all_text.lower().split()
    word_freq = {}
    for word in words:
        if len(word) > 4:  # Only check meaningful words
            word_freq[word] = word_freq.get(word, 0) + 1

    repeated_words = [word for word, count in word_freq.items() if count > 5]
    if len(repeated_words) == 0:
        score += 4
    elif len(repeated_words) <= 2:
        score += 2
        issues.append(("info", f"Some word repetition detected - vary your language"))
    else:
        score += 1
        issues.append(("warning", f"Excessive repetition of words: {', '.join(repeated_words[:3])}"))

    # Check bullet length (3 points) - check experience bullets if available
    if resume.experience:
        # Placeholder: assume bullets are in experience dicts
        score += 2  # Partial credit for having experience section
        issues.append(("info", "Bullet length analysis requires detailed parsing"))
    else:
        issues.append(("suggestion", "Add experience section with concise bullet points (50-150 characters each)"))

    return {"score": score, "issues": issues}


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

    Scoring:
    - Optimal word count for page count: 5 points
    - Good white space ratio: 5 points

    Args:
        resume: ResumeData object with parsed resume information

    Returns:
        Dict with "score" (int) and "issues" (List[Tuple[str, str]])
    """
    score = 0
    issues: List[Tuple[str, str]] = []

    page_count = resume.metadata.get("pageCount", 1)
    word_count = resume.metadata.get("wordCount", 0)

    # Word count for page count (5 points)
    if page_count == 1:
        if 400 <= word_count <= 600:
            score += 5
        elif 300 <= word_count < 400 or 600 < word_count <= 700:
            score += 3
            issues.append(("info", f"1-page resume with {word_count} words - ideal is 400-600"))
        else:
            score += 1
            if word_count < 300:
                issues.append(("warning", f"Too brief for 1 page ({word_count} words) - add more detail"))
            else:
                issues.append(("warning", f"Too dense for 1 page ({word_count} words) - consider 2 pages"))

    elif page_count == 2:
        if 600 <= word_count <= 900:
            score += 5
        elif 500 <= word_count < 600 or 900 < word_count <= 1100:
            score += 3
            issues.append(("info", f"2-page resume with {word_count} words - ideal is 600-900"))
        else:
            score += 1
            if word_count < 500:
                issues.append(("warning", f"Too brief for 2 pages ({word_count} words) - consolidate to 1 page"))
            else:
                issues.append(("warning", f"Too wordy for 2 pages ({word_count} words) - be more concise"))

    else:
        score += 2
        issues.append(("warning", f"{page_count} pages is non-standard - use 1-2 pages"))

    # White space / density (5 points)
    # Approximate: chars_per_page should be 2000-3500 for good density
    if word_count and page_count:
        chars_per_page = (word_count * 5) / page_count  # Assume avg 5 chars per word

        if 2000 <= chars_per_page <= 3500:
            score += 5
        elif 1500 <= chars_per_page < 2000 or 3500 < chars_per_page <= 4000:
            score += 3
            if chars_per_page < 2000:
                issues.append(("info", "Resume has good white space - could add more content"))
            else:
                issues.append(("info", "Resume is fairly dense - consider more white space"))
        else:
            score += 1
            if chars_per_page < 1500:
                issues.append(("warning", "Too much white space - add more content"))
            else:
                issues.append(("warning", "Too dense - needs more white space for readability"))

    return {"score": score, "issues": issues}


def score_industry_specific(resume: ResumeData, industry: str = "") -> Dict:
    """
    Score industry-specific requirements (20 points max).

    Scoring:
    - Tech: Technical skills (5), GitHub/portfolio (5), tech keywords (10)
    - Sales/Marketing: Metrics (10), client keywords (10)
    - Other: Generic professional scoring

    Args:
        resume: ResumeData object with parsed resume information
        industry: Industry to evaluate against

    Returns:
        Dict with "score" (int) and "issues" (List[Tuple[str, str]])
    """
    score = 0
    issues: List[Tuple[str, str]] = []

    if not industry:
        score = 10  # Default score
        issues.append(("suggestion", "Specify industry for tailored scoring"))
        return {"score": score, "issues": issues}

    industry_lower = industry.lower()

    # Get resume text
    all_text = " ".join([
        " ".join([str(exp) for exp in resume.experience]),
        " ".join(resume.skills)
    ]).lower()

    if "tech" in industry_lower or "software" in industry_lower or "engineer" in industry_lower:
        # Tech role scoring

        # Technical skills section (5 points)
        if resume.skills and len(resume.skills) >= 5:
            score += 5
        elif resume.skills and len(resume.skills) >= 3:
            score += 3
            issues.append(("suggestion", f"Add more technical skills (found {len(resume.skills)}, aim for 5+)"))
        else:
            score += 1
            issues.append(("warning", "Add technical skills section with relevant technologies"))

        # GitHub/portfolio link (5 points)
        if resume.contact.get("website") or "github" in all_text:
            score += 5
        else:
            issues.append(("warning", "Add GitHub profile or portfolio link for tech roles"))

        # Tech keywords (10 points)
        tech_keywords = ['python', 'javascript', 'java', 'react', 'node', 'aws', 'docker',
                         'kubernetes', 'sql', 'api', 'cloud', 'agile', 'git', 'ci/cd']

        tech_keyword_count = sum(1 for keyword in tech_keywords if keyword in all_text)
        if tech_keyword_count >= 5:
            score += 10
        elif tech_keyword_count >= 3:
            score += 6
            issues.append(("suggestion", f"Add more technical keywords (found {tech_keyword_count})"))
        else:
            score += 2
            issues.append(("warning", "Add relevant technical keywords and technologies"))

    elif "sales" in industry_lower or "marketing" in industry_lower:
        # Sales/Marketing role scoring

        # Metrics-heavy (10 points)
        metrics_patterns = [r'\d+%', r'\$\d+', r'\d+\s*million', r'\d+\s*clients',
                           r'revenue', r'growth', r'roi', r'\d+x']

        metrics_count = sum(len(re.findall(pattern, all_text)) for pattern in metrics_patterns)
        if metrics_count >= 5:
            score += 10
        elif metrics_count >= 3:
            score += 6
            issues.append(("suggestion", f"Add more quantified results (found {metrics_count}, aim for 5+)"))
        else:
            score += 2
            issues.append(("warning", "Sales/Marketing resumes need quantified achievements (revenue, growth %)"))

        # Client/relationship keywords (10 points)
        client_keywords = ['client', 'customer', 'relationship', 'stakeholder', 'partnership',
                          'negotiated', 'closed', 'pipeline', 'forecast', 'quota']

        client_keyword_count = sum(1 for keyword in client_keywords if keyword in all_text)
        if client_keyword_count >= 4:
            score += 10
        elif client_keyword_count >= 2:
            score += 6
            issues.append(("suggestion", "Add more client-facing and relationship keywords"))
        else:
            score += 2
            issues.append(("warning", "Emphasize client relationships and business development"))

    else:
        # Generic professional scoring
        score = 10
        issues.append(("info", f"Generic scoring applied for {industry} industry"))

    return {"score": score, "issues": issues}


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
