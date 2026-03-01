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
import logging
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
from functools import lru_cache

logger = logging.getLogger(__name__)

# Starting a local LanguageTool JVM can take 60-90s on Render free tier.
# 20s is enough for a warm JVM (already started by preload) while still
# protecting against cold-start hangs.
_GRAMMAR_LOAD_TIMEOUT_SECONDS = 20
_RETRY_COOLDOWN_SECONDS = 300  # 5 minutes


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
        self._last_failed_at: float = 0.0

    def _lazy_init(self):
        """
        Lazy initialization with a hard timeout and cooldown-based retry.

        LanguageTool starts a local JVM which takes 60-90s on Render free tier.
        We pre-start it in backend/preload_models.py so the JVM is warm at
        runtime.  The timeout here guards against the cold-start case.
        """
        if self._initialized:
            return

        # Respect retry cooldown
        if self._last_failed_at and (time.time() - self._last_failed_at) < _RETRY_COOLDOWN_SECONDS:
            return

        def _load():
            import language_tool_python
            return language_tool_python.LanguageTool(self._language)

        try:
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(_load)
                try:
                    self._tool = future.result(timeout=_GRAMMAR_LOAD_TIMEOUT_SECONDS)
                    self._initialized = True
                    self._last_failed_at = 0.0
                    logger.info("LanguageTool grammar checker initialized successfully")
                except FuturesTimeoutError:
                    logger.warning(
                        "LanguageTool initialization timed out after %ds — "
                        "falling back to basic grammar checking. Will retry in %d minutes.",
                        _GRAMMAR_LOAD_TIMEOUT_SECONDS, _RETRY_COOLDOWN_SECONDS // 60,
                    )
                    self._tool = None
                    self._last_failed_at = time.time()
                except Exception as e:
                    logger.warning(
                        "LanguageTool initialization failed (%s) — "
                        "falling back to basic grammar checking. Will retry in %d minutes.",
                        e, _RETRY_COOLDOWN_SECONDS // 60,
                    )
                    self._tool = None
                    self._last_failed_at = time.time()
        except Exception as e:
            logger.warning("LanguageTool could not be loaded: %s", e)
            self._tool = None
            self._last_failed_at = time.time()

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
            # LanguageTool unavailable — use pyspellchecker-based fallback
            return self._fallback_check(text)

        try:
            tool = self._tool  # local ref for thread safety

            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(tool.check, text)
                try:
                    matches = future.result(timeout=10)
                except FuturesTimeoutError:
                    logger.warning("LanguageTool.check() timed out — falling back to basic checking")
                    return self._fallback_check(text)

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
        Fallback grammar checking using pyspellchecker + basic patterns.
        Used when LanguageTool (Java) is not available.

        Args:
            text: Text to check

        Returns:
            Basic grammar check results
        """
        import re

        issues = []

        # 1. Double spaces
        if '  ' in text:
            issues.append({
                'message': 'Multiple consecutive spaces found',
                'category': 'formatting',
                'severity': 'info'
            })

        # 2. Spell check using pyspellchecker (installed, works without Java)
        try:
            from spellchecker import SpellChecker
            spell = SpellChecker()

            # Extract plain alphabetic words; skip short words and likely proper nouns
            raw_words = re.findall(r'\b[a-zA-Z]{4,}\b', text)

            # Skip words that are all-caps (acronyms: SQL, AWS, MBA, etc.)
            # and words starting with uppercase followed by lowercase (proper nouns)
            words_to_check = [
                w for w in raw_words
                if not w.isupper() and not (w[0].isupper() and w[1:].islower())
            ]

            misspelled = spell.unknown(words_to_check)
            for word in misspelled:
                suggestion = spell.correction(word)
                if suggestion and suggestion != word:
                    issues.append({
                        'message': f"Possible spelling error: '{word}' (suggestion: '{suggestion}')",
                        'category': 'spelling',
                        'severity': 'critical',
                        'replacements': [suggestion]
                    })
        except ImportError:
            # pyspellchecker not available — fall through to hardcoded typos only
            pass
        except Exception:
            pass

        # 3. Hardcoded common typos as final backstop
        common_typos = {
            'teh': 'the', 'recieve': 'receive', 'occured': 'occurred',
            'seperate': 'separate', 'definately': 'definitely',
            'managment': 'management', 'developement': 'development',
            'experiance': 'experience', 'enviroment': 'environment',
        }
        words_lower = re.findall(r'\b\w+\b', text.lower())
        for word in words_lower:
            if word in common_typos:
                already_flagged = any(word in i['message'] for i in issues)
                if not already_flagged:
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
            'message': (
                f"{total_issues} spelling/formatting issue(s) found (basic check — install Java for full grammar checking)"
                if total_issues > 0
                else "No obvious spelling errors detected (basic check — install Java for full grammar checking)"
            )
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
