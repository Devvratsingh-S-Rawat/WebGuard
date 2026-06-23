from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from datetime import datetime
import io

SEVERITY_COLORS = {
    "critical": colors.HexColor("#e24b4a"),
    "high":     colors.HexColor("#ef9f27"),
    "medium":   colors.HexColor("#f5c542"),
    "low":      colors.HexColor("#3b8bd4"),
    "info":     colors.HexColor("#888888"),
}

BG_DARK   = colors.HexColor("#0a0a0f")
BG_CARD   = colors.HexColor("#111118")
TEAL      = colors.HexColor("#00d4aa")
TEXT_MAIN = colors.HexColor("#e2e8f0")
TEXT_MUTED= colors.HexColor("#94a3b8")

def generate_pdf(scan_data: dict) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )

    styles = getSampleStyleSheet()
    elements = []

    # --- Title ---
    title_style = ParagraphStyle(
        "Title", fontSize=24, textColor=TEAL,
        fontName="Helvetica-Bold", alignment=TA_CENTER, spaceAfter=4
    )
    sub_style = ParagraphStyle(
        "Sub", fontSize=11, textColor=TEXT_MUTED,
        fontName="Helvetica", alignment=TA_CENTER, spaceAfter=2
    )
    normal_style = ParagraphStyle(
        "Normal2", fontSize=9, textColor=TEXT_MAIN,
        fontName="Helvetica", spaceAfter=4
    )
    muted_style = ParagraphStyle(
        "Muted", fontSize=8, textColor=TEXT_MUTED,
        fontName="Helvetica", spaceAfter=4
    )
    section_style = ParagraphStyle(
        "Section", fontSize=13, textColor=TEAL,
        fontName="Helvetica-Bold", spaceAfter=6, spaceBefore=12
    )
    scanner_style = ParagraphStyle(
        "Scanner", fontSize=11, textColor=TEXT_MAIN,
        fontName="Helvetica-Bold", spaceAfter=4, spaceBefore=8
    )

    elements.append(Paragraph("🛡 WebGuard", title_style))
    elements.append(Paragraph("Website Vulnerability Scan Report", sub_style))
    elements.append(Spacer(1, 0.3*cm))
    elements.append(HRFlowable(width="100%", thickness=1, color=TEAL))
    elements.append(Spacer(1, 0.3*cm))

    # --- Scan Info ---
    scan_date = datetime.now().strftime("%B %d, %Y at %H:%M UTC")
    elements.append(Paragraph(f"<b>Target:</b> {scan_data.get('target', 'N/A')}", normal_style))
    elements.append(Paragraph(f"<b>Scan Date:</b> {scan_date}", normal_style))
    elements.append(Paragraph(f"<b>Total Findings:</b> {scan_data.get('total_findings', 0)}", normal_style))
    elements.append(Spacer(1, 0.4*cm))

    # --- Summary Table ---
    elements.append(Paragraph("Executive Summary", section_style))
    summary = scan_data.get("summary", {})
    summary_data = [
        ["Severity", "Count"],
        ["Critical", str(summary.get("critical", 0))],
        ["High",     str(summary.get("high", 0))],
        ["Medium",   str(summary.get("medium", 0))],
        ["Low",      str(summary.get("low", 0))],
        ["Info",     str(summary.get("info", 0))],
    ]
    summary_table = Table(summary_data, colWidths=[8*cm, 4*cm])
    summary_table.setStyle(TableStyle([
        ("BACKGROUND",  (0,0), (-1,0), BG_CARD),
        ("TEXTCOLOR",   (0,0), (-1,0), TEAL),
        ("FONTNAME",    (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",    (0,0), (-1,-1), 9),
        ("BACKGROUND",  (0,1), (-1,-1), BG_DARK),
        ("TEXTCOLOR",   (0,1), (-1,-1), TEXT_MAIN),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [BG_DARK, BG_CARD]),
        ("GRID",        (0,0), (-1,-1), 0.5, colors.HexColor("#2d2d3d")),
        ("ALIGN",       (1,0), (1,-1), "CENTER"),
        ("LEFTPADDING", (0,0), (-1,-1), 8),
        ("RIGHTPADDING",(0,0), (-1,-1), 8),
        ("TOPPADDING",  (0,0), (-1,-1), 5),
        ("BOTTOMPADDING",(0,0), (-1,-1), 5),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 0.5*cm))

    # --- Findings ---
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#2d2d3d")))
    elements.append(Paragraph("Detailed Findings", section_style))

    for result in scan_data.get("results", []):
        elements.append(Paragraph(f"► {result['scanner']}", scanner_style))
        for finding in result.get("findings", []):
            sev = finding.get("severity", "info")
            sev_color = SEVERITY_COLORS.get(sev, colors.grey)

            finding_data = [
                [Paragraph(f"<b>{finding['title']}</b>", normal_style),
                 Paragraph(f"<b>{sev.upper()}</b>", ParagraphStyle("Sev", fontSize=8, textColor=sev_color, fontName="Helvetica-Bold", alignment=TA_LEFT))],
                [Paragraph(finding.get("description", ""), muted_style), ""],
                [Paragraph(f"💡 {finding.get('recommendation', '')}", ParagraphStyle("Rec", fontSize=8, textColor=TEAL, fontName="Helvetica")), ""],
            ]
            finding_table = Table(finding_data, colWidths=[13*cm, 3*cm])
            finding_table.setStyle(TableStyle([
                ("BACKGROUND",  (0,0), (-1,-1), BG_CARD),
                ("GRID",        (0,0), (-1,-1), 0.5, colors.HexColor("#2d2d3d")),
                ("SPAN",        (0,1), (1,1)),
                ("SPAN",        (0,2), (1,2)),
                ("LEFTPADDING", (0,0), (-1,-1), 8),
                ("RIGHTPADDING",(0,0), (-1,-1), 8),
                ("TOPPADDING",  (0,0), (-1,-1), 4),
                ("BOTTOMPADDING",(0,0), (-1,-1), 4),
                ("LINEABOVE",   (0,0), (-1,0), 1, sev_color),
            ]))
            elements.append(finding_table)
            elements.append(Spacer(1, 0.2*cm))

    # --- Footer ---
    elements.append(Spacer(1, 0.5*cm))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=TEAL))
    elements.append(Spacer(1, 0.2*cm))
    elements.append(Paragraph(
        "Generated by WebGuard — Website Vulnerability Scanner | For educational purposes only",
        ParagraphStyle("Footer", fontSize=7, textColor=TEXT_MUTED, alignment=TA_CENTER)
    ))

    doc.build(elements)
    buffer.seek(0)
    return buffer.read()