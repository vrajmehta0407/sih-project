"""
rules_evaluator.py
==================
Stage 5 — Statutory Legal Metrology Rules Evaluation Engine

Evaluates Product attributes against active Legal Metrology rules (Rule 6 of LM PCR 2011,
Section 18 & Section 36 of Legal Metrology Act, 2009).
"""

from dataclasses import dataclass
from datetime import date, datetime, timezone
from typing import List, Optional, Dict, Any

from app.models.product import Product
from app.models.rule import Rule

STANDARD_UNITS = {"g", "kg", "mg", "l", "ml", "m", "cm", "mm", "sq.m", "N", "u"}


@dataclass
class EvaluatedViolation:
    """An identified statutory infraction ready for persistence."""
    rule_code: str
    field_affected: str
    section_violated: str
    statute_title: str
    penalty_provision: str
    estimated_fine: str
    violation_title: str
    violation_description: str
    severity: str                                       # 'critical' | 'major' | 'minor'
    rule_id: Optional[str] = None


class RulesEvaluator:
    """
    Applies Legal Metrology rule specifications to extracted product declarations.
    """

    def evaluate_product(
        self,
        product: Product,
        rules: List[Rule],
        inspection_date: Optional[date] = None,
    ) -> List[EvaluatedViolation]:
        """
        Evaluates a Product against a list of active Rule definitions.
        Returns a list of EvaluatedViolation dataclasses.
        """
        today = inspection_date or datetime.now(timezone.utc).date()
        violations: List[EvaluatedViolation] = []

        # Map rules by rule_code for fast lookup
        rule_map = {r.rule_code: r for r in rules}

        # ── 1. MRP & Taxes — Rule 6(1)(e) r/w Section 18 ───────────────────────
        mrp_rule = rule_map.get("LM_RULE_6_1_E_MRP")
        if mrp_rule and mrp_rule.is_active:
            if product.mrp_value is None or product.mrp_value <= 0:
                violations.append(
                    EvaluatedViolation(
                        rule_id=str(mrp_rule.id),
                        rule_code=mrp_rule.rule_code,
                        field_affected="mrp",
                        section_violated=mrp_rule.statutory_source,
                        statute_title="Legal Metrology (Packaged Commodities) Rules, 2011",
                        penalty_provision=mrp_rule.statutory_penalty_source,
                        estimated_fine=mrp_rule.penalty_first_offence,
                        violation_title="Missing Maximum Retail Price (MRP) Declaration",
                        violation_description=(
                            "The pre-packaged commodity fails to declare the Maximum Retail Price (MRP). "
                            "Every package must bear a clear, legible declaration of the retail sale price."
                        ),
                        severity="critical",
                    )
                )
            elif not product.mrp_inclusive_taxes_declared:
                violations.append(
                    EvaluatedViolation(
                        rule_id=str(mrp_rule.id),
                        rule_code=mrp_rule.rule_code,
                        field_affected="mrp",
                        section_violated=mrp_rule.statutory_source,
                        statute_title="Legal Metrology (Packaged Commodities) Rules, 2011",
                        penalty_provision=mrp_rule.statutory_penalty_source,
                        estimated_fine=mrp_rule.penalty_first_offence,
                        violation_title="Omission of Mandatory 'Inclusive of All Taxes' Declaration",
                        violation_description=(
                            f"MRP of ₹{product.mrp_value:.2f} is declared, but the mandatory statutory statement "
                            "'inclusive of all taxes' or 'incl. of all taxes' is missing."
                        ),
                        severity="major",
                    )
                )

        # ── 2. Net Quantity & Standard Units — Rule 6(1)(c) & Rule 11 ─────────
        qty_rule = rule_map.get("LM_RULE_6_1_C_NET_QTY")
        if qty_rule and qty_rule.is_active:
            if product.net_quantity_value is None or product.net_quantity_value <= 0:
                violations.append(
                    EvaluatedViolation(
                        rule_id=str(qty_rule.id),
                        rule_code=qty_rule.rule_code,
                        field_affected="net_quantity",
                        section_violated=qty_rule.statutory_source,
                        statute_title="Legal Metrology (Packaged Commodities) Rules, 2011",
                        penalty_provision=qty_rule.statutory_penalty_source,
                        estimated_fine=qty_rule.penalty_first_offence,
                        violation_title="Missing Net Quantity Declaration",
                        violation_description=(
                            "The package fails to declare the net quantity in terms of standard unit of "
                            "weight or measure or number as required under Rule 6(1)(c)."
                        ),
                        severity="critical",
                    )
                )
            elif product.net_quantity_unit and product.net_quantity_unit not in STANDARD_UNITS:
                violations.append(
                    EvaluatedViolation(
                        rule_id=str(qty_rule.id),
                        rule_code=qty_rule.rule_code,
                        field_affected="net_quantity",
                        section_violated="Rule 6(1)(c) and Rule 11, LM PCR 2011",
                        statute_title="Legal Metrology (Packaged Commodities) Rules, 2011",
                        penalty_provision=qty_rule.statutory_penalty_source,
                        estimated_fine=qty_rule.penalty_first_offence,
                        violation_title="Non-Standard Unit of Measurement Used",
                        violation_description=(
                            f"Net quantity uses non-standard unit '{product.net_quantity_unit}'. "
                            "Rule 11 mandates the use of standard metric units (g, kg, ml, l, m, cm, N)."
                        ),
                        severity="major",
                    )
                )

        # ── 3. Manufacturer / Packer Details — Rule 6(1)(a) ────────────────────
        mfg_rule = rule_map.get("LM_RULE_6_1_A_MFG_DETAILS")
        if mfg_rule and mfg_rule.is_active:
            has_name = bool(product.manufacturer_name or product.packer_name or product.importer_name)
            has_address = bool(product.manufacturer_address or product.packer_address or product.importer_address)

            if not has_name:
                violations.append(
                    EvaluatedViolation(
                        rule_id=str(mfg_rule.id),
                        rule_code=mfg_rule.rule_code,
                        field_affected="manufacturer_details",
                        section_violated=mfg_rule.statutory_source,
                        statute_title="Legal Metrology (Packaged Commodities) Rules, 2011",
                        penalty_provision=mfg_rule.statutory_penalty_source,
                        estimated_fine=mfg_rule.penalty_first_offence,
                        violation_title="Missing Manufacturer / Packer Name",
                        violation_description=(
                            "The package fails to declare the name of the manufacturer, packer, or importer."
                        ),
                        severity="critical",
                    )
                )
            elif not has_address or len(str(product.manufacturer_address or product.packer_address or "")) < 5:
                violations.append(
                    EvaluatedViolation(
                        rule_id=str(mfg_rule.id),
                        rule_code=mfg_rule.rule_code,
                        field_affected="manufacturer_details",
                        section_violated=mfg_rule.statutory_source,
                        statute_title="Legal Metrology (Packaged Commodities) Rules, 2011",
                        penalty_provision=mfg_rule.statutory_penalty_source,
                        estimated_fine=mfg_rule.penalty_first_offence,
                        violation_title="Incomplete Address of Manufacturer / Packer",
                        violation_description=(
                            "The package declares a manufacturer/packer name but omits a complete physical address "
                            "including city, state, or PIN code."
                        ),
                        severity="major",
                    )
                )

        # ── 4. Manufacturing Date — Rule 6(1)(d) ──────────────────────────────
        date_rule = rule_map.get("LM_RULE_6_1_D_MFG_DATE")
        if date_rule and date_rule.is_active:
            if not product.mfg_date and not product.mfg_date_raw:
                violations.append(
                    EvaluatedViolation(
                        rule_id=str(date_rule.id),
                        rule_code=date_rule.rule_code,
                        field_affected="mfg_date",
                        section_violated=date_rule.statutory_source,
                        statute_title="Legal Metrology (Packaged Commodities) Rules, 2011",
                        penalty_provision=date_rule.statutory_penalty_source,
                        estimated_fine=date_rule.penalty_first_offence,
                        violation_title="Missing Date of Manufacture / Packing",
                        violation_description=(
                            "The package fails to declare the month and year of manufacture, packing, or import."
                        ),
                        severity="critical",
                    )
                )
            elif product.mfg_date and product.mfg_date > today:
                violations.append(
                    EvaluatedViolation(
                        rule_id=str(date_rule.id),
                        rule_code=date_rule.rule_code,
                        field_affected="mfg_date",
                        section_violated=date_rule.statutory_source,
                        statute_title="Legal Metrology (Packaged Commodities) Rules, 2011",
                        penalty_provision=date_rule.statutory_penalty_source,
                        estimated_fine=date_rule.penalty_first_offence,
                        violation_title="Post-Dated Manufacturing Declaration",
                        violation_description=(
                            f"The declared manufacturing date ({product.mfg_date.strftime('%m/%Y')}) is post-dated "
                            f"beyond the inspection date ({today.strftime('%d/%m/%Y')})."
                        ),
                        severity="critical",
                    )
                )

        # ── 5. Expiry Date & Shelf Life — Rule 6(1)(h) ─────────────────────────
        exp_rule = rule_map.get("LM_RULE_6_1_H_EXPIRY_DATE")
        if exp_rule and exp_rule.is_active:
            if product.exp_date:
                if product.exp_date < today:
                    violations.append(
                        EvaluatedViolation(
                            rule_id=str(exp_rule.id),
                            rule_code=exp_rule.rule_code,
                            field_affected="exp_date",
                            section_violated=exp_rule.statutory_source,
                            statute_title="Legal Metrology (Packaged Commodities) Rules, 2011",
                            penalty_provision=exp_rule.statutory_penalty_source,
                            estimated_fine=exp_rule.penalty_first_offence,
                            violation_title="Expired Commodity Offered for Sale",
                            violation_description=(
                                f"The pre-packaged commodity has expired (Expiry: {product.exp_date.strftime('%d/%m/%Y')}) "
                                f"prior to inspection date ({today.strftime('%d/%m/%Y')})."
                            ),
                            severity="critical",
                        )
                    )
                elif product.mfg_date and product.exp_date < product.mfg_date:
                    violations.append(
                        EvaluatedViolation(
                            rule_id=str(exp_rule.id),
                            rule_code=exp_rule.rule_code,
                            field_affected="exp_date",
                            section_violated=exp_rule.statutory_source,
                            statute_title="Legal Metrology (Packaged Commodities) Rules, 2011",
                            penalty_provision=exp_rule.statutory_penalty_source,
                            estimated_fine=exp_rule.penalty_first_offence,
                            violation_title="Illogical Expiry Date Preceding Manufacturing Date",
                            violation_description=(
                                f"Declared expiry date ({product.exp_date.strftime('%m/%Y')}) precedes manufacturing date "
                                f"({product.mfg_date.strftime('%m/%Y')})."
                            ),
                            severity="major",
                        )
                    )

        # ── 6. Country of Origin — Rule 6(1)(g) ────────────────────────────────
        origin_rule = rule_map.get("LM_RULE_6_1_G_COUNTRY_OF_ORIGIN")
        if origin_rule and origin_rule.is_active:
            if not product.country_of_origin and product.importer_name:
                violations.append(
                    EvaluatedViolation(
                        rule_id=str(origin_rule.id),
                        rule_code=origin_rule.rule_code,
                        field_affected="country_of_origin",
                        section_violated=origin_rule.statutory_source,
                        statute_title="Legal Metrology (Packaged Commodities) Rules, 2011",
                        penalty_provision=origin_rule.statutory_penalty_source,
                        estimated_fine=origin_rule.penalty_first_offence,
                        violation_title="Missing Country of Origin for Imported Commodity",
                        violation_description=(
                            "The package declares an importer but fails to declare the Country of Origin as required by Rule 6(1)(g)."
                        ),
                        severity="major",
                    )
                )

        # ── 7. Consumer Care Details — Rule 6(1)(f) ────────────────────────────
        care_rule = rule_map.get("LM_RULE_6_1_F_CONSUMER_CARE")
        if care_rule and care_rule.is_active:
            has_phone = bool(product.consumer_care_phone)
            has_email = bool(product.consumer_care_email)
            has_address = bool(product.consumer_care_address)

            if not has_phone and not has_email and not has_address:
                violations.append(
                    EvaluatedViolation(
                        rule_id=str(care_rule.id),
                        rule_code=care_rule.rule_code,
                        field_affected="consumer_care",
                        section_violated=care_rule.statutory_source,
                        statute_title="Legal Metrology (Packaged Commodities) Rules, 2011",
                        penalty_provision=care_rule.statutory_penalty_source,
                        estimated_fine=care_rule.penalty_first_offence,
                        violation_title="Missing Consumer Grievance Redressal Mechanism",
                        violation_description=(
                            "The package fails to declare any contact details (name, telephone number, email, or address) "
                            "for consumer complaints under Rule 6(1)(f)."
                        ),
                        severity="critical",
                    )
                )
            elif not (has_phone or has_email):
                violations.append(
                    EvaluatedViolation(
                        rule_id=str(care_rule.id),
                        rule_code=care_rule.rule_code,
                        field_affected="consumer_care",
                        section_violated=care_rule.statutory_source,
                        statute_title="Legal Metrology (Packaged Commodities) Rules, 2011",
                        penalty_provision=care_rule.statutory_penalty_source,
                        estimated_fine=care_rule.penalty_first_offence,
                        violation_title="Incomplete Consumer Care Contact Details",
                        violation_description=(
                            "Rule 6(1)(f) requires at least a telephone number or email address for consumer grievances."
                        ),
                        severity="minor",
                    )
                )

        return violations


# Singleton
rules_evaluator = RulesEvaluator()
