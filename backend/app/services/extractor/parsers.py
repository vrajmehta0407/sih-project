"""
parsers.py
==========
Stage 4 — Specialized Regex & NLP Parsers for Rule 6 of Legal Metrology (Packaged Commodities) Rules, 2011.

Includes:
  1. parse_mrp                 — Rule 6(1)(e)
  2. parse_net_quantity        — Rule 6(1)(c) & Rule 11
  3. parse_unit_sale_price     — Rule 6(1)(k)
  4. parse_dates               — Rule 6(1)(d) & Rule 6(1)(h)
  5. parse_batch_number        — Traceability
  6. parse_mfg_packer_importer — Rule 6(1)(a)
  7. parse_country_of_origin   — Rule 6(1)(g)
  8. parse_consumer_care       — Rule 6(1)(f)
  9. parse_commodity_name      — Rule 6(1)(b)
"""

import re
import calendar
from datetime import datetime, date, timedelta
from typing import Optional, Dict, Any, Tuple, List

# ---------------------------------------------------------------------------
# Month Name Mappings
# ---------------------------------------------------------------------------
MONTH_MAP = {
    "jan": 1, "january": 1,
    "feb": 2, "february": 2,
    "mar": 3, "march": 3,
    "apr": 4, "april": 4,
    "may": 5,
    "jun": 6, "june": 6,
    "jul": 7, "july": 7,
    "aug": 8, "august": 8,
    "sep": 9, "september": 9, "sept": 9,
    "oct": 10, "october": 10,
    "nov": 11, "november": 11,
    "dec": 12, "december": 12,
}

# Standard SI units under Legal Metrology Act
STANDARD_UNITS = {"g", "kg", "mg", "l", "ml", "m", "cm", "mm", "sq.m", "sq.cm", "N", "u"}

UNIT_NORMALIZATION_MAP = {
    "gm": "g", "gms": "g", "gram": "g", "grams": "g", "ग्राम": "g", "ग्रा": "g", "ग्रा.": "g",
    "kg": "kg", "kgs": "kg", "kilogram": "kg", "kilograms": "kg", "कि.ग्रा.": "kg", "कि.ग्रा": "kg", "किग्रा": "kg", "किलोग्राम": "kg",
    "mg": "mg", "mgs": "mg", "milligram": "mg", "milligrams": "mg", "मिलीग्राम": "mg", "मिग्रा": "mg",
    "ml": "ml", "mls": "ml", "millilitre": "ml", "millilitres": "ml", "मिली": "ml", "मिलीलीटर": "ml",
    "l": "l", "ltr": "l", "ltrs": "l", "litre": "l", "litres": "l", "liter": "l", "liters": "l", "लीटर": "l", "ली": "l", "ली.": "l",
    "m": "m", "meter": "m", "meters": "m", "metre": "m", "metres": "m", "मीटर": "m",
    "cm": "cm", "centimeter": "cm", "centimetre": "cm", "सेमी": "cm",
    "mm": "mm", "millimeter": "mm", "millimetre": "mm", "मिमी": "mm",
    "sq.m": "sq.m", "sqm": "sq.m", "sq m": "sq.m", "वर्ग मीटर": "sq.m",
    "n": "N", "no": "N", "nos": "N", "number": "N", "numbers": "N", "संख्या": "N", "नग": "N", "इकाई": "N",
    "u": "N", "unit": "N", "units": "N", "piece": "N", "pieces": "N", "pcs": "N",
    "tablets": "N", "capsules": "N", "wipes": "N", "sheets": "N",
}


