"""
endpoints/registry.py
======================
Stage 13 — National Product Reference Registry API Endpoints
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.security import require_inspector, require_admin
from app.models.registered_product import RegisteredProduct
from app.models.user import User
from app.schemas.registry import RegisteredProductCreate, RegisteredProductResponse
from app.schemas.scorecard import (
    BrandScorecardResponse,
    CertificateGenerateRequest,
    CertificateGenerateResponse,
)
from app.services.brand_scorecard_service import brand_scorecard_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post(
    "/products",
    response_model=RegisteredProductResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a product in the National Reference Registry",
)
def register_product(
    payload: RegisteredProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    Register a manufacturer's authorized product in the National Product Registry.
    Only Enforcement Directors (admin) may register reference products.
    Provides the golden reference baseline for counterfeit detection.
    """
    # Check for duplicate barcode
    if payload.barcode_ean13:
        existing = db.query(RegisteredProduct).filter(
            RegisteredProduct.barcode_ean13 == payload.barcode_ean13,
            RegisteredProduct.is_active == True,
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"An active product with barcode '{payload.barcode_ean13}' is already registered.",
            )

    product = RegisteredProduct(
        **payload.model_dump(exclude_none=True),
        registered_by_email=current_user.email,
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    logger.info("Product '%s' registered by %s", product.product_name, current_user.email)
    return product


@router.get(
    "/products",
    response_model=List[RegisteredProductResponse],
    summary="List all registered products in the National Registry",
)
def list_registered_products(
    active_only: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_inspector),
):
    """List all registered products, optionally filtering to active entries only."""
    query = db.query(RegisteredProduct)
    if active_only:
        query = query.filter(RegisteredProduct.is_active == True)
    return query.order_by(RegisteredProduct.created_at.desc()).all()


@router.get(
    "/products/barcode/{barcode}",
    response_model=RegisteredProductResponse,
    summary="Lookup a product by EAN-13 barcode",
)
def lookup_by_barcode(
    barcode: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_inspector),
):
    """
    Lookup a manufacturer-registered product by its EAN-13 barcode.
    Used by field inspectors to instantly retrieve the compliance baseline
    after the barcode is scanned during preprocessing.
    """
    product = db.query(RegisteredProduct).filter(
        RegisteredProduct.barcode_ean13 == barcode,
        RegisteredProduct.is_active == True,
    ).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No active registered product found for barcode '{barcode}'.",
        )
    return product


@router.delete(
    "/products/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deactivate a registered product",
)
def deactivate_product(
    product_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Soft-deactivate a registered product entry (does not delete the record)."""
    product = db.query(RegisteredProduct).filter(
        RegisteredProduct.id == product_id
    ).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found.")
    product.is_active = False
    db.commit()
    logger.info("Product %s deactivated by %s", product_id, current_admin.email)


# ===========================================================================
# Brand Compliance Scorecard & National Trust Seal Index
# ===========================================================================

@router.get(
    "/brands/{brand_name}/scorecard",
    response_model=BrandScorecardResponse,
    summary="Get Brand Compliance Scorecard & Trust Tier Index",
)
def get_brand_scorecard(
    brand_name: str,
    db: Session = Depends(get_db),
):
    """
    Public lookup endpoint to calculate dynamic brand packaging compliance score (0–100%),
    recidivism frequency, and assign a National Trust Tier (Platinum, Gold, Amber, Red).
    """
    return brand_scorecard_service.compute_scorecard(db=db, brand_name=brand_name)


# ===========================================================================
# Statutory Model Registration & Verification Certificate Generator
# ===========================================================================

@router.post(
    "/certificates/generate",
    response_model=CertificateGenerateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate Legal Metrology Model Verification Certificate",
)
def generate_model_certificate(
    req: CertificateGenerateRequest,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_admin),
):
    """
    Generate an official digitally sealed Certificate of Model Registration under Rule 27
    of the Legal Metrology Rules, 2011 with SHA-256 seal and QR verification gateway token.
    Restricted to Enforcement Directors (admin).
    """
    return brand_scorecard_service.generate_certificate(req=req, issued_by_email=current_admin.email)
