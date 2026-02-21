"""
Grammar Checker - Phase 1.3
Uses LanguageTool for professional-grade grammar and spelling checking.

This module provides:
- Grammar error detection
- Spelling error detection
- Typographical error detection
- Scoring based on error count
"""

from typing import Dict, List
from functools import lru_cache


class GrammarChecker:
    """
    Grammar checker using LanguageTool Python.

    Features:
    - Detects grammar, spelling, and typographical errors
    - Provides suggestions for corrections
    - Scores based on error severity and count
    """

    def __init__(self, language: str = 'en-US'):
        """
        Initialize grammar checker.

        Args:
            language: Language code (default: 'en-US')
        """
        self._tool = None
        self._language = language
        self._initialized = False

    def _lazy_init(self):
        """Lazy initialization to avoid loading LanguageTool on import"""
        if self._initialized:
            return

        try:
            import language_tool_python
            # Initialize LanguageTool with local server (no remote API calls)
            self._tool = language_tool_python.LanguageTool(self._language)
            self._initialized = True
        except Exception as e:
            print(f"Warning: LanguageTool initialization failed: {e}")
            print("Falling back to basic grammar checking")
            self._tool = None
            self._initialized = True  # Still mark as initialized to use fallback

    def check(self, text: str, max_issues: int = 50) -> Dict:
        """
        Check text for grammar, spelling, and typographical errors.

        Args:
            text: Text to check
            max_issues: Maximum number of issues to return (default: 50)

        Returns:
            Dictionary with:
            - total_issues: Total error count
            - issues: List of error details
            - score: Grammar score (0-100)
            - severity_breakdown: Count by severity
        """
        self._lazy_init()

        if not text or len(text.strip()) < 5:
            return {
                'total_issues': 0,
                'issues': [],
                'score': 100,
                'severity_breakdown': {'critical': 0, 'warning': 0, 'info': 0},
                'message': 'Text too short to analyze'
            }

        if not self._initialized or not self._tool:
            # Fallback to basic checking (disabled for resumes)
            # Most "errors" are actually normal resume formatting
            return {
                'total_issues': 0,
                'issues': [],
                'score': 100,
                'severity_breakdown': {'critical': 0, 'warning': 0, 'info': 0},
                'message': 'Grammar checking unavailable (LanguageTool not configured)'
            }

        try:
            matches = self._tool.check(text)

            # Filter and categorize issues
            issues = []
            severity_count = {'critical': 0, 'warning': 0, 'info': 0}

            for match in matches[:max_issues]:
                # Determine severity
                issue_type = match.ruleIssueType or 'unknown'
                category = self._categorize_issue(match)

                severity = 'warning'
                if issue_type in ['misspelling', 'grammar']:
                    severity = 'critical'
                elif issue_type in ['typographical', 'style']:
                    severity = 'warning'
                else:
                    severity = 'info'

                severity_count[severity] += 1

                issue = {
                    'message': match.message,
                    'context': match.context,
                    'replacements': match.replacements[:3] if match.replacements else [],
                    'offset': match.offset,
                    'length': match.errorLength,
                    'category': category,
                    'severity': severity,
                    'rule': match.ruleId
                }
                issues.append(issue)

            # Calculate score
            total_issues = len(matches)
            score = self._calculate_score(
                total_issues,
                severity_count,
                len(text.split())
            )

            message = self._generate_message(total_issues, severity_count)

            return {
                'total_issues': total_issues,
                'issues': issues,
                'score': score,
                'severity_breakdown': severity_count,
                'message': message
            }

        except Exception as e:
            print(f"Grammar checking failed: {e}")
            return self._fallback_check(text)

    def check_and_suggest(self, text: str, max_suggestions: int = 10) -> Dict:
        """
        Check text and provide top correction suggestions.

        Args:
            text: Text to check
            max_suggestions: Maximum suggestions to return

        Returns:
            Dictionary with issues and top suggestions
        """
        result = self.check(text)

        if not result['issues']:
            return result

        # Get top priority issues
        critical_issues = [
            issue for issue in result['issues']
            if issue['severity'] == 'critical'
        ]

        top_suggestions = critical_issues[:max_suggestions]

        result['top_suggestions'] = top_suggestions
        return result

    def _categorize_issue(self, match) -> str:
        """
        Categorize issue type for better reporting.

        Args:
            match: LanguageTool match object

        Returns:
            Category string
        """
        issue_type = match.ruleIssueType or ''

        if 'misspelling' in issue_type.lower():
            return 'spelling'
        elif 'grammar' in issue_type.lower():
            return 'grammar'
        elif 'typo' in issue_type.lower():
            return 'typo'
        elif 'punctuation' in issue_type.lower():
            return 'punctuation'
        elif 'capitalization' in issue_type.lower():
            return 'capitalization'
        elif 'style' in issue_type.lower():
            return 'style'
        else:
            return 'other'

    def _calculate_score(
        self,
        total_issues: int,
        severity_count: Dict,
        word_count: int
    ) -> int:
        """
        Calculate grammar score based on errors.

        Scoring:
        - Start with 100 points
        - Critical errors: -5 points each
        - Warning errors: -2 points each
        - Info errors: -1 point each
        - Minimum score: 0

        Args:
            total_issues: Total error count
            severity_count: Breakdown by severity
            word_count: Total word count

        Returns:
            Score (0-100)
        """
        score = 100

        # Deduct points based on severity
        score -= severity_count.get('critical', 0) * 5
        score -= severity_count.get('warning', 0) * 2
        score -= severity_count.get('info', 0) * 1

        # Apply length penalty (more errors in short text is worse)
        if word_count > 0:
            error_rate = total_issues / word_count
            if error_rate > 0.05:  # More than 5% error rate
                score -= 10

        return max(0, min(100, score))

    def _generate_message(self, total_issues: int, severity_count: Dict) -> str:
        """
        Generate human-readable message about grammar check.

        Args:
            total_issues: Total error count
            severity_count: Breakdown by severity

        Returns:
            Message string
        """
        critical = severity_count.get('critical', 0)
        warning = severity_count.get('warning', 0)

        if total_issues == 0:
            return "No grammar or spelling errors detected"
        elif critical == 0 and warning <= 2:
            return f"{total_issues} minor issue(s) found - excellent"
        elif critical <= 2:
            return f"{critical} critical error(s), {warning} warning(s) - needs minor corrections"
        elif critical <= 5:
            return f"{critical} critical error(s) - requires proofreading"
        else:
            return f"{critical} critical error(s) - requires thorough proofreading"

    def _fallback_check(self, text: str) -> Dict:
        """
        Fallback grammar checking using basic patterns.
        Used when LanguageTool is not available.

        Args:
            text: Text to check

        Returns:
            Basic grammar check results
        """
        import re

        issues = []

        # Check for common issues
        # 1. Double spaces
        if '  ' in text:
            issues.append({
                'message': 'Multiple consecutive spaces found',
                'category': 'formatting',
                'severity': 'info'
            })

        # 2. Missing capitalization at sentence start (DISABLED for resumes)
        # Resume bullets often don't start with capitals - this is normal formatting
        # sentences = re.split(r'[.!?]\s+', text)
        # for sentence in sentences:
        #     if sentence and sentence[0].islower():
        #         issues.append({
        #             'message': 'Sentence should start with capital letter',
        #             'category': 'capitalization',
        #             'severity': 'warning'
        #         })

        # 3. Common typos
        common_typos = {
            'teh': 'the',
            'recieve': 'receive',
            'occured': 'occurred',
            'seperate': 'separate',
            'definately': 'definitely'
        }

        words = re.findall(r'\b\w+\b', text.lower())
        for word in words:
            if word in common_typos:
                issues.append({
                    'message': f"Possible typo: '{word}' -> '{common_typos[word]}'",
                    'category': 'spelling',
                    'severity': 'critical',
                    'replacements': [common_typos[word]]
                })

        total_issues = len(issues)
        score = max(0, 100 - total_issues * 5)

        return {
            'total_issues': total_issues,
            'issues': issues,
            'score': score,
            'severity_breakdown': {
                'critical': sum(1 for i in issues if i['severity'] == 'critical'),
                'warning': sum(1 for i in issues if i['severity'] == 'warning'),
                'info': sum(1 for i in issues if i['severity'] == 'info')
            },
            'message': f"{total_issues} issue(s) found (basic check only)"
        }

    def close(self):
        """Clean up resources"""
        if self._tool:
            try:
                self._tool.close()
            except:
                pass


# Singleton instance
_grammar_checker_instance = None


def get_grammar_checker() -> GrammarChecker:
    """
    Get singleton instance of GrammarChecker.

    Returns:
        GrammarChecker instance
    """
    global _grammar_checker_instance
    if _grammar_checker_instance is None:
        _grammar_checker_instance = GrammarChecker()
    return _grammar_checker_instance
