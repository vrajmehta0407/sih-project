"""
declaration_extractor.py
========================
Stage 4 — High-Level Statutory Declarations Extractor

Orchestrates specialized regex & NLP parsers across consensus OCR text streams.
Computes field-level confidences and identifies missing statutory declarations.
"""

from dataclasses import dataclass, field
from datetime import date
from typing import Dict, Any, Optional, List

from app.services.extractor.parsers import (
    parse_mrp,
    parse_net_quantity,
    parse_unit_sale_price,
    parse_dates,
    parse_batch_number,
    parse_mfg_packer_importer,
    parse_country_of_origin,
    parse_consumer_care,
    parse_commodity_name,
)


@dataclass
class ExtractedDeclarations:
    """Consolidated representation of extracted statutory declarations."""
    # MRP — Rule 6(1)(e)
    mrp_raw: Optional[str] = None
    mrp_value: Optional[float] = None
    mrp_currency: str = "INR"
    mrp_inclusive_taxes_declared: bool = False
    mrp_confidence: float = 0.0

    # Net Quantity — Rule 6(1)(c)
    net_quantity_raw: Optional[str] = None
    net_quantity_value: Optional[float] = None
    net_quantity_unit: Optional[str] = None
    net_quantity_is_standard: bool = False
    net_quantity_confidence: float = 0.0

    # Unit Sale Price — Rule 6(1)(k)
    unit_sale_price_raw: Optional[str] = None
    unit_sale_price_value: Optional[float] = None
    unit_sale_price_unit: Optional[str] = None
    unit_sale_price_confidence: float = 0.0

    # Dates — Rule 6(1)(d) & 6(1)(h)
    mfg_date_raw: Optional[str] = None
    mfg_date: Optional[date] = None
    exp_date_raw: Optional[str] = None
    exp_date: Optional[date] = None
    date_confidence: float = 0.0

    # Batch Number
    batch_number: Optional[str] = None
    batch_confidence: float = 0.0

    # Manufacturer / Packer / Importer — Rule 6(1)(a)
    manufacturer_name: Optional[str] = None
    manufacturer_address: Optional[str] = None
    packer_name: Optional[str] = None
    packer_address: Optional[str] = None
    importer_name: Optional[str] = None
    importer_address: Optional[str] = None
    mfg_packer_confidence: float = 0.0

    # Country of Origin — Rule 6(1)(g)
    country_of_origin: Optional[str] = None
    origin_confidence: float = 0.0

    # Consumer Care Details — Rule 6(1)(f)
    consumer_care_email: Optional[str] = None
    consumer_care_phone: Optional[str] = None
    consumer_care_address: Optional[str] = None
    consumer_care_confidence: float = 0.0

    # Commodity Name — Rule 6(1)(b)
    commodity_generic_name: Optional[str] = None
    brand_name: Optional[str] = None
    commodity_confidence: float = 0.0

    # Summary Metrics
    declared_fields_count: int = 0
    missing_mandatory_fields: List[str] = field(default_factory=list)
    overall_confidence: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "mrp": {
                "raw": self.mrp_raw,
                "value": self.mrp_value,
                "currency": self.mrp_currency,
                "inclusive_taxes_declared": self.mrp_inclusive_taxes_declared,
                "confidence": round(self.mrp_confidence, 4),
            },
            "net_quantity": {
                "raw": self.net_quantity_raw,
                "value": self.net_quantity_value,
                "unit": self.net_quantity_unit,
                "is_standard_unit": self.net_quantity_is_standard,
                "confidence": round(self.net_quantity_confidence, 4),
            },
            "unit_sale_price": {
                "raw": self.unit_sale_price_raw,
                "value": self.unit_sale_price_value,
                "unit": self.unit_sale_price_unit,
                "confidence": round(self.unit_sale_price_confidence, 4),
            },
            "dates": {
                "mfg_date_raw": self.mfg_date_raw,
                "mfg_date": self.mfg_date.isoformat() if self.mfg_date else None,
                "exp_date_raw": self.exp_date_raw,
                "exp_date": self.exp_date.isoformat() if self.exp_date else None,
                "confidence": round(self.date_confidence, 4),
            },
            "batch_number": {
                "value": self.batch_number,
                "confidence": round(self.batch_confidence, 4),
            },
            "manufacturer_details": {
                "manufacturer_name": self.manufacturer_name,
                "manufacturer_address": self.manufacturer_address,
                "packer_name": self.packer_name,
                "packer_address": self.packer_address,
                "importer_name": self.importer_name,
                "importer_address": self.importer_address,
                "confidence": round(self.mfg_packer_confidence, 4),
            },
            "country_of_origin": {
                "country": self.country_of_origin,
                "confidence": round(self.origin_confidence, 4),
            },
            "consumer_care": {
                "email": self.consumer_care_email,
                "phone": self.consumer_care_phone,
                "address": self.consumer_care_address,
                "confidence": round(self.consumer_care_confidence, 4),
            },
            "commodity": {
                "generic_name": self.commodity_generic_name,
                "brand_name": self.brand_name,
                "confidence": round(self.commodity_confidence, 4),
            },
            "summary": {
                "declared_fields_count": self.declared_fields_count,
                "missing_mandatory_fields": self.missing_mandatory_fields,
                "overall_confidence": round(self.overall_confidence, 4),
            },
        }


