"""
app.services.extractor
======================
Stage 4 — NLP & Regex Statutory Declarations Extractor Module
"""

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
from app.services.extractor.declaration_extractor import (
    ExtractedDeclarations,
    DeclarationExtractor,
    declaration_extractor,
)
from app.services.extractor.extraction_service import (
    ExtractionService,
    extraction_service,
)

__all__ = [
    "parse_mrp",
    "parse_net_quantity",
    "parse_unit_sale_price",
    "parse_dates",
    "parse_batch_number",
    "parse_mfg_packer_importer",
    "parse_country_of_origin",
    "parse_consumer_care",
    "parse_commodity_name",
    "ExtractedDeclarations",
    "DeclarationExtractor",
    "declaration_extractor",
    "ExtractionService",
    "extraction_service",
]
