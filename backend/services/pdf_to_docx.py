"""
PDF to DOCX conversion service using LibreOffice headless.

Falls back to the pdf2docx library if LibreOffice is not installed.
"""
import io
import logging
import subprocess
import shutil
import tempfile
import os

logger = logging.getLogger(__name__)

# Try to find LibreOffice / soffice binary
_SOFFICE_PATHS = [
    shutil.which("soffice"),
    shutil.which("libreoffice"),
    "/Applications/LibreOffice.app/Contents/MacOS/soffice",  # macOS
    "/usr/bin/soffice",       # Linux
    "/usr/bin/libreoffice",   # Linux alt
]
SOFFICE_BIN = next((p for p in _SOFFICE_PATHS if p and os.path.isfile(p)), None)


def convert_pdf_to_docx_libreoffice(pdf_bytes: bytes) -> bytes:
    """
    Convert PDF bytes to DOCX bytes using LibreOffice headless.

    Args:
        pdf_bytes: PDF file content as bytes

    Returns:
        DOCX file content as bytes

    Raises:
        Exception: If conversion fails or LibreOffice is not available
    """
    if not SOFFICE_BIN:
        raise RuntimeError(
            "LibreOffice (soffice) not found. "
            "Install it via `brew install --cask libreoffice` on macOS "
            "or `apt install libreoffice` on Linux."
        )

    logger.info(f"Converting PDF to DOCX using LibreOffice ({SOFFICE_BIN})...")

    with tempfile.TemporaryDirectory() as tmpdir:
        input_path = os.path.join(tmpdir, "input.pdf")
        with open(input_path, "wb") as f:
            f.write(pdf_bytes)

        try:
            result = subprocess.run(
                [
                    SOFFICE_BIN,
                    "--headless",
                    "--infilter=writer_pdf_import",
                    "--convert-to", "docx",
                    "--outdir", tmpdir,
                    input_path,
                ],
                capture_output=True,
                text=True,
                timeout=60,  # 60 second timeout
            )

            if result.returncode != 0:
                logger.error(f"LibreOffice stderr: {result.stderr}")
                raise RuntimeError(f"LibreOffice conversion failed: {result.stderr}")

            # LibreOffice outputs to <input_basename>.docx in outdir
            output_path = os.path.join(tmpdir, "input.docx")
            if not os.path.exists(output_path):
                # Sometimes the extension differs
                for fname in os.listdir(tmpdir):
                    if fname.endswith(".docx"):
                        output_path = os.path.join(tmpdir, fname)
                        break
                else:
                    raise RuntimeError(
                        f"LibreOffice ran but no .docx output found. "
                        f"Files in tmpdir: {os.listdir(tmpdir)}"
                    )

            with open(output_path, "rb") as f:
                docx_bytes = f.read()

            logger.info(f"PDF converted to DOCX successfully ({len(docx_bytes)} bytes)")
            return docx_bytes

        except subprocess.TimeoutExpired:
            raise RuntimeError("LibreOffice conversion timed out (60s)")


def convert_pdf_to_docx(pdf_bytes: bytes) -> bytes:
    """
    Convert PDF bytes to DOCX bytes.

    Uses LibreOffice headless if available, otherwise falls back to pdf2docx.

    Args:
        pdf_bytes: PDF file content as bytes

    Returns:
        DOCX file content as bytes
    """
    # Prefer LibreOffice
    if SOFFICE_BIN:
        return convert_pdf_to_docx_libreoffice(pdf_bytes)

    # Fallback: pdf2docx library
    logger.warning("LibreOffice not available, falling back to pdf2docx")
    try:
        from pdf2docx import Converter

        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as pdf_temp:
            pdf_temp.write(pdf_bytes)
            pdf_path = pdf_temp.name

        with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as docx_temp:
            docx_path = docx_temp.name

        try:
            cv = Converter(pdf_path)
            cv.convert(docx_path, start=0, end=None)
            cv.close()

            with open(docx_path, 'rb') as f:
                docx_bytes = f.read()

            logger.info(f"PDF converted to DOCX via pdf2docx ({len(docx_bytes)} bytes)")
            return docx_bytes
        finally:
            if os.path.exists(pdf_path):
                os.unlink(pdf_path)
            if os.path.exists(docx_path):
                os.unlink(docx_path)

    except ImportError:
        raise RuntimeError(
            "Neither LibreOffice nor pdf2docx is available for PDF→DOCX conversion."
        )
