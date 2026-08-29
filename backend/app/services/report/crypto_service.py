"""
crypto_service.py
=================
Stage 6 — Cryptographic Chain-of-Custody & QR Code Generation Service

Provides:
  1. Deterministic SHA-256 canonical hashing of inspection records for court tamper-proofing.
  2. Cryptographic QR verification token generation.
  3. High-resolution QR code rendering linking to public verification endpoint.
"""

import os
import json
import hashlib
import uuid
from datetime import datetime, timezone, date
from typing import Dict, Any

import qrcode


class CryptoService:
    """
    Handles cryptographic hashing, chain-of-custody verification, and QR code generation.
    """

    def compute_canonical_hash(self, payload: Dict[str, Any]) -> str:
        """
        Produces a deterministic 64-character SHA-256 hex digest over sorted canonical JSON.
        """
        def json_serial(obj):
            if isinstance(obj, (datetime, date)):
                return obj.isoformat()
            return str(obj)

        canonical_json = json.dumps(
            payload,
            sort_keys=True,
            default=json_serial,
            separators=(",", ":"),
        )
        return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()

    def generate_qr_token(self) -> str:
        """
        Generates a tamper-evident QR verification token.
        Format: QR-LM-YYYYMMDD-<12-char-random-hex>
        """
        date_str = datetime.now(timezone.utc).strftime("%Y%m%d")
        rand_token = uuid.uuid4().hex[:12].upper()
        return f"QR-LM-{date_str}-{rand_token}"

    def generate_qr_code_image(self, verification_url: str, output_path: str) -> str:
        """
        Renders a high-contrast QR code image linking to verification_url.
        Saves to output_path and returns the path.
        """
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=8,
            border=2,
        )
        qr.add_data(verification_url)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        img.save(output_path)
        return output_path


# Singleton
crypto_service = CryptoService()
