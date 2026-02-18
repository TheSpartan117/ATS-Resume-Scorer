"""
Resume scoring engine that evaluates resumes based on ATS best practices.
"""
import re
from typing import Dict, List, Tuple, Optional
from backend.services.parser import ResumeData
from backend.services.role_taxonomy import get_role_scoring_data, ExperienceLevel


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


def score_content(resume: ResumeData, role_id: str = "", level: str = "") -> Dict:
    """
    Score resume content quality based on CV writing standards (25 points max).

    Scoring breakdown:
    - Action verbs at bullet start: 6 points
    - Quantified achievements: 6 points
    - Proper sentence structure: 5 points
    - No passive voice: 3 points
    - Professional language: 3 points
    - Low buzzword count: 2 points

    Args:
        resume: ResumeData object with parsed resume information
        role_id: Optional role identifier for role-specific action verbs
        level: Optional experience level for role-specific action verbs
    """
    score = 0
    issues: List[Tuple[str, str]] = []

    # Get role-specific action verbs if role provided
    if role_id and level:
        try:
            level_enum = ExperienceLevel(level)
            role_data = get_role_scoring_data(role_id, level_enum)
            if role_data and role_data.get('action_verbs'):
                strong_action_verbs = role_data['action_verbs']
            else:
                # Fallback to generic action verbs
                strong_action_verbs = _get_generic_action_verbs()
        except (ValueError, KeyError):
            # Fallback to generic action verbs
            strong_action_verbs = _get_generic_action_verbs()
    else:
        # Use generic action verbs
        strong_action_verbs = _get_generic_action_verbs()

    # Weak/passive constructions to avoid
    passive_indicators = [
        'was responsible for', 'responsible for', 'duties included', 'worked on',
        'helped with', 'assisted with', 'involved in', 'tasked with', 'participated in'
    ]

    # First-person pronouns (should not appear in CV)
    first_person_pronouns = ['i ', ' i ', 'my ', ' my ', 'me ', ' me ', 'we ', ' we ', 'our ', ' our ']

    # Get experience text for detailed analysis
    experience_bullets = []
    for exp in resume.experience:
        if isinstance(exp, dict) and 'description' in exp:
            # Split description into bullet points
            desc = exp.get('description', '')
            bullets = [line.strip() for line in desc.split('\n') if line.strip() and line.strip().startswith('-')]
            experience_bullets.extend(bullets)

    all_experience_text = " ".join([str(exp) for exp in resume.experience])
    all_text = all_experience_text + " " + " ".join([str(edu) for edu in resume.education])

    # 1. ACTION VERBS AT BULLET START (6 points)
    bullets_with_action_verbs = 0
    total_bullets = len(experience_bullets)

    if total_bullets > 0:
        for bullet in experience_bullets:
            # Remove leading dash/bullet marker
            bullet_text = bullet.lstrip('-•*▪ ').strip()
            first_word = bullet_text.split()[0].lower() if bullet_text else ''

            if first_word in strong_action_verbs:
                bullets_with_action_verbs += 1

        action_verb_percentage = (bullets_with_action_verbs / total_bullets) * 100

        if action_verb_percentage >= 80:
            score += 6
        elif action_verb_percentage >= 60:
            score += 4
            issues.append(("suggestion", f"{bullets_with_action_verbs}/{total_bullets} bullets start with action verbs - aim for 80%+"))
        elif action_verb_percentage >= 40:
            score += 2
            issues.append(("warning", f"Only {bullets_with_action_verbs}/{total_bullets} bullets start with action verbs - start each with: Led, Developed, Achieved, etc."))
        else:
            score += 1
            issues.append(("critical", f"Only {bullets_with_action_verbs}/{total_bullets} bullets start with strong action verbs - each bullet should start with an action verb"))
    else:
        # Check for action verbs in general text if no bullets detected
        action_verb_count = sum(1 for verb in strong_action_verbs if verb in all_text.lower())
        if action_verb_count >= 8:
            score += 4
        elif action_verb_count >= 5:
            score += 3
            issues.append(("suggestion", f"Use more action verbs (found {action_verb_count}, aim for 8+)"))
        else:
            score += 1
            issues.append(("warning", f"Few action verbs found ({action_verb_count}) - use bullet points starting with action verbs"))

    # 2. QUANTIFIED ACHIEVEMENTS (6 points)
    numbers_found = len(re.findall(r'\d+[%$,\d]*', all_text))
    bullets_with_numbers = sum(1 for bullet in experience_bullets if re.search(r'\d+', bullet))

    if total_bullets > 0:
        quantified_percentage = (bullets_with_numbers / total_bullets) * 100
        if quantified_percentage >= 60:
            score += 6
        elif quantified_percentage >= 40:
            score += 4
            issues.append(("suggestion", f"{bullets_with_numbers}/{total_bullets} bullets include numbers - aim to quantify 60%+ of achievements"))
        elif quantified_percentage >= 20:
            score += 2
            issues.append(("warning", f"Only {bullets_with_numbers}/{total_bullets} bullets include numbers - add metrics (%, $, numbers, timeframes)"))
        else:
            score += 1
            issues.append(("critical", f"Only {bullets_with_numbers}/{total_bullets} bullets quantified - add measurable results: revenue, percentages, team size, timeframes"))
    else:
        if numbers_found >= 5:
            score += 4
        elif numbers_found >= 3:
            score += 3
            issues.append(("suggestion", f"Add more metrics (found {numbers_found}, aim for 5+)"))
        elif numbers_found >= 1:
            score += 1
            issues.append(("warning", f"Few metrics ({numbers_found}) - add percentages, dollar amounts, quantities"))
        else:
            issues.append(("critical", "No quantified achievements - add measurable results"))

    # 3. PROPER SENTENCE STRUCTURE (5 points)
    structure_score = 5
    structure_issues = 0

    # Check bullet length (should be 50-150 characters for readability)
    long_bullets = [b for b in experience_bullets if len(b) > 150]
    short_bullets = [b for b in experience_bullets if len(b) < 30]

    if len(long_bullets) > total_bullets * 0.3:
        structure_score -= 2
        structure_issues += 1
        issues.append(("warning", f"{len(long_bullets)} bullets too long (>150 chars) - keep bullets concise and scannable"))

    if len(short_bullets) > total_bullets * 0.3:
        structure_score -= 1
        structure_issues += 1
        issues.append(("info", f"{len(short_bullets)} bullets very short (<30 chars) - add more detail to showcase impact"))

    # Check for run-on sentences (multiple clauses)
    bullets_with_multiple_clauses = [b for b in experience_bullets if b.count(',') > 2 or b.count(' and ') > 1]
    if len(bullets_with_multiple_clauses) > total_bullets * 0.4:
        structure_score -= 1
        structure_issues += 1
        issues.append(("suggestion", f"{len(bullets_with_multiple_clauses)} bullets have multiple clauses - split complex bullets into separate points"))

    # Check for proper formatting (bullets should start with dash/bullet)
    if total_bullets == 0 and len(resume.experience) > 0:
        structure_score -= 2
        issues.append(("warning", "Use bullet points (•, -, *) to list achievements - avoid paragraph format"))

    score += max(0, structure_score)

    # 4. NO PASSIVE VOICE (3 points)
    passive_count = sum(1 for phrase in passive_indicators if phrase in all_text.lower())

    if passive_count == 0:
        score += 3
    elif passive_count <= 2:
        score += 1
        issues.append(("suggestion", f"Avoid passive phrases like 'was responsible for', 'worked on' - use active voice: 'Led', 'Developed'"))
    else:
        issues.append(("warning", f"Found {passive_count} passive constructions - replace with active voice (Led team vs. Was responsible for leading team)"))

    # 5. PROFESSIONAL LANGUAGE (3 points)
    professional_score = 3

    # Check for first-person pronouns
    first_person_count = sum(1 for pronoun in first_person_pronouns if pronoun in all_text.lower())
    if first_person_count > 0:
        professional_score -= 2
        issues.append(("critical", f"Remove first-person pronouns (I, my, we, our) - use third-person: 'Led team' not 'I led team'"))

    # Check for informal language
    informal_words = ['stuff', 'things', 'got', 'bunch', 'lots', 'tons', 'really', 'very', 'pretty much']
    informal_count = sum(1 for word in informal_words if word in all_text.lower())
    if informal_count > 0:
        professional_score -= 1
        issues.append(("warning", f"Avoid informal language - use professional terminology"))

    score += max(0, professional_score)

    # 6. LOW BUZZWORD COUNT (2 points)
    buzzwords = ['synergy', 'rockstar', 'ninja', 'guru', 'passionate', 'team player',
                 'think outside', 'go-getter', 'self-starter', 'results-driven', 'hard worker',
                 'detail-oriented', 'people person', 'thought leader']

    buzzword_count = sum(1 for word in buzzwords if word in all_text.lower())
    if buzzword_count == 0:
        score += 2
    elif buzzword_count <= 2:
        score += 1
        issues.append(("info", f"Minimize buzzwords (found {buzzword_count}) - use specific achievements instead"))
    else:
        issues.append(("warning", f"Too many buzzwords ({buzzword_count}) - replace with concrete, measurable achievements"))

    return {"score": score, "issues": issues}


