"""
schemas/extraction.py
=====================
Pydantic v2 schemas for Statutory Declarations Extraction API (Rule 6 of LM PCR 2011)
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class MRPDeclarationSchema(BaseModel):
    raw: Optional[str] = None
    value: Optional[float] = None
    currency: str = "INR"
    inclusive_taxes_declared: bool = False
    confidence: float = 0.0

    model_config = {"from_attributes": True}


class NetQuantityDeclarationSchema(BaseModel):
    raw: Optional[str] = None
    value: Optional[float] = None
    unit: Optional[str] = None
    is_standard_unit: bool = False
    confidence: float = 0.0

    model_config = {"from_attributes": True}


class USPDeclarationSchema(BaseModel):
    raw: Optional[str] = None
    value: Optional[float] = None
    unit: Optional[str] = None
    confidence: float = 0.0

    model_config = {"from_attributes": True}


class DatesDeclarationSchema(BaseModel):
    mfg_date_raw: Optional[str] = None
    mfg_date: Optional[str] = None
    exp_date_raw: Optional[str] = None
    exp_date: Optional[str] = None
    confidence: float = 0.0

    model_config = {"from_attributes": True}


class BatchDeclarationSchema(BaseModel):
    value: Optional[str] = None
    confidence: float = 0.0

    model_config = {"from_attributes": True}


class ManufacturerDetailsSchema(BaseModel):
    manufacturer_name: Optional[str] = None
    manufacturer_address: Optional[str] = None
    packer_name: Optional[str] = None
    packer_address: Optional[str] = None
    importer_name: Optional[str] = None
    importer_address: Optional[str] = None
    confidence: float = 0.0

    model_config = {"from_attributes": True}


class CountryOfOriginSchema(BaseModel):
    country: Optional[str] = None
    confidence: float = 0.0

    model_config = {"from_attributes": True}


class ConsumerCareSchema(BaseModel):
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    confidence: float = 0.0

    model_config = {"from_attributes": True}


class CommoditySchema(BaseModel):
    generic_name: Optional[str] = None
    brand_name: Optional[str] = None
    confidence: float = 0.0

    model_config = {"from_attributes": True}


class DeclarationSummarySchema(BaseModel):
    declared_fields_count: int = 0
    missing_mandatory_fields: List[str] = Field(default_factory=list)
    overall_confidence: float = 0.0

    model_config = {"from_attributes": True}


class DeclarationsPayloadSchema(BaseModel):
    mrp: MRPDeclarationSchema
    net_quantity: NetQuantityDeclarationSchema
    unit_sale_price: USPDeclarationSchema
    dates: DatesDeclarationSchema
    batch_number: BatchDeclarationSchema
    manufacturer_details: ManufacturerDetailsSchema
    country_of_origin: CountryOfOriginSchema
    consumer_care: ConsumerCareSchema
    commodity: CommoditySchema
    summary: DeclarationSummarySchema

    model_config = {"from_attributes": True}


class ExtractedDeclarationsResponse(BaseModel):
    inspection_id: str
    inspection_number: str
    product_id: Optional[str] = None
    status: str
    declarations: DeclarationsPayloadSchema

    model_config = {"from_attributes": True}