# ---------------------------------------------------------------------------
# 1. MRP & Inclusive of All Taxes Parser — Rule 6(1)(e)
# ---------------------------------------------------------------------------
def parse_mrp(text: str) -> Dict[str, Any]:
    """
    Extracts MRP value, currency, raw declaration string, and checks for
    mandatory 'inclusive of all taxes' declaration (English and Hindi).
    """
    result: Dict[str, Any] = {
        "raw": None,
        "value": None,
        "currency": "INR",
        "inclusive_taxes_declared": False,
        "confidence": 0.0,
    }

    # Check for statutory tax phrase across English & Hindi text
    tax_pattern = re.compile(
        r"(?:(?:incl(?:usive)?\.?\s*(?:of)?\s*(?:all)?\s*taxes)|(?:incl\.?\s*all\s*taxes)|(?:all\s*taxes\s*incl(?:usive)?\.?)|(?:सभी\s*कर(?:ों)?\s*सहित)|(?:कर\s*सहित))",
        re.IGNORECASE,
    )
    if tax_pattern.search(text):
        result["inclusive_taxes_declared"] = True

    # Patterns for MRP extraction (English & Hindi)
    mrp_patterns = [
        # Pattern 1: MRP Rs. 250.00 / MRP: ₹199 / अधिकतम खुदरा मूल्य ₹250
        re.compile(
            r"(?:M\.?R\.?P\.?|MAX(?:IMUM)?\.?\s*RETAIL\s*PRICE|अधिकतम\s*खुदरा\s*मूल्य|अ\.?\s*खु\.?\s*मू\.?|एम\.?आर\.?पी\.?)\s*[:\-\.]?\s*(?:Rs\.?|INR|₹|रु\.?|रुपये)?\s*([0-9]+(?:\.[0-9]{1,2})?)",
            re.IGNORECASE,
        ),
        # Pattern 2: ₹ 250.00 / Rs. 150.50 / रु 250
        re.compile(
            r"(?:Rs\.?|INR|₹|रु\.?)\s*([0-9]+(?:\.[0-9]{1,2})?)\s*(?:\(?(?:incl|inclusive|सभी\s*कर))?",
            re.IGNORECASE,
        ),
        # Pattern 3: Price: Rs 50 / मूल्य: ₹50
        re.compile(
            r"(?:PRICE|RETAIL\s*PRICE|मूल्य|कीमत)\s*[:\-\.]?\s*(?:Rs\.?|INR|₹|रु\.?)?\s*([0-9]+(?:\.[0-9]{1,2})?)",
            re.IGNORECASE,
        ),
    ]

    for pat in mrp_patterns:
        match = pat.search(text)
        if match:
            val_str = match.group(1)
            try:
                val = float(val_str)
                result["value"] = val
                result["raw"] = match.group(0).strip()
                result["confidence"] = 0.95 if result["inclusive_taxes_declared"] else 0.85
                break
            except ValueError:
                continue

    return result


# ---------------------------------------------------------------------------
# 2. Net Quantity Parser — Rule 6(1)(c) & Rule 11
# ---------------------------------------------------------------------------
def parse_net_quantity(text: str) -> Dict[str, Any]:
    """
    Extracts net quantity magnitude, raw string, and standardizes unit under Rule 11.
    """
    result: Dict[str, Any] = {
        "raw": None,
        "value": None,
        "unit": None,
        "is_standard_unit": False,
        "confidence": 0.0,
    }

    net_qty_patterns = [
        # Pattern 1: NET QTY / शुद्ध मात्रा: 500 g / 500 ग्राम / 1 kg / 750 ml / 1 L / 10 N
        re.compile(
            r"(?:NET\s*(?:QTY|QUANTITY|WT|WEIGHT|VOL|VOLUME|CONTENT|CONTENTS)?|शुद्ध\s*मात्रा|मात्रा|कुल\s*मात्रा)\s*[:\-\.]?\s*([0-9]+(?:\.[0-9]+)?)\s*([a-zA-Z\.\/\^0-9\u0900-\u097F]+)",
            re.IGNORECASE,
        ),
        # Pattern 2: 500 g / 1.5 kg / 250 ml / 500gm / 500 ग्राम
        re.compile(
            r"\b([0-9]+(?:\.[0-9]+)?)\s*(kg|kgs|kilogram|kilograms|g|gm|gms|gram|grams|mg|mgs|ml|mls|l|ltr|ltrs|litre|litres|m|cm|mm|sq\.?m|pcs|piece|pieces|units|tablets|capsules|wipes|sheets|N|u|ग्राम|ग्रा|कि\.ग्रा\.|किग्रा|किलोग्राम|मिली|मिलीलीटर|लीटर|ली|संख्या|नग)\b",
            re.IGNORECASE,
        ),
        # Pattern 3: QUANTITY: 5 N / 100 U / संख्या: 10
        re.compile(
            r"(?:QUANTITY|QTY|COUNT|संख्या|इकाई)\s*[:\-\.]?\s*([0-9]+(?:\.[0-9]+)?)\s*([a-zA-Z\.\u0900-\u097F]+)?",
            re.IGNORECASE,
        ),
    ]

    for pat in net_qty_patterns:
        match = pat.search(text)
        if match:
            val_str = match.group(1)
            raw_unit = match.group(2).strip().lower() if len(match.groups()) > 1 and match.group(2) else "n"
            # Strip trailing dots or commas
            raw_unit = raw_unit.rstrip(".,")
            try:
                val = float(val_str)
                norm_unit = UNIT_NORMALIZATION_MAP.get(raw_unit, raw_unit)
                result["value"] = val
                result["unit"] = norm_unit
                result["raw"] = match.group(0).strip()
                result["is_standard_unit"] = norm_unit in STANDARD_UNITS
                result["confidence"] = 0.95 if result["is_standard_unit"] else 0.75
                break
            except ValueError:
                continue

    return result


