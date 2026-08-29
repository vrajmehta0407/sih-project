import logging
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.security import get_password_hash
from app.models.user import User
from app.models.rule import RuleVersion, Rule
from app.db.base import Base
from app.db.session import engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_db(db: Session) -> None:
    # Ensure tables exist (dynamically bound to the active session engine)
    Base.metadata.create_all(bind=db.get_bind())

    # 1. Seed Default Superuser (Admin)
    admin_user = db.query(User).filter(User.email == settings.FIRST_SUPERUSER_EMAIL).first()
    if not admin_user:
        admin_user = User(
            email=settings.FIRST_SUPERUSER_EMAIL,
            hashed_password=get_password_hash(settings.FIRST_SUPERUSER_PASSWORD),
            full_name="National Director of Legal Metrology",
            role="admin",
            badge_number="LM-NAT-DIR-001",
            phone_number="+91-11-23380000",
            jurisdiction_district="HQ New Delhi",
            jurisdiction_state="National",
            is_active=True
        )
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        logger.info("Default Admin user created.")

    # 2. Seed Default Inspector
    inspector_user = db.query(User).filter(User.email == settings.FIRST_INSPECTOR_EMAIL).first()
    if not inspector_user:
        inspector_user = User(
            email=settings.FIRST_INSPECTOR_EMAIL,
            hashed_password=get_password_hash(settings.FIRST_INSPECTOR_PASSWORD),
            full_name="Rajesh Verma (Senior Inspector)",
            role="inspector",
            badge_number="LM-MH-MUM-402",
            phone_number="+91-9876543210",
            jurisdiction_district="Mumbai City",
            jurisdiction_state="Maharashtra",
            is_active=True
        )
        db.add(inspector_user)
        db.commit()
        db.refresh(inspector_user)
        logger.info("Default Inspector user created.")

    # 3. Seed Grounded Statutory Legal Metrology Rules Version 1.0
    active_version = db.query(RuleVersion).filter(RuleVersion.version_tag == "LM-PCR-2011-V1.0-NATIONAL").first()
    if not active_version:
        active_version = RuleVersion(
            version_tag="LM-PCR-2011-V1.0-NATIONAL",
            statutory_act="Legal Metrology Act, 2009 & Legal Metrology (Packaged Commodities) Rules, 2011",
            description="Official Gazette grounded mandatory packaging rules under Section 18 of the Act and Rule 6 of the PCR 2011.",
            gazette_notification_ref="GSR 202(E) dated 07-03-2011 as amended",
            is_active=True,
            created_by=admin_user.id
        )
        db.add(active_version)
        db.commit()
        db.refresh(active_version)
        logger.info("Default statutory Rule Version created.")

        statutory_rules = [
            Rule(
                version_id=active_version.id,
                rule_code="LM_RULE_6_1_E_MRP",
                title="Mandatory Maximum Retail Price (MRP) Declaration",
                statutory_source="Rule 6(1)(e), Legal Metrology (Packaged Commodities) Rules, 2011 r/w Section 18",
                statutory_penalty_source="Section 36(1), Legal Metrology Act, 2009",
                penalty_first_offence="Fine up to ₹25,000",
                penalty_repeat_offence="Fine up to ₹50,000 or imprisonment up to 1 year",
                description="Retail sale price shall be declared clearly as 'Maximum or Max. Retail Price Rs... inclusive of all taxes' or 'MRP Rs... incl. of all taxes'.",
                field_to_validate="mrp",
                is_mandatory=True,
                validation_type="presence_and_format",
                validation_parameters={
                    "require_numeric": True,
                    "require_inclusive_taxes_text": True,
                    "forbidden_phrases": ["MRP extra", "Local taxes extra"]
                },
                severity="critical"
            ),
            Rule(
                version_id=active_version.id,
                rule_code="LM_RULE_6_1_C_NET_QTY",
                title="Mandatory Net Quantity Declaration in Standard SI Units",
                statutory_source="Rule 6(1)(c) & Rule 11, Legal Metrology (Packaged Commodities) Rules, 2011",
                statutory_penalty_source="Section 25 / Section 36, Legal Metrology Act, 2009",
                penalty_first_offence="Fine up to ₹25,000",
                penalty_repeat_offence="Fine up to ₹50,000 or imprisonment up to 1 year",
                description="The net quantity in terms of standard unit of weight (g, kg), volume (ml, l) or measure (m, cm) or number (N / U) shall be declared unambiguously.",
                field_to_validate="net_quantity",
                is_mandatory=True,
                validation_type="unit_check",
                validation_parameters={
                    "valid_units": ["g", "kg", "ml", "l", "ltr", "gm", "mg", "m", "cm", "mm", "n", "u", "units", "pieces", "nos"],
                    "require_numeric": True
                },
                severity="critical"
            ),
            Rule(
                version_id=active_version.id,
                rule_code="LM_RULE_6_1_A_MFG_DETAILS",
                title="Name and Complete Address of Manufacturer / Packer / Importer",
                statutory_source="Rule 6(1)(a), Legal Metrology (Packaged Commodities) Rules, 2011",
                statutory_penalty_source="Section 36(1), Legal Metrology Act, 2009",
                penalty_first_offence="Fine up to ₹25,000",
                penalty_repeat_offence="Fine up to ₹50,000 or imprisonment up to 1 year",
                description="The name and complete physical address of the manufacturer, or where manufacturer is not packer, the name and address of packer/importer must be indicated on principal display panel.",
                field_to_validate="manufacturer",
                is_mandatory=True,
                validation_type="presence_and_format",
                validation_parameters={
                    "min_characters": 10
                },
                severity="critical"
            ),
            Rule(
                version_id=active_version.id,
                rule_code="LM_RULE_6_1_D_MFG_DATE",
                title="Month and Year of Manufacture / Packing / Import",
                statutory_source="Rule 6(1)(d), Legal Metrology (Packaged Commodities) Rules, 2011",
                statutory_penalty_source="Section 36(1), Legal Metrology Act, 2009",
                penalty_first_offence="Fine up to ₹25,000",
                penalty_repeat_offence="Fine up to ₹50,000 or imprisonment up to 1 year",
                description="Month and year in which commodity is manufactured or pre-packed or imported shall be clearly mentioned (e.g. MM/YYYY or Month YYYY).",
                field_to_validate="mfg_date",
                is_mandatory=True,
                validation_type="date_validity",
                validation_parameters={
                    "require_month_year": True
                },
                severity="critical"
            ),
            Rule(
                version_id=active_version.id,
                rule_code="LM_RULE_6_1_G_COUNTRY_OF_ORIGIN",
                title="Country of Origin Declaration (Mandatory for Imports)",
                statutory_source="Rule 6(1)(g) & Rule 6(10), Legal Metrology (Packaged Commodities) Rules, 2011",
                statutory_penalty_source="Section 36(1), Legal Metrology Act, 2009",
                penalty_first_offence="Fine up to ₹25,000",
                penalty_repeat_offence="Fine up to ₹50,000 or imprisonment up to 1 year",
                description="For pre-packaged commodities imported into India, country of origin or manufacture shall be conspicuously declared on the label.",
                field_to_validate="country_of_origin",
                is_mandatory=True,
                validation_type="presence_and_format",
                validation_parameters={},
                severity="major"
            ),
            Rule(
                version_id=active_version.id,
                rule_code="LM_RULE_6_1_F_CONSUMER_CARE",
                title="Consumer Care Helpline / Email / Address",
                statutory_source="Rule 6(1)(f), Legal Metrology (Packaged Commodities) Rules, 2011",
                statutory_penalty_source="Section 36(1), Legal Metrology Act, 2009",
                penalty_first_offence="Fine up to ₹25,000",
                penalty_repeat_offence="Fine up to ₹50,000 or imprisonment up to 1 year",
                description="Name, address, telephone number, and e-mail address of the person or company who can be contacted in case of consumer complaints.",
                field_to_validate="consumer_care",
                is_mandatory=True,
                validation_type="presence_and_format",
                validation_parameters={
                    "require_contact_info": True
                },
                severity="major"
            ),
            Rule(
                version_id=active_version.id,
                rule_code="LM_RULE_6_1_H_EXPIRY_DATE",
                title="Best Before / Expiry Date (for Food & Perishables)",
                statutory_source="Rule 6(1)(h), Legal Metrology (Packaged Commodities) Rules, 2011",
                statutory_penalty_source="Section 36(1), Legal Metrology Act, 2009",
                penalty_first_offence="Fine up to ₹25,000",
                penalty_repeat_offence="Fine up to ₹50,000 or imprisonment up to 1 year",
                description="Best before / use by date, month and year for human consumption commodities or cosmetics.",
                field_to_validate="exp_date",
                is_mandatory=False,
                validation_type="date_validity",
                validation_parameters={},
                severity="major"
            ),
            Rule(
                version_id=active_version.id,
                rule_code="LM_RULE_6_1_K_UNIT_SALE_PRICE",
                title="Unit Sale Price Declaration",
                statutory_source="Rule 6(1)(k), Legal Metrology (Packaged Commodities) Rules, 2011 (Amendment 2021)",
                statutory_penalty_source="Section 36(1), Legal Metrology Act, 2009",
                penalty_first_offence="Fine up to ₹25,000",
                penalty_repeat_offence="Fine up to ₹50,000 or imprisonment up to 1 year",
                description="Declaration of unit sale price (e.g., Rs. X per g/ml/piece) rounded to two decimal places on packages where net quantity is greater than 1 kg/litre/piece.",
                field_to_validate="unit_sale_price",
                is_mandatory=False,
                validation_type="presence_and_format",
                validation_parameters={},
                severity="minor"
            ),
        ]
        db.add_all(statutory_rules)
        db.commit()
        logger.info("Seeded %d statutory Legal Metrology rules.", len(statutory_rules))
