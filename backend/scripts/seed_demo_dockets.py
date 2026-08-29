import os
import sys
import uuid
import datetime
from datetime import timezone, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import SessionLocal
from app.models.user import User
from app.models.inspection import Inspection
from app.models.product import Product
from app.models.violation import Violation
from app.models.report import Report
from app.models.rule import Rule, RuleVersion
from app.models.audit_log import AuditLog
from app.services.report.crypto_service import crypto_service
from app.services.report.pdf_report_generator import pdf_report_generator

def seed_rich_demo_data():
    db = SessionLocal()

    print("==============================================================================")
    print(" SEEDING COMPREHENSIVE NATIONAL DEMO DATASET FOR SIH 2026 JURY EVALUATION")
    print("==============================================================================")

    # 1. Fetch active inspector & rule version
    inspector = db.query(User).filter(User.email == "inspector.mumbai@legalmetrology.gov.in").first()
    active_version = db.query(RuleVersion).filter(RuleVersion.is_active == True).first()
    rules = db.query(Rule).filter(Rule.version_id == active_version.id).all() if active_version else []

    if not inspector:
        print("ERROR: Inspector user not found. Run backend initialization first.")
        db.close()
        return

    # 2. Portfolio of 12 Realistic Multi-State Packaging Inspections
    demo_records = [
        {
            "store_name": "Modern Hypermarket Ltd",
            "store_address": "Linking Road, Bandra West, Mumbai 400050",
            "district": "Mumbai Suburban",
            "state": "Maharashtra",
            "lat": 19.0596,
            "lon": 72.8295,
            "product_name": "Shuddh Besan (Gram Flour) 500g",
            "brand_name": "Shuddh Foods",
            "manufacturer_name": "Shuddh Foods Agrotech Pvt Ltd, Plot 14, MIDC Phase 2, Pune 411019",
            "mrp_value": 65.0,
            "mrp_inclusive": True,
            "net_qty_value": 500.0,
            "net_qty_unit": "g",
            "mfg_date": datetime.date(2026, 2, 1),
            "exp_date": datetime.date(2026, 12, 1),
            "batch_number": "SB-2026-08",
            "consumer_care": "1800-222-3344 care@shuddhfoods.in",
            "compliance_status": "compliant",
            "violations": [],
            "days_ago": 1
        },
        {
            "store_name": "Mega Mart Supermarket",
            "store_address": "GIDC Commercial Complex, Surat 395003",
            "district": "Surat",
            "state": "Gujarat",
            "lat": 21.1702,
            "lon": 72.8311,
            "product_name": "Prime Sunflower Oil 1 L",
            "brand_name": "Prime Oils",
            "manufacturer_name": "Prime Edible Oils Ltd, GIDC Estate, Surat 395003",
            "mrp_value": 140.0,
            "mrp_inclusive": False,  # Violation: Missing incl of taxes
            "net_qty_value": 1.0,
            "net_qty_unit": "l",
            "mfg_date": datetime.date(2026, 1, 1),
            "exp_date": datetime.date(2027, 1, 1),
            "batch_number": "PSO-9921",
            "consumer_care": "1800-111-9988 support@primeoils.in",
            "compliance_status": "non_compliant",
            "violations": [
                {
                    "rule_code": "LM_RULE_6_1_E_MRP",
                    "field_affected": "mrp",
                    "section_violated": "Rule 6(1)(e), LM PCR 2011 r/w Section 18",
                    "statute_title": "Legal Metrology (Packaged Commodities) Rules, 2011",
                    "penalty_provision": "Section 36(1), Legal Metrology Act, 2009",
                    "estimated_fine": "Fine up to ₹25,000",
                    "violation_title": "Omission of Mandatory 'Inclusive of All Taxes' Statement",
                    "violation_description": "MRP of ₹140.00 declared without mandatory 'inclusive of all taxes' phrase.",
                    "severity": "major",
                    "repeat": False
                }
            ],
            "days_ago": 2
        },
        {
            "store_name": "Royal Dry Fruits & Nuts",
            "store_address": "MG Road, Panaji 403001",
            "district": "North Goa",
            "state": "Goa",
            "lat": 15.4909,
            "lon": 73.8278,
            "product_name": "Crispy Roasted Cashews 500g",
            "brand_name": "Royal Crunch",
            "manufacturer_name": "Royal Crunch Nutworks, Panaji 403001",
            "mrp_value": 450.0,
            "mrp_inclusive": True,
            "net_qty_value": 500.0,
            "net_qty_unit": "gm",  # Violation: non-standard unit
            "mfg_date": datetime.date(2026, 2, 1),
            "exp_date": datetime.date(2026, 11, 1),
            "batch_number": "RC-4402",
            "consumer_care": "1800-444-5566 help@royalcrunch.in",
            "compliance_status": "non_compliant",
            "violations": [
                {
                    "rule_code": "LM_RULE_11_NET_QTY_STANDARD",
                    "field_affected": "net_quantity",
                    "section_violated": "Rule 6(1)(c) & Rule 11, LM PCR 2011 r/w Section 25",
                    "statute_title": "Legal Metrology (Packaged Commodities) Rules, 2011",
                    "penalty_provision": "Section 29, Legal Metrology Act, 2009",
                    "estimated_fine": "Fine up to ₹10,000",
                    "violation_title": "Non-Standard Unit of Weight ('gm' used instead of standard 'g')",
                    "violation_description": "Commodity declares '500 gm'. Under Rule 11, gram must strictly be expressed as 'g'.",
                    "severity": "major",
                    "repeat": False
                }
            ],
            "days_ago": 3
        },
        {
            "store_name": "Golden Wholesalers Hub",
            "store_address": "APMC Market, Vashi, Navi Mumbai 400703",
            "district": "Thane",
            "state": "Maharashtra",
            "lat": 19.0771,
            "lon": 72.9986,
            "product_name": "Golden Drop Palm Oil 1 L",
            "brand_name": "Golden Drop",
            "manufacturer_name": "Golden Drop Agro Industries Ltd",
            "mrp_value": 110.0,
            "mrp_inclusive": False,
            "net_qty_value": 1000.0,
            "net_qty_unit": "cc",
            "mfg_date": datetime.date(2026, 1, 1),
            "exp_date": datetime.date(2026, 10, 1),
            "batch_number": "GD-991",
            "consumer_care": None,
            "compliance_status": "non_compliant",
            "violations": [
                {
                    "rule_code": "LM_RULE_6_1_E_MRP",
                    "field_affected": "mrp",
                    "section_violated": "Rule 6(1)(e) r/w Section 18 & Section 36(2)",
                    "statute_title": "Legal Metrology Act, 2009",
                    "penalty_provision": "Section 36(2), Legal Metrology Act, 2009",
                    "estimated_fine": "Section 36(2) Repeat Offence: Fine up to ₹50,000 or imprisonment up to 1 year",
                    "violation_title": "Repeat Offence: Omission of Mandatory Taxes Statement",
                    "violation_description": "Entity is a recidivist violator with 3 prior compounding notices.",
                    "severity": "critical",
                    "repeat": True
                },
                {
                    "rule_code": "LM_RULE_6_1_F_CONSUMER_CARE",
                    "field_affected": "consumer_care",
                    "section_violated": "Rule 6(1)(f), LM PCR 2011",
                    "statute_title": "Legal Metrology (Packaged Commodities) Rules, 2011",
                    "penalty_provision": "Section 36(1), Legal Metrology Act, 2009",
                    "estimated_fine": "Fine up to ₹25,000",
                    "violation_title": "Complete Absence of Consumer Care Redressal Mechanism",
                    "violation_description": "Neither email, telephone number, nor physical address provided for grievance.",
                    "severity": "critical",
                    "repeat": True
                }
            ],
            "days_ago": 4
        },
        {
            "store_name": "Fresh Foods Daily Bazaar",
            "store_address": "Connaught Place, New Delhi 110001",
            "district": "New Delhi",
            "state": "Delhi",
            "lat": 28.6304,
            "lon": 77.2177,
            "product_name": "Premium Basmati Rice 5 kg",
            "brand_name": "Kohinoor Koh",
            "manufacturer_name": "Koh Foods India Ltd, Delhi 110034",
            "mrp_value": 480.0,
            "mrp_inclusive": True,
            "net_qty_value": 5.0,
            "net_qty_unit": "kg",
            "mfg_date": datetime.date(2026, 1, 1),
            "exp_date": datetime.date(2027, 1, 1),
            "batch_number": "KB-2026",
            "consumer_care": "1800-999-1122 care@kohfoods.in",
            "compliance_status": "compliant",
            "violations": [],
            "days_ago": 5
        },
        {
            "store_name": "Apex General Stores",
            "store_address": "Indiranagar 100 Feet Road, Bengaluru 560038",
            "district": "Bengaluru Urban",
            "state": "Karnataka",
            "lat": 12.9784,
            "lon": 77.6408,
            "product_name": "Herbal Toothpaste 150g",
            "brand_name": "AyurDent",
            "manufacturer_name": "Ayur Herbals India, Bengaluru 560068",
            "mrp_value": 85.0,
            "mrp_inclusive": True,
            "net_qty_value": 150.0,
            "net_qty_unit": "g",
            "mfg_date": datetime.date(2026, 2, 1),
            "exp_date": datetime.date(2028, 2, 1),
            "batch_number": "AD-882",
            "consumer_care": "080-22334455 support@ayurdent.com",
            "compliance_status": "compliant",
            "violations": [],
            "days_ago": 6
        },
        {
            "store_name": "Heritage Provisions Mart",
            "store_address": "T. Nagar, Chennai 600017",
            "district": "Chennai",
            "state": "Tamil Nadu",
            "lat": 13.0418,
            "lon": 80.2341,
            "product_name": "Pure Cow Ghee 500 ml",
            "brand_name": "Annapoorna Dairy",
            "manufacturer_name": "Annapoorna Milk Producers Union, Madurai 625020",
            "mrp_value": 310.0,
            "mrp_inclusive": True,
            "net_qty_value": 500.0,
            "net_qty_unit": "ml",
            "mfg_date": datetime.date(2026, 1, 1),
            "exp_date": datetime.date(2026, 9, 1),
            "batch_number": "AG-104",
            "consumer_care": "1800-425-9988 care@annapoornadairy.in",
            "compliance_status": "compliant",
            "violations": [],
            "days_ago": 7
        },
        {
            "store_name": "Suburban Corner Mart",
            "store_address": "FC Road, Shivajinagar, Pune 411005",
            "district": "Pune",
            "state": "Maharashtra",
            "lat": 18.5204,
            "lon": 73.8567,
            "product_name": "Dairy Fresh Milk 500 ml",
            "brand_name": "Fresh Dairy",
            "manufacturer_name": "Fresh Dairy Union, Anand 388001",
            "mrp_value": 32.0,
            "mrp_inclusive": True,
            "net_qty_value": 500.0,
            "net_qty_unit": "ml",
            "mfg_date": datetime.date(2026, 1, 1),
            "exp_date": datetime.date(2026, 3, 1),  # Expired
            "batch_number": "FD-03",
            "consumer_care": "1800-333-2211 dairy@freshmilk.org",
            "compliance_status": "non_compliant",
            "violations": [
                {
                    "rule_code": "LM_RULE_6_1_D_DATES",
                    "field_affected": "exp_date",
                    "section_violated": "Rule 6(1)(h) & Rule 6(1)(d), LM PCR 2011",
                    "statute_title": "Legal Metrology (Packaged Commodities) Rules, 2011",
                    "penalty_provision": "Section 36(1), Legal Metrology Act, 2009",
                    "estimated_fine": "Fine up to ₹25,000",
                    "violation_title": "Offer / Sale of Expired Pre-Packaged Commodity on Market Shelf",
                    "violation_description": "Product 'Use By' date expired on 2026-03-01.",
                    "severity": "critical",
                    "repeat": False
                }
            ],
            "days_ago": 8
        }
    ]

    created_count = 0

    for rec in demo_records:
        created_time = datetime.datetime.now(timezone.utc) - timedelta(days=rec["days_ago"])
        insp_num = f"INS-202608{25-rec['days_ago']:02d}-{uuid.uuid4().hex[:8].upper()}"

        # 1. Create Inspection
        insp = Inspection(
            id=str(uuid.uuid4()),
            inspection_number=insp_num,
            inspector_id=inspector.id,
            rule_version_id=active_version.id if active_version else None,
            district=rec["district"],
            state=rec["state"],
            store_name=rec["store_name"],
            store_address=rec["store_address"],
            gps_latitude=rec["lat"],
            gps_longitude=rec["lon"],
            gps_accuracy_meters=4.5,
            inspector_notes="Seeded national compliance docket for SIH 2026 evaluation.",
            status="completed",
            compliance_status=rec["compliance_status"],
            created_at=created_time,
            updated_at=created_time
        )
        db.add(insp)

        # 2. Create Product
        prod = Product(
            id=str(uuid.uuid4()),
            inspection_id=insp.id,
            product_name=rec["product_name"],
            brand_name=rec["brand_name"],
            mrp_value=rec["mrp_value"],
            mrp_currency="INR",
            mrp_inclusive_taxes_declared=rec["mrp_inclusive"],
            net_quantity_value=rec["net_qty_value"],
            net_quantity_unit=rec["net_qty_unit"],
            mfg_date=rec["mfg_date"],
            exp_date=rec["exp_date"],
            batch_number=rec["batch_number"],
            manufacturer_name=rec["manufacturer_name"],
            consumer_care_phone=rec["consumer_care"],
            country_of_origin="India",
            created_at=created_time,
            updated_at=created_time
        )
        db.add(prod)

        # 3. Add Violations (if any)
        for v in rec["violations"]:
            matching_rule = next((r for r in rules if r.rule_code == v["rule_code"]), None)
            viol = Violation(
                id=str(uuid.uuid4()),
                inspection_id=insp.id,
                rule_id=matching_rule.id if matching_rule else None,
                rule_code=v["rule_code"],
                field_affected=v["field_affected"],
                section_violated=v["section_violated"],
                statute_title=v["statute_title"],
                penalty_provision=v["penalty_provision"],
                estimated_fine=v["estimated_fine"],
                violation_title=v["violation_title"],
                violation_description=v["violation_description"],
                severity=v["severity"],
                is_repeat_offender_alert=v["repeat"],
                created_at=created_time
            )
            db.add(viol)

        # 4. Generate SHA-256 Digest & QR Token
        sha_hash = crypto_service.compute_canonical_hash({
            "inspection_id": insp.id,
            "inspection_number": insp.inspection_number,
            "inspector_id": inspector.id,
            "timestamp_utc": created_time.isoformat(),
            "product_name": prod.product_name,
            "mrp_value": prod.mrp_value,
            "net_quantity": f"{prod.net_quantity_value} {prod.net_quantity_unit}",
            "compliance_status": insp.compliance_status,
            "violations_count": len(rec["violations"])
        })
        qr_token = crypto_service.generate_qr_token()
        insp.record_sha256_hash = sha_hash
        insp.qr_verification_token = qr_token

        # 5. Create Report Record
        docket_prefix = "MH" if rec["state"] == "Maharashtra" else "GU" if rec["state"] == "Gujarat" else "DL" if rec["state"] == "Delhi" else "KA" if rec["state"] == "Karnataka" else "TN" if rec["state"] == "Tamil Nadu" else "IN"
        docket_no = f"DOCKET-{docket_prefix}-202608{25-rec['days_ago']:02d}-{uuid.uuid4().hex[:4].upper()}"

        rep = Report(
            id=str(uuid.uuid4()),
            inspection_id=insp.id,
            docket_number=docket_no,
            pdf_file_path=f"generated_reports/{insp.id}/statutory_notice.pdf",
            pdf_download_url=f"/api/v1/inspections/{insp.id}/report/download",
            chain_of_custody_hash=sha_hash,
            status="issued",
            generated_at=created_time,
            signed_by_inspector=True
        )
        db.add(rep)

        # 6. Audit Log
        audit = AuditLog(
            id=str(uuid.uuid4()),
            action="GENERATE_REPORT",
            entity_name="Inspection",
            entity_id=insp.id,
            user_id=inspector.id,
            details={
                "docket_number": docket_no,
                "compliance_status": insp.compliance_status,
                "sha256_hash": sha_hash
            },
            created_at=created_time
        )
        db.add(audit)

        created_count += 1

    db.commit()
    db.close()

    print(f"[OK] Successfully seeded {created_count} realistic national compliance inspection records!")
    print("[OK] Executive Dashboard, Charts, GIS Table & Audit Logs are now richly populated.")

if __name__ == "__main__":
    seed_rich_demo_data()
