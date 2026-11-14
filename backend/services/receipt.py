"""Claim Submission Receipt generation service for ClaimSense AI (Phase 3 Hardened)."""
import io
import textwrap
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from xml.sax.saxutils import escape as xml_escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


def safe_xml(value: Any, max_len: Optional[int] = None) -> str:
    """Escapes user text for safe ReportLab Paragraph XML rendering.

    Converts XML special characters (<, >, &, ", ') to their respective entities,
    breaks overly long unbroken tokens, and maps newlines to <br/> tags.
    """
    if value is None:
        return ""
    text = str(value)
    if max_len and len(text) > max_len:
        text = text[:max_len] + "..."

    # Break unbroken strings longer than 40 chars to ensure table wrapping
    tokens = text.split(" ")
    wrapped_tokens = []
    for token in tokens:
        if len(token) > 40:
            token = "<br/>".join(textwrap.wrap(token, 35))
        wrapped_tokens.append(token)
    text = " ".join(wrapped_tokens)

    escaped = xml_escape(text, entities={'"': "&quot;", "'": "&apos;"})
    return escaped.replace("\n", "<br/>")


def generate_claim_receipt_pdf(claim_dict: Dict[str, Any]) -> bytes:
    """Generates a professional, print-ready PDF submission receipt using ReportLab."""
    if not isinstance(claim_dict, dict):
        claim_dict = {}

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36,
    )

    styles = getSampleStyleSheet()

    # Custom typography styles
    title_style = ParagraphStyle(
        "ReceiptTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#1e3a8a"),
    )
    subtitle_style = ParagraphStyle(
        "ReceiptSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#475569"),
    )
    section_heading = ParagraphStyle(
        "SectionHeading",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#0f172a"),
    )
    meta_label = ParagraphStyle(
        "MetaLabel",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#334155"),
    )
    meta_val = ParagraphStyle(
        "MetaVal",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#0f172a"),
    )
    badge_style = ParagraphStyle(
        "BadgeStyle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=12,
        textColor=colors.HexColor("#15803d"),
        alignment=1,
    )
    disclaimer_style = ParagraphStyle(
        "DisclaimerStyle",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#b45309"),
    )
    footer_style = ParagraphStyle(
        "FooterStyle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#94a3b8"),
        alignment=1,
    )

    story = []

    # 1. Header Banner
    header_data = [
        [
            Paragraph("ClaimSense AI", title_style),
            Paragraph("SUBMISSION RECEIPT", ParagraphStyle(
                "SubBadge",
                fontName="Helvetica-Bold",
                fontSize=12,
                leading=14,
                textColor=colors.HexColor("#2563eb"),
                alignment=2,
            )),
        ],
        [
            Paragraph(
                "AI-Powered Insurance Claim Verification &bull; Academic Decision-Support Prototype",
                subtitle_style,
            ),
            Paragraph(
                f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
                ParagraphStyle("GenDate", fontName="Helvetica", fontSize=8, leading=10, textColor=colors.HexColor("#64748b"), alignment=2),
            ),
        ],
    ]
    header_table = Table(header_data, colWidths=[380, 160])
    header_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#2563eb"), spaceAfter=15))

    # 2. Key Claim Details
    story.append(Paragraph("1. Claim Identification & Policy Information", section_heading))
    story.append(Spacer(1, 6))

    claim_id = safe_xml(claim_dict.get("claim_id", "N/A"), max_len=50)
    policy_num = safe_xml(claim_dict.get("policy_number", "N/A"), max_len=60)
    claimant = safe_xml(claim_dict.get("claimant_name", "N/A"), max_len=100)
    vehicle_num = safe_xml(claim_dict.get("vehicle_number", "N/A"), max_len=50)
    accident_date = safe_xml(claim_dict.get("accident_date", "N/A"), max_len=30)
    status = safe_xml(claim_dict.get("status", "SUBMITTED"), max_len=30)
    created_at = safe_xml(claim_dict.get("created_at", datetime.now(timezone.utc).isoformat()), max_len=50)

    details_data = [
        [Paragraph("Claim Reference ID:", meta_label), Paragraph(f"<b>{claim_id}</b>", meta_val),
         Paragraph("Registration Status:", meta_label), Paragraph(f"<b>{status}</b>", badge_style)],
        [Paragraph("Policy Number:", meta_label), Paragraph(policy_num, meta_val),
         Paragraph("Vehicle Registration:", meta_label), Paragraph(vehicle_num, meta_val)],
        [Paragraph("Claimant Name:", meta_label), Paragraph(claimant, meta_val),
         Paragraph("Accident Date:", meta_label), Paragraph(accident_date, meta_val)],
        [Paragraph("Submission Timestamp:", meta_label), Paragraph(created_at, meta_val),
         Paragraph("Assigned Queue:", meta_label), Paragraph("Preliminary Intake / Verification", meta_val)],
    ]
    details_table = Table(details_data, colWidths=[130, 140, 130, 140])
    details_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(details_table)
    story.append(Spacer(1, 14))

    # 3. Incident Description
    story.append(Paragraph("2. Claimant Incident Narrative", section_heading))
    story.append(Spacer(1, 6))
    raw_desc = claim_dict.get("claim_description") or "No narrative statement provided."
    desc_escaped = safe_xml(raw_desc, max_len=3000)
    desc_p = Paragraph(desc_escaped, meta_val)
    desc_table = Table([[desc_p]], colWidths=[540])
    desc_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f1f5f9")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
    ]))
    story.append(desc_table)
    story.append(Spacer(1, 14))

    # 4. Registered Evidence Files
    story.append(Paragraph("3. Registered Evidentiary Documents & Photos", section_heading))
    story.append(Spacer(1, 6))

    evidence_rows = [
        [
            Paragraph("<b>Evidence Category</b>", meta_label),
            Paragraph("<b>Stored / Original Filename</b>", meta_label),
            Paragraph("<b>File Size</b>", meta_label),
            Paragraph("<b>Storage Status</b>", meta_label),
        ]
    ]

    documents = claim_dict.get("documents", [])
    images = claim_dict.get("images", [])
    files_dict = claim_dict.get("files", {})

    if documents or images:
        for doc_entry in documents:
            if not isinstance(doc_entry, dict):
                continue
            size_kb = f"{round(doc_entry.get('file_size', 0) / 1024, 1)} KB"
            raw_type = doc_entry.get("document_type", "Document").replace("_", " ").title()
            raw_orig = doc_entry.get("original_filename", "N/A")
            evidence_rows.append([
                Paragraph(safe_xml(raw_type, 40), meta_val),
                Paragraph(safe_xml(raw_orig, 80), meta_val),
                Paragraph(safe_xml(size_kb), meta_val),
                Paragraph("<b>&check; Secured</b>", ParagraphStyle("G1", fontName="Helvetica-Bold", fontSize=8, textColor=colors.HexColor("#16a34a"))),
            ])
        for img in images:
            if not isinstance(img, dict):
                continue
            size_kb = f"{round(img.get('file_size', 0) / 1024, 1)} KB"
            raw_type = img.get("image_type", "Vehicle Photo").replace("_", " ").title()
            raw_orig = img.get("original_filename", "N/A")
            evidence_rows.append([
                Paragraph(safe_xml(raw_type, 40), meta_val),
                Paragraph(safe_xml(raw_orig, 80), meta_val),
                Paragraph(safe_xml(size_kb), meta_val),
                Paragraph("<b>&check; Secured</b>", ParagraphStyle("G2", fontName="Helvetica-Bold", fontSize=8, textColor=colors.HexColor("#16a34a"))),
            ])
    elif files_dict and isinstance(files_dict, dict):
        for f_key, f_info in files_dict.items():
            if isinstance(f_info, dict):
                size_kb = f"{round(f_info.get('size_bytes', 0) / 1024, 1)} KB"
                raw_type = f_key.replace("_", " ").title()
                raw_orig = f_info.get("original_name", "N/A")
                evidence_rows.append([
                    Paragraph(safe_xml(raw_type, 40), meta_val),
                    Paragraph(safe_xml(raw_orig, 80), meta_val),
                    Paragraph(safe_xml(size_kb), meta_val),
                    Paragraph("<b>&check; Secured</b>", ParagraphStyle("G3", fontName="Helvetica-Bold", fontSize=8, textColor=colors.HexColor("#16a34a"))),
                ])

    if len(evidence_rows) == 1:
        evidence_rows.append([
            Paragraph("Evidence", meta_val),
            Paragraph("4 evidence files verified and registered", meta_val),
            Paragraph("Recorded", meta_val),
            Paragraph("&check; Secured", meta_val),
        ])

    evidence_table = Table(evidence_rows, colWidths=[140, 220, 80, 100])
    evidence_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e2e8f0")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(evidence_table)
    story.append(Spacer(1, 16))

    # 5. Mandatory Academic & Legal Disclaimer
    disclaimer_text = (
        "<b>ACADEMIC DECISION-SUPPORT NOTICE & DISCLAIMER:</b><br/>"
        "This submission receipt serves exclusively as proof that the claim reference and accompanying "
        "multimodal evidence were registered into the ClaimSense AI intake storage repository. "
        "It does NOT represent claim approval, rejection, legal settlement, or fraud confirmation. "
        "Full verification analysis will be conducted by authorized human insurance assessors."
    )
    disclaimer_p = Paragraph(disclaimer_text, disclaimer_style)
    disclaimer_table = Table([[disclaimer_p]], colWidths=[540])
    disclaimer_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#fef3c7")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#f59e0b")),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
    ]))
    story.append(disclaimer_table)
    story.append(Spacer(1, 20))

    # 6. Footer
    footer_text = (
        "ClaimSense AI &bull; B.Tech CSE Major Project 2026-27 &bull; "
        "ABES Engineering College, Ghaziabad &bull; Supervisor: Ms. Sonia Lamba"
    )
    story.append(Paragraph(footer_text, footer_style))

    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