def score_keywords(resume: ResumeData, job_description: str = "", role_id: str = "", level: str = "") -> Dict:
    """
    Score keyword optimization for ATS (15 points max).

    Scoring:
    - With JD: Match percentage * 15 points (0-100% match)
    - With role: Match percentage against typical role keywords
    - Without context: 10 points default, suggest adding JD or role

    Args:
        resume: ResumeData object with parsed resume information
        job_description: Optional job description to match against
        role_id: Optional role identifier for role-specific keywords
        level: Optional experience level for role-specific keywords

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
    elif role_id and level:
        # Use role-specific typical keywords
        try:
            level_enum = ExperienceLevel(level)
            role_data = get_role_scoring_data(role_id, level_enum)

            if role_data and role_data.get('typical_keywords'):
                typical_keywords = role_data['typical_keywords']

                # Count matches
                matches = sum(1 for keyword in typical_keywords if keyword.lower() in resume_text)
                match_percentage = (matches / len(typical_keywords)) * 100 if typical_keywords else 0

                score = int((match_percentage / 100) * 15)

                if match_percentage < 40:
                    issues.append(("warning", f"Low role keyword match: {match_percentage:.0f}% - add typical {level} {role_data['name']} keywords"))
                elif match_percentage < 60:
                    issues.append(("suggestion", f"Moderate keyword match: {match_percentage:.0f}% - consider adding more role-relevant terms"))

                # Identify missing keywords
                missing = [kw for kw in typical_keywords[:5] if kw.lower() not in resume_text]
                if missing:
                    issues.append(("suggestion", f"Missing key terms for {role_data['name']}: {', '.join(missing)}"))
            else:
                # Role data found but no keywords
                score = 10
                issues.append(("info", "Using generic scoring - provide job description for better matching"))
        except (ValueError, KeyError):
            # Invalid role or level
            score = 10
            issues.append(("info", "Invalid role/level - provide job description for better matching"))
    else:
        # No JD or role provided - give default score
        score = 10
        issues.append(("suggestion", "Provide job description or select role for better keyword matching"))

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


def _get_generic_action_verbs() -> List[str]:
    """
    Get generic action verb list for resume content scoring.
    Used as fallback when no role-specific verbs are available.
    """
    return [
        # Leadership & Management
        'led', 'managed', 'directed', 'supervised', 'coordinated', 'orchestrated', 'spearheaded',
        'oversaw', 'mentored', 'trained', 'guided', 'delegated', 'executed',
        # Creation & Development
        'developed', 'created', 'designed', 'built', 'established', 'launched', 'implemented',
        'engineered', 'architected', 'crafted', 'authored', 'pioneered', 'initiated',
        # Improvement & Optimization
        'improved', 'optimized', 'enhanced', 'streamlined', 'refined', 'transformed',
        'modernized', 'revitalized', 'upgraded', 'accelerated', 'strengthened',
        # Achievement & Results
        'achieved', 'delivered', 'exceeded', 'increased', 'decreased', 'reduced', 'generated',
        'drove', 'boosted', 'maximized', 'minimized', 'secured', 'attained',
        # Analysis & Strategy
        'analyzed', 'evaluated', 'assessed', 'researched', 'identified', 'diagnosed',
        'forecasted', 'strategized', 'planned', 'formulated',
        # Communication & Collaboration
        'collaborated', 'partnered', 'presented', 'communicated', 'negotiated', 'facilitated',
        'advocated', 'consulted', 'advised', 'liaised'
    ]


def score_role_specific(resume: ResumeData, role_id: str = "", level: str = "") -> Dict:
    """
    Score role-specific requirements (20 points max).

    Scoring based on role and experience level:
    - Required skills present: 5 points
    - Level-appropriate keywords: 10 points
    - Preferred sections: 5 points

    Args:
        resume: ResumeData object with parsed resume information
        role_id: Role identifier (e.g., "software_engineer", "product_manager")
        level: Experience level ("entry", "mid", "senior", "lead", "executive")

    Returns:
        Dict with "score" (int) and "issues" (List[Tuple[str, str]])
    """
    score = 0
    issues: List[Tuple[str, str]] = []

    if not role_id or not level:
        score = 10  # Default score
        issues.append(("suggestion", "Select role and experience level for tailored scoring"))
        return {"score": score, "issues": issues}

    # Get role criteria
    try:
        level_enum = ExperienceLevel(level)
        role_data = get_role_scoring_data(role_id, level_enum)
    except (ValueError, KeyError):
        score = 10
        issues.append(("info", "Invalid role or level - using generic scoring"))
        return {"score": score, "issues": issues}

    if not role_data:
        score = 10
        issues.append(("info", f"Role '{role_id}' not found - using generic scoring"))
        return {"score": score, "issues": issues}

    # Get resume text
    all_text = " ".join([
        " ".join([str(exp) for exp in resume.experience]),
        " ".join(resume.skills),
        " ".join([str(edu) for edu in resume.education])
    ]).lower()

    # Required skills (5 points)
    required_skills = role_data.get('required_skills', [])
    if required_skills:
        found_required = sum(1 for skill in required_skills if skill.lower() in all_text)

        if found_required == len(required_skills):
            score += 5
        elif found_required >= len(required_skills) * 0.66:
            score += 3
            missing = [s for s in required_skills if s.lower() not in all_text]
            issues.append(("suggestion", f"Add required skills: {', '.join(missing)}"))
        else:
            score += 1
            issues.append(("warning", f"Missing most required skills for {role_data['name']}"))
    else:
        score += 5  # Default if no required skills defined

    # Level-appropriate keywords (10 points)
    level_keywords = role_data.get('typical_keywords', [])
    if level_keywords:
        found_keywords = sum(1 for keyword in level_keywords if keyword.lower() in all_text)
        keyword_percentage = (found_keywords / len(level_keywords)) * 100 if level_keywords else 0

        if keyword_percentage >= 60:
            score += 10
        elif keyword_percentage >= 40:
            score += 6
            issues.append(("suggestion", f"Add more {level} level keywords for {role_data['name']}"))
        elif keyword_percentage >= 20:
            score += 3
            issues.append(("warning", f"Few {level} level keywords found - showcase relevant experience"))
        else:
            score += 1
            issues.append(("warning", f"Very few {level} level keywords - highlight relevant skills and experience"))
    else:
        score += 5  # Default if no keywords defined

    # Preferred sections (5 points)
    preferred_sections = role_data.get('preferred_sections', [])
    if preferred_sections:
        found_sections = sum(1 for section in preferred_sections if section.lower() in all_text)

        if found_sections >= len(preferred_sections) * 0.66:
            score += 5
        elif found_sections > 0:
            score += 3
            missing = [s for s in preferred_sections if s.lower() not in all_text]
            issues.append(("info", f"Consider adding: {', '.join(missing)}"))
        else:
            score += 1
            issues.append(("suggestion", f"For {role_data['name']}, include: {', '.join(preferred_sections)}"))
    else:
        score += 5  # Default if no preferred sections

    return {"score": score, "issues": issues}


def calculate_overall_score(
    resume: ResumeData,
    job_description: str = "",
    role_id: str = "",
    level: str = "",
    industry: str = ""  # Kept for backward compatibility
) -> Dict:
    """
    Calculate overall ATS score by aggregating all scoring components.

    Total possible score: 100 points
    - Contact info: 10 points
    - Formatting: 20 points
    - Content quality: 25 points
    - Keywords: 15 points
    - Length & Density: 10 points
    - Role-specific: 20 points

    Args:
        resume: ResumeData object with parsed resume information
        job_description: Optional job description for keyword matching
        role_id: Optional role identifier (e.g., "software_engineer")
        level: Optional experience level (e.g., "mid", "senior")
        industry: Deprecated - use role_id and level instead

    Returns:
        Dict with overall score, breakdown, and all issues
    """
    # Score each component
    contact_result = score_contact_info(resume)
    formatting_result = score_formatting(resume)
    content_result = score_content(resume, role_id, level)
    keywords_result = score_keywords(resume, job_description, role_id, level)
    length_density_result = score_length_density(resume)

    # Use role-specific scoring if role_id provided, otherwise fall back to industry
    if role_id and level:
        role_result = score_role_specific(resume, role_id, level)
    elif industry:
        # Backward compatibility: use old industry-specific scoring
        role_result = score_industry_specific(resume, industry)
    else:
        role_result = score_role_specific(resume, "", "")

    # Calculate total score
    total_score = (
        contact_result["score"] +
        formatting_result["score"] +
        content_result["score"] +
        keywords_result["score"] +
        length_density_result["score"] +
        role_result["score"]
    )

    # Aggregate all issues
    all_issues = (
        contact_result["issues"] +
        formatting_result["issues"] +
        content_result["issues"] +
        keywords_result["issues"] +
        length_density_result["issues"] +
        role_result["issues"]
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
            "roleSpecific": {
                "score": role_result["score"],
                "maxScore": 20,
                "issues": role_result["issues"]
            }
        },
        "issues": {
            "critical": critical_issues,
            "warnings": warnings,
            "suggestions": suggestions,
            "info": info
        }
    }
