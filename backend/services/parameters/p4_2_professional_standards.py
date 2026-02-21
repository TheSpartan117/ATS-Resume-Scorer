"""
P4.2: Professional Standards (5 points)

Checks for unprofessional content and presentation:
1. Personal pronouns (I, me, my) = -2 pts
2. Unprofessional email (e.g., cooldude@) = -1 pt
3. Inappropriate content = -2 pts
4. Inconsistent formatting = -1 pt

Scoring:
- Start with 5 points
- Deduct penalties (minimum 0)

Research basis:
- ATS systems flag personal pronouns as unprofessional
- Unprofessional emails reduce credibility (ResumeWorded)
- Controversial content can lead to rejection
- Inconsistent formatting shows lack of attention to detail
"""

import re
from typing import Dict, List, Any, Optional


class ProfessionalStandardsScorer:
    """Scores professional standards and presentation quality."""

    def __init__(self):
        """Initialize scorer with pattern definitions."""
        # Personal pronouns pattern (case insensitive)
        self.pronoun_pattern = re.compile(
            r'\b(I|me|my|mine|myself)\b',
            re.IGNORECASE
        )

        # Unprofessional email patterns
        self.unprofessional_patterns = [
            r'cool',
            r'cute',
            r'sexy',
            r'hot',
            r'party',
            r'love',
            r'xxx',
            r'gaming?',
            r'boss',
            r'king',
            r'queen',
            r'prince',
            r'rock\s*star',
            r'ninja',
            r'guru',
            r'wizard',
            r'master',
            r'dude',
            r'bro',
            r'girl',
            r'boy',
            r'kid'
        ]

        # Inappropriate/controversial content keywords
        self.inappropriate_patterns = [
            r'\breligious?\b',
            r'\bpolitical?\b',
            r'\bpolitics\b',
            r'\bchurch\b',
            r'\bmosque\b',
            r'\btemple\b',
            r'\bcontroversia(l|les)\b',
            r'\bactivism\b',
            r'\bprotest\b',
            r'\bcampaign\s+(for|against)',
            r'\belection\s+campaign\b',
            r'\bpartisan\b'
        ]

    def score(
        self,
        contact: Dict[str, Optional[str]],
        bullets: List[str],
        full_text: str
    ) -> Dict[str, Any]:
        """
        Score professional standards for a resume.

        Args:
            contact: Contact information dict with 'email', 'name', 'phone'
            bullets: List of resume bullet points
            full_text: Full resume text for analysis

        Returns:
            Dictionary containing:
            - score: Total points (0-5)
            - max_score: Maximum possible points (5)
            - personal_pronoun_count: Number of personal pronouns found
            - unprofessional_email: Boolean flag for unprofessional email
            - has_inappropriate_content: Boolean flag for inappropriate content
            - has_formatting_issues: Boolean flag for formatting issues
            - has_professional_email: Boolean flag for professional email
            - issues: List of issue descriptions
            - issue_details: Detailed breakdown of each issue type
        """
        # Start with full points
        score = 5
        issues = []
        issue_details = {
            'pronouns': [],
            'email': [],
            'content': [],
            'formatting': []
        }

        # Check 1: Personal pronouns (-2 pts)
        pronoun_count = self._check_personal_pronouns(full_text, issues, issue_details)
        if pronoun_count > 0:
            score -= 2

        # Check 2: Unprofessional email (-1 pt)
        email = contact.get('email', '')
        unprofessional_email = self._check_unprofessional_email(email, issues, issue_details)
        if unprofessional_email:
            score -= 1

        # Check 3: Inappropriate content (-2 pts)
        has_inappropriate = self._check_inappropriate_content(full_text, issues, issue_details)
        if has_inappropriate:
            score -= 2

        # Check 4: Inconsistent formatting (-1 pt)
        has_formatting_issues = self._check_formatting_consistency(bullets, issues, issue_details)
        if has_formatting_issues:
            score -= 1

        # Ensure minimum score is 0
        score = max(0, score)

        return {
            'score': score,
            'max_score': 5,
            'personal_pronoun_count': pronoun_count,
            'unprofessional_email': unprofessional_email,
            'has_inappropriate_content': has_inappropriate,
            'has_formatting_issues': has_formatting_issues,
            'has_professional_email': not unprofessional_email and bool(email),
            'issues': issues,
            'issue_details': issue_details
        }

    def _check_personal_pronouns(
        self,
        text: str,
        issues: List[str],
        issue_details: Dict
    ) -> int:
        """
        Check for personal pronouns in resume text.

        Returns:
            Count of personal pronouns found
        """
        if not text:
            return 0

        matches = self.pronoun_pattern.findall(text)
        count = len(matches)

        if count > 0:
            issue_msg = f"Found {count} personal pronouns (I, me, my). Use third-person perspective (-2 pts)"
            issues.append(issue_msg)
            issue_details['pronouns'].append({
                'count': count,
                'penalty': 2,
                'examples': matches[:5]  # Show first 5 examples
            })

        return count

    def _check_unprofessional_email(
        self,
        email: str,
        issues: List[str],
        issue_details: Dict
    ) -> bool:
        """
        Check if email address is unprofessional.

        Returns:
            True if unprofessional, False otherwise
        """
        if not email:
            return False

        email_lower = email.lower()

        # Check against unprofessional patterns
        for pattern in self.unprofessional_patterns:
            if re.search(pattern, email_lower):
                issue_msg = f"Unprofessional email address detected: {email}. Use a professional email (-1 pt)"
                issues.append(issue_msg)
                issue_details['email'].append({
                    'email': email,
                    'penalty': 1,
                    'pattern_matched': pattern
                })
                return True

        return False

    def _check_inappropriate_content(
        self,
        text: str,
        issues: List[str],
        issue_details: Dict
    ) -> bool:
        """
        Check for inappropriate or controversial content.

        Returns:
            True if inappropriate content found, False otherwise
        """
        if not text:
            return False

        text_lower = text.lower()
        found_patterns = []

        for pattern in self.inappropriate_patterns:
            matches = re.findall(pattern, text_lower)
            if matches:
                found_patterns.extend(matches)

        if found_patterns:
            issue_msg = "Inappropriate content detected (religious, political). Keep resume professional (-2 pts)"
            issues.append(issue_msg)
            issue_details['content'].append({
                'penalty': 2,
                'patterns_found': found_patterns[:3],  # Show first 3 examples
                'count': len(found_patterns)
            })
            return True

        return False

    def _check_formatting_consistency(
        self,
        bullets: List[str],
        issues: List[str],
        issue_details: Dict
    ) -> bool:
        """
        Check for formatting consistency across bullet points.

        Checks:
        1. Consistent capitalization (all start with capital letter)
        2. No all-caps bullets
        3. Consistent punctuation

        Returns:
            True if formatting issues found, False otherwise
        """
        if not bullets or len(bullets) < 2:
            return False

        # Track capitalization patterns
        starts_with_capital = 0
        starts_with_lowercase = 0
        all_caps_count = 0
        inconsistent_examples = []

        for bullet in bullets:
            bullet_clean = bullet.strip()
            if not bullet_clean:
                continue

            # Check first character capitalization
            first_char = bullet_clean[0]
            if first_char.isupper():
                starts_with_capital += 1
            elif first_char.islower():
                starts_with_lowercase += 1
                inconsistent_examples.append(bullet_clean[:50])

            # Check for all-caps (more than 70% uppercase letters)
            letters = [c for c in bullet_clean if c.isalpha()]
            if letters:
                uppercase_ratio = sum(1 for c in letters if c.isupper()) / len(letters)
                if uppercase_ratio > 0.7:
                    all_caps_count += 1
                    inconsistent_examples.append(bullet_clean[:50])

        # Determine if there's inconsistency
        total_bullets = len([b for b in bullets if b.strip()])
        has_issues = False

        # Mixed capitalization or all-caps bullets indicate inconsistency
        if starts_with_lowercase > 0 and starts_with_capital > 0:
            has_issues = True
        elif all_caps_count > 0:
            has_issues = True

        if has_issues:
            issue_msg = "Inconsistent bullet point formatting detected. Ensure consistent capitalization (-1 pt)"
            issues.append(issue_msg)
            issue_details['formatting'].append({
                'penalty': 1,
                'starts_with_capital': starts_with_capital,
                'starts_with_lowercase': starts_with_lowercase,
                'all_caps_count': all_caps_count,
                'examples': inconsistent_examples[:3]
            })

        return has_issues


def score_professional_standards(
    contact: Dict[str, Optional[str]],
    bullets: List[str],
    full_text: str
) -> Dict[str, Any]:
    """
    Convenience function to score professional standards.

    Args:
        contact: Contact information dict with 'email', 'name', 'phone'
        bullets: List of resume bullet points
        full_text: Full resume text for analysis

    Returns:
        Score result dictionary
    """
    scorer = ProfessionalStandardsScorer()
    return scorer.score(contact, bullets, full_text)
