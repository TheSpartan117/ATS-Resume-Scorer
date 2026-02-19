"""
PDF to DOCX conversion service using pdf2docx
"""
import io
import logging
from pdf2docx import Converter
import tempfile
import os

logger = logging.getLogger(__name__)


def convert_pdf_to_docx(pdf_bytes: bytes) -> bytes:
    """
    Convert PDF bytes to DOCX bytes

    Args:
        pdf_bytes: PDF file content as bytes

    Returns:
        DOCX file content as bytes

    Raises:
        Exception: If conversion fails
    """
    try:
        logger.info("Converting PDF to DOCX using pdf2docx...")

        # Create temporary files for input PDF and output DOCX
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as pdf_temp:
            pdf_temp.write(pdf_bytes)
            pdf_path = pdf_temp.name

        with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as docx_temp:
            docx_path = docx_temp.name

        try:
            # Convert PDF to DOCX
            cv = Converter(pdf_path)
            cv.convert(docx_path, start=0, end=None)
            cv.close()

            # Read the converted DOCX
            with open(docx_path, 'rb') as f:
                docx_bytes = f.read()

            logger.info(f"PDF converted to DOCX successfully ({len(docx_bytes)} bytes)")
            return docx_bytes

        finally:
            # Clean up temporary files
            if os.path.exists(pdf_path):
                os.unlink(pdf_path)
            if os.path.exists(docx_path):
                os.unlink(docx_path)

    except Exception as e:
        logger.error(f"Failed to convert PDF to DOCX: {str(e)}")
        raise Exception(f"PDF to DOCX conversion failed: {str(e)}")