class DeclarationExtractor:
    """
    Executes statutory declaration parsers across OCR consensus text.
    """

    def extract_from_text(self, text: str) -> ExtractedDeclarations:
        """Runs full parser suite against aggregated text."""
        if not text or not text.strip():
            return ExtractedDeclarations(
                missing_mandatory_fields=[
                    "MRP (Rule 6(1)(e))",
                    "Net Quantity (Rule 6(1)(c))",
                    "Mfg Date (Rule 6(1)(d))",
                    "Manufacturer / Packer (Rule 6(1)(a))",
                    "Consumer Care (Rule 6(1)(f))",
                ]
            )

        mrp_data = parse_mrp(text)
        qty_data = parse_net_quantity(text)
        usp_data = parse_unit_sale_price(text)
        dates_data = parse_dates(text)
        batch_data = parse_batch_number(text)
        mfg_data = parse_mfg_packer_importer(text)
        origin_data = parse_country_of_origin(text)
        care_data = parse_consumer_care(text)
        comm_data = parse_commodity_name(text)

        decl = ExtractedDeclarations(
            # MRP
            mrp_raw=mrp_data["raw"],
            mrp_value=mrp_data["value"],
            mrp_currency=mrp_data["currency"],
            mrp_inclusive_taxes_declared=mrp_data["inclusive_taxes_declared"],
            mrp_confidence=mrp_data["confidence"],
            # Net Qty
            net_quantity_raw=qty_data["raw"],
            net_quantity_value=qty_data["value"],
            net_quantity_unit=qty_data["unit"],
            net_quantity_is_standard=qty_data["is_standard_unit"],
            net_quantity_confidence=qty_data["confidence"],
            # USP
            unit_sale_price_raw=usp_data["raw"],
            unit_sale_price_value=usp_data["value"],
            unit_sale_price_unit=usp_data["unit"],
            unit_sale_price_confidence=usp_data["confidence"],
            # Dates
            mfg_date_raw=dates_data["mfg_date_raw"],
            mfg_date=dates_data["mfg_date"],
            exp_date_raw=dates_data["exp_date_raw"],
            exp_date=dates_data["exp_date"],
            date_confidence=dates_data["confidence"],
            # Batch
            batch_number=batch_data["batch_number"],
            batch_confidence=batch_data["confidence"],
            # Mfg / Packer
            manufacturer_name=mfg_data["manufacturer_name"],
            manufacturer_address=mfg_data["manufacturer_address"],
            packer_name=mfg_data["packer_name"],
            packer_address=mfg_data["packer_address"],
            importer_name=mfg_data["importer_name"],
            importer_address=mfg_data["importer_address"],
            mfg_packer_confidence=mfg_data["confidence"],
            # Origin
            country_of_origin=origin_data["country"],
            origin_confidence=origin_data["confidence"],
            # Consumer Care
            consumer_care_email=care_data["email"],
            consumer_care_phone=care_data["phone"],
            consumer_care_address=care_data["address"],
            consumer_care_confidence=care_data["confidence"],
            # Commodity
            commodity_generic_name=comm_data["generic_name"],
            brand_name=comm_data["brand_name"],
            commodity_confidence=comm_data["confidence"],
        )

        # Count declared mandatory fields
        declared_count = 0
        missing = []

        if decl.mrp_value is not None:
            declared_count += 1
        else:
            missing.append("MRP (Rule 6(1)(e))")

        if decl.net_quantity_value is not None:
            declared_count += 1
        else:
            missing.append("Net Quantity (Rule 6(1)(c))")

        if decl.mfg_date is not None or decl.mfg_date_raw is not None:
            declared_count += 1
        else:
            missing.append("Mfg Date (Rule 6(1)(d))")

        if decl.manufacturer_name is not None or decl.packer_name is not None or decl.importer_name is not None:
            declared_count += 1
        else:
            missing.append("Manufacturer / Packer (Rule 6(1)(a))")

        if decl.consumer_care_email is not None or decl.consumer_care_phone is not None or decl.consumer_care_address is not None:
            declared_count += 1
        else:
            missing.append("Consumer Care (Rule 6(1)(f))")

        if decl.country_of_origin is not None:
            declared_count += 1

        if decl.unit_sale_price_value is not None:
            declared_count += 1

        decl.declared_fields_count = declared_count
        decl.missing_mandatory_fields = missing

        # Calculate overall confidence across active fields
        confidences = [
            decl.mrp_confidence,
            decl.net_quantity_confidence,
            decl.date_confidence,
            decl.mfg_packer_confidence,
            decl.consumer_care_confidence,
        ]
        active_confs = [c for c in confidences if c > 0]
        decl.overall_confidence = sum(active_confs) / len(active_confs) if active_confs else 0.0

        return decl


# Singleton
declaration_extractor = DeclarationExtractor()
