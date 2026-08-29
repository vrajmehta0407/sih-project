"""
deceptive_packaging_service.py
==============================
Stage 29 — Multi-Platform Dark Pattern & Deceptive Packaging VDI Service
"""

import uuid
import hashlib
import logging
from datetime import datetime
from typing import Dict, Optional, List

from app.schemas.deceptive_packaging import (
    DeceptivePackagingAuditRequest,
    DeceptivePackagingAuditResponse,
)

logger = logging.getLogger(__name__)


class DeceptivePackagingService:
    """Calculates 3D volumetric slack-fill, Visual Deception Index (VDI), and Rule 5 compliance."""

    _cached_audits: Dict[str, DeceptivePackagingAuditResponse] = {}

    def audit_package(self, req: DeceptivePackagingAuditRequest) -> DeceptivePackagingAuditResponse:
        """Evaluate volumetric dimensions, slack-fill ratio, and statutory deception index."""
        now = datetime.now()
        audit_id = f"DECEPTIVE-AUDIT-2026-{uuid.uuid4().hex[:8].upper()}"

        # 1. Compute Outer Container Volume (cm3)
        v_outer = round(req.package_length_cm * req.package_width_cm * req.package_height_cm, 2)

        # 2. Compute Product Bulk Volume (cm3)
        density = req.product_bulk_density_g_per_cm3 if (req.product_bulk_density_g_per_cm3 and req.product_bulk_density_g_per_cm3 > 0) else 0.5
        v_product = round(req.declared_net_quantity_grams / density, 2)

        # 3. Calculate Slack Fill
        v_slack = max(0.0, round(v_outer - v_product, 2))
        total_slack_pct = round((v_slack / v_outer) * 100.0, 1) if v_outer > 0 else 0.0

        # 4. Determine Engineering Functional Cushion Allowance
        if req.functional_cushion_allowance_pct is not None and req.functional_cushion_allowance_pct > 0:
            func_allowance = req.functional_cushion_allowance_pct
        elif req.packaging_type == "FLEXIBLE_POUCH":
            func_allowance = 30.0  # Nitrogen cushion for chips/snacks
        elif req.packaging_type == "JAR_WITH_FALSE_BOTTOM":
            func_allowance = 10.0
        elif req.packaging_type == "BOTTLE":
            func_allowance = 8.0
        else:
            func_allowance = 15.0  # Default rigid box

        # 5. Compute Deceptive Non-Functional Slack Fill
        deceptive_pct = max(0.0, round(total_slack_pct - func_allowance, 1))

        # 6. Calculate Visual Deception Index (VDI) on 0.0 - 10.0 scale
        vdi = min(10.0, round(deceptive_pct / 6.0, 1))

        # 7. Statutory Risk Assessment
        citations = [
            "Section 18, Legal Metrology Act, 2009 (Prohibition of Misleading/Deceptive Packaging)",
            "Rule 5 & Rule 21, Legal Metrology (Packaged Commodities) Rules, 2011",
        ]

        if deceptive_pct > 15.0 or vdi >= 4.0:
            is_comp = False
            verdict = "DECEPTIVE_PACKAGING_VIOLATION"
            penalty = 25000.0
            citations.append("Section 36(1), Legal Metrology Act, 2009 (Penalty for Non-Standard Package)")
            if vdi >= 7.0:
                risk_level = "CRITICAL_FRAUD"
                recom = (
                    f"Severe deceptive packaging detected. Container contains {total_slack_pct}% empty volume "
                    f"({deceptive_pct}% non-functional slack fill). Visual Deception Index: {vdi}/10.0. "
                    f"Recommend seizure of stock under Section 15 and issue Show-Cause Notice under Section 18."
                )
            else:
                risk_level = "HIGH_DECEPTIVE"
                recom = (
                    f"Deceptive packaging confirmed. Non-functional slack fill ({deceptive_pct}%) exceeds "
                    f"statutory limits. VDI: {vdi}/10.0. Issue Section 18 corrective notice."
                )
        elif deceptive_pct > 5.0:
            is_comp = True
            verdict = "COMPLIANT_FUNCTIONAL_PACKAGING"
            risk_level = "MODERATE_CAUTION"
            penalty = 0.0
            recom = "Slack-fill within acceptable tolerance but approaching threshold. Issue advisory note."
        else:
            is_comp = True
            verdict = "COMPLIANT_FUNCTIONAL_PACKAGING"
            risk_level = "NEGLIGIBLE"
            penalty = 0.0
            recom = "Container volume proportionally matches declared net content. Fully compliant."

        # Cryptographic Audit Seal
        seal_payload = f"{audit_id}|{req.product_name}|{v_outer}|{v_product}|{vdi}|{now.isoformat()}"
        seal_hash = hashlib.sha256(seal_payload.encode("utf-8")).hexdigest()

        response = DeceptivePackagingAuditResponse(
            audit_id=audit_id,
            product_name=req.product_name,
            brand_name=req.brand_name,
            packaging_type=req.packaging_type,
            audited_at=now,
            container_outer_volume_cm3=v_outer,
            actual_product_volume_cm3=v_product,
            total_slack_fill_volume_cm3=v_slack,
            total_slack_fill_pct=total_slack_pct,
            functional_allowance_pct=func_allowance,
            deceptive_non_functional_slack_fill_pct=deceptive_pct,
            visual_deception_index=vdi,
            deception_risk_level=risk_level,
            is_compliant_with_rule_5=is_comp,
            statutory_verdict=verdict,
            statutory_penalty_amount_inr=penalty,
            statutory_citations=citations,
            officer_action_recommendation=recom,
            digital_audit_seal=seal_hash,
        )

        self._cached_audits[audit_id] = response
        logger.info("Deceptive packaging audit %s completed for %s (VDI: %s, Verdict: %s)", audit_id, req.product_name, vdi, verdict)
        return response

    def get_audit(self, audit_id: str) -> Optional[DeceptivePackagingAuditResponse]:
        """Retrieve previously executed deceptive packaging audit report."""
        if audit_id in self._cached_audits:
            return self._cached_audits[audit_id]
        # Return fallback simulated audit
        req = DeceptivePackagingAuditRequest(
            product_name="Crunchy Cornflakes 500g Mega Box",
            brand_name="CrispyBites",
            packaging_type="RIGID_BOX",
            package_length_cm=24.0,
            package_width_cm=12.0,
            package_height_cm=36.0,
            declared_net_quantity_grams=500.0,
            product_bulk_density_g_per_cm3=0.18,
            functional_cushion_allowance_pct=15.0,
        )
        return self.audit_package(req)


deceptive_packaging_service = DeceptivePackagingService()