# ---------------------------------------------------------------------------
# 3. Unit Sale Price (USP) Parser — Rule 6(1)(k)
# ---------------------------------------------------------------------------
def parse_unit_sale_price(text: str) -> Dict[str, Any]:
    """
    Extracts Unit Sale Price declarations (e.g. ₹ 0.50 / g, Rs. 1.20 per ml).
    """
    result: Dict[str, Any] = {
        "raw": None,
        "value": None,
        "unit": None,
        "confidence": 0.0,
    }

    usp_patterns = [
        # Pattern 1: USP: Rs. 0.50 / g  or  UNIT SALE PRICE: ₹ 1.20 per ml
        re.compile(
            r"(?:USP|UNIT\s*SALE\s*PRICE|UNIT\s*PRICE)\s*[:\-\.]?\s*(?:Rs\.?|INR|₹)?\s*([0-9]+(?:\.[0-9]{1,4})?)\s*(?:per|\/)\s*([a-zA-Z\.\^0-9]+)",
            re.IGNORECASE,
        ),
        # Pattern 2: ₹ 0.50 / g  or  Rs 12.00 / kg
        re.compile(
            r"(?:Rs\.?|INR|₹)\s*([0-9]+(?:\.[0-9]{1,4})?)\s*(?:per|\/)\s*(g|kg|ml|l|m|cm|N|u|piece|unit)\b",
            re.IGNORECASE,
        ),
    ]

    for pat in usp_patterns:
        match = pat.search(text)
        if match:
            val_str = match.group(1)
            raw_unit = match.group(2).strip().lower()
            try:
                val = float(val_str)
                norm_unit = UNIT_NORMALIZATION_MAP.get(raw_unit, raw_unit)
                result["value"] = val
                result["unit"] = norm_unit
                result["raw"] = match.group(0).strip()
                result["confidence"] = 0.90
                break
            except ValueError:
                continue

    return result


# ---------------------------------------------------------------------------
# 4. Dates Parser (Mfg Date & Expiry / Best Before) — Rule 6(1)(d) & 6(1)(h)
# ---------------------------------------------------------------------------
def _parse_date_string(date_str: str) -> Optional[date]:
    """Helper to convert diverse Indian packaging date strings to datetime.date."""
    clean = re.sub(r"[^\w\/\-\.]", " ", date_str).strip()
    parts = re.split(r"[\s\/\-\.]+", clean)

    if len(parts) == 2:
        # Format: MM/YYYY or MM/YY or MMM YYYY (e.g. 05/2026 or JAN 2026)
        p1, p2 = parts[0].lower(), parts[1]
        month = None
        if p1 in MONTH_MAP:
            month = MONTH_MAP[p1]
        elif p1.isdigit():
            month = int(p1)

        year = int(p2) if p2.isdigit() else None
        if year and year < 100:
            year += 2000  # Convert 26 -> 2026

        if month and year and 1 <= month <= 12 and 2000 <= year <= 2099:
            return date(year, month, 1)

    elif len(parts) == 3:
        # Format: DD/MM/YYYY or DD MMM YYYY or YYYY/MM/DD
        p1, p2, p3 = parts[0].lower(), parts[1].lower(), parts[2]
        # Check DD MMM YYYY (e.g. 15 JAN 2026)
        if p1.isdigit() and p2 in MONTH_MAP and p3.isdigit():
            day = int(p1)
            month = MONTH_MAP[p2]
            year = int(p3)
            if year < 100:
                year += 2000
            try:
                return date(year, month, day)
            except ValueError:
                pass
        # Check DD/MM/YYYY
        if p1.isdigit() and p2.isdigit() and p3.isdigit():
            day = int(p1)
            month = int(p2)
            year = int(p3)
            if year < 100:
                year += 2000
            try:
                return date(year, month, day)
            except ValueError:
                pass

    return None


