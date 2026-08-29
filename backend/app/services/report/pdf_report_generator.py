"""
pdf_report_generator.py
=======================
Stage 6 — Statutory Legal Metrology Inspection Report & Notice PDF Generator

Builds court-admissible PDF inspection documents with:
  1. Official Government Header & Verification QR Code
  2. Inspector & Establishment Credentials with GPS
  3. Product Packaging Declarations Matrix
  4. Statutory Violation Docket Table (Rule 6, Section 18 & 36)
  5. Show-Cause Legal Directive & Penalty Assessment
  6. Cryptographic Chain-of-Custody Hash & Evidence Annexure
"""

import os
from typing import Dict, Any, List, Optional
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
    KeepTogether,
    HRFlowable,
)


class PDFReportGenerator:
    """
    Renders court-admissible PDF inspection reports and statutory notices.
    """

    def generate_report(
        self,
        output_pdf_path: str,
        inspection_data: Dict[str, Any],
        qr_image_path: Optional[str] = None,
    ) -> str:
        """
        Builds the PDF document and writes to output_pdf_path.
        """
        os.makedirs(os.path.dirname(output_pdf_path), exist_ok=True)

        doc = SimpleDocTemplate(
            output_pdf_path,
            pagesize=A4,
            leftMargin=36,
            rightMargin=36,
            topMargin=36,
            bottomMargin=36,
        )

        styles = getSampleStyleSheet()

        # Custom typography styles
        title_style = ParagraphStyle(
            "DocTitle",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=13,
            leading=16,
            textColor=colors.HexColor("#0B2545"),
            alignment=0,
        )
        subtitle_style = ParagraphStyle(
            "DocSubtitle",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=9,
            leading=12,
            textColor=colors.HexColor("#134074"),
        )
        section_heading = ParagraphStyle(
            "SectionHeading",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=10,
            leading=13,
            textColor=colors.HexColor("#0B2545"),
            spaceBefore=8,
            spaceAfter=4,
        )
        body_style = ParagraphStyle(
            "Body",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=8,
            leading=10,
            textColor=colors.HexColor("#1D2D44"),
        )
        body_bold = ParagraphStyle(
            "BodyBold",
            parent=body_style,
            fontName="Helvetica-Bold",
        )
        body_small = ParagraphStyle(
            "BodySmall",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=7,
            leading=9,
            textColor=colors.HexColor("#4A5568"),
        )
        directive_style = ParagraphStyle(
            "Directive",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=8,
            leading=11,
            textColor=colors.HexColor("#742A2A"),
        )

        story = []

        # ── 1. Official Header & QR Code ──────────────────────────────────────
        header_text = [
            Paragraph("GOVERNMENT OF INDIA", subtitle_style),
            Paragraph("DEPARTMENT OF CONSUMER AFFAIRS — LEGAL METROLOGY DIVISION", title_style),
            Paragraph("STATUTORY INSPECTION REPORT & RECORD OF COMPLIANCE", subtitle_style),
            Paragraph("Under Legal Metrology Act, 2009 & Packaged Commodities Rules, 2011", body_small),
        ]

        if qr_image_path and os.path.isfile(qr_image_path):
            qr_img = Image(qr_image_path, width=54, height=54)
            header_table_data = [[header_text, qr_img]]
            header_table = Table(header_table_data, colWidths=[460, 60])
            header_table.setStyle(
                TableStyle([
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("ALIGN", (1, 0), (1, 0), "RIGHT"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ])
            )
            story.append(header_table)
        else:
            for p in header_text:
                story.append(p)

        story.append(Spacer(1, 6))
        story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0B2545"), spaceAfter=8))

        # ── 2. Inspection & Establishment Dossier ──────────────────────────────
        insp = inspection_data.get("inspection", {})
        inspector = inspection_data.get("inspector", {})
        docket_no = inspection_data.get("docket_number", "DOCKET-PENDING")

        dossier_data = [
            [
                Paragraph("<b>Docket Number:</b>", body_style),
                Paragraph(f"<b>{docket_no}</b>", body_style),
                Paragraph("<b>Inspection No:</b>", body_style),
                Paragraph(insp.get("inspection_number", "N/A"), body_style),
            ],
            [
                Paragraph("<b>Inspection Date:</b>", body_style),
                Paragraph(insp.get("created_at", datetime.now().strftime("%d-%m-%Y %H:%M")), body_style),
                Paragraph("<b>Compliance Status:</b>", body_style),
                Paragraph(
                    f"<b><font color='{'#C53030' if insp.get('compliance_status') == 'non_compliant' else '#2F855A'}'>"
                    f"{insp.get('compliance_status', 'pending').upper()}</font></b>",
                    body_style,
                ),
            ],
            [
                Paragraph("<b>Enforcement Officer:</b>", body_style),
                Paragraph(f"{inspector.get('name', 'Inspector')} ({inspector.get('badge_number', 'N/A')})", body_style),
                Paragraph("<b>Jurisdiction:</b>", body_style),
                Paragraph(f"{insp.get('district', 'N/A')}, {insp.get('state', 'N/A')}", body_style),
            ],
            [
                Paragraph("<b>Establishment / Store:</b>", body_style),
                Paragraph(f"{insp.get('store_name', 'Retail Outlet')}", body_style),
                Paragraph("<b>GPS Coordinates:</b>", body_style),
                Paragraph(
                    f"{insp.get('gps_latitude', 'N/A')}, {insp.get('gps_longitude', 'N/A')}",
                    body_style,
                ),
            ],
        ]

        dossier_table = Table(dossier_data, colWidths=[110, 150, 110, 150])
        dossier_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F7FAFC")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ])
        )
        story.append(dossier_table)
        story.append(Spacer(1, 8))

        # ── 3. Product Packaging Declarations Matrix ───────────────────────────
        story.append(Paragraph("1. PACKAGING DECLARATIONS MATRIX (Rule 6)", section_heading))
        prod = inspection_data.get("product", {})

        mrp_str = f"Rs. {prod.get('mrp_value', 'N/A')}" if prod.get("mrp_value") is not None else "NOT DECLARED"
        if prod.get("mrp_inclusive_taxes_declared"):
            mrp_str += " (incl. of all taxes)"

        qty_str = f"{prod.get('net_quantity_value', '')} {prod.get('net_quantity_unit', '')}".strip() or "NOT DECLARED"

        mfg_str = prod.get("mfg_date_raw") or (prod.get("mfg_date") if prod.get("mfg_date") else "NOT DECLARED")
        exp_str = prod.get("exp_date_raw") or (prod.get("exp_date") if prod.get("exp_date") else "NOT DECLARED")

        decl_table_data = [
            [
                Paragraph("<b>Product / Brand:</b>", body_style),
                Paragraph(f"{prod.get('product_name') or prod.get('brand_name') or 'N/A'}", body_style),
                Paragraph("<b>Commodity Name:</b>", body_style),
                Paragraph(f"{prod.get('commodity_generic_name', 'N/A')}", body_style),
            ],
            [
                Paragraph("<b>Declared MRP:</b>", body_style),
                Paragraph(mrp_str, body_style),
                Paragraph("<b>Net Quantity:</b>", body_style),
                Paragraph(qty_str, body_style),
            ],
            [
                Paragraph("<b>Date of Mfg / Pkg:</b>", body_style),
                Paragraph(mfg_str, body_style),
                Paragraph("<b>Expiry / Best Before:</b>", body_style),
                Paragraph(exp_str, body_style),
            ],
            [
                Paragraph("<b>Batch / Lot No:</b>", body_style),
                Paragraph(f"{prod.get('batch_number', 'NOT DECLARED')}", body_style),
                Paragraph("<b>Country of Origin:</b>", body_style),
                Paragraph(f"{prod.get('country_of_origin', 'NOT DECLARED')}", body_style),
            ],
            [
                Paragraph("<b>Manufacturer / Packer:</b>", body_style),
                Paragraph(f"{prod.get('manufacturer_name', 'N/A')}, {prod.get('manufacturer_address', '')}", body_style),
                Paragraph("<b>Consumer Care:</b>", body_style),
                Paragraph(f"{prod.get('consumer_care_phone', '')} | {prod.get('consumer_care_email', '')}", body_style),
            ],
        ]

        decl_table = Table(decl_table_data, colWidths=[110, 150, 110, 150])
        decl_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FFFFFF")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ])
        )
        story.append(decl_table)
        story.append(Spacer(1, 8))

        # ── 4. Statutory Violations Docket Table ────────────────────────────────
        story.append(Paragraph("2. STATUTORY INFRACTIONS & VIOLATIONS DOCKET", section_heading))
        violations: List[Dict[str, Any]] = inspection_data.get("violations", [])

        if violations:
            v_headers = [
                Paragraph("<b>#</b>", body_bold),
                Paragraph("<b>Section / Rule Violated</b>", body_bold),
                Paragraph("<b>Infraction Title & Description</b>", body_bold),
                Paragraph("<b>Severity</b>", body_bold),
                Paragraph("<b>Penalty Liability</b>", body_bold),
            ]
            v_rows = [v_headers]

            for idx, v in enumerate(violations, 1):
                sev_color = "#C53030" if v.get("severity") == "critical" else "#DD6B20" if v.get("severity") == "major" else "#3182CE"
                v_rows.append([
                    Paragraph(str(idx), body_style),
                    Paragraph(f"<b>{v.get('section_violated', 'Rule 6')}</b><br/><font color='#718096'>{v.get('statute_title', 'LM PCR 2011')}</font>", body_style),
                    Paragraph(f"<b>{v.get('violation_title', '')}</b><br/>{v.get('violation_description', '')}", body_style),
                    Paragraph(f"<b><font color='{sev_color}'>{v.get('severity', 'critical').upper()}</font></b>", body_style),
                    Paragraph(f"<b>{v.get('estimated_fine', 'Sec 36')}</b>", body_style),
                ])

            v_table = Table(v_rows, colWidths=[20, 110, 200, 60, 130])
            v_table.setStyle(
                TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EDF2F7")),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("TOPPADDING", (0, 0), (-1, -1), 3),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                    ("LEFTPADDING", (0, 0), (-1, -1), 3),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 3),
                ])
            )
            story.append(v_table)
        else:
            compliant_notice = [
                [
                    Paragraph(
                        "<b>COMPLIANCE CERTIFICATION:</b> No statutory violations detected under Rule 6 of the "
                        "Legal Metrology (Packaged Commodities) Rules, 2011. The scanned product label satisfies all "
                        "mandatory declaration parameters.",
                        body_style,
                    )
                ]
            ]
            c_table = Table(compliant_notice, colWidths=[520])
            c_table.setStyle(
                TableStyle([
                    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F0FFF4")),
                    ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#38A169")),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ])
            )
            story.append(c_table)

        story.append(Spacer(1, 8))

        # ── 5. Statutory Directive / Show Cause Notice ──────────────────────────
        if violations:
            story.append(Paragraph("3. STATUTORY NOTICE & LEGAL DIRECTIVE", section_heading))
            directive_text = (
                "<b>TAKE NOTICE</b> that the establishment and manufacturer named above have prima facie contravened "
                "the mandatory provisions of the Legal Metrology (Packaged Commodities) Rules, 2011 and Section 18 of the "
                "Legal Metrology Act, 2009. You are hereby called upon to show cause within <b>fifteen (15) days</b> of the "
                "receipt of this notice as to why penal action under <b>Section 36</b> should not be initiated against you. "
                "Failure to respond shall result in compounding proceedings or prosecution before the competent Magistrate."
            )
            directive_box = [[Paragraph(directive_text, directive_style)]]
            d_table = Table(directive_box, colWidths=[520])
            d_table.setStyle(
                TableStyle([
                    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FFF5F5")),
                    ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#E53E3E")),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ])
            )
            story.append(d_table)
            story.append(Spacer(1, 8))

        # ── 6. Cryptographic Chain-of-Custody Footer ───────────────────────────
        story.append(Paragraph("4. CHAIN-OF-CUSTODY & CRYPTOGRAPHIC VERIFICATION", section_heading))
        coc_hash = inspection_data.get("chain_of_custody_hash", "HASH-PENDING")
        qr_token = inspection_data.get("qr_verification_token", "TOKEN-PENDING")

        coc_data = [
            [
                Paragraph("<b>Record SHA-256 Digest:</b>", body_style),
                Paragraph(f"<font name='Courier' size='7'>{coc_hash}</font>", body_style),
            ],
            [
                Paragraph("<b>QR Verification Token:</b>", body_style),
                Paragraph(f"<font name='Courier' size='7'>{qr_token}</font>", body_style),
            ],
            [
                Paragraph("<b>Tamper-Proofing Standard:</b>", body_style),
                Paragraph("Section 65B Indian Evidence Act / BSA 2023 Digital Record Integrity Compliant", body_small),
            ],
        ]
        coc_table = Table(coc_data, colWidths=[140, 380])
        coc_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#EDF2F7")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
                ("TOPPADDING", (0, 0), (-1, -1), 2),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
            ])
        )
        story.append(coc_table)

        # Build PDF document
        doc.build(story)
        return output_pdf_path


# Singleton
pdf_report_generator = PDFReportGenerator()
