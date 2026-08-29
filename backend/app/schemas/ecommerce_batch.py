"""
schemas/ecommerce_batch.py
==========================
Stage 26 — High-Throughput E-Commerce Batch URL Crawler Schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime


class BatchProductUrlItem(BaseModel):
    """Single product URL entry in a batch scrape request."""
    url: str = Field(..., example="https://www.blinkit.com/prn/amul-gold-milk-1l/prid/102941")
    platform_name: str = Field("Blinkit", example="Blinkit")  # "Blinkit", "Zepto", "Amazon", "Flipkart", "Swiggy Instamart"
    product_category: Optional[str] = Field("Dairy & Groceries", example="Dairy & Groceries")
    seller_name: Optional[str] = Field(None, example="Blinkit Commerce Retail Pvt Ltd")


class BatchAuditRequest(BaseModel):
    """Request payload to initiate high-throughput batch URL compliance scraping."""
    batch_title: str = Field("National Quick-Commerce Audit", example="National Quick-Commerce Audit")
    platform_name: str = Field("Blinkit", example="Blinkit")
    items: List[BatchProductUrlItem] = Field(..., min_items=1, max_items=100)


class ProductListingAuditVerdict(BaseModel):
    """Individual product audit verdict resulting from batch crawling."""
    url: str
    product_title: str
    platform_name: str
    is_compliant: bool
    missing_declarations: List[str]
    detected_mrp: Optional[float]
    detected_net_qty: Optional[str]
    detected_country_of_origin: Optional[str]
    detected_usp: Optional[str]
    statutory_penalty_amount: float
    rule_violation_codes: List[str]


class BatchAuditResponse(BaseModel):
    """Aggregated batch audit summary report."""
    batch_id: str
    batch_title: str
    platform_name: str
    created_at: datetime
    total_listings_audited: int
    compliant_count: int
    non_compliant_count: int
    compliance_rate_pct: float
    total_statutory_liability_inr: float
    high_risk_infraction_distribution: Dict[str, int]
    items_verdicts: List[ProductListingAuditVerdict]
    bulk_show_cause_notice_draft: str
