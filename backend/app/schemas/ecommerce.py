"""
schemas/ecommerce.py
====================
Stage 12 — E-Commerce Rule 6(10) Digital Label Compliance Auditor Schemas
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List
from enum import Enum


class EcommerceViolationType(str, Enum):
    MISSING_MRP = "MISSING_MRP"
    MISSING_USP = "MISSING_USP"
    MISSING_NET_QUANTITY = "MISSING_NET_QUANTITY"
    MISSING_COUNTRY_OF_ORIGIN = "MISSING_COUNTRY_OF_ORIGIN"
    MISSING_MFG_DETAILS = "MISSING_MFG_DETAILS"
    MISSING_IMPORTER_DETAILS = "MISSING_IMPORTER_DETAILS"
    MISSING_CUSTOMER_CARE = "MISSING_CUSTOMER_CARE"
    MISSING_EXPIRY_DATE = "MISSING_EXPIRY_DATE"
    MRP_WITHOUT_TAX_DECLARATION = "MRP_WITHOUT_TAX_DECLARATION"


class EcommerceViolation(BaseModel):
    code: EcommerceViolationType
    rule_ref: str
    description: str
    severity: str  # "CRITICAL", "MAJOR", "MINOR"


class EcommerceAuditRequest(BaseModel):
    """
    Digital product listing details submitted for Rule 6(10) compliance audit.
    Rule 6(10) (LM PCR 2011, as amended 2017 & 2021) mandates that every
    e-commerce entity display all mandatory declarations before purchase.
    """
    platform: str = Field(..., example="Amazon India", description="E-commerce marketplace name")
    listing_url: Optional[str] = Field(None, example="https://www.amazon.in/dp/B08XYZ")
    product_name: str
    mrp_displayed: Optional[float] = Field(None, description="MRP shown on listing page")
    mrp_includes_taxes_declared: bool = Field(False)
    net_quantity_displayed: Optional[str] = Field(None, example="500 g")
    unit_sale_price_displayed: Optional[str] = Field(None, example="₹1.20/g")
    country_of_origin_displayed: Optional[str] = Field(None)
    manufacturer_details_displayed: Optional[str] = Field(None)
    importer_details_displayed: Optional[str] = Field(None, description="Mandatory for imported goods")
    customer_care_displayed: Optional[str] = Field(None)
    expiry_date_displayed: Optional[str] = Field(None)
    is_imported: bool = Field(False, description="True if product is imported")
    product_category: Optional[str] = Field(None, example="Food & Beverages")


class EcommerceAuditResponse(BaseModel):
    """Result of Rule 6(10) digital label compliance audit."""
    platform: str
    product_name: str
    is_compliant: bool
    compliance_score: float = Field(..., description="Percentage compliance score (0–100)")
    violations: List[EcommerceViolation]
    total_violations: int
    critical_violations: int
    statutory_notice: Optional[str] = Field(None, description="Drafted show-cause notice text if non-compliant")
    relevant_sections: List[str] = Field(default_factory=list)