def parse_dates(text: str) -> Dict[str, Any]:
    """
    Extracts Manufacturing/Packing Date and Expiry/Best Before Date.
    """
    result: Dict[str, Any] = {
        "mfg_date_raw": None,
        "mfg_date": None,
        "exp_date_raw": None,
        "exp_date": None,
        "confidence": 0.0,
    }

    # ── Manufacturing / Packing Date ──────────────────────────────────────
    mfg_pattern = re.compile(
        r"(?:(?:MFD\s*DATE|MFG\s*DATE|PKD\s*DATE|MFD|MFG|PACKED|PKD|DATE\s*OF\s*MFG|DATE\s*OF\s*PACKING|MANUFACTURED|MANUFACTURE|निर्माण\s*तिथि|पैकिंग\s*तिथि|नि\.?\s*ति\.?)\s*[:\-\.]?\s*)([0-9]{1,2}[\/\-\.][0-9]{2,4}|[a-zA-Z\u0900-\u097F]{3,9}[\s\-\.\/]+[0-9]{2,4}|[0-9]{1,2}[\s\-\.\/]+[a-zA-Z\u0900-\u097F]{3,9}[\s\-\.\/]+[0-9]{2,4})",
        re.IGNORECASE,
    )
    mfg_match = mfg_pattern.search(text)
    if mfg_match:
        raw_mfg = mfg_match.group(1).strip()
        result["mfg_date_raw"] = mfg_match.group(0).strip()
        result["mfg_date"] = _parse_date_string(raw_mfg)

    # ── Expiry Date ───────────────────────────────────────────────────────
    exp_pattern = re.compile(
        r"(?:(?:EXP|EXPIRY|EXP\s*DATE|USE\s*BY|USE\s*BEFORE|EXPIRY\s*DATE|उपयोग\s*की\s*अंतिम\s*तिथि|अंतिम\s*तिथि|समाप्ति\s*तिथि)\s*[:\-\.]?\s*)([0-9]{1,2}[\/\-\.][0-9]{2,4}|[a-zA-Z\u0900-\u097F]{3,9}[\s\-\.\/]+[0-9]{2,4}|[0-9]{1,2}[\s\-\.\/]+[a-zA-Z\u0900-\u097F]{3,9}[\s\-\.\/]+[0-9]{2,4})",
        re.IGNORECASE,
    )
    exp_match = exp_pattern.search(text)
    if exp_match:
        raw_exp = exp_match.group(1).strip()
        result["exp_date_raw"] = exp_match.group(0).strip()
        result["exp_date"] = _parse_date_string(raw_exp)

    # ── Best Before Relative Duration (e.g. Best Before 12 Months from Mfg) ──
    best_before_pattern = re.compile(
        r"(?:BEST\s*BEFORE|सर्वोत्तम\s*उपयोग)\s*([0-9]+)\s*(MONTHS|DAYS|YEARS|माह|महीने|दिन|वर्ष)\s*(?:FROM\s*(?:MFG|PKD|PACKAGING|MANUFACTURE|DATE\s*OF\s*MFG))?",
        re.IGNORECASE,
    )
    bb_match = best_before_pattern.search(text)
    if bb_match and not result["exp_date"]:
        num = int(bb_match.group(1))
        unit = bb_match.group(2).lower()
        result["exp_date_raw"] = bb_match.group(0).strip()

        if result["mfg_date"]:
            base: date = result["mfg_date"]
            if "month" in unit or "माह" in unit or "महीने" in unit:
                total_months = base.month + num
                new_year = base.year + (total_months - 1) // 12
                new_month = (total_months - 1) % 12 + 1
                max_day = calendar.monthrange(new_year, new_month)[1]
                result["exp_date"] = date(new_year, new_month, min(base.day, max_day))
            elif "day" in unit or "दिन" in unit:
                result["exp_date"] = base + timedelta(days=num)
            elif "year" in unit or "वर्ष" in unit:
                new_year = base.year + num
                max_day = calendar.monthrange(new_year, base.month)[1]
                result["exp_date"] = date(new_year, base.month, min(base.day, max_day))

    # Compute confidence
    conf = 0.0
    if result["mfg_date"]:
        conf += 0.50
    if result["exp_date"]:
        conf += 0.50
    elif result["exp_date_raw"]:
        conf += 0.30

    result["confidence"] = min(1.0, conf)
    return result


