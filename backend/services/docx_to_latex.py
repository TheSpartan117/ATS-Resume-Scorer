"""
DOCX to LaTeX Converter
Converts uploaded DOCX files to LaTeX format for editing
"""
from docx import Document
from typing import List, Dict
import re


class DocxToLatexConverter:
    """Convert DOCX resume to LaTeX format"""

    def __init__(self):
        self.latex_output = []

    def convert(self, docx_path: str) -> str:
        """
        Convert DOCX file to LaTeX

        Args:
            docx_path: Path to DOCX file

        Returns:
            LaTeX string
        """
        doc = Document(docx_path)

        # Start LaTeX document
        self.latex_output = [
            "\\documentclass[11pt,a4paper]{article}",
            "\\usepackage[utf8]{inputenc}",
            "\\usepackage[margin=1in]{geometry}",
            "\\usepackage{enumitem}",
            "\\usepackage{hyperref}",
            "\\usepackage{parskip}",
            "",
            "\\begin{document}",
            ""
        ]

        # Process paragraphs
        current_list = None
        for para in doc.paragraphs:
            text = para.text.strip()

            if not text:
                # Empty paragraph - add spacing
                if current_list:
                    self.latex_output.append("\\end{itemize}")
                    current_list = None
                self.latex_output.append("")
                continue

            # Detect headings/sections (all caps, short, or specific patterns)
            if self._is_heading(text, para):
                if current_list:
                    self.latex_output.append("\\end{itemize}")
                    current_list = None

                # Add section
                latex_text = self._escape_latex(text)
                self.latex_output.append(f"\\section*{{{latex_text}}}")
                self.latex_output.append("")

            # Detect bullet points
            elif self._is_bullet(text):
                if not current_list:
                    self.latex_output.append("\\begin{itemize}[leftmargin=*]")
                    current_list = True

                bullet_text = self._remove_bullet(text)
                bullet_text = self._escape_latex(bullet_text)
                self.latex_output.append(f"  \\item {bullet_text}")

            # Regular paragraph
            else:
                if current_list:
                    self.latex_output.append("\\end{itemize}")
                    current_list = None

                # Apply formatting
                latex_text = self._apply_formatting(text, para)
                self.latex_output.append(latex_text)

        # Close any open list
        if current_list:
            self.latex_output.append("\\end{itemize}")

        # End document
        self.latex_output.append("")
        self.latex_output.append("\\end{document}")

        return "\n".join(self.latex_output)

    def _is_heading(self, text: str, para) -> bool:
        """Detect if paragraph is a heading"""
        # Check if all caps
        if len(text) > 2 and text.isupper() and len(text) < 50:
            return True

        # Check if bold and short
        if para.runs and len(para.runs) > 0:
            if para.runs[0].bold and len(text) < 80:
                # Common section names
                sections = [
                    'experience', 'education', 'skills', 'summary',
                    'objective', 'projects', 'certifications', 'awards',
                    'publications', 'languages', 'interests', 'contact'
                ]
                if any(section in text.lower() for section in sections):
                    return True

        return False

    def _is_bullet(self, text: str) -> bool:
        """Detect if text is a bullet point"""
        bullets = ['•', '●', '○', '◦', '▪', '▫', '–', '-', '*']
        return any(text.startswith(b) for b in bullets)

    def _remove_bullet(self, text: str) -> str:
        """Remove bullet character from text"""
        bullets = ['•', '●', '○', '◦', '▪', '▫', '–', '-', '*']
        for bullet in bullets:
            if text.startswith(bullet):
                return text[len(bullet):].strip()
        return text

    def _escape_latex(self, text: str) -> str:
        """Escape special LaTeX characters"""
        # Characters that need escaping
        replacements = {
            '\\': '\\textbackslash{}',
            '{': '\\{',
            '}': '\\}',
            '$': '\\$',
            '&': '\\&',
            '%': '\\%',
            '#': '\\#',
            '_': '\\_',
            '~': '\\textasciitilde{}',
            '^': '\\textasciicircum{}',
        }

        result = text
        for char, replacement in replacements.items():
            result = result.replace(char, replacement)

        return result

    def _apply_formatting(self, text: str, para) -> str:
        """Apply bold, italic, underline formatting"""
        # For now, just escape and return
        # TODO: Detect run-level formatting
        latex_text = self._escape_latex(text)

        # Check if entire paragraph is bold
        if para.runs and all(run.bold for run in para.runs if run.text.strip()):
            latex_text = f"\\textbf{{{latex_text}}}"

        # Check if entire paragraph is italic
        elif para.runs and all(run.italic for run in para.runs if run.text.strip()):
            latex_text = f"\\textit{{{latex_text}}}"

        # Add line break at end
        latex_text += " \\\\"

        return latex_text


def convert_docx_to_latex(docx_path: str) -> str:
    """
    Convert DOCX file to LaTeX

    Args:
        docx_path: Path to DOCX file

    Returns:
        LaTeX string
    """
    converter = DocxToLatexConverter()
    return converter.convert(docx_path)
