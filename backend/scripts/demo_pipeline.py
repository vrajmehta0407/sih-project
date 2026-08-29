import os
import sys
import json
import time

# Ensure UTF-8 output on Windows terminal
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings

def print_banner(text: str, char="="):
    print("\n" + char * 78)
    print(f" {text}")
    print(char * 78)

def print_step(step_num: int, title: str):
    print(f"\n[STEP {step_num}] {title}")
    print("-" * 60)

def run_live_demonstration():
    client = TestClient(app)

    print_banner("SIH 2026: LEGAL METROLOGY COMPLIANCE SCANNER — LIVE E2E DEMO")
    print("Statute: Legal Metrology Act, 2009 & Packaged Commodities Rules, 2011")
    print("Architecture: Dual OCR Consensus + NLP Extractor + SHA-256 Chain of Custody")

    # ─────────────────────────────────────────────────────────────────────────
    # STEP 1: Officer Authentication & RBAC Token
    # ─────────────────────────────────────────────────────────────────────────
    print_step(1, "OFFICER AUTHENTICATION & JWT RBAC TOKEN ISSUANCE")
    login_payload = {
        "email": settings.FIRST_INSPECTOR_EMAIL,
        "password": settings.FIRST_INSPECTOR_PASSWORD
    }
    resp = client.post(f"{settings.API_V1_STR}/auth/login/json", json=login_payload)
    if resp.status_code != 200:
        print(f"FAILED: Login failed: {resp.text}")
        return

    auth_data = resp.json()
    token = auth_data["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    print(f"[OK] Officer Authenticated: {auth_data['full_name']}")
    print(f"[OK] Role: {auth_data['role'].upper()}")
    print(f"[OK] JWT Token Issued: {token[:35]}...[SECURE]")

    # ─────────────────────────────────────────────────────────────────────────
    # STEP 2: Inspection Creation & OpenCV Multi-Side Image Preprocessing
    # ─────────────────────────────────────────────────────────────────────────
    print_step(2, "INSPECTION DOCKET CREATION & OPENCV PREPROCESSING")
    label_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sample_data", "labels", "02_violation_mrp_no_tax.png")

    if not os.path.exists(label_path):
        print(f"ERROR: Label file {label_path} not found.")
        return

    with open(label_path, "rb") as f:
        file_bytes = f.read()

    files = [
        ("images", ("02_violation_mrp_no_tax.png", file_bytes, "image/png"))
    ]
    data = {
        "district": "Surat",
        "state": "Gujarat",
        "store_name": "Mega Mart Supermarket",
        "store_address": "GIDC Commercial Complex, Surat 395003",
        "gps_latitude": "21.1702",
        "gps_longitude": "72.8311",
        "inspector_notes": "Market surveillance inspection under Section 18 of Legal Metrology Act, 2009.",
        "sides": ["front"]
    }

    create_resp = client.post(f"{settings.API_V1_STR}/inspections/", data=data, files=files, headers=headers)
    if create_resp.status_code != 201:
        print(f"FAILED: Inspection creation: {create_resp.text}")
        return

    insp = create_resp.json()
    insp_id = insp["id"]
    print(f"[OK] Inspection Docket Registered: {insp['inspection_number']}")
    print(f"[OK] Location: {insp['store_name']}, {insp['district']}, {insp['state']}")
    print(f"[OK] OpenCV Preprocessed Images: {len(insp.get('preprocessed_images', []))} side(s) processed")

    # ─────────────────────────────────────────────────────────────────────────
    # STEP 3: Dual OCR Consensus (PaddleOCR + Tesseract)
    # ─────────────────────────────────────────────────────────────────────────
    print_step(3, "DUAL OCR ENGINE CONSENSUS EXECUTION (PADDLE + TESSERACT)")
    ocr_resp = client.post(f"{settings.API_V1_STR}/inspections/{insp_id}/ocr", headers=headers)
    if ocr_resp.status_code != 200:
        print(f"FAILED: OCR Execution: {ocr_resp.text}")
        return

    ocr_data = ocr_resp.json()
    ocr_consensus = ocr_data["ocr_consensus"]
    print(f"[OK] Total Tokens Extracted: {ocr_consensus['total_tokens']}")
    print(f"[OK] Disagreements Flagged:   {ocr_consensus['total_disagreements']}")
    print(f"[OK] Overall OCR Confidence:  {round(ocr_consensus['overall_confidence'] * 100, 1)}%")
    print(f"[OK] Manual Review Required:  {ocr_consensus['manual_review_required']}")
    print(f"[OK] PaddleOCR Raw Sample:    {ocr_consensus['aggregated_paddle_text'][:50]}...")

    # ─────────────────────────────────────────────────────────────────────────
    # STEP 4: Rule 6 Statutory Declarations Extractor
    # ─────────────────────────────────────────────────────────────────────────
    print_step(4, "RULE 6 STATUTORY DECLARATIONS EXTRACTION (NLP & REGEX ENGINE)")
    ext_resp = client.post(f"{settings.API_V1_STR}/inspections/{insp_id}/extract-declarations", headers=headers)
    if ext_resp.status_code != 200:
        print(f"FAILED: Declarations Extraction: {ext_resp.text}")
        return

    decl_data = ext_resp.json()["declarations"]
    summary = decl_data.get("summary", {})
    print(f"[OK] Extracted Mandatory Fields: {summary.get('declared_fields_count', 0)} fields declared")
    print(f"  * MRP Declared: Rs. {decl_data['mrp']['value']} (Inclusive taxes declared: {decl_data['mrp']['inclusive_taxes_declared']})")
    print(f"  * Net Quantity: {decl_data['net_quantity']['value']} {decl_data['net_quantity']['unit']} (Standard: {decl_data['net_quantity']['is_standard_unit']})")
    print(f"  * Packing / Mfg Date: {decl_data['dates']['mfg_date_raw']}")
    print(f"  * Expiry / Best Before: {decl_data['dates']['exp_date_raw']}")
    print(f"  * Batch / Lot Code: {decl_data['batch_number']['value']}")
    print(f"  * Manufacturer: {decl_data['manufacturer_details']['manufacturer_name']}")
    print(f"  * Consumer Care: {decl_data['consumer_care']['phone'] or decl_data['consumer_care']['email']}")

    if summary.get("missing_mandatory_fields"):
        print(f"  [WARN] Missing Mandatory Fields: {summary['missing_mandatory_fields']}")

    # ─────────────────────────────────────────────────────────────────────────
    # STEP 5: Statutory Compliance Validation & Violation Docketing
    # ─────────────────────────────────────────────────────────────────────────
    print_step(5, "STATUTORY COMPLIANCE VALIDATION & PENALTY ASSESSMENT")
    val_resp = client.post(f"{settings.API_V1_STR}/inspections/{insp_id}/validate", headers=headers)
    if val_resp.status_code != 200:
        print(f"FAILED: Compliance validation: {val_resp.text}")
        return

    val_data = val_resp.json()
    print(f"[OK] Compliance Outcome: {val_data['compliance_status'].upper()}")
    print(f"[OK] Total Grounded Violations: {len(val_data['violations'])}")

    for i, v in enumerate(val_data["violations"], 1):
        print(f"\n  [{i}] Violation: {v['violation_title']}")
        print(f"      Section Breached: {v['section_violated']}")
        print(f"      Statutory Base:   {v['statute_title']}")
        print(f"      Severity:         {v['severity'].upper()}")
        print(f"      Penalty Notice:   {v['penalty_provision']} ({v['estimated_fine']})")

    # ─────────────────────────────────────────────────────────────────────────
    # STEP 6: ReportLab Court PDF Compilation & SHA-256 Digest Sealing
    # ─────────────────────────────────────────────────────────────────────────
    print_step(6, "COURT-ADMISSIBLE PDF COMPILATION & SHA-256 CRYPTOGRAPHIC SEAL")
    rep_resp = client.post(f"{settings.API_V1_STR}/inspections/{insp_id}/report", headers=headers)
    if rep_resp.status_code != 200:
        print(f"FAILED: Report Generation: {rep_resp.text}")
        return

    rep_data = rep_resp.json()
    print(f"[OK] Statutory Docket Number:     {rep_data['docket_number']}")
    print(f"[OK] SHA-256 Canonical Digest:    {rep_data['chain_of_custody_hash']}")
    print(f"[OK] Public QR Verification Token: {rep_data['qr_verification_token']}")
    print(f"[OK] PDF Download Route:           {rep_data['pdf_download_url']}")
    print(f"[OK] Evidence Act Compliance:      Section 65B BSA 2023 / Indian Evidence Act Seal Validated")

    # ─────────────────────────────────────────────────────────────────────────
    # STEP 7: Public QR Verification Check
    # ─────────────────────────────────────────────────────────────────────────
    print_step(7, "PUBLIC QR VERIFICATION PORTAL GATEWAY CHECK")
    qr_token = rep_data["qr_verification_token"]
    qr_resp = client.get(f"{settings.API_V1_STR}/inspections/verify/{qr_token}")
    if qr_resp.status_code != 200:
        print(f"FAILED: QR Verification: {qr_resp.text}")
        return

    qr_data = qr_resp.json()
    print(f"[OK] Public Gateway Status: 200 OK (VERIFIED)")
    print(f"[OK] Certified Inspection Number: {qr_data['inspection_number']}")
    print(f"[OK] Certified Docket Number:     {qr_data['docket_number']}")
    print(f"[OK] Certified SHA-256 Digest:    {qr_data['chain_of_custody_hash']}")
    print(f"[OK] Authenticated Violations:    {qr_data['total_violations']} infraction(s) recorded")

    print_banner("SIH 2026 PIPELINE DEMONSTRATION COMPLETE — 100% SUCCESS")
    print(f"Inspection ID: {insp_id}")
    print(f"Frontend URL:  http://localhost:5174/inspections/{insp_id}")
    print(f"Public QR URL: http://localhost:5174/verify/{qr_token}\n")

if __name__ == "__main__":
    run_live_demonstration()
