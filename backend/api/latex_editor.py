"""
LaTeX Editor API Endpoints
Handles DOCX to LaTeX conversion and LaTeX editing
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from typing import Optional
import logging
import tempfile
import os
from pathlib import Path

from backend.services.docx_to_latex import convert_docx_to_latex

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/latex", tags=["latex-editor"])


class ConvertResponse(BaseModel):
    latex_code: str
    filename: str


@router.post("/convert", response_model=ConvertResponse)
async def convert_docx_to_latex_endpoint(file: UploadFile = File(...)):
    """
    Convert uploaded DOCX file to LaTeX

    Args:
        file: Uploaded DOCX file

    Returns:
        LaTeX code and filename
    """
    if not file.filename.endswith('.docx'):
        raise HTTPException(status_code=400, detail="Only DOCX files are supported")

    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name

        # Convert to LaTeX
        latex_code = convert_docx_to_latex(tmp_path)

        # Clean up temp file
        os.unlink(tmp_path)

        # Extract filename without extension
        base_filename = Path(file.filename).stem

        logger.info(f"Successfully converted {file.filename} to LaTeX")

        return ConvertResponse(
            latex_code=latex_code,
            filename=base_filename
        )

    except Exception as e:
        logger.error(f"Failed to convert DOCX to LaTeX: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Conversion failed: {str(e)}")


class CompileRequest(BaseModel):
    latex_code: str


@router.post("/compile")
async def compile_latex(request: CompileRequest):
    """
    Compile LaTeX to PDF (future implementation)

    For now, this endpoint acknowledges the request but doesn't compile.
    Frontend handles PDF export using html2pdf.js

    Args:
        request: LaTeX code to compile

    Returns:
        Status message
    """
    # This is a placeholder for future server-side LaTeX compilation
    # Currently, we use LaTeX.js in the browser for rendering
    # and html2pdf.js for PDF export

    return {
        "status": "acknowledged",
        "message": "PDF export is handled client-side via html2pdf.js",
        "note": "For server-side compilation, install TeX Live and uncomment implementation"
    }

    # TODO: Implement server-side compilation with TeX Live
    # try:
    #     with tempfile.TemporaryDirectory() as tmpdir:
    #         tex_path = Path(tmpdir) / "resume.tex"
    #         tex_path.write_text(request.latex_code)
    #
    #         # Compile with pdflatex
    #         result = subprocess.run(
    #             ['pdflatex', '-interaction=nonstopmode', 'resume.tex'],
    #             cwd=tmpdir,
    #             capture_output=True,
    #             timeout=30
    #         )
    #
    #         if result.returncode != 0:
    #             raise Exception(f"LaTeX compilation failed: {result.stderr.decode()}")
    #
    #         pdf_path = Path(tmpdir) / "resume.pdf"
    #         if not pdf_path.exists():
    #             raise Exception("PDF file not generated")
    #
    #         pdf_bytes = pdf_path.read_bytes()
    #
    #         return Response(
    #             content=pdf_bytes,
    #             media_type="application/pdf",
    #             headers={"Content-Disposition": "attachment; filename=resume.pdf"}
    #         )
    #
    # except Exception as e:
    #     logger.error(f"LaTeX compilation failed: {e}", exc_info=True)
    #     raise HTTPException(status_code=500, detail=str(e))


@router.get("/templates")
async def get_latex_templates():
    """
    Get available LaTeX resume templates

    Returns:
        List of template names and descriptions
    """
    templates = [
        {
            "id": "modern",
            "name": "Modern Resume",
            "description": "Clean and professional design with clear sections"
        },
        {
            "id": "classic",
            "name": "Classic Resume",
            "description": "Traditional format with serif font"
        },
        {
            "id": "academic",
            "name": "Academic CV",
            "description": "Detailed format for academia and research"
        },
        {
            "id": "technical",
            "name": "Technical Resume",
            "description": "Optimized for software engineers and developers"
        }
    ]

    return {"templates": templates}
