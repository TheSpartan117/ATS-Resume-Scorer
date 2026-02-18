"""Export API for resume and report downloads"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from typing import Dict, Optional
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from docx import Document

router = APIRouter(prefix="/api/export", tags=["export"])


class ExportResumeRequest(BaseModel):
    content: str  # HTML content
    name: str
    format: str  # "pdf" or "docx"


class ExportReportRequest(BaseModel):
    resumeData: Dict
    scoreData: Dict
    mode: str
    role: str
    level: str


@router.post("/resume")
async def export_resume(request: ExportResumeRequest):
    """Export edited resume as PDF or DOCX"""

    if request.format == "pdf":
        # Simple PDF generation with text wrapping
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)

        # Strip HTML tags for simple text
        import re
        text = re.sub('<[^<]+?>', '', request.content)

        # Page dimensions
        page_width = 612  # letter size width in points
        margin = 50
        max_width = page_width - (2 * margin)

        y = 750

        for line in text.split('\n'):
            # Skip empty lines but preserve spacing
            if not line.strip():
                y -= 15
                if y < 50:
                    c.showPage()
                    y = 750
                continue

            # Check if this line looks like a section header (short, uppercase words)
            is_header = len(line.strip().split()) <= 3 and any(word.isupper() for word in line.strip().split())

            if is_header:
                c.setFont("Helvetica-Bold", 14)
            else:
                c.setFont("Helvetica", 11)

            # Word wrap long lines
            words = line.split()
            current_line = []

            for word in words:
                test_line = ' '.join(current_line + [word])
                text_width = c.stringWidth(test_line, c._fontname, c._fontsize)

                if text_width <= max_width:
                    current_line.append(word)
                else:
                    # Draw current line and start new one
                    if current_line:
                        if y < 50:
                            c.showPage()
                            y = 750
                        c.drawString(margin, y, ' '.join(current_line))
                        y -= 15
                    current_line = [word]

            # Draw remaining words
            if current_line:
                if y < 50:
                    c.showPage()
                    y = 750
                c.drawString(margin, y, ' '.join(current_line))
                y -= 15

        c.save()
        buffer.seek(0)

        filename = f"{request.name.replace(' ', '_')}_Resume.pdf"

        return Response(
            content=buffer.read(),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )

    elif request.format == "docx":
        # Simple DOCX generation
        doc = Document()

        # Strip HTML for simple text
        import re
        text = re.sub('<[^<]+?>', '', request.content)

        for line in text.split('\n'):
            if line.strip():
                doc.add_paragraph(line)

        buffer = io.BytesIO()
        doc.save(buffer)
        buffer.seek(0)

        filename = f"{request.name.replace(' ', '_')}_Resume.docx"

        return Response(
            content=buffer.read(),
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )

    else:
        raise HTTPException(400, "Invalid format. Use 'pdf' or 'docx'")


@router.post("/report")
async def export_score_report(request: ExportReportRequest):
    """Export ATS score report as PDF"""

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)

    # Title
    c.setFont("Helvetica-Bold", 18)
    name = request.resumeData.get("contact", {}).get("name", "Resume")
    c.drawString(50, 750, f"ATS Resume Report - {name}")

    # Mode
    c.setFont("Helvetica", 12)
    mode_text = "ATS Simulation Mode" if request.mode == "ats_simulation" else "Quality Coach Mode"
    c.drawString(50, 720, f"Mode: {mode_text}")

    # Score
    c.setFont("Helvetica-Bold", 14)
    score = request.scoreData.get("overall_score", 0)
    c.drawString(50, 690, f"Score: {score}/100")

    # Breakdown
    y = 660
    c.setFont("Helvetica", 11)
    c.drawString(50, y, "Breakdown:")
    y -= 20

    breakdown = request.scoreData.get("breakdown", {})
    for category, score_val in breakdown.items():
        c.drawString(60, y, f"• {category.replace('_', ' ').title()}: {score_val}")
        y -= 15

    c.save()
    buffer.seek(0)

    filename = f"{name.replace(' ', '_')}_ATS_Report.pdf"

    return Response(
        content=buffer.read(),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
