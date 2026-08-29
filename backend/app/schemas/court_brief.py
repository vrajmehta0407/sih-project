"""
schemas/court_brief.py
======================
Stage 28 — Automated Pre-Trial Court Evidence Brief & Section 65B Certificate Schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class AccusedEntityDetails(BaseModel):
    """Details of accused enterprise and officers under Section 49."""
    company_name: str = Field(..., example="FastRetail Supermarkets Pvt. Ltd.")
    registered_address: str = Field(..., example="Plot 42, Bandra Kurla Complex, Mumbai 400051")
    managing_director_name: str = Field(..., example="Vikramaditya Singhania")
    nominated_director_section_49: Optional[str] = Field(None, example="Anand R. Verma (Director - Supply Chain)")
    cin_number: Optional[str] = Field("U52100MH2018PTC304891", example="U52100MH2018PTC304891")


class ProsecutionWitness(BaseModel):
    """Inspection / Seizure witnesses."""
    witness_name: str
    designation_or_occupation: str
    address: str


class ExhibitEvidenceItem(BaseModel):
    """Individual evidentiary exhibit submitted to the Court."""
    exhibit_number: str  # "Exhibit P-1", "Exhibit P-2", etc.
    description: str
    sha256_hash: str
    date_of_seizure_or_generation: str


class CourtBriefGenerateRequest(BaseModel):
    """Request to generate official Pre-Trial Court Brief."""
    case_title: str = Field("State of Maharashtra (Legal Metrology Dept) vs. FastRetail Supermarkets Pvt. Ltd.", example="State of Maharashtra (Legal Metrology Dept) vs. FastRetail Supermarkets Pvt. Ltd.")
    court_name: str = Field("Court of the Chief Judicial Magistrate (CJM), Mumbai", example="Court of the Chief Judicial Magistrate (CJM), Mumbai")
    jurisdiction_district: str = Field("Mumbai Suburban", example="Mumbai Suburban")
    inspection_id: Optional[str] = Field(None, example="INSP-MUM-2026-0042")
    complainant_officer_name: str = Field("Inspector Rajesh Kumar, LM Inspector Grade-I", example="Inspector Rajesh Kumar, LM Inspector Grade-I")
    accused: AccusedEntityDetails
    offence_summary: str = Field(..., example="Willful and repeated overcharging above Maximum Retail Price (MRP) and altered price stickers under Section 18 read with Section 36(2) and Section 49.")
    statutory_penal_sections: List[str] = Field(
        default=["Section 18 LM Act 2009", "Section 36(2) LM Act 2009 (Recidivism)", "Section 49 LM Act 2009 (Corporate Liability)", "Rule 6(1)(e) LM PCR 2011"],
        example=["Section 18 LM Act 2009", "Section 36(2) LM Act 2009", "Section 49 LM Act 2009"]
    )


class CourtBriefResponse(BaseModel):
    """Official Pre-Trial Judicial Prosecution Dossier & Sec 65B BSA 2023 Affidavit."""
    dossier_id: str
    case_title: str
    court_name: str
    jurisdiction_district: str
    filing_date: datetime
    complainant_officer_name: str
    accused: AccusedEntityDetails
    statement_of_facts: List[str]
    statutory_penal_sections: List[str]
    exhibits_inventory: List[ExhibitEvidenceItem]
    statutory_prayer_to_magistrate: str
    section_65b_bsa_affidavit_text: str
    master_court_seal_hash: str