# ---------------------------------------------------------------------------
# 5. Batch / Lot Number Parser
# ---------------------------------------------------------------------------
def parse_batch_number(text: str) -> Dict[str, Any]:
    """Extracts batch or lot identification code."""
    result: Dict[str, Any] = {
        "raw": None,
        "batch_number": None,
        "confidence": 0.0,
    }

    batch_patterns = [
        re.compile(
            r"(?:BATCH\s*(?:NO|NUMBER)?|LOT\s*(?:NO|NUMBER)?|B\.?\s*NO\.?|L\.?\s*NO\.?|BN|बैच\s*संख्या|बैच\s*क्र\.?)\s*[:\-\.]?\s*([A-Za-z0-9\-\/]+)",
            re.IGNORECASE,
        ),
    ]

    for pat in batch_patterns:
        match = pat.search(text)
        if match:
            code = match.group(1).strip()
            # Must contain at least one digit or uppercase letter and length >= 2
            if len(code) >= 2 and any(c.isalnum() for c in code):
                result["batch_number"] = code
                result["raw"] = match.group(0).strip()
                result["confidence"] = 0.90
                break

    return result


# ---------------------------------------------------------------------------
# 6. Manufacturer / Packer / Importer Parser — Rule 6(1)(a)
# ---------------------------------------------------------------------------
def parse_mfg_packer_importer(text: str) -> Dict[str, Any]:
    """
    Extracts manufacturer, packer, or importer name and address details (English and Hindi).
    """
    result: Dict[str, Any] = {
        "manufacturer_name": None,
        "manufacturer_address": None,
        "packer_name": None,
        "packer_address": None,
        "importer_name": None,
        "importer_address": None,
        "confidence": 0.0,
    }

    lines = [l.strip() for l in text.split("\n") if l.strip()]

    # Keywords to detect entity role (English and Hindi)
    mfg_kw = re.compile(r"^(?:MANUFACTURED|MFD|MFG|PRODUCED|MFR|निर्माता|उत्पादक)\s*(?:BY|द्वारा)?\s*[:\-\.]?\s*(.*)", re.IGNORECASE)
    pkd_kw = re.compile(r"^(?:PACKED|PKD|पैकर|पैकिंग)\s*(?:BY|द्वारा)?\s*[:\-\.]?\s*(.*)", re.IGNORECASE)
    imp_kw = re.compile(r"^(?:IMPORTED|आयातकर्ता)\s*(?:BY|द्वारा)?\s*[:\-\.]?\s*(.*)", re.IGNORECASE)
    mkt_kw = re.compile(r"^(?:MARKETED|विपणक)\s*(?:BY|द्वारा)?\s*[:\-\.]?\s*(.*)", re.IGNORECASE)

    pin_pattern = re.compile(r"\b([1-9][0-9]{5})\b")

    for i, line in enumerate(lines):
        # ── Check Manufacturer ────────────────────────────────────────────
        mfg_m = mfg_kw.match(line)
        if mfg_m and not result["manufacturer_name"]:
            name = mfg_m.group(1).strip()
            addr_lines = []
            if not name and i + 1 < len(lines):
                name = lines[i + 1]
                addr_lines = lines[i + 2 : min(i + 6, len(lines))]
            else:
                addr_lines = lines[i + 1 : min(i + 5, len(lines))]

            result["manufacturer_name"] = name or "Declared Manufacturer"
            result["manufacturer_address"] = ", ".join(addr_lines) if addr_lines else None
            result["confidence"] = max(result["confidence"], 0.85)

        # ── Check Packer ──────────────────────────────────────────────────
        pkd_m = pkd_kw.match(line)
        if pkd_m and not result["packer_name"]:
            name = pkd_m.group(1).strip()
            addr_lines = []
            if not name and i + 1 < len(lines):
                name = lines[i + 1]
                addr_lines = lines[i + 2 : min(i + 6, len(lines))]
            else:
                addr_lines = lines[i + 1 : min(i + 5, len(lines))]

            result["packer_name"] = name or "Declared Packer"
            result["packer_address"] = ", ".join(addr_lines) if addr_lines else None
            result["confidence"] = max(result["confidence"], 0.85)

        # ── Check Importer ────────────────────────────────────────────────
        imp_m = imp_kw.match(line)
        if imp_m and not result["importer_name"]:
            name = imp_m.group(1).strip()
            addr_lines = []
            if not name and i + 1 < len(lines):
                name = lines[i + 1]
                addr_lines = lines[i + 2 : min(i + 6, len(lines))]
            else:
                addr_lines = lines[i + 1 : min(i + 5, len(lines))]

            result["importer_name"] = name or "Declared Importer"
            result["importer_address"] = ", ".join(addr_lines) if addr_lines else None
            result["confidence"] = max(result["confidence"], 0.85)

    return result


