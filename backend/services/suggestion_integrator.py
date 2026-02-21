"""
Suggestion Integrator - Connects enhanced suggestions to scoring results.

This module enriches the scorer output with actionable, specific suggestions
by analyzing the scoring results and resume data.
"""

from typing import Dict, List
from backend.services.parser import ResumeData
from backend.services.suggestion_generator import EnhancedSuggestionGenerator


class SuggestionIntegrator:
    """
    Integrates enhanced suggestions into scoring results.

    Transforms scoring issues into actionable suggestions with templates,
    examples, and specific guidance.
    """

    @staticmethod
    def enrich_score_result(
        score_result: Dict,
        resume_data: ResumeData,
        role: str,
        level: str,
        job_description: str = ""
    ) -> Dict:
        """
        Enrich scoring result with enhanced suggestions.

        Args:
            score_result: Original scoring result from AdaptiveScorer
            resume_data: Parsed resume data
            role: Role ID
            level: Experience level
            job_description: Optional job description

        Returns:
            Enriched score result with enhanced suggestions
        """
        # Initialize suggestion generator
        generator = EnhancedSuggestionGenerator(role, level, job_description)

        # Extract missing keywords from scoring results
        missing_keywords = SuggestionIntegrator._extract_missing_keywords(score_result)

        # Extract weak bullet points from resume
        weak_bullets = SuggestionIntegrator._find_weak_bullets(resume_data)

        # Extract format issues
        format_issues = SuggestionIntegrator._extract_format_issues(score_result)

        # Generate enhanced suggestions
        enhanced_suggestions = generator.generate_suggestions(
            resume_data=resume_data,
            missing_keywords=missing_keywords,
            weak_bullets=weak_bullets,
            format_issues=format_issues
        )

        # Add enhanced suggestions to score result
        score_result['enhanced_suggestions'] = enhanced_suggestions

        # Don't enrich issues dict - enhanced_suggestions are separate field
        # The issues dict should only contain string lists (critical, warnings, suggestions, info)

        return score_result

    @staticmethod
    def _extract_missing_keywords(score_result: Dict) -> List[str]:
        """Extract missing keywords from score result."""
        missing = []

        # From keyword_details in ATS mode
        keyword_details = score_result.get('keyword_details')

        # Check if keyword_details exists and is not None
        if keyword_details and isinstance(keyword_details, dict):
            if 'missing_keywords' in keyword_details:
                missing.extend(keyword_details['missing_keywords'])
            elif 'missingKeywords' in keyword_details:
                missing.extend(keyword_details['missingKeywords'])

        # From breakdown issues
        for category, data in score_result.get('breakdown', {}).items():
            for issue in data.get('issues', []):
                # Issue is tuple: (severity, message)
                if isinstance(issue, tuple):
                    message = issue[1]
                else:
                    message = issue

                # Extract keywords from "missing X keyword" messages
                if 'missing' in message.lower() and 'keyword' in message.lower():
                    # Try to extract keyword names from message
                    # This is a simple extraction; adjust based on actual message format
                    pass

        return missing

    @staticmethod
    def _find_weak_bullets(resume_data: ResumeData) -> List[Dict]:
        """Find weak bullet points in experience section."""
        weak_bullets = []

        if not resume_data.experience:
            return weak_bullets

        for exp in resume_data.experience:
            description = exp.get('description', '')

            if not description:
                continue

            # Check for weak patterns
            desc_lower = description.lower()

            # Weak indicators
            is_weak = False

            # 1. Starts with weak verbs
            weak_starters = ['worked on', 'responsible for', 'helped', 'assisted', 'involved in']
            if any(desc_lower.startswith(weak) for weak in weak_starters):
                is_weak = True

            # 2. No numbers/metrics
            if not any(char.isdigit() for char in description):
                is_weak = True

            # 3. Too short (< 30 chars)
            if len(description) < 30:
                is_weak = True

            # 4. Too long (> 200 chars) without structure
            if len(description) > 200 and '. ' not in description:
                is_weak = True

            # 5. Generic phrases
            generic_phrases = ['various', 'multiple', 'different', 'some', 'several']
            if any(phrase in desc_lower for phrase in generic_phrases):
                is_weak = True

            if is_weak:
                weak_bullets.append({
                    'text': description,
                    'description': description,
                    'company': exp.get('company', ''),
                    'title': exp.get('title', '')
                })

        return weak_bullets[:5]  # Return top 5 weak bullets

    @staticmethod
    def _extract_format_issues(score_result: Dict) -> List[str]:
        """Extract formatting issues from score result."""
        format_issues = []

        # From breakdown format section
        format_data = score_result.get('breakdown', {}).get('format', {})

        for issue in format_data.get('issues', []):
            # Issue is tuple: (severity, message)
            if isinstance(issue, tuple):
                message = issue[1]
            else:
                message = issue

            if message:
                format_issues.append(message)

        return format_issues

    @staticmethod
    def _enrich_issues(issues: Dict, enhanced_suggestions: List[Dict]) -> Dict:
        """
        Enrich existing issues with enhanced suggestion IDs.

        This allows the frontend to link issues to their detailed suggestions.
        """
        # Create a map of issue descriptions to suggestion IDs
        suggestion_map = {}

        for suggestion in enhanced_suggestions:
            # Use description as key for matching
            desc = suggestion.get('description', '')
            suggestion_id = suggestion.get('id', '')
            suggestion_map[desc] = suggestion_id

        # Enrich each issue category
        enriched_issues = {}

        for severity, issue_list in issues.items():
            enriched_list = []

            for issue in issue_list:
                # Issue is tuple: (severity, message) or just message
                if isinstance(issue, tuple):
                    message = issue[1]
                    enriched_list.append(issue)  # Keep original format
                else:
                    enriched_list.append(issue)

            enriched_issues[severity] = enriched_list

        # Add enhanced suggestions as structured objects
        enriched_issues['enhanced_suggestions'] = enhanced_suggestions

        return enriched_issues

    @staticmethod
    def format_suggestion_for_frontend(suggestion: Dict) -> Dict:
        """
        Format suggestion for frontend consumption.

        Converts enhanced suggestion to format expected by IssuesList component.
        """
        return {
            'id': suggestion.get('id', ''),
            'type': suggestion.get('type', 'missing_content'),
            'severity': suggestion.get('severity', 'medium'),
            'title': suggestion.get('title', ''),
            'description': suggestion.get('description', ''),
            'template': suggestion.get('template', ''),
            'quickFix': suggestion.get('quickFix', {}),
            'keywords': suggestion.get('keywords', [])
        }
