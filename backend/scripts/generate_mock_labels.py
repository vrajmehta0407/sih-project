import os
from PIL import Image, ImageDraw, ImageFont

def create_synthetic_label(
    filename: str,
    title: str,
    lines: list,
    output_dir: str = "sample_data/labels",
    border_color: tuple = (40, 50, 70),
    bg_color: tuple = (255, 255, 255),
    width: int = 800,
    height: int = 600
) -> str:
    """Generates a realistic packaging label image with statutory declarations."""
    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, filename)

    img = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(img)

    # Outer packaging border
    draw.rectangle([(20, 20), (width - 20, height - 20)], outline=border_color, width=4)
    # Inner header banner
    draw.rectangle([(20, 20), (width - 20, 80)], fill=(15, 30, 60))

    # Header text
    try:
        font_title = ImageFont.truetype("arial.ttf", 26)
        font_body = ImageFont.truetype("arial.ttf", 18)
        font_bold = ImageFont.truetype("arialbd.ttf", 20)
        font_meta = ImageFont.truetype("cour.ttf", 15)
    except Exception:
        font_title = ImageFont.load_default()
        font_body = ImageFont.load_default()
        font_bold = ImageFont.load_default()
        font_meta = ImageFont.load_default()

    draw.text((40, 35), title, fill=(255, 215, 0), font=font_title)

    # Decorative sub-header
    draw.line([(20, 80), (width - 20, 80)], fill=(200, 160, 40), width=3)

    # Body lines
    y = 105
    for line in lines:
        if line.startswith("---"):
            draw.line([(30, y + 5), (width - 30, y + 5)], fill=(200, 200, 200), width=1)
            y += 18
        elif line.startswith("[BOLD]"):
            draw.text((40, y), line.replace("[BOLD]", "").strip(), fill=(20, 20, 20), font=font_bold)
            y += 32
        elif line.startswith("[META]"):
            draw.text((40, y), line.replace("[META]", "").strip(), fill=(80, 80, 80), font=font_meta)
            y += 24
        else:
            draw.text((40, y), line, fill=(30, 30, 30), font=font_body)
            y += 28

    # Bottom statutory banner
    draw.rectangle([(20, height - 50), (width - 20, height - 20)], fill=(240, 244, 248))
    draw.text((40, height - 42), "LEGAL METROLOGY (PACKAGED COMMODITIES) RULES 2011 STATUTORY PANEL", fill=(60, 80, 100), font=font_meta)

    img.save(out_path, "PNG", quality=95)
    print(f"Generated sample label: {out_path}")
    return out_path


