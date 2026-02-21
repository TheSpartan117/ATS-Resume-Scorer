"""
P3.4: ATS-Friendly Formatting (7 points)

Penalizes formatting that causes ATS parsing failures.

Penalty Structure:
- Tables/columns: -2 pts (parsing issues)
- Text boxes: -2 pts (text extraction fails)
- Headers/footers: -1 pt (inconsistent parsing)
- Images/graphics: -1 pt (unparseable)
- Fancy fonts: -1 pt (character recognition issues)

Scoring:
- Start with 7 points
- Deduct penalties
- Minimum 0 points

Research Basis:
- Workday/Greenhouse/Lever ATS limitations
- Tables cause column misalignment in parsing
- Text boxes often completely missed by parsers
- Headers/footers inconsistently extracted
- Images unparseable and increase file size
- Fancy fonts cause OCR/character recognition errors
"""

from typing import Dict, List, Any, Optional


# Standard ATS-friendly fonts
STANDARD_FONTS = {
    'Calibri', 'Arial', 'Times New Roman', 'Helvetica',
    'Georgia', 'Verdana', 'Tahoma', 'Trebuchet MS',
    'Garamond', 'Cambria', 'Book Antiqua', 'Palatino Linotype',
    'Century Gothic', 'Franklin Gothic', 'Lucida Sans',
    'Lucida Sans Unicode', 'Lucida Grande'
}

# Fancy/decorative fonts that cause ATS issues
FANCY_FONTS = {
    'Comic Sans MS', 'Papyrus', 'Curlz MT', 'Brush Script MT',
    'Lucida Handwriting', 'Chiller', 'Jokerman', 'Impact',
    'Kunstler Script', 'Mistral', 'Monotype Corsiva',
    'Script MT Bold', 'Vivaldi', 'Vladimir Script'
}


