"""
ATS Parsing Simulation Service

Simulates how different ATS platforms (Taleo, Workday, Greenhouse) parse resumes.
This helps users understand which platforms their resume is compatible with.

Based on research from:
- Taleo: Strictest parser, fails on tables, text boxes, complex formatting
- Workday: Moderate parser, handles most standard formats
- Greenhouse: Most lenient, modern parser with good format support
"""

import re
from typing import Dict, List, Any
from dataclasses import dataclass


@dataclass
class ATSIssue:
    """Represents an issue found during ATS parsing simulation"""
    severity: str  # 'critical', 'warning', 'info'
    message: str
    recommendation: str
    impact_score: int  # How much this reduces pass probability (0-30)


class ATSSimulator:
    """
    Simulates parsing behavior of major ATS platforms.

    Platform Market Share (2025):
    - Workday: 45%
    - Taleo (Oracle): 30%
    - Greenhouse: 15%
    - Others: 10%
    """

    def __init__(self):
        """Initialize ATS simulator with platform-specific rules"""
        self.platforms = ['Taleo', 'Workday', 'Greenhouse']

        # Format compatibility rules
        self.problematic_elements = {
            'tables': ['<table>', '\\begin{tabular}', '|---|'],
            'text_boxes': ['text box', 'textbox', 'frame'],
            'headers_footers': ['header', 'footer'],
            'columns': ['\\begin{multicols}', 'column'],
            'graphics': ['\\includegraphics', '<img', 'image']
        }

    def simulate_taleo(self, resume_text: str, resume_metadata: Dict = None) -> Dict[str, Any]:
        """
        Simulate Taleo (Oracle) ATS parsing.

        Taleo Characteristics:
        - Strictest parser in the industry
        - Cannot parse tables, text boxes, headers/footers
        - Requires clear section breaks (double newlines)
        - Struggles with multi-column layouts
        - Cannot extract text from images

        Pass Rate Baseline: 65% (most resumes have issues)

        Args:
            resume_text: Full text content of resume
            resume_metadata: Optional metadata (page count, format, etc.)

        Returns:
            Dict with platform name, pass probability, issues, recommendations
        """
        issues = []
        pass_probability = 100  # Start at 100%, deduct for issues

        metadata = resume_metadata or {}

        # Critical Issue 1: Tables (most common problem)
        if self._has_tables(resume_text):
            issues.append(ATSIssue(
                severity='critical',
                message="Resume contains tables - Taleo cannot parse tables reliably",
                recommendation="Convert tables to bullet points with clear section headers",
                impact_score=30
            ))
            pass_probability -= 30

        # Critical Issue 2: Text boxes
        if self._has_text_boxes(resume_text):
            issues.append(ATSIssue(
                severity='critical',
                message="Resume contains text boxes - Taleo will skip these sections",
                recommendation="Remove text boxes, use standard text formatting",
                impact_score=25
            ))
            pass_probability -= 25

        # Critical Issue 3: Headers/Footers
        if self._has_headers_footers(resume_text, metadata):
            issues.append(ATSIssue(
                severity='warning',
                message="Important information in headers/footers may be ignored",
                recommendation="Move contact info to main body of resume",
                impact_score=15
            ))
            pass_probability -= 15

        # Warning 1: Poor section separation
        section_breaks = len(re.findall(r'\n\n+', resume_text))
        if section_breaks < 3:
            issues.append(ATSIssue(
                severity='warning',
                message="Insufficient section breaks - Taleo needs clear separation",
                recommendation="Add blank lines between major sections (Experience, Education, Skills)",
                impact_score=10
            ))
            pass_probability -= 10

        # Warning 2: Multi-column layout
        if self._has_columns(resume_text):
            issues.append(ATSIssue(
                severity='warning',
                message="Multi-column layout detected - may be parsed out of order",
                recommendation="Use single-column layout for maximum compatibility",
                impact_score=15
            ))
            pass_probability -= 15

        # Warning 3: Special characters
        special_char_count = len(re.findall(r'[^\x00-\x7F]', resume_text))
        if special_char_count > 50:
            issues.append(ATSIssue(
                severity='info',
                message=f"Resume contains {special_char_count} non-ASCII characters",
                recommendation="Replace special characters with ASCII equivalents",
                impact_score=5
            ))
            pass_probability -= 5

        # Ensure probability stays in valid range
        pass_probability = max(0, min(100, pass_probability))

        return {
            'platform': 'Taleo (Oracle)',
            'market_share': '30%',
            'pass_probability': pass_probability,
            'rating': self._get_rating(pass_probability),
            'issues': [
                {
                    'severity': issue.severity,
                    'message': issue.message,
                    'recommendation': issue.recommendation
                } for issue in issues
            ],
            'summary': self._generate_summary('Taleo', pass_probability, len(issues)),
            'parsing_notes': [
                "Taleo uses older parsing technology (text extraction only)",
                "Cannot interpret visual formatting",
                "Requires explicit section headers (EXPERIENCE, EDUCATION, etc.)",
                "Best format: Simple, single-column, text-based resume"
            ]
        }

    def simulate_workday(self, resume_text: str, resume_metadata: Dict = None) -> Dict[str, Any]:
        """
        Simulate Workday ATS parsing.

        Workday Characteristics:
        - Moderate parser, handles most standard formats
        - Can parse simple tables (but not complex ones)
        - Handles headers/footers reasonably well
        - Good at contact info extraction
        - Supports PDF and DOCX equally well

        Pass Rate Baseline: 82% (most resumes pass)

        Args:
            resume_text: Full text content of resume
            resume_metadata: Optional metadata

        Returns:
            Dict with platform name, pass probability, issues, recommendations
        """
        issues = []
        pass_probability = 100

        metadata = resume_metadata or {}

        # Warning 1: Complex tables (simple tables are OK)
        if self._has_complex_tables(resume_text):
            issues.append(ATSIssue(
                severity='warning',
                message="Complex nested tables may not parse correctly",
                recommendation="Simplify table structure or convert to bullet points",
                impact_score=15
            ))
            pass_probability -= 15

        # Warning 2: Images with text
        if self._has_graphics(resume_text):
            issues.append(ATSIssue(
                severity='warning',
                message="Images detected - text in images won't be extracted",
                recommendation="Remove images or convert image text to regular text",
                impact_score=10
            ))
            pass_probability -= 10

        # Info 1: Non-standard sections
        standard_sections = ['experience', 'education', 'skills', 'summary']
        detected_sections = self._detect_sections(resume_text)

        non_standard = [s for s in detected_sections if s.lower() not in standard_sections]
        if len(non_standard) > 3:
            issues.append(ATSIssue(
                severity='info',
                message=f"Resume has {len(non_standard)} non-standard section headers",
                recommendation="Use standard headers: Experience, Education, Skills, Summary",
                impact_score=5
            ))
            pass_probability -= 5

        # Info 2: File format (if metadata available)
        file_format = metadata.get('format', '').lower()
        if file_format and file_format not in ['pdf', 'docx', 'doc']:
            issues.append(ATSIssue(
                severity='info',
                message=f"Format '{file_format}' may have compatibility issues",
                recommendation="Use PDF or DOCX for best compatibility",
                impact_score=10
            ))
            pass_probability -= 10

        pass_probability = max(0, min(100, pass_probability))

        return {
            'platform': 'Workday',
            'market_share': '45%',
            'pass_probability': pass_probability,
            'rating': self._get_rating(pass_probability),
            'issues': [
                {
                    'severity': issue.severity,
                    'message': issue.message,
                    'recommendation': issue.recommendation
                } for issue in issues
            ],
            'summary': self._generate_summary('Workday', pass_probability, len(issues)),
            'parsing_notes': [
                "Workday uses modern parsing with ML assistance",
                "Handles most standard resume formats well",
                "Good at extracting structured data (dates, companies, titles)",
                "Recommended format: Standard PDF or DOCX with clear sections"
            ]
        }

    def simulate_greenhouse(self, resume_text: str, resume_metadata: Dict = None) -> Dict[str, Any]:
        """
        Simulate Greenhouse ATS parsing.

        Greenhouse Characteristics:
        - Most lenient parser, used by modern tech companies
        - Can parse tables, columns, complex layouts
        - Good OCR capabilities for image-based PDFs
        - Excellent contact info extraction
        - Best format support overall

        Pass Rate Baseline: 93% (very forgiving)

        Args:
            resume_text: Full text content of resume
            resume_metadata: Optional metadata

        Returns:
            Dict with platform name, pass probability, issues, recommendations
        """
        issues = []
        pass_probability = 100

        metadata = resume_metadata or {}

        # Info 1: Very complex layouts (even Greenhouse has limits)
        if self._has_very_complex_layout(resume_text):
            issues.append(ATSIssue(
                severity='info',
                message="Very complex layout detected - some formatting may be lost",
                recommendation="Consider simplifying layout for maximum compatibility",
                impact_score=5
            ))
            pass_probability -= 5

        # Info 2: Password-protected or corrupted files
        if metadata.get('parse_quality', 1.0) < 0.5:
            issues.append(ATSIssue(
                severity='warning',
                message="Document parsing quality is low - file may be corrupted",
                recommendation="Try re-saving the document or converting to PDF",
                impact_score=15
            ))
            pass_probability -= 15

        # Info 3: Missing contact information
        if not self._has_contact_info(resume_text):
            issues.append(ATSIssue(
                severity='info',
                message="Contact information not clearly detected",
                recommendation="Add clear contact section with email and phone",
                impact_score=5
            ))
            pass_probability -= 5

        pass_probability = max(0, min(100, pass_probability))

        return {
            'platform': 'Greenhouse',
            'market_share': '15%',
            'pass_probability': pass_probability,
            'rating': self._get_rating(pass_probability),
            'issues': [
                {
                    'severity': issue.severity,
                    'message': issue.message,
                    'recommendation': issue.recommendation
                } for issue in issues
            ],
            'summary': self._generate_summary('Greenhouse', pass_probability, len(issues)),
            'parsing_notes': [
                "Greenhouse uses advanced AI-powered parsing",
                "Most forgiving of formatting variations",
                "Excellent at handling modern resume designs",
                "Can parse creative layouts that fail on other systems"
            ]
        }

    def get_overall_ats_compatibility(self, resume_text: str, resume_metadata: Dict = None) -> Dict[str, Any]:
        """
        Get overall ATS compatibility across all major platforms.

        Weighted by market share:
        - Workday: 45% weight
        - Taleo: 30% weight
        - Greenhouse: 15% weight
        - Buffer: 10% (for other platforms)

        Args:
            resume_text: Full text content
            resume_metadata: Optional metadata

        Returns:
            Dict with overall compatibility score and platform-specific results
        """
        # Run simulations for each platform
        taleo_result = self.simulate_taleo(resume_text, resume_metadata)
        workday_result = self.simulate_workday(resume_text, resume_metadata)
        greenhouse_result = self.simulate_greenhouse(resume_text, resume_metadata)

        # Calculate weighted average (market share based)
        overall_probability = (
            taleo_result['pass_probability'] * 0.30 +
            workday_result['pass_probability'] * 0.45 +
            greenhouse_result['pass_probability'] * 0.15 +
            90 * 0.10  # Assume 90% for other platforms (approximation)
        )

        # Collect all unique critical issues
        all_critical_issues = []
        for result in [taleo_result, workday_result, greenhouse_result]:
            critical = [i for i in result['issues'] if i['severity'] == 'critical']
            for issue in critical:
                if issue['message'] not in [i['message'] for i in all_critical_issues]:
                    all_critical_issues.append(issue)

        # Determine estimated pass rate (how many ATS systems will accept this)
        platforms_passed = sum([
            1 if r['pass_probability'] >= 70 else 0
            for r in [taleo_result, workday_result, greenhouse_result]
        ])

        return {
            'overall_score': round(overall_probability, 1),
            'rating': self._get_rating(overall_probability),
            'platforms_passed': f"{platforms_passed}/3 major platforms",
            'estimated_pass_rate': f"{round(overall_probability)}% of ATS systems",
            'platforms': {
                'Taleo': taleo_result,
                'Workday': workday_result,
                'Greenhouse': greenhouse_result
            },
            'critical_issues': all_critical_issues,
            'recommendations': self._generate_top_recommendations(
                taleo_result, workday_result, greenhouse_result
            ),
            'summary': self._generate_overall_summary(
                overall_probability, platforms_passed, len(all_critical_issues)
            )
        }

    # Helper methods for format detection

    def _has_tables(self, text: str) -> bool:
        """Detect if resume contains tables"""
        table_indicators = [
            r'\|[\s\w]+\|',  # Markdown tables
            r'<table>',       # HTML tables
            r'\\begin{tabular}',  # LaTeX tables
            # Heuristic: Multiple tab characters in a row
            r'\t{2,}',
        ]
        return any(re.search(pattern, text, re.IGNORECASE) for pattern in table_indicators)

    def _has_complex_tables(self, text: str) -> bool:
        """Detect complex nested tables"""
        # Look for nested table structures or tables within tables
        if '<table>' in text.lower():
            # Count table tags
            table_count = text.lower().count('<table>')
            return table_count > 1
        return False

    def _has_text_boxes(self, text: str) -> bool:
        """Detect text boxes"""
        return any(indicator in text.lower() for indicator in self.problematic_elements['text_boxes'])

    def _has_headers_footers(self, text: str, metadata: Dict) -> bool:
        """Detect if important content is in headers/footers"""
        # If metadata indicates headers/footers exist
        if metadata.get('has_headers') or metadata.get('has_footers'):
            return True
        return False

    def _has_columns(self, text: str) -> bool:
        """Detect multi-column layout"""
        # Heuristic: Look for column indicators or unusual spacing patterns
        column_indicators = [
            r'\\begin{multicols}',
            r'column-count:',
        ]
        return any(re.search(pattern, text, re.IGNORECASE) for pattern in column_indicators)

    def _has_graphics(self, text: str) -> bool:
        """Detect images or graphics"""
        return any(indicator in text.lower() for indicator in self.problematic_elements['graphics'])

    def _has_very_complex_layout(self, text: str) -> bool:
        """Detect very complex layouts that might challenge even good parsers"""
        complexity_score = 0

        if self._has_tables(text):
            complexity_score += 1
        if self._has_columns(text):
            complexity_score += 1
        if self._has_graphics(text):
            complexity_score += 1
        if len(re.findall(r'[^\x00-\x7F]', text)) > 100:
            complexity_score += 1

        return complexity_score >= 3

    def _has_contact_info(self, text: str) -> bool:
        """Detect if resume has basic contact information"""
        has_email = bool(re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text))
        has_phone = bool(re.search(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', text))

        return has_email or has_phone

    def _detect_sections(self, text: str) -> List[str]:
        """Detect section headers in resume"""
        # Common section header patterns
        section_pattern = r'^([A-Z][A-Z\s&]+)$'
        sections = re.findall(section_pattern, text, re.MULTILINE)

        # Also check for headers with underlines or after newlines
        sections.extend(re.findall(r'\n([A-Z][A-Z\s&]+)\n', text))

        return list(set(sections))  # Remove duplicates

    def _get_rating(self, probability: float) -> str:
        """Convert probability to human-readable rating"""
        if probability >= 90:
            return "Excellent"
        elif probability >= 80:
            return "Very Good"
        elif probability >= 70:
            return "Good"
        elif probability >= 60:
            return "Fair"
        else:
            return "Needs Improvement"

    def _generate_summary(self, platform: str, probability: float, issue_count: int) -> str:
        """Generate human-readable summary for a platform"""
        rating = self._get_rating(probability)

        if probability >= 90:
            return f"{platform} will likely parse your resume correctly. {rating} compatibility!"
        elif probability >= 70:
            return f"{platform} will probably parse your resume, but {issue_count} improvement(s) recommended."
        elif probability >= 50:
            return f"{platform} may have difficulty parsing your resume. {issue_count} issue(s) should be addressed."
        else:
            return f"{platform} will likely fail to parse your resume correctly. Critical issues found."

    def _generate_overall_summary(self, probability: float, platforms_passed: int, critical_count: int) -> str:
        """Generate overall ATS compatibility summary"""
        if platforms_passed == 3 and critical_count == 0:
            return "Excellent! Your resume is compatible with all major ATS platforms."
        elif platforms_passed >= 2:
            return f"Good compatibility. Your resume will pass {platforms_passed} out of 3 major ATS platforms."
        elif platforms_passed == 1:
            return f"Limited compatibility. Your resume needs improvements to pass most ATS systems."
        else:
            return "Poor compatibility. Your resume has critical issues that will prevent ATS parsing."

    def _generate_top_recommendations(self, taleo_result: Dict, workday_result: Dict, greenhouse_result: Dict) -> List[str]:
        """Generate top 3-5 recommendations across all platforms"""
        all_recommendations = []

        # Collect all recommendations with their severity
        for result in [taleo_result, workday_result, greenhouse_result]:
            for issue in result['issues']:
                if issue['severity'] in ['critical', 'warning']:
                    rec = issue['recommendation']
                    if rec not in all_recommendations:
                        all_recommendations.append(rec)

        # Return top 5 (or all if less than 5)
        return all_recommendations[:5]


# Convenience function for quick analysis
def analyze_ats_compatibility(resume_text: str, resume_metadata: Dict = None) -> Dict[str, Any]:
    """
    Quick function to analyze ATS compatibility.

    Usage:
        result = analyze_ats_compatibility(resume_text)
        print(f"Overall Score: {result['overall_score']}")
        print(f"Rating: {result['rating']}")
    """
    simulator = ATSSimulator()
    return simulator.get_overall_ats_compatibility(resume_text, resume_metadata)
