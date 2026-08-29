"""
endpoints/ecommerce.py
======================
Stage 12 — E-Commerce Rule 6(10) Digital Label Compliance Auditor Endpoint

Legal Basis:
  - Rule 6(10), Legal Metrology (Packaged Commodities) Rules 2011 — inserted by
    LM (PC) Amendment Rules 2017 & 2021.
  - Mandates every e-commerce entity to display all mandatory declarations
    including MRP, net qty, country of origin, USP, and manufacturer details
    on the product detail page prior to purchase.
  - Section 36 (penalty) & Section 48/49 (compounding) — LM Act 2009.
"""

import logging
from fastapi import APIRouter, Depends
from app.schemas.ecommerce import (
    EcommerceAuditRequest,
    EcommerceAuditResponse,
    EcommerceViolation,
    EcommerceViolationType,
)
from app.schemas.ecommerce_batch import (
    BatchAuditRequest,
    BatchAuditResponse,
    BatchProductUrlItem,
)
from app.services.ecommerce_batch_service import ecommerce_batch_service
from app.core.security import require_inspector
from app.models.user import User

router = APIRouter()
logger = logging.getLogger(__name__)


def _run_rule_6_10_audit(req: EcommerceAuditRequest) -> EcommerceAuditResponse:
    """
    Execute the Rule 6(10) compliance checklist across mandatory digital declarations.
    """
    violations: list[EcommerceViolation] = []

    def add_violation(code, rule_ref, description, severity="CRITICAL"):
        violations.append(EcommerceViolation(
            code=code,
            rule_ref=rule_ref,
            description=description,
            severity=severity,
        ))

    # ── Rule 6(1)(e): MRP (incl. of all taxes) ──────────────────────────────
    if req.mrp_displayed is None or req.mrp_displayed <= 0:
        add_violation(
            EcommerceViolationType.MISSING_MRP,
            "Rule 6(1)(e) r/w Rule 6(10) LM PCR 2011",
            f"Maximum Retail Price (MRP) is not displayed on the {req.platform} product listing page. "
            "This is a mandatory statutory declaration under Rule 6(1)(e).",
        )
    elif not req.mrp_includes_taxes_declared:
        add_violation(
            EcommerceViolationType.MRP_WITHOUT_TAX_DECLARATION,
            "Rule 6(1)(e) LM PCR 2011",
            "MRP is displayed but the mandatory phrase 'inclusive of all taxes' is absent.",
            severity="MAJOR",
        )

    # ── Rule 6(1)(c): Net Quantity ───────────────────────────────────────────
    if not req.net_quantity_displayed:
        add_violation(
            EcommerceViolationType.MISSING_NET_QUANTITY,
            "Rule 6(1)(c) r/w Rule 6(10) LM PCR 2011",
            f"Net quantity/weight/volume is not displayed on the {req.platform} product listing.",
        )

    # ── Rule 6(1)(k): Unit Sale Price ───────────────────────────────────────
    if not req.unit_sale_price_displayed:
        add_violation(
            EcommerceViolationType.MISSING_USP,
            "Rule 6(1)(k) r/w Rule 6(10) LM PCR 2011",
            "Unit Sale Price (per gram/ml/unit) is not shown, preventing consumer price comparison.",
            severity="MAJOR",
        )

    # ── Rule 6(1)(l): Country of Origin ─────────────────────────────────────
    if not req.country_of_origin_displayed:
        add_violation(
            EcommerceViolationType.MISSING_COUNTRY_OF_ORIGIN,
            "Rule 6(1)(l) r/w Rule 6(10) LM PCR 2011 & Consumer Protection (E-Commerce) Rules 2020",
            "Country of Origin is mandatory on all e-commerce product listings.",
        )

    # ── Rule 6(1)(a): Manufacturer/Packer Name & Address ────────────────────
    if not req.manufacturer_details_displayed:
        add_violation(
            EcommerceViolationType.MISSING_MFG_DETAILS,
            "Rule 6(1)(a) r/w Rule 6(10) LM PCR 2011",
            "Manufacturer/Packer name and complete address are not displayed on the listing page.",
        )

    # ── Rule 6(1)(a): Importer Details (imported goods only) ────────────────
    if req.is_imported and not req.importer_details_displayed:
        add_violation(
            EcommerceViolationType.MISSING_IMPORTER_DETAILS,
            "Rule 6(1)(a) proviso r/w Rule 6(10) LM PCR 2011",
            "Importer name and Indian address are mandatory for imported packaged commodities.",
        )

    # ── Rule 6(1)(f): Customer Care ─────────────────────────────────────────
    if not req.customer_care_displayed:
        add_violation(
            EcommerceViolationType.MISSING_CUSTOMER_CARE,
            "Rule 6(1)(f) r/w Rule 6(10) LM PCR 2011",
            "Consumer care details (toll-free number or email) are not displayed.",
            severity="MINOR",
        )

    # ── Rule 6(1)(d): Expiry/Best Before (food & pharma) ────────────────────
    if req.product_category in ("Food & Beverages", "Pharmaceuticals", "Cosmetics") and not req.expiry_date_displayed:
        add_violation(
            EcommerceViolationType.MISSING_EXPIRY_DATE,
            "Rule 6(1)(d) r/w Rule 6(10) LM PCR 2011",
            f"Expiry or 'Best Before' date is mandatory for '{req.product_category}' category products.",
        )

    # ── Score & Statutory Notice ─────────────────────────────────────────────
    total_checks = 8
    critical_count = sum(1 for v in violations if v.severity == "CRITICAL")
    weighted_failures = sum(
        3 if v.severity == "CRITICAL" else 2 if v.severity == "MAJOR" else 1
        for v in violations
    )
    compliance_score = max(0.0, round(100.0 - (weighted_failures / (total_checks * 3)) * 100, 1))
    is_compliant = len(violations) == 0

    notice = None
    if not is_compliant:
        violation_list = "\n  ".join([f"- {v.description}" for v in violations])
        notice = (
            f"SHOW-CAUSE NOTICE under Section 36 of the Legal Metrology Act, 2009\n\n"
            f"To: {req.platform} (E-Commerce Entity)\n"
            f"Re: Non-compliance with Rule 6(10) of the Legal Metrology (Packaged Commodities) "
            f"Rules, 2011 for product: '{req.product_name}'\n\n"
            f"Statutory violations detected:\n  {violation_list}\n\n"
            f"You are hereby directed to rectify the above violations within 7 (seven) days "
            f"from the date of this notice, failing which penal action under Section 36 (penalty "
            f"up to ₹25,000 for first offence and ₹50,000 for subsequent offences) shall be initiated."
        )

    return EcommerceAuditResponse(
        platform=req.platform,
        product_name=req.product_name,
        is_compliant=is_compliant,
        compliance_score=compliance_score,
        violations=violations,
        total_violations=len(violations),
        critical_violations=critical_count,
        statutory_notice=notice,
        relevant_sections=["Section 36 LM Act 2009", "Rule 6(10) LM PCR 2011"],
    )