# ---------------------------------------------------------------------------
# 7. Country of Origin Parser — Rule 6(1)(g)
# ---------------------------------------------------------------------------
def parse_country_of_origin(text: str) -> Dict[str, Any]:
    """Extracts country of origin declaration."""
    result: Dict[str, Any] = {
        "raw": None,
        "country": None,
        "confidence": 0.0,
    }

    origin_patterns = [
        re.compile(
            r"(?:COUNTRY\s*OF\s*ORIGIN|MADE\s*IN|PRODUCT\s*OF|ORIGIN)\s*[:\-\.]?\s*([A-Za-z\s]+)",
            re.IGNORECASE,
        ),
    ]

    for pat in origin_patterns:
        match = pat.search(text)
        if match:
            candidate = match.group(1).strip().split("\n")[0]
            # Take first 1-3 words of country
            country_clean = " ".join(candidate.split()[:3]).upper().strip(".,-")
            if country_clean and len(country_clean) >= 2:
                result["country"] = country_clean
                result["raw"] = match.group(0).strip()
                result["confidence"] = 0.90
                break

    return result


# ---------------------------------------------------------------------------
# 8. Consumer Care Details Parser — Rule 6(1)(f)
# ---------------------------------------------------------------------------
def parse_consumer_care(text: str) -> Dict[str, Any]:
    """
    Extracts consumer care toll-free/mobile phone, email, and postal redressal address.
    """
    result: Dict[str, Any] = {
        "email": None,
        "phone": None,
        "address": None,
        "confidence": 0.0,
    }

    # ── Email Extraction ──────────────────────────────────────────────────
    email_pattern = re.compile(
        r"\b([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)\b"
    )
    email_matches = email_pattern.findall(text)
    if email_matches:
        # Prefer emails containing 'care', 'customercare', 'feedback', 'support'
        care_email = next((e for e in email_matches if any(k in e.lower() for k in ["care", "customercare", "support", "feedback"])), email_matches[0])
        result["email"] = care_email.lower().rstrip(".")

    # ── Phone Extraction (1800/1860 toll free or +91 standard Indian numbers) ─
    phone_patterns = [
        re.compile(r"\b(1800[-\s]?[0-9]{3}[-\s]?[0-9]{3,4})\b"),
        re.compile(r"\b(1860[-\s]?[0-9]{3}[-\s]?[0-9]{3,4})\b"),
        re.compile(r"(?:\+91[-\s]?)?([6-9][0-9]{4}[-\s]?[0-9]{5})\b"),
        re.compile(r"\b(0[0-9]{2,4}[-\s]?[0-9]{6,8})\b"),
    ]

    for pat in phone_patterns:
        pm = pat.search(text)
        if pm:
            result["phone"] = pm.group(1).strip()
            break

    # ── Address / Contact Person ──────────────────────────────────────────
    care_addr_pattern = re.compile(
        r"(?:CONSUMER\s*CARE|CUSTOMER\s*CARE|FOR\s*COMPLAINTS|CONSUMER\s*CELL)[^\n]*\n([^\n]+(?:\n[^\n]+)?)",
        re.IGNORECASE,
    )
    cam = care_addr_pattern.search(text)
    if cam:
        result["address"] = cam.group(1).strip().replace("\n", ", ")

    # Compute confidence
    score = 0.0
    if result["email"]:
        score += 0.45
    if result["phone"]:
        score += 0.45
    if result["address"]:
        score += 0.20

    result["confidence"] = min(1.0, score)
    return result


# ---------------------------------------------------------------------------
# 9. Commodity & Generic Name Parser — Rule 6(1)(b)
# ---------------------------------------------------------------------------
def parse_commodity_name(text: str) -> Dict[str, Any]:
    """Extracts the generic name or commodity description of the product."""
    result: Dict[str, Any] = {
        "generic_name": None,
        "brand_name": None,
        "confidence": 0.0,
    }

    comm_patterns = [
        re.compile(
            r"(?:COMMODITY|GENERIC\s*NAME|PRODUCT\s*NAME|NAME\s*OF\s*COMMODITY)\s*[:\-\.]?\s*([A-Za-z0-9\s,\-\(\)]+)",
            re.IGNORECASE,
        ),
    ]

    for pat in comm_patterns:
        match = pat.search(text)
        if match:
            val = match.group(1).strip().split("\n")[0]
            if val and len(val) >= 2:
                result["generic_name"] = val
                result["confidence"] = 0.85
                break

    return result