class ATSFormattingScorer:
    """Scores resume based on ATS-friendly formatting."""

    def __init__(self):
        """Initialize scorer with formatting rules."""
        self.max_score = 7

    def score(
        self,
        resume: Any,
        docx_structure: Optional[Dict] = None,
        file_format: str = 'docx'
    ) -> Dict[str, Any]:
        """
        Score ATS-friendly formatting.

        Args:
            resume: Resume data object
            docx_structure: Parsed DOCX structure (if available)
            file_format: File format ('pdf' or 'docx')

        Returns:
            Dictionary containing:
            - score: Total points (0-7)
            - file_format: File format used
            - has_tables: Whether tables detected
            - has_text_boxes: Whether text boxes detected
            - has_headers_footers: Whether headers/footers detected
            - has_images: Whether images detected
            - has_fancy_fonts: Whether fancy fonts detected
            - total_penalties: Total penalty points
            - issues_found: List of issue descriptions
        """
        penalties = 0
        issues = []

        # Initialize detection flags
        has_tables = False
        has_text_boxes = False
        has_headers_footers = False
        has_images = False
        has_fancy_fonts = False

        # Check based on available data
        if file_format == 'docx' and docx_structure:
            # Full structure analysis for DOCX
            has_tables = self._check_tables(docx_structure)
            has_text_boxes = self._check_text_boxes(docx_structure)
            has_headers_footers = self._check_headers_footers(docx_structure)
            has_images_structure = self._check_images_structure(docx_structure)
            has_fancy_fonts = self._check_fancy_fonts(docx_structure)

            # Check metadata for images
            has_images_metadata = self._check_images_metadata(resume)
            has_images = has_images_structure or has_images_metadata

        elif file_format == 'pdf':
            # Limited checks for PDF (mostly metadata)
            has_images = self._check_images_metadata(resume)
            # PDFs get benefit of doubt for structure issues we can't detect
            # Could add heuristics here later

        else:
            # file_format == 'docx' but no structure provided
            # Check metadata only
            has_images = self._check_images_metadata(resume)
            # Give benefit of doubt for other issues

        # Calculate penalties
        if has_tables:
            penalties += 2
            issues.append("Tables detected (-2 pts): Tables cause column misalignment in ATS parsing")

        if has_text_boxes:
            penalties += 2
            issues.append("Text boxes detected (-2 pts): Text boxes often completely missed by ATS parsers")

        if has_headers_footers:
            penalties += 1
            issues.append("Headers/footers detected (-1 pt): Headers/footers inconsistently extracted by ATS")

        if has_images:
            penalties += 1
            issues.append("Images/graphics detected (-1 pt): Images are unparseable and increase file size")

        if has_fancy_fonts:
            penalties += 1
            issues.append("Fancy fonts detected (-1 pt): Decorative fonts cause OCR/character recognition errors")

        # Calculate final score
        final_score = max(0, self.max_score - penalties)

        return {
            'score': final_score,
            'file_format': file_format,
            'has_tables': has_tables,
            'has_text_boxes': has_text_boxes,
            'has_headers_footers': has_headers_footers,
            'has_images': has_images,
            'has_fancy_fonts': has_fancy_fonts,
            'total_penalties': penalties,
            'issues_found': issues
        }

    def _check_tables(self, docx_structure: Dict) -> bool:
        """Check if resume contains tables."""
        if not docx_structure:
            return False

        sections = docx_structure.get('sections', [])
        for section in sections:
            tables = section.get('tables', [])
            if tables and len(tables) > 0:
                return True

        return False

    def _check_text_boxes(self, docx_structure: Dict) -> bool:
        """Check if resume contains text boxes."""
        if not docx_structure:
            return False

        sections = docx_structure.get('sections', [])
        for section in sections:
            text_boxes = section.get('text_boxes', [])
            if text_boxes and len(text_boxes) > 0:
                return True

        return False

    def _check_headers_footers(self, docx_structure: Dict) -> bool:
        """Check if resume contains headers or footers."""
        if not docx_structure:
            return False

        has_header = docx_structure.get('has_header', False)
        has_footer = docx_structure.get('has_footer', False)

        return has_header or has_footer

    def _check_images_structure(self, docx_structure: Dict) -> bool:
        """Check if resume contains images in DOCX structure."""
        if not docx_structure:
            return False

        sections = docx_structure.get('sections', [])
        for section in sections:
            images = section.get('images', [])
            if images and len(images) > 0:
                return True

        return False

    def _check_images_metadata(self, resume: Any) -> bool:
        """Check if resume contains images from metadata."""
        if not resume:
            return False

        # Check metadata attribute
        if hasattr(resume, 'metadata'):
            metadata = resume.metadata
            if metadata:
                if isinstance(metadata, dict):
                    return metadata.get('hasPhoto', False)
                # If metadata is an object
                if hasattr(metadata, 'hasPhoto'):
                    return metadata.hasPhoto

        return False

    def _check_fancy_fonts(self, docx_structure: Dict) -> bool:
        """Check if resume uses fancy/decorative fonts."""
        if not docx_structure:
            return False

        sections = docx_structure.get('sections', [])

        for section in sections:
            paragraphs = section.get('paragraphs', [])

            for paragraph in paragraphs:
                runs = paragraph.get('runs', [])

                for run in runs:
                    formatting = run.get('formatting', {})
                    font_name = formatting.get('font_name', 'Calibri')

                    # Check if font is fancy
                    if self._is_fancy_font(font_name):
                        return True

        return False

    def _is_fancy_font(self, font_name: str) -> bool:
        """
        Determine if a font is fancy/decorative.

        Args:
            font_name: Font name

        Returns:
            True if fancy, False if standard
        """
        if not font_name:
            return False

        # Normalize font name
        font_normalized = font_name.strip()

        # Check if in fancy fonts list
        if font_normalized in FANCY_FONTS:
            return True

        # Check if in standard fonts list
        if font_normalized in STANDARD_FONTS:
            return False

        # Check for decorative keywords
        decorative_keywords = [
            'script', 'handwriting', 'brush', 'comic',
            'casual', 'decorative', 'fantasy', 'display'
        ]

        font_lower = font_normalized.lower()
        for keyword in decorative_keywords:
            if keyword in font_lower:
                return True

        # Default to standard (benefit of doubt)
        return False


def score_ats_formatting(
    resume: Any,
    docx_structure: Optional[Dict] = None,
    file_format: str = 'docx'
) -> Dict[str, Any]:
    """
    Convenience function to score ATS formatting.

    Args:
        resume: Resume data object
        docx_structure: Parsed DOCX structure (if available)
        file_format: File format ('pdf' or 'docx')

    Returns:
        Score result dictionary
    """
    scorer = ATSFormattingScorer()
    return scorer.score(resume, docx_structure, file_format)