@router.post("/audit", response_model=EcommerceAuditResponse, summary="Audit E-Commerce Digital Label (Rule 6(10))")
def audit_ecommerce_listing(
    req: EcommerceAuditRequest,
    current_user: User = Depends(require_inspector),
):
    """
    Audit a digital e-commerce product listing for Rule 6(10) compliance.
    Returns a structured violation report with severity ratings and a
    statutory show-cause notice draft for detected infractions.
    """
    logger.info(
        "E-Commerce Rule 6(10) audit initiated for '%s' on %s by %s",
        req.product_name, req.platform, current_user.email
    )
    return _run_rule_6_10_audit(req)


# ===========================================================================
# Stage 26 — High-Throughput E-Commerce Multi-Product Batch URL Scraping
# ===========================================================================

@router.post(
    "/batch-audit",
    response_model=BatchAuditResponse,
    summary="Execute High-Throughput E-Commerce Multi-Product Batch Scrape",
)
def run_ecommerce_batch_audit(
    req: BatchAuditRequest,
):
    """
    Asynchronously scrape and audit multiple e-commerce product URLs across platforms
    (Amazon, Flipkart, Blinkit, Zepto, Swiggy Instamart) against Rule 6(10) declarations.
    """
    return ecommerce_batch_service.audit_batch(req)


@router.get(
    "/batch-audit/{batch_id}",
    response_model=BatchAuditResponse,
    summary="Get E-Commerce Batch Audit Report by ID",
)
def get_ecommerce_batch_audit(
    batch_id: str,
):
    """Retrieve structured compliance ledger and bulk notice draft for an executed batch audit."""
    return ecommerce_batch_service.get_batch(batch_id)
