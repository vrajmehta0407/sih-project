"""
regulatory_copilot_service.py
=============================
Stage 25 — National Legal Metrology AI Regulatory Copilot Service
"""

import re
import logging
from datetime import datetime
from typing import List, Dict, Any

from app.schemas.copilot import (
    CopilotQueryRequest,
    CopilotQueryResponse,
    StatutoryCitation,
)
from app.core.config import settings

logger = logging.getLogger(__name__)


class RegulatoryCopilotService:
    """Semantic Statutory Knowledge Graph & Legal Retrieval Copilot for Legal Metrology."""

    async def async_query(self, req: CopilotQueryRequest) -> CopilotQueryResponse:
        """Process query with optional live Gemini LLM enrichment if GEMINI_API_KEY is configured."""
        base_resp = self.query(req)
        
        # If Gemini AI is configured, generate advanced LLM response
        if settings.GEMINI_API_KEY:
            try:
                from app.services.public_api_service import public_api_service
                gemini_res = await public_api_service.query_gemini_llm(
                    prompt=f"Question: {req.query}\nContext Base Opinion: {base_resp.legal_opinion}\nDetected Intent: {base_resp.detected_intent}",
                    system_instruction=(
                        "You are an expert Legal Metrology AI Statutory Copilot for the Ministry of Consumer Affairs, "
                        "Government of India. Provide authoritative legal analysis referencing the Legal Metrology Act 2009 "
                        "(Sections 18, 25, 36, 48, 49) and Legal Metrology (Packaged Commodities) Rules 2011 (Rule 6, 9, 11, Schedule I/II)."
                    )
                )
                if gemini_res.get("success") and gemini_res.get("response_text"):
                    base_resp.legal_opinion = f"{gemini_res.get('response_text').strip()}\n\n[Authoritative Knowledge Graph Grounding]:\n{base_resp.legal_opinion}"
            except Exception as e:
                logger.warning("Gemini AI enrichment failed, falling back to statutory base: %s", e)

        return base_resp

    def query(self, req: CopilotQueryRequest) -> CopilotQueryResponse:
        """Process legal question and return authoritative statutory analysis with citations."""
        now = datetime.utcnow()
        q = req.query.lower()

        # Topic 1: Unit Sale Price (USP) & Exemptions
        if any(k in q for k in ["unit sale price", "usp", "10 gram", "10 ml", "10g", "10ml", "exemption", "small package"]):
            intent = "USP_EXEMPTION_RULES"
            opinion = (
                "Under Rule 6(11) of the Legal Metrology (Packaged Commodities) Rules, 2011 (amended 2021/2022), "
                "declaration of Unit Sale Price (USP) is NOT mandatory for:\n"
                "1. Pre-packaged commodities having a net quantity of 10 grams or less, or 10 milliliters or less.\n"
                "2. Pre-packaged commodities sold by number containing only one item.\n"
                "For all other packages, Unit Sale Price must be declared in rupees per gram/milliliter (if net quantity < 1kg/1L) "
                "or rupees per kilogram/liter (if net quantity >= 1kg/1L)."
            )
            citations = [
                StatutoryCitation(
                    act_or_rule="LM (Packaged Commodities) Rules, 2011",
                    section_or_rule_no="Rule 6(11)",
                    title="Exemption from Unit Sale Price Declaration",
                    statutory_text_excerpt="Declaration of Unit Sale Price is not mandatory for packages having net quantity equal to or less than 10g or 10ml, or where package contains one item sold by number.",
                ),
                StatutoryCitation(
                    act_or_rule="LM (Packaged Commodities) Rules, 2011",
                    section_or_rule_no="Rule 6(1)(e)",
                    title="Mandatory Declarations on Pre-Packaged Commodities",
                    statutory_text_excerpt="Every package shall bear the unit sale price rounded off to the nearest two decimal places.",
                ),
            ]
            penalty = "Non-declaration on non-exempt packages attracts Section 36(1) penalty up to ₹25,000 for first offence."
            actions = [
                "Verify certified net quantity of the subject package via weighment.",
                "If net quantity > 10g or > 10ml, inspect principal display panel for USP.",
                "If absent, issue Form-1 Notice under Rule 6(1)(e) read with Section 36(1).",
            ]
            compoundable = True

        # Topic 2: E-Commerce Marketplace Mandates
        elif any(k in q for k in ["e-commerce", "ecommerce", "online", "marketplace", "amazon", "flipkart", "blinkit", "zepto", "swiggy"]):
            intent = "ECOMMERCE_RULE_6_10"
            opinion = (
                "Under Rule 6(10) of the Legal Metrology (Packaged Commodities) Rules, 2011:\n"
                "An e-commerce entity shall ensure that the mandatory declarations under Rule 6 (Name & Address of Manufacturer/Packer, "
                "Name of Country of Origin, Common Name of Commodity, Net Quantity, Best Before Date, MRP, and Consumer Care Details) "
                "are displayed on the digital marketplace listing.\n"
                "Note: The manufacturer, packer, or importer remains solely responsible for the correctness of declarations, "
                "while the marketplace entity is responsible for displaying the digital declarations provided by the seller."
            )
            citations = [
                StatutoryCitation(
                    act_or_rule="LM (Packaged Commodities) Rules, 2011",
                    section_or_rule_no="Rule 6(10)",
                    title="E-Commerce Digital Marketplace Declarations",
                    statutory_text_excerpt="An e-commerce entity shall ensure that the mandatory declarations required on the package under these rules are displayed on the digital and electronic network used for e-commerce transactions.",
                ),
                StatutoryCitation(
                    act_or_rule="Legal Metrology Act, 2009",
                    section_or_rule_no="Section 36(1)",
                    title="Penalty for Non-Standard Pre-Packaged Goods",
                    statutory_text_excerpt="Whoever manufactures, packs, imports, sells, distributes, or delivers any pre-packaged commodity which does not conform to the declarations on the package shall be punished with fine up to twenty-five thousand rupees.",
                ),
            ]
            penalty = "Violation of Rule 6(10) attracts penalty under Section 36(1) (up to ₹25,000 on first offence; up to ₹50,000 on second)."
            actions = [
                "Audit e-commerce digital product listing web page and capture timestamped screenshot.",
                "Cross-check physical delivered item with digital listing declarations.",
                "Issue Show-Cause Notice to both the third-party seller and the e-commerce marketplace platform.",
            ]
            compoundable = True

        # Topic 3: Font Size & Principal Display Panel (PDP)
        elif any(k in q for k in ["font", "height", "pdp", "principal display", "letter size", "numeral height", "schedule"]):
            intent = "FONT_HEIGHT_SCHEDULE"
            opinion = (
                "Under Rule 7 and the First Schedule of the Legal Metrology (Packaged Commodities) Rules, 2011, "
                "the minimum height of numerals and letters for net quantity and MRP declarations is strictly governed by the area of the Principal Display Panel (PDP):\n"
                "• Net Qty <= 50g / 50ml: Minimum font height is 1.0 mm (embossed: 2.0 mm).\n"
                "• Net Qty 50g - 200g / 50ml - 200ml: Minimum font height is 2.0 mm (embossed: 4.0 mm).\n"
                "• Net Qty 200g - 1kg / 200ml - 1L: Minimum font height is 4.0 mm (embossed: 6.0 mm).\n"
                "• Net Qty > 1kg / > 1L: Minimum font height is 6.0 mm (embossed: 8.0 mm)."
            )
            citations = [
                StatutoryCitation(
                    act_or_rule="LM (Packaged Commodities) Rules, 2011",
                    section_or_rule_no="Rule 7 & First Schedule",
                    title="Minimum Font Height Specifications for Numerals & Letters",
                    statutory_text_excerpt="The height of any numeral and letter in the declaration shall not be less than the minimum prescribed in the Table of the First Schedule.",
                ),
            ]
            penalty = "Defective or sub-standard font sizes violate Rule 7, punishable under Section 36(1) (fine up to ₹25,000)."
            actions = [
                "Measure physical principal display panel surface area with calibrated gauge.",
                "Verify printed character height using digital optical micrometer or OCR bounding box scale.",
                "If font height is below statutory minimum, register Rule 7 infraction.",
            ]
            compoundable = True

        # Topic 4: Overcharging & Dual MRP
        elif any(k in q for k in ["overcharg", "dual mrp", "sticker", "higher price", "above mrp", "section 18", "section 36"]):
            intent = "OVERCHARGING_AND_DUAL_MRP"
            opinion = (
                "Under Section 18 of the Legal Metrology Act, 2009 read with Rule 6(1)(e):\n"
                "No person shall alter, obliterate, or cover the Maximum Retail Price (MRP) printed on a package with any sticker or label. "
                "No pre-packaged commodity shall be sold, distributed, or delivered at a price higher than the printed MRP.\n"
                "Dual MRP for identical commodities across different retail channels (e.g. cinema halls, airports, restaurants) "
                "is strictly prohibited pursuant to Union of India vs. Federation of Hotels & Restaurants Association precedents."
            )
            citations = [
                StatutoryCitation(
                    act_or_rule="Legal Metrology Act, 2009",
                    section_or_rule_no="Section 18(1)",
                    title="Prohibition of Sale of Non-Standard or Overpriced Packages",
                    statutory_text_excerpt="No person shall manufacture, pack, sell, distribute, deliver, or cause to be sold or delivered any pre-packaged commodity unless such package conforms to such standard quantities or number as may be prescribed.",
                ),
                StatutoryCitation(
                    act_or_rule="Legal Metrology Act, 2009",
                    section_or_rule_no="Section 36(2)",
                    title="Penalty for Second or Subsequent Offences",
                    statutory_text_excerpt="Whoever commits a second or subsequent offence under sub-section (1) shall be punished with fine which may extend to fifty thousand rupees or with imprisonment for a term which may extend to one year, or with both.",
                ),
            ]
            penalty = "First offence: Fine up to ₹25,000. Second offence under Section 36(2): Fine up to ₹50,000 and/or imprisonment up to 1 year."
            actions = [
                "Conduct test purchase and preserve authentic cash receipt showing charged sum.",
                "Perform Error Level Analysis (ELA) on price label to verify sticker tampering.",
                "Check national database for prior convictions under Section 36(2) recidivism escalator.",
            ]
            compoundable = True

        # General Catch-All Statutory Response
        else:
            intent = "GENERAL_STATUTORY_GUIDANCE"
            opinion = (
                f"Under the Legal Metrology Act, 2009 and the Legal Metrology (Packaged Commodities) Rules, 2011, "
                f"all pre-packaged goods sold in India must carry 7 mandatory declarations on the Principal Display Panel: "
                f"1. Name and complete address of Manufacturer / Packer / Importer.\n"
                f"2. Generic / common name of the commodity.\n"
                f"3. Net quantity in standard SI units (g, kg, ml, L, or count).\n"
                f"4. Month and Year of Manufacture / Packing / Import.\n"
                f"5. Unit Sale Price (USP) in Rs. per g/ml or kg/L (unless exempt under Rule 6(11)).\n"
                f"6. Maximum Retail Price (MRP) inclusive of all taxes.\n"
                f"7. Consumer grievance redressal details (Name, Address, Tel No, Email of nodal person)."
            )
            citations = [
                StatutoryCitation(
                    act_or_rule="Legal Metrology Act, 2009",
                    section_or_rule_no="Section 18 & Section 36",
                    title="Statutory Standards for Pre-Packaged Goods",
                    statutory_text_excerpt="All pre-packaged commodities must strictly conform to the declarations prescribed under the Packaged Commodities Rules, 2011.",
                ),
            ]
            penalty = "General packaging non-compliance is penalized under Section 36(1) with compounding available under Section 48."
            actions = [
                "Execute full 7-declaration physical label audit.",
                "Cross-reference manufacturer registration on the National Product Registry.",
            ]
            compoundable = True

        logger.info("Copilot query '%s' processed as intent %s", req.query, intent)

        return CopilotQueryResponse(
            query=req.query,
            legal_opinion=opinion,
            detected_intent=intent,
            citations=citations,
            penalty_implications=penalty,
            recommended_officer_actions=actions,
            is_compoundable=compoundable,
            created_at=now,
        )


regulatory_copilot_service = RegulatoryCopilotService()