def generate_all_samples():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    target_dir = os.path.join(base_dir, "sample_data", "labels")

    # 1. Fully Compliant Gram Flour
    create_synthetic_label(
        filename="01_compliant_gram_flour.png",
        title="SHUDDH BESAN (GRAM FLOUR) 500g",
        lines=[
            "[BOLD] PRODUCT: 100% PURE CHANA DAL FLOUR",
            "---",
            "MRP: Rs. 65.00 (inclusive of all taxes)",
            "NET WEIGHT: 500 g",
            "UNIT SALE PRICE: Rs. 0.13 / g",
            "DATE OF PACKING: 02/2026",
            "BEST BEFORE: 12/2026",
            "BATCH NO: SB-2026-08",
            "---",
            "MANUFACTURED & PACKED BY:",
            "Shuddh Foods Agrotech Pvt Ltd, Plot 14, MIDC Phase 2,",
            "Pune, Maharashtra 411019, India",
            "COUNTRY OF ORIGIN: INDIA",
            "---",
            "[META] CONSUMER CARE: Toll Free 1800-222-3344 | care@shuddhfoods.in",
        ],
        output_dir=target_dir,
    )

    # 2. Rule 6(1)(e) Violation — Missing "inclusive of all taxes"
    create_synthetic_label(
        filename="02_violation_mrp_no_tax.png",
        title="PRIME SUNFLOWER OIL 1 L",
        lines=[
            "[BOLD] PRODUCT: REFINED SUNFLOWER SEED OIL",
            "---",
            "MRP: Rs. 140.00",  # VIOLATION: Missing (incl. of all taxes)
            "NET QUANTITY: 1 L",
            "DATE OF PACKING: 01/2026",
            "BEST BEFORE: 01/2027",
            "BATCH NO: PSO-9921",
            "---",
            "MANUFACTURED BY: Prime Edible Oils Ltd,",
            "GIDC Estate, Surat, Gujarat 395003",
            "COUNTRY OF ORIGIN: INDIA",
            "---",
            "[META] CONSUMER CARE: 1800-111-9988 | support@primeoils.in",
        ],
        output_dir=target_dir,
    )

    # 3. Rule 6(1)(c) & Rule 11 Violation — Non-standard unit ("500 gm")
    create_synthetic_label(
        filename="03_violation_nonstandard_unit.png",
        title="CRISPY ROASTED CASHEWS",
        lines=[
            "[BOLD] PRODUCT: PREMIUM JUMBO CASHEW NUTS",
            "---",
            "MRP: Rs. 450.00 (incl. of all taxes)",
            "NET WEIGHT: 500 gm",  # VIOLATION: "gm" instead of standard "g"
            "MFD DATE: 02/2026",
            "USE BY: 11/2026",
            "BATCH NO: RC-4402",
            "---",
            "PACKED BY: Royal Crunch Nutworks,",
            "Industrial Area, Panaji, Goa 403001",
            "---",
            "[META] CONSUMER CARE: 1800-444-5566 | help@royalcrunch.in",
        ],
        output_dir=target_dir,
    )

    # 4. Rule 6(1)(a) Violation — Missing Manufacturer Address
    create_synthetic_label(
        filename="04_violation_missing_mfg.png",
        title="HERBAL ALOE VERA GEL",
        lines=[
            "[BOLD] PRODUCT: NATURAL SKIN MOISTURIZING GEL",
            "---",
            "MRP: Rs. 99.00 (incl. of all taxes)",
            "NET VOLUME: 200 ml",
            "MFG DATE: 01/2026",
            "EXPIRY DATE: 01/2028",
            "BATCH NO: AVG-102",
            "---",
            # VIOLATION: Missing Manufacturer postal address and PIN code
            "MARKETED BY: Pure Nature Cosmetics Corp",
            "---",
            "[META] CONSUMER CARE: care@purenature.com",
        ],
        output_dir=target_dir,
    )

    # 5. Rule 6(1)(h) Violation — Expired Commodity on Shelf
    create_synthetic_label(
        filename="05_violation_expired_commodity.png",
        title="DAIRY FRESH PASTEURIZED MILK",
        lines=[
            "[BOLD] PRODUCT: STANDARDIZED TONED MILK",
            "---",
            "MRP: Rs. 32.00 (incl. of all taxes)",
            "NET QUANTITY: 500 ml",
            "PKD DATE: 01/2026",
            "USE BY DATE: 03/2026",  # VIOLATION: Expired commodity
            "BATCH NO: DFM-03",
            "---",
            "MFD BY: Dairy Fresh Milk Union, Anand, Gujarat 388001",
            "---",
            "[META] CONSUMER CARE: 1800-333-2211 | dairy@freshmilk.org",
        ],
        output_dir=target_dir,
    )

    # 6. Section 36(2) Repeat Offender Entity
    create_synthetic_label(
        filename="06_repeat_offender_edible_oil.png",
        title="GOLDEN DROP PALM OIL 1 L",
        lines=[
            "[BOLD] PRODUCT: IMPORTED REFINED PALM OIL",
            "---",
            "MRP: Rs. 110.00",  # Violation
            "NET CONTENT: 1000 cc",  # Non-standard unit
            "DATE OF PACKING: 02/2026",
            "BATCH: GD-2026",
            "---",
            "PACKED BY: Golden Drop Agro Ltd",  # Known recidivist entity
            "---",
            "[META] CONSUMER CARE: Not Provided",  # Missing consumer care
        ],
        output_dir=target_dir,
    )

    print("\nAll 6 synthetic mock commodity labels generated in:", target_dir)


if __name__ == "__main__":
    generate_all_samples()
